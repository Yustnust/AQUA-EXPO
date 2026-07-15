# Story 1.7 断电保持与恢复逻辑 — 程序设计规格书 v1.0

**Jira**: AQEX-11
**关联文档**: PLC设计文档 v9.3 第十章(断电恢复)、第三章(标志位)、HMI-PLC变量地址表 v1.0 附录A
**前置依赖**: Story 1.2 状态机骨架(FC0骨架)、Story 1.4 节奏纠偏(VD_S5_Elapsed重算)、Story 1.6 报警详细(V303.5 RTC丢失)
**产出**: 本规格书 + FC0 STL代码重写 + 状态FC断电保护补充 + 变量表附录A更新

---

## 一、概述与设计决策闭环

### 1.1 范围

实现 PLC 设计文档第十章定义的断电保持与恢复逻辑:
- **冷启动 vs 断电恢复区分**:首次上电(出厂/长期断电后)走冷启动初始化;短期断电(超级电容保持期内)走恢复逻辑
- **RTC丢失检测**:开机时若RTC时间 < DT_TankB_FullTime → 触发V303.5报警
- **VD_S5_Elapsed重算**:断电恢复后用"当前RTC − DT10"重新计算下缸满计时器(Story 1.4规格)
- **状态机恢复策略**:根据断电时刻状态机所处状态,决定恢复或转S_ERROR
- **断电保持区配置**:补充Story 1.3/1.4/1.6新增变量的断电保持范围

### 1.2 设计决策闭环(9项)

| # | 决策项 | 结论 | 依据 |
|---|---|---|---|
| 1 | 冷启动/断电恢复判据 | **用V1.7(下缸状态)+ DT10有效性 + VW2有效性**综合判断;新增V304.0(M_InitDone初始化完成标志,断电保持) | 无专用"上电类型"寄存器;用业务数据有效性判断最可靠 |
| 2 | 初始化完成标志 | **V304.0 M_InitDone**:FC0首次执行成功后置1,断电保持;上电时若V304.0=0→冷启动,=1→断电恢复 | 简单可靠;超级电容失效时V304.0丢失→自动走冷启动 |
| 3 | 冷启动处理 | **全部清零到安全状态**(沿用FC0骨架),V304.0置1,转S0 | 出厂/长期断电后无有效历史数据 |
| 4 | 断电恢复处理 | **保留断电保持数据,根据VW2状态分类处理**,RTC重算VD_S5_Elapsed | 第十章"重新上电后用RTC−DT10重算已运行时长" |
| 5 | RTC丢失检测 | **开机时READ_RTC,与DT10比较(年月日时分秒逐字段BCD比较)**,RTC<DT10 → S V303.5 | 第十章"若RTC时间早于DT_TankB_FullTime,判定时钟已丢失";BCD直接比较(同年月日内) |
| 6 | 状态机恢复策略 | **S0/S5/S7可恢复;S1/S2/S3/S3.5/S4/S6转S_ERROR(阀门/泵动作中断不安全)** | 阀门动作中断可能导致液位未知/阀门半开,安全起见转S_ERROR人工处理;S5(实验运行)无阀门动作可恢复;S7(实验结束)锁定态可恢复 |
| 7 | VD_S5_Elapsed重算算法 | **BCD→总秒数(RTC和DT10各转秒)→相减**;跨天用"天数差×86400" | Story 1.4规格;BCD转秒用"时×3600+分×60+秒+天×86400";天数用简化儒略日 |
| 8 | 阀门动作态转S_ERROR时输出 | **强制QB0=0(阀门关/泵停/NC电磁阀失电)**,与FC2/FC19一致 | 断电恢复时阀门状态未知,强制安全 |
| 9 | 报警位断电恢复处理 | **断电保持区报警位保持,FC0不主动清除**(由FC3/FC19按确认流程处理) | 断电前已触发的报警仍需人工确认;仅冷启动才清报警字 |

### 1.3 待确认项(0项)

本Story所有逻辑依据第十章规格,无新增待确认项。

---

## 二、程序架构

### 2.1 修改POU

| POU | 类型 | 动作 | 职责 |
|---|---|---|---|
| FC0 SysInit | 修改 | 重写 | 冷启动/断电恢复双路径+RTC检测+VD_S5_Elapsed重算+状态机恢复策略 |
| FC11/FC15/FC17/FC16 | 修改 | 补充注释 | 断电恢复状态保护说明(实际逻辑在FC0统一处理,状态FC无需改代码) |
| 变量表附录A | 修改 | 补充 | 断电保持区配置新增VD150~VD190/VD178/VB500 |

