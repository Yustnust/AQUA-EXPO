#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 McgsPro 设备信息导入 CSV，格式与 McgsPro 3.3.6 导出格式一致。

每个子设备（设备0~7）对应一个 CSV 文件，可直接通过"设备信息导入"批量导入。
文件头中的"组态设备名称"必须与子设备名一致，否则报"设备名称不符合"。
"""

import csv
import os
import re

OUT_DIR = os.environ.get("MCGS_CSV_OUT", os.path.dirname(__file__))

# 驱动信息头（从 McgsPro 导出文件复制）
DRV_PATH = r"d:\program files\mcgspro\program\drivers\plc\西门子\smart200\smart200_ex.ui"
DRV_NAME = "西门子_S7_Smart200_以太网"
DRV_VER = "7.001"

# 每单元变量定义： (通道类型, 数据类型, 地址, 个数, 读写, 基础变量名, 备注)
# 数据类型：位变量用"第XX位"，字/双字用 McgsPro 下拉框中的中文名称
rows = []

# V0/V1 位区
bit_rows = [
    (0, 0, "CMD_Start", "启动实验命令"),
    (0, 1, "Reserved_CMD_Pause", "暂停命令(PLC未实现,预留)"),
    (0, 2, "CMD_Stop", "停止实验命令"),
    (0, 3, "CMD_AckAlarm", "报警确认命令"),
    (0, 4, "CMD_Mute", "消音命令"),
    (0, 5, "Reserved_CMD_ForceTankA_Empty", "强制上缸=空(PLC未实现,预留)"),
    (0, 6, "Reserved_CMD_ForceTankA_Full", "强制上缸=满(PLC未实现,预留)"),
    (0, 7, "CMD_SafetyRelayAck", "安全继电器故障高权限确认"),
    (1, 0, "STA_StartAck", "启动命令已接收"),
    (1, 1, "Reserved_STA_PauseAck", "暂停命令已接收(预留)"),
    (1, 2, "STA_StopAck", "停止命令已接收"),
    (1, 3, "STA_AlarmAckDone", "报警确认已执行"),
    (1, 4, "STA_MuteDone", "消音已执行"),
    (1, 5, "STA_ForceDone", "状态强制修正已执行"),
    (1, 6, "STA_TankA_State", "上缸状态 0=空 1=满"),
    (1, 7, "STA_TankB_State", "下缸状态 0=空 1=满"),
]
for byte, bit, name, note in bit_rows:
    rows.append(("V区变量", f"第{bit:02d}位", byte, 1, "读写" if byte == 0 else "只读", name, note))

# DI 输入继电器（手动控制页阀门/泵反馈等）
dio_rows = [
    # I 输入继电器
    (0, 0, "DI_FlowSwitch_A", "流量开关A(阀A开启后有流)"),
    (0, 1, "DI_FlowSwitch_B", "流量开关B(阀B开启后有流)"),
    (0, 2, "DI_FlowSwitch_C", "流量开关C(阀C开启后有流)"),
    (1, 1, "DI_EStop", "急停信号反馈(ON=正常 OFF=急停触发)"),
    (1, 2, "DI_SafetyRelay_FB", "安全继电器反馈(ON=正常)"),
    (1, 3, "DI_ValveA_Open", "阀A开到位反馈"),
    (1, 4, "DI_ValveA_Close", "阀A关到位反馈"),
    (1, 5, "DI_ValveB_Open", "阀B开到位反馈"),
    (1, 6, "DI_ValveB_Close", "阀B关到位反馈"),
    (1, 7, "DI_ValveC_Open", "阀C开到位反馈"),
    (2, 0, "DI_ValveC_Close", "阀C关到位反馈"),
]
for byte, bit, name, note in dio_rows:
    rows.append(("I输入继电器", f"第{bit:02d}位", byte, 1, "只读", name, note))

# 字/双字区（按地址排序）
word_rows = [
    ("V区变量", "16位有符号二进制", 2, 1, "只读", "VW2_StateMachine", "状态机当前状态(S0~S7/S_ERROR)"),
    ("V区变量", "16位有符号二进制", 4, 1, "只读", "VW4_PumpStatus", "注射泵状态码(映射41001)"),
    ("V区变量", "16位有符号二进制", 6, 1, "只读", "VW6_AlarmCode", "当前最高优先级报警码"),
    ("V区变量", "16位有符号二进制", 8, 1, "只读", "VW8_RoundCount", "实验轮次计数"),
    ("V区变量", "32位浮点数", 10, 1, "读写", "VD_C_Set", "目标浓度设定值(%)"),
    ("V区变量", "32位浮点数", 14, 1, "读写", "VD_C_Stock", "母液浓度(%)"),
    ("V区变量", "32位浮点数", 24, 1, "读写", "VD_ExperimentTarget", "实验时长目标(min)"),
    ("V区变量", "32位浮点数", 28, 1, "读写", "VD_PreMixTime", "预循环标称时长S2(s)"),
    ("V区变量", "32位浮点数", 32, 1, "读写", "VD_PreMixTime_MinSafe", "预循环压缩下限(s)"),
    ("V区变量", "32位浮点数", 36, 1, "读写", "VD_RestTime", "静止等候标称S3.5(s)"),
    ("V区变量", "32位浮点数", 40, 1, "读写", "VD_RestTime_Min", "静止等候压缩下限(s)"),
    ("V区变量", "32位浮点数", 44, 1, "读写", "VD_CycleExtend_Max", "换水周期顺延上限(min)"),
    ("V区变量", "32位浮点数", 54, 1, "读写", "VD_Timeout_ValveC", "阀C动作超时(s)"),
    ("V区变量", "32位浮点数", 58, 1, "读写", "VD_Timeout_Pump1", "潜水泵1动作超时(s)"),
    ("V区变量", "32位浮点数", 62, 1, "读写", "VD_Timeout_Pump2", "潜水泵2动作超时(s)"),
    ("V区变量", "32位浮点数", 66, 1, "读写", "VD_Delay_ValveA_Verify", "阀A关闭后延时验证时长(s)"),
    ("V区变量", "32位浮点数", 70, 1, "只读", "VD_S1_Actual", "S1上缸进水实测时长(s)"),
    ("V区变量", "32位浮点数", 74, 1, "只读", "VD_S4_Actual", "S4上→下转移实测时长(s)"),
    ("V区变量", "32位浮点数", 78, 1, "只读", "VD_S6_Actual", "S6下缸排水实测时长(s)"),
    ("V区变量", "32位浮点数", 82, 1, "只读", "VD_FlowMeter_Snapshot", "阀A开启瞬间流量计累计快照"),
    ("V区变量", "32位浮点数", 86, 1, "只读", "VD_FlowMeter_Current", "流量计当前累计值(L)"),
    ("V区变量", "32位浮点数", 90, 1, "只读", "VD_Current_InletVolume", "本次进水量=Current-Snapshot(L)"),
    ("V区变量", "32位浮点数", 94, 1, "只读", "VD_FlowRate_Instant", "瞬时流速(L/min)"),
    ("V区变量", "32位浮点数", 102, 1, "只读", "VD_Dose_Steps", "本轮加药目标步数"),
    ("V区变量", "32位浮点数", 112, 1, "读写", "VD_T_Rolling", "滚动实测T总时长(s)"),
    ("V区变量", "32位浮点数", 116, 1, "读写", "VD_S6_Rolling", "滚动实测S6排水时长(s)"),
    ("V区变量", "32位浮点数", 120, 1, "读写", "VD_S2_Target", "本轮S2实际执行目标(s)"),
    ("V区变量", "32位浮点数", 124, 1, "读写", "VD_RestTime_Target", "本轮S3.5实际执行目标(s)"),
    ("V区变量", "32位浮点数", 132, 1, "读写", "VD_PumpSpeed_Start", "注射泵启动速度(Hz)"),
    ("V区变量", "32位浮点数", 136, 1, "读写", "VD_PumpSpeed_Max", "注射泵最高速度(Hz)"),
    ("V区变量", "32位浮点数", 140, 1, "读写", "VD_PumpSpeed_Cutoff", "注射泵截止速度(Hz)"),
    ("V区变量", "32位浮点数", 150, 1, "只读", "VD_Available", "剩余可用时间(min)"),
    ("V区变量", "32位浮点数", 154, 1, "只读", "VD_Corr_Needed", "纠偏Needed(min)"),
    ("V区变量", "32位浮点数", 174, 1, "读写", "VD_S3_Estimate", "S3估算时长(s)"),
    ("V区变量", "32位浮点数", 178, 1, "只读", "VD_S5_Elapsed", "S5累计运行时长(min)"),
    ("V区变量", "16位有符号二进制", 182, 1, "读写", "VW_Corr_Mode", "纠偏模式"),
    ("V区变量", "16位有符号二进制", 184, 1, "读写", "VW_Corr_Result", "纠偏结果"),
    ("V区变量", "32位浮点数", 308, 1, "只读", "VD_FlowMeter_CloseSnapshot", "阀A关闭后流量计快照(内漏诊断)"),
    ("V区变量", "32位浮点数", 312, 1, "只读", "VD_LeakDiff", "阀A内漏差值"),
    ("V区变量", "32位浮点数", 316, 1, "只读", "VD_TargetInletVolume", "PLC计算的目标进水量(L)"),
    ("V区变量", "32位浮点数", 328, 1, "只读", "VD_Timeout_ValveC_x10", "阀C超时×10校验值"),
    ("V区变量", "32位浮点数", 350, 1, "读写", "VD_StepResolution", "注射泵单步分辨率(µL/步) AQEX-36:VD18→VD350"),
    ("V区变量", "32位浮点数", 354, 1, "读写", "VD_CycleSetpoint", "换水周期设定(min) AQEX-36:VD20→VD354"),
    ("V区变量", "32位浮点数", 358, 1, "读写", "VD_Timeout_ValveA", "阀A动作超时(s) AQEX-36:VD48→VD358"),
    ("V区变量", "32位浮点数", 362, 1, "读写", "VD_Timeout_ValveB", "阀B动作超时(s) AQEX-36:VD50→VD362"),
    ("V区变量", "32位浮点数", 364, 1, "只读", "VD_ExpTotal_Flow", "本次实验累计流量(L)"),
    ("V区变量", "32位浮点数", 366, 1, "只读", "VD_ExperimentDuration_Accum", "实验时长累加(min) AQEX-36:VD96→VD366"),
    ("V区变量", "32位浮点数", 370, 1, "只读", "VD_Vol_Target", "本轮目标抽取母液体积(µL) AQEX-36:VD98→VD370"),
    ("V区变量", "32位浮点数", 372, 1, "只读", "VD_Remaining_Vol", "S3加药剩余待加体积(µL)"),
    ("V区变量", "32位浮点数", 378, 1, "只读", "VD_Dosed_Volume_Total", "本次实验累计加药量(µL)"),
]
rows.extend(word_rows)

# 报警字：按位读取 V300.0~V303.7，用于报警滚动条/指示灯阵列
alarm_bits = [
    # VB300 高优先级
    (300, 0, "Alarm_Overflow_AHigh", "上缸漫溢-立即检查液位计A与进水阀A"),
    (300, 1, "Alarm_Overflow_BHigh", "下缸漫溢-立即检查液位计B与转移阀B"),
    (300, 2, "Alarm_NCValve_Top", "上缸NC阀已动作-阀A失效保护触发"),
    (300, 3, "Alarm_NCValve_Bottom", "下缸NC阀已动作-阀B/液位计B故障保护触发"),
    (300, 4, "EStop_Latch", "急停触发-现场已急停，等待物理系统复位"),
    (300, 5, "Alarm_SafetyRelay", "安全继电器故障-立即检查动力回路"),
    (300, 6, "Alarm_ScheduleLag", "配液节奏严重滞后-三层纠偏已用尽"),
    (300, 7, "Alarm_ScheduleLag_Warn", "配液节奏滞后提示-已启用第2层顺延"),
    # VB301 阀门A类一般故障
    (301, 0, "Alarm_ValveA_CloseFlow", "阀A关闭后延时验证仍有流-检查阀A内漏"),
    (301, 1, "Alarm_ValveA_Leak", "阀A内漏-已关但流量计计量值仍增长"),
    (301, 2, "Alarm_ValveA_CloseTimeout", "阀A关到位超时-检查阀A机械或限位"),
    (301, 3, "Alarm_ValveA_CloseLeak", "阀A关到位但仍有流-内漏"),
    (301, 4, "Alarm_ValveA_OpenTimeout", "阀A开到位超时-检查阀A机械或限位"),
    (301, 5, "Alarm_ValveA_OpenNoFlow", "阀A开到位但无流-检查上游供水/堵塞"),
    (301, 6, "Alarm_ValveA_S1Start", "S5触发新一轮S1时上缸状态非空"),
    (301, 7, "Alarm_Reserved_301_7", "预留扩展位"),
    # VB302 阀门B/C类一般故障
    (302, 0, "Alarm_ValveB_Diag", "阀B四态诊断异常-检查阀B与液位"),
    (302, 1, "Alarm_ValveB_OpenTimeout", "阀B开到位超时-检查阀B机械或限位"),
    (302, 2, "Alarm_ValveB_OpenNoFlow", "阀B开到位但无流-检查管路"),
    (302, 3, "Alarm_ValveB_CloseTimeout", "阀B关到位超时-检查阀B机械或限位"),
    (302, 4, "Alarm_ValveB_CloseLeak", "阀B关到位但仍有流-内漏"),
    (302, 5, "Alarm_ValveC_Diag", "阀C四态诊断异常-检查阀C与液位"),
    (302, 6, "Alarm_ValveC_OpenTimeout", "阀C开到位超时-检查阀C机械或限位"),
    (302, 7, "Alarm_ValveC_OpenNoFlow", "阀C开到位但无流-检查排水管路"),
    # VB303 其他一般故障
    (303, 0, "Alarm_ValveC_CloseTimeout", "阀C关到位超时-检查阀C机械或限位"),
    (303, 1, "Alarm_ValveC_CloseLeak", "阀C关到位但仍有流-内漏"),
    (303, 2, "Alarm_Pump1_Abnormal", "潜水泵1启动后超时无流-检查泵1或管路"),
    (303, 3, "Alarm_Pump2_Abnormal", "潜水泵2启动后超时无流-检查泵2或管路"),
    (303, 4, "Alarm_SyringePump", "注射泵通讯/动作异常-检查Modbus与泵状态"),
    (303, 5, "Alarm_RTC_Lost", "RTC时钟丢失-请校时"),
    (303, 6, "Alarm_FlowSwitch_Instant", "流量开关瞬时异常-检查流量开关信号"),
    (303, 7, "Alarm_Reserved_303_7", "预留扩展位"),
]
for byte, bit, name, note in alarm_bits:
    rows.append(("V区变量", f"第{bit:02d}位", byte, 1, "只读", name, note))

# 手动命令位 V2.4~V3.5
manual_bits = [
    (2, 4, "CMD_Manual_ValveA_Open", "手动开阀A"),
    (2, 5, "CMD_Manual_ValveA_Close", "手动关阀A"),
    (2, 6, "CMD_Manual_ValveB_Open", "手动开阀B"),
    (2, 7, "CMD_Manual_ValveB_Close", "手动关阀B"),
    (3, 0, "CMD_Manual_ValveC_Open", "手动开阀C"),
    (3, 1, "CMD_Manual_ValveC_Close", "手动关阀C"),
    (3, 2, "CMD_Manual_Pump1_On", "手动启动潜水泵1"),
    (3, 3, "CMD_Manual_Pump1_Off", "手动停止潜水泵1"),
    (3, 4, "CMD_Manual_Pump2_On", "手动启动潜水泵2(V3.4)"),
    (3, 5, "CMD_Manual_Pump2_Off", "手动停止潜水泵2(V3.5)"),
]
for byte, bit, name, note in manual_bits:
    rows.append(("V区变量", f"第{bit:02d}位", byte, 1, "读写", name, note))

# Modbus 注射泵缓冲字
mb_rows = [
    ("V区变量", "16位有符号二进制", 202, 1, "读写", "MB_Pump_Reset", "注射泵复位命令 40003"),
    ("V区变量", "16位有符号二进制", 204, 1, "读写", "MB_Pump_Aspirate", "注射泵抽液目标步数 40006"),
    ("V区变量", "16位有符号二进制", 206, 1, "读写", "MB_Pump_Dispense", "注射泵排液目标步数 40007"),
    ("V区变量", "16位有符号二进制", 208, 1, "读写", "MB_Pump_SpeedStart", "注射泵启动速度 40009(Hz)"),
    ("V区变量", "16位有符号二进制", 210, 1, "读写", "MB_Pump_SpeedMax", "注射泵最高速度 40010(Hz)"),
    ("V区变量", "16位有符号二进制", 212, 1, "读写", "MB_Pump_SpeedCutoff", "注射泵截止速度 40011(Hz)"),
    ("V区变量", "16位有符号二进制", 222, 1, "只读", "MB_Pump_Position", "注射泵位置反馈 41007"),
]
rows.extend(mb_rows)

# 状态/模式位
rows.append(("V区变量", "第00位", 200, 1, "读写", "M_AlarmAckMode", "报警确认模式 0=自动恢复 1=人工确认"))
rows.append(("V区变量", "第00位", 304, 1, "只读", "M_InitDone", "PLC初始化完成标志"))


def parse_dtype(dtype: str):
    """解析数据类型，返回 (mcgs数据类型, 位号或None)。"""
    m = re.match(r"第(\d{2})位", dtype)
    if m:
        return "通道的第" + m.group(1) + "位", int(m.group(1))
    mapping = {
        "16位有符号二进制": "16位 有符号二进制",
        "32位浮点数": "32位 浮点数",
        "8位无符号": "8位无符号二进制",
    }
    if dtype in mapping:
        return mapping[dtype], None
    raise ValueError(f"未映射的数据类型: {dtype}")


def mcgs_var_type(mcgs_dtype: str, bit: int | None) -> str:
    """McgsPro 变量类型：只有位通道用 INTEGER，字/字节/浮点数值用 SINGLE。"""
    if bit is not None:
        return "INTEGER"
    return "SINGLE"


def mcgs_channel_name(rw: str, addr: int, mcgs_dtype: str, bit: int | None, typ: str) -> str:
    """生成 McgsPro 通道名称列（如"读写V000.0"、"只读VWB002"、"只读I001.3"）。"""
    action = "读写" if rw == "读写" else "只读"
    if bit is not None:
        prefix = "V"
        if typ == "I输入继电器":
            prefix = "I"
        elif typ == "Q输出继电器":
            prefix = "Q"
        return f"{action}{prefix}{addr:03d}.{bit}"
    if "16位" in mcgs_dtype:
        return f"{action}VWB{addr:03d}"
    if "32位" in mcgs_dtype:
        return f"{action}VDF{addr:03d}"
    if "8位" in mcgs_dtype:
        return f"{action}VBB{addr:03d}"
    raise ValueError(f"无法生成通道名称: {mcgs_dtype}")


def unit_rows(unit: int):
    """为指定单元添加 U{unit}_ 前缀。"""
    prefix = f"U{unit}_"
    out = []
    for typ, dtype, addr, count, rw, name, note in rows:
        out.append((typ, dtype, addr, count, rw, prefix + name, note))
    return out


def write_unit_csv(unit: int) -> int:
    dev_id = unit - 1
    filename = os.path.join(OUT_DIR, f"McgsPro变量导入_单元{unit}.csv")
    with open(filename, "w", newline="", encoding="gbk") as f:
        w = csv.writer(f)
        # McgsPro 设备信息文件头
        w.writerow([f"组态设备名称:设备{dev_id}"])
        w.writerow([f"驱动库文件路径:{DRV_PATH}"])
        w.writerow([f"驱动构件名称:{DRV_NAME}"])
        w.writerow([f"驱动构件版本:{DRV_VER}"])
        # 表头
        w.writerow([
            "通道号", "变量名", "变量类型", "通道名称", "读写类型",
            "寄存器名称", "数据类型", "寄存器地址", "地址偏移",
            "通道采集频次", "通道处理"
        ])

        channel_no = 0
        for typ, dtype, addr, _count, rw, name, _note in unit_rows(unit):
            mcgs_dtype, bit = parse_dtype(dtype)
            var_type = mcgs_var_type(mcgs_dtype, bit)
            ch_name = mcgs_channel_name(rw, addr, mcgs_dtype, bit, typ)
            rw_type = "读写" if rw == "读写" else "只读"
            if typ == "V区变量":
                reg_name = "V数据寄存器"
            elif typ == "I输入继电器":
                reg_name = "I输入继电器"
            elif typ == "Q输出继电器":
                reg_name = "Q输出继电器"
            else:
                reg_name = typ
            w.writerow([
                channel_no,      # 通道号
                name,            # 变量名
                var_type,        # 变量类型
                ch_name,         # 通道名称
                rw_type,         # 读写类型
                reg_name,        # 寄存器名称
                mcgs_dtype,      # 数据类型
                addr,            # 寄存器地址
                "",              # 地址偏移
                "1",             # 通道采集频次
                "",              # 通道处理
            ])
            channel_no += 1

    print(f"单元{unit}: {channel_no} 通道 -> {filename}")
    return channel_no


if __name__ == "__main__":
    total = 0
    for unit in range(1, 9):
        total += write_unit_csv(unit)
    print(f"\n全部完成：8 单元，共 {total} 通道")
