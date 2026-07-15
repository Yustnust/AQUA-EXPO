# Story 1.4 配液节奏三层纠偏机制 — 程序设计规格书 v1.0

**Jira**: AQEX-8
**关联文档**: PLC设计文档 v9.3 第七章(三层纠偏机制)、第四章(S5/S6流程)
**前置依赖**: Story 1.2 状态机骨架(FC16/FC11已预留接口)、Story 1.3 阀门诊断
**产出**: 本规格书 + FC40 STL代码 + FC16/FC11 集成更新

---

## 一、概述与设计决策闭环

### 1.1 范围

实现 PLC 设计文档第七章定义的"配液节奏滞后三层自动纠偏机制",包含:
- **预规划**(7.2):S5 阶段调度条件达成的上升沿触发,一次性规划本轮 S2/S3.5 目标时长
- **二次校正**(7.3):S1 完成后用实测值 S1_actual 重新核定 S2/S3.5 目标
- **人工介入报警**(7.4):三层额度用尽仍无法覆盖缺口时触发

### 1.2 设计决策闭环(8项)

| # | 决策项 | 结论 | 依据 |
|---|---|---|---|
| 1 | FC编号 | **FC40 RhythmCorrection**(纯纠偏算法);FC16负责时间采集,FC11负责二次校正调用 | FC30/31/32已被阀门诊断占用;FC40与FC11预留注释`CALL FC40:PreMixCorrection`一致 |
| 2 | 预规划/二次校正是否合用一个FC | **合用**,用模式字VW178区分(0=预规划,1=二次校正) | 7.2与7.3是同一套三层算法,仅Available/Needed取值时机不同,合用避免重复代码 |
| 3 | 时间机制实现 | **下缸满计时器VD_S5_Elapsed(秒累加)+断电恢复RTC重算**,非每周期DT转换 | S7-200 SMART的DT(BCD)→秒转换繁琐,运行时用秒累加器最简;断电后用RTC一次性重算 |
| 4 | Available计算公式 | `VD_Available = VD_CycleSetpoint×60 + VD_S6_Rolling − VD_S5_Elapsed`(秒) | 下缸预计排空时刻=DT_TankB_FullTime+CycleSetpoint+S6_Rolling;当前时间-DT_TankB_FullTime=VD_S5_Elapsed |
| 5 | 预规划触发判据 | `VD_Available ≤ VD_T_Rolling` 的**上升沿**(由不满足→满足,只触发一次) | 设计文档7.2明确要求上升沿触发,非逐扫描周期重复 |
| 6 | 转S6判据 | `VD_S5_Elapsed ≥ VD_CycleSetpoint×60`(换水周期到) | 下缸已满时长达到换水周期设定值,该排空了;与预规划触发是两个独立事件 |
| 7 | 第2层额度单位 | VD_CycleExtend_Max(min)在FC40内部**×60转秒**参与运算,输出VD_CycleExtend_Target(min)**÷60写回** | 参数表VD44/VD128单位为min,算法内部统一用秒 |
| 8 | S3估算时长 | 新增**VD_S3_Estimate(秒)**,二次校正Needed'=VD_S2_Target+VD_S3_Estimate+VD_RestTime_Target;预规划Needed=VD_T_Rolling(内含S3标称) | 7.3明确Needed'含"S3计算值";预规划用VD_T_Rolling已含S3标称无需单列 |

### 1.3 待确认项(1项,不影响开发)

| # | 待确认项 | 处理 |
|---|---|---|
| 1 | VD_S3_Estimate的精确计算公式(N步×单步耗时)依赖注射泵速度参数VD_PumpSpeed_*的确认(变量表8.4标注"待确认") | 暂用固定估算值`VD_Dose_Steps × 单步耗时系数`,在FC13(S3)完成后写入;系数待注射泵选型确认后标定。二次校正功能不受影响,仅估算精度待提升 |

---

## 二、程序架构

### 2.1 新增/修改POU

| POU | 类型 | 动作 | 职责 |
|---|---|---|---|
| FC40 RhythmCorrection | 新增 | 编写 | 三层纠偏核心算法(纯数学,输入Available/Needed,输出Targets+报警) |
| FC16 State_S5_Run | 修改 | 集成 | 下缸满计时器、Available计算、预规划上升沿触发、S1启动、S6转移 |
| FC11 State_S1_Inlet | 修改 | 集成 | S1完成时填充预留的FC40二次校正调用 |

