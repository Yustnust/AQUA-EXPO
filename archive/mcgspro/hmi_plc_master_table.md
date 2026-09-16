| PLC地址  | HMI变量名（建议）                           | 类型      | 读写 | PLC实际用途                  | 备注               |
| ------ | ------------------------------------ | ------- | -- | ------------------------ | ---------------- |
| I0.0   | U1\_DI\_FlowSwitch\_A\_Inlet         | INTEGER | 只读 | 上缸进水流量开关                 | PLC代码读           |
| I0.1   | U1\_DI\_FlowSwitch\_B\_UpToDown      | INTEGER | 只读 | 上→下转移流量开关                | PLC代码读           |
| I0.2   | U1\_DI\_FlowSwitch\_C\_Drain         | INTEGER | 只读 | 下缸排水流量开关                 | PLC代码读           |
| I0.3   | U1\_???\_I0\_3                       | -       | -  | 系统复位按钮                   | 需新增到HMI；PLC代码读   |
| I0.4   | U1\_???\_I0\_4                       | -       | -  | 消音按钮                     | 需新增到HMI；PLC代码读   |
| I0.5   | U1\_DI\_LevelA\_High                 | INTEGER | 只读 | 上缸液位高位                   | PLC代码读           |
| I0.6   | U1\_DI\_LevelA\_Low                  | INTEGER | 只读 | 上缸液位低位                   | PLC代码读           |
| I0.7   | U1\_DI\_LevelB\_High                 | INTEGER | 只读 | 下缸液位高位                   | PLC代码读           |
| I1.0   | U1\_DI\_LevelB\_Low                  | INTEGER | 只读 | 下缸液位低位                   | PLC代码读           |
| I1.1   | U1\_DI\_EStop                        | INTEGER | 只读 | 急停按钮                     | PLC代码读           |
| I1.2   | U1\_DI\_SafetyRelay\_Feedback        | INTEGER | 只读 | 安全继电器反馈                  | PLC代码读           |
| I8.0   | U1\_DI\_ValveA\_Open                 | INTEGER | 只读 | 阀A开到位                    | PLC代码读           |
| I8.1   | U1\_DI\_ValveA\_Close                | INTEGER | 只读 | 阀A关到位                    | PLC代码读           |
| I8.2   | U1\_DI\_ValveB\_Open                 | INTEGER | 只读 | 阀B开到位                    | PLC代码读           |
| I8.3   | U1\_DI\_ValveB\_Close                | INTEGER | 只读 | 阀B关到位                    | PLC代码读           |
| I8.4   | U1\_DI\_ValveC\_Open                 | INTEGER | 只读 | 阀C开到位                    | PLC代码读           |
| I8.5   | U1\_DI\_ValveC\_Close                | INTEGER | 只读 | 阀C关到位                    | PLC代码读           |
| Q0.0   | U1\_DO\_Pump1                        | INTEGER | 只读 | 潜水泵1输出                   | PLC代码读写          |
| Q0.1   | U1\_DO\_Pump2                        | INTEGER | 只读 | 潜水泵2输出                   | PLC代码读写          |
| Q0.2   | U1\_???\_Q0\_2                       | -       | -  | 阀A输出                     | 需新增到HMI；PLC代码读写  |
| Q0.3   | U1\_???\_Q0\_3                       | -       | -  | 阀B输出                     | 需新增到HMI；PLC代码读写  |
| Q0.4   | U1\_???\_Q0\_4                       | -       | -  | 阀C输出                     | 需新增到HMI；PLC代码读写  |
| Q0.5   | U1\_DO\_NCValve\_Top                 | INTEGER | 读写 | 上缸NC球阀输出                 | PLC代码读写          |
| Q0.6   | U1\_DO\_NCValve\_Bottom              | INTEGER | 读写 | 下缸NC球阀输出                 | PLC代码读写          |
| Q0.7   | U1\_???\_Q0\_7                       | -       | -  | 报警声音输出                   | 需新增到HMI；PLC代码写   |
| Q8.0   | U1\_???\_Q8\_0                       | -       | -  | 报警灯光输出                   | 需新增到HMI；PLC代码写   |
| V0.0   | U1\_CMD\_Start                       | INTEGER | 读写 | 启动命令                     | PLC代码读写          |
| V0.1   | U1\_Reserved\_CMD\_Pause             | INTEGER | 读写 | 暂停命令（预留未实现）              | PLC代码未使用         |
| V0.2   | U1\_CMD\_Stop                        | INTEGER | 读写 | 停止命令                     | PLC代码读写          |
| V0.3   | U1\_CMD\_AckAlarm                    | INTEGER | 读写 | 报警确认命令                   | PLC代码读写          |
| V0.4   | U1\_CMD\_Mute                        | INTEGER | 读写 | 消音命令                     | PLC代码读写          |
| V0.5   | U1\_Reserved\_CMD\_ForceTankA\_Empty | INTEGER | 读写 | 强制上缸空命令（预留未实现）           | PLC代码读           |
| V0.6   | U1\_CMD\_RTC\_Sync                   | INTEGER | 读写 | RTC校时命令                  | PLC代码读写          |
| V0.7   | U1\_CMD\_SafetyRelayAck              | INTEGER | 读写 | 安全继电器故障确认命令              | PLC代码读写          |
| V1.0   | U1\_STA\_StartAck                    | INTEGER | 只读 | 启动命令确认                   | PLC代码写           |
| V1.1   | U1\_Reserved\_STA\_PauseAck          | INTEGER | 只读 | 暂停命令确认（预留）               | PLC代码未使用         |
| V1.2   | U1\_STA\_StopAck                     | INTEGER | 只读 | 停止命令确认                   | PLC代码未使用         |
| V1.3   | U1\_STA\_AlarmAckDone                | INTEGER | 只读 | 报警确认完成                   | PLC代码写           |
| V1.4   | U1\_STA\_MuteDone                    | INTEGER | 只读 | 消音完成                     | PLC代码写           |
| V1.5   | U1\_STA\_ForceDone                   | INTEGER | 只读 | 强制修正完成                   | PLC代码写           |
| V1.6   | U1\_STA\_TankA\_State                | INTEGER | 只读 | 上缸状态 0=空 1=满             | PLC代码读写          |
| V1.7   | U1\_STA\_TankB\_State                | INTEGER | 只读 | 下缸状态 0=空 1=满             | PLC代码读写          |
| VW2    | U1\_VW2\_StateMachine                | SINGLE  | 只读 | 下缸主状态机当前状态               | PLC代码读写          |
| VW4    | U1\_VW4\_PumpStatus                  | SINGLE  | 只读 | 注射泵状态码                   | PLC代码读写          |
| VW6    | U1\_VW6\_AlarmCode                   | SINGLE  | 只读 | 当前最高优先级报警码               | PLC代码读写          |
| VW8    | U1\_VW8\_RoundCount                  | SINGLE  | 只读 | 实验轮次计数                   | PLC代码写           |
| VW304  | U1\_???\_VW304                       | -       | -  | 上缸配液子流程状态                | 需新增到HMI；PLC代码读写  |
| VW306  | U1\_???\_VW306                       | -       | -  | 已完成下缸换水次数                | 需新增到HMI；PLC代码读写  |
| VD10   | U1\_???\_VD10                        | -       | -  | 目标浓度设定值（v2.0新增）          | 需新增到HMI；PLC代码未使用 |
| VD14   | U1\_???\_VD14                        | -       | -  | 母液浓度设定值（v2.0新增）          | 需新增到HMI；PLC代码未使用 |
| VD24   | U1\_VD\_ExperimentTarget             | SINGLE  | 读写 | 实验时长目标设定值(min)           | PLC代码读写          |
| VD28   | U1\_VD\_PreMixTime                   | SINGLE  | 读写 | S2搅拌+加药固定时长(s)           | PLC代码写           |
| VD54   | U1\_VD\_Timeout\_ValveC              | SINGLE  | 读写 | 阀C动作超时保护时长(s)            | PLC代码写           |
| VD66   | U1\_VD\_Delay\_ValveA\_Verify        | SINGLE  | 读写 | 阀A关闭后延时验证时长(s)           | PLC代码写           |
| VD350  | U1\_VD\_StepResolution               | SINGLE  | 读写 | 注射泵单步分辨率(uL/步)           | PLC代码写           |
| VD358  | U1\_VD\_Timeout\_ValveA              | SINGLE  | 读写 | 阀A动作超时保护时长(s)            | PLC代码写           |
| VD362  | U1\_VD\_Timeout\_ValveB              | SINGLE  | 读写 | 阀B动作超时保护时长(s)            | PLC代码写           |
| VD366  | U1\_VD\_ExperimentDuration\_Accum    | SINGLE  | 只读 | 实验时长累加值(min)             | PLC代码读写          |
| VD370  | U1\_???\_VD370                       | -       | -  | 目标抽取母液体积(uL)             | 需新增到HMI；PLC代码未使用 |
| VD414  | U1\_???\_VD414                       | -       | -  | 24h换水目标次数（v2.2新增）        | 需新增到HMI；PLC代码读写  |
| VD426  | U1\_???\_VD426                       | -       | -  | 周期尾端转移余量(s)（v2.2新增）      | 需新增到HMI；PLC代码写   |
| VD430  | U1\_???\_VD430                       | -       | -  | 上缸配液安全余量(s)（v2.2新增）      | 需新增到HMI；PLC代码写   |
| VD448  | U1\_VD\_S4WaitTimeout                | SINGLE  | 读写 | S4等待超时阈值(s)              | PLC代码写           |
| VD452  | U1\_VD\_ManualDose\_Target           | SINGLE  | 读写 | 手动注射泵总加药量(uL)            | PLC代码读写          |
| VD584  | U1\_VD\_Vol\_Target                  | SINGLE  | 读写 | 本轮目标抽取母液体积(uL)           | PLC代码读写          |
| VD70   | U1\_VD\_S1\_Actual                   | SINGLE  | 只读 | S1上缸进水实测时长(s)            | PLC代码写           |
| VD82   | U1\_VD\_FlowMeter\_Snapshot          | SINGLE  | 只读 | 阀A开启瞬间流量计快照              | PLC代码写           |
| VD86   | U1\_VD\_FlowMeter\_Current           | SINGLE  | 只读 | 流量计当前累计值                 | PLC代码写           |
| VD90   | U1\_VD\_Current\_InletVolume         | SINGLE  | 只读 | 本次当前进水量(L)               | PLC代码读写          |
| VD94   | U1\_VD\_FlowRate\_Instant            | SINGLE  | 只读 | 瞬时流速(L/min)              | PLC代码写           |
| VD102  | U1\_VD\_Dose\_Steps                  | SINGLE  | 只读 | 本轮加药目标步数                 | PLC代码读写          |
| VD116  | U1\_VD\_S6\_Rolling                  | SINGLE  | 读写 | S6滚动实测时长(s)，首轮存S4实测      | PLC代码读写          |
| VD178  | U1\_VD\_S5\_Elapsed                  | SINGLE  | 只读 | S5运行已用时长(s)              | PLC代码读写          |
| VD244  | U1\_???\_VD244                       | -       | -  | 周期倒计时器B当前值(s)            | 需新增到HMI；PLC代码写   |
| VD256  | U1\_???\_VD256                       | -       | -  | 周期倒计时器A当前值(s)            | 需新增到HMI；PLC代码写   |
| VD308  | U1\_VD\_FlowMeter\_CloseSnapshot     | SINGLE  | 只读 | 阀A关阀快照（HMI可查看）           | PLC代码写           |
| VD316  | U1\_VD\_TargetInletVolume            | SINGLE  | 读写 | 目标进水量(L)                 | PLC代码读写          |
| VD440  | U1\_VD\_Dosed\_Volume\_Total         | SINGLE  | 只读 | 累计加药量(uL)                | PLC代码读写          |
| VD444  | U1\_VD\_S4Wait\_Time                 | SINGLE  | 只读 | S4等待时长内部变量(s)            | PLC代码写           |
| V300.0 | U1\_Alarm\_Overflow\_AHigh           | INTEGER | 只读 | 上缸漫溢报警                   | PLC代码读写          |
| V300.1 | U1\_Alarm\_Overflow\_BHigh           | INTEGER | 只读 | 下缸漫溢报警                   | PLC代码读写          |
| V300.2 | U1\_Alarm\_NCValve\_Top              | INTEGER | 只读 | NC球阀-上缸动作                | PLC代码读写          |
| V300.3 | U1\_Alarm\_NCValve\_Bottom           | INTEGER | 只读 | NC球阀-下缸动作                | PLC代码读写          |
| V300.4 | U1\_EStop\_Latch                     | INTEGER | 只读 | 急停触发锁存                   | PLC代码读写          |
| V300.5 | U1\_Alarm\_SafetyRelay               | INTEGER | 只读 | 安全继电器故障                  | PLC代码读写          |
| V300.6 | U1\_Alarm\_ScheduleLag               | INTEGER | 只读 | 配液节奏严重滞后                 | PLC代码读           |
| V300.7 | U1\_Alarm\_ScheduleLag\_Warn         | INTEGER | 只读 | 配液节奏滞后提示                 | PLC代码读           |
| V301.0 | U1\_Alarm\_ValveA\_CloseFlow         | INTEGER | 只读 | 阀A关后延时验证仍有流              | PLC代码读写          |
| V301.2 | U1\_Alarm\_ValveA\_CloseTimeout      | INTEGER | 只读 | 阀A关到位反馈超时                | PLC代码读写          |
| V301.3 | U1\_Alarm\_ValveA\_CloseLeak         | INTEGER | 只读 | 阀A关到位但仍有流                | PLC代码读写          |
| V301.4 | U1\_Alarm\_ValveA\_OpenTimeout       | INTEGER | 只读 | 阀A开到位反馈超时                | PLC代码读写          |
| V301.5 | U1\_Alarm\_ValveA\_OpenNoFlow        | INTEGER | 只读 | 阀A开到位但无流                 | PLC代码读写          |
| V301.6 | U1\_Alarm\_ValveA\_S1Start           | INTEGER | 只读 | S5触发新一轮S1时上缸非空           | PLC代码读写          |
| V302.0 | U1\_Alarm\_ValveB\_Diag              | INTEGER | 只读 | 阀B四态诊断异常                 | PLC代码读写          |
| V302.1 | U1\_Alarm\_ValveB\_OpenTimeout       | INTEGER | 只读 | 阀B开到位反馈超时                | PLC代码读写          |
| V302.2 | U1\_Alarm\_ValveB\_OpenNoFlow        | INTEGER | 只读 | 阀B开到位但无流                 | PLC代码读写          |
| V302.3 | U1\_Alarm\_ValveB\_CloseTimeout      | INTEGER | 只读 | 阀B关到位反馈超时                | PLC代码读写          |
| V302.4 | U1\_Alarm\_ValveB\_CloseLeak         | INTEGER | 只读 | 阀B关到位但仍有流                | PLC代码读写          |
| V302.5 | U1\_Alarm\_ValveC\_Diag              | INTEGER | 只读 | 阀C四态诊断异常                 | PLC代码读写          |
| V302.6 | U1\_Alarm\_ValveC\_OpenTimeout       | INTEGER | 只读 | 阀C开到位反馈超时                | PLC代码读写          |
| V302.7 | U1\_Alarm\_ValveC\_OpenNoFlow        | INTEGER | 只读 | 阀C开到位但无流                 | PLC代码读写          |
| V303.0 | U1\_Alarm\_ValveC\_CloseTimeout      | INTEGER | 只读 | 阀C关到位反馈超时                | PLC代码读写          |
| V303.1 | U1\_Alarm\_ValveC\_CloseLeak         | INTEGER | 只读 | 阀C关到位但仍有流                | PLC代码读写          |
| V303.2 | U1\_Alarm\_S4TransferWaitTimeout     | INTEGER | 只读 | S4等待超时报警                 | PLC代码读写          |
| V303.4 | U1\_Alarm\_SyringePump               | INTEGER | 只读 | 注射泵通讯/动作异常               | PLC代码读写          |
| V303.5 | U1\_Alarm\_RTC\_Lost                 | INTEGER | 只读 | RTC时钟丢失                  | PLC代码读写          |
| V303.6 | U1\_Alarm\_FlowSwitch\_Instant       | INTEGER | 只读 | 单轮换水周期超时                 | PLC代码读写          |
| V303.7 | U1\_Need\_RTC\_Sync                  | INTEGER | 只读 | PLC请求HMI同步RTC            | PLC代码读写          |
| VB305  | U1\_VB\_SystemStatus                 | SINGLE  | 只读 | 系统总状态字(0=良好/1=故障/2=急停)   | PLC代码写           |
| M16.4  | U1\_???\_M16\_4                      | -       | -  | 系统初始化完成标志                | 需新增到HMI；PLC代码读写  |
| M16.5  | U1\_???\_M16\_5                      | -       | -  | 注射泵RTU从站在线               | 需新增到HMI；PLC代码写   |
| M16.6  | U1\_???\_M16\_6                      | -       | -  | 流量计RTU从站在线               | 需新增到HMI；PLC代码写   |
| V306.0 | U1\_CMD\_Manual\_ValveA\_Open        | INTEGER | 读写 | 手动开阀A命令                  | PLC代码读写          |
| V306.1 | U1\_CMD\_Manual\_ValveA\_Close       | INTEGER | 读写 | 手动关阀A命令                  | PLC代码读写          |
| V306.2 | U1\_CMD\_Manual\_ValveB\_Open        | INTEGER | 读写 | 手动开阀B命令                  | PLC代码读写          |
| V306.3 | U1\_CMD\_Manual\_ValveB\_Close       | INTEGER | 读写 | 手动关阀B命令                  | PLC代码读写          |
| V306.4 | U1\_CMD\_Manual\_ValveC\_Open        | INTEGER | 读写 | 手动开阀C命令                  | PLC代码读写          |
| V306.5 | U1\_CMD\_Manual\_ValveC\_Close       | INTEGER | 读写 | 手动关阀C命令                  | PLC代码读写          |
| V306.6 | U1\_CMD\_Manual\_Pump1\_On           | INTEGER | 读写 | 手动启动潜水泵1命令               | PLC代码读写          |
| V306.7 | U1\_CMD\_Manual\_Pump1\_Off          | INTEGER | 读写 | 手动停止潜水泵1命令               | PLC代码读写          |
| V307.0 | U1\_CMD\_Manual\_Pump2\_On           | INTEGER | 读写 | 手动启动潜水泵2命令               | PLC代码读写          |
| V307.1 | U1\_CMD\_Manual\_Pump2\_Off          | INTEGER | 读写 | 手动停止潜水泵2命令               | PLC代码读写          |
| V307.2 | U1\_CMD\_Manual\_SyringePump\_Start  | INTEGER | 读写 | 手动注射泵启动命令                | PLC代码读写          |
| V307.3 | U1\_CMD\_Manual\_SyringePump\_Stop   | INTEGER | 读写 | 手动注射泵停止/回零命令             | PLC代码读写          |
| V309.0 | U1\_V309\_0\_DebugMode               | INTEGER | 读写 | 调试模式开关                   | PLC代码读           |
| V200.0 | U1\_M\_AlarmAckMode                  | INTEGER | 读写 | 报警确认模式(0=自动/1=人工)        | PLC代码读写          |
| VB378  | U1\_???\_VB378                       | -       | -  | MBUS\_CTRL Error错误码      | 需新增到HMI；PLC代码读   |
| VB379  | U1\_???\_VB379                       | -       | -  | MBUS\_MSG任务0 Error       | 需新增到HMI；PLC代码读   |
| VB380  | U1\_???\_VB380                       | -       | -  | MBUS\_MSG任务2 Error       | 需新增到HMI；PLC代码读   |
| VB381  | U1\_???\_VB381                       | -       | -  | MBUS\_MSG任务1 Error       | 需新增到HMI；PLC代码读   |
| VB382  | U1\_???\_VB382                       | -       | -  | MBUS\_MSG任务3 Error       | 需新增到HMI；PLC代码读   |
| VB383  | U1\_???\_VB383                       | -       | -  | MBUS\_MSG任务4 Error       | 需新增到HMI；PLC代码读   |
| VW294  | U1\_VW294\_PumpContFail              | SINGLE  | 只读 | 注射泵连续失败计数                | PLC代码读写          |
| VW296  | U1\_VW296\_FlowContFail              | SINGLE  | 只读 | 流量计连续失败计数                | PLC代码读写          |
| VW388  | U1\_VD\_ManualDose\_Mode             | SINGLE  | 读写 | 手动注射泵模式(0=单次/1=循环)       | PLC代码读写          |
| VW390  | U1\_VW\_ManualDose\_State            | SINGLE  | 只读 | 手动注射泵子状态                 | PLC代码读写          |
| VD392  | U1\_VD\_ManualDose\_Dosed            | SINGLE  | 只读 | 手动注射泵累计加药量(uL)           | PLC代码读写          |
| VD396  | U1\_VD\_ManualDose\_Remaining        | SINGLE  | 只读 | 手动注射泵剩余加药量(uL)           | PLC代码写           |
| VB900  | U1\_???\_VB900                       | -       | -  | RTC年(BCD)                | 需新增到HMI；PLC代码读写  |
| VB901  | U1\_???\_VB901                       | -       | -  | RTC月(BCD)                | 需新增到HMI；PLC代码读写  |
| VB902  | U1\_???\_VB902                       | -       | -  | RTC日(BCD)                | 需新增到HMI；PLC代码读写  |
| VB903  | U1\_???\_VB903                       | -       | -  | RTC时(BCD)                | 需新增到HMI；PLC代码读写  |
| VB904  | U1\_???\_VB904                       | -       | -  | RTC分(BCD)                | 需新增到HMI；PLC代码读写  |
| VB905  | U1\_???\_VB905                       | -       | -  | RTC秒(BCD)                | 需新增到HMI；PLC代码读写  |
| VB906  | U1\_???\_VB906                       | -       | -  | RTC星期                    | 需新增到HMI；PLC代码写   |
| VB907  | U1\_???\_VB907                       | -       | -  | RTC保留                    | 需新增到HMI；PLC代码读写  |
| VB456  | U1\_???\_VB456                       | -       | -  | HMI参数镜像标志字节              | 需新增到HMI；PLC代码读   |
| VD460  | U1\_UD\_VD24\_ExpTarget              | SINGLE  | 读写 | HMI镜像 VD24\_ExpTarget    | PLC代码写           |
| VD464  | U1\_UD\_VD28\_PreMixTime             | SINGLE  | 读写 | HMI镜像 VD28\_PreMixTime   | PLC代码写           |
| VD488  | U1\_UD\_VD66\_DelayA                 | SINGLE  | 读写 | HMI镜像 VD66\_DelayA       | PLC代码写           |
| VD500  | U1\_UD\_VD316\_InletVol              | SINGLE  | 读写 | HMI镜像 VD316\_InletVol    | PLC代码写           |
| VD504  | U1\_UD\_VD350\_StepRes               | SINGLE  | 读写 | HMI镜像 VD350\_StepRes     | PLC代码写           |
| VD512  | U1\_UD\_VD358\_TimeoutA              | SINGLE  | 读写 | HMI镜像 VD358\_TimeoutA    | PLC代码写           |
| VD516  | U1\_UD\_VD362\_TimeoutB              | SINGLE  | 读写 | HMI镜像 VD362\_TimeoutB    | PLC代码写           |
| VD524  | U1\_UD\_VD448\_WaitTimeout           | SINGLE  | 读写 | HMI镜像 VD448\_WaitTimeout | PLC代码写           |
| VD528  | U1\_UD\_VD452\_ManualDose            | SINGLE  | 读写 | HMI镜像 VD452\_ManualDose  | PLC代码写           |
| V536.0 | U1\_UD\_V200\_0\_AckMode             | INTEGER | 读写 | HMI镜像 V200\_0\_AckMode   | PLC代码未使用         |