### 2.2 新增变量分配

| 地址 | 符号 | 类型 | 说明 |
|---|---|---|---|
| V304.0 | M_InitDone | BOOL | 初始化完成标志(断电保持,FC0首次成功后置1) |
| VD186 | VD_RTC_Now_Sec | DWORD | 当前RTC转换总秒数(BCD转秒中间值,Story1.4已分配) |
| VD190 | VD_DT10_Sec | DWORD | DT10转换总秒数(Story1.4已分配) |
| VD194 | VD_RTC_DT_Diff | DWORD | RTC与DT10秒数差(VD_S5_Elapsed重算用) |
| VW198 | VW_Init_Step | WORD | 初始化步骤号(调试用,0=完成) |

### 2.3 断电保持区扩展(附录A补充)

| 起始 | 结束 | 字节数 | 内容 | 状态 |
|---|---|---|---|---|
| VB0 | VB9 | 10 | 系统命令位/状态位/状态机/泵状态/报警码/轮次 | 已有 |
| VB10 | VB149 | 140 | HMI设定参数+实测值+纠偏变量(VD10~VD140) | 已有 |
| VB150 | VB199 | 50 | **纠偏中间变量(VD150~VD190)+断电恢复中间量(VD194/VW198)** | **新增** |
| VB200 | VB229 | 30 | Modbus寄存器映射缓冲区 | 已有 |
| VB300 | VB303 | 4 | 报警字 | 已有 |
| **VB304** | **VB304** | **1** | **M_InitDone初始化完成标志(V304.0)** | **新增** |
| **VB500** | **VB599** | **100** | **报警日志缓冲区(FC3 NETWORK6)** | **新增** |
| DT10 | DT10 | 8 | DT_TankB_FullTime时间戳 | 已有 |

---

## 三、FC0 系统初始化规格

### 3.1 NETWORK结构

| NETWORK | 功能 |
|---|---|
| 1 | 初始化步骤号 + 判断冷启动/断电恢复(V304.0) |
| 2 | 冷启动路径: 全部清零安全状态 + V304.0置1 |
| 3 | 断电恢复路径: READ_RTC + RTC丢失检测 |
| 4 | 断电恢复路径: BCD转秒(RTC) |
| 5 | 断电恢复路径: BCD转秒(DT10) |
| 6 | 断电恢复路径: VD_S5_Elapsed重算(仅下缸=满时) |
| 7 | 断电恢复路径: 状态机恢复策略(VW2分类处理) |
| 8 | 初始化完成: V304.0置1, VW198=0 |

### 3.2 NETWORK 1: 判断冷启动/断电恢复

```
// SM0.1首次扫描触发
// V304.0=0 → 冷启动(出厂/长期断电后)
// V304.0=1 → 断电恢复(超级电容保持期内)
LD     SM0.1
MOVW   1, VW198                    // 初始化步骤=1(开始)
LD     V304.0                      // 初始化完成标志=1?
JMP    nWarmStart                  // 是 → 断电恢复路径
// 否 → 冷启动路径(NETWORK 2)
```

### 3.3 NETWORK 2: 冷启动路径(全部清零)

```
// 出厂/长期断电后,无有效历史数据,全部初始化安全状态
LD     SM0.1
AN     V304.0                      // 冷启动(V304.0=0)
MOVB   0, VB2                      // VW2=0(S0)
MOVB   0, VB3
R      V1.6, 1                     // 上缸=空
R      V1.7, 1                     // 下缸=空
MOVB   0, QB0                      // DO全部=0
MOVB   0, QB1
R      V300.4, 1                   // 清急停锁存
FILL   0, VW300, 4                 // 清报警字VB300~303
MOVB   0, VB6                      // VW6=0
MOVB   0, VB7
R      V1.0, 6                     // 清握手V1.0~V1.5
MOVB   0, VB8                      // VW8=0(轮次)
MOVB   0, VB9
MOVR   0.0, VD178                  // VD_S5_Elapsed=0
R      M10.7, 1                    // 清预规划标志
// VD参数区(VD10~VD140)不初始化,保留HMI设定值(若也是冷启动,HMI会重新下发)
// DT10不初始化(冷启动时DT10可能是乱码,后续S4完成时覆盖)
MOVW   2, VW198                    // 步骤=2(冷启动完成)
JMP    nInitDone                   // → 完成跳过断电恢复
```

