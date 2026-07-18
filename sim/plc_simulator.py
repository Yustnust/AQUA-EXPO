"""
药液配置加注控制系统 — PLC逻辑仿真器 v2.0

功能: 模拟S7-200 SMART PLC的V区变量+状态机+核心FC逻辑,
     在无硬件环境下运行SAT测试用例,提前发现STL逻辑bug。

仿真范围 (v2.0 扩展):
  - V区变量镜像(VB/VW/VD/V位)
  - I/Q物理映射
  - 定时器模型 (1 tick = 100ms, 对应STL TON 100ms时基)
  - 边沿检测 (EU/ED) 快照机制
  - 状态机VW2 (S0~S7/S_ERROR) + FC1状态调度
  - FC0 断电恢复 (冷启动/断电恢复双路径, RTC检测, Elapsed重算)
  - FC2 急停 (I1.1下降沿锁存, T35继电器故障2秒, 输出安全)
  - FC3 报警 (32位优先级链, 消音, 消光确认, 自动恢复)
  - FC10~FC19 各状态FC (S0~S7/S_ERROR)
  - FC30 阀A诊断 (差值法+延时验证4项+漫溢)
  - FC31 阀B诊断 (四态诊断+开关到位+超时+漫溢)
  - FC32 阀C诊断 (四态诊断+开关到位+超时)
  - FC40 节奏纠偏 (三层额度算法)

非仿真范围(简化):
  - Modbus通讯(用VW4/VD86变量直接赋值模拟从站)
  - BCD转秒(用直接秒数赋值, self.rtc_sec / self.dt10_sec)
  - 实时计时(用tick计数, 1 tick=100ms)

已知STL实现差异(仿真器按"预期语义"实现并在报告中标注):
  - STL FC1未置位M10.2/M10.4状态首入脉冲 → 仿真器用first_enter机制替代
  - STL FC17用M10.7作S6首入脉冲(与预规划标志冲突) → 仿真器用first_enter
  - STL FC30/FC31用MOVB VB266/VB268写诊断结果(高字节)导致AW=字比较失效
    → 仿真器按MOVW语义写VW266/VW268 (FC32已修正, FC30/FC31未修正属STL bug)
  - STL FC40用MOVB VB184写纠偏结果 → 仿真器按MOVW VW184语义实现

用法:
  from plc_simulator import PLCSim
  plc = PLCSim()
  plc.run_cold_start()
  plc.trigger_estop()
  assert plc.vw2 == 99
"""

from typing import Dict, Optional
import copy
import struct


