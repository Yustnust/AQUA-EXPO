#!/usr/bin/env python3
"""
MCGS变量导入CSV生成器
从HMI变量导入CSV模板生成8套单元的MCGS格式CSV
每套单元73个PLC变量 × 8套 = 584个 + 18个HMI内部变量 = 602个
"""
import csv
import os

# PLC变量定义(单套单元,73个)
# 格式: (变量名, MCGS类型, PLC地址, 读写, 断电保持, 注释, 画面编号)
SINGLE_UNIT_VARS = [
    # === 命令位 V0区 (8个) ===
    ("CMD_Start", "Bool", "V0.0", "RW", "是", "启动实验(从S0进入S1)", 3),
    ("CMD_Pause", "Bool", "V0.1", "RW", "是", "暂停实验(预留)", 3),
    ("CMD_Stop", "Bool", "V0.2", "RW", "是", "停止实验(进入S7)", 3),
    ("CMD_AckAlarm", "Bool", "V0.3", "RW", "是", "报警确认", 5),
    ("CMD_Mute", "Bool", "V0.4", "RW", "是", "消音命令", 5),
    ("CMD_ForceTankA_Empty", "Bool", "V0.5", "RW", "是", "强制上缸状态=空", 3),
    ("CMD_ForceTankA_Full", "Bool", "V0.6", "RW", "是", "强制上缸状态=满", 3),
    ("CMD_SafetyRelayAck", "Bool", "V0.7", "RW", "是", "继电器故障HMI确认", 5),

    # === 状态位 V1区 (8个) ===
    ("STA_StartAck", "Bool", "V1.0", "R", "是", "启动命令已接收", 1),
    ("STA_PauseAck", "Bool", "V1.1", "R", "是", "暂停命令已接收", 3),
    ("STA_StopAck", "Bool", "V1.2", "R", "是", "停止命令已接收", 3),
    ("STA_AlarmAckDone", "Bool", "V1.3", "R", "是", "报警确认已执行", 5),
    ("STA_MuteDone", "Bool", "V1.4", "R", "是", "消音已执行", 5),
    ("STA_ForceDone", "Bool", "V1.5", "R", "是", "状态强制已执行", 3),
    ("STA_TankA_State", "Bool", "V1.6", "R", "是", "上缸状态(0=空,1=满)", 1),
    ("STA_TankB_State", "Bool", "V1.7", "R", "是", "下缸状态(0=空,1=满)", 1),

    # === 状态机 VW区 (4个) ===
    ("VW2_StateMachine", "Int", "VW2", "R", "是", "状态机当前状态(0~8,99)", 1),
    ("VW4_PumpStatus", "Int", "VW4", "R", "否", "注射泵状态码", 2),
    ("VW6_AlarmCode", "Int", "VW6", "R", "是", "当前最高优先级报警码", 5),
    ("VW8_RoundCount", "Int", "VW8", "R", "是", "实验轮次计数", 1),

    # === HMI设定参数 VD区 (24个) ===
    ("VD_C_Set", "Float", "VD10", "RW", "是", "目标浓度设定值(%)", 4),
    ("VD_C_Stock", "Float", "VD14", "RW", "是", "母液浓度(%)", 4),
    ("VD_StepResolution", "Float", "VD350", "RW", "是", "注射泵单步分辨率(µL/步)", 4),
    ("VD_CycleSetpoint", "Float", "VD354", "RW", "是", "换水周期设定值(min)", 4),
    ("VD_ExperimentTarget", "Float", "VD24", "RW", "是", "实验时长目标(min)", 4),
    ("VD_PreMixTime", "Float", "VD28", "RW", "是", "S2预循环标称时长(s)", 4),
    ("VD_PreMixTime_MinSafe", "Float", "VD32", "RW", "是", "S2压缩下限(s)", 4),
    ("VD_RestTime", "Float", "VD36", "RW", "是", "S3.5静止等候标称时长(s)", 4),
    ("VD_RestTime_Min", "Float", "VD40", "RW", "是", "S3.5压缩下限(s)", 4),
    ("VD_CycleExtend_Max", "Float", "VD44", "RW", "是", "换水周期顺延上限(min)", 4),
    ("VD_Timeout_ValveA", "Float", "VD358", "RW", "是", "阀A动作超时(s)", 4),
    ("VD_Timeout_ValveB", "Float", "VD362", "RW", "是", "阀B动作超时(s)", 4),
    ("VD_Timeout_ValveC", "Float", "VD54", "RW", "是", "阀C动作超时(s)", 4),
    ("VD_Timeout_Pump1", "Float", "VD58", "RW", "是", "潜水泵1超时(s)", 4),
    ("VD_Timeout_Pump2", "Float", "VD62", "RW", "是", "潜水泵2超时(s)", 4),
    ("VD_Delay_ValveA_Verify", "Float", "VD66", "RW", "是", "阀A关闭延时验证(s)", 4),
    ("VD_ExperimentDuration_Accum", "Float", "VD366", "R", "是", "实验时长累加(min)", 1),
    ("VD_Vol_Target", "Float", "VD370", "R", "是", "本轮目标抽取体积(µL)", 2),
    ("VD_Dose_Steps", "Float", "VD102", "R", "是", "本轮加药目标步数", 2),

    # === PLC实测值 VD区 (9个) ===
    ("VD_S1_Actual", "Float", "VD70", "R", "是", "S1进水实测时长(s)", 2),
    ("VD_S4_Actual", "Float", "VD74", "R", "是", "S4转移实测时长(s)", 2),
    ("VD_S6_Actual", "Float", "VD78", "R", "是", "S6排水实测时长(s)", 2),
    ("VD_FlowMeter_Snapshot", "Float", "VD82", "R", "是", "流量计快照(差值基准)", 2),
    ("VD_FlowMeter_Current", "Float", "VD86", "R", "是", "流量计当前累计值", 2),
    ("VD_Current_InletVolume", "Float", "VD90", "R", "是", "本次进水量(L)", 2),
    ("VD_FlowRate_Instant", "Float", "VD94", "R", "是", "瞬时流速(L/min)", 2),

    # === 纠偏参数 (10个) ===
    ("VD_T_Default", "Float", "VD104", "R", "是", "T初始默认值(s)", 6),
    ("VD_S6_Default", "Float", "VD108", "R", "是", "S6排水默认时长(s)", 6),
    ("VD_T_Rolling", "Float", "VD112", "R", "是", "T滚动实测值(s)", 6),
    ("VD_S6_Rolling", "Float", "VD116", "R", "是", "S6滚动实测值(s)", 6),
    ("VD_S2_Target", "Float", "VD120", "R", "是", "本轮S2实际目标(s)", 6),
    ("VD_RestTime_Target", "Float", "VD124", "R", "是", "本轮S3.5实际目标(s)", 6),
    ("VD_CycleExtend_Target", "Float", "VD128", "R", "是", "本轮允许空等时长(min)", 6),
    ("VD_PumpSpeed_Start", "Float", "VD132", "RW", "是", "注射泵启动速度(Hz)", 4),
    ("VD_PumpSpeed_Max", "Float", "VD136", "RW", "是", "注射泵最高速度(Hz)", 4),
    ("VD_PumpSpeed_Cutoff", "Float", "VD140", "RW", "是", "注射泵截止速度(Hz)", 4),

    # === 报警字 VB300~303 (32个位) ===
    ("V300_0_Alarm_Overflow_AHigh", "Bool", "V300.0", "R", "是", "上缸漫溢", 5),
    ("V300_1_Alarm_Overflow_BHigh", "Bool", "V300.1", "R", "是", "下缸漫溢", 5),
    ("V300_2_Alarm_NCValve_Top", "Bool", "V300.2", "R", "是", "NC电磁阀-上缸动作", 5),
    ("V300_3_Alarm_NCValve_Bottom", "Bool", "V300.3", "R", "是", "NC电磁阀-下缸动作", 5),
    ("V300_4_EStop_Latch", "Bool", "V300.4", "R", "是", "急停触发锁存", 5),
    ("V300_5_Alarm_SafetyRelay", "Bool", "V300.5", "R", "是", "安全继电器故障(最高级)", 5),
    ("V300_6_Alarm_ScheduleLag", "Bool", "V300.6", "R", "是", "配液节奏严重滞后", 5),
    ("V300_7_Alarm_ScheduleLag_Warn", "Bool", "V300.7", "R", "是", "配液节奏滞后提示", 5),
    ("V301_0_Alarm_ValveA_CloseFlow", "Bool", "V301.0", "R", "是", "阀A关后仍有流", 5),
    ("V301_1_Alarm_ValveA_Leak", "Bool", "V301.1", "R", "是", "阀A内漏", 5),
    ("V301_2_Alarm_ValveA_CloseTimeout", "Bool", "V301.2", "R", "是", "阀A关超时", 5),
    ("V301_3_Alarm_ValveA_CloseLeak", "Bool", "V301.3", "R", "是", "阀A关到位有流", 5),
    ("V301_4_Alarm_ValveA_OpenTimeout", "Bool", "V301.4", "R", "是", "阀A开超时", 5),
    ("V301_5_Alarm_ValveA_OpenNoFlow", "Bool", "V301.5", "R", "是", "阀A开到位无流", 5),
    ("V301_6_Alarm_ValveA_S1Start", "Bool", "V301.6", "R", "是", "S5触发新一轮S1上缸非空", 5),
    ("V302_0_Alarm_ValveB_Diag", "Bool", "V302.0", "R", "是", "阀B四态诊断异常", 5),
    ("V302_1_Alarm_ValveB_OpenTimeout", "Bool", "V302.1", "R", "是", "阀B开超时", 5),
    ("V302_2_Alarm_ValveB_OpenNoFlow", "Bool", "V302.2", "R", "是", "阀B开到位无流", 5),
    ("V302_3_Alarm_ValveB_CloseTimeout", "Bool", "V302.3", "R", "是", "阀B关超时", 5),
    ("V302_4_Alarm_ValveB_CloseLeak", "Bool", "V302.4", "R", "是", "阀B关到位有流", 5),
    ("V302_5_Alarm_ValveC_Diag", "Bool", "V302.5", "R", "是", "阀C四态诊断异常", 5),
    ("V302_6_Alarm_ValveC_OpenTimeout", "Bool", "V302.6", "R", "是", "阀C开超时", 5),
    ("V302_7_Alarm_ValveC_OpenNoFlow", "Bool", "V302.7", "R", "是", "阀C开到位无流", 5),
    ("V303_0_Alarm_ValveC_CloseTimeout", "Bool", "V303.0", "R", "是", "阀C关超时", 5),
    ("V303_1_Alarm_ValveC_CloseLeak", "Bool", "V303.1", "R", "是", "阀C关到位有流", 5),
    ("V303_2_Alarm_Pump1_Abnormal", "Bool", "V303.2", "R", "是", "潜水泵1超时无流", 5),
    ("V303_3_Alarm_Pump2_Abnormal", "Bool", "V303.3", "R", "是", "潜水泵2超时无流", 5),
    ("V303_4_Alarm_SyringePump", "Bool", "V303.4", "R", "是", "注射泵通讯/动作异常", 5),
    ("V303_5_Alarm_RTC_Lost", "Bool", "V303.5", "R", "是", "RTC时钟丢失", 5),
    ("V303_6_Alarm_FlowSwitch_Instant", "Bool", "V303.6", "R", "是", "流量开关瞬时异常", 5),

    # === 手动控制 V2.4~V3.3 (8个) ===
    ("CMD_Manual_ValveA_Open", "Bool", "V2.4", "RW", "是", "手动开阀A", 3),
    ("CMD_Manual_ValveA_Close", "Bool", "V2.5", "RW", "是", "手动关阀A", 3),
    ("CMD_Manual_ValveB_Open", "Bool", "V2.6", "RW", "是", "手动开阀B", 3),
    ("CMD_Manual_ValveB_Close", "Bool", "V2.7", "RW", "是", "手动关阀B", 3),
    ("CMD_Manual_ValveC_Open", "Bool", "V3.0", "RW", "是", "手动开阀C", 3),
    ("CMD_Manual_ValveC_Close", "Bool", "V3.1", "RW", "是", "手动关阀C", 3),
    ("CMD_Manual_Pump1_On", "Bool", "V3.2", "RW", "是", "手动启动泵1", 3),
    ("CMD_Manual_Pump1_Off", "Bool", "V3.3", "RW", "是", "手动停止泵1", 3),
]

