# PLC 完整寄存器映射表（所有区）

> **文档性质**: 机器生成 + 人工确认。由 Python 静态分析器扫描所有 STL 文件 + MCGS CSV 自动生成。
> **生成日期**: 2026-09-12
> **覆盖范围**: S7-200 SMART 全部寄存器区 — V区、M区、T区、C区、I区、Q区、AC累加器区、模拟量区
> **用途**: 杜绝地址冲突、分配新寄存器时的唯一参考、排查现场 Bug 时的第一工具
> **重命名说明**: 原文件名 `PLC_V区寄存器映射表_v1.0.md`，v1.0 追加 M/T/C/I/Q/AC 区扫描后改为现名

***

## 一、字节级占用全景（VB0 \~ VB908）

颜色图例：🟢 正常独占  🟡 多FC共用但不冲突  🔴 物理重叠/多用途冲突  🔵 HMI参数  ⚪ 空闲

| 字节范围         | 最宽类型            | FC引用                        | HMI参数                                                              | 用途摘要                                                     | 冲突?      | 断电保持      |
| ------------ | --------------- | --------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------- | -------- | --------- |
| VB  0\~VB  3 | WORD (2B)       | FC0,FC10,FC11,FC12,FC13 等21 | <br />                                                             | ★ 2026-09-11修复: 冷启动必须清 VB0, 防止 V0.x 命令位断电保持后卡1           | 🔴 **是** | <br />    |
| VB  4\~VB  7 | WORD (2B)       | FC0,FC10,FC13,FC15,FC19 等11 | <br />                                                             | 2. 状态码: VW4=0(96就绪), VW4=1(64空闲), VW4=2(100运动中), VW4≥4(  | 🔴 **是** | <br />    |
| VB  8\~VB 11 | REAL/DWORD (4B) | FC0,FC13,FC15,OB1           | U1\_VD\_C\_Set\@10                                                 | VW8=0                                                    | 🔴 **是** | <br />    |
| VB 12\~VB 15 | REAL/DWORD (4B) | FC0,FC13,FC15               | U1\_VD\_C\_Stock\@14                                               | VD\_C\_Set 目标浓度(%)                                       | 🔴 **是** | ⚠️ DT10重叠 |
| VB 16\~VB 19 | REAL/DWORD (4B) | FC0,FC13,FC15               | <br />                                                             | VD\_C\_Stock 母液浓度(%)                                     | 🔴 **是** | ⚠️ DT10重叠 |
| VB 24\~VB 27 | REAL/DWORD (4B) | FC0,FC16                    | U1\_VD\_ExperimentTarget\@24                                       | VD\_ExperimentTarget 实验总时长(min)                          | 🔴 **是** | <br />    |
| VB 28\~VB 31 | REAL/DWORD (4B) | FC0,FC11,FC40               | U1\_VD\_PreMixTime\@28                                             | VD\_PreMixTime S2预循环标称时长(s)                              | 🔴 **是** | <br />    |
| VB 32\~VB 35 | REAL/DWORD (4B) | FC0,FC40                    | U1\_VD\_PreMixTime\_MinSafe\@32                                    | VD\_PreMixTime\_MinSafe S2压缩下限(s)                        | 🔴 **是** | <br />    |
| VB 36\~VB 39 | REAL/DWORD (4B) | FC0,FC11,FC40               | U1\_VD\_RestTime\@36                                               | VD\_RestTime S3.5静止等候标称时长(s)                             | 🔴 **是** | <br />    |
| VB 40\~VB 43 | REAL/DWORD (4B) | FC0,FC40                    | U1\_VD\_RestTime\_Min\@40                                          | VD\_RestTime\_Min S3.5压缩下限(s)                            | 🔴 **是** | <br />    |
| VB 44\~VB 47 | REAL/DWORD (4B) | FC0,FC40                    | U1\_VD\_CycleExtend\_Max\@44                                       | VD\_CycleExtend\_Max 换水周期顺延最大幅度(min)                     | 🔴 **是** | <br />    |
| VB 52\~VB 55 | REAL/DWORD (4B) | FC0,FC17,FC32               | U1\_VD\_Timeout\_ValveC\@54                                        | VD\_Timeout\_ValveC 阀C开/关到位超时(s)                         | 🔴 **是** | <br />    |
| VB 56\~VB 59 | REAL/DWORD (4B) | FC0,FC17,FC32               | U1\_VD\_Timeout\_Pump1\@58                                         | VD\_Timeout\_ValveC 阀C开/关到位超时(s)                         | 🔴 **是** | <br />    |
| VB 60\~VB 63 | REAL/DWORD (4B) | FC0                         | U1\_VD\_Timeout\_Pump2\@62                                         | VD\_Timeout\_Pump1 (预留未用)                                | <br />   | <br />    |
| VB 64\~VB 67 | REAL/DWORD (4B) | FC0,FC11                    | U1\_VD\_Delay\_ValveA\_Verify\@66                                  | VD\_Timeout\_Pump2 (预留未用)                                | 🔴 **是** | <br />    |
| VB 68\~VB 71 | REAL/DWORD (4B) | FC0,FC11                    | U1\_VD\_S1\_Actual\@70                                             | VD\_Delay\_ValveA\_Verify 阀A关后延时验证(s)                    | 🔴 **是** | <br />    |
| VB 72\~VB 75 | REAL/DWORD (4B) | FC11,FC15                   | U1\_VD\_S4\_Actual\@74                                             | 双整数→实数(VD\_S1\_Actual)                                   | 🟡 多FC共享 | <br />    |
| VB 76\~VB 79 | REAL/DWORD (4B) | FC15,FC17                   | U1\_VD\_S6\_Actual\@78                                             | 双整数→实数(VD\_S4\_Actual)                                   | 🟡 多FC共享 | <br />    |
| VB 80\~VB 83 | REAL/DWORD (4B) | FC11,FC17,FC30              | U1\_VD\_FlowMeter\_Snapshot\@82                                    | 双整数→实数(VD\_S6\_Actual)                                   | 🔴 **是** | <br />    |
| VB 84\~VB 87 | REAL/DWORD (4B) | FC11,FC30,FC4               | U1\_VD\_FlowMeter\_Current\@86                                     | VD\_Current\_InletVolume(VD90) = VD86(当前累计) - VD82(开启快照) | 🔴 **是** | <br />    |
| VB 88\~VB 91 | REAL/DWORD (4B) | FC11,FC13,FC30,FC4          | U1\_VD\_Current\_InletVolume\@90                                   | VD\_Current\_InletVolume(VD90) = VD86(当前累计) - VD82(开启快照) | 🔴 **是** | <br />    |
| VB 92\~VB 95 | REAL/DWORD (4B) | FC11,FC13,FC30,FC4          | U1\_VD\_FlowRate\_Instant\@94                                      | AC0 = VD\_Current\_InletVolume                           | 🔴 **是** | <br />    |
| VB 96\~VB 99 | REAL/DWORD (4B) | FC4                         | <br />                                                             | 任务3: 流量计瞬时流量读(40007) → VD94                              | <br />   | <br />    |
| VB100\~VB103 | REAL/DWORD (4B) | FC13,FC21                   | U1\_VD\_Dose\_Steps\@102                                           | VD102 : VD\_Dose\_Steps    本次循环目标步数(REAL)                | 🔴 **是** | <br />    |
| VB104\~VB107 | REAL/DWORD (4B) | FC13,FC21                   | <br />                                                             | VD102 : VD\_Dose\_Steps    本次循环目标步数(REAL)                | 🔴 **是** | <br />    |
| VB108\~VB111 | REAL/DWORD (4B) | FC0,FC10                    | U1\_VD\_S6\_Default\@108                                           | VD\_S6\_Default 首轮S6排水时长默认值(s)                           | 🔴 **是** | <br />    |
| VB112\~VB115 | REAL/DWORD (4B) | FC10,FC11,FC16              | U1\_VD\_T\_Rolling\@112                                            | T滚动值 ← T默认值(HMI设定)                                       | 🔴 **是** | <br />    |
| VB116\~VB119 | REAL/DWORD (4B) | FC10,FC11,FC16,FC17         | U1\_VD\_S6\_Rolling\@116                                           | S6滚动值 ← S6默认值(HMI设定)                                     | 🔴 **是** | <br />    |
| VB120\~VB123 | REAL/DWORD (4B) | FC11,FC12,FC40              | U1\_VD\_S2\_Target\@120                                            | VD\_S2\_Target                                           | 🔴 **是** | <br />    |
| VB124\~VB127 | REAL/DWORD (4B) | FC11,FC14,FC40              | U1\_VD\_RestTime\_Target\@124                                      | + VD\_RestTime\_Target = Needed'                         | 🔴 **是** | <br />    |
| VB128\~VB131 | REAL/DWORD (4B) | FC40                        | <br />                                                             | VD128 : VD\_CycleExtend\_Target 输出:允许下缸空等时长(min)         | <br />   | <br />    |
| VB132\~VB135 | HMI only        | <br />                      | U1\_VD\_PumpSpeed\_Start\@132                                      | <br />                                                   | <br />   | <br />    |
| VB136\~VB139 | HMI only        | <br />                      | U1\_VD\_PumpSpeed\_Max\@136                                        | <br />                                                   | <br />   | <br />    |
| VB140\~VB143 | HMI only        | <br />                      | U1\_VD\_PumpSpeed\_Cutoff\@140                                     | <br />                                                   | <br />   | <br />    |
| VB144\~VB147 | REAL/DWORD (4B) | FC0,FC10                    | U1\_VD\_T\_Default\@144                                            | VD\_T\_Default 首轮配液总时长默认值(s)                             | 🔴 **是** | <br />    |
| VB148\~VB151 | REAL/DWORD (4B) | FC11,FC16,FC40              | U1\_VD\_Available\@150                                             | VD\_CycleSetpoint(min)                                   | 🔴 **是** | <br />    |
| VB152\~VB155 | REAL/DWORD (4B) | FC11,FC16,FC40              | U1\_VD\_Corr\_Needed\@154                                          | VD\_CycleSetpoint(min)                                   | 🔴 **是** | <br />    |
| VB156\~VB159 | REAL/DWORD (4B) | FC11,FC16,FC40              | <br />                                                             | VD\_S2\_Target                                           | 🔴 **是** | <br />    |
| VB160\~VB163 | REAL/DWORD (4B) | FC40                        | <br />                                                             | VD158 : VD\_Delta           缺口 = Needed - Available(s)   | <br />   | <br />    |
| VB164\~VB167 | REAL/DWORD (4B) | FC40                        | <br />                                                             | VD162 : VD\_Layer0\_Quota    第0层额度(静止等候可压缩量)             | <br />   | <br />    |
| VB168\~VB171 | REAL/DWORD (4B) | FC40                        | <br />                                                             | VD166 : VD\_Layer1\_Quota    第1层额度(S2可压缩量)               | <br />   | <br />    |
| VB172\~VB175 | REAL/DWORD (4B) | FC11,FC40                   | U1\_VD\_S3\_Estimate\@174                                          | VD170 : VD\_Layer2\_Quota    第2层额度(周期可顺延量,s)             | 🟡 多FC共享 | <br />    |
| VB176\~VB179 | REAL/DWORD (4B) | FC0,FC11,FC15,FC16          | U1\_VD\_S5\_Elapsed\@178                                           | + VD\_S3\_Estimate                                       | 🔴 **是** | <br />    |
| VB180\~VB183 | REAL/DWORD (4B) | FC0,FC11,FC15,FC16,FC40     | <br />                                                             | VD\_S5\_Elapsed=0                                        | 🔴 **是** | <br />    |
| VB184\~VB187 | REAL/DWORD (4B) | FC0,FC11,FC16,FC40          | <br />                                                             | VW184 : VW\_Corr\_Result     纠偏结果(FC40输出)                | 🔴 **是** | <br />    |
| VB188\~VB191 | REAL/DWORD (4B) | FC0                         | <br />                                                             | VD186 : VD\_RTC\_Now\_Sec    当前RTC转换总秒数(BCD转秒)           | <br />   | <br />    |
| VB192\~VB195 | REAL/DWORD (4B) | FC0                         | <br />                                                             | VD190 : VD\_DT10\_Sec       DT10转换总秒数(BCD转秒)             | <br />   | <br />    |
| VB196\~VB199 | REAL/DWORD (4B) | FC0                         | <br />                                                             | VD194 : VD\_RTC\_DT\_Diff    RTC与DT10秒数差                 | <br />   | <br />    |
| VB204\~VB207 | WORD (2B)       | FC13,FC21                   | <br />                                                             | VW204 : MB\_Pump\_Aspirate 抽液步数缓冲(映射40006)               | 🔴 **是** | <br />    |
| VB220\~VB223 | WORD (2B)       | FC4                         | <br />                                                             | 任务2成功处理: VW410->VW222, 成功计数, 清失败计数                       | <br />   | <br />    |
| VB224\~VB227 | WORD (2B)       | FC0,FC12,FC13,FC4           | <br />                                                             | 清S3子状态                                                   | 🔴 **是** | <br />    |
| VB228\~VB231 | WORD (2B)       | FC0,FC13,FC21,FC4           | <br />                                                             | 清写数据                                                     | 🔴 **是** | <br />    |
| VB232\~VB235 | REAL/DWORD (4B) | FC0,FC13,FC21,FC4           | <br />                                                             | 清写目标地址                                                   | 🔴 **是** | <br />    |
| VB248\~VB251 | REAL/DWORD (4B) | FC0,FC11                    | <br />                                                             | 注意:VW250/VW252与HMI参数VD250重叠,已迁移到VW290/VW292/VW294/VW296  | 🔴 **是** | <br />    |
| VB252\~VB255 | REAL/DWORD (4B) | FC11,FC12,FC14              | <br />                                                             | VD250 : 目标进水量(HMI设定)                                     | 🔴 **是** | <br />    |
| VB260\~VB263 | WORD (2B)       | FC0,FC11,FC15,FC19,FC30 等7  | <br />                                                             | 保险: 即使冷启动,VB260\~VB275可能残留断电前状态,                         | 🔴 **是** | <br />    |
| VB264\~VB267 | WORD (2B)       | FC11,FC17,FC30,FC32         | <br />                                                             | VW264 : Diag\_State\_C  阀C诊断子状态                          | 🔴 **是** | <br />    |
| VB268\~VB271 | WORD (2B)       | FC15,FC17,FC31,FC32         | <br />                                                             | VW268 : Diag\_Result\_B    阀B诊断结果(0/1/2)                 | 🔴 **是** | <br />    |
| VB272\~VB275 | WORD (2B)       | FC0,FC15,FC19,FC31,OB1      | <br />                                                             | PT=VD\_Timeout\_ValveB(VD362)×10                         | 🔴 **是** | <br />    |
| VB276\~VB279 | WORD (2B)       | FC11,FC17,FC30,FC32         | <br />                                                             | VW276 : VD\_Timeout\_ValveC×10 转换值(供FC32用)               | 🔴 **是** | <br />    |
| VB280\~VB283 | WORD (2B)       | FC11,FC12,FC30              | <br />                                                             | VW280 : VD\_Delay\_ValveA\_Verify×10 转换值(供FC30的T51用)     | 🔴 **是** | <br />    |
| VB284\~VB287 | WORD (2B)       | FC12,FC15                   | <br />                                                             | 2. v9.4更新: 取消潜水泵1/2流量开关及超时保护(T44/T45/VW282/VW284/VD344不  | 🟡 多FC共享 | <br />    |
| VB288\~VB291 | WORD (2B)       | FC0,FC4                     | <br />                                                             | 轮询计数器=0(任务0)                                             | 🔴 **是** | <br />    |
| VB292\~VB295 | WORD (2B)       | FC0,FC4                     | <br />                                                             | 注意:VW250/VW252与HMI参数VD250重叠,已迁移到VW290/VW292/VW294/VW296  | 🔴 **是** | <br />    |
| VB296\~VB299 | WORD (2B)       | FC0,FC4                     | <br />                                                             | 注意:VW250/VW252与HMI参数VD250重叠,已迁移到VW290/VW292/VW294/VW296  | 🔴 **是** | <br />    |
| VB300\~VB303 | WORD (2B)       | FC0                         | <br />                                                             | VB300\~VB303清零(报警字)                                      | 🔴 **是** | <br />    |
| VB304\~VB307 | BYTE (1B)       | OB1                         | <br />                                                             | 系统总状态计算 → VB305                                          | <br />   | <br />    |
| VB308\~VB311 | REAL/DWORD (4B) | FC30                        | U1\_VD\_FlowMeter\_CloseSnapshot\@308                              | VD308 : VD\_FlowMeter\_CloseSnapshot  阀A关阀瞬间流量计快照        | <br />   | <br />    |
| VB312\~VB315 | REAL/DWORD (4B) | FC30                        | U1\_VD\_LeakDiff\@312                                              | VD312 : VD\_FlowMeter\_CloseDelta     阀A关阀后流量计差值         | <br />   | <br />    |
| VB316\~VB319 | REAL/DWORD (4B) | FC0,FC30                    | U1\_VD\_TargetInletVolume\@316                                     | 目标进水量(L,默认10L)                                           | 🔴 **是** | <br />    |
| VB320\~VB323 | REAL/DWORD (4B) | FC11                        | <br />                                                             | <br />                                                   | <br />   | <br />    |
| VB324\~VB327 | REAL/DWORD (4B) | FC15                        | <br />                                                             | <br />                                                   | <br />   | <br />    |
| VB328\~VB331 | REAL/DWORD (4B) | FC17                        | U1\_VD\_Timeout\_ValveC\_x10\@328                                  | <br />                                                   | <br />   | <br />    |
| VB332\~VB335 | REAL/DWORD (4B) | FC11                        | <br />                                                             | VD332 : VD358运算中间变量(避免修改HMI参数VD358)                      | <br />   | <br />    |
| VB336\~VB339 | REAL/DWORD (4B) | FC12                        | <br />                                                             | VD336 : VD120运算中间变量(避免修改VD\_S2\_Target)                  | <br />   | <br />    |
| VB340\~VB343 | REAL/DWORD (4B) | FC14                        | <br />                                                             | VD340 : VD124运算中间变量(避免修改VD\_RestTime\_Target)            | <br />   | <br />    |
| VB344\~VB347 | REAL/DWORD (4B) | FC13                        | <br />                                                             | VD346 : 运算中间变量(避免污染HMI设定区)                               | <br />   | <br />    |
| VB348\~VB351 | REAL/DWORD (4B) | FC0,FC13,FC21               | U1\_VD\_StepResolution\@350                                        | VD346 : 运算中间变量(避免污染HMI设定区)                               | 🔴 **是** | <br />    |
| VB352\~VB355 | REAL/DWORD (4B) | FC0,FC11,FC13,FC16,FC21     | U1\_VD\_CycleSetpoint\@354                                         | VD\_StepResolution                                       | 🔴 **是** | ✅ 是       |
| VB356\~VB359 | REAL/DWORD (4B) | FC0,FC11,FC16               | U1\_VD\_Timeout\_ValveA\@358                                       | VD\_CycleSetpoint 换水周期(min)                              | 🔴 **是** | ✅ 是       |
| VB360\~VB363 | REAL/DWORD (4B) | FC0,FC11,FC15,FC31          | U1\_VD\_Timeout\_ValveB\@362                                       | VD\_Timeout\_ValveA 阀A开/关到位超时(s)                         | 🔴 **是** | ✅ 是       |
| VB364\~VB367 | REAL/DWORD (4B) | FC0,FC11,FC15,FC16,FC18 等6  | U1\_VD\_ExpTotal\_Flow\@364 U1\_VD\_ExperimentDuration\_Accum\@366 | VD\_Timeout\_ValveB 阀B开/关到位超时(s)                         | 🔴 **是** | ✅ 是       |
| VB368\~VB371 | REAL/DWORD (4B) | FC13,FC16                   | U1\_VD\_Vol\_Target\@370                                           | VD\_ExperimentDuration\_Accum(VD366)每分钟+1                | 🟡 多FC共享 | ✅ 是       |
| VB372\~VB375 | REAL/DWORD (4B) | FC0,FC13,FC18               | U1\_VD\_Remaining\_Vol\@372                                        | VD\_Remaining\_Vol=0(µL)                                 | 🔴 **是** | ✅ 是       |
| VB376\~VB379 | REAL/DWORD (4B) | FC0,FC13,FC18,FC4           | U1\_VD\_Dosed\_Volume\_Total\@378                                  | 流量计降级值清零                                                 | 🔴 **是** | <br />    |
| VB380\~VB383 | REAL/DWORD (4B) | FC0,FC11,FC13,FC15,FC16 等8  | U1\_VD\_S4Wait\_Time\@380 U1\_VD\_S4WaitTimeout\@382               | 清MBUS\_MSG Error(流量计)                                    | 🔴 **是** | <br />    |
| VB384\~VB387 | REAL/DWORD (4B) | FC0,FC15,FC21               | U1\_VD\_ManualDose\_Target\@384                                    | VD\_S4WaitTimeout S4等待超时阈值(s,默认30min)                    | 🔴 **是** | ⚠️ MBUS重叠 |
| VB388\~VB391 | WORD (2B)       | FC0,FC21,OB1                | <br />                                                             | VW\_ManualDose\_Mode 手动模式(0=单次,1=循环)                     | 🔴 **是** | ✅ 是       |
| VB392\~VB395 | REAL/DWORD (4B) | FC0,FC21                    | U1\_VD\_ManualDose\_Dosed\@392                                     | 手动累计加药量=0(内部)                                            | 🔴 **是** | ✅ 是       |
| VB396\~VB399 | REAL/DWORD (4B) | FC0,FC21                    | U1\_VD\_ManualDose\_Remaining\@396                                 | 手动剩余加药量=0(内部)                                            | 🔴 **是** | ✅ 是       |
| VB408\~VB411 | REAL/DWORD (4B) | FC4                         | <br />                                                             | 任务0成功处理: VW410->VW4, 成功计数, 清失败计数                         | 🔴 **是** | <br />    |
| VB412\~VB415 | REAL/DWORD (4B) | FC4                         | <br />                                                             | 任务1成功处理: VD410->VD86, 成功计数, 清失败计数                        | <br />   | <br />    |
| VB416\~VB455 | -      | 无                              | <br />                                                             | 空闲区（FC21 计数器迁走后，原值 VW516\~VW548 已迁出到 VB550\~VB583）         | ❌       | ❌        |
| VB456\~VB459 | BYTE/WORD/REAL | FC0, MCGS                    | U1\_UD\_Flag\@456                                                  | **用户默认存储区**: VB456=用户默认有效标志(0=出厂/1=自定义), 占位4B  | ❌       | ❌        |
| VB460\~VB523 | REAL/DWORD (4B) | FC0, MCGS                    | U1\_UD\_VD24\_ExpTarget\@460 ~ U1\_UD\_VD370\_VolTarget\@520        | **用户默认存储区**: VD460~VD520 共16个REAL, 存18个工艺参数的用户默认值      | ❌       | ❌        |
| VB524\~VB527 | REAL/DWORD (4B) | FC0, MCGS                    | U1\_UD\_VD448\_WaitTimeout\@524                                    | **用户默认存储区**: VD524=S4等待超时阈值用户默认                         | ❌       | ❌        |
| VB528\~VB531 | REAL/DWORD (4B) | FC0, MCGS                    | U1\_UD\_VD452\_ManualDose\@528                                    | **用户默认存储区**: VD528=手动总加药量用户默认                           | ❌       | ❌        |
| VB532\~VB533 | WORD (2B)       | FC0, MCGS                    | U1\_UD\_VW388\_Mode\@532                                           | **用户默认存储区**: VW532=手动模式用户默认(0=单次/1=循环)                | ❌       | ❌        |
| VB536\~VB536 | BYTE (1B)       | FC0, MCGS                    | U1\_UD\_V200\_0\_AckMode\@536.0                                    | **用户默认存储区**: V536.0=报警确认模式用户默认(bit0)                    | ❌       | ❌        |
| VB540\~VB548 | WORD (2B)       | 无                              | <br />                                                             | 空闲（原FC21计数器旧位置，已迁出到 VB550\~VB582）                        | ❌       | ❌        |
| VB550\~VB551 | WORD (2B)       | FC0,FC21                    | <br />                                                             | FC21监控计数器(新位置,上电MOVW 0清零,运行INCW累加)                   | ❌       | ❌        |
| VB552\~VB553 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB554\~VB555 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB556\~VB557 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB558\~VB559 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB560\~VB561 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB562\~VB563 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB564\~VB565 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB566\~VB567 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB568\~VB569 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB570\~VB571 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB572\~VB573 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB574\~VB575 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB576\~VB577 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB578\~VB579 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB580\~VB581 | WORD (2B)       | FC0,FC21                    | <br />                                                             | <br />                                                   | ❌       | ❌        |
| VB582\~VB583 | WORD (2B)       | FC0,FC21                    | <br />                                                             | FC21最后一个计数器                                       | ❌       | ❌        |
| VB600\~VB603 | WORD (2B)       | FC0                         | <br />                                                             | VB600\~VB885清零(Modbus库存储区)                               | 🔴 **是** | <br />    |
| VB504\~VB507 | WORD (2B)       | FC0,FC4                     | <br />                                                             | 注意:VW250/VW252与HMI参数VD250重叠,已迁移到VW290/VW292/VW294/VW296  | 🔴 **是** | <br />    |
| VB508\~VB511 | WORD (2B)       | FC21,FC3,FC4                | <br />                                                             | 单元编号=1(本PLC)                                             | 🔴 **是** | <br />    |
| VB512\~VB515 | WORD (2B)       | FC4                         | <br />                                                             | <br />                                                   | <br />   | <br />    |

| VB600\~VB603 | WORD (2B)       | FC0                         | <br />                                                             | VB600\~VB885清零(Modbus库存储区)                               | 🔴 **是** | <br />    |
| VB884\~VB887 | BYTE (1B)       | FC0                         | <br />                                                             | ★ 2026-09-06新增(FC99调试经验): 清空Modbus库存储区VB600\~VB885       | <br />   | <br />    |
| VB900\~VB903 | BYTE (1B)       | FC0,FC15,FC22               | <br />                                                             | RTC   : VB900\~VB907       READ\_RTC读取结果(BCD)            | 🔴 **是** | <br />    |
| VB904\~VB907 | BYTE (1B)       | FC0,FC15,FC22               | <br />                                                             | 分>59                                                     | 🔴 **是** | <br />    |
| VB908\~VB908 | BYTE (1B)       | FC15                        | <br />                                                             | <br />                                                   | <br />   | <br />    |

***

## 二、真正的物理冲突区（按严重程度排序）

> **注意**：本章由 Python 静态分析器 + 人工核实双重确认。判定标准：**同一字节被两个不同的 4 字节起始地址占用**（不是多 FC 读同一个 HMI 参数的正常共享）。

***

### 🔴 P0-1：VB10\~VB17（8字节）— VD10/VD14 浓度参数 vs DT10 RTC 时间戳

| 字节         | 起始地址 | 大小 | 类型   | 来源FC     | 用途                        |
| ---------- | ---- | -- | ---- | -------- | ------------------------- |
| VB10\~VB13 | VD10 | 4B | REAL | FC0/FC13 | **目标浓度 (HMI 参数)**         |
| VB10\~VB17 | DT10 | 8B | BCD  | FC0/FC15 | **下缸变满时间戳**（FC15 S4 完成时写） |
| VB14\~VB17 | VD14 | 4B | REAL | FC0/FC13 | **母液浓度 (HMI 参数)**         |

**根因**：2026 年 7 月 VD 参数区重排时，浓度参数先被分配到 VD10/VD14，后来有人加了 DT10（FC15 S4 完成写 RTC），选地址时没查冲突。两者物理地址完全重叠。

**破坏链**：

1. 冷启动 FC0 → `MOVR 5.0, VD10` / `MOVR 1000.0, VD14` 初始化浓度 ✅
2. HMI 运行 → 用户可设置浓度值 ✅
3. 状态机进 S4 且下缸满 → FC15 写 `DT10 = READ_RTC()` → **VB10\~VB17 全被 RTC BCD 覆盖** ❌
4. FC13 S3 加药时读 `VD10 × VD90 / VD14` → **分子分母是 RTC 时间戳的垃圾值** ❌
5. 但冷启动又重初始化了 → 现场没暴露，是**隐藏炸弹**

**修复方案（已对齐 2026-09-12）**：
1. ❌ **删除 VD10 目标浓度** 和 **VD14 母液浓度**（HMI 参数，简化为用户直接输入加药量）
2. ✅ **DT10 RTC 原地保留**（VB10\~VB17 8 字节现在完全独占，安全了！）
3. FC0 冷启动移除 MOVR 5.0, VD10 / MOVR 1000.0, VD14
4. FC13 加药公式去掉 *R VD10 /R VD14，改成直接用 VD370（目标加药量由用户输入）

***

### 🔴 P0-2：VB378\~VB383（6字节）— MBUS\_MSG Error vs 用户变量（**最严重**）

| 字节           | 起始地址  | 大小 | 类型   | 来源FC           | 用途                                   |
| ------------ | ----- | -- | ---- | -------------- | ------------------------------------ |
| VB378        | VB378 | 1B | BYTE | FC0/FC4        | **MBUS\_CTRL Error**                 |
| VB378\~VB381 | VD378 | 4B | REAL | FC0/FC13/FC18  | **累计加药量 Dosed\_Volume\_Total (HMI)** |
| VB379        | VB379 | 1B | BYTE | FC0/FC4        | **MBUS\_MSG 任务0 Error**              |
| VB380        | VB380 | 1B | BYTE | FC0/FC4        | **MBUS\_MSG 任务2 Error**              |
| VB380\~VB383 | VD380 | 4B | REAL | FC11/FC15/FC16 | **S4Wait\_Time 内部计算**                |
| VB380\~VB381 | VW380 | 2B | WORD | FC11/FC15/FC17 | **定时器暂存**                            |
| VB381        | VB381 | 1B | BYTE | FC0/FC4        | **MBUS\_MSG 任务1 Error**              |
| VB382        | VB382 | 1B | BYTE | FC0/FC4        | **MBUS\_MSG 任务3 Error**              |
| VB382\~VB385 | VD382 | 4B | REAL | FC0/FC15       | **S4WaitTimeout (HMI 参数)**           |
| VB383        | VB383 | 1B | BYTE | FC0/FC4        | **MBUS\_MSG 任务4 Error**              |

**根因**：FC4 的 6 个 MBUS Error 字节写死了 VB378\~VB383，后来 v1.2 加 S4 等待计时时直接用了 VD380/VD382，没查 MBUS Error 在哪。

**破坏链**（现场确认）：

1. HMI 写入 `VD382 = 1800.0`（S4 等 30 分钟）→ 内存 `[0x44, 0xE1, 0x00, 0x00]`
2. MBUS\_MSG 轮询完成 → `VB382 = 0x00`（Error=0，正常）、`VB383 = 0x00`
3. VD382 的 IEEE-754 浮点指数位（bit30\~23 在 VB382 的高 7 位）被清零 → 值变成 **4.23E-37**
4. FC15 比较 `VD_S4Wait_Time >= VD382(1800)` 永远不触发 → S4 超时报警失效
5. MBUS\_MSG 每 \~300ms 轮询一次 → **每秒污染 VD382 3\~4 次**，完全不可用

**修复方案（已对齐 2026-09-12）**：MBUS Error 原地不动（VB378\~VB383 6 字节完全归 FC4 使用）。把所有冲突变量迁到 VB414\~VB499 大空闲区（不复用任何已有变量）：

| 变量 | 旧地址 | 新地址 | 新字节范围 | 断电保持 |
|------|--------|--------|-----------|---------|
| VD_Dosed\_Volume\_Total 累计加药量 | VD378 | **VD440** | VB440\~VB443 | 否 |
| VD_S4Wait\_Time S4等待时长 | VD380 | **VD444** | VB444\~VB447 | 否 |
| VW380 定时器暂存 | VW380 | **VB414** | VB414\~VB447 | 否 |
| VD_S4WaitTimeout S4等待超时(HMI) | VD382 | **VD448** | VB448\~VB451 | **是（新增）** |
| VD_ManualDose\_Target 手动剂量(HMI) | VD384 | **VD452** | VB452\~VB455 | **是（新增）** |

> **为什么不复用 VD370？** VD370 是 VD_Vol\_Target（FC13 S3 用的目标加药量），虽然 S3 结束后到下一次 S3 是空窗，但不留隐患。全部迁到空闲区。

> **为什么不迁 MBUS Error？** 你明确要求 MBUS Error 原地独占，FC4 的代码一行不动。

> **VD384 的 Bug A 与迁出独立**：先修 Bug A（FC15 L77\~79 用 VD324 替代 VD384），VD384 再迁到 VD452（只影响 FC0/FC21）。

***

### 🔴 P0-3：FC15 Bug A — 用 VD384(ManualDose\_Target) 当临时变量

**位置**：`plc/stl/FC15_State_S4_Transfer.stl` NETWORK 1, L77-79

```stl
// 当前错误代码:
MOVR   VD382, VD384     // VD384 = ManualDose_Target (HMI参数!)
*R     10.0, VD384
ROUND  VD384, AC0
MOVW   AC0, VW286       // 结果存 VW286 ← 这才是应该操作的变量
```

**破坏链**：状态机每次进 S4 时计算 T61 PT 值，**顺便覆盖了 VD384**（ManualDose\_Target）。然后 FC21 启动手动注射泵时 `MOVR VD384, VD396` 拿"剩余药量"→ **拿到的是 VD382×10 ≈ 18000.0 这种垃圾值**。

**修复方案**（已确认零冲突）：用 **VD324**（FC15 本 NETWORK 上半段已经在用的临时变量）：

```stl
MOVR   VD382, VD324     // VD324 在本 NETWORK L53 算过 VD362×10，完全空闲可复用
*R     10.0, VD324
ROUND  VD324, AC0
MOVW   AC0, VW286
```

**改动量**：3 行 STL 代码。

***

### 🟢 已修复的历史冲突（仅登记，无需再改）

| 冲突                            | 原地址          | 修复日期                 | 迁移到            |
| ----------------------------- | ------------ | -------------------- | -------------- |
| 手动控制命令位 V2.4\~V3.7 vs VW2 状态机 | VB2\~VB3     | 2026-09-03 (v1.8)    | V306.0\~V307.3 |
| VW250/VW252 vs HMI 参数 VD250   | VB250\~VB253 | 2026-07-18 (AQEX-36) | VW290\~VB296   |

***

### ⚪ 架构性质的"冲突"（合理设计，无需修复）

下列字节在 Python 静态分析中被标记，但经人工核实为**有意设计**：

| 区域           | 说明                                                                                                                                                                           |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| VB260\~VB275 | 阀门诊断：FC30/31/32 用 `VW260×10` 算 T50 PT（WORD），同时 FC11/15/17 用 `VB260` 存诊断子状态（BYTE）。VW260 = VB260 + VB261，FC 们**只用高字节 VB260**（PT 值低字节 VB261=0），子状态存在 VB261 不影响 PT。              |
| VB364\~VB365 | VD362(4B) 的高 2 字节覆盖 VD364(4B) 的低 2 字节。但 VD362(ValveB Timeout) 是**秒级整数值**（范围 30\~300），在 WORD 范围内，高 2 字节 = 0。VD364(ExpTotal\_Flow) 从 0 开始每分钟累加，低 2 字节 = 小数部分（L）。两者**低字节互不干扰**。 |
| VB410\~VB413 | FC4 Modbus 统一缓冲 VW410 + VD410 同时使用。FC4 内部：VW410 = 成功计数（每次 MBUS\_MSG 完加 1），VD410 = 任务1 成功后的流量计读数搬运（VD410→VD86）。**任务互斥**，不会同时写。                                                |

***

## 三、最大连续空闲区（可分配给新变量）

> 注意：S7-200 SMART V 区最大 1024 字节，下列空闲区均已排除 STL 引用和 CSV 导入。

| 起始    | 结束    | 字节数 | 可放REAL数 | 对齐?    | 推荐用途         |
| ----- | ----- | --- | ------- | ------ | ------------ |
| VB 18 | VB 23 | 6   | 1       | ⚠️ 非对齐 | 太小，慎分配       |
| VB 48 | VB 53 | 6   | 1       | ✅ 4字节  | 太小，慎分配       |
| VB 98 | VB101 | 4   | 1       | ⚠️ 非对齐 | 太小，慎分配       |
| VB200 | VB203 | 4   | 1       | ✅ 4字节  | 太小，慎分配       |
| VB208 | VB221 | 14  | 3       | ✅ 4字节  | 可用，但别浪费      |
| VB236 | VB249 | 14  | 3       | ✅ 4字节  | 可用，但别浪费      |
| VB256 | VB259 | 4   | 1       | ✅ 4字节  | 太小，慎分配       |
| VB400 | VB409 | 10  | 2       | ✅ 4字节  | 可用，但别浪费      |
| VB414 | VB499 | 86  | 21      | ⚠️ 非对齐 | ⭐ 大区域，适合批量参数 |
| VB550 | VB599 | 50  | 12      | ⚠️ 非对齐 | ⭐ 大区域，适合批量参数 |
| VB602 | VB884 | 283 | 70      | ⚠️ 非对齐 | ⭐ 大区域，适合批量参数 |
| VB886 | VB899 | 14  | 3       | ⚠️ 非对齐 | 可用，但别浪费      |

***

## 四、按功能分组摘要

| 区域                   | 地址范围             | 大小      | 功能                                                          | HMI可读    | HMI可写         | 断电保持          |
| -------------------- | ---------------- | ------- | ----------------------------------------------------------- | -------- | ------------- | ------------- |
| 状态机核心                | VB0\~VB9         | 10B     | V0.x命令位、VW2状态、VW4泵状态、VW6报警                                  | ✅        | ❌(仅V306\~307) | ⚠️V0需清        |
| RTC时间戳               | **VB10\~VB17**   | 8B      | **⚠️与VD10/VD14重叠！DT10下缸满时间**                                | ❌        | ❌             | ❌             |
| 实验参数HMI              | **VD24\~VD70**   | \~46B   | 实验总时长/预循环/静止/超时/延时                                          | ✅        | ✅             | ✅(选填)         |
| 流量计运算                | VD82\~VD94       | 16B     | 当前进水量快照/差值                                                  | ✅(显示)    | ❌             | ❌             |
| 注射泵步数                | VD102\~VD108     | 12B     | 本次目标步数                                                      | ❌        | ❌             | ❌             |
| T/S6默认值              | VD108\~VD119     | 12B     | FC10状态机初始化参数                                                | ❌        | ❌             | ❌             |
| 状态机目标                | VD120\~VD131     | 12B     | S2/S3.5目标值(FC40调节输出)                                        | ❌        | ❌             | ❌             |
| 周期延伸计算               | VD128\~VD174     | 48B     | FC40内部算法变量                                                  | ❌        | ❌             | ❌             |
| VD186\~VD198         | VD186\~VB199     | 16B     | RTC秒数差计算                                                    | ❌        | ❌             | ❌             |
| Modbus缓冲区            | VB204\~VB235     | 32B     | 注射泵步缓冲/写命令缓冲                                                | ❌        | ❌             | ❌             |
| 诊断暂存                 | VB260\~VB286     | 28B     | 阀A/B/C诊断状态机暂存                                               | ❌        | ❌             | ❌             |
| Modbus计数器            | VB290\~VB299     | 10B     | FC4轮询成功/失败计数                                                | ❌        | ❌             | ❌             |
| 系统状态字                | VB300\~VB305     | 6B      | 报警字/系统总状态                                                   | ✅(显示)    | ❌             | ❌             |
| 阀门诊断计算               | VD308\~VD316     | 12B     | 关阀快照/差值/目标进水量                                               | ✅(VD316) | ⚠️(TD027)     | ❌             |
| 运算中间变量               | VD320\~VD349     | 32B     | FC11/12/14/15/17 临时REAL                                     | ❌        | ❌             | ❌             |
| **HMI参数(AQEX-36迁移)** | **VD350\~VD374** | **24B** | **步分辨率/周期/超时(阀A/B/C)/累计**                                   | **✅**    | **✅**         | **✅**         |
| 内部计算                 | VD370\~VD377     | 8B      | VD\_Vol\_Target/Remaining/降级值                               | ❌        | ❌             | ❌             |
| **MBUS Error区**      | **VB378\~VB383** | **6B**  | **MBUS\_CTRL Error + 4×MBUS\_MSG Error**                    | ✅(维护页)   | ❌             | ❌             |
| **冲突区(待迁出)**         | **VD380\~VD387** | **8B**  | **S4Wait\_Time/S4WaitTimeout(HMI)/ManualDose\_Target(HMI)** | **✅**    | **✅**         | **⚠️被MBUS覆盖** |
| 手动注射泵                | VW388\~VD399     | 12B     | 模式/子状态/累计/剩余                                                | ✅(状态)    | ❌             | ✅(子状态)        |
| Modbus统一缓冲           | VB410\~VB413     | 4B      | FC4 DataPtr (40001)                                         | ❌        | ❌             | ❌             |
| **RTC搬移候选**          | **VB460\~VB467** | **8B**  | **当前空闲 → 迁 DT10 到此区**                                       | ❌        | ❌             | ❌             |
| **加药量输入候选**          | **VB468\~VB471** | **4B**  | **当前空闲 → 用户直接输入加药量 REAL**                                   | ✅        | ✅             | ✅             |
| 报警日志缓冲               | VB500\~VB548     | \~48B   | FC3 报警记录（原FC21计数器已迁出到 VB550\~VB583）                   | ✅(维护页)   | ❌             | ❌             |
| Modbus库存储区           | VB600\~VB885     | 286B    | MBUS\_CTRL/MSG 内部使用（清零初始化）                                  | ❌        | ❌             | ❌             |
| READ\_RTC结果          | VB900\~VB908     | 9B      | RTC读取结果(BCD)，FC15/FC22用                                     | ❌        | ❌             | ❌             |

***

## 五、S7-200 SMART V 区容量限制提醒

| 区域    | 最大容量                  | 当前已用     | 备注          |
| ----- | --------------------- | -------- | ----------- |
| V区    | 1024 字节 (VB0\~VB1023) | \~890 字节 | 已用 87%，接近上限 |
| M区    | 256 字节 (M0\~M255)     | \~20 字节  | 充裕          |
| T区    | 256 个定时器              | \~50 个   | 充裕          |
| C区    | 256 个计数器              | 5 个      | 充裕          |
| AI/AQ | 各 128 字               | 未使用模拟量   | 充裕          |

> **⚠️ 警告**: V区已用 \~890/1023 字节 (87%)。再新增参数请优先考虑 M 区（如果不要求断电保持），或精简不常用的 Modbus 缓冲/报警日志区。

***

## 六、寄存器分配规范（防止再冲突）

1. **REAL 必须 4 字节对齐**：VD 地址必须是 4 的倍数（0,4,8,12,...），否则 S7-200 SMART 可能读写错误。
2. **先查本文件再分配**：新增变量前，先在本文件第一节查目标地址是否被占用。
3. **STL 代码里写注释**：每个 VD/VW/VB 声明后必须加 `// 用途说明`。
4. **HMI 参数必须同时更新 CSV 和地址表**：改 PLC 地址时 MCGS CSV 通道地址也要同步。
5. **断电保持配置**：新增需要断电保持的 HMI 参数，必须在 STEP7 系统块里配断电保持，并在本文件标注。
6. **禁止在 FC4 MBUS Error 区写用户变量**：VB378\~VB383 是 FC4 的 6 个 Error 输出，严禁分配给用户。
7. **RTC/READ\_RTC 结果区禁止**：VB900\~VB908 是 READ\_RTC 结果，FC15/FC22 会覆盖。
8. **Modbus 库存储区禁止**：VB600\~VB885 是 MBUS\_CTRL/MSG 内部使用，FC0 冷启动会 FILL 0 清零。

***

## 八、其他寄存器区扫描结果（M / T / C / I / Q / AC）

> **扫描方法**: 2026-09-12 追加扫描，覆盖 23 个 STL 文件中除 V 区外的所有寄存器引用。
> **关键结论**: **V 区是唯一存在"类型级物理重叠"风险的区域**。其余区域因架构设计避免了字节覆盖问题。

### 为什么只有 V 区会出"物理重叠"？

```
V 区（会重叠）：
┌──────────────────────────────────────────────────────────┐
│ VB10  VB11  VB12  VB13  VB14  VB15  VB16  VB17          │
├──────────────┤                                             │
│   VD10 (4B REAL)    ← FC13 把 VB10~13 当"浓度"读          │
│               ├───────────────┤                           │
│               │ VD14 (4B REAL)│   ← FC13 把 VB14~17 当"母液浓度"读
├──────────────────────────────────────────────────────────┤
│                  DT10 (8B BCD)    ← FC15 把 VB10~17 当"时间戳"写
└──────────────────────────────────────────────────────────┘
→ 三者物理地址完全重叠！写 DT10 直接覆盖 VD10/VD14！

对比 M 区（不会重叠）：
┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
│M10.0 │M10.1 │M10.2 │M10.3 │M10.4 │M10.5 │M10.6 │M10.7 │
│MBUS  │MBUS  │S1首  │预留  │(不用) │流量计│预规划 │预规划 │
│Done0 │Done1 │次标志│      │      │降级  │触发  │活跃  │
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘
→ 每个 Mxx.x 是独立的位对象，互不干扰
→ 即使 FC0 清 M10.0，FC4 也不会丢失 M10.1 的值

对比 T 区（不会重叠）：
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ T37     │ T38     │ T39     │ T61     │ ...     │
│ S1计时  │ S2计时  │ S3.5计时│ S4等待  │         │
└─────────┴─────────┴─────────┴─────────┴─────────┘
→ 每个 T 号是独立的定时器对象（含 PT/ET/Q 三个内部变量）
→ 不会出现"写 T38 的 PT 不小心改了 T37 的 ET"
```

**根本原因**: V 区支持多类型寻址（VB=1字节、VW=2字节、VD=4字节），不同类型声明就会互相覆盖底层字节。这是 S7-200 SMART / S7-300 / S7-400 / S7-1200 / S7-1500 全系列的架构特性。

***

### 8.1 M 区（内部标志位 M0 \~ M255）— ✅ 干净，无冲突

**已使用范围**: M10.0 \~ M15.4（共约 44 个位，6 个字节 MB10\~MB15）
**最大容量**: 256 字节（2048 个位）
**占用率**: 约 **3%**，非常充裕

| 地址           | 位     | 类型  | 引用FC                       | 用途                          | 是否冲突   |
| ------------ | ----- | --- | -------------------------- | --------------------------- | ------ |
| M10.0        | Bit   | 标志位 | FC0/FC4                    | MBUS\_MSG 任务0 Done（注射泵状态）   | ❌ 正常共享 |
| M10.1        | Bit   | 标志位 | FC4                        | MBUS\_MSG 任务1 Done（注射泵位置）   | ❌      |
| M10.2        | Bit   | 标志位 | FC1/FC11/OB1               | S1 首次进入标志                   | ❌ 正常共享 |
| M10.4        | Bit   | 标志位 | FC15                       | S4 等待 EU（不用上升沿，避免周期切换时丢失）   | ❌      |
| M10.5        | Bit   | 标志位 | FC0                        | 流量计降级标志（连续 5 次 MBUS 失败）     | ❌      |
| M10.6        | Bit   | 标志位 | FC17/FC18                  | 实验未结束标志                     | ❌      |
| M10.7        | Bit   | 标志位 | FC1/FC15/FC16/FC17/FC2/OB1 | 预规划触发标志                     | ❌ 正常共享 |
| M11.0        | Bit   | 标志位 | FC0/FC4                    | MBUS\_CTRL Done（每周期脉冲）      | ❌      |
| M11.1        | Bit   | 标志位 | FC0/FC3                    | 消音标志（声报警锁存复位）               | ❌      |
| M11.2        | Bit   | 标志位 | FC0/FC3                    | 上周期有报警标志（用于消音检测）            | ❌      |
| M11.6        | Bit   | 标志位 | FC0/FC4/FC13/FC21/OB1      | 注射泵写请求（手动/自动互斥）             | ❌ 握手标志 |
| M11.7        | Bit   | 标志位 | FC0/FC4/FC13/FC21          | 注射泵写忙（MBUS 正在执行）            | ❌ 握手标志 |
| M12.0        | Bit   | 标志位 | FC0/FC4/FC13/FC21          | 注射泵写完成（MBUS 写入成功）           | ❌ 握手标志 |
| M12.1        | Bit   | 标志位 | FC0/FC13                   | S3 抽液开始标志                   | ❌      |
| M12.2        | Bit   | 标志位 | FC0/FC13                   | S3 排液开始标志                   | ❌      |
| M13.0\~M13.4 | Bit×5 | 标志位 | FC0/FC20/OB1               | 手动控制锁存（阀/泵手动操作保持）           | ❌ 手动专用 |
| M13.5\~M13.7 | Bit×3 | 标志位 | FC0/FC21/OB1               | 手动注射泵标志                     | ❌ 手动专用 |
| M14.0\~M14.1 | Bit×2 | 标志位 | FC4                        | MBUS\_MSG 任务使能（保留）          | ❌      |
| M15.0\~M15.4 | Bit×5 | 标志位 | FC0/FC4                    | MBUS\_MSG 任务调度（First/EN 边沿） | ❌      |

**结论**: ✅ **无冲突**。每个 M 位是独立对象，不重叠。多 FC 引用同一 M 位属于"正常初始化 + 运行"或"握手标志"模式，不是覆盖。

***

### 8.2 T 区（定时器 T0 \~ T255）— ✅ 干净，无冲突

**已使用范围**: T35 \~ T104（共 **25 个**）
**最大容量**: 256 个
**占用率**: 约 **10%**，充裕

| 地址       | 时基    | 引用FC              | 用途                              | 是否冲突    |
| -------- | ----- | ----------------- | ------------------------------- | ------- |
| T35      | 100ms | FC2               | 安全继电器反馈延时（PT=20，2s）             | ❌       |
| T37      | 100ms | FC11/OB1          | S1 上缸进水计时器（可滚动）                 | ❌ 状态机互斥 |
| T38      | 100ms | FC12              | S2 预循环计时器（PT=VD\_S2\_Target×10） | ❌ 状态机互斥 |
| T39      | 100ms | FC14              | S3.5 静止等候计时器                    | ❌ 状态机互斥 |
| T40      | 100ms | FC15/FC16         | S4 转移计时器                        | ❌ 状态机互斥 |
| T41      | 100ms | FC16              | S5 实验计时器（可滚动）                   | ❌ 状态机互斥 |
| T42      | 100ms | FC17              | S6 排水计时器                        | ❌ 状态机互斥 |
| T44\~T45 | 100ms | FC12              | ⚠️ v9.4 已废弃（注释保留，不运行）           | ❌ 死代码   |
| T47      | 100ms | FC16/FC18         | S5 实验累计计时（60s 周期）               | ❌       |
| T50      | 100ms | FC0/FC19/FC30/OB1 | 阀A诊断计时器                         | ❌ 状态机互斥 |
| T51      | 100ms | FC30              | 阀A关阀后延时验证                       | ❌       |
| T52      | 100ms | FC30              | 开到位无流 2s 确认                     | ❌       |
| T53      | 100ms | FC31              | 阀B开到位超时                         | ❌       |
| T54      | 100ms | FC31              | 阀B流量开关超时                        | ❌       |
| T55      | 100ms | FC0/FC19/FC31/OB1 | 阀B诊断计时器                         | ❌ 状态机互斥 |
| T56\~T57 | 100ms | FC32              | 阀C诊断（超时 + 流量）                   | ❌       |
| T58      | 100ms | FC32              | 阀C关到位超时                         | ❌       |
| T59      | 100ms | FC22              | RTC 校时超时（5 分钟）                  | ❌       |
| T60      | 100ms | FC16              | S5 1 秒脉冲（驱动累计）                  | ❌       |
| T61      | 100ms | FC15              | S4 等待计时器（PT=VD382×10）           | ❌       |
| T62      | 100ms | FC15              | S4 等待计时 1s 脉冲                   | ❌       |
| T102     | 100ms | FC13              | 注射泵运动超时（30s 兜底）                 | ❌       |
| T103     | 100ms | FC0/FC4           | MBUS\_MSG 总超时定时器                | ❌       |
| T104     | 100ms | FC0/FC21          | 手动注射泵回零冷却                       | ❌       |

**结论**: ✅ **无冲突**。每个 T 号是独立的定时器对象（内部含 ET/PT/Q 三个变量），互不影响。多 FC 引用同一 T 号属于"冷启动清 + 状态机运行"模式，**同一时刻只有一个状态 FC 活跃**（VW2 互斥）。

***

### 8.3 C 区（计数器 C0 \~ C255）— ✅ 未使用，空闲

**扫描结果**: **0 个引用**。当前 PLC 逻辑中没有用到任何计数器。
**可用数量**: 256 个，完全空闲。

***

### 8.4 I/Q 区（输入/输出继电器）— ✅ 干净，安全

#### I 区（输入继电器，只读，来自物理传感器/开关）

**已使用范围**: I0.0 \~ I8.5（共 17 个数字量输入位）
**最大容量**: 128 字节（1024 个位）
**占用率**: 约 **1.7%**

| 输入   | 信号名     | 用途                 | 引用FC              |
| ---- | ------- | ------------------ | ----------------- |
| I0.0 | 流量开关A   | 上缸进水管有流=ON         | FC30/FC3          |
| I0.1 | 流量开关B   | 下缸出口有流=ON          | FC31/FC3          |
| I0.2 | 流量开关C   | 排水管有流=ON           | FC32/FC3          |
| I0.3 | 潜水泵1流量  | ⚠️ v9.4 废弃         | FC12/FC19/OB1     |
| I0.4 | 潜水泵2流量  | ⚠️ v9.4 废弃         | FC12/FC3          |
| I0.5 | 液位计A高位  | 上缸漫溢=ON            | FC30/FC3          |
| I0.6 | 液位计A低位  | 上缸空=ON（S0→S1 启动条件） | FC10/FC31/FC3     |
| I0.7 | 液位计B高位  | 下缸漫溢=ON            | FC31/FC3          |
| I1.0 | 液位计B低位  | 下缸空=ON             | FC10/FC32/FC3     |
| I1.1 | 急停按钮    | **急停触发**（常闭，断开=急停） | FC2/FC18/FC19/OB1 |
| I1.2 | 安全继电器FB | 安全继电器反馈（ON=动力断开确认） | FC2/FC19          |
| I8.0 | 阀A开到位   | =ON 阀A完全打开         | FC30/FC3          |
| I8.1 | 阀A关到位   | =ON 阀A完全关闭         | FC30/FC3          |
| I8.2 | 阀B开到位   | =ON                | FC31/FC3          |
| I8.3 | 阀B关到位   | =ON                | FC31/FC3          |
| I8.4 | 阀C开到位   | =ON                | FC32/FC3          |
| I8.5 | 阀C关到位   | =ON                | FC32/FC3          |

**结论**: ✅ I 区无冲突。输入继电器是**只读**的，不会被 PLC 内部覆盖。

#### Q 区（输出继电器，写控制）

**已使用范围**: Q0.0 \~ Q8.7（共 10 个输出位）
**最大容量**: 128 字节（1024 个位）

| 输出         | 信号名     | 用途       | 自动写      | 手动写  | 是否冲突   |
| ---------- | ------- | -------- | -------- | ---- | ------ |
| Q0.0       | 潜水泵1    | 运行=ON    | S2/S3 自动 | 手动控制 | ❌ 互斥保护 |
| Q0.1       | 潜水泵2    | 运行=ON    | S2/S3 自动 | 手动控制 | ❌ 互斥保护 |
| Q0.2       | 阀A      | 打开上水阀    | S1/S4 自动 | 手动控制 | ❌ 互斥保护 |
| Q0.3       | 阀B      | 打开上→下转移阀 | S4 自动    | 手动控制 | ❌ 互斥保护 |
| Q0.4       | 阀C      | 打开排水阀    | S6 自动    | 手动控制 | ❌ 互斥保护 |
| Q0.5       | 上缸NC球阀  | 与阀A配合    | S1 自动    | 手动控制 | ❌ 互斥保护 |
| Q0.6       | 下缸NC球阀  | 与阀C配合    | S6 自动    | 手动控制 | ❌ 互斥保护 |
| Q0.7       | 报警蜂鸣器   | 响=ON     | FC3 统一管理 | —    | ❌ 单独管理 |
| Q8.0\~Q8.7 | DR32 输出 | 报警灯      | FC3 统一管理 | —    | ❌ 单独管理 |

**结论**: ✅ Q 区无冲突。多 FC 写同一 Q 点是**有意设计**，有**手动/自动互斥保护**：

- 自动输出只在 `VW2 ≠ 0`（非 S0 初始化状态）时生效

- 手动控制只在 `VW2 = 0`（S0）时生效

- OB1 每周期清零 QB0/QB8 兜底，防止状态切换时残留

***

### 8.5 AC 区（累加器 AC0 \~ AC3）— ⚠️ 低风险，需注意

**已使用范围**: AC0（11 个 FC），AC1/AC2/AC3 暂未使用
**最大容量**: 4 个累加器（CPU 内部）

**为什么有风险？**

> S7-200 SMART 的累加器 **AC0\~AC3 是 CPU 全局寄存器**，**不随 FC 调用自动保护现场**。如果 FC\_A 正在用 AC0 计算时被 FC\_B 中断，AC0 的值会被覆盖。

| 当前用法                       | 是否安全                                          |
| -------------------------- | --------------------------------------------- |
| 11 个 FC 共用 AC0             | ✅ 安全 — **状态机互斥**，同一时刻只有一个状态 FC（FC11\~FC17）在运行 |
| OB1 每次循环重载 AC0             | ✅ 安全                                          |
| FC0 冷启动一次性使用               | ✅ 安全                                          |
| **未来如果加中断程序（如脉冲捕获）也用 AC0** | 🔴 有风险 — 中断会打断当前 AC0 计算                       |

**规范建议**:

1. 中断程序中如果需要用累加器，先保存再恢复：

   ```stl
   // 中断入口
   MOVR   AC0, VD_Temp_AC0_Backup   // 先保存
   MOVR   AC1, VD_Temp_AC1_Backup
   // ... 中断逻辑，随便用 AC0~AC3 ...
   MOVR   VD_Temp_AC0_Backup, AC0   // 恢复
   MOVR   VD_Temp_AC1_Backup, AC1
   RETI
   ```

2. 在 V 区分配 **4 个 REAL**（如 VD460\~VD475）专门做"中断 AC 备份区"

3. 当前版本**无中断程序**，可以暂不处理，但必须记录此风险

***

### 8.6 AI/AQ 区（模拟量）— ✅ 完全未使用

**扫描结果**: **0 个引用**。当前 PLC 逻辑中没有使用任何模拟量输入/输出。
**可用数量**: AIW0~~AIW254 共 128 个输入字 + AQW0~~AQW254 共 128 个输出字，**完全空闲**。
**用途**: 如果后续需要接入流量计（4-20mA）或变频器（±10V），AI/AQ 区是首选。

***

### 8.7 S 区（系统存储器）— ✅ 未显式使用

**扫描结果**: SMB/SMW 系列**0 个显式引用**。系统存储器（SMB0\~SMB30）由 PLC 自动维护（如 SMB0.0=首次扫描、SMB0.1=RUN 状态等），用户程序不需要显式读取。

***

### 8.8 所有寄存器区冲突风险总览

| 寄存器区    | 是否存在"V区式"物理重叠       | 已用容量                     | 风险等级                 | 备注                        |
| ------- | ------------------- | ------------------------ | -------------------- | ------------------------- |
| **V 区** | ✅ **是（已发现 4 个 P0）** | 890 / 1024 B (87%)       | 🔴 **高**             | **唯一需要"寄存器映射表"管理的区**      |
| M 区     | ❌ 否                 | 44 bit / 2048 bit (2%)   | 🟢 低                 | 每个 M 位独立对象                |
| T 区     | ❌ 否                 | 25 / 256 个 (10%)         | 🟢 低                 | 每个定时器独立对象                 |
| C 区     | ❌ 否                 | 0 / 256 个 (0%)           | 🟢 无                 | 完全空闲                      |
| I 区     | ❌ 否                 | 17 bit / 1024 bit (1.7%) | 🟢 无                 | 只读，来自硬件                   |
| Q 区     | ❌ 否                 | 10 bit / 1024 bit (1%)   | 🟢 低                 | 有手动/自动互斥保护                |
| AC 区    | ⚠️ 有条件风险            | 1/4 个累加器                 | 🟡 低（当前）→ 🔴 中（加中断后） | CPU 全局寄存器，中断程序必须 PUSH/POP |
| AI/AQ 区 | ❌ 否                 | 0 / 128 字 (0%)           | 🟢 无                 | 完全空闲                      |
| S 区（SM） | ❌ 否                 | 自动维护                     | 🟢 无                 | 用户不应该显式操作                 |

**核心结论**:

> **V 区是 S7-200 SMART 架构里唯一需要"字节级寄存器映射表"来管理冲突的区域**。
> 其余区域因"每对象独立（M/T/C）"、"只读（I）"、"CPU 内部（AC）"、"未使用（AI/AQ）"等原因，不会出现 V 区那样的多类型物理重叠。

***

## 九、版本历史

| 版本   | 日期         | 变更                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| v1.1 | 2026-09-13 | **FC21 计数器迁出**：（a）根因定位 FC21 调试计数器 VW516~~VW548 覆盖用户默认存储区 VB456~~VB539（VD516~VD528/VW532/V536.0），导致 FC0 上电 MOVW 0 清零用户默认值，断电后再上电即丢失（b）修复：VW516~~VW548 全部迁到 VB550~~VB583，FC0 清零指令和 FC21 INCW 同步修改（c）补齐映射表漏掉的 VB416~~VB548 区域：新增用户默认存储区 VB456~~VB539 完整条目，标记空闲区 VB416~~VB455 / VB540~~VB548（d）更新 L301 报警日志缓冲描述：移除"+ FC21 监控计数器"，标记已迁出 |
| v1.0 | 2026-09-12 | **首次生成**，扫描 23 个 STL 文件 + MCGS CSV + 全部寄存器区。（a）**标题升级**：原 `PLC_V区寄存器映射表` → `PLC_完整寄存器映射表（所有区）`（b）新增**第八章**：M/T/C/I/Q/AC 区完整扫描结果（c）**V 区 4 个 P0 级物理冲突**：P0-1 VD10/VD14 vs DT10、P0-2 VB378~~383 MBUS vs VD378/380/382、P0-3 FC15 Bug A、P0-4 VD378 累计加药量 vs MBUS\_CTRL Error（d）**AC0 风险预估**：当前无中断安全，加中断后必须 PUSH/POP（e）空闲区最大块~~ **~~86 字节~~**~~（VB414~~VB499）可分配 RTC 搬移 + 新 HMI 加药量输入（f）V 区占用率 **87%**（890/1024 字节），接近上限 |

