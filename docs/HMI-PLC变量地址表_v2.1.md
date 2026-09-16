# 药液配置与加注控制系统 — HMI-PLC 变量地址表 v2.1

**配套文档**：《药液配置加注控制系统\_PLC设计文档》v9.4、《S2-S4流程重构设计方案\_v2.2》\
**适用范围**：8套缸单元（每套1台S7-200 SMART CPU ST20），1台本地集中HMI\
**本文档目的**：以PLC代码为唯一真值，重新定义HMI与PLC之间的变量地址映射，删除PLC未使用变量，补全HMI缺失变量\
**编址规范**：西门子S7-200 SMART V区编址（VB字节/VW字/VD双字/M位/I点/Q点）

> **v2.1变更摘要（2026-09-16，PLC代码对齐重写）**：
>
> - **删除项**：彻底移除PLC代码中未使用或已废弃的变量。包括V0.1/V1.1/V1.2暂停相关位；VD32/VD36/VD40/VD44预循环/休息参数；VD58/VD62泵超时保护（预留未用，无报警逻辑）；VD74（原S4\_Actual，现未使用）；VD78（原S6\_Actual）；VD108（首轮S6默认时长，v2.2改为直接用VD116首轮S4实测值）；VD112（T\_Rolling）；VD120/VD124/VD128（S2/Rest/CycleExtend目标）；VD132/VD136/VD140（注射泵速度设定，已停用）；VD144（T\_Default）；VD150/VD154（纠偏中间值）；VD174（S3\_Estimate）；VW182/VW184（纠偏模式/结果）；VW202/VW204/VW206（泵Modbus写缓冲，实际由FC4内部VW230/VD232管理）；VW208/VW210/VW212（泵速度读取，已停用）；V301.7保留位；V304.0/1/2（已迁至M16.4/5/6）；VD312（LeakDiff，已删除）；VD354（CycleSetpoint）；VD370（旧目标体积，功能由VD584替代）；以及全部UD镜像区废弃条目。
>
> - **新增项**：补充PLC代码实际使用但HMI通道缺失的地址。包括I0.3系统复位按钮、I0.4消音按钮；Q0.2~~Q0.4阀A/B/C输出、Q0.7报警声音、Q8.0报警灯光；VW304上缸子流程状态、VW306已完成下缸换水次数；VD116 S6滚动实测、VD244/VD256双倒计时器显示、VD414 24h换水目标、VD426周期尾端转移余量、VD430上缸配液安全余量；V1.1初始化完成、V1.2注射泵RTU在线、V0.1流量计RTU在线（均为M16.4/5/6的OB1镜像）；VB378~~VB383 Modbus错误码；VB900\~VB907 RTC时间。
>
> - **重大修正**：VD74在当前PLC代码中**既不存S4实测也不存S2实测**，原《HMI-PLC变量地址表\_v2.0》及CSV中的`U1_VD_S4_Actual`映射错误。S4转移实测时长实际写入**VD116（U1\_VD\_S6\_Rolling）**，首轮作为S6滚动默认值。
>
> - **命名规则**：保留HMI已有变量名（以`西门子_S7_Smart200_以太网_通道处理.csv`为准）；新增变量按`U1_类型_功能`规则命名，保持与现有风格一致。
>
> - **语义澄清**：VD28原名为VD\_PreMixTime（预循环搅拌时长），v2.2取消预循环后已改为**S2搅拌+加药合并阶段固定时长**。HMI变量名`U1_VD_PreMixTime`保持不变，但HMI画面标签与注释应同步更新为"S2搅拌时长"。

***

## 一、编址总则与地址区规划

### 1.1 编址总则

1. **8套PLC程序完全相同**：每台PLC使用相同的变量地址表，区别仅在IP地址（192.168.2.101\~108）。HMI通过不同IP连接不同单元。
2. **断电保持**：所有需要断电保持的V区变量，需在STEP 7-Micro/WIN SMART的"系统块→断电保持"中配置对应V区范围。
3. **HMI访问方式**：HMI通过以太网S7协议读写PLC的V区变量，按本表地址直接映射。
4. **命名规范**：变量符号采用 `U1_类型_功能` 命名，如 `U1_VD_ExperimentTarget`、`U1_CMD_Start`。
5. **PLC代码为唯一真值**：本表所有条目均以`plc/stl/*.stl`实际读写为准，旧版文档/CSV如有冲突，以本表为准。

### 1.2 地址区规划（v2.1 实际使用区）

| 地址区                        | 用途                          | 数据类型      | 断电保持 |
| -------------------------- | --------------------------- | --------- | ---- |
| I0.0 \~ I1.2, I8.0 \~ I8.5 | DI物理输入                      | BOOL      | —    |
| Q0.0 \~ Q0.7, Q8.0         | DO物理输出                      | BOOL      | —    |
| V0.0, V0.2 \~ V0.7         | 系统命令位（HMI→PLC）              | BOOL      | 是    |
| V1.0, V1.3 \~ V1.7         | 系统状态位（PLC→HMI）              | BOOL      | 是    |
| V306.0 \~ V307.3           | 手动控制命令位                     | BOOL      | 是    |
| VW2                        | 下缸主状态机当前状态                  | WORD      | 是    |
| VW4                        | 注射泵状态码                      | WORD      | 否    |
| VW6                        | 当前报警码                       | WORD      | 是    |
| VW8                        | 实验轮次计数                      | WORD      | 是    |
| VW304                      | 上缸配液子流程状态                   | WORD      | 是    |
| VW306                      | 已完成下缸换水次数                   | WORD      | 是    |
| VD24 \~ VD66               | HMI设定参数                     | REAL      | 是    |
| VD70/VD116                 | PLC实测值/计算值                  | REAL      | 是    |
| VD178                      | S5运行已用时长                    | REAL      | 是    |
| VD244/VD256                | 周期倒计时器显示值                   | REAL      | 否    |
| VD308                      | 阀A关阀快照                      | REAL      | 否    |
| VD316                      | 目标进水量                       | REAL      | 是    |
| VD350 \~ VD366             | 参数与累计值                      | REAL      | 是    |
| VD414/VD426/VD430          | v2.2节奏管理参数                  | REAL      | 是    |
| VD440/VD452                | 加药量/手动剂量                    | REAL      | 部分   |
| VD584                      | 目标抽取母液体积                    | REAL      | 是    |
| VB300 \~ VB303             | 报警字（4字节32位）                 | BYTE×4    | 是    |
| VB305                      | 系统总状态字                      | BYTE      | 否    |
| VB378 \~ VB383             | Modbus RTU错误码               | BYTE×6    | 否    |
| VB456 \~ VB536             | HMI参数镜像区                    | BYTE/REAL | 是    |
| VB900 \~ VB907             | RTC实时时钟BCD                  | BYTE×8    | 否    |
| V0.1/V1.1/V1.2             | M16.4/5/6的V区镜像(初始化完成/RTU在线) | BOOL      | 否    |
| VB500 \~ VB599             | 报警日志缓冲区（FC3）                | BYTE      | 是    |
| VB600 \~ VB6xx             | Modbus RTU Master库占用区       | BYTE      | 否    |

