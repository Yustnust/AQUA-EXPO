"""
PLC 寄存器映射表
基于 docs/HMI-PLC变量地址表_v1.0.md 定义

S7-200 SMART Modbus TCP 保持寄存器映射规则：
- 40001 -> VW0
- 40002 -> VW2
- 40001 + n -> VW(2*n)

因此：
- pymodbus 0-based 地址 = (V 地址 / 2)
- VW2 对应地址 1
- VD10 对应地址 5~6（2 个寄存器）
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DataType(str, Enum):
    BOOL = "bool"          # 位变量，需按字读取后位解析
    INT16 = "int16"        # 有符号字
    UINT16 = "uint16"      # 无符号字
    INT32 = "int32"        # 有符号双字
    UINT32 = "uint32"      # 无符号双字
    FLOAT32 = "float32"    # REAL / 32 位浮点数
    BYTE = "byte"          # 字节（从字中拆分）


@dataclass
class RegisterDef:
    """单个寄存器/变量定义。"""
    name: str              # Web HMI 字段名
    v_addr: int            # PLC V 区起始地址
    dtype: DataType        # 数据类型
    reg_count: int         # 占用的 Modbus 寄存器数量
    bit_index: Optional[int] = None  # BOOL 类型对应的位号（0~15，V 区内）
    scale: float = 1.0     # 量程缩放（暂未使用，保留）
    writable: bool = False # 是否允许 HMI 写入
    note: str = ""         # 备注

    @property
    def reg_addr(self) -> int:
        """pymodbus 0-based 保持寄存器地址。"""
        return self.v_addr // 2


# ============================================================
# 按 V 地址排序的寄存器块定义，用于批量读取
# 每个块包含：起始 V 地址、结束 V 地址（含）、说明
# ============================================================
READ_BLOCKS = [
    {"start_v": 0,   "end_v": 6,   "note": "命令位与状态位 V0.0~V3.7"},
    {"start_v": 2,   "end_v": 10,  "note": "状态机、泵状态、报警码、轮次"},
    {"start_v": 10,  "end_v": 96,  "note": "工艺参数与过程值 VD10~VD94"},
    {"start_v": 182, "end_v": 186, "note": "纠偏模式/结果 VW182/VW184"},
    {"start_v": 200, "end_v": 224, "note": "手动命令位 + Modbus 注射泵缓冲"},
    {"start_v": 300, "end_v": 304, "note": "报警字节 VB300~VB303（按 VW300/VW302 读取）"},
    {"start_v": 304, "end_v": 308, "note": "初始化完成标志等"},
    {"start_v": 308, "end_v": 372, "note": "额外过程值 VD308~VD370"},
    {"start_v": 350, "end_v": 374, "note": "AQEX-36 迁移参数 VD350~VD370"},
]


# ============================================================
# 变量定义清单
# 命名规则：小写 + 下划线，去掉 U1_ 前缀（前端按单元索引）
# ============================================================
VARIABLES = [
    # ---- V0/V1 命令与状态位 ----
    RegisterDef("cmd_start",              0, DataType.BOOL,   1, bit_index=0,  writable=True,  note="启动实验命令"),
    RegisterDef("cmd_pause",              0, DataType.BOOL,   1, bit_index=1,  writable=True,  note="暂停命令(预留)"),
    RegisterDef("cmd_stop",               0, DataType.BOOL,   1, bit_index=2,  writable=True,  note="停止实验命令"),
    RegisterDef("cmd_ack_alarm",          0, DataType.BOOL,   1, bit_index=3,  writable=True,  note="报警确认命令"),
    RegisterDef("cmd_mute",               0, DataType.BOOL,   1, bit_index=4,  writable=True,  note="消音命令"),
    RegisterDef("cmd_force_tank_a_empty", 0, DataType.BOOL,   1, bit_index=5,  writable=True,  note="强制上缸=空(预留)"),
    RegisterDef("cmd_force_tank_a_full",  0, DataType.BOOL,   1, bit_index=6,  writable=True,  note="强制上缸=满(预留)"),
    RegisterDef("cmd_safety_relay_ack",   0, DataType.BOOL,   1, bit_index=7,  writable=True,  note="安全继电器故障高权限确认"),

    RegisterDef("sta_start_ack",          1, DataType.BOOL,   1, bit_index=0,  writable=False, note="启动命令已接收"),
    RegisterDef("sta_pause_ack",          1, DataType.BOOL,   1, bit_index=1,  writable=False, note="暂停命令已接收(预留)"),
    RegisterDef("sta_stop_ack",           1, DataType.BOOL,   1, bit_index=2,  writable=False, note="停止命令已接收"),
    RegisterDef("sta_alarm_ack_done",     1, DataType.BOOL,   1, bit_index=3,  writable=False, note="报警确认已执行"),
    RegisterDef("sta_mute_done",          1, DataType.BOOL,   1, bit_index=4,  writable=False, note="消音已执行"),
    RegisterDef("sta_force_done",         1, DataType.BOOL,   1, bit_index=5,  writable=False, note="状态强制修正已执行"),
    RegisterDef("sta_tank_a_state",       1, DataType.BOOL,   1, bit_index=6,  writable=False, note="上缸状态 0=空 1=满"),
    RegisterDef("sta_tank_b_state",       1, DataType.BOOL,   1, bit_index=7,  writable=False, note="下缸状态 0=空 1=满"),

    # ---- V2/V3 手动命令位 ----
    RegisterDef("cmd_manual_valve_a_open",   2, DataType.BOOL, 1, bit_index=4, writable=True, note="手动开阀A"),
    RegisterDef("cmd_manual_valve_a_close",  2, DataType.BOOL, 1, bit_index=5, writable=True, note="手动关阀A"),
    RegisterDef("cmd_manual_valve_b_open",   2, DataType.BOOL, 1, bit_index=6, writable=True, note="手动开阀B"),
    RegisterDef("cmd_manual_valve_b_close",  2, DataType.BOOL, 1, bit_index=7, writable=True, note="手动关阀B"),
    RegisterDef("cmd_manual_valve_c_open",   3, DataType.BOOL, 1, bit_index=0, writable=True, note="手动开阀C"),
    RegisterDef("cmd_manual_valve_c_close",  3, DataType.BOOL, 1, bit_index=1, writable=True, note="手动关阀C"),
    RegisterDef("cmd_manual_pump1_on",       3, DataType.BOOL, 1, bit_index=2, writable=True, note="手动启动潜水泵1"),
    RegisterDef("cmd_manual_pump1_off",      3, DataType.BOOL, 1, bit_index=3, writable=True, note="手动停止潜水泵1"),
    RegisterDef("cmd_manual_pump2_on",       3, DataType.BOOL, 1, bit_index=4, writable=True, note="手动启动潜水泵2(预留)"),
    RegisterDef("cmd_manual_pump2_off",      3, DataType.BOOL, 1, bit_index=5, writable=True, note="手动停止潜水泵2(预留)"),

    # ---- 状态/模式位 ----
    RegisterDef("m_alarm_ack_mode", 200, DataType.BOOL, 1, bit_index=0, writable=True,  note="报警确认模式 0=自动恢复 1=人工确认"),
    RegisterDef("m_init_done",      304, DataType.BOOL, 1, bit_index=0, writable=False, note="PLC初始化完成标志"),

    # ---- 字变量 ----
    RegisterDef("state_machine",     2,  DataType.INT16,  1, writable=False, note="状态机当前状态"),
    RegisterDef("pump_status",       4,  DataType.INT16,  1, writable=False, note="注射泵状态码"),
    RegisterDef("alarm_code",        6,  DataType.INT16,  1, writable=False, note="当前最高优先级报警码"),
    RegisterDef("round_count",       8,  DataType.INT16,  1, writable=False, note="实验轮次计数"),
    RegisterDef("corr_mode",        182, DataType.INT16,  1, writable=True,  note="纠偏模式"),
    RegisterDef("corr_result",      184, DataType.INT16,  1, writable=True,  note="纠偏结果"),

    # ---- Modbus 注射泵缓冲字 ----
    RegisterDef("mb_pump_reset",      202, DataType.INT16, 1, writable=True,  note="注射泵复位命令 40003"),
    RegisterDef("mb_pump_aspirate",   204, DataType.INT16, 1, writable=True,  note="注射泵抽液目标步数 40006"),
    RegisterDef("mb_pump_dispense",   206, DataType.INT16, 1, writable=True,  note="注射泵排液目标步数 40007"),
    RegisterDef("mb_pump_speed_start",208, DataType.INT16, 1, writable=True,  note="注射泵启动速度 40009"),
    RegisterDef("mb_pump_speed_max",  210, DataType.INT16, 1, writable=True,  note="注射泵最高速度 40010"),
    RegisterDef("mb_pump_speed_cutoff",212,DataType.INT16, 1, writable=True,  note="注射泵截止速度 40011"),
    RegisterDef("mb_pump_position",   222, DataType.INT16, 1, writable=False, note="注射泵位置反馈 41007"),

    # ---- 双字浮点参数 ----
    RegisterDef("c_set",                  10, DataType.FLOAT32, 2, writable=True,  note="目标浓度设定值(%)"),
    RegisterDef("c_stock",                14, DataType.FLOAT32, 2, writable=True,  note="母液浓度(%)"),
    RegisterDef("experiment_target",        24, DataType.FLOAT32, 2, writable=True,  note="实验时长目标(min)"),
    RegisterDef("premix_time",              28, DataType.FLOAT32, 2, writable=True,  note="预循环标称时长S2(s)"),
    RegisterDef("premix_time_minsafe",      32, DataType.FLOAT32, 2, writable=True,  note="预循环压缩下限(s)"),
    RegisterDef("rest_time",                36, DataType.FLOAT32, 2, writable=True,  note="静止等候标称S3.5(s)"),
    RegisterDef("rest_time_min",            40, DataType.FLOAT32, 2, writable=True,  note="静止等候压缩下限(s)"),
    RegisterDef("cycle_extend_max",         44, DataType.FLOAT32, 2, writable=True,  note="换水周期顺延上限(min)"),
    RegisterDef("timeout_valve_c",          54, DataType.FLOAT32, 2, writable=True,  note="阀C动作超时(s)"),
    RegisterDef("timeout_pump1",            58, DataType.FLOAT32, 2, writable=True,  note="潜水泵1动作超时(s)"),
    RegisterDef("timeout_pump2",            62, DataType.FLOAT32, 2, writable=True,  note="潜水泵2动作超时(s)"),
    RegisterDef("delay_valve_a_verify",     66, DataType.FLOAT32, 2, writable=True,  note="阀A关闭后延时验证时长(s)"),
    RegisterDef("s1_actual",                70, DataType.FLOAT32, 2, writable=False, note="S1上缸进水实测时长(s)"),
    RegisterDef("s4_actual",                74, DataType.FLOAT32, 2, writable=False, note="S4上→下转移实测时长(s)"),
    RegisterDef("s6_actual",                78, DataType.FLOAT32, 2, writable=False, note="S6下缸排水实测时长(s)"),
    RegisterDef("flowmeter_snapshot",       82, DataType.FLOAT32, 2, writable=False, note="阀A开启瞬间流量计累计快照"),
    RegisterDef("flowmeter_current",        86, DataType.FLOAT32, 2, writable=False, note="流量计当前累计值(L)"),
    RegisterDef("current_inlet_volume",     90, DataType.FLOAT32, 2, writable=False, note="本次进水量(L)"),
    RegisterDef("flowrate_instant",         94, DataType.FLOAT32, 2, writable=False, note="瞬时流速(L/min)"),
    RegisterDef("dose_steps",              102, DataType.FLOAT32, 2, writable=False, note="本轮加药目标步数"),
    RegisterDef("t_rolling",               112, DataType.FLOAT32, 2, writable=True,  note="滚动实测T总时长(s)"),
    RegisterDef("s6_rolling",              116, DataType.FLOAT32, 2, writable=True,  note="滚动实测S6排水时长(s)"),
    RegisterDef("s2_target",               120, DataType.FLOAT32, 2, writable=True,  note="本轮S2实际执行目标(s)"),
    RegisterDef("resttime_target",         124, DataType.FLOAT32, 2, writable=True,  note="本轮S3.5实际执行目标(s)"),
    RegisterDef("pump_speed_start",        132, DataType.FLOAT32, 2, writable=True,  note="注射泵启动速度(Hz)"),
    RegisterDef("pump_speed_max",          136, DataType.FLOAT32, 2, writable=True,  note="注射泵最高速度(Hz)"),
    RegisterDef("pump_speed_cutoff",       140, DataType.FLOAT32, 2, writable=True,  note="注射泵截止速度(Hz)"),
    RegisterDef("available",               150, DataType.FLOAT32, 2, writable=False, note="剩余可用时间(min)"),
    RegisterDef("corr_needed",             154, DataType.FLOAT32, 2, writable=False, note="纠偏Needed(min)"),
    RegisterDef("s3_estimate",             174, DataType.FLOAT32, 2, writable=True,  note="S3估算时长(s)"),
    RegisterDef("s5_elapsed",              178, DataType.FLOAT32, 2, writable=False, note="S5累计运行时长(min)"),
    RegisterDef("flowmeter_close_snapshot",308, DataType.FLOAT32, 2, writable=False, note="阀A关闭后流量计快照"),
    RegisterDef("leak_diff",               312, DataType.FLOAT32, 2, writable=False, note="阀A内漏差值"),
    RegisterDef("target_inlet_volume",     316, DataType.FLOAT32, 2, writable=False, note="PLC计算的目标进水量(L)"),
    RegisterDef("timeout_valve_c_x10",     328, DataType.FLOAT32, 2, writable=False, note="阀C超时×10校验值"),
    RegisterDef("step_resolution",         350, DataType.FLOAT32, 2, writable=True,  note="注射泵单步分辨率(µL/步)"),
    RegisterDef("cycle_setpoint",          354, DataType.FLOAT32, 2, writable=True,  note="换水周期设定(min)"),
    RegisterDef("timeout_valve_a",         358, DataType.FLOAT32, 2, writable=True,  note="阀A动作超时(s)"),
    RegisterDef("timeout_valve_b",         362, DataType.FLOAT32, 2, writable=True,  note="阀B动作超时(s)"),
    RegisterDef("experiment_duration_accum",366,DataType.FLOAT32,2, writable=False, note="实验时长累加(min)"),
    RegisterDef("vol_target",              370, DataType.FLOAT32, 2, writable=False, note="本轮目标抽取母液体积(µL)"),

    # ---- 报警字节（从 VW300/VW302 拆分）----
    RegisterDef("alarm_byte_0", 300, DataType.BYTE, 1, writable=False, note="报警字节0: V300.0~V300.7"),
    RegisterDef("alarm_byte_1", 301, DataType.BYTE, 1, writable=False, note="报警字节1: V301.0~V301.7"),
    RegisterDef("alarm_byte_2", 302, DataType.BYTE, 1, writable=False, note="报警字节2: V302.0~V302.7"),
    RegisterDef("alarm_byte_3", 303, DataType.BYTE, 1, writable=False, note="报警字节3: V303.0~V303.7"),
]


# 建立快速索引
VARIABLE_MAP = {v.name: v for v in VARIABLES}


def get_variable(name: str) -> Optional[RegisterDef]:
    """按字段名获取变量定义。"""
    return VARIABLE_MAP.get(name)