### 2.2 新增变量分配(VD150~VD199区,REAL浮点,断电保持)

| 地址 | 符号 | 单位 | 说明 |
|---|---|---|---|
| VD150 | VD_Available | s | 剩余可用时间(FC16计算,传给FC40) |
| VD154 | VD_Needed | s | 所需时间(调用方填入) |
| VD158 | VD_Delta | s | 缺口 Δ = Needed − Available(FC40内部) |
| VD162 | VD_Layer0_Quota | s | 第0层额度 = VD_RestTime − VD_RestTime_Min |
| VD166 | VD_Layer1_Quota | s | 第1层额度 = VD_PreMixTime − VD_PreMixTime_MinSafe |
| VD170 | VD_Layer2_Quota | s | 第2层额度 = VD_CycleExtend_Max × 60 |
| VD174 | VD_S3_Estimate | s | S3估算时长(二次校正Needed'用,FC13写入) |
| VD178 | VD_S5_Elapsed | s | 下缸变满后累计运行秒数(每秒+1,断电恢复RTC重算) |
| VW182 | VW_Corr_Mode | — | 纠偏模式(0=预规划,1=二次校正) |
| VW184 | VW_Corr_Result | — | 纠偏结果(0=进行中,1=正常无需纠偏,2=已纠偏,3=滞后提示,4=人工介入) |
| VD186 | VD_RTC_Now_Sec | s | 当前RTC转换总秒数(断电恢复用) |
| VD190 | VD_DT10_Sec | s | DT_TankB_FullTime转换总秒数(断电恢复用) |

### 2.3 已用变量回顾(不重新分配)

| 地址 | 符号 | 单位 | 来源 |
|---|---|---|---|
| VD20 | VD_CycleSetpoint | min | 参数表6.2 |
| VD28 | VD_PreMixTime | s | 参数表6.2 |
| VD32 | VD_PreMixTime_MinSafe | s | 参数表6.2 |
| VD36 | VD_RestTime | s | 参数表6.2 |
| VD40 | VD_RestTime_Min | s | 参数表6.2 |
| VD44 | VD_CycleExtend_Max | min | 参数表6.2 |
| VD70 | VD_S1_Actual | s | 实测7.1 |
| VD104 | VD_T_Default | s | 纠偏8.1 |
| VD112 | VD_T_Rolling | s | 纠偏8.2 |
| VD116 | VD_S6_Rolling | s | 纠偏8.2 |
| VD120 | VD_S2_Target | s | 纠偏8.3(FC40输出) |
| VD124 | VD_RestTime_Target | s | 纠偏8.3(FC40输出) |
| VD128 | VD_CycleExtend_Target | min | 纠偏8.3(FC40输出) |
| V300.6 | M_Alarm_ScheduleLag | — | 报警字(严重滞后,强制人工确认) |
| V300.7 | M_Alarm_ScheduleLag_Warn | — | 报警字(滞后提示,一般级) |
| M10.5 | S5首次进入标志 | — | FC16已有(Story1.2) |
| M10.7 | 预规划已触发标志 | — | 新增(上升沿锁存,本轮只触发一次) |

### 2.4 计时器分配

| 计时器 | 时基 | 用途 | 所属 |
|---|---|---|---|
| T60 | 100ms | 1秒基准(PT=10),每秒触发VD_S5_Elapsed累加 | FC16 |
| T41 | 100ms | (保留)换水周期粗计时,Story1.2已有,本Story改为由VD_S5_Elapsed替代判据 | FC16 |

---

## 三、时间机制规格(FC16内)

### 3.1 下缸满计时器 VD_S5_Elapsed

```
含义: 下缸变满时刻(S4完成写DT10)至今累计运行的秒数
累加: T60(PT=10,100ms时基)每完成一次 → VD_S5_Elapsed + 1.0
清零: S4完成(下缸变满)时刻清零,开始新一轮计数
断电保持: VD178在断电保持区,超级电容保持
```

### 3.2 Available 计算(每扫描周期)

```
VD_Available(VD150) = VD_CycleSetpoint(VD20) × 60.0 + VD_S6_Rolling(VD116) − VD_S5_Elapsed(VD178)

说明:
  - VD_CycleSetpoint×60: 换水周期(min→s)
  - VD_S6_Rolling: 预留的排水时长(排空需提前算入)
  - VD_S5_Elapsed: 下缸已满时长
  - Available > 0: 距排空还有Available秒
  - Available ≤ 0: 已到/过了排空时刻
```

### 3.3 断电恢复重算(FC0_SysInit或FC16首次进入时)

```
上电后若V1.7(下缸=满)且VD_S5_Elapsed可能不准(断电期间未累加):
  1. READ_RTC → VB900~VB907 (BCD格式)
  2. BCD→秒转换: VD_RTC_Now_Sec = RTC总秒数(从2000-01-01基准)
  3. DT10(VB10~VB17) BCD→秒转换: VD_DT10_Sec
  4. VD_S5_Elapsed = VD_RTC_Now_Sec − VD_DT10_Sec
  5. 若VD_RTC_Now_Sec < VD_DT10_Sec → RTC异常,触发M_Alarm_RTC_Lost(V303.5)

BCD→总秒数转换(简化,按天内秒数+天数):
  当天秒数 = 时×3600 + 分×60 + 秒
  天数 = 日期序号差 × 86400
  (日期序号用简易儒略日算法,考虑闰年)
```

> **实现说明**: BCD→秒转换逻辑较繁琐,在STL中用一个独立NETWORK实现。考虑到换水周期通常不跨天(30min~数小时),实际工程中可先用"当天秒数差"近似,跨天场景再补全日期序号。本规格书给出完整算法,STL实现时日期序号部分用循环减法近似。

---

## 四、FC40 三层纠偏核心算法规格

### 4.1 接口

```
输入:
  VW182 (VW_Corr_Mode)   : 0=预规划, 1=二次校正
  VD150 (VD_Available)   : 剩余可用时间(s) — 调用方填入
  VD154 (VD_Needed)      : 所需时间(s) — 调用方填入
                           预规划: Needed = VD_T_Rolling
                           二次校正: Needed = VD_S2_Target + VD_S3_Estimate + VD_RestTime_Target

输出:
  VD120 (VD_S2_Target)         : 本轮S2目标时长(s)
  VD124 (VD_RestTime_Target)   : 本轮S3.5目标时长(s)
  VD128 (VD_CycleExtend_Target): 允许下缸空等时长(min)
  VW184 (VW_Corr_Result)       : 0进行中/1正常无需纠偏/2已纠偏/3滞后提示/4人工介入
  V300.6 (M_Alarm_ScheduleLag) : 严重滞后(人工介入)报警
  V300.7 (M_Alarm_ScheduleLag_Warn): 滞后提示报警

内部:
  VD158 (VD_Delta)       : 缺口 = Needed − Available
  VD162 (VD_Layer0_Quota): 第0层额度
  VD166 (VD_Layer1_Quota): 第1层额度
  VD170 (VD_Layer2_Quota): 第2层额度
```

### 4.2 算法流程(NETWORK结构)

```
NETWORK 1: 计算三层额度
  VD_Layer0_Quota = VD_RestTime − VD_RestTime_Min          (静止等候可压缩量)
  VD_Layer1_Quota = VD_PreMixTime − VD_PreMixTime_MinSafe  (S2可压缩量)
  VD_Layer2_Quota = VD_CycleExtend_Max × 60.0              (周期可顺延量,min→s)

NETWORK 2: 判断是否需要纠偏
  IF VD_Available ≥ VD_Needed:
    → 无需纠偏(正常情况)
    → VD_S2_Target = VD_PreMixTime
    → VD_RestTime_Target = VD_RestTime
    → VD_CycleExtend_Target = 0.0
    → VW_Corr_Result = 1 (正常)
    → 返回

NETWORK 3: 计算缺口并开始第0层扣减
  VD_Delta = VD_Needed − VD_Available
  IF VD_Delta ≤ VD_Layer0_Quota:
    → VD_RestTime_Target = VD_RestTime − VD_Delta
    → VD_S2_Target = VD_PreMixTime
    → VD_CycleExtend_Target = 0.0
    → VW_Corr_Result = 2 (已纠偏)
    → 返回
  ELSE:
    → VD_RestTime_Target = VD_RestTime_Min  (第0层用满)
    → VD_Delta = VD_Delta − VD_Layer0_Quota (继续第1层)

NETWORK 4: 第1层扣减
  IF VD_Delta ≤ VD_Layer1_Quota:
    → VD_S2_Target = VD_PreMixTime − VD_Delta
    → VD_CycleExtend_Target = 0.0
    → VW_Corr_Result = 2 (已纠偏)
    → 返回
  ELSE:
    → VD_S2_Target = VD_PreMixTime_MinSafe  (第1层用满)
    → VD_Delta = VD_Delta − VD_Layer1_Quota (继续第2层)

NETWORK 5: 第2层扣减(顺延周期)
  IF VD_Delta ≤ VD_Layer2_Quota:
    → VD_CycleExtend_Target = VD_Delta / 60.0  (s→min写回)
    → VW_Corr_Result = 3 (滞后提示)
    → S V300.7  (M_Alarm_ScheduleLag_Warn 置位,一般故障级)
    → 返回
  ELSE:
    → 三层额度全部用尽
    → VW_Corr_Result = 4 (人工介入)
    → S V300.6  (M_Alarm_ScheduleLag 置位,强制人工确认)
    → 转S_ERROR: MOVB 99,VB2

NETWORK 6: 二次校正模式特殊处理
  IF VW_Corr_Mode = 1 (二次校正):
    → 若7.2预规划已定过VD_CycleExtend_Target且本次只是微调,
      不重复触发V300.7滞后报警(除非缺口进一步扩大超出已定额度)
    → 实现方式: 二次校正进入第2层时,先比较VD_Delta与已定VD_CycleExtend_Target×60,
      仅当超出时才置位V300.7/V300.6
```

### 4.3 STL实现要点

- S7-200 SMART STL浮点比较指令:`AR>=`(≥)、`AR<=`(≤)、`AR>`(>)、`AR<`(<)
- 浮点运算:`+R`(加)、`-R`(减)、`*R`(乘)、`/R`(除)
- 分层扣减用顺序的`AR<=`比较 + 跳转实现(类似CASE)
- 报警置位用`S`指令(锁存),复位由FC3报警处理在人工确认后执行

---

## 五、FC16(S5)集成规格

### 5.1 NETWORK结构调整

原FC16(Story1.2骨架)的NETWORK结构调整为:

| NETWORK | 功能 | 改动 |
|---|---|---|
| 1 | 下缸满计时器VD_S5_Elapsed累加 | **新增** |
| 2 | Available计算 + 预规划上升沿触发 | **重写**(替代原NETWORK1的M10.5简化逻辑) |
| 3 | 实验时长累加 | 保留(沿用Story1.2) |
| 4 | 换水周期到达转S6 | **重写**(用VD_S5_Elapsed判据替代T41) |
| 5 | 实验时长达标转S7 | 保留 |
| 6 | HMI手动停止 | 保留 |

### 5.2 NETWORK 1: 下缸满计时器

```
LD     SM0.0
LPS
A      V1.7                        // 下缸=满才计时
R      T60, 1
TON    T60, 10                     // 1秒(10×100ms)
LPP
LD     T60                         // 1秒到
EU
+R     1.0, VD178                  // VD_S5_Elapsed + 1
R      T60, 1                      // 重置进入下一秒
```

### 5.3 NETWORK 2: Available计算 + 预规划触发

```
// 计算Available
LD     SM0.0
MOVR   VD20, VD150                 // VD_CycleSetpoint(min)
*R     60.0, VD150                 // →秒
+R     VD116, VD150                // + VD_S6_Rolling
-R     VD178, VD150                // − VD_S5_Elapsed = VD_Available

// 预规划上升沿触发: VD_Available ≤ VD_T_Rolling 且 本轮未触发过
LD     SM0.0
LPS
AR<=   VD150, VD112                // Available ≤ T_Rolling ?
AN     M10.7                       // 且本轮未触发过
S      M10.7, 1                    // 锁存:本轮已触发
// 填入FC40输入
MOVW   0, VW182                    // 模式=0(预规划)
MOVR   VD112, VD154                // Needed = VD_T_Rolling
CALL   FC40:V RhythmCorrection
// 检查纠偏结果
AW<>   VW184, 4                    // 非"人工介入"才启动S1
LPS
AN     V1.6                        // 上缸=空
MOVB   1, VB2                     // →S1启动新一轮
MOVB   0, VB3
LPP
LPP

// 预规划触发后,若上缸≠空(异常,上一轮没收尾)
LD     M10.7
A      V1.6                        // 上缸=满(异常)
S      V301.6, 1                   // 复用报警位(上缸未排空异常)
MOVB   99, VB2
```

### 5.4 NETWORK 4: 换水周期到达转S6

```
// VD_S5_Elapsed ≥ VD_CycleSetpoint×60 → 换水周期到,转S6排水
LD     SM0.0
LPS
MOVR   VD20, AC0                   // VD_CycleSetpoint(min)
*R     60.0, AC0                   // →秒
AR>=   VD178, AC0                  // 已满时长 ≥ 周期 ?
R      M10.7, 1                    // 清预规划触发标志(下轮重新触发)
R      T60, 1                      // 停下缸满计时器
MOVB   7, VB2                     // →S6排水
MOVB   0, VB3
LPP
```

### 5.5 S4完成时清零VD_S5_Elapsed(FC15补充)

FC15(S4转移)在阀B诊断正常完成、下缸变满时,需补充:
```
MOVR   0.0, VD178                  // VD_S5_Elapsed清零,开始新一轮计时
R      M10.7, 1                    // 清预规划触发标志
```
(此条在FC15集成时补充,本Story一并修改FC15)

---

## 六、FC11(S1)二次校正集成规格

### 6.1 填充预留接口

FC11 NETWORK 3 原预留注释:
```
// 【预留】二次校正接口 - S1完成后触发纠偏(Story 1.4)
// CALL FC40:PreMixCorrection
```

填充为:

```
// S1完成后二次校正(7.3)
LD     SM0.0
LPS
AW=    VW266, 1                    // 阀A诊断正常完成
// 重新计算Available(此刻已扣除S1实际耗时)
MOVR   VD20, VD150                 // VD_CycleSetpoint×60
*R     60.0, VD150
+R     VD116, VD150                // + VD_S6_Rolling
-R     VD178, VD150                // − VD_S5_Elapsed(含S1耗时) = Available'
// Needed' = VD_S2_Target + VD_S3_Estimate + VD_RestTime_Target
MOVR   VD120, VD154                // VD_S2_Target(7.2预规划已定)
+R     VD174, VD154                // + VD_S3_Estimate
+R     VD124, VD154                // + VD_RestTime_Target = Needed'
MOVW   1, VW182                    // 模式=1(二次校正)
CALL   FC40:V RhythmCorrection
// 二次校正后更新VD_T_Rolling(取标称值,7.5)
// VD_T_Rolling = VD_S1_Actual + VD_PreMixTime + VD_S3_Estimate + VD_RestTime
MOVR   VD70, VD112                 // S1实测
+R     VD28, VD112                 // + S2标称
+R     VD174, VD112                // + S3估算
+R     VD36, VD112                 // + S3.5标称 = 新VD_T_Rolling
LPP
```

### 6.2 二次校正与转S2的时序

二次校正必须在"转S2"之前完成。FC11 NETWORK 3 调整为:
1. 阀A诊断正常(VW266=1)
2. 记录S1实测时长(VD70)
3. **调用FC40二次校正**(填充接口)
4. 更新VD_T_Rolling
5. 转S2

---

## 七、T滚动更新与报警汇总

### 7.1 VD_T_Rolling 滚动更新(7.5原则)

```
更新时机: S1完成(二次校正后)
更新公式: VD_T_Rolling = VD_S1_Actual + VD_PreMixTime + VD_S3_Estimate + VD_RestTime
取值原则: 取标称值(PreMixTime/RestTime),不用纠偏压缩后的Target值
首轮处理: 无历史数据时VD_T_Rolling = VD_T_Default(FC0初始化)
```

### 7.2 VD_S6_Rolling 滚动更新(FC17 S6完成时,本Story不修改)

```
更新时机: S6排水完成(FC17已有)
更新公式: VD_S6_Rolling = VD_S6_Actual(单次实测直接用,或0.7×历史+0.3×本次平滑)
首轮处理: VD_S6_Rolling = VD_S6_Default
```

### 7.3 本Story新增/涉及报警

| 位 | 符号 | 触发条件 | 优先级 | 强制人工确认 | 处理 |
|---|---|---|---|---|---|
| V300.6 | M_Alarm_ScheduleLag | 三层纠偏额度用尽仍无法覆盖缺口(FC40 NETWORK 5) | 节奏滞后级 | 是 | 停止自动纠偏,转S_ERROR,等待人工处理 |
| V300.7 | M_Alarm_ScheduleLag_Warn | 第2层顺延周期触发(FC40 NETWORK 5) | 一般故障级 | 按模式 | 继续运行但提示滞后,HMI显示顺延量 |

### 7.4 报警复位

- V300.6(M_Alarm_ScheduleLag):强制人工确认,由FC3报警处理在HMI确认后复位,复位后状态机从S0重新开始
- V300.7(M_Alarm_ScheduleLag_Warn):按M_AlarmAckMode,自动模式下条件消失自动清除,人工模式下HMI确认后清除

---

## 八、与状态机交互机制

### 8.1 完整一轮节奏调度时序

```
S4完成(下缸变满)
  → 写DT10, 清VD_S5_Elapsed=0, 清M10.7
  → 转S5

S5运行中(下缸满,上缸空)
  → VD_S5_Elapsed每秒+1
  → 每周期算VD_Available
  → [事件A] VD_Available ≤ VD_T_Rolling 上升沿:
       → FC40预规划(模式0) → 定VD_S2_Target/VD_RestTime_Target/VD_CycleExtend_Target
       → 上缸=空 → 转S1(上缸配液与下缸实验并行)
       → 上缸=满 → 报警(异常)
  → [事件B] VD_S5_Elapsed ≥ VD_CycleSetpoint×60(换水周期到):
       → 转S6排水

S1运行中(上缸进水,与S5并行)
  → 阀A诊断正常完成
  → FC40二次校正(模式1) → 重核VD_S2_Target/VD_RestTime_Target
  → 更新VD_T_Rolling(标称值)
  → 转S2 → S3 → S3.5(按Target执行)

S6完成(下缸排空)
  → 若新一轮S1-S3.5已完成 → 转S4(转移新溶液)
  → 若未完成 → 下缸空等,不超过VD_CycleExtend_Target×60秒
       → 超时仍未就绪 → 已在FC40预规划阶段触发人工介入报警
```

### 8.2 并行性说明

S5(下缸实验)与S1-S3.5(上缸配液)是**并行**的:状态机VW2在同一时刻只有一个值,但工艺上"下缸还在做实验"的同时"上缸已在配下一轮药液"。

实现方式:状态机主线在S5时,通过[事件A]转S1开始上缸配液;S1→S2→S3→S3.5完成后,若S5仍在运行(下缸还没到换水周期),则在S3.5完成后转回S5等待(或停留在S3.5完成态),直到[事件B]换水周期到才转S6。

> **注**: 并行等待的细节(上缸配液完成后下缸还没到周期,状态如何停留)需在FC14(S3.5)完成后细化。本Story确保纠偏算法和预规划触发正确,并行停留逻辑在后续Story完善。

---

## 九、验证要点

1. **预规划触发**:VD_S5_Elapsed 增长使 VD_Available 降到 VD_T_Rolling 时,M10.7 置位且 FC40 被调用一次(非每周期重复)
2. **正常无纠偏**:Available ≥ Needed 时,Targets 等于标称值,VW_Corr_Result=1
3. **第0层纠偏**:缺口仅靠压缩静止等候即可覆盖,VD_RestTime_Target减小,VD_S2_Target不变
4. **三层用尽**:V300.6置位,转S_ERROR(VW2=99)
5. **二次校正**:S1完成后Available'重新计算,FC40模式1调用,VD_T_Rolling更新
6. **断电恢复**:VD_S5_Elapsed由RTC重算,Available连续不跳变

---

// ============================================================
// 规格书结束
// ============================================================