***

## 二、数字量输入DI映射

| PLC地址 | HMI变量名                          | 信号来源    | 信号类型     | 用途                |
| ----- | ------------------------------- | ------- | -------- | ----------------- |
| I0.0  | U1\_DI\_FlowSwitch\_A\_Inlet    | 流量开关A   | 无源常开     | 上缸进水流量检测          |
| I0.1  | U1\_DI\_FlowSwitch\_B\_UpToDown | 流量开关B   | 无源常开     | 上→下转移流量检测         |
| I0.2  | U1\_DI\_FlowSwitch\_C\_Drain    | 流量开关C   | 无源常开     | 下缸排水流量检测          |
| I0.3  | U1\_DI\_SystemReset             | 系统复位按钮  | 无源常开点动   | 急停解除后系统复位（v2.1新增） |
| I0.4  | U1\_DI\_MuteBtn                 | 消音按钮    | 无源常开点动   | 就地面板消音（v2.1新增）    |
| I0.5  | U1\_DI\_LevelA\_High            | 液位计A-高位 | 无源常开     | 上缸漫溢保护            |
| I0.6  | U1\_DI\_LevelA\_Low             | 液位计A-低位 | 无源常开     | 上缸已排空检测           |
| I0.7  | U1\_DI\_LevelB\_High            | 液位计B-高位 | 无源常开     | 下缸漫溢保护            |
| I1.0  | U1\_DI\_LevelB\_Low             | 液位计B-低位 | 无源常开     | 下缸已排空检测           |
| I1.1  | U1\_DI\_EStop                   | 急停按钮    | 常开NO     | 急停触发信号            |
| I1.2  | U1\_DI\_SafetyRelay\_Feedback   | 安全继电器反馈 | 干接点NO    | 动力切断反馈            |
| I8.0  | U1\_DI\_ValveA\_Open            | 阀A开到位   | 有源→继电器转换 | 阀A全开确认            |
| I8.1  | U1\_DI\_ValveA\_Close           | 阀A关到位   | 有源→继电器转换 | 阀A全关确认            |
| I8.2  | U1\_DI\_ValveB\_Open            | 阀B开到位   | 有源→继电器转换 | 阀B全开确认            |
| I8.3  | U1\_DI\_ValveB\_Close           | 阀B关到位   | 有源→继电器转换 | 阀B全关确认            |
| I8.4  | U1\_DI\_ValveC\_Open            | 阀C开到位   | 有源→继电器转换 | 阀C全开确认            |
| I8.5  | U1\_DI\_ValveC\_Close           | 阀C关到位   | 有源→继电器转换 | 阀C全关确认            |

**容量**：本体12DI + DR32扩展8DI = 20DI，使用17点，I8.6/I8.7预留备用。

***

## 三、数字量输出DO映射

| PLC地址 | HMI变量名                  | 驱动负载    | 用途             |
| ----- | ----------------------- | ------- | -------------- |
| Q0.0  | U1\_DO\_Pump1           | 潜水泵1    | 上缸搅拌泵1         |
| Q0.1  | U1\_DO\_Pump2           | 潜水泵2    | 上缸搅拌泵2         |
| Q0.2  | U1\_DO\_ValveA          | 电动球阀A   | 上缸进水（v2.1新增）   |
| Q0.3  | U1\_DO\_ValveB          | 电动球阀B   | 上→下转移（v2.1新增）  |
| Q0.4  | U1\_DO\_ValveC          | 电动球阀C   | 下缸排水（v2.1新增）   |
| Q0.5  | U1\_DO\_NCValve\_Top    | NC球阀-上缸 | 阀A失效第二道保护      |
| Q0.6  | U1\_DO\_NCValve\_Bottom | NC球阀-下缸 | 阀B/液位B高报警第二道保护 |
| Q0.7  | U1\_DO\_Alarm\_Sound    | 报警-声音   | 蜂鸣器输出（v2.1新增）  |
| Q8.0  | U1\_DO\_Alarm\_Light    | 报警-灯光   | 报警灯输出（v2.1新增）  |

***

## 四、系统命令位与状态位

### 4.1 系统命令位（V0区，HMI→PLC，断电保持）

| 地址   | HMI变量名                               | 说明           | 握手确认         |
| ---- | ------------------------------------ | ------------ | ------------ |
| V0.0 | U1\_CMD\_Start                       | 启动实验         | PLC置V1.0=1确认 |
| V0.2 | U1\_CMD\_Stop                        | 停止实验         | PLC清V0.2=0确认 |
| V0.3 | U1\_CMD\_AckAlarm                    | 报警确认         | PLC置V1.3=1确认 |
| V0.4 | U1\_CMD\_Mute                        | 消音命令         | PLC置V1.4=1确认 |
| V0.5 | U1\_Reserved\_CMD\_ForceTankA\_Empty | 强制上缸空（预留未实现） | —            |
| V0.6 | U1\_CMD\_RTC\_Sync                   | RTC校时命令      | PLC清V0.6=0确认 |
| V0.7 | U1\_CMD\_SafetyRelayAck              | 安全继电器故障确认    | PLC清V0.7=0确认 |

> **说明**：V0.1暂停命令位在PLC当前程序中未使用，已从本表删除；V0.5功能预留但当前未实现，保留占位但不下发有效命令。

### 4.2 系统状态位（V1区，PLC→HMI，断电保持）

| 地址   | HMI变量名                | 说明           |
| ---- | --------------------- | ------------ |
| V1.0 | U1\_STA\_StartAck     | 启动命令已接收      |
| V1.3 | U1\_STA\_AlarmAckDone | 报警确认已执行      |
| V1.4 | U1\_STA\_MuteDone     | 消音已执行        |
| V1.5 | U1\_STA\_ForceDone    | 强制修正已执行      |
| V1.6 | U1\_STA\_TankA\_State | 上缸状态：0=空，1=满 |
| V1.7 | U1\_STA\_TankB\_State | 下缸状态：0=空，1=满 |

> **说明**：V1.1/V1.2在PLC当前程序中未使用，已从本表删除。

### 4.3 系统总状态字

| 地址    | HMI变量名               | 说明                   |
| ----- | -------------------- | -------------------- |
| VB305 | U1\_VB\_SystemStatus | 系统总状态：0=良好/1=故障/2=急停 |

***

## 五、状态机与泵状态

### 5.1 下缸主状态机（VW2）

| 值  | 状态       | 说明      |
| -- | -------- | ------- |
| 0  | S0 初始化   | 待机、等待启动 |
| 5  | S4 转移    | 上缸→下缸转移 |
| 6  | S5 实验运行  | 下缸实验计时中 |
| 7  | S6 下缸排水  | 下缸排空    |
| 8  | S7 实验结束  | 全部结束    |
| 99 | S\_ERROR | 报警停机    |

### 5.2 上缸配液子流程状态（VW304，v2.2新增）

| 值 | HMI变量名                   | 状态         | 说明          |
| - | ------------------------ | ---------- | ----------- |
| — | U1\_VW304\_State\_UpTank | 0 空闲       | 上缸无配液任务     |
| — | —                        | 1 S1上缸进水   | 阀A开，流量计累计   |
| — | —                        | 2 S2搅拌+加药  | 潜水泵运行，注射泵加药 |
| — | —                        | 3 S3配完等待转移 | 已完成，等下缸排空   |
| — | —                        | 4 已转移      | 本轮完成，准备下一轮  |

### 5.3 注射泵状态码（VW4）

| 状态码 | 含义    | HMI处理     |
| --- | ----- | --------- |
| 0   | 就绪/完成 | 可下发新指令    |
| 1   | 空闲    | 等待        |
| 2   | 运动中   | 显示"加药中"   |
| ≥4  | 错误码   | 触发注射泵故障报警 |

### 5.4 其他状态字

| 地址    | HMI变量名                | 说明                  |
| ----- | --------------------- | ------------------- |
| VW6   | U1\_VW6\_AlarmCode    | 当前最高优先级未确认报警码，0=无报警 |
| VW8   | U1\_VW8\_RoundCount   | 当前实验轮次计数            |
| VW306 | U1\_VW306\_CycleCount | 已完成下缸换水次数（v2.2新增）   |

***

## 六、HMI设定参数（VD区）

| 地址    | HMI变量名                        | 单位   | 说明                |
| ----- | ----------------------------- | ---- | ----------------- |
| VD24  | U1\_VD\_ExperimentTarget      | min  | 实验时长目标设定值         |
| VD28  | U1\_VD\_PreMixTime            | s    | S2搅拌+加药固定时长       |
| VD54  | U1\_VD\_Timeout\_ValveC       | s    | 阀C动作超时保护时长        |
| VD66  | U1\_VD\_Delay\_ValveA\_Verify | s    | 阀A关闭后延时验证时长       |
| VD316 | U1\_VD\_TargetInletVolume     | L    | 目标进水量             |
| VD350 | U1\_VD\_StepResolution        | µL/步 | 注射泵单步分辨率          |
| VD358 | U1\_VD\_Timeout\_ValveA       | s    | 阀A动作超时保护时长        |
| VD362 | U1\_VD\_Timeout\_ValveB       | s    | 阀B动作超时保护时长        |
| VD414 | U1\_VD\_24h\_Target           | 次    | 24h换水目标次数（v2.2新增） |
| VD426 | U1\_VD\_Transfer\_Margin      | s    | 周期尾端转移余量（v2.2新增）  |
| VD430 | U1\_VD\_Prep\_Safety\_Margin  | s    | 上缸配液安全余量（v2.2新增）  |
| VD452 | U1\_VD\_ManualDose\_Target    | µL   | 手动注射泵总加药量         |
| VD584 | U1\_VD\_Vol\_Target           | µL   | 自动模式目标抽取母液体积      |

> **删除说明**：VD10/VD14目标浓度/母液浓度、VD32/VD36/VD40/VD44预循环参数、VD58/VD62泵超时保护（预留未用，无报警逻辑）、VD108首轮S6默认时长（v2.2改为直接用VD116首轮S4实测值）、VD120/VD124/VD128/VD144节奏目标/默认值、VD132/VD136/VD140泵速度设定、VD174 S3估算、VD354周期设定点、VD448 S4等待超时阈值（v2.2设计未使用，FC15中仅为兼容保留）、VD444 S4等待时长（v2.2设计未使用，实为PLC内部工作变量）等已从PLC代码删除或不再面向HMI，本表不再列出。

***

## 七、PLC实测值与计算值（VD区）

| 地址    | HMI变量名                            | 说明                  | 数据来源           |
| ----- | --------------------------------- | ------------------- | -------------- |
| VD70  | U1\_VD\_S1\_Actual                | S1上缸进水实测时长(s)       | FC11写入         |
| VD82  | U1\_VD\_FlowMeter\_Snapshot       | 阀A开启瞬间流量计快照         | FC11写入         |
| VD86  | U1\_VD\_FlowMeter\_Current        | 流量计当前累计值            | FC4 Modbus读取   |
| VD90  | U1\_VD\_Current\_InletVolume      | 本次当前进水量(L)          | FC11计算         |
| VD94  | U1\_VD\_FlowRate\_Instant         | 瞬时流速(L/min)         | FC4 Modbus读取   |
| VD102 | U1\_VD\_Dose\_Steps               | 本轮加药目标步数            | FC13计算         |
| VD116 | U1\_VD\_S6\_Rolling               | S6滚动实测时长(s)，首轮存S4实测 | FC15/FC17写入    |
| VD178 | U1\_VD\_S5\_Elapsed               | S5运行已用时长(s)         | FC16/SBR26写入   |
| VD244 | U1\_VD\_TimerB\_Display           | 周期倒计时器B当前值(s)       | FC40写入（v2.2新增） |
| VD256 | U1\_VD\_TimerA\_Display           | 周期倒计时器A当前值(s)       | FC40写入（v2.2新增） |
| VD308 | U1\_VD\_FlowMeter\_CloseSnapshot  | 阀A关阀快照              | FC30写入         |
| VD366 | U1\_VD\_ExperimentDuration\_Accum | 实验时长累加值(min)        | FC16/FC17写入    |
| VD440 | U1\_VD\_Dosed\_Volume\_Total      | 累计加药量(µL)           | FC13/FC1A写入    |

