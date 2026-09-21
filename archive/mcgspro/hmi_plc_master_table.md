| PLC地址 | HMI变量名（建议） | 类型 | 读写 | PLC实际用途 | 备注 |
|---------|------------------|------|------|------------|------|
| I0.0 | U1_DI_FlowSwitch_A_Inlet | INTEGER | 只读 | 上缸进水流量开关 | PLC代码读 |
| I0.1 | U1_DI_FlowSwitch_B_UpToDown | INTEGER | 只读 | 上→下转移流量开关 | PLC代码读 |
| I0.3 | U1_DI_SystemReset | INTEGER | 只读 | 系统复位按钮 | PLC代码读 |
| I0.4 | U1_DI_MuteBtn | INTEGER | 只读 | 消音按钮 | PLC代码读 |
| I0.5 | U1_DI_LevelA_High | INTEGER | 只读 | 上缸液位高位 | PLC代码读 |
| I0.6 | U1_DI_LevelA_Low | INTEGER | 只读 | 上缸液位低位 | PLC代码读 |
| I0.7 | U1_DI_LevelB_High | INTEGER | 只读 | 下缸液位高位 | PLC代码读 |
| I1.0 | U1_DI_LevelB_Low | INTEGER | 只读 | 下缸液位低位 | PLC代码读 |
| I1.1 | U1_DI_EStop | INTEGER | 只读 | 急停按钮 | PLC代码读 |
| I1.2 | U1_DI_SafetyRelay_Feedback | INTEGER | 只读 | 安全继电器反馈 | PLC代码读 |
| I8.0 | U1_DI_ValveA_Open | INTEGER | 只读 | 阀A开到位 | PLC代码读 |
| I8.1 | U1_DI_ValveA_Close | INTEGER | 只读 | 阀A关到位 | PLC代码读 |
| I8.2 | U1_DI_ValveB_Open | INTEGER | 只读 | 阀B开到位 | PLC代码读 |
| I8.3 | U1_DI_ValveB_Close | INTEGER | 只读 | 阀B关到位 | PLC代码读 |
| I8.4 | U1_DI_ValveC_Open | INTEGER | 只读 | 阀C开到位 | PLC代码读 |
| I8.5 | U1_DI_ValveC_Close | INTEGER | 只读 | 阀C关到位 | PLC代码读 |
| Q0.0 | U1_DO_Pump1 | INTEGER | 只读 | 潜水泵1输出 | PLC代码读写 |
| Q0.1 | U1_DO_Pump2 | INTEGER | 只读 | 潜水泵2输出 | PLC代码读写 |
| Q0.2 | U1_DO_ValveA | INTEGER | 只读 | 阀A输出 | PLC代码读写 |
| Q0.3 | U1_DO_ValveB | INTEGER | 只读 | 阀B输出 | PLC代码读写 |
| Q0.4 | U1_DO_ValveC | INTEGER | 只读 | 阀C输出 | PLC代码读写 |
| Q0.5 | U1_DO_NCValve_Top | INTEGER | 读写 | 上缸NC球阀输出 | PLC代码读写 |
| Q0.7 | U1_DO_Alarm_Sound | INTEGER | 只读 | 报警声音输出 | PLC代码写 |
| Q8.0 | U1_DO_Alarm_Light | INTEGER | 只读 | 报警灯光输出 | PLC代码写 |
| V0.0 | U1_CMD_Start | INTEGER | 读写 | 启动命令 | PLC代码读写 |
| V0.1 | U1_STA_RTU2_Online | INTEGER | 只读 | 暂停命令（预留未实现） | PLC代码读 |
| V0.2 | U1_CMD_Stop | INTEGER | 读写 | 停止命令 | PLC代码读写 |
| V0.3 | U1_CMD_AckAlarm | INTEGER | 读写 | 报警确认命令 | PLC代码读写 |
| V0.4 | U1_CMD_Mute | INTEGER | 读写 | 消音命令 | PLC代码读写 |
| V0.5 | U1_Reserved_CMD_ForceTankA_Empty | INTEGER | 读写 | 强制上缸空命令（预留未实现） | PLC代码读 |
| V0.6 | U1_CMD_RTC_Sync | INTEGER | 读写 | RTC校时命令 | PLC代码读写 |
| V0.7 | U1_CMD_SafetyRelayAck | INTEGER | 读写 | 安全继电器故障确认命令 | PLC代码读写 |
| V1.0 | U1_STA_StartAck | INTEGER | 只读 | 启动命令确认 | PLC代码写 |
| V1.1 | U1_STA_InitDone | INTEGER | 读写 | 暂停命令确认（预留） | PLC代码读 |
| V1.2 | U1_STA_RTU1_Online | INTEGER | 只读 | 停止命令确认 | PLC代码读 |
| V1.3 | U1_STA_AlarmAckDone | INTEGER | 只读 | 报警确认完成 | PLC代码写 |
| V1.4 | U1_STA_MuteDone | INTEGER | 只读 | 消音完成 | PLC代码写 |
| V1.5 | U1_STA_ForceDone | INTEGER | 只读 | 强制修正完成 | PLC代码写 |
| V1.6 | U1_STA_TankA_State | INTEGER | 只读 | 上缸状态 0=空 1=满 | PLC代码读写 |
| V1.7 | U1_STA_TankB_State | INTEGER | 只读 | 下缸状态 0=空 1=满 | PLC代码读写 |
| VW2 | U1_VW2_StateMachine | SINGLE | 只读 | 下缸主状态机当前状态 | PLC代码读写 |
| VW4 | U1_VW4_PumpStatus | SINGLE | 只读 | 注射泵状态码 | PLC代码读写 |
| VW6 | U1_VW6_AlarmCode | SINGLE | 只读 | 当前最高优先级报警码 | PLC代码读写 |
| VW8 | U1_VW8_RoundCount | SINGLE | 只读 | 实验总换水次数目标(=VD414×VD24/1440) | PLC代码读 |
| VW304 | U1_VW304_State_UpTank | SINGLE | 只读 | 上缸配液子流程状态 | PLC代码读写 |
| VW400 | U1_VW400_CycleCount | SINGLE | 读写 | 已完成下缸换水次数（v2.3.2由VW306迁入，避让手动命令位） | PLC代码写 |
| VW288 | U1_VW288_S4_Transfer_PT | SINGLE | 读写 | S4转移计时T49的PT(100ms单位，v2.3.1迁入) | PLC代码写 |
| VD10 | U1_???_VD10 | - | - | 目标浓度设定值（v2.0新增） | 需新增到HMI；PLC代码未使用 |
| VD14 | U1_???_VD14 | - | - | 母液浓度设定值（v2.0新增） | 需新增到HMI；PLC代码未使用 |
| VD24 | U1_VD_ExperimentTarget | SINGLE | 读写 | 实验时长目标设定值(min) | PLC代码读写 |
| VD28 | U1_VD_PreMixTime | SINGLE | 读写 | S2搅拌+加药固定时长(s) | PLC代码写 |
| VD54 | U1_VD_Timeout_ValveC | SINGLE | 读写 | 阀C动作超时保护时长(s) | PLC代码写 |
| VD60 | U1_VD_Delay_ValveC_Verify | SINGLE | 读写 | 阀C液位B低位延时验证时长(s)（v10.4新增，默认5） | PLC代码写 |
| VD66 | U1_VD_Delay_ValveA_Verify | SINGLE | 读写 | 阀A关闭后延时验证时长(s) | PLC代码写 |
| VD350 | U1_VD_StepResolution | SINGLE | 读写 | 注射泵单步分辨率(uL/步) | PLC代码写 |
| VD358 | U1_VD_Timeout_ValveA | SINGLE | 读写 | 阀A动作超时保护时长(s) | PLC代码写 |
| VD362 | U1_VD_Timeout_ValveB | SINGLE | 读写 | 阀B动作超时保护时长(s) | PLC代码写 |
| VD366 | U1_VD_ExperimentDuration_Accum | SINGLE | 只读 | 实验时长累加值(min) | PLC代码读写 |
| VD414 | U1_VD_24h_Target | SINGLE | 读写 | 24h换水目标次数（v2.2新增） | PLC代码读写 |
| VD426 | U1_VD_Transfer_Margin | SINGLE | 读写 | 周期尾端转移余量(s)（v2.2新增） | PLC代码写 |
| VD430 | U1_VD_Prep_Safety_Margin | SINGLE | 读写 | 上缸配液安全余量(s)（v2.2新增） | PLC代码写 |
| VD448 | U1_VD_S4WaitTimeout | SINGLE | 读写 | S4等待超时阈值(s) | PLC代码写 |
| VD452 | U1_VD_ManualDose_Target | SINGLE | 读写 | 手动注射泵总加药量(uL) | PLC代码读写 |
| VD584 | U1_VD_Vol_Target | SINGLE | 读写 | 本轮目标抽取母液体积(uL) | PLC代码读写 |
| VD70 | U1_VD_S1_Actual | SINGLE | 只读 | S1上缸进水实测时长(s) | PLC代码写 |
| VD82 | U1_VD_FlowMeter_Snapshot | SINGLE | 只读 | 阀A开启瞬间流量计快照 | PLC代码写 |
| VD86 | U1_VD_FlowMeter_Current | SINGLE | 只读 | 流量计当前累计值 | PLC代码写 |
| VD90 | U1_VD_Current_InletVolume | SINGLE | 只读 | 本次当前进水量(L) | PLC代码读写 |
| VD94 | U1_VD_FlowRate_Instant | SINGLE | 只读 | 瞬时流速(L/min) | PLC代码写 |
| VD102 | U1_VD_Dose_Steps | SINGLE | 只读 | 本轮加药目标步数 | PLC代码读写 |
| VD116 | U1_VD_S6_Rolling | SINGLE | 只读 | S6滚动实测时长(s)，首轮存S4实测 | PLC代码写 |
| VD178 | U1_VD_S5_Elapsed | SINGLE | 只读 | S5运行已用时长(s) | PLC代码写 |
| VD244 | U1_???_VD244 | - | - | 周期倒计时器B显示值(s,DINT) | 需新增到HMI；PLC代码写 |
| VD248 | U1_VD_TimerA_Elapsed | SINGLE | 只读 | TimerA已运行秒数(REAL,调试) | PLC代码写 |
| VD256 | U1_???_VD256 | - | - | 周期倒计时器A显示值(s,DINT) | 需新增到HMI；PLC代码写 |
| VD252 | U1_VD_TimerB_Elapsed | SINGLE | 只读 | TimerB已运行秒数(REAL,调试) | PLC代码写 |
| VD308 | U1_VD_FlowMeter_CloseSnapshot | SINGLE | 只读 | 阀A关阀快照（HMI可查看） | PLC代码写 |
| VD316 | U1_VD_TargetInletVolume | SINGLE | 读写 | 目标进水量(L) | PLC代码读写 |
| VD440 | U1_VD_Dosed_Volume_Total | SINGLE | 只读 | 累计加药量(uL) | PLC代码读写 |
| VD444 | U1_???_VD444 | - | - | S4等待时长内部变量(s) | 需新增到HMI；PLC代码写 |
| V300.0 | U1_Alarm_Overflow_AHigh | INTEGER | 只读 | 上缸漫溢报警 | PLC代码读写 |
| V300.1 | U1_Alarm_Overflow_BHigh | INTEGER | 只读 | 下缸漫溢报警 | PLC代码读写 |
| V300.2 | U1_Alarm_NCValve_Top | INTEGER | 只读 | NC球阀-上缸动作 | PLC代码读写 |
| V300.4 | U1_EStop_Latch | INTEGER | 只读 | 急停触发锁存 | PLC代码读写 |
| V300.5 | U1_Alarm_SafetyRelay | INTEGER | 只读 | 安全继电器故障 | PLC代码读写 |
| V300.6 | U1_Alarm_ScheduleLag | INTEGER | 只读 | 配液节奏严重滞后 | PLC代码读 |
| V300.7 | U1_Alarm_ScheduleLag_Warn | INTEGER | 只读 | 配液节奏滞后提示 | PLC代码读 |
| V301.0 | U1_Alarm_ValveA_CloseFlow | INTEGER | 只读 | 阀A关后延时验证仍有流 | PLC代码读写 |
| V301.2 | U1_Alarm_ValveA_CloseTimeout | INTEGER | 只读 | 阀A关到位反馈超时 | PLC代码读写 |
| V301.3 | U1_Alarm_ValveA_CloseLeak | INTEGER | 只读 | 阀A关到位但仍有流 | PLC代码读写 |
| V301.4 | U1_Alarm_ValveA_OpenTimeout | INTEGER | 只读 | 阀A开到位反馈超时 | PLC代码读写 |
| V301.5 | U1_Alarm_ValveA_OpenNoFlow | INTEGER | 只读 | 阀A开到位但无流 | PLC代码读写 |
| V301.6 | U1_Alarm_ValveA_S1Start | INTEGER | 只读 | S5触发新一轮S1时上缸非空 | PLC代码读写 |
| V302.0 | U1_Alarm_ValveB_Diag | INTEGER | 只读 | 阀B四态诊断异常 | PLC代码读写 |
| V302.1 | U1_Alarm_ValveB_OpenTimeout | INTEGER | 只读 | 阀B开到位反馈超时 | PLC代码读写 |
| V302.2 | U1_Alarm_ValveB_OpenNoFlow | INTEGER | 只读 | 阀B开到位但无流 | PLC代码读写 |
| V302.3 | U1_Alarm_ValveB_CloseTimeout | INTEGER | 只读 | 阀B关到位反馈超时 | PLC代码读写 |
| V302.4 | U1_Alarm_ValveB_CloseLeak | INTEGER | 只读 | 阀B关到位但仍有流 | PLC代码读写 |
| V302.5 | U1_Alarm_ValveC_Diag | INTEGER | 只读 | 阀C四态诊断异常（v10.4废弃,不再置位） | PLC代码未使用 |
| V302.6 | U1_Alarm_ValveC_OpenTimeout | INTEGER | 只读 | 阀C开到位反馈超时 | PLC代码读写 |
| V302.7 | U1_Alarm_ValveC_OpenNoFlow | INTEGER | 只读 | 阀C开到位但无流（v10.4废弃） | PLC代码未使用 |
| V303.0 | U1_Alarm_ValveC_CloseTimeout | INTEGER | 只读 | 阀C关到位反馈超时 | PLC代码读写 |
| V303.1 | U1_Alarm_ValveC_CloseLeak | INTEGER | 只读 | 阀C关到位但仍有流（v10.4废弃） | PLC代码未使用 |
| V303.2 | U1_Alarm_S4TransferWaitTimeout | INTEGER | 只读 | S4等待超时报警 | PLC代码读写 |
| V303.4 | U1_Alarm_SyringePump | INTEGER | 只读 | 注射泵通讯/动作异常 | PLC代码读写 |
| V303.5 | U1_Alarm_RTC_Lost | INTEGER | 只读 | RTC时钟丢失 | PLC代码读写 |
| V303.6 | U1_Alarm_CycleTimeout | INTEGER | 只读 | 单轮换水周期超时 | PLC代码读写 |
| V303.7 | U1_Need_RTC_Sync | INTEGER | 只读 | PLC请求HMI同步RTC | PLC代码读写 |
| VB305 | U1_VB_SystemStatus | SINGLE | 只读 | 系统总状态字(0=良好/1=故障/2=急停) | PLC代码写 |
| M16.4 | U1_???_M16_4 | - | - | 系统初始化完成标志 | 需新增到HMI；PLC代码读写 |
| M16.5 | U1_???_M16_5 | - | - | 注射泵RTU从站在线 | 需新增到HMI；PLC代码读写 |
| M16.6 | U1_???_M16_6 | - | - | 流量计RTU从站在线 | 需新增到HMI；PLC代码读写 |
| V306.0 | U1_CMD_Manual_ValveA_Open | INTEGER | 读写 | 手动开阀A命令 | PLC代码读写 |
| V306.1 | U1_CMD_Manual_ValveA_Close | INTEGER | 读写 | 手动关阀A命令 | PLC代码读写 |
| V306.2 | U1_CMD_Manual_ValveB_Open | INTEGER | 读写 | 手动开阀B命令 | PLC代码读写 |
| V306.3 | U1_CMD_Manual_ValveB_Close | INTEGER | 读写 | 手动关阀B命令 | PLC代码读写 |
| V306.4 | U1_CMD_Manual_ValveC_Open | INTEGER | 读写 | 手动开阀C命令 | PLC代码读写 |
| V306.5 | U1_CMD_Manual_ValveC_Close | INTEGER | 读写 | 手动关阀C命令 | PLC代码读写 |
| V306.6 | U1_CMD_Manual_Pump1_On | INTEGER | 读写 | 手动启动潜水泵1命令 | PLC代码读写 |
| V306.7 | U1_CMD_Manual_Pump1_Off | INTEGER | 读写 | 手动停止潜水泵1命令 | PLC代码读写 |
| V307.0 | U1_CMD_Manual_Pump2_On | INTEGER | 读写 | 手动启动潜水泵2命令 | PLC代码读写 |
| V307.1 | U1_CMD_Manual_Pump2_Off | INTEGER | 读写 | 手动停止潜水泵2命令 | PLC代码读写 |
| V307.2 | U1_CMD_Manual_SyringePump_Start | INTEGER | 读写 | 手动注射泵启动命令 | PLC代码读写 |
| V307.3 | U1_CMD_Manual_SyringePump_Stop | INTEGER | 读写 | 手动注射泵停止/回零命令 | PLC代码读写 |
| V309.0 | U1_V309_0_DebugMode | INTEGER | 读写 | 调试模式开关 | PLC代码读 |
| V200.0 | U1_M_AlarmAckMode | INTEGER | 读写 | 报警确认模式(0=自动/1=人工) | PLC代码读写 |
| VB378 | U1_VB378_MB_CTRL_Error | SINGLE | 只读 | MBUS_CTRL Error错误码 | PLC代码读 |
| VB379 | U1_VB379_MB_MSG_Error_Task0 | SINGLE | 只读 | MBUS_MSG任务0 Error | PLC代码读 |
| VB380 | U1_VB380_MB_MSG_Error_Task2 | SINGLE | 只读 | MBUS_MSG任务2 Error | PLC代码读 |
| VB381 | U1_VB381_MB_MSG_Error_Task1 | SINGLE | 只读 | MBUS_MSG任务1 Error | PLC代码读 |
| VB382 | U1_VB382_MB_MSG_Error_Task3 | SINGLE | 只读 | MBUS_MSG任务3 Error | PLC代码读 |
| VB383 | U1_VB383_MB_MSG_Error_Task4 | SINGLE | 只读 | MBUS_MSG任务4 Error | PLC代码读 |
| VW294 | U1_VW294_PumpContFail | SINGLE | 只读 | 注射泵连续失败计数 | PLC代码读写 |
| VW296 | U1_VW296_FlowContFail | SINGLE | 只读 | 流量计连续失败计数 | PLC代码读写 |
| VW388 | U1_VD_ManualDose_Mode | SINGLE | 读写 | 手动注射泵模式(0=单次/1=循环) | PLC代码读写 |
| VW390 | U1_VW_ManualDose_State | SINGLE | 只读 | 手动注射泵子状态 | PLC代码读写 |
| VD392 | U1_VD_ManualDose_Dosed | SINGLE | 只读 | 手动注射泵累计加药量(uL) | PLC代码读写 |
| VD396 | U1_VD_ManualDose_Remaining | SINGLE | 只读 | 手动注射泵剩余加药量(uL) | PLC代码写 |
| VB900 | U1_VB900_RTC_Year | SINGLE | 读写 | RTC年(BCD) | PLC代码读写 |
| VB901 | U1_VB901_RTC_Month | SINGLE | 读写 | RTC月(BCD) | PLC代码读写 |
| VB902 | U1_VB902_RTC_Day | SINGLE | 读写 | RTC日(BCD) | PLC代码读写 |
| VB903 | U1_VB903_RTC_Hour | SINGLE | 读写 | RTC时(BCD) | PLC代码读写 |
| VB904 | U1_VB904_RTC_Minute | SINGLE | 读写 | RTC分(BCD) | PLC代码读写 |
| VB905 | U1_VB905_RTC_Second | SINGLE | 读写 | RTC秒(BCD) | PLC代码读写 |
| VB906 | U1_VB906_RTC_Weekday | SINGLE | 只读 | RTC星期 | PLC代码写 |
| VB907 | U1_VB907_RTC_Reserved | SINGLE | 读写 | RTC保留 | PLC代码读写 |
| VB456 | U1_UD_Flag | SINGLE | 读写 | HMI参数镜像标志字节 | PLC代码读 |
| VD460 | U1_UD_VD24_ExpTarget | SINGLE | 读写 | HMI镜像 VD24_ExpTarget | PLC代码写 |
| VD464 | U1_UD_VD28_PreMixTime | SINGLE | 读写 | HMI镜像 VD28_PreMixTime | PLC代码写 |
| VD468 | U1_UD_VD414_24h_Target | SINGLE | 读写 | HMI镜像 VD414_24h_Target v2.2 | PLC代码写 |
| VD476 | U1_UD_VD426_Transfer_Margin | SINGLE | 读写 | HMI镜像 VD426_Transfer_Margin v2.2 | PLC代码写 |
| VD480 | U1_UD_VD430_Safety_Margin | SINGLE | 读写 | HMI镜像 VD430_Safety_Margin v2.2 | PLC代码写 |
| VD488 | U1_UD_VD66_DelayA | SINGLE | 读写 | HMI镜像 VD66_DelayA | PLC代码写 |
| VD492 | U1_UD_VD60_DelayC | SINGLE | 读写 | HMI镜像 VD60_DelayC(排液完成验证延时UD) v3.1新增 | PLC代码写 |
| VD500 | U1_UD_VD316_InletVol | SINGLE | 读写 | HMI镜像 VD316_InletVol | PLC代码写 |
| VD504 | U1_UD_VD350_StepRes | SINGLE | 读写 | HMI镜像 VD350_StepRes | PLC代码写 |
| VD512 | U1_UD_VD358_TimeoutA | SINGLE | 读写 | HMI镜像 VD358_TimeoutA | PLC代码写 |
| VD516 | U1_UD_VD362_TimeoutB | SINGLE | 读写 | HMI镜像 VD362_TimeoutB | PLC代码写 |
| VD524 | U1_UD_VD448_S4WaitTimeout | SINGLE | 读写 | HMI镜像 VD448_WaitTimeout | PLC代码写 |
| VD528 | U1_UD_VD452_ManualDose | SINGLE | 读写 | HMI镜像 VD452_ManualDose | PLC代码写 |
| V536.0 | U1_V200_AlarmAckMode | INTEGER | 读写 | HMI镜像 V200_0_AckMode | PLC代码未使用 |