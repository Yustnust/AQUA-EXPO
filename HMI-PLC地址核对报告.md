# AQUA-EXPO 项目 HMI-PLC 地址核对报告

**生成日期**：2026-07-29
**核对范围**：`d:\work\CTI\plc\stl` 下全部 21 个 STL 源文件
**接口基准**：
- `d:\work\CTI\docs\HMI-PLC变量地址表_v1.0.md`
- `d:\work\CTI\docs\hmi_preparation\McgsPro变量导入_8单元_v2.0.csv`（**已废弃**，最新拆分为 `McgsPro变量导入_单元1.csv` ~ `单元8.csv`）

> **重要说明**：本报告生成后，McgsPro CSV 已拆分为 8 个单元独立文件，且因 McgsPro 西门子_Smart200 驱动对 8 位无符号导入支持不完整，报警字已由 `VB300~VB303` 四个字节通道改为 `VW300/VW302` 两个 16 位字通道。报告中的 `U1_VB300_AlarmByte0` ~ `U1_VB303_AlarmByte3` 等旧变量名已不存在，请以最新 HMI-PLC 变量地址表和 CSV 为准。

## 一、核对概览

| 项目 | 数量 | 说明 |
|---|---|---|
| PLC实际使用地址记录 | 1271 | 含重复出现 |
| PLC实际使用唯一地址 | 243 | 去重后 |
| 文档/CSV定义地址 | 175 | MD+CSV合并去重 |
| PLC用但文档未定义 | 78 | 需重点核查 |
| 文档定义但PLC未使用 | 37 | 可能已废弃或预留 |
| 类型不一致 | 0 | VD/VW/VB 混用 |
| 读写方向冲突 | 1 | 文档只读但PLC写 |
| 地址重叠/冲突（疑似真正冲突） | 1 | 字-双字等需重点排查 |
| 地址重叠/冲突（位/字节打包） | 46 | 状态字/报警字/时间戳/Modbus缓冲区等打包使用，通常正常 |

## 二、严重不一致

### 2.1 读写方向冲突（文档只读，PLC实际写入）

| 地址 | 文档符号 | 问题描述 | 涉及文件/行号/上下文 | 建议修正 |
|---|---|---|---|---|
| VD:VD86 | VD_FlowMeter_Current | PLC写入但文档标记为只读 | FC4_ModbusPolling.stl:138 `MOVD   VD374, VD86                   // VD86=上一有效值` | 确认文档方向应为'读写'或检查PLC是否误写 |

### 2.3 地址重叠/冲突（疑似真正冲突）

| 地址1 | 字节范围1 | 地址2 | 字节范围2 | 重叠类型 | 建议修正 |
|---|---|---|---|---|---|
| VW:VW380 | VB380~VB381 | VD:VD380 | VB380~VB383 | 字-双字重叠（需重点排查） | 重新分配地址或确认不会同时有效 |

## 三、一般不一致

### 3.1 PLC程序使用但文档未定义/未说明的地址

> 注：下表包含大量PLC内部中间变量、状态机变量、Modbus缓冲区、定时器转换值等，这些通常无需写入HMI接口文档。建议优先关注V区参数、M区HMI交互位以及与CSV变量命名不一致的地址。

| 地址 | PLC类型 | 出现次数 | 涉及文件/行号（样例） | 建议修正 |
|---|---|---|---|---|
| VD:VD158 | VD | 12 | FC40_RhythmCorrection.stl:53 `MOVR   VD154, VD158                // Delta = Needed` | 补充到地址表/CSV或删除无用引用 |
| VD:VD162 | VD | 4 | FC40_RhythmCorrection.stl:31 `MOVR   VD36, VD162                 // VD_RestTime` | 补充到地址表/CSV或删除无用引用 |
| VD:VD166 | VD | 4 | FC40_RhythmCorrection.stl:34 `MOVR   VD28, VD166                 // VD_PreMixTime` | 补充到地址表/CSV或删除无用引用 |
| VD:VD170 | VD | 3 | FC40_RhythmCorrection.stl:37 `MOVR   VD44, VD170                 // VD_CycleExtend_Max(min)` | 补充到地址表/CSV或删除无用引用 |
| VD:VD186 | VD | 5 | FC0_SysInit.stl:144 `MOVR   0.0, VD186                  // 清VD_RTC_Now_Sec` | 补充到地址表/CSV或删除无用引用 |
| VD:VD190 | VD | 5 | FC0_SysInit.stl:167 `MOVR   0.0, VD190                  // 清VD_DT10_Sec` | 补充到地址表/CSV或删除无用引用 |
| VD:VD320 | VD | 3 | FC11_State_S1_Inlet.stl:47 `MOVR   VD66, VD320` | 补充到地址表/CSV或删除无用引用 |
| VD:VD324 | VD | 3 | FC15_State_S4_Transfer.stl:35 `MOVR   VD362, VD324` | 补充到地址表/CSV或删除无用引用 |
| VD:VD332 | VD | 3 | FC11_State_S1_Inlet.stl:42 `MOVR   VD358, VD332                  // 复制到中间变量(避免修改HMI设定值)` | 补充到地址表/CSV或删除无用引用 |
| VD:VD336 | VD | 3 | FC12_State_S2_PreMix.stl:22 `MOVR   VD120, VD336                // 复制到中间变量(避免修改VD_S2_Target)` | 补充到地址表/CSV或删除无用引用 |
| VD:VD340 | VD | 3 | FC14_State_S35_Rest.stl:18 `MOVR   VD124, VD340                // 复制到中间变量(避免修改VD_RestTime_Target)` | 补充到地址表/CSV或删除无用引用 |
| VD:VD344 | VD | 6 | FC12_State_S2_PreMix.stl:36 `MOVR   VD58, VD344                 // 复制VD_Timeout_Pump1` | 补充到地址表/CSV或删除无用引用 |
| VD:VD374 | VD | 3 | FC0_SysInit.stl:74 `MOVR   0.0, VD374                  // 流量计降级值清零` | 补充到地址表/CSV或删除无用引用 |
| VD:VD380 | VD | 6 | FC11_State_S1_Inlet.stl:75 `ITD    VW380, VD380                 // 整数→双整数` | 补充到地址表/CSV或删除无用引用 |
| VW:VW198 | VW | 10 | FC0_SysInit.stl:34 `MOVW   1, VW198                    // 步骤=1(开始初始化)` | 补充到地址表/CSV或删除无用引用 |
| VW:VW252 | VW | 2 | FC12_State_S2_PreMix.stl:25 `MOVW   AC0, VW252                  // VW252 = VD120×10` | 补充到地址表/CSV或删除无用引用 |
| VW:VW254 | VW | 2 | FC14_State_S35_Rest.stl:21 `MOVW   AC0, VW254                  // VW254 = VD124×10` | 补充到地址表/CSV或删除无用引用 |
| VW:VW260 | VW | 5 | FC30_ValveA_Diag.stl:42 `LDW=   VW260, 0` | 补充到地址表/CSV或删除无用引用 |
| VW:VW262 | VW | 5 | FC31_ValveB_Diag.stl:40 `LDW=   VW262, 0` | 补充到地址表/CSV或删除无用引用 |
| VW:VW264 | VW | 5 | FC32_ValveC_Diag.stl:27 `LDW=   VW264, 0` | 补充到地址表/CSV或删除无用引用 |
| VW:VW266 | VW | 1 | FC11_State_S1_Inlet.stl:67 `AW=    VW266, 1                    // 诊断正常完成?` | 补充到地址表/CSV或删除无用引用 |
| VW:VW268 | VW | 1 | FC15_State_S4_Transfer.stl:54 `AW=    VW268, 1` | 补充到地址表/CSV或删除无用引用 |
| VW:VW270 | VW | 9 | FC17_State_S6_Drain.stl:29 `MOVW   0, VW270` | 补充到地址表/CSV或删除无用引用 |
| VW:VW274 | VW | 4 | FC15_State_S4_Transfer.stl:38 `MOVW   AC0, VW274` | 补充到地址表/CSV或删除无用引用 |
| VW:VW276 | VW | 4 | FC17_State_S6_Drain.stl:34 `MOVW   AC0, VW276` | 补充到地址表/CSV或删除无用引用 |
| VW:VW278 | VW | 2 | FC11_State_S1_Inlet.stl:45 `MOVW   AC0, VW278` | 补充到地址表/CSV或删除无用引用 |
| VW:VW280 | VW | 2 | FC11_State_S1_Inlet.stl:50 `MOVW   AC0, VW280` | 补充到地址表/CSV或删除无用引用 |
| VW:VW282 | VW | 2 | FC12_State_S2_PreMix.stl:39 `MOVW   AC0, VW282                  // VW282 = VD58×10(泵1超时PT)` | 补充到地址表/CSV或删除无用引用 |
| VW:VW284 | VW | 2 | FC12_State_S2_PreMix.stl:51 `MOVW   AC0, VW284                  // VW284 = VD62×10(泵2超时PT)` | 补充到地址表/CSV或删除无用引用 |
| VW:VW300 | VW | 1 | FC0_SysInit.stl:54 `FILL   0, VW300, 4                 // VB300~VB303清零(报警字)` | 补充到地址表/CSV或删除无用引用 |
| VW:VW380 | VW | 8 | FC11_State_S1_Inlet.stl:74 `MOVW   T37, VW380                   // 暂存定时器值(16位整数)` | 补充到地址表/CSV或删除无用引用 |
| VW:VW96 | VW | 2 | FC4_ModbusPolling.stl:73 `MOVW   VW96, VW4                     // VW4=上一有效值` | 补充到地址表/CSV或删除无用引用 |
| VB:VB10 | VB | 4 | FC0_SysInit.stl:90 `LDB=   VB10, 0` | 补充到地址表/CSV或删除无用引用 |
| VB:VB11 | VB | 3 | FC0_SysInit.stl:101 `LDB<   VB901, VB11` | 补充到地址表/CSV或删除无用引用 |
| VB:VB12 | VB | 3 | FC0_SysInit.stl:106 `LDB<   VB902, VB12` | 补充到地址表/CSV或删除无用引用 |
| VB:VB13 | VB | 4 | FC0_SysInit.stl:111 `LDB<   VB903, VB13` | 补充到地址表/CSV或删除无用引用 |
| VB:VB14 | VB | 4 | FC0_SysInit.stl:116 `LDB<   VB904, VB14` | 补充到地址表/CSV或删除无用引用 |
| VB:VB15 | VB | 3 | FC0_SysInit.stl:121 `LDB<   VB905, VB15` | 补充到地址表/CSV或删除无用引用 |
| VB:VB16 | VB | 1 | FC15_State_S4_Transfer.stl:71 `MOVB   VB906, VB16` | 补充到地址表/CSV或删除无用引用 |
| VB:VB17 | VB | 1 | FC15_State_S4_Transfer.stl:72 `MOVB   VB908, VB17` | 补充到地址表/CSV或删除无用引用 |
| VB:VB184 | VB | 5 | FC40_RhythmCorrection.stl:73 `MOVB   2, VB184                   // Result=2(已纠偏)` | 补充到地址表/CSV或删除无用引用 |
| VB:VB204 | VB | 1 | FC4_ModbusPolling.stl:194 `CALL   SBR21, L63.7, 16#01, 16#00, 40006, 16#02, &VB204, M10.2, VB379` | 补充到地址表/CSV或删除无用引用 |
| VB:VB208 | VB | 1 | FC4_ModbusPolling.stl:240 `CALL   SBR21, L63.7, 16#01, 16#00, 40009, 16#03, &VB208, M10.3, VB379` | 补充到地址表/CSV或删除无用引用 |
| VB:VB260 | VB | 5 | FC11_State_S1_Inlet.stl:35 `MOVB   1, VB260` | 补充到地址表/CSV或删除无用引用 |
| VB:VB261 | VB | 5 | FC11_State_S1_Inlet.stl:36 `MOVB   0, VB261` | 补充到地址表/CSV或删除无用引用 |
| VB:VB262 | VB | 5 | FC15_State_S4_Transfer.stl:29 `MOVB   1, VB262` | 补充到地址表/CSV或删除无用引用 |
| VB:VB263 | VB | 5 | FC15_State_S4_Transfer.stl:30 `MOVB   0, VB263` | 补充到地址表/CSV或删除无用引用 |
| VB:VB264 | VB | 5 | FC17_State_S6_Drain.stl:26 `MOVB   1, VB264` | 补充到地址表/CSV或删除无用引用 |
| VB:VB265 | VB | 5 | FC17_State_S6_Drain.stl:27 `MOVB   0, VB265` | 补充到地址表/CSV或删除无用引用 |
| VB:VB266 | VB | 6 | FC11_State_S1_Inlet.stl:38 `MOVB   0, VB266` | 补充到地址表/CSV或删除无用引用 |
| VB:VB267 | VB | 1 | FC11_State_S1_Inlet.stl:39 `MOVB   0, VB267` | 补充到地址表/CSV或删除无用引用 |
| VB:VB268 | VB | 9 | FC15_State_S4_Transfer.stl:32 `MOVB   0, VB268` | 补充到地址表/CSV或删除无用引用 |
| VB:VB269 | VB | 1 | FC15_State_S4_Transfer.stl:33 `MOVB   0, VB269` | 补充到地址表/CSV或删除无用引用 |
| VB:VB4 | VB | 1 | FC4_ModbusPolling.stl:68 `CALL   SBR21, L63.7, 16#01, 16#00, 41001, 16#01, &VB4, M10.0, VB379` | 补充到地址表/CSV或删除无用引用 |
| VB:VB500 | VB | 1 | FC3_AlarmHandling.stl:437 `TODR VB500                       // 时间戳写入VB500~507` | 补充到地址表/CSV或删除无用引用 |
| VB:VB508 | VB | 1 | FC3_AlarmHandling.stl:440 `MOVB   1, VB508                      // 单元编号=1(本PLC)` | 补充到地址表/CSV或删除无用引用 |
| VB:VB509 | VB | 1 | FC3_AlarmHandling.stl:438 `MOVB   VB7, VB509                    // 报警码(VW6低字节VB7)` | 补充到地址表/CSV或删除无用引用 |
| VB:VB510 | VB | 1 | FC3_AlarmHandling.stl:439 `MOVB   1, VB510                      // 动作=1(触发)` | 补充到地址表/CSV或删除无用引用 |
| VB:VB520 | VB | 1 | FC4_ModbusPolling.stl:281 `TODR   VB520                       // 记录进入降级模式时间` | 补充到地址表/CSV或删除无用引用 |
| VB:VB530 | VB | 1 | FC4_ModbusPolling.stl:284 `TODR   VB530                       // 记录流量计进入降级时间` | 补充到地址表/CSV或删除无用引用 |
| VB:VB7 | VB | 1 | FC3_AlarmHandling.stl:438 `MOVB   VB7, VB509                    // 报警码(VW6低字节VB7)` | 补充到地址表/CSV或删除无用引用 |
| VB:VB86 | VB | 1 | FC4_ModbusPolling.stl:133 `CALL   SBR21, L63.7, 16#02, 16#00, 40009, 16#02, &VB86, M10.1, VB384` | 补充到地址表/CSV或删除无用引用 |
| VB:VB900 | VB | 5 | FC0_SysInit.stl:85 `TODR VB900                     // 读RTC到VB900~VB907(BCD)` | 补充到地址表/CSV或删除无用引用 |
| VB:VB901 | VB | 3 | FC0_SysInit.stl:101 `LDB<   VB901, VB11` | 补充到地址表/CSV或删除无用引用 |
| VB:VB902 | VB | 3 | FC0_SysInit.stl:106 `LDB<   VB902, VB12` | 补充到地址表/CSV或删除无用引用 |
| VB:VB903 | VB | 4 | FC0_SysInit.stl:111 `LDB<   VB903, VB13` | 补充到地址表/CSV或删除无用引用 |
| VB:VB904 | VB | 4 | FC0_SysInit.stl:116 `LDB<   VB904, VB14` | 补充到地址表/CSV或删除无用引用 |
| VB:VB905 | VB | 3 | FC0_SysInit.stl:121 `LDB<   VB905, VB15` | 补充到地址表/CSV或删除无用引用 |
| VB:VB906 | VB | 1 | FC15_State_S4_Transfer.stl:71 `MOVB   VB906, VB16` | 补充到地址表/CSV或删除无用引用 |
| VB:VB908 | VB | 1 | FC15_State_S4_Transfer.stl:72 `MOVB   VB908, VB17` | 补充到地址表/CSV或删除无用引用 |
| V_bit:V304.0 | V_bit | 3 | FC0_SysInit.stl:35 `LD     V304.0                      // 初始化完成标志=1?` | 补充到地址表/CSV或删除无用引用 |
| M_bit:M10.6 | M_bit | 5 | FC17_State_S6_Drain.stl:69 `AN     M10.6                       // 实验未结束` | 补充到地址表/CSV或删除无用引用 |
| M_bit:M10.7 | M_bit | 10 | FC0_SysInit.stl:62 `R      M10.7, 1                    // 清预规划触发标志` | 补充到地址表/CSV或删除无用引用 |
| M_bit:M11.1 | M_bit | 4 | FC3_AlarmHandling.stl:210 `R      M11.1, 1                      // 清消音标志(新报警重鸣)` | 补充到地址表/CSV或删除无用引用 |
| M_bit:M11.2 | M_bit | 3 | FC3_AlarmHandling.stl:209 `AN     M11.2                         // 上一周期无报警 → 新报警` | 补充到地址表/CSV或删除无用引用 |
| M_bit:M11.3 | M_bit | 3 | FC3_AlarmHandling.stl:472 `AN     M11.3                         // 上一周期OFF,本周期ON → 翻转` | 补充到地址表/CSV或删除无用引用 |
| M_bit:M11.4 | M_bit | 3 | FC3_AlarmHandling.stl:481 `AN     M11.4                         // M11.4=I0.1上一周期状态` | 补充到地址表/CSV或删除无用引用 |
| M_bit:M11.5 | M_bit | 3 | FC3_AlarmHandling.stl:490 `AN     M11.5                         // M11.5=I0.2上一周期状态` | 补充到地址表/CSV或删除无用引用 |

### 3.2 文档/CSV定义但PLC程序未见使用的地址

| 地址 | 文档类型 | 方向 | 符号/备注 | 来源 | 建议修正 |
|---|---|---|---|---|---|
| DT:DT10 | 未指定 | 未指定 | DT_TankB_FullTime / DT(日期时间) | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| I_bit:I2.2 | BOOL | 未指定 | —（备用） / 预留 | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VB:VB300 | BYTE | 只读 | U1_VB300_AlarmByte0 / 报警字节0(漫溢+急停) | CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VB:VB301 | BYTE | 只读 | U1_VB301_AlarmByte1 / 报警字节1(阀A诊断) | CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VB:VB302 | BYTE | 只读 | U1_VB302_AlarmByte2 / 报警字节2(阀B诊断) | CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VB:VB303 | BYTE | 只读 | U1_VB303_AlarmByte3 / 报警字节3(其他) | CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD100 | REAL | 未指定 | 配液节奏纠偏变量 / REAL | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD104 | REAL | 未指定 | VD_T_Default / s | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD108 | REAL | 未指定 | VD_S6_Default / s | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD132 | REAL | 未指定 | VD_PumpSpeed_Start / Hz | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD136 | REAL | 未指定 | VD_PumpSpeed_Max / Hz | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD140 | REAL | 未指定 | VD_PumpSpeed_Cutoff / Hz | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD22 | REAL | 未指定 | HMI设定参数（浮点；VD18/VD48已迁移至VD350/VD358） / REAL | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD26 | REAL | 未指定 | HMI设定参数（浮点；VD18/VD48已迁移至VD350/VD358） / REAL | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD30 | REAL | 未指定 | HMI设定参数（浮点；VD18/VD48已迁移至VD350/VD358） / REAL | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD34 | REAL | 未指定 | HMI设定参数（浮点；VD18/VD48已迁移至VD350/VD358） / REAL | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD38 | REAL | 未指定 | HMI设定参数（浮点；VD18/VD48已迁移至VD350/VD358） / REAL | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD42 | REAL | 未指定 | HMI设定参数（浮点；VD18/VD48已迁移至VD350/VD358） / REAL | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD46 | REAL | 未指定 | HMI设定参数（浮点；VD18/VD48已迁移至VD350/VD358） / REAL | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VD:VD94 | REAL | 未指定 | VD_FlowRate_Instant / REAL(L/min) | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW200 | INT/WORD | 未指定 | 40002 / 0x0001 | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW202 | INT/WORD | 未指定 | 40003 / 0x0002 | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW208 | INT/WORD | 读写 | 40009 / 0x0008 | MD,CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW210 | INT/WORD | 读写 | 40010 / 0x0009 | MD,CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW212 | INT/WORD | 未指定 | 40011 / 0x000A | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW214 | INT/WORD | 未指定 | 40015 / 0x000E | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW216 | INT/WORD | 未指定 | 40016 / 0x000F | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW218 | INT/WORD | 未指定 | 40017 / 0x0010 | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW220 | INT/WORD | 未指定 | 40018 / 0x0011 | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW222 | INT/WORD | 未指定 | 41007 / 0x03EE | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| VW:VW228 | INT/WORD | 未指定 | 0x0012 / 0x0012 | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| V_bit:V0.1 | BOOL | 读写 | CMD_Pause / 暂停实验（保留，当前状态机无暂停态，预留） | MD,CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| V_bit:V0.5 | BOOL | 读写 | CMD_ForceTankA_Empty / 强制修正上缸状态=空 | MD,CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| V_bit:V0.6 | BOOL | 读写 | CMD_ForceTankA_Full / 强制修正上缸状态=满 | MD,CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| V_bit:V1.1 | BOOL | 只读 | STA_PauseAck / 暂停命令已接收（预留） | MD,CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| V_bit:V1.5 | BOOL | 只读 | STA_ForceDone / 状态强制修正已执行 | MD,CSV,CSV,CSV,CSV,CSV,CSV,CSV,CSV | 确认是否预留/废弃；若废弃则从文档/CSV移除 |
| V_bit:V303.7 | BOOL | 未指定 | —（预留） / 预留扩展 | MD | 确认是否预留/废弃；若废弃则从文档/CSV移除 |

## 四、仅文档待更新

### 4.1 注释/命名与文档符号不一致（需澄清）

以下地址在代码注释或CSV变量名中的称呼与地址表符号存在差异，建议统一命名。

| 地址 | 文档符号 | CSV/代码称呼 | 说明 | 建议 |
|---|---|---|---|---|
| VD:VD86 | VD_FlowMeter_Current | U1_VD_FlowCum | 文档称Current，CSV称Cum | 统一变量命名 |
| VW:VW4 | MB_Pump_Status | U1_VW4_PumpStatus | CSV未体现Modbus来源 | 统一变量命名 |
| VD:VD90 | VD_Current_InletVolume | U1_VD_FlowDiff | 文档为进水量，CSV为差值 | 统一变量命名 |

### 4.2 默认值差异

CSV中部分参数默认值与地址表不一致，需核实：

| 地址 | CSV默认值 | 地址表默认值 | 建议 |
|---|---|---|---|
| VD:VD350 | 0.5 | 0.2083 | 以地址表0.2083为准，CSV需更新 |
| VD:VD354 | 3.0 | 30.0 | 以地址表30.0为准，CSV需更新 |
| VD:VD24 | 5.0 | 480.0 | 以地址表480.0为准，CSV需更新 |
| VD:VD28 | 12.0 | 120.0 | 以地址表120.0为准，CSV需更新 |
| VD:VD32 | 3.0 | 30.0 | 以地址表30.0为准，CSV需更新 |
| VD:VD36 | 6.0 | 60.0 | 以地址表60.0为准，CSV需更新 |
| VD:VD40 | 1.5 | 15.0 | 以地址表15.0为准，CSV需更新 |
| VD:VD44 | 0.5 | 5.0 | 以地址表5.0为准，CSV需更新 |
| VD:VD358 | 2.0 | 60.0 | 以地址表60.0为准，CSV需更新 |
| VD:VD362 | 2.0 | 60.0 | 以地址表60.0为准，CSV需更新 |
| VD:VD54 | 2.0 | 60.0 | 以地址表60.0为准，CSV需更新 |
| VD:VD58 | 2.0 | 10.0 | 以地址表10.0为准，CSV需更新 |
| VD:VD62 | 2.0 | 10.0 | 以地址表10.0为准，CSV需更新 |
| VD:VD66 | 0.5 | 5.0 | 以地址表5.0为准，CSV需更新 |
| VD:VD112 | 20.0 | — | CSV有默认值但地址表未列，需补充 |
| VD:VD116 | 0.0 | — | CSV有默认值但地址表未列，需补充 |
| VD:VD120 | 12.0 | — | CSV有默认值但地址表未列，需补充 |
| VD:VD124 | 6.0 | — | 地址表已迁移至VD128，CSV未同步 |
| VD:VD174 | 5.0 | — | CSV中S3估算，地址表未定义 |
| VD:VD316 | 10.0 | — | CSV中目标进水量，地址表未定义 |
| VD:VD308 | 0.0 | — | CSV中关阀快照，地址表未定义 |
| VD:VD150 | — | — | PLC实测值，CSV只读，地址表未定义 |
| VD:VD154 | — | — | PLC中间值，CSV只读，地址表未定义 |
| VD:VD178 | — | — | PLC实测值S5_Elapsed，CSV只读，地址表未定义 |
| VD:VD312 | — | — | PLC中间值LeakDiff，CSV只读，地址表未定义 |
| VD:VD328 | — | — | PLC中间值Timeout_ValveC_x10，CSV只读，地址表未定义 |

## 五、建议澄清

### 5.1 关键 recently changed 地址核查

以下地址在FC4/FC0/OB1中 recently changed，建议逐一确认文档已同步：

| 地址 | 涉及文件 | 状态 | 建议 |
|---|---|---|---|
| M_bit:M10.0 | FC0_SysInit.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| M_bit:M10.1 | FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| M_bit:M10.2 | FC11_State_S1_Inlet.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| M_bit:M10.3 | FC13_State_S3_Dosing.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| M_bit:M10.4 | FC15_State_S4_Transfer.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| M_bit:M10.5 | FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| VB:VB378 | FC0_SysInit.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| VB:VB379 | FC0_SysInit.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| VB:VB384 | FC0_SysInit.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| VW:VW290 | FC0_SysInit.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| VW:VW292 | FC0_SysInit.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| VW:VW294 | FC0_SysInit.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |
| VW:VW296 | FC0_SysInit.stl, FC4_ModbusPolling.stl | ✅ 已定义 | 文档已同步，保持 |

### 5.2 未解析或异常地址

以下地址类型在STL中出现但文档未明确规划，或属于内部临时变量：

| 类型 | 示例地址 | 说明 | 建议 |
|---|---|---|---|
| AC | AC:AC0 | STL局部变量/累加器 | 无需进入HMI文档 |
| L_bit | L_bit:L60.0, L_bit:L60.1, L_bit:L63.7 | STL局部变量/累加器 | 无需进入HMI文档 |
| SM | SM:SM0.0, SM:SM0.1 | 系统特殊存储器 | 无需进入HMI文档，但应在PLC设计文档说明 |