> **重大修正**：旧版文档/CSV将VD74标注为`U1_VD_S4_Actual`。经核对PLC代码（FC15 L97 `MOVR VD444, VD116`），S4转移实测时长实际写入**VD116**。VD74在全部STL中无读写，属于悬空地址。本表已删除VD74条目。

***

## 八、配液节奏纠偏变量（v2.2 双倒计时器）

| 地址     | HMI变量名                         | 读写 | 说明               |
| ------ | ------------------------------ | -- | ---------------- |
| VD414  | U1\_VD\_24h\_Target            | 读写 | 24h换水目标次数        |
| VD426  | U1\_VD\_Transfer\_Margin       | 读写 | 周期尾端转移余量(s)      |
| VD430  | U1\_VD\_Prep\_Safety\_Margin   | 读写 | 上缸配液安全余量(s)      |
| VD244  | U1\_VD\_TimerB\_Display        | 只读 | 倒计时器B当前显示值(s)    |
| VD256  | U1\_VD\_TimerA\_Display        | 只读 | 倒计时器A当前显示值(s)    |
| VD116  | U1\_VD\_S6\_Rolling            | 读写 | S6滚动实测/首轮S4实测(s) |
| V303.6 | U1\_Alarm\_FlowSwitch\_Instant | 只读 | 单轮换水周期超时报警       |

> **说明**：FC40根据VD414计算单次目标周期，通过T46/T48双倒计时器乒乓工作，保证24h换水次数硬约束。VD244/VD256供HMI显示两个倒计时器当前值。

***

## 九、报警标志与报警码定义

### 9.1 报警字 VB300 \~ VB303

| 地址     | HMI变量名                           | 说明             |
| ------ | -------------------------------- | -------------- |
| V300.0 | U1\_Alarm\_Overflow\_AHigh       | 上缸漫溢报警         |
| V300.1 | U1\_Alarm\_Overflow\_BHigh       | 下缸漫溢报警         |
| V300.2 | U1\_Alarm\_NCValve\_Top          | NC球阀-上缸动作报警    |
| V300.3 | U1\_Alarm\_NCValve\_Bottom       | NC球阀-下缸动作报警    |
| V300.4 | U1\_EStop\_Latch                 | 急停触发锁存         |
| V300.5 | U1\_Alarm\_SafetyRelay           | 安全继电器故障        |
| V300.6 | U1\_Alarm\_ScheduleLag           | 配液节奏严重滞后       |
| V300.7 | U1\_Alarm\_ScheduleLag\_Warn     | 配液节奏滞后提示       |
| V301.0 | U1\_Alarm\_ValveA\_CloseFlow     | 阀A关后延时验证仍有流    |
| V301.2 | U1\_Alarm\_ValveA\_CloseTimeout  | 阀A关到位反馈超时      |
| V301.3 | U1\_Alarm\_ValveA\_CloseLeak     | 阀A关到位但仍有流      |
| V301.4 | U1\_Alarm\_ValveA\_OpenTimeout   | 阀A开到位反馈超时      |
| V301.5 | U1\_Alarm\_ValveA\_OpenNoFlow    | 阀A开到位但无流       |
| V301.6 | U1\_Alarm\_ValveA\_S1Start       | S5触发新一轮S1时上缸非空 |
| V302.0 | U1\_Alarm\_ValveB\_Diag          | 阀B四态诊断异常       |
| V302.1 | U1\_Alarm\_ValveB\_OpenTimeout   | 阀B开到位反馈超时      |
| V302.2 | U1\_Alarm\_ValveB\_OpenNoFlow    | 阀B开到位但无流       |
| V302.3 | U1\_Alarm\_ValveB\_CloseTimeout  | 阀B关到位反馈超时      |
| V302.4 | U1\_Alarm\_ValveB\_CloseLeak     | 阀B关到位但仍有流      |
| V302.5 | U1\_Alarm\_ValveC\_Diag          | 阀C四态诊断异常       |
| V302.6 | U1\_Alarm\_ValveC\_OpenTimeout   | 阀C开到位反馈超时      |
| V302.7 | U1\_Alarm\_ValveC\_OpenNoFlow    | 阀C开到位但无流       |
| V303.0 | U1\_Alarm\_ValveC\_CloseTimeout  | 阀C关到位反馈超时      |
| V303.1 | U1\_Alarm\_ValveC\_CloseLeak     | 阀C关到位但仍有流      |
| V303.2 | U1\_Alarm\_S4TransferWaitTimeout | S4等待超时报警       |
| V303.4 | U1\_Alarm\_SyringePump           | 注射泵通讯/动作异常     |
| V303.5 | U1\_Alarm\_RTC\_Lost             | RTC时钟丢失        |
| V303.6 | U1\_Alarm\_FlowSwitch\_Instant   | 单轮换水周期超时       |
| V303.7 | U1\_Need\_RTC\_Sync              | PLC请求HMI同步RTC  |

> **说明**：V301.1（原阀A内漏判定）和V301.7保留位已从PLC代码删除；V304.0~~V304.2先迁至M16.4~~M16.6，后因McgsPro驱动不支持M区导入，改为在OB1中镜像到V1.1/V1.2/V0.1。

### 9.2 当前报警码（VW6）

由FC3按优先级编码，HMI读取VW6显示当前最高优先级报警。详见PLC设计文档第九章。

***

## 十、手动控制命令位

| 地址     | HMI变量名                              | 说明                  |
| ------ | ----------------------------------- | ------------------- |
| V306.0 | U1\_CMD\_Manual\_ValveA\_Open       | 手动开阀A               |
| V306.1 | U1\_CMD\_Manual\_ValveA\_Close      | 手动关阀A               |
| V306.2 | U1\_CMD\_Manual\_ValveB\_Open       | 手动开阀B               |
| V306.3 | U1\_CMD\_Manual\_ValveB\_Close      | 手动关阀B               |
| V306.4 | U1\_CMD\_Manual\_ValveC\_Open       | 手动开阀C               |
| V306.5 | U1\_CMD\_Manual\_ValveC\_Close      | 手动关阀C               |
| V306.6 | U1\_CMD\_Manual\_Pump1\_On          | 手动启动潜水泵1            |
| V306.7 | U1\_CMD\_Manual\_Pump1\_Off         | 手动停止潜水泵1            |
| V307.0 | U1\_CMD\_Manual\_Pump2\_On          | 手动启动潜水泵2            |
| V307.1 | U1\_CMD\_Manual\_Pump2\_Off         | 手动停止潜水泵2            |
| V307.2 | U1\_CMD\_Manual\_SyringePump\_Start | 手动注射泵启动             |
| V307.3 | U1\_CMD\_Manual\_SyringePump\_Stop  | 手动注射泵停止/回零          |
| V309.0 | U1\_V309\_0\_DebugMode              | 调试模式开关（旁路阀B/阀C液位联锁） |

***

## 十一、手动注射泵参数与状态

| 地址    | HMI变量名                        | 读写 | 说明                                |
| ----- | ----------------------------- | -- | --------------------------------- |
| VW388 | U1\_VD\_ManualDose\_Mode      | 读写 | 手动注射泵模式：0=单次，1=循环                 |
| VW390 | U1\_VW\_ManualDose\_State     | 只读 | 手动注射泵子状态：0空闲/1抽液/2排液/3回零/4完成/99错误 |
| VD392 | U1\_VD\_ManualDose\_Dosed     | 只读 | 手动注射泵累计加药量(µL)                    |
| VD396 | U1\_VD\_ManualDose\_Remaining | 只读 | 手动注射泵剩余加药量(µL)                    |

***

## 十二、RTC实时时钟

| 地址    | HMI变量名                   | 说明        |
| ----- | ------------------------ | --------- |
| VB900 | U1\_VB900\_RTC\_Year     | RTC年（BCD） |
| VB901 | U1\_VB901\_RTC\_Month    | RTC月（BCD） |
| VB902 | U1\_VB902\_RTC\_Day      | RTC日（BCD） |
| VB903 | U1\_VB903\_RTC\_Hour     | RTC时（BCD） |
| VB904 | U1\_VB904\_RTC\_Minute   | RTC分（BCD） |
| VB905 | U1\_VB905\_RTC\_Second   | RTC秒（BCD） |
| VB906 | U1\_VB906\_RTC\_Weekday  | RTC星期     |
| VB907 | U1\_VB907\_RTC\_Reserved | RTC保留     |

***

## 十三、Modbus RTU通讯状态

| 地址    | HMI变量名                           | 说明                    |
| ----- | -------------------------------- | --------------------- |
| VB378 | U1\_VB378\_MB\_CTRL\_Error       | MBUS\_CTRL错误码         |
| VB379 | U1\_VB379\_MB\_MSG\_Error\_Task0 | MBUS\_MSG任务0错误（泵状态读）  |
| VB380 | U1\_VB380\_MB\_MSG\_Error\_Task2 | MBUS\_MSG任务2错误（泵位置读）  |
| VB381 | U1\_VB381\_MB\_MSG\_Error\_Task1 | MBUS\_MSG任务1错误（流量计读）  |
| VB382 | U1\_VB382\_MB\_MSG\_Error\_Task3 | MBUS\_MSG任务3错误（瞬时流量读） |
| VB383 | U1\_VB383\_MB\_MSG\_Error\_Task4 | MBUS\_MSG任务4错误（泵写命令）  |
| VW294 | U1\_VW294\_PumpContFail          | 注射泵连续失败计数             |
| VW296 | U1\_VW296\_FlowContFail          | 流量计连续失败计数             |

***

## 十四、HMI参数镜像区（断电保持默认值）

PLC在SBR25冷启动时读取以下镜像值作为HMI参数的断电保持默认值。

| 地址    | HMI变量名                    | 镜像源   | 说明                      |
| ----- | ------------------------- | ----- | ----------------------- |
| VB456 | U1\_UD\_Flag              | —     | HMI参数镜像标志字节             |
| VD460 | U1\_UD\_VD24\_ExpTarget   | VD24  | HMI镜像 VD24\_ExpTarget   |
| VD464 | U1\_UD\_VD28\_PreMixTime  | VD28  | HMI镜像 VD28\_PreMixTime  |
| VD488 | U1\_UD\_VD66\_DelayA      | VD66  | HMI镜像 VD66\_DelayA      |
| VD500 | U1\_UD\_VD316\_InletVol   | VD316 | HMI镜像 VD316\_InletVol   |
| VD504 | U1\_UD\_VD350\_StepRes    | VD350 | HMI镜像 VD350\_StepRes    |
| VD512 | U1\_UD\_VD358\_TimeoutA   | VD358 | HMI镜像 VD358\_TimeoutA   |
| VD516 | U1\_UD\_VD362\_TimeoutB   | VD362 | HMI镜像 VD362\_TimeoutB   |
| VD528 | U1\_UD\_VD452\_ManualDose | VD452 | HMI镜像 VD452\_ManualDose |

> **说明**：UD镜像区中对应VD32/VD36/VD40/VD44/VD108/VD144/VD354/VD370/VW388/V200.0等已删除参数的条目不再使用，本表仅保留PLC在SBR25中实际读取的镜像项。

***

## 十五、HMI-PLC变量交互总表

