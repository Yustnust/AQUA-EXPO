#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 McgsPro 变量导入 CSV v2.1，按 HMI-PLC 变量地址表 v1.3 同步变量名/地址/读写属性。"""

import csv
import os

OUT = os.path.join(os.path.dirname(__file__), "McgsPro变量导入_8单元_v2.1.csv")

# 每单元变量定义： (类型, 数据类型, 地址, 个数, 读写, 基础变量名, 备注)
# 类型固定为 V区变量；数据类型为 McgsPro 通道数据类型中文描述；地址为整数（位地址用字节地址）
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
    ("V区变量", "32位浮点数", 366, 1, "只读", "VD_ExperimentDuration_Accum", "实验时长累加(min) AQEX-36:VD96→VD366"),
    ("V区变量", "32位浮点数", 370, 1, "只读", "VD_Vol_Target", "本轮目标抽取母液体积(µL) AQEX-36:VD98→VD370"),
]
rows.extend(word_rows)

# 报警字节
alarm_bytes = [
    (300, "VB300_AlarmByte0", "报警字VB300(漫溢+急停+安全继电器+节奏滞后)"),
    (301, "VB301_AlarmByte1", "报警字VB301(阀A诊断)"),
    (302, "VB302_AlarmByte2", "报警字VB302(阀B/C/泵诊断)"),
    (303, "VB303_AlarmByte3", "报警字VB303(其他)"),
]
for addr, name, note in alarm_bytes:
    rows.append(("V区变量", "8位无符号", addr, 1, "只读", name, note))

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
    (3, 4, "CMD_Manual_Pump2_On", "手动启动潜水泵2(预留,V3.4)"),
    (3, 5, "CMD_Manual_Pump2_Off", "手动停止潜水泵2(预留,V3.5)"),
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


def unit_rows(unit):
    prefix = f"U{unit}_"
    out = []
    for typ, dtype, addr, count, rw, name, note in rows:
        out.append((typ, dtype, addr, count, rw, prefix + name, note))
    return out


with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["通道类型", "数据类型", "通道地址", "通道个数", "读写方式", "连接变量", "备注"])
    total = 0
    for unit in range(1, 9):
        w.writerow([f"# ===== Unit {unit} (PLC_0{unit}, 192.168.2.10{unit}) ====="])
        for row in unit_rows(unit):
            w.writerow(row)
            total += 1

print(f"已生成 {OUT}")
print(f"每单元变量数: {len(rows)}，总通道数: {total}")