# HMI内部变量(不读PLC,18个)
INTERNAL_VARS = [
    ("SelectedUnit", "Int", "", "", "", "当前选中单元号(1~8)", 0),
    ("UnitEnabled_01", "Bool", "", "", "是", "1号单元使能", 7),
    ("UnitEnabled_02", "Bool", "", "", "是", "2号单元使能", 7),
    ("UnitEnabled_03", "Bool", "", "", "是", "3号单元使能", 7),
    ("UnitEnabled_04", "Bool", "", "", "是", "4号单元使能", 7),
    ("UnitEnabled_05", "Bool", "", "", "是", "5号单元使能", 7),
    ("UnitEnabled_06", "Bool", "", "", "是", "6号单元使能", 7),
    ("UnitEnabled_07", "Bool", "", "", "是", "7号单元使能", 7),
    ("UnitEnabled_08", "Bool", "", "", "是", "8号单元使能", 7),
    ("LoginLevel", "Int", "", "", "否", "当前登录权限(0/1/2/3)", 0),
    ("LoginTime", "String", "", "", "否", "登录时间(超时判断)", 0),
    ("GlobalAlarmActive", "Bool", "", "", "否", "全局报警活动", 0),
    ("GlobalMuteState", "Bool", "", "", "否", "全局消音状态", 0),
    ("CommStatus_01", "Bool", "", "", "否", "1号连接通讯状态", 1),
    ("CommStatus_02", "Bool", "", "", "否", "2号连接通讯状态", 1),
    ("CommStatus_03", "Bool", "", "", "否", "3号连接通讯状态", 1),
    ("CommStatus_04", "Bool", "", "", "否", "4号连接通讯状态", 1),
    ("CommStatus_05", "Bool", "", "", "否", "5号连接通讯状态", 1),
    ("CommStatus_06", "Bool", "", "", "否", "6号连接通讯状态", 1),
    ("CommStatus_07", "Bool", "", "", "否", "7号连接通讯状态", 1),
    ("CommStatus_08", "Bool", "", "", "否", "8号连接通讯状态", 1),
]