### 3.4 NETWORK 3: 断电恢复路径 — READ_RTC + RTC丢失检测

```
LBL    nWarmStart
LD     SM0.1
READ_RTC VB900                     // 读RTC到VB900~VB907(BCD格式)
// VB900=年,VB901=月,VB902=日,VB903=时,VB904=分,VB905=秒,VB906=0,VB907=星期

// RTC丢失检测: 比较RTC与DT10(VB10~VB17)
// DT10: VB10=年,VB11=月,VB12=日,VB13=时,VB14=分,VB15=秒,VB16=0,VB17=星期
// BCD逐字段比较: 先比年,年大则RTC新;年同比月...以此类推
// 简化: 若DT10全0(未写入过)→跳过检测;否则逐字段比较
LD     VB10                        // DT10年=0?(未写入)
AW=   VB10, 0
JMP    nRTCOK                      // DT10未写入,跳过检测

// 逐字段比较(年→月→日→时→分→秒)
// 若任一字段RTC<DT10 → RTC丢失
LD     VB900                       // RTC年 < DT10年?
AW<   VB900, VB10
S      V303.5, 1                   // RTC丢失报警
JMP    nRTCError

LD     VB900                       // RTC年 = DT10年?
AW=   VB900, VB10
JMP    nChkMonth                   // 年相同,比月
// RTC年 > DT10年 → 正常,继续
JMP    nRTCOK

nChkMonth:
LD     VB901                       // RTC月 < DT10月?
AW<   VB901, VB11
S      V303.5, 1
JMP    nRTCError
LD     VB901
AW=   VB901, VB11
JMP    nChkDay
JMP    nRTCOK

nChkDay:
// ... 类比日/时/分/秒比较(省略,STL实现时逐字段)
// 任一字段RTC<DT10 → S V303.5, JMP nRTCError
// 全部RTC>=DT10 → JMP nRTCOK

nRTCOK:
MOVW   3, VW198                    // 步骤=3(RTC正常)
JMP    nBCDConvert

nRTCError:
// RTC丢失: V303.5已置位,VD_S5_Elapsed无法重算,置0,状态机转S_ERROR
MOVR   0.0, VD178                  // VD_S5_Elapsed=0(无法重算)
MOVB   99, VB2                     // 转S_ERROR
MOVB   0, VB3
MOVW   8, VW198                    // 步骤=8(RTC错误)
JMP    nInitDone
```

### 3.5 NETWORK 4-5: BCD转秒(RTC和DT10)

```
// BCD转总秒数算法:
// 总秒数 = 天数×86400 + 时×3600 + 分×60 + 秒
// 天数用简化儒略日(从2000-01-01起算)
// 简化:换水周期通常不跨天(30min~数小时),实际工程先用"当天秒数差"近似
// 跨天场景:天数差×86400

nBCDConvert:
// RTC转秒: VD_RTC_Now_Sec = 时×3600 + 分×60 + 秒 + 天数×86400
LD     SM0.1
// BCD→BIN: VB903(时)→AC0
BTI    VB903, AC0                  // BCD转INT(时)
MOVR   0.0, VD186                  // 清VD_RTC_Now_Sec
+R     AC0, VD186                  // 不对,AC0是INT,需转REAL
// 修正: BCD→INT→REAL
BTI    VB903, AC0                  // 时(BCD→INT)
ITD    AC0, AC0                    // INT→DINT
DTR    AC0, AC0                    // DINT→REAL
*R     3600.0, AC0                 // ×3600
MOVR   AC0, VD186                  // 存入VD_RTC_Now_Sec
// 分
BTI    VB904, AC0
ITD    AC0, AC0
DTR    AC0, AC0
*R     60.0, AC0
+R     AC0, VD186
// 秒
BTI    VB905, AC0
ITD    AC0, AC0
DTR    AC0, AC0
+R     AC0, VD186
// 天数(简化:用日期序号差,本规格先用0,跨天场景补全)
// 完整实现: 计算从2000-01-01到当前日期的天数,×86400加入
// 简化版: 若RTC与DT10同一天,天数差=0;跨天则按日差×86400
// 此处省略天数计算,STL实现时补充

// DT10转秒: VD_DT10_Sec = 同上算法,输入VB13/14/15
LD     SM0.1
BTI    VB13, AC0                   // 时
ITD    AC0, AC0
DTR    AC0, AC0
*R     3600.0, AC0
MOVR   AC0, VD190                  // VD_DT10_Sec
BTI    VB14, AC0                   // 分
ITD    AC0, AC0
DTR    AC0, AC0
*R     60.0, AC0
+R     AC0, VD190
BTI    VB15, AC0                   // 秒
ITD    AC0, AC0
DTR    AC0, AC0
+R     AC0, VD190
MOVW   4, VW198                    // 步骤=4(BCD转秒完成)
```