| PLC地址  | HMI变量名                               | 数据类型    | HMI读写 | PLC用途             | 备注             |
| ------ | ------------------------------------ | ------- | ----- | ----------------- | -------------- |
| I0.0   | U1\_DI\_FlowSwitch\_A\_Inlet         | INTEGER | 只读    | 上缸进水流量开关          | —              |
| I0.1   | U1\_DI\_FlowSwitch\_B\_UpToDown      | INTEGER | 只读    | 上→下转移流量开关         | —              |
| I0.2   | U1\_DI\_FlowSwitch\_C\_Drain         | INTEGER | 只读    | 下缸排水流量开关          | —              |
| I0.3   | U1\_DI\_SystemReset                  | INTEGER | 只读    | 系统复位按钮            | v2.1新增         |
| I0.4   | U1\_DI\_MuteBtn                      | INTEGER | 只读    | 消音按钮              | v2.1新增         |
| I0.5   | U1\_DI\_LevelA\_High                 | INTEGER | 只读    | 上缸液位高位            | —              |
| I0.6   | U1\_DI\_LevelA\_Low                  | INTEGER | 只读    | 上缸液位低位            | —              |
| I0.7   | U1\_DI\_LevelB\_High                 | INTEGER | 只读    | 下缸液位高位            | —              |
| I1.0   | U1\_DI\_LevelB\_Low                  | INTEGER | 只读    | 下缸液位低位            | —              |
| I1.1   | U1\_DI\_EStop                        | INTEGER | 只读    | 急停按钮              | —              |
| I1.2   | U1\_DI\_SafetyRelay\_Feedback        | INTEGER | 只读    | 安全继电器反馈           | —              |
| I8.0   | U1\_DI\_ValveA\_Open                 | INTEGER | 只读    | 阀A开到位             | —              |
| I8.1   | U1\_DI\_ValveA\_Close                | INTEGER | 只读    | 阀A关到位             | —              |
| I8.2   | U1\_DI\_ValveB\_Open                 | INTEGER | 只读    | 阀B开到位             | —              |
| I8.3   | U1\_DI\_ValveB\_Close                | INTEGER | 只读    | 阀B关到位             | —              |
| I8.4   | U1\_DI\_ValveC\_Open                 | INTEGER | 只读    | 阀C开到位             | —              |
| I8.5   | U1\_DI\_ValveC\_Close                | INTEGER | 只读    | 阀C关到位             | —              |
| Q0.0   | U1\_DO\_Pump1                        | INTEGER | 只读    | 潜水泵1输出            | —              |
| Q0.1   | U1\_DO\_Pump2                        | INTEGER | 只读    | 潜水泵2输出            | —              |
| Q0.2   | U1\_DO\_ValveA                       | INTEGER | 只读    | 阀A输出              | v2.1新增         |
| Q0.3   | U1\_DO\_ValveB                       | INTEGER | 只读    | 阀B输出              | v2.1新增         |
| Q0.4   | U1\_DO\_ValveC                       | INTEGER | 只读    | 阀C输出              | v2.1新增         |
| Q0.5   | U1\_DO\_NCValve\_Top                 | INTEGER | 读写    | 上缸NC球阀输出          | —              |
| Q0.6   | U1\_DO\_NCValve\_Bottom              | INTEGER | 读写    | 下缸NC球阀输出          | —              |
| Q0.7   | U1\_DO\_Alarm\_Sound                 | INTEGER | 只读    | 报警声音输出            | v2.1新增         |
| Q8.0   | U1\_DO\_Alarm\_Light                 | INTEGER | 只读    | 报警灯光输出            | v2.1新增         |
| V0.0   | U1\_CMD\_Start                       | INTEGER | 读写    | 启动命令              | —              |
| V0.2   | U1\_CMD\_Stop                        | INTEGER | 读写    | 停止命令              | —              |
| V0.3   | U1\_CMD\_AckAlarm                    | INTEGER | 读写    | 报警确认命令            | —              |
| V0.4   | U1\_CMD\_Mute                        | INTEGER | 读写    | 消音命令              | —              |
| V0.5   | U1\_Reserved\_CMD\_ForceTankA\_Empty | INTEGER | 读写    | 强制上缸空（预留）         | 未实现            |
| V0.6   | U1\_CMD\_RTC\_Sync                   | INTEGER | 读写    | RTC校时命令           | —              |
| V0.7   | U1\_CMD\_SafetyRelayAck              | INTEGER | 读写    | 安全继电器故障确认         | —              |
| V1.0   | U1\_STA\_StartAck                    | INTEGER | 只读    | 启动命令确认            | —              |
| V1.3   | U1\_STA\_AlarmAckDone                | INTEGER | 只读    | 报警确认完成            | —              |
| V1.4   | U1\_STA\_MuteDone                    | INTEGER | 只读    | 消音完成              | —              |
| V1.5   | U1\_STA\_ForceDone                   | INTEGER | 只读    | 强制修正完成            | —              |
| V1.6   | U1\_STA\_TankA\_State                | INTEGER | 只读    | 上缸状态              | 0=空/1=满        |
| V1.7   | U1\_STA\_TankB\_State                | INTEGER | 只读    | 下缸状态              | 0=空/1=满        |
| VW2    | U1\_VW2\_StateMachine                | SINGLE  | 只读    | 下缸主状态机            | —              |
| VW4    | U1\_VW4\_PumpStatus                  | SINGLE  | 只读    | 注射泵状态码            | —              |
| VW6    | U1\_VW6\_AlarmCode                   | SINGLE  | 只读    | 当前报警码             | —              |
| VW8    | U1\_VW8\_RoundCount                  | SINGLE  | 只读    | 实验轮次计数            | —              |
| VW304  | U1\_VW304\_State\_UpTank             | SINGLE  | 只读    | 上缸配液子流程状态         | v2.2新增         |
| VW306  | U1\_VW306\_CycleCount                | SINGLE  | 只读    | 已完成下缸换水次数         | v2.2新增         |
| V200.0 | U1\_M\_AlarmAckMode                  | INTEGER | 读写    | 报警确认模式            | 0=自动/1=人工      |
| VD24   | U1\_VD\_ExperimentTarget             | SINGLE  | 读写    | 实验时长目标(min)       | —              |
| VD28   | U1\_VD\_PreMixTime                   | SINGLE  | 读写    | S2搅拌固定时长(s)       | —              |
| VD54   | U1\_VD\_Timeout\_ValveC              | SINGLE  | 读写    | 阀C超时保护(s)         | —              |
| VD66   | U1\_VD\_Delay\_ValveA\_Verify        | SINGLE  | 读写    | 阀A关后验证延时(s)       | —              |
| VD70   | U1\_VD\_S1\_Actual                   | SINGLE  | 只读    | S1实测时长(s)         | —              |
| VD82   | U1\_VD\_FlowMeter\_Snapshot          | SINGLE  | 只读    | 流量计开启快照           | —              |
| VD86   | U1\_VD\_FlowMeter\_Current           | SINGLE  | 只读    | 流量计当前累计值          | —              |
| VD90   | U1\_VD\_Current\_InletVolume         | SINGLE  | 只读    | 本次当前进水量(L)        | —              |
| VD94   | U1\_VD\_FlowRate\_Instant            | SINGLE  | 只读    | 瞬时流速(L/min)       | —              |
| VD102  | U1\_VD\_Dose\_Steps                  | SINGLE  | 只读    | 本轮加药目标步数          | —              |
| VD116  | U1\_VD\_S6\_Rolling                  | SINGLE  | 只读    | S6滚动实测(s),首轮为S4实测 | 重要修正           |
| VD178  | U1\_VD\_S5\_Elapsed                  | SINGLE  | 只读    | S5运行已用时长(s)       | —              |
| VD244  | U1\_VD\_TimerB\_Display              | SINGLE  | 只读    | 倒计时器B当前值(s)       | v2.2新增         |
| VD256  | U1\_VD\_TimerA\_Display              | SINGLE  | 只读    | 倒计时器A当前值(s)       | v2.2新增         |
| VD308  | U1\_VD\_FlowMeter\_CloseSnapshot     | SINGLE  | 只读    | 阀A关阀快照            | —              |
| VD316  | U1\_VD\_TargetInletVolume            | SINGLE  | 读写    | 目标进水量(L)          | —              |
| VD350  | U1\_VD\_StepResolution               | SINGLE  | 读写    | 注射泵单步分辨率(µL/步)    | —              |
| VD358  | U1\_VD\_Timeout\_ValveA              | SINGLE  | 读写    | 阀A超时保护(s)         | —              |
| VD362  | U1\_VD\_Timeout\_ValveB              | SINGLE  | 读写    | 阀B超时保护(s)         | —              |
| VD366  | U1\_VD\_ExperimentDuration\_Accum    | SINGLE  | 只读    | 实验时长累加(min)       | —              |
| VD414  | U1\_VD\_24h\_Target                  | SINGLE  | 读写    | 24h换水目标次数         | v2.2新增         |
| VD426  | U1\_VD\_Transfer\_Margin             | SINGLE  | 读写    | 周期尾端转移余量(s)       | v2.2新增         |
| VD430  | U1\_VD\_Prep\_Safety\_Margin         | SINGLE  | 读写    | 上缸配液安全余量(s)       | v2.2新增         |
| VD440  | U1\_VD\_Dosed\_Volume\_Total         | SINGLE  | 只读    | 累计加药量(µL)         | —              |
| VD452  | U1\_VD\_ManualDose\_Target           | SINGLE  | 读写    | 手动注射泵总加药量(µL)     | —              |
| VD584  | U1\_VD\_Vol\_Target                  | SINGLE  | 读写    | 目标抽取母液体积(µL)      | —              |
| VB305  | U1\_VB\_SystemStatus                 | SINGLE  | 只读    | 系统总状态字            | 0=良好/1=故障/2=急停 |
| V300.0 | U1\_Alarm\_Overflow\_AHigh           | INTEGER | 只读    | 上缸漫溢报警            | —              |
| V300.1 | U1\_Alarm\_Overflow\_BHigh           | INTEGER | 只读    | 下缸漫溢报警            | —              |
| V300.2 | U1\_Alarm\_NCValve\_Top              | INTEGER | 只读    | NC球阀-上缸动作         | —              |
| V300.3 | U1\_Alarm\_NCValve\_Bottom           | INTEGER | 只读    | NC球阀-下缸动作         | —              |
| V300.4 | U1\_EStop\_Latch                     | INTEGER | 只读    | 急停触发锁存            | —              |
| V300.5 | U1\_Alarm\_SafetyRelay               | INTEGER | 只读    | 安全继电器故障           | —              |
| V300.6 | U1\_Alarm\_ScheduleLag               | INTEGER | 只读    | 配液节奏严重滞后          | —              |
| V300.7 | U1\_Alarm\_ScheduleLag\_Warn         | INTEGER | 只读    | 配液节奏滞后提示          | —              |
| V301.0 | U1\_Alarm\_ValveA\_CloseFlow         | INTEGER | 只读    | 阀A关后延时仍有流         | —              |
| V301.2 | U1\_Alarm\_ValveA\_CloseTimeout      | INTEGER | 只读    | 阀A关到位超时           | —              |
| V301.3 | U1\_Alarm\_ValveA\_CloseLeak         | INTEGER | 只读    | 阀A关到位但仍有流         | —              |
| V301.4 | U1\_Alarm\_ValveA\_OpenTimeout       | INTEGER | 只读    | 阀A开到位超时           | —              |
| V301.5 | U1\_Alarm\_ValveA\_OpenNoFlow        | INTEGER | 只读    | 阀A开到位但无流          | —              |
| V301.6 | U1\_Alarm\_ValveA\_S1Start           | INTEGER | 只读    | S5触发S1时上缸非空       | —              |
| V302.0 | U1\_Alarm\_ValveB\_Diag              | INTEGER | 只读    | 阀B四态诊断异常          | —              |
| V302.1 | U1\_Alarm\_ValveB\_OpenTimeout       | INTEGER | 只读    | 阀B开到位超时           | —              |
| V302.2 | U1\_Alarm\_ValveB\_OpenNoFlow        | INTEGER | 只读    | 阀B开到位但无流          | —              |
| V302.3 | U1\_Alarm\_ValveB\_CloseTimeout      | INTEGER | 只读    | 阀B关到位超时           | —              |
| V302.4 | U1\_Alarm\_ValveB\_CloseLeak         | INTEGER | 只读    | 阀B关到位但仍有流         | —              |
| V302.5 | U1\_Alarm\_ValveC\_Diag              | INTEGER | 只读    | 阀C四态诊断异常          | —              |
| V302.6 | U1\_Alarm\_ValveC\_OpenTimeout       | INTEGER | 只读    | 阀C开到位超时           | —              |
| V302.7 | U1\_Alarm\_ValveC\_OpenNoFlow        | INTEGER | 只读    | 阀C开到位但无流          | —              |
| V303.0 | U1\_Alarm\_ValveC\_CloseTimeout      | INTEGER | 只读    | 阀C关到位超时           | —              |
| V303.1 | U1\_Alarm\_ValveC\_CloseLeak         | INTEGER | 只读    | 阀C关到位但仍有流         | —              |
| V303.2 | U1\_Alarm\_S4TransferWaitTimeout     | INTEGER | 只读    | S4等待超时报警          | —              |
| V303.4 | U1\_Alarm\_SyringePump               | INTEGER | 只读    | 注射泵通讯/动作异常        | —              |
| V303.5 | U1\_Alarm\_RTC\_Lost                 | INTEGER | 只读    | RTC时钟丢失           | —              |
| V303.6 | U1\_Alarm\_FlowSwitch\_Instant       | INTEGER | 只读    | 单轮换水周期超时          | v2.2复用         |
| V303.7 | U1\_Need\_RTC\_Sync                  | INTEGER | 只读    | PLC请求HMI同步RTC     | —              |
| V306.0 | U1\_CMD\_Manual\_ValveA\_Open        | INTEGER | 读写    | 手动开阀A             | —              |
| V306.1 | U1\_CMD\_Manual\_ValveA\_Close       | INTEGER | 读写    | 手动关阀A             | —              |
| V306.2 | U1\_CMD\_Manual\_ValveB\_Open        | INTEGER | 读写    | 手动开阀B             | —              |
| V306.3 | U1\_CMD\_Manual\_ValveB\_Close       | INTEGER | 读写    | 手动关阀B             | —              |
| V306.4 | U1\_CMD\_Manual\_ValveC\_Open        | INTEGER | 读写    | 手动开阀C             | —              |
| V306.5 | U1\_CMD\_Manual\_ValveC\_Close       | INTEGER | 读写    | 手动关阀C             | —              |
| V306.6 | U1\_CMD\_Manual\_Pump1\_On           | INTEGER | 读写    | 手动启动潜水泵1          | —              |
| V306.7 | U1\_CMD\_Manual\_Pump1\_Off          | INTEGER | 读写    | 手动停止潜水泵1          | —              |
| V307.0 | U1\_CMD\_Manual\_Pump2\_On           | INTEGER | 读写    | 手动启动潜水泵2          | —              |
| V307.1 | U1\_CMD\_Manual\_Pump2\_Off          | INTEGER | 读写    | 手动停止潜水泵2          | —              |
| V307.2 | U1\_CMD\_Manual\_SyringePump\_Start  | INTEGER | 读写    | 手动注射泵启动           | —              |
| V307.3 | U1\_CMD\_Manual\_SyringePump\_Stop   | INTEGER | 读写    | 手动注射泵停止/回零        | —              |
| V309.0 | U1\_V309\_0\_DebugMode               | INTEGER | 读写    | 调试模式开关            | —              |
| VW388  | U1\_VD\_ManualDose\_Mode             | SINGLE  | 读写    | 手动注射泵模式           | 0=单次/1=循环      |
| VW390  | U1\_VW\_ManualDose\_State            | SINGLE  | 只读    | 手动注射泵子状态          | —              |
| VD392  | U1\_VD\_ManualDose\_Dosed            | SINGLE  | 只读    | 手动注射泵累计加药量        | —              |
| VD396  | U1\_VD\_ManualDose\_Remaining        | SINGLE  | 只读    | 手动注射泵剩余加药量        | —              |
| VB378  | U1\_VB378\_MB\_CTRL\_Error           | SINGLE  | 只读    | MBUS\_CTRL错误码     | v2.1新增         |
| VB379  | U1\_VB379\_MB\_MSG\_Error\_Task0     | SINGLE  | 只读    | MBUS\_MSG任务0错误    | v2.1新增         |
| VB380  | U1\_VB380\_MB\_MSG\_Error\_Task2     | SINGLE  | 只读    | MBUS\_MSG任务2错误    | v2.1新增         |
| VB381  | U1\_VB381\_MB\_MSG\_Error\_Task1     | SINGLE  | 只读    | MBUS\_MSG任务1错误    | v2.1新增         |
| VB382  | U1\_VB382\_MB\_MSG\_Error\_Task3     | SINGLE  | 只读    | MBUS\_MSG任务3错误    | v2.1新增         |
| VB383  | U1\_VB383\_MB\_MSG\_Error\_Task4     | SINGLE  | 只读    | MBUS\_MSG任务4错误    | v2.1新增         |
| VW294  | U1\_VW294\_PumpContFail              | SINGLE  | 只读    | 注射泵连续失败计数         | —              |
| VW296  | U1\_VW296\_FlowContFail              | SINGLE  | 只读    | 流量计连续失败计数         | —              |
| VB900  | U1\_VB900\_RTC\_Year                 | SINGLE  | 读写    | RTC年(BCD)         | v2.1新增         |
| VB901  | U1\_VB901\_RTC\_Month                | SINGLE  | 读写    | RTC月(BCD)         | v2.1新增         |
| VB902  | U1\_VB902\_RTC\_Day                  | SINGLE  | 读写    | RTC日(BCD)         | v2.1新增         |
| VB903  | U1\_VB903\_RTC\_Hour                 | SINGLE  | 读写    | RTC时(BCD)         | v2.1新增         |
| VB904  | U1\_VB904\_RTC\_Minute               | SINGLE  | 读写    | RTC分(BCD)         | v2.1新增         |
| VB905  | U1\_VB905\_RTC\_Second               | SINGLE  | 读写    | RTC秒(BCD)         | v2.1新增         |
| VB906  | U1\_VB906\_RTC\_Weekday              | SINGLE  | 只读    | RTC星期             | v2.1新增         |
| VB907  | U1\_VB907\_RTC\_Reserved             | SINGLE  | 读写    | RTC保留             | v2.1新增         |
| VB456  | U1\_UD\_Flag                         | SINGLE  | 读写    | HMI参数镜像标志字节       | —              |
| VD460  | U1\_UD\_VD24\_ExpTarget              | SINGLE  | 读写    | HMI镜像 VD24        | —              |
| VD464  | U1\_UD\_VD28\_PreMixTime             | SINGLE  | 读写    | HMI镜像 VD28        | —              |
| VD488  | U1\_UD\_VD66\_DelayA                 | SINGLE  | 读写    | HMI镜像 VD66        | —              |
| VD500  | U1\_UD\_VD316\_InletVol              | SINGLE  | 读写    | HMI镜像 VD316       | —              |
| VD504  | U1\_UD\_VD350\_StepRes               | SINGLE  | 读写    | HMI镜像 VD350       | —              |
| VD512  | U1\_UD\_VD358\_TimeoutA              | SINGLE  | 读写    | HMI镜像 VD358       | —              |
| VD516  | U1\_UD\_VD362\_TimeoutB              | SINGLE  | 读写    | HMI镜像 VD362       | —              |
| VD528  | U1\_UD\_VD452\_ManualDose            | SINGLE  | 读写    | HMI镜像 VD452       | —              |

***

## 十六、待确认事项

1. **McgsPro导入CSV**：当前最新CSV为`McgsPro变量导入_单元1_v2.2d.csv`（151通道），已删除VD74/VD78/VD108/VD492等废弃变量，新增I0.3/I0.4、Q区、VW304/VW306、VD244/VD256/VD414/VD426/VD430、V0.1/V1.1/V1.2等通道。关闭McgsPro后用v2.2d重新导入。
2. **HMI画面绑定更新**：

   - 单元详情/趋势曲线中原绑定到VD74（S4\_Actual）的元素改为VD116（S6\_Rolling）。

   - 原绑定到V304.0/1/2（InitDone/PumpOnline/FlowOnline）的元素改为V1.1/V1.2/V0.1。

   - 参数设置画面中删除VD58/VD62泵超时保护输入框；删除VD108首轮S6默认时长输入框；删除VD10/VD14浓度参数、VD354换水周期、VD30静止等候、VD448 S4等待超时等已废弃参数输入框。

   - 参数设置画面中VD28标签从"预循环时长"改为"S2搅拌时长"。