def generate_csv(output_path):
    """生成MCGS变量导入CSV(8套单元+内部变量)"""
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        # 表头
        w.writerow(['变量名', '数据类型', '连接名', 'PLC地址', '读写属性',
                    '断电保持', '注释', '画面编号'])

        count = 0
        # 8套单元PLC变量
        for unit in range(1, 9):
            conn = f"PLC_{unit:02d}"
            for v in SINGLE_UNIT_VARS:
                name, dtype, addr, rw, retain, comment, page = v
                full_name = f"U{unit}_{name}"
                w.writerow([full_name, dtype, conn, addr, rw, retain, comment, page])
                count += 1

        # HMI内部变量
        for v in INTERNAL_VARS:
            name, dtype, addr, rw, retain, comment, page = v
            w.writerow([name, dtype, "(内部)", addr, rw, retain, comment, page])
            count += 1

    return count


def main():
    out = '/workspace/AQUA-EXPO/docs/hmi_preparation/MCGS变量导入_8连接版.csv'
    count = generate_csv(out)
    print(f"✅ 已生成: {out}")
    print(f"   变量总数: {count}")
    print(f"   PLC变量: {len(SINGLE_UNIT_VARS) * 8} (={len(SINGLE_UNIT_VARS)}×8套)")
    print(f"   内部变量: {len(INTERNAL_VARS)}")
    print()
    # 类型统计
    from collections import Counter
    types = Counter(v[1] for v in SINGLE_UNIT_VARS * 8 + INTERNAL_VARS)
    print("   类型统计:")
    for t, c in types.most_common():
        print(f"     {t}: {c}")


if __name__ == '__main__':
    main()