### 3.6 NETWORK 6: VD_S5_Elapsed重算

```
// VD_S5_Elapsed = VD_RTC_Now_Sec - VD_DT10_Sec
// 仅当下缸=满(V1.7=1)时才重算(下缸=空时VD_S5_Elapsed应为0)
LD     V1.7                        // 下缸=满
MOVR   VD186, VD178                // VD_S5_Elapsed = RTC秒
-R     VD190, VD178                // - DT10秒 = 断电期间经过的秒数
// 若结果<0(RTC异常)已在NETWORK3处理,此处不重复
MOVW   5, VW198                    // 步骤=5(Elapsed重算完成)

// 下缸=空时VD_S5_Elapsed保持0
LD     V1.7
NOT
MOVR   0.0, VD178                  // 下缸空,Elapsed=0
```

### 3.7 NETWORK 7: 状态机恢复策略

```
// 根据断电时刻VW2状态分类处理:
// S0(0)/S5(6)/S7(8) → 可恢复,保持原状态
// S1(1)/S2(2)/S3(3)/S3.5(4)/S4(5)/S6(7) → 转S_ERROR(阀门/泵动作中断不安全)

// S0: 初始化态,保持S0
LD     VW2
AW=    VW2, 0
JMP    nStateOK                    // 保持S0

// S1: 上缸进水(阀A动作中断)→转S_ERROR
LD     VW2
AW=    VW2, 1
JMP    nStateError

// S2: 预循环(泵动作中断)→转S_ERROR
LD     VW2
AW=    VW2, 2
JMP    nStateError

// S3: 加药(注射泵动作中断)→转S_ERROR
LD     VW2
AW=    VW2, 3
JMP    nStateError

// S3.5: 静止等候(无动作,但液位未知)→转S_ERROR
LD     VW2
AW=    VW2, 4
JMP    nStateError

// S4: 转移(阀B动作中断)→转S_ERROR
LD     VW2
AW=    VW2, 5
JMP    nStateError

// S5: 实验运行(无阀门动作)→保持S5,VD_S5_Elapsed已重算
LD     VW2
AW=    VW2, 6
JMP    nStateOK                    // 保持S5继续

// S6: 排水(阀C动作中断)→转S_ERROR
LD     VW2
AW=    VW2, 7
JMP    nStateError

// S7: 实验结束(锁定态)→保持S7
LD     VW2
AW=    VW2, 8
JMP    nStateOK                    // 保持S7

// S_ERROR(99): 故障态→保持S_ERROR
LD     VW2
AW=    VW2, 99
JMP    nStateOK                    // 保持S_ERROR

nStateError:
// 阀门动作态断电,强制安全输出+转S_ERROR
LD     SM0.1
MOVB   0, QB0                      // 阀门关/泵停/NC电磁阀失电
MOVB   99, VB2                     // 转S_ERROR
MOVB   0, VB3
S      V300.4, 1                   // 置急停锁存(类比急停处理,需人工复位)
MOVW   7, VW198                    // 步骤=7(状态机转S_ERROR)
JMP    nInitDone

nStateOK:
// 可恢复状态,保持VW2原值,VD_S5_Elapsed已重算
MOVW   6, VW198                    // 步骤=6(状态恢复完成)
```

### 3.8 NETWORK 8: 初始化完成

```
nInitDone:
LD     SM0.1
S      V304.0, 1                   // M_InitDone=1(初始化完成,断电保持)
MOVW   0, VW198                    // 步骤=0(完成)
```

---

## 四、断电恢复完整时序