### 5.3 地址重叠/冲突（位/字节打包使用，通常正常）

以下地址存在不同粒度重叠，但多为状态字/报警字/时间戳/Modbus缓冲区位打包使用，通常正常，建议人工复核确认：

| 地址1 | 字节范围1 | 地址2 | 字节范围2 | 重叠类型 | 涉及文件（样例） | 建议 |
|---|---|---|---|---|---|---|
| V_bit:V2.7 | V2.7 | VW:VW2 | VB2~VB3 | 位打包（通常正常） | FC20_ManualControl.stl:69 | 确认属于位/字节打包后保持现状 |
| V_bit:V300.5 | V300.5 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC19_State_Error.stl:36 | 确认属于位/字节打包后保持现状 |
| VB:VB13 | VB13~VB13 | VD:VD10 | VB10~VB13 | 字节打包（通常正常） | FC0_SysInit.stl:111 | 确认属于位/字节打包后保持现状 |
| VB:VB263 | VB263~VB263 | VW:VW262 | VB262~VB263 | 字节打包（通常正常） | FC15_State_S4_Transfer.stl:30 | 确认属于位/字节打包后保持现状 |
| VB:VB16 | VB16~VB16 | VD:VD14 | VB14~VB17 | 字节打包（通常正常） | FC15_State_S4_Transfer.stl:71 | 确认属于位/字节打包后保持现状 |
| V_bit:V301.3 | V301.3 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC30_ValveA_Diag.stl:173 | 确认属于位/字节打包后保持现状 |
| VW:VW262 | VB262~VB263 | VB:VB262 | VB262~VB262 | 字节打包（通常正常） | FC31_ValveB_Diag.stl:40 | 确认属于位/字节打包后保持现状 |
| VB:VB266 | VB266~VB266 | VW:VW266 | VB266~VB267 | 字节打包（通常正常） | FC11_State_S1_Inlet.stl:38 | 确认属于位/字节打包后保持现状 |
| V_bit:V2.5 | V2.5 | VW:VW2 | VB2~VB3 | 位打包（通常正常） | FC20_ManualControl.stl:51 | 确认属于位/字节打包后保持现状 |
| VB:VB12 | VB12~VB12 | VD:VD10 | VB10~VB13 | 字节打包（通常正常） | FC0_SysInit.stl:106 | 确认属于位/字节打包后保持现状 |
| VD:VD10 | VB10~VB13 | VB:VB11 | VB11~VB11 | 字节打包（通常正常） | FC13_State_S3_Dosing.stl:15 | 确认属于位/字节打包后保持现状 |
| VD:VD10 | VB10~VB13 | VB:VB10 | VB10~VB10 | 字节打包（通常正常） | FC13_State_S3_Dosing.stl:15 | 确认属于位/字节打包后保持现状 |
| VB:VB7 | VB7~VB7 | VW:VW6 | VB6~VB7 | 字节打包（通常正常） | FC3_AlarmHandling.stl:438 | 确认属于位/字节打包后保持现状 |
| V_bit:V300.0 | V300.0 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC30_ValveA_Diag.stl:30 | 确认属于位/字节打包后保持现状 |
| V_bit:V300.7 | V300.7 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC3_AlarmHandling.stl:48 | 确认属于位/字节打包后保持现状 |
| VB:VB261 | VB261~VB261 | VW:VW260 | VB260~VB261 | 字节打包（通常正常） | FC11_State_S1_Inlet.stl:36 | 确认属于位/字节打包后保持现状 |
| V_bit:V300.2 | V300.2 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC30_ValveA_Diag.stl:31 | 确认属于位/字节打包后保持现状 |
| V_bit:V2.6 | V2.6 | VW:VW2 | VB2~VB3 | 位打包（通常正常） | FC20_ManualControl.stl:61 | 确认属于位/字节打包后保持现状 |
| VD:VD14 | VB14~VB17 | VB:VB17 | VB17~VB17 | 字节打包（通常正常） | FC13_State_S3_Dosing.stl:17 | 确认属于位/字节打包后保持现状 |
| VD:VD14 | VB14~VB17 | VB:VB15 | VB15~VB15 | 字节打包（通常正常） | FC13_State_S3_Dosing.stl:17 | 确认属于位/字节打包后保持现状 |
| VD:VD14 | VB14~VB17 | VB:VB14 | VB14~VB14 | 字节打包（通常正常） | FC13_State_S3_Dosing.stl:17 | 确认属于位/字节打包后保持现状 |
| VW:VW266 | VB266~VB267 | VB:VB267 | VB267~VB267 | 字节打包（通常正常） | FC11_State_S1_Inlet.stl:67 | 确认属于位/字节打包后保持现状 |
| VB:VB265 | VB265~VB265 | VW:VW264 | VB264~VB265 | 字节打包（通常正常） | FC17_State_S6_Drain.stl:27 | 确认属于位/字节打包后保持现状 |
| V_bit:V301.0 | V301.0 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC30_ValveA_Diag.stl:157 | 确认属于位/字节打包后保持现状 |
| V_bit:V301.2 | V301.2 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC30_ValveA_Diag.stl:168 | 确认属于位/字节打包后保持现状 |
| V_bit:V301.5 | V301.5 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC30_ValveA_Diag.stl:103 | 确认属于位/字节打包后保持现状 |
| V_bit:V3.2 | V3.2 | VW:VW2 | VB2~VB3 | 位打包（通常正常） | FC20_ManualControl.stl:96 | 确认属于位/字节打包后保持现状 |
| VB:VB268 | VB268~VB268 | VW:VW268 | VB268~VB269 | 字节打包（通常正常） | FC15_State_S4_Transfer.stl:32 | 确认属于位/字节打包后保持现状 |
| V_bit:V3.0 | V3.0 | VW:VW2 | VB2~VB3 | 位打包（通常正常） | FC20_ManualControl.stl:79 | 确认属于位/字节打包后保持现状 |
| VW:VW268 | VB268~VB269 | VB:VB269 | VB269~VB269 | 字节打包（通常正常） | FC15_State_S4_Transfer.stl:54 | 确认属于位/字节打包后保持现状 |
| V_bit:V301.6 | V301.6 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC16_State_S5_Run.stl:66 | 确认属于位/字节打包后保持现状 |
| V_bit:V3.1 | V3.1 | VW:VW2 | VB2~VB3 | 位打包（通常正常） | FC20_ManualControl.stl:86 | 确认属于位/字节打包后保持现状 |
| VB:VB260 | VB260~VB260 | VW:VW260 | VB260~VB261 | 字节打包（通常正常） | FC11_State_S1_Inlet.stl:35 | 确认属于位/字节打包后保持现状 |
| V_bit:V301.4 | V301.4 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC30_ValveA_Diag.stl:81 | 确认属于位/字节打包后保持现状 |
| VW:VW264 | VB264~VB265 | VB:VB264 | VB264~VB264 | 字节打包（通常正常） | FC32_ValveC_Diag.stl:27 | 确认属于位/字节打包后保持现状 |
| VW:VW4 | VB4~VB5 | VB:VB4 | VB4~VB4 | 字节打包（通常正常） | FC13_State_S3_Dosing.stl:48 | 确认属于位/字节打包后保持现状 |
| V_bit:V3.3 | V3.3 | VW:VW2 | VB2~VB3 | 位打包（通常正常） | FC20_ManualControl.stl:102 | 确认属于位/字节打包后保持现状 |
| VB:VB184 | VB184~VB184 | VW:VW184 | VB184~VB185 | 字节打包（通常正常） | FC40_RhythmCorrection.stl:73 | 确认属于位/字节打包后保持现状 |
| V_bit:V300.1 | V300.1 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC31_ValveB_Diag.stl:29 | 确认属于位/字节打包后保持现状 |
| VB:VB86 | VB86~VB86 | VD:VD86 | VB86~VB89 | 字节打包（通常正常） | FC4_ModbusPolling.stl:133 | 确认属于位/字节打包后保持现状 |
| V_bit:V300.6 | V300.6 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC3_AlarmHandling.stl:46 | 确认属于位/字节打包后保持现状 |
| VW:VW2 | VB2~VB3 | V_bit:V2.4 | V2.4 | 位打包（通常正常） | FC0_SysInit.stl:44 | 确认属于位/字节打包后保持现状 |
| V_bit:V300.3 | V300.3 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC31_ValveB_Diag.stl:30 | 确认属于位/字节打包后保持现状 |
| V_bit:V301.1 | V301.1 | VW:VW300 | VB300~VB301 | 位打包（通常正常） | FC30_ValveA_Diag.stl:163 | 确认属于位/字节打包后保持现状 |
| VW:VW300 | VB300~VB301 | V_bit:V300.4 | V300.4 | 位打包（通常正常） | FC0_SysInit.stl:54 | 确认属于位/字节打包后保持现状 |
| VW:VW204 | VB204~VB205 | VB:VB204 | VB204~VB204 | 字节打包（通常正常） | FC13_State_S3_Dosing.stl:35 | 确认属于位/字节打包后保持现状 |

## 六、附录：核对方法说明

1. **地址提取**：使用正则表达式从STL源码中提取V/I/Q/M/SM/T/C/DT/AC/L区地址，保留文件、行号、指令上下文。
2. **文档基准**：合并 `HMI-PLC变量地址表_v1.0.md` 与 `McgsPro变量导入_8单元_v2.0.csv` 中的地址定义。
3. **读写方向判断**：根据STL指令助记符（=、S、R、MOVx、MOVR、FILL、+R/-R/*R等）判断PLC是否写入该地址。
4. **地址重叠**：将V区地址统一换算为字节范围，检测范围交集。
5. **分级原则**：
   - **严重不一致**：读写方向冲突、数据类型不一致、地址重叠冲突。
   - **一般不一致**：PLC使用但文档未定义、文档定义但PLC未使用。
   - **仅文档待更新**：命名差异、默认值差异。
   - **建议澄清**：recently changed地址、内部/系统变量等需人工确认项。