class PLCSim:
    """S7-200 SMART PLC仿真器"""

    # 状态码定义
    S0_INIT = 0
    S1_INLET = 1
    S2_PREMIX = 2
    S3_DOSING = 3
    S35_REST = 4
    S4_TRANSFER = 5
    S5_RUN = 6
    S6_DRAIN = 7
    S7_END = 8
    S_ERROR = 99

    # 报警码定义
    ALM_NONE = 0
    ALM_RELAY = 99
    ALM_OVERFLOW_A = 10
    ALM_OVERFLOW_B = 11
    ALM_NC_TOP = 12
    ALM_NC_BOTTOM = 13
    ALM_ESTOP = 14
    ALM_LAG_SERIOUS = 20
    ALM_LAG_WARN = 21

    def __init__(self):
        """初始化V区(全部清零)"""
        self.vb = {}          # VB字节
        self.i = {}           # I点位 {(byte,bit):bool}
        self.q = {}           # Q点位
        self.m = {}           # M位
        self.sm = {0.1: False, 0.0: True}
        self.t_state = {}     # 定时器 {num:{'enabled','pt','acc','done'}}
        self.tick = 0
        self.first_scan = True
        self.rtc_sec = 0.0    # RTC当前秒数(简化: 直接秒, 非BCD)
        self.dt10_sec = 0.0   # DT10下缸变满时间戳秒数
        self._last_dispatched = None  # 上周期调度的状态(用于首入检测)
        self._prev_vb = {}
        self._prev_i = {}
        self._prev_t_done = {}
        self._init_memory()

    def _init_memory(self):
        """初始化内存区域 + 默认参数"""
        for i in range(600):
            self.vb[i] = 0
        for byte_idx in range(3):
            for bit in range(8):
                self.i[(byte_idx, bit)] = False
        for byte_idx in range(2):
            for bit in range(8):
                self.q[(byte_idx, bit)] = False
        for byte_idx in range(20):
            for bit in range(8):
                self.m[(byte_idx, bit)] = False
        # 默认工艺参数 (测试友好: 较小超时, 快速推进)
        self.set_vd(10, 5.0)       # VD_C_Set 目标浓度
        self.set_vd(14, 100.0)     # VD_C_Stock 母液浓度
        self.set_vd(18, 0.5)       # VD_StepResolution 步进分辨率
        self.set_vd(20, 3.0)       # VD_CycleSetpoint 换水周期(min)
        self.set_vd(24, 5.0)       # VD_ExperimentTarget 实验目标(min)
        self.set_vd(28, 12.0)      # VD_PreMixTime 预循环
        self.set_vd(32, 3.0)       # VD_PreMixTime_MinSafe
        self.set_vd(36, 6.0)       # VD_RestTime 静止
        self.set_vd(40, 1.5)       # VD_RestTime_Min
        self.set_vd(44, 0.5)       # VD_CycleExtend_Max(min)
        self.set_vd(48, 2.0)       # VD_Timeout_ValveA
        self.set_vd(50, 2.0)       # VD_Timeout_ValveB
        self.set_vd(54, 2.0)       # VD_Timeout_ValveC
        self.set_vd(58, 2.0)       # VD_Timeout_Pump1
        self.set_vd(62, 2.0)       # VD_Timeout_Pump2
        self.set_vd(66, 0.5)       # VD_Delay_ValveA_Verify
        self.set_vd(112, 20.0)     # VD_T_Rolling
        self.set_vd(116, 0.0)      # VD_S6_Rolling
        self.set_vd(120, 12.0)     # VD_S2_Target
        self.set_vd(124, 6.0)      # VD_RestTime_Target
        self.set_vd(174, 5.0)      # VD_S3_Estimate
        self.set_vd(316, 10.0)     # 目标进水量(FC30用)
        self.set_vd(86, 0.0)       # VD_FlowMeter_Cumulative
        # 急停常闭触点默认ON
        self.i[(1, 1)] = True

    # ===== V区读写 =====
    def get_vb(self, addr: int) -> int:
        return self.vb.get(addr, 0) & 0xFF

    def set_vb(self, addr: int, val: int):
        self.vb[addr] = val & 0xFF

    def get_vw(self, addr: int) -> int:
        hi = self.get_vb(addr)
        lo = self.get_vb(addr + 1)
        return (hi << 8) | lo

    def set_vw(self, addr: int, val: int):
        val &= 0xFFFF
        self.set_vb(addr, (val >> 8) & 0xFF)
        self.set_vb(addr + 1, val & 0xFF)

    def get_vd(self, addr: int) -> float:
        b = bytes([self.get_vb(addr), self.get_vb(addr+1),
                   self.get_vb(addr+2), self.get_vb(addr+3)])
        return struct.unpack('>f', b)[0]

    def set_vd(self, addr: int, val: float):
        b = struct.pack('>f', val)
        for i, byte in enumerate(b):
            self.set_vb(addr + i, byte)

    def get_v_bit(self, byte_addr: int, bit: int) -> bool:
        return bool((self.get_vb(byte_addr) >> bit) & 1)

    def set_v_bit(self, byte_addr: int, bit: int, val: bool):
        cur = self.get_vb(byte_addr)
        if val:
            cur |= (1 << bit)
        else:
            cur &= ~(1 << bit) & 0xFF
        self.set_vb(byte_addr, cur)

    # ===== I/Q 操作 =====
    def set_di(self, byte: int, bit: int, val: bool):
        self.i[(byte, bit)] = bool(val)

    def set_q(self, byte: int, bit: int, val: bool):
        self.q[(byte, bit)] = bool(val)

    def get_qb0(self) -> int:
        v = 0
        for bit in range(8):
            if self.q.get((0, bit)):
                v |= (1 << bit)
        return v

    # ===== 定时器模型 (1 tick = 100ms) =====
    def ton(self, num: int, pt: int, enabled: bool = True) -> bool:
        """TON定时器: enabled=True时累计, acc>=pt置done; False时复位"""
        t = self.t_state.setdefault(num, {'enabled': False, 'pt': 0, 'acc': 0, 'done': False})
        if not enabled:
            t['acc'] = 0
            t['done'] = False
            t['enabled'] = False
            return False
        t['enabled'] = True
        t['pt'] = pt
        if not t['done']:
            t['acc'] += 1
            if t['acc'] >= t['pt']:
                t['done'] = True
        return t['done']

    def r_timer(self, num: int):
        """复位定时器 (R Tn)"""
        self.t_state[num] = {'enabled': False, 'pt': 0, 'acc': 0, 'done': False}

    def get_t(self, num: int) -> bool:
        t = self.t_state.get(num)
        return t['done'] if t else False

    def t_acc_sec(self, num: int) -> float:
        """读定时器累计值(秒)"""
        t = self.t_state.get(num)
        return (t['acc'] / 10.0) if t else 0.0

    # ===== 边沿检测 =====
    def _snapshot_edges(self):
        self._prev_vb = dict(self.vb)
        self._prev_i = dict(self.i)
        self._prev_t_done = {n: t['done'] for n, t in self.t_state.items()}

    def rose_v(self, byte: int, bit: int) -> bool:
        cur = self.get_v_bit(byte, bit)
        prev = bool((self._prev_vb.get(byte, 0) >> bit) & 1)
        return cur and not prev

    def rose_i(self, byte: int, bit: int) -> bool:
        return self.i[(byte, bit)] and not self._prev_i.get((byte, bit), False)

    def fell_i(self, byte: int, bit: int) -> bool:
        return (not self.i[(byte, bit)]) and self._prev_i.get((byte, bit), False)

    def rose_t(self, num: int) -> bool:
        return self.get_t(num) and not self._prev_t_done.get(num, False)

    # ===== 符号化访问 =====
    @property
    def vw2(self): return self.get_vw(2)
    @vw2.setter
    def vw2(self, v): self.set_vw(2, v)
    @property
    def vw6(self): return self.get_vw(6)
    @vw6.setter
    def vw6(self, v): self.set_vw(6, v)
    @property
    def vw8(self): return self.get_vw(8)
    @vw8.setter
    def vw8(self, v): self.set_vw(8, v)
    @property
    def vw4(self): return self.get_vw(4)
    @vw4.setter
    def vw4(self, v): self.set_vw(4, v)

    @property
    def m_estop_latch(self): return self.get_v_bit(300, 4)
    @m_estop_latch.setter
    def m_estop_latch(self, v): self.set_v_bit(300, 4, v)
    @property
    def m_relay_fault(self): return self.get_v_bit(300, 5)
    @m_relay_fault.setter
    def m_relay_fault(self, v): self.set_v_bit(300, 5, v)
    @property
    def m_overflow_a(self): return self.get_v_bit(300, 0)
    @m_overflow_a.setter
    def m_overflow_a(self, v): self.set_v_bit(300, 0, v)
    @property
    def m_init_done(self): return self.get_v_bit(304, 0)
    @m_init_done.setter
    def m_init_done(self, v): self.set_v_bit(304, 0, v)
    @property
    def i_estop(self): return self.i[(1, 1)]
    @i_estop.setter
    def i_estop(self, v): self.i[(1, 1)] = v
    @property
    def i_relay_fb(self): return self.i[(1, 2)]
    @i_relay_fb.setter
    def i_relay_fb(self, v): self.i[(1, 2)] = v

    # ===== FC0 系统初始化 =====
    def fc0_sys_init(self):
        """FC0系统初始化(冷启动/断电恢复双路径)"""
        if not self.first_scan:
            return
        if not self.m_init_done:
            # 冷启动路径
            self.vw2 = self.S0_INIT
            self.set_v_bit(1, 6, False)
            self.set_v_bit(1, 7, False)
            for byte_idx in range(2):
                for bit in range(8):
                    self.q[(byte_idx, bit)] = False
            self.m_estop_latch = False
            self.m_relay_fault = False
            for b in range(300, 304):
                self.set_vb(b, 0)
            self.vw6 = 0
            for bit in range(6):
                self.set_v_bit(1, bit, False)
            self.vw8 = 0
            self.set_vd(178, 0.0)
            self.m[(10, 7)] = False
        else:
            # 断电恢复路径
            rtc_ok = True
            if self.dt10_sec > 0 and self.rtc_sec < self.dt10_sec:
                rtc_ok = False
            if not rtc_ok:
                self.set_v_bit(303, 5, True)
                self.set_vd(178, 0.0)
                self.vw2 = self.S_ERROR
            else:
                # VD_S5_Elapsed重算: 仅V1.7=1且VW2==6
                if self.get_v_bit(1, 7) and self.vw2 == self.S5_RUN:
                    self.set_vd(178, self.rtc_sec - self.dt10_sec)
                else:
                    self.set_vd(178, 0.0)
                # 状态恢复策略
                state = self.vw2
                if state in (self.S0_INIT, self.S5_RUN, self.S7_END, self.S_ERROR):
                    pass  # 保持
                else:
                    # S1~S6 → S_ERROR
                    for byte_idx in range(2):
                        for bit in range(8):
                            self.q[(byte_idx, bit)] = False
                    self.vw2 = self.S_ERROR
                    self.m_estop_latch = True
        self.m_init_done = True
        self.first_scan = False

    # ===== FC2 急停处理 =====
    def fc2_estop(self):
        """FC2急停处理: I1.1下降沿锁存+T35继电器故障+输出安全"""
        # NETWORK1: 急停下降沿检测
        if self.fell_i(1, 1):
            self.m_estop_latch = True
            self.vw2 = self.S_ERROR
            self.m[(10, 7)] = False
        # NETWORK2: 安全继电器反馈延时(T35 PT=20=2秒)
        if self.m_estop_latch and not self.i_relay_fb:
            self.ton(35, 20, enabled=True)
        else:
            self.ton(35, 20, enabled=False)
        if self.rose_t(35):
            self.m_relay_fault = True
        # NETWORK3: 急停锁存时输出强制安全
        if self.m_estop_latch:
            for bit in range(8):
                self.q[(0, bit)] = False
            self.q[(0, 7)] = True
        # NETWORK4: 报警码(继电器故障99 > 急停10) — FC3会重算覆盖, 此处按STL写
        if self.m_relay_fault:
            self.vw6 = 99
        elif self.m_estop_latch:
            self.vw6 = 10

    # ===== FC3 报警处理 =====
    def _priority_chain(self) -> int:
        """优先级链计算VW6"""
        if self.get_v_bit(300, 5): return 99
        if self.get_v_bit(300, 0): return 10
        if self.get_v_bit(300, 1): return 11
        if self.get_v_bit(300, 2): return 12
        if self.get_v_bit(300, 3): return 13
        if self.get_v_bit(300, 4): return 14
        if self.get_v_bit(300, 6): return 20
        if self.get_v_bit(300, 7): return 21
        for bit, code in [(0, 30), (1, 31), (2, 32), (3, 33),
                          (4, 34), (5, 35), (6, 36)]:
            if self.get_v_bit(301, bit):
                return code
        for bit, code in [(0, 40), (1, 41), (2, 42), (3, 43),
                          (4, 44), (5, 45), (6, 46), (7, 47)]:
            if self.get_v_bit(302, bit):
                return code
        for bit, code in [(0, 60), (1, 61), (2, 62), (3, 63),
                          (4, 64), (5, 65), (6, 66)]:
            if self.get_v_bit(303, bit):
                return code
        return 0

    def fc3_alarm(self):
        """FC3报警处理: 优先级链+消音+消光确认+自动恢复"""
        # NETWORK1: 优先级链
        code = self._priority_chain()
        self.vw6 = code
        m11_2_prev = self.m[(11, 2)]
        new_alarm = (code != 0) and (not m11_2_prev)
        # NETWORK2: 输出管理
        if code != 0:
            self.q[(1, 0)] = True  # 灯光常亮
            if new_alarm:
                self.m[(11, 1)] = False  # 清消音标志(新报警重鸣)
            if not self.m[(11, 1)]:
                self.q[(0, 7)] = True  # 声音开
        else:
            # 无报警: 自动消光消音
            self.q[(1, 0)] = False
            self.q[(0, 7)] = False
            self.m[(11, 1)] = False
        # NETWORK3: 消音(I2.1 OR V0.4 上升沿)
        if self.rose_i(2, 1) or self.rose_v(0, 4):
            self.q[(0, 7)] = False
            self.m[(11, 1)] = True
            self.set_v_bit(1, 4, True)  # STA_MuteDone
            self.set_v_bit(0, 4, False)  # 清V0.4
        # NETWORK4: 报警确认(V0.3上升沿 → 条件消失才复位)
        if self.rose_v(0, 3):
            self.set_v_bit(1, 3, True)  # STA_AlarmAckDone
            self.set_v_bit(0, 3, False)
            # 漫溢级: 条件消失才复位
            if self.get_v_bit(300, 0) and not self.i[(0, 5)]:
                self.set_v_bit(300, 0, False)
            if self.get_v_bit(300, 1) and not self.i[(0, 7)]:
                self.set_v_bit(300, 1, False)
            # 阀A类
            if self.get_v_bit(301, 0) and not self.i[(0, 0)]:
                self.set_v_bit(301, 0, False)
            if self.get_v_bit(301, 1) and not self.i[(0, 0)]:
                self.set_v_bit(301, 1, False)
            if self.get_v_bit(301, 2) and self.i[(1, 4)]:
                self.set_v_bit(301, 2, False)
            if self.get_v_bit(301, 3) and not self.i[(0, 0)]:
                self.set_v_bit(301, 3, False)
            if self.get_v_bit(301, 4) and self.i[(1, 3)]:
                self.set_v_bit(301, 4, False)
            if self.get_v_bit(301, 5) and self.i[(0, 0)]:
                self.set_v_bit(301, 5, False)
            if self.get_v_bit(301, 6) and not self.get_v_bit(1, 6):
                self.set_v_bit(301, 6, False)
            # 阀B类
            if self.get_v_bit(302, 0) and (self.i[(0, 1)] or self.i[(0, 6)]):
                self.set_v_bit(302, 0, False)
            if self.get_v_bit(302, 1) and self.i[(1, 5)]:
                self.set_v_bit(302, 1, False)
            if self.get_v_bit(302, 2) and self.i[(0, 1)]:
                self.set_v_bit(302, 2, False)
            if self.get_v_bit(302, 3) and self.i[(1, 6)]:
                self.set_v_bit(302, 3, False)
            if self.get_v_bit(302, 4) and not self.i[(0, 1)]:
                self.set_v_bit(302, 4, False)
            if self.get_v_bit(302, 5) and (self.i[(0, 2)] or self.i[(1, 0)]):
                self.set_v_bit(302, 5, False)
            if self.get_v_bit(302, 6) and self.i[(1, 7)]:
                self.set_v_bit(302, 6, False)
            if self.get_v_bit(302, 7) and self.i[(0, 2)]:
                self.set_v_bit(302, 7, False)
            # 其他类
            if self.get_v_bit(303, 0) and self.i[(2, 0)]:
                self.set_v_bit(303, 0, False)
            if self.get_v_bit(303, 1) and not self.i[(0, 2)]:
                self.set_v_bit(303, 1, False)
            if self.get_v_bit(303, 2) and self.i[(0, 3)]:
                self.set_v_bit(303, 2, False)
            if self.get_v_bit(303, 3) and self.i[(0, 4)]:
                self.set_v_bit(303, 3, False)
            if self.get_v_bit(303, 4) and self.vw4 == 0:
                self.set_v_bit(303, 4, False)
        # NETWORK5: 自动恢复模式(V200.0=0) 一般故障级条件消失自动复位
        if not self.get_v_bit(200, 0):
            if self.get_v_bit(301, 0) and not self.i[(0, 0)]:
                self.set_v_bit(301, 0, False)
            if self.get_v_bit(301, 1) and not self.i[(0, 0)]:
                self.set_v_bit(301, 1, False)
            if self.get_v_bit(301, 2) and self.i[(1, 4)]:
                self.set_v_bit(301, 2, False)
            if self.get_v_bit(301, 3) and not self.i[(0, 0)]:
                self.set_v_bit(301, 3, False)
            if self.get_v_bit(301, 4) and self.i[(1, 3)]:
                self.set_v_bit(301, 4, False)
            if self.get_v_bit(301, 5) and self.i[(0, 0)]:
                self.set_v_bit(301, 5, False)
            if self.get_v_bit(301, 6) and not self.get_v_bit(1, 6):
                self.set_v_bit(301, 6, False)
            if self.get_v_bit(302, 0) and (self.i[(0, 1)] or self.i[(0, 6)]):
                self.set_v_bit(302, 0, False)
            if self.get_v_bit(302, 4) and not self.i[(0, 1)]:
                self.set_v_bit(302, 4, False)
            if self.get_v_bit(303, 2) and self.i[(0, 3)]:
                self.set_v_bit(303, 2, False)
            if self.get_v_bit(303, 3) and self.i[(0, 4)]:
                self.set_v_bit(303, 3, False)
        # 更新上一周期报警标志
        self.m[(11, 2)] = (self.vw6 != 0)

    # ===== FC1 状态调度 =====
    def fc1_dispatch(self):
        """FC1状态调度: 根据VW2调用对应状态FC, 处理首入脉冲/非法态"""
        cur = self.vw2
        first = (cur != self._last_dispatched)
        if cur == self.S0_INIT:
            self.fc10(first)
        elif cur == self.S1_INLET:
            self.fc11(first)
        elif cur == self.S2_PREMIX:
            self.fc12(first)
        elif cur == self.S3_DOSING:
            self.fc13(first)
        elif cur == self.S35_REST:
            self.fc14(first)
        elif cur == self.S4_TRANSFER:
            self.fc15(first)
        elif cur == self.S5_RUN:
            self.fc16(first)
        elif cur == self.S6_DRAIN:
            self.fc17(first)
        elif cur == self.S7_END:
            self.fc18(first)
        elif cur == self.S_ERROR:
            self.fc19(first)
        else:
            # 非法状态强制回S0
            self.vw2 = self.S0_INIT
        self._last_dispatched = cur

    # ===== FC10 S0 初始化 =====
    def fc10(self, first: bool):
        # 每周期安全待命
        for bit in range(8):
            self.q[(0, bit)] = False
        self.q[(0, 7)] = False
        # CMD_Start上升沿 + 无报警 → S1
        if self.rose_v(0, 0) and self.vw6 == 0:
            self.vw2 = self.S1_INLET
            self.set_v_bit(1, 0, True)  # STA_StartAck
            self.set_v_bit(0, 0, False)  # 清命令

    # ===== FC11 S1 上缸进水 =====
    def fc11(self, first: bool):
        # 首入动作(STL用M10.2 EU, FC1未置位 → 仿真器用first替代)
        if first:
            self.set_vd(82, self.get_vd(86))  # VD82流量计快照
            self.q[(0, 2)] = True             # 开阀A
            self.r_timer(37)
            self.ton(37, 32767, enabled=True)  # S1计时(自由)
            self.set_v_bit(1, 6, False)        # 上缸=空
            self.set_vw(260, 1)                # 诊断子状态=1
            self.set_vw(266, 0)                # 清诊断结果
            # VW278 = VD48×10, VW280 = VD66×10
            self.set_vw(278, int(round(self.get_vd(48) * 10)))
            self.set_vw(280, int(round(self.get_vd(66) * 10)))
        # 调用FC30阀A诊断
        self.fc30()
        # 检查诊断结果
        if self.get_vw(266) == 1:
            # 诊断正常完成
            self.r_timer(37)
            self.set_vd(70, self.t_acc_sec(37))  # VD_S1_Actual
            # Story1.4 二次校正(模式1)
            self.set_vd(150, self.get_vd(20) * 60.0 + self.get_vd(116) - self.get_vd(178))
            self.set_vd(154, self.get_vd(120) + self.get_vd(174) + self.get_vd(124))
            self.set_vw(182, 1)
            self.fc40()
            # 更新VD_T_Rolling
            self.set_vd(112, self.get_vd(70) + self.get_vd(28) + self.get_vd(174) + self.get_vd(36))
            # 非人工介入 → S2
            if self.get_vw(184) != 4:
                self.vw2 = self.S2_PREMIX

    # ===== FC12 S2 预循环 =====
    def fc12(self, first: bool):
        if first:
            self.q[(0, 0)] = True  # 潜水泵1
            self.q[(0, 1)] = True  # 潜水泵2
            self.set_vw(252, int(round(self.get_vd(120) * 10)))
            self.r_timer(38)
            self.ton(38, self.get_vw(252), enabled=True)
            self.set_v_bit(1, 6, True)  # 上缸=满
        # 泵1流量检测
        self.set_vw(282, int(round(self.get_vd(58) * 10)))
        self.ton(44, self.get_vw(282), enabled=self.q[(0, 0)] and not self.i[(0, 3)])
        if self.rose_t(44):
            self.set_v_bit(303, 2, True)
            self.vw2 = self.S_ERROR
        # 泵2流量检测
        self.set_vw(284, int(round(self.get_vd(62) * 10)))
        self.ton(45, self.get_vw(284), enabled=self.q[(0, 1)] and not self.i[(0, 4)])
        if self.rose_t(45):
            self.set_v_bit(303, 3, True)
            self.vw2 = self.S_ERROR
        # 预循环完成
        if self.get_t(38):
            self.q[(0, 0)] = False
            self.q[(0, 1)] = False
            self.vw2 = self.S3_DOSING

    # ===== FC13 S3 加药 =====
    def fc13(self, first: bool):
        if first:
            # 简化剂量计算
            vol = self.get_vd(10) * self.get_vd(90) / self.get_vd(14)
            steps = vol / self.get_vd(18)
            self.set_vd(98, vol)
            self.set_vd(102, steps)
            self.set_vw(204, int(round(steps)))
            self.set_vw(206, int(round(steps)))
            self.m[(10, 3)] = True
        # 轮询注射泵状态码
        if self.vw4 == 0:
            self.vw2 = self.S35_REST
            self.m[(10, 3)] = False
        elif self.vw4 >= 4:
            self.set_v_bit(303, 4, True)
            self.vw2 = self.S_ERROR

    # ===== FC14 S3.5 静止等候 =====
    def fc14(self, first: bool):
        if first:
            self.set_vw(254, int(round(self.get_vd(124) * 10)))
            self.r_timer(39)
            self.ton(39, self.get_vw(254), enabled=True)
        if self.get_t(39):
            self.vw2 = self.S4_TRANSFER

    # ===== FC15 S4 上→下转移 =====
    def fc15(self, first: bool):
        if first:
            self.q[(0, 3)] = True  # 开阀B
            self.r_timer(40)
            self.ton(40, 32767, enabled=True)
            self.set_v_bit(1, 6, False)  # 上缸=空
            self.set_vw(262, 1)
            self.set_vw(268, 0)
            self.set_vw(274, int(round(self.get_vd(50) * 10)))
        self.fc31()
        if self.get_vw(268) == 1:
            self.r_timer(40)
            self.set_vd(74, self.t_acc_sec(40))
            self.set_v_bit(1, 7, True)  # 下缸=满
            self.dt10_sec = self.rtc_sec  # 记录下缸变满时间戳
            self.set_vd(178, 0.0)         # VD_S5_Elapsed清零
            self.m[(10, 7)] = False       # 清预规划标志
            self.vw2 = self.S5_RUN

    # ===== FC16 S5 实验运行 =====
    def fc16(self, first: bool):
        # NETWORK1: 下缸满计时器VD_S5_Elapsed每秒+1
        if self.get_v_bit(1, 7):
            self.ton(60, 10, enabled=True)
        else:
            self.ton(60, 10, enabled=False)
        if self.rose_t(60):
            self.set_vd(178, self.get_vd(178) + 1.0)
            self.r_timer(60)
        # NETWORK2: Available计算 + 预规划上升沿
        self.set_vd(150, self.get_vd(20) * 60.0 + self.get_vd(116) - self.get_vd(178))
        if (self.get_vd(150) <= self.get_vd(112)) and (not self.m[(10, 7)]):
            self.m[(10, 7)] = True
            self.set_vw(182, 0)
            self.set_vd(154, self.get_vd(112))
            self.fc40()
            if self.get_vw(184) != 4:
                if not self.get_v_bit(1, 6):
                    self.vw2 = self.S1_INLET  # 上缸=空 → 启动新一轮配液
        # 预规划触发后上缸≠空(异常)
        if self.m[(10, 7)] and self.get_v_bit(1, 6):
            self.set_v_bit(301, 6, True)
            self.vw2 = self.S_ERROR
        # NETWORK3: 实验时长累加(每分钟+1)
        if self.get_v_bit(1, 7):
            self.ton(47, 600, enabled=True)
        else:
            self.ton(47, 600, enabled=False)
        if self.rose_t(47):
            self.set_vd(96, self.get_vd(96) + 1.0)
        # NETWORK4: 换水周期到达 → S6
        if self.get_vd(178) >= self.get_vd(20) * 60.0:
            self.m[(10, 7)] = False
            self.r_timer(60)
            self.vw2 = self.S6_DRAIN
        # NETWORK5: 实验时长达标 → S7
        if self.get_vd(96) >= self.get_vd(24):
            self.r_timer(47)
            self.r_timer(60)
            self.m[(10, 7)] = False
            self.vw2 = self.S7_END
        # NETWORK6: HMI手动停止
        if self.rose_v(0, 2):
            self.r_timer(47)
            self.r_timer(60)
            self.m[(10, 7)] = False
            self.vw2 = self.S7_END
            self.set_v_bit(1, 2, True)  # STA_StopAck
            self.set_v_bit(0, 2, False)

    # ===== FC17 S6 下缸排水 =====
    def fc17(self, first: bool):
        if first:
            self.q[(0, 4)] = True  # 开阀C
            self.r_timer(42)
            self.ton(42, 32767, enabled=True)
            self.set_vw(264, 1)
            self.set_vw(270, 0)
            self.set_vw(276, int(round(self.get_vd(54) * 10)))
        self.fc32()
        if self.get_vw(270) == 1:
            self.r_timer(42)
            self.set_vd(78, self.t_acc_sec(42))
            self.set_vd(116, self.get_vd(78))  # VD_S6_Rolling
            self.set_v_bit(1, 7, False)        # 下缸=空
            # 状态转移: 实验未结束→S5(轮次+1), 实验结束→S7
            if not self.m[(10, 6)]:
                self.vw8 = self.vw8 + 1
                self.vw2 = self.S5_RUN
            else:
                self.m[(10, 6)] = False
                self.vw2 = self.S7_END

    # ===== FC18 S7 实验结束 =====
    def fc18(self, first: bool):
        if first:
            for bit in range(8):
                self.q[(0, bit)] = False
            self.q[(0, 7)] = False
            self.q[(1, 0)] = False
            self.r_timer(47)
            self.m[(10, 6)] = True  # 实验结束标志
        # CMD_Start上升沿 → S0
        if self.rose_v(0, 0):
            self.m[(10, 6)] = False
            self.set_v_bit(1, 0, False)
            self.vw2 = self.S0_INIT

    # ===== FC19 S_ERROR 故障锁定 =====
    def fc19(self, first: bool):
        # NETWORK1: 输出强制安全(双保险)
        for bit in range(8):
            self.q[(0, bit)] = False
        self.q[(0, 7)] = True
        # NETWORK2/3: 继电器故障禁止复位; 无继电器故障时系统复位
        if not self.m_relay_fault:
            if self.i_estop and self.rose_i(2, 3):
                self.m_estop_latch = False
                self.set_v_bit(1, 6, False)
                self.set_v_bit(1, 7, False)
                self.vw2 = self.S0_INIT
                self.vw6 = 0
                self.q[(0, 7)] = False
        # NETWORK4: 继电器故障HMI高权限确认(V0.7 + I1.2)
        if self.rose_v(0, 7) and self.i_relay_fb:
            self.m_relay_fault = False
            self.set_v_bit(0, 7, False)

    # ===== FC30 阀A诊断 =====
    def fc30(self):
        # NETWORK1: 漫溢保护(全程最高优先级)
        if self.i[(0, 5)]:
            self.set_v_bit(300, 0, True)
            self.set_v_bit(300, 2, True)
            self.q[(0, 5)] = True  # NC电磁阀上缸
            self.q[(0, 2)] = False  # 关阀A
            self.vw2 = self.S_ERROR
            self.set_vw(266, 2)
            return
        # 诊断子状态调度
        st = self.get_vw(260)
        if st == 1:
            # 等开到位
            self.ton(50, self.get_vw(278), enabled=True)
            if self.rose_i(1, 3):
                self.set_vw(260, 2)
                self.r_timer(50)
                return
            if self.get_t(50):
                self.set_v_bit(301, 4, True)  # 开到位超时
                self.vw2 = self.S_ERROR
                self.set_vw(266, 2)
                return
        elif st == 2:
            # 开启完成检查
            if self.i[(0, 0)]:
                self.set_vw(260, 3)
                return
            # 开到位但无流(2s确认)
            if self.i[(1, 3)] and not self.i[(0, 0)]:
                self.ton(52, 20, enabled=True)
                if self.get_t(52):
                    self.set_v_bit(301, 5, True)
                    self.vw2 = self.S_ERROR
                    self.set_vw(266, 2)
                    return
            else:
                self.ton(52, 20, enabled=False)
        elif st == 3:
            # 运行中-差值法持续计量
            self.set_vd(90, self.get_vd(86) - self.get_vd(82))
            if self.get_vd(90) >= self.get_vd(316):
                self.q[(0, 2)] = False  # 关阀A
                self.set_vd(308, self.get_vd(86))  # 关阀瞬间快照
                self.set_vw(260, 5)
                self.r_timer(52)
        elif st == 5:
            # 关闭后延时验证(4项并行)
            self.ton(51, self.get_vw(280), enabled=True)
            self.set_vd(312, self.get_vd(86) - self.get_vd(308))
            if self.get_t(51):
                # 4项校验
                if self.i[(0, 0)]:
                    self.set_v_bit(301, 0, True)  # 关后仍有流
                if self.get_vd(312) > 0.1:
                    self.set_v_bit(301, 1, True)  # 内漏
                if not self.i[(1, 4)]:
                    self.set_v_bit(301, 2, True)  # 关到位超时
                if self.i[(1, 4)] and self.i[(0, 0)]:
                    self.set_v_bit(301, 3, True)  # 关到位但仍有流
                # 判定
                if (not self.i[(0, 0)]) and (self.get_vd(312) <= 0.1) and self.i[(1, 4)]:
                    self.set_vw(260, 0)
                    self.set_vw(266, 1)  # 正常完成
                    self.r_timer(51)
                else:
                    self.vw2 = self.S_ERROR
                    self.set_vw(266, 2)

    # ===== FC31 阀B诊断 =====
    def fc31(self):
        # NETWORK1: 漫溢保护(下缸)
        if self.i[(0, 7)]:
            self.set_v_bit(300, 1, True)
            self.set_v_bit(300, 3, True)
            self.q[(0, 6)] = True  # NC电磁阀下缸
            self.q[(0, 3)] = False
            self.vw2 = self.S_ERROR
            self.set_vw(268, 2)
            return
        st = self.get_vw(262)
        if st == 1:
            self.ton(53, self.get_vw(274), enabled=True)
            self.ton(54, self.get_vw(274), enabled=True)
            if self.rose_i(1, 5):
                self.set_vw(262, 2)
                self.r_timer(53)
                self.r_timer(54)
                return
            if self.get_t(53):
                self.set_v_bit(302, 1, True)
                self.vw2 = self.S_ERROR
                self.set_vw(268, 2)
                return
            if self.get_t(54) and not self.i[(0, 1)]:
                self.set_v_bit(302, 2, True)
                self.vw2 = self.S_ERROR
                self.set_vw(268, 2)
                return
        elif st == 2:
            if self.i[(0, 1)]:
                self.set_vw(262, 3)
                return
            if self.i[(1, 5)] and not self.i[(0, 1)]:
                self.set_v_bit(302, 2, True)
                self.vw2 = self.S_ERROR
                self.set_vw(268, 2)
                return
        elif st == 3:
            # 四态诊断
            if self.i[(0, 6)] and not self.i[(0, 1)]:
                self.q[(0, 3)] = False  # 关阀B
                self.set_vw(262, 4)
                return
            if (not self.i[(0, 1)]) and (not self.i[(0, 6)]):
                self.set_v_bit(302, 0, True)  # 设备故障
                self.vw2 = self.S_ERROR
                self.set_vw(268, 2)
                return
            # 流量开关ON → 继续
        elif st == 4:
            self.ton(55, self.get_vw(274), enabled=True)
            if self.i[(1, 6)] and not self.i[(0, 1)]:
                self.set_vw(262, 0)
                self.set_vw(268, 1)
                self.r_timer(55)
                return
            if self.i[(1, 6)] and self.i[(0, 1)]:
                self.set_v_bit(302, 4, True)  # 内漏
                self.vw2 = self.S_ERROR
                self.set_vw(268, 2)
                return
            if self.get_t(55) and not self.i[(1, 6)]:
                self.set_v_bit(302, 3, True)  # 关到位超时
                self.vw2 = self.S_ERROR
                self.set_vw(268, 2)
                return

    # ===== FC32 阀C诊断 =====
    def fc32(self):
        st = self.get_vw(264)
        if st == 1:
            self.ton(56, self.get_vw(276), enabled=True)
            self.ton(57, self.get_vw(276), enabled=True)
            if self.rose_i(1, 7):
                self.set_vw(264, 2)
                self.r_timer(56)
                self.r_timer(57)
                return
            if self.get_t(56):
                self.set_v_bit(302, 6, True)
                self.vw2 = self.S_ERROR
                self.set_vw(270, 2)
                return
            if self.get_t(57) and not self.i[(0, 2)]:
                self.set_v_bit(302, 7, True)
                self.vw2 = self.S_ERROR
                self.set_vw(270, 2)
                return
        elif st == 2:
            if self.i[(0, 2)]:
                self.set_vw(264, 3)
                return
            if self.i[(1, 7)] and not self.i[(0, 2)]:
                self.set_v_bit(302, 7, True)
                self.vw2 = self.S_ERROR
                self.set_vw(270, 2)
                return
        elif st == 3:
            if self.i[(1, 0)] and not self.i[(0, 2)]:
                self.q[(0, 4)] = False
                self.set_vw(264, 4)
                return
            if (not self.i[(0, 2)]) and (not self.i[(1, 0)]):
                self.set_v_bit(302, 5, True)
                self.vw2 = self.S_ERROR
                self.set_vw(270, 2)
                return
        elif st == 4:
            self.ton(58, self.get_vw(276), enabled=True)
            if self.i[(2, 0)] and not self.i[(0, 2)]:
                self.set_vw(264, 0)
                self.set_vw(270, 1)
                self.r_timer(58)
                return
            if self.i[(2, 0)] and self.i[(0, 2)]:
                self.set_v_bit(303, 1, True)
                self.vw2 = self.S_ERROR
                self.set_vw(270, 2)
                return
            if self.get_t(58) and not self.i[(2, 0)]:
                self.set_v_bit(303, 0, True)
                self.vw2 = self.S_ERROR
                self.set_vw(270, 2)
                return

    # ===== FC40 节奏纠偏 =====
    def fc40(self):
        """三层纠偏算法(纯数学). 输入VD150/VD154/VW182, 输出VD120/124/128/VW184"""
        self.set_vw(184, 0)
        # 三层额度
        layer0 = self.get_vd(36) - self.get_vd(40)   # RestTime - RestTime_Min
        layer1 = self.get_vd(28) - self.get_vd(32)   # PreMixTime - PreMixTime_MinSafe
        layer2 = self.get_vd(44) * 60.0               # CycleExtend_Max(min→s)
        avail = self.get_vd(150)
        needed = self.get_vd(154)
        if avail >= needed:
            # 无需纠偏
            self.set_vd(120, self.get_vd(28))
            self.set_vd(124, self.get_vd(36))
            self.set_vd(128, 0.0)
            self.set_vw(184, 1)
            return
        delta = needed - avail
        # 第0层
        if delta <= layer0:
            self.set_vd(124, self.get_vd(36) - delta)
            self.set_vd(120, self.get_vd(28))
            self.set_vd(128, 0.0)
            self.set_vw(184, 2)
            return
        # 第0层用满
        self.set_vd(124, self.get_vd(40))
        delta -= layer0
        # 第1层
        if delta <= layer1:
            self.set_vd(120, self.get_vd(28) - delta)
            self.set_vd(128, 0.0)
            self.set_vw(184, 2)
            return
        # 第1层用满
        self.set_vd(120, self.get_vd(32))
        delta -= layer1
        # 第2层
        if delta <= layer2:
            self.set_vd(128, delta / 60.0)  # 秒→分
            self.set_vw(184, 3)
            if not self.get_v_bit(300, 7):
                self.set_v_bit(300, 7, True)
            return
        # 三层用尽
        self.set_vw(184, 4)
        self.set_v_bit(300, 6, True)
        self.vw2 = self.S_ERROR

    # ===== 主循环 =====
    def run_cycle(self):
        """运行一个扫描周期 (1 tick = 100ms)
        边沿检测模型: _prev_* 保存上一周期末状态, 本周期内 rose_*/fell_*
        比较"当前值"与"上一周期末值", 周期结束时再快照供下周期使用。
        """
        self.tick += 1
        self.sm[0.1] = self.first_scan
        # 注: 不在周期开始时快照(否则prev=current导致边沿恒为False)
        if self.first_scan:
            self.fc0_sys_init()
        self.fc2_estop()
        self.fc3_alarm()
        self.fc1_dispatch()
        # 周期末快照, 作为下周期的"前一状态"
        self._snapshot_edges()

    # ===== 测试辅助 =====
    def run_cold_start(self, cycles: int = 3):
        for _ in range(cycles):
            self.run_cycle()

    def trigger_estop(self):
        self.i_estop = False
        self.run_cycle()

    def release_estop(self):
        self.i_estop = True
        self.run_cycle()

    def system_reset(self):
        """按下系统复位按钮I2.3(点动)"""
        self.i[(2, 3)] = True
        self.run_cycle()
        self.i[(2, 3)] = False

    def press_mute(self):
        """按下消音按钮I2.1(点动)"""
        self.i[(2, 1)] = True
        self.run_cycle()
        self.i[(2, 1)] = False

    def send_cmd(self, byte: int, bit: int, cycles: int = 1):
        """HMI下发命令位(上升沿)并运行cycles周期后清命令"""
        self.set_v_bit(byte, bit, True)
        for _ in range(cycles):
            self.run_cycle()
        self.set_v_bit(byte, bit, False)

    def advance_seconds(self, seconds: float):
        """推进指定秒数(1秒=10周期)"""
        n = int(seconds * 10)
        for _ in range(n):
            self.run_cycle()

    def warm_restart(self, vw2: int, v17: bool, rtc_sec: float, dt10_sec: float):
        """断电恢复上电: 设置断电前状态后走FC0断电恢复路径"""
        self.m_init_done = True  # V304.0=1
        self.first_scan = True
        self.vw2 = vw2
        self.set_v_bit(1, 7, v17)
        self.rtc_sec = rtc_sec
        self.dt10_sec = dt10_sec
        self.run_cycle()

    def get_status(self) -> Dict:
        return {
            'tick': self.tick,
            'vw2': self.vw2,
            'vw6': self.vw6,
            'vw8': self.vw8,
            'm_estop_latch': self.m_estop_latch,
            'm_relay_fault': self.m_relay_fault,
            'm_init_done': self.m_init_done,
            'i_estop': self.i_estop,
            'q_alarm_sound': self.q[(0, 7)],
            'q_alarm_light': self.q[(1, 0)],
            'qb0': self.get_qb0(),
        }


if __name__ == '__main__':
    print("=== PLC仿真器自检 v2.0 ===")
    plc = PLCSim()
    plc.run_cold_start()
    print(f"冷启动后: VW2={plc.vw2}(期望0), VW6={plc.vw6}(期望0), InitDone={plc.m_init_done}(期望True)")
    assert plc.vw2 == 0, f"冷启动VW2应为0, 实际{plc.vw2}"
    assert plc.m_init_done, "冷启动后InitDone应为True"
    print("✓ 冷启动自检通过")
    plc.trigger_estop()
    print(f"急停后: VW2={plc.vw2}(期望99), V300.4={plc.m_estop_latch}(期望True)")
    assert plc.vw2 == 99
    assert plc.m_estop_latch
    print("✓ 急停自检通过")