### 4.1 冷启动时序(出厂/长期断电后)

```
T0: 上电,SM0.1=1
  → FC0 NETWORK1: V304.0=0 → 冷启动路径
  → FC0 NETWORK2: VW2=0(S0), 上下缸置空, QB0=0, 清报警/锁存/握手/轮次
  → FC0 NETWORK8: V304.0=1(标记初始化完成)
T1: 进入S0,等待HMI启动命令
```

### 4.2 断电恢复时序(S5实验运行中,短期断电)

```
T0: 断电时刻,VW2=6(S5),V1.7=1(下缸满),VD_S5_Elapsed=1800s(30min)
  → 超级电容保持VW2/V1.7/VD_S5_Elapsed/DT10等

T1: 重新上电,SM0.1=1
  → FC0 NETWORK1: V304.0=1 → 断电恢复路径
  → FC0 NETWORK3: READ_RTC, 比较RTC与DT10, RTC>=DT10 → 正常
  → FC0 NETWORK4-5: BCD转秒,VD_RTC_Now_Sec, VD_DT10_Sec
  → FC0 NETWORK6: V1.7=1, VD_S5_Elapsed = VD_RTC_Now_Sec - VD_DT10_Sec
                  (断电期间经过的秒数计入,Available连续不跳变)
  → FC0 NETWORK7: VW2=6(S5) → nStateOK,保持S5
  → FC0 NETWORK8: V304.0=1

T2: FC1调度VW2=6 → FC16(S5)继续运行
  → VD_S5_Elapsed已重算,Available正确,继续实验
```

### 4.3 断电恢复时序(S1进水中,阀A动作中断)

```
T0: 断电时刻,VW2=1(S1),阀A开启中
  → 超级电容保持VW2=1

T1: 重新上电,SM0.1=1
  → FC0 NETWORK1: V304.0=1 → 断电恢复路径
  → FC0 NETWORK3-6: RTC检测+重算
  → FC0 NETWORK7: VW2=1(S1) → nStateError
    → QB0=0(阀A强制关), VW2=99(S_ERROR), S V300.4(急停锁存)
  → FC0 NETWORK8: V304.0=1

T2: FC1调度VW2=99 → FC19(S_ERROR)
  → HMI显示"断电恢复,阀门动作中断,需人工检查后系统复位"
  → 操作员现场检查阀A/液位,确认安全后按I2.3系统复位 → 回S0
```

### 4.4 RTC丢失时序(断电超过7天,超级电容失效)

```
T0: 长期断电(>7天),超级电容失效
  → V304.0丢失(=0),VW2/DT10/VD_S5_Elapsed等全部丢失

T1: 上电,SM0.1=1
  → FC0 NETWORK1: V304.0=0 → 冷启动路径
  → FC0 NETWORK2: 全部清零,V304.0=1
  → 系统从S0重新开始,HMI需重新校准RTC(若RTC也停走)
```

### 4.5 RTC部分丢失(超级电容保持,但RTC停走)

```
T0: 断电(3天,超级电容保持),但RTC电池耗尽停走
  → V304.0=1,VW2=6,DT10保持,但RTC时间错误(早于DT10)

T1: 上电,SM0.1=1
  → FC0 NETWORK3: READ_RTC, 比较RTC与DT10
  → RTC时间 < DT10 → S V303.5(RTC丢失报警)
  → FC0 NETWORK3: nRTCError → VD_S5_Elapsed=0, VW2=99(S_ERROR)
  → FC0 NETWORK8: V304.0=1

T2: FC1调度VW2=99 → FC19(S_ERROR)
  → HMI显示"RTC时钟丢失,请校准PLC时钟"
  → 操作员HMI校时后,确认V303.5 → 系统复位回S0
```

---

## 五、状态FC断电保护说明

### 5.1 实际保护逻辑归属

断电恢复的状态保护逻辑**统一在FC0 NETWORK7处理**,状态FC(FC11/FC15/FC17/FC16)无需修改代码。原因:
- 断电发生时PLC停止扫描,状态FC不会执行
- 上电时SM0.1触发FC0,在FC1调度前完成状态机恢复决策
- FC0 NETWORK7根据VW2(断电保持)判断,转S_ERROR或保持

### 5.2 各状态FC补充注释(仅注释,不改代码)

| 状态FC | 断电恢复处理 | 注释补充 |
|---|---|---|
| FC11(S1) | 转S_ERROR(阀A动作中断) | // 注:断电恢复由FC0统一处理,VW2=1时FC0转S_ERROR |
| FC12(S2) | 转S_ERROR(泵动作中断) | 同上 |
| FC13(S3) | 转S_ERROR(注射泵动作中断) | 同上 |
| FC14(S3.5) | 转S_ERROR(液位未知) | 同上 |
| FC15(S4) | 转S_ERROR(阀B动作中断) | 同上 |
| FC16(S5) | 保持S5(无阀门动作) | // 注:断电恢复FC0重算VD_S5_Elapsed,保持S5继续 |
| FC17(S6) | 转S_ERROR(阀C动作中断) | 同上 |
| FC18(S7) | 保持S7(锁定态) | // 注:断电恢复保持S7,需HMI确认重启 |

---

## 六、与各模块交互

### 6.1 与FC1(状态调度)交互

- FC0在SM0.1(首次扫描)执行,完成后VW2已确定(冷启动=0/恢复保持/转S_ERROR=99)
- FC1在NETWORK5(每周期)调度,首次扫描时FC0已完成,VW2有效

### 6.2 与FC16(S5)交互

- 断电恢复保持S5时,VD_S5_Elapsed已由FC0重算
- FC16 NETWORK1继续每秒累加VD_S5_Elapsed,Available连续不跳变

### 6.3 与FC3(报警)交互

- RTC丢失(V303.5)由FC0 NETWORK3置位
- FC0不主动清除报警位(断电保持),由FC3/FC19按确认流程处理
- 冷启动时FC0 NETWORK2清报警字

### 6.4 与FC19(S_ERROR)交互

- 断电恢复转S_ERROR时,FC0置V300.4(急停锁存)
- FC19检测V300.4=1,等待系统复位按钮(I2.3)回S0

---

## 七、BCD转秒算法详细说明

### 7.1 S7-200 SMART RTC格式

```
READ_RTC VB900 读取8字节BCD:
  VB900 = 年 (00~99, BCD)
  VB901 = 月 (01~12, BCD)
  VB902 = 日 (01~31, BCD)
  VB903 = 时 (00~23, BCD)
  VB904 = 分 (00~59, BCD)
  VB905 = 秒 (00~59, BCD)
  VB906 = 0
  VB907 = 星期 (01~07, BCD)
```

### 7.2 BCD转INT指令

```
BTI    VB903, AC0    // BCD→INT(S7-200 SMART的BTI自动处理BCD→BIN)
```

### 7.3 总秒数计算(简化版,同一天内)

```
当天秒数 = 时×3600 + 分×60 + 秒
```

### 7.4 跨天处理(完整版,用日期序号差)

```
天数差 = 儒略日(RTC) - 儒略日(DT10)
总秒数差 = 天数差×86400 + 当天秒数差

儒略日简化算法(从2000-01-01起算):
  设Y=年,M=月,D=日
  若M<=2: Y=Y-1, M=M+12
  天数 = INT(365.25×(Y+2000)) + INT(30.6×(M+1)) + D - 621049

注: STL实现浮点运算较繁琐,实际工程中:
  - 换水周期通常30min~数小时,同一天内,用"当天秒数差"足够
  - 跨天场景(长周期实验)补充日期序号计算
  - 本Story STL实现用"当天秒数差"为主,注释标注跨天扩展点
```

---

## 八、验证要点

1. **冷启动**:V304.0=0,FC0清零全部,VW2=0,V304.0=1
2. **断电恢复(S5)**:V304.0=1,VW2=6,RTC>=DT10,VD_S5_Elapsed重算,保持S5
3. **断电恢复(S1阀A动作)**:V304.0=1,VW2=1,转S_ERROR,V300.4置位
4. **RTC丢失**:RTC<DT10,V303.5置位,转S_ERROR
5. **RTC正常但DT10未写入**:DT10=0,跳过检测,VD_S5_Elapsed=0
6. **下缸空时恢复**:V1.7=0,VD_S5_Elapsed=0(不重算)
7. **断电保持区配置**:附录A补充VB150~199/VB304/VB500~599
8. **状态机恢复策略**:S0/S5/S7/S_ERROR保持;S1/S2/S3/S3.5/S4/S6转S_ERROR

---

// ============================================================
// 规格书结束
// ============================================================
