# VD参数区重排说明 v2.0

> 2026-09-12 更新：v2.0 对齐寄存器冲突最终方案（浓度删除 + Bug A 修复 + 5 个变量迁到空闲区）。与 PLC_完整寄存器映射表 v1.1、HMI-PLC变量地址表 v1.9 完全一致。

**项目**：药液配置与加注控制系统（AQUA-EXPO）
**关联Jira**：AQEX-36
**编制日期**：2026-07-18
**配套文档**：HMI-PLC变量地址表 v1.0、HMI变量导入CSV模板、画面变量绑定清单
**适用范围**：8套缸单元通用（192.168.2.101~108，变量地址一致）

---

## 一、重排原因

### 1.1 缺陷描述

PLC代码静态分析器（`/workspace/AQUA-EXPO/tools/stl_static_analyzer.py`）检出3个**严重级**VD编址冲突（严重问题#1~#3），源于HMI-PLC变量地址表v1.0第6/7章中6个VD参数的编址步长为2（VD双字应4字节对齐），导致相邻VD地址的字节范围重叠：

| 严重问题编号 | 冲突对 | 字节重叠区 | 步长 |
|---|---|---|---|
| #1 | VD18(VD_StepResolution) ↔ VD20(VD_CycleSetpoint) | VB20~VB21 | 2（应为4） |
| #2 | VD48(VD_Timeout_ValveA) ↔ VD50(VD_Timeout_ValveB) | VB50~VB51 | 2（应为4） |
| #3 | VD96(VD_ExperimentDuration_Accum) ↔ VD98(VD_Vol_Target) | VB98~VB99 | 2（应为4） |

### 1.2 风险

VD双字（DWORD/REAL，4字节）编址步长若为2，会导致相邻变量的低2字节与高2字节重叠，读写任一变量都会破坏另一变量，引发：
- HMI设定参数被PLC运算中间结果覆盖（参数漂移）
- 实验时长累加值与目标体积相互污染（计量错误）
- 阀门超时保护时长失真（安全功能失效）

### 1.3 重排策略

经核查，VD150~VD190扩展区已被FC40（节奏纠偏）、FC0（系统初始化）、FC11（S1进水）、FC16（S5运行）的中间变量完全占用（VD150/154/158/162/166/170/174/178/186/190/194、VW182/VW184/VW198），不可复用。

故选择**VB350~VB373空闲区段**作为迁移目标：
- 位于VB305~VB349（阀门诊断数据VD308~VD344）之后
- 位于VB500~VB599（报警日志缓冲区）之前
- 全区间空闲，4字节对齐，共24字节容纳6个VD参数
- 不与VD308~VD344（本轮已迁移完成的诊断中间变量区）冲突
- 不与VB300~VB303（报警字）、VW2/4/6/8（状态机）冲突

### 1.4 约束遵守

- ✅ 不修改VD308~VD344（中间变量区）
- ✅ 不修改VB300~VB303（报警字）
- ✅ 不修改VW2/4/6/8（状态机）
- ✅ 每个VD符号名保持不变，仅改地址
- ✅ 所有引用文件均已更新（详见第三章影响文件清单）

---

## 二、旧→新地址映射表

| 旧地址 | 旧字节范围 | 符号名 | 新地址 | 新字节范围 | 数据类型 | 用途 | 所属章节 |
|---|---|---|---|---|---|---|---|
| VD18 | VB18~VB21 | VD_StepResolution | VD350 | VB350~VB353 | REAL | 注射泵单步分辨率（µL/步） | 6.1 浓度与容量 |
| VD20 | VB20~VB23 | VD_CycleSetpoint | VD354 | VB354~VB357 | REAL | 换水周期设定值（min） | 6.2 时间周期 |
| VD48 | VB48~VB51 | VD_Timeout_ValveA | VD358 | VB358~VB361 | REAL | 阀A动作超时保护时长（s） | 6.3 超时保护 |
| VD50 | VB50~VB53 | VD_Timeout_ValveB | VD362 | VB362~VB365 | REAL | 阀B动作超时保护时长（s） | 6.3 超时保护 |
| VD96 | VB96~VB99 | VD_ExperimentDuration_Accum | VD366 | VB366~VB369 | REAL | 实验时长累加值（min） | 7.3 实验进度 |
| VD98 | VB98~VB101 | VD_Vol_Target | VD370 | VB370~VB373 | REAL | 本轮目标抽取母液体积（µL） | 7.4 加药计算 |

**迁移后新区域汇总**：
- 区段：VD350 ~ VD370（VB350 ~ VB373）
- 字节数：24字节（6个VD × 4字节）
- 步长：4字节对齐（无冲突）
- 断电保持：是（需在系统块→断电保持中配置VB350~VB373）

---

## 三、影响文件清单

### 3.1 PLC STL代码文件（6个，全部已更新）

| 文件路径 | 替换内容 | 替换方式 |
|---|---|---|
| /workspace/AQUA-EXPO/plc/stl/FC13_State_S3_Dosing.stl | VD18→VD350、VD98→VD370 | replace_all |
| /workspace/AQUA-EXPO/plc/stl/FC11_State_S1_Inlet.stl | VD20→VD354、VD48→VD358 | replace_all |
| /workspace/AQUA-EXPO/plc/stl/FC15_State_S4_Transfer.stl | VD50→VD362 | replace_all |
| /workspace/AQUA-EXPO/plc/stl/FC16_State_S5_Run.stl | VD20→VD354、VD96→VD366 | replace_all |
| /workspace/AQUA-EXPO/plc/stl/FC30_ValveA_Diag.stl | VD48→VD358 | replace_all |
| /workspace/AQUA-EXPO/plc/stl/FC31_ValveB_Diag.stl | VD50→VD362 | replace_all |

### 3.2 HMI组态文档（3个，全部已更新）

| 文件路径 | 修改内容 |
|---|---|
| /workspace/AQUA-EXPO/docs/HMI-PLC变量地址表_v1.0.md | 第1章地址总表新增VD350~VD370行；第6.1/6.2/6.3章更新VD18/20/48/50行；第7.3/7.4章更新VD96/98行；第13.1/13.2/13.6章更新VD96引用；附录A新增VB350~VB373断电保持条目；附录B新增VD350~VD370快速索引行 |
| /workspace/AQUA-EXPO/docs/hmi_preparation/HMI变量导入CSV模板.csv | 第24/25/32/33/45/46行更新VD18/20/48/50/96/98为新地址 |
| /workspace/AQUA-EXPO/docs/hmi_preparation/画面变量绑定清单.md | 第34/63/64/153/154/161/162/210行更新VD地址引用 |

### 3.3 未修改但需现场关注的文档

以下文档也包含旧VD地址引用，但属于历史快照/分析报告/培训材料，不参与PLC编译与HMI组态，按需在后续版本同步更新：
- /workspace/AQUA-EXPO/docs/PLC代码静态分析报告_v1.0.md（历史分析报告快照）
- /workspace/AQUA-EXPO/docs/PLC代码静态分析结果_v1.0.json（历史分析结果快照）
- /workspace/AQUA-EXPO/tools/static_analysis_report.md（工具生成报告，重跑自动刷新）
- /workspace/AQUA-EXPO/docs/操作员培训材料_v1.0.md
- /workspace/AQUA-EXPO/docs/需求追溯矩阵_v1.0.md
- /workspace/AQUA-EXPO/docs/校准规程_v1.0.md
- /workspace/AQUA-EXPO/docs/技术债务清单_v1.0.md
- /workspace/AQUA-EXPO/docs/项目风险登记册_v1.0.md
- /workspace/AQUA-EXPO/docs/Modbus通讯报文规格书_v1.0.md
- /workspace/AQUA-EXPO/docs/版本发布说明_v1.0.md
- /workspace/AQUA-EXPO/docs/代码评审checklist_v1.0.md
- /workspace/AQUA-EXPO/docs/跨FC数据流分析报告_v1.0.md
- /workspace/AQUA-EXPO/docs/hmi_preparation/历史数据记录与导出规格_v1.0.md
- /workspace/AQUA-EXPO/docs/commissioning/数据备份与恢复方案_v1.0.md
- /workspace/AQUA-EXPO/docs/commissioning/性能基准测试方案_v1.0.md
- /workspace/AQUA-EXPO/docs/commissioning/故障代码字典_v1.0.md
- /workspace/AQUA-EXPO/docs/commissioning/现场调试SOP_v1.0.md
- /workspace/AQUA-EXPO/docs/commissioning/首期1套验收交付包_v1.0.md
- /workspace/AQUA-EXPO/docs/commissioning/PLC首次下装与上电调试Checklist_v1.0.md
- /workspace/AQUA-EXPO/docs/reliability/边界条件与异常场景清单_v1.0.md
- /workspace/AQUA-EXPO/docs/SAT_FAT验收测试用例_v1.0.md
- /workspace/AQUA-EXPO/docs/PLC代码完整性校验报告_v1.0.md
- /workspace/AQUA-EXPO/docs/hmi_preparation/HMI用户权限矩阵_v1.0.md
- /workspace/AQUA-EXPO/docs/hmi_preparation/昆仑通态MCGS组态实施指南_v1.0.md
- /workspace/AQUA-EXPO/docs/hmi_preparation/HMI数据量估算与存储时长测算_v1.0.md
- /workspace/AQUA-EXPO/plc/spec/Story1.2_状态机骨架_程序设计规格书_v1.0.md
- /workspace/AQUA-EXPO/plc/spec/Story1.2_状态机骨架_LAD梯形图说明_v1.0.md
- /workspace/AQUA-EXPO/plc/spec/Story1.3_阀门诊断_程序设计规格书_v1.0.md
- /workspace/AQUA-EXPO/plc/spec/Story1.4_节奏纠偏_程序设计规格书_v1.0.md
- /workspace/AQUA-EXPO/sim/test_sat_cases.py
- /workspace/AQUA-EXPO/sim/plc_simulator.py
- /workspace/AQUA-EXPO/tools/cross_fc_dataflow_analyzer.py

---

## 四、验证方法

### 4.1 静态分析器验证（首要验证）

执行以下命令确认3个严重冲突消失：

```bash
cd /workspace/AQUA-EXPO/tools && python3 stl_static_analyzer.py 2>&1 | grep -E "严重|VD18|VD20|VD48|VD50|VD96|VD98" | head -20
```

**预期结果**：
- 输出中不再包含以下3条严重冲突：
  - `[严重] [VD编址冲突] 全局 VD18(VB18~VB21) 与 VD20(VB20~VB23) 地址重叠`
  - `[严重] [VD编址冲突] 全局 VD48(VB48~VB51) 与 VD50(VB50~VB53) 地址重叠`
  - `[严重] [VD编址冲突] 全局 VD96(VB96~VB99) 与 VD98(VB98~VB101) 地址重叠`
- 报告底部"严重"问题数应为0（本轮AQEX-36修复前为3）

### 4.2 引用完整性验证

执行以下Grep命令确认PLC STL代码与HMI组态文档中无残留旧VD地址：

```bash
# STL代码中不应再出现VD18/VD20/VD48/VD50/VD96/VD98（作为独立token）
cd /workspace/AQUA-EXPO && grep -rnE "\b(VD18|VD20|VD48|VD50|VD96|VD98)\b" plc/stl/

# HMI组态文档中不应再出现旧VD地址（CSV地址列）
grep -nE ",(VD18|VD20|VD48|VD50|VD96|VD98)," docs/hmi_preparation/HMI变量导入CSV模板.csv

# 画面绑定清单中不应再出现旧VD地址
grep -nE "\b(VD18|VD20|VD48|VD50|VD96|VD98)\b" docs/hmi_preparation/画面变量绑定清单.md
```

**预期结果**：以上3条命令均无输出。

### 4.3 新地址无冲突验证

执行以下Grep命令确认新地址VD350/354/358/362/366/370在STL代码中无其他冲突引用：

```bash
cd /workspace/AQUA-EXPO && grep -rnE "\b(VD350|VD354|VD358|VD362|VD366|VD370)\b" plc/stl/
```

**预期结果**：仅在6个已修改的STL文件中出现，且每个新地址仅对应其预期的符号变量。

### 4.4 断电保持配置验证

在STEP 7-Micro/WIN SMART的"系统块→断电保持"中，需新增配置：
- 起始：VB350
- 结束：VB373
- 字节数：24
- 内容：AQEX-36迁移的6个VD参数

确认系统块断电保持范围已覆盖VB350~VB373，否则HMI设定参数（VD_StepResolution/VD_CycleSetpoint/VD_Timeout_ValveA/VD_Timeout_ValveB）及实验进度数据（VD_ExperimentDuration_Accum/VD_Vol_Target）在断电后将丢失。

### 4.5 HMI变量导入验证

将更新后的`HMI变量导入CSV模板.csv`导入HMI工程后，确认：
- 6个变量的PLC地址列已更新为新地址（VD350/354/358/362/366/370）
- 变量名（VD_StepResolution等）保持不变
- 读写属性、断电保持属性、画面编号均与原值一致
- 8套PLC连接（PLC_01~PLC_08）均按新地址绑定

---

## 五、回滚方案

若现场验证发现新地址引入问题，可按以下步骤回滚：
1. 还原6个STL文件至AQEX-36修复前版本（git checkout）
2. 还原3个HMI组态文档至修复前版本
3. 删除系统块中断电保持VB350~VB373配置
4. 重新规划冲突变量的迁移目标地址（确保4字节对齐且不与现有VD区冲突）

---

---

## 六、v2.0 新增：2026-09-11 现场联机 Bug 修复（3 个 Bug + 1 个潜在冲突）

### 6.1 Bug 发现背景

**现场现象**（用户反馈，MCGS v2.0 工程 + 1 台 S7-200 SMART PLC 联机调试）：

| 变量 | 地址 | 现象 |
|------|------|------|
| U1_VD_TargetInletVolume | VD316 | 始终保持默认值 10.0，HMI 无法写入 |
| U1_VD_S4WaitTimeout | VD382 | 可写入，但很快被改写为 `4.23178E-37`（IEEE-754 接近零的垃圾值） |
| U1_VD_ManualDose_Target | VD384 | 多数情况为 0，偶尔能写入；与 VD382 写入互相影响 |
| 其余参数 | VD10/VD350/VD354/VD358/VD362/... | ✅ 正常保存与读取 |

核心链路验证（MCGS 设备窗口 PLC_01 在线 + 实时数据库变量绑定正确 + MBUS_MSG 正常轮询）后，定位到以下 Bug。

### 6.2 Bug A：FC15 借用 VD384 当临时变量覆盖用户参数（根因）

**位置**：`plc/stl/FC15_State_S4_Transfer.stl` NETWORK 1，v1.2 新增的 S4 等待计时分支。

**代码**（L77-79）：

```stl
// v1.2 新增: S4 等待计时 + 超时报警分支
// 需要计算 T61 的 PT 值 (VD_S4WaitTimeout × 10, 供 100ms 时基 TON 使用)
// 开发者懒得用临时变量, 直接把 VD384 当中间变量:
MOVR   VD382, VD384     // ★ VD384 是 ManualDose_Target! 被覆盖!
*R     10.0, VD384
ROUND  VD384, AC0
MOVW   AC0, VW286       // 结果存 VW286 ← 正确的目标变量
```

**后果**：只要状态机进入 S4（VW2=5）且下缸未排空（V1.7=1），首次进入时 FC15 的上升沿（EU）触发一次计算，`VD384` 被覆盖为 `VD382×10`（≈ 18000.0）。随后 FC21 手动注射泵启动时 L23 `MOVR VD384, VD396` 把这个错误值当成"剩余药量"。

**正确做法**：FC15 NETWORK 1 上半段（L53-55）已经在用 `VD324` 当临时变量算 `VD362×10`，同 NETWORK 内完全可以复用：

```stl
MOVR   VD382, VD324     // VD324 是本 NETWORK 已有的临时变量, 无冲突
*R     10.0, VD324
ROUND  VD324, AC0
MOVW   AC0, VW286
```

或用累加器 AC0 完全不占 V 区：

```stl
MOVR   VD382, AC0       // 用 AC0, 零 V 区占用
*R     10.0, AC0
ROUND  AC0, VW286
```

### 6.3 Bug B：VB380~383（MBUS_MSG Error）与 VD380/382/384 物理重叠（根因）

**地址重叠全景**：

```
地址:    VB378  VB379  VB380  VB381  VB382  VB383  VB384  VB385  VB386  VB387  VB388
MBUS:    │CTRL  │T0   │T2    │T1    │T3    │T4    │      │      │      │      │
Error:   │Error │Error│Error │Error │Error │Error │      │      │      │      │
─────────────────────────────────────────────────────────────────────────────────
VD380:                    ├─── VD380 (4字节: S4Wait_Time, FC15/16内部) ────┤
VD382:                            ├─── VD382 (4字节: S4WaitTimeout, HMI参数) ────┤
VD384:                                    ├─── VD384 (4字节: ManualDose_Target, HMI参数) ────┤
VW380:                    ├── VW380 (2字节: FC11/15/17 定时器暂存) ────┤
```

**冲突链**：

1. **FC4_ModbusPolling.stl** 调用 4 个 `MBUS_MSG`，每个 Error 输出到独立的 BYTE：
   - `CALL MBUS_MSG, ..., VB380` （任务2：流量计读数）
   - `CALL MBUS_MSG, ..., VB381` （任务1：注射泵位置）
   - `CALL MBUS_MSG, ..., VB382` （任务3：流量计瞬时）
   - `CALL MBUS_MSG, ..., VB383` （任务4：写命令）
   → 每完成一次轮询（约 200~500ms 一次），MBUS_MSG 就把 Error 码写回 VB380~383

2. **VD382** 的四个字节是 `VB382, VB383, VB384, VB385`（小端序：高地址为高字节）
   - HMI 写入 `VD382 = 1800.0` → 内存字节 `[0x44, 0xE1, 0x00, 0x00]`（VB382=0x44, VB383=0xE1）
   - 下一次 MBUS_MSG 完成 → `VB382 = 0x00`（Error=0），VB382 从 0x44 变成 0x00
   - IEEE-754 浮点数指数位（bit 30~23）被清零 → 值变成 `2^(-149) ≈ 4.23E-37`
   → **完美解释了现场观察到的 "4.23178E-37"**

3. **VD384** 的四个字节是 `VB384, VB385, VB386, VB387`
   - VB384~385 虽然不直接被 MBUS_MSG Error 覆盖
   - 但 Bug A（FC15 用 VD384 当临时变量）每进 S4 就覆盖一次
   - 叠加效应：手动注射泵启动时 `VD396 = VD384` 拿到被污染的值

4. **VW380**（= VB380 + VB381）
   - FC11 L86: `MOVW T37, VW380`（S1 进水定时器暂存）
   - FC15 L123: `MOVW T40, VW380`（S4 转移定时器暂存）
   - FC17 L53: `MOVW T42, VW380`（S6 排水定时器暂存）
   - 这三个都是"执行一次、用完就丢"的临时变量，和 MBUS_MSG Error 字节功能重叠但**因调用时间不同（状态机互斥），实际破坏率较低**。但属于架构隐患。

**文档与代码不一致**：地址表 v1.8 第 11.5 节 L643 写的是 `VB384 | VB_MBUS_MSG_Flow_Error`，但代码里 MBUS_MSG Error 实际占用 VB380~VB383 四个字节，VB384 属于 VD384 的起始字节。这本身就是文档 Bug。

### 6.4 Bug C：VD316 CSV 通道属性误标为"只读"

**位置**：`archive/mcgspro/McgsPro变量导入_单元1.csv` 第 133 行

```
U1_VD_TargetInletVolume,SINGLE,只读VDF316,只读,V数据寄存器,32位浮点数,316,,1,
```

MCGS CSV 导入时，"只读VDF316" 中的 "只读" 被解析为通道的读写属性。MCGS 运行时**不对只读通道下发写命令**，所以 HMI 输入框改了值，PLC VD316 完全不变化。

**设计意图推测**：FC30 阀门诊断代码中 `VD316` 作为"目标进水量"参与阀门内漏判断计算，可能最初设计为"只读显示"。但用户希望现场能调整这个参数，所以通道属性必须改为"读写"。

**修复**：将 CSV 中该通道从 `只读VDF316` 改为 `读写VDF316`，重新导入 MCGS 变量。

### 6.5 重排策略

#### 6.5.1 为什么不直接"修 Bug A"（改 FC15 用 VD324），而是要整体迁移？

Bug A 的修复只需要改 3 行，但 Bug B（VB380~383 与 VD380/382/384 物理重叠）无法通过改 STL 逻辑来解决——**MBUS_MSG 是库指令，Error 输出地址在调用时硬编码为 `CALL MBUS_MSG, ..., VBxxx`，要改就得改 FC4 的 4 个 CALL 参数**。考虑到用户说"不想动 FC4 里面的东西"（FC4 重构过两次，太复杂），最干净的方案是：

> **让 MBUS_MSG Error 区（VB378~VB383）原地不动，把冲突的 VD380/382/384 和 VW380 整体迁到空闲区。**

#### 6.5.2 目标地址选择：VD440~VD452 空闲区

选择依据：

| 检查项 | 结果 |
|--------|------|
| STL 代码 grep `VD4[2-9][0-9] / VD5[0-3][0-9]` | **零匹配**（除 VB500~508 时间戳） |
| MCGS CSV grep VD4xx | **零匹配** |
| 地址表 v1.8 附录 B 规划 | VB410~VB413（Modbus 缓冲区）+ VB500+（报警日志）中间完全空闲 |
| 断电保持区要求 | VD440~VD452 不在原断电保持区，需要新增配置 |

#### 6.5.3 旧→新地址映射表（最终版，2026-09-12 对齐）

> **本次共处理 4 件事**：(1) 删除浓度参数 VD10/VD14 → DT10 RTC 原地独占；(2) 修 Bug A（FC15 用 VD324 替代 VD384）；(3) 所有与 MBUS Error 冲突的变量迁走；(4) 不复用任何已有变量。

##### A. 浓度删除（VD10/VD14 删，DT10 安全了）

| 原地址 | 原字节范围 | 符号名 | 操作 | 原因 |
|--------|-----------|--------|------|------|
| VD10 | VB10~VB13 | 目标浓度 | ❌ **删除** | 简化为用户直接输入加药量，不再需要浓度公式 |
| VD14 | VB14~VB17 | 母液浓度 | ❌ **删除** | 同上 |
| DT10 | VB10~VB17 | RTC 时间戳 | ✅ **原地独占** | 浓度删后 VB10~17 空出，DT10 不再被覆盖 |

##### B. Bug A 修复（与地址迁移独立，先改这个再迁）

| 文件 | 旧代码 | 新代码 | 改动数 |
|------|--------|--------|--------|
| FC15 L77-79 | MOVR VD382, VD384 → *R 10.0, VD384 → ROUND VD384, AC0 | MOVR VD382, **VD324** → *R 10.0, **VD324** → ROUND **VD324**, AC0 | 3 行 |

改完后 VD384 在 FC15 里就没有引用了，只剩 FC0/FC21 用它。

##### C. 冲突变量迁移（MBUS Error 原地独占 VB378~VB383）

| 原地址 | 原字节范围 | 符号名 | 性质 | 新地址 | 新字节范围 | 断电保持 |
|--------|-----------|--------|------|--------|-----------|---------|
| **VD378** | VB378~VB381 | VD_Dosed_Volume_Total 累计加药量 | 内部+FC13写 | **VD440** | VB440~VB443 | 否 |
| **VD380** | VB380~VB383 | VD_S4Wait_Time S4等待时长 | 内部 | **VD444** | VB444~VB447 | 否 |
| **VW380** | VB380~VB381 | 共享定时器暂存 | 内部 | **VB414** | VB414~VB447 | 否 |
| **VD382** | VB382~VB385 | VD_S4WaitTimeout S4等待超时 | HMI 参数 | **VD448** | VB448~VB451 | **是 ← 新增** |
| **VD384** | VB384~VB387 | VD_ManualDose_Target 手动剂量 | HMI 参数 | **VD452** | VB452~VB455 | **是 ← 新增** |

**迁移后 VD380~VB383 区域**：完全归 MBUS_MSG Error 使用，不再有任何冲突。

**VD440~VB452 占用全景**（迁移后）：

```
地址         类型     用途                          断电保持
──────────────────────────────────────────────────────────
VB410~VB413  BYTE[4]  FC4 Modbus 统一缓冲区(DataPtr)   否
─── 本次新增区 ───
VD440        REAL     VD_S4Wait_Time (FC15/16 内部)    否
VB444~VB445  BYTE     VW444 (跨 VD444/VD448 边界, 不用)
VW414        WORD     FC11/15/17 定时器暂存           否
─── HMI 参数区(需断电保持) ───
VD444        REAL     VD_S4WaitTimeout (HMI 可调)      是 ← 新增断电保持
VD448        REAL     VD_ManualDose_Target (HMI 可调)  是 ← 新增断电保持
─── 原有, 不迁移 ───
VW388        WORD     VW_ManualDose_Mode              是 (原已在断电保持区)
VW390        WORD     FC21 手动注射泵状态机            是 (原已在断电保持区)
VD392        REAL     FC21 内部累计量                  否
VD396        REAL     FC21 内部剩余量                  否
─── MBUS Error 区 (原地不动) ───
VB378        BYTE     MBUS_CTRL Error                  否
VB379        BYTE     MBUS_MSG 任务0 Error              否
VB380        BYTE     MBUS_MSG 任务2 Error              否
VB381        BYTE     MBUS_MSG 任务1 Error              否
VB382        BYTE     MBUS_MSG 任务3 Error              否
VB383        BYTE     MBUS_MSG 任务4 Error              否
```

### 6.6 Bug A 单独修复（不涉及地址迁移，最小改动）

如果现场紧急需要先救"手动注射泵参数保存"，可以先单独修 Bug A：

**文件**：`plc/stl/FC15_State_S4_Transfer.stl`
**位置**：NETWORK 1，L77-79
**改动**：

```diff
  MOVR   VD382, VD384
- *R     10.0, VD384
- ROUND  VD384, AC0
+ MOVR   VD382, VD324
+ *R     10.0, VD324
+ ROUND  VD324, AC0
  MOVW   AC0, VW286
```

**效果**：FC15 不再覆盖 VD384，手动注射泵参数可以正常保存（但 VD382 仍受 Bug B 影响会被 MBUS Error 反复覆盖）。

### 6.7 影响文件清单

#### 6.7.1 Bug A 单独修复（1 个文件，3 行改动）

| 文件 | 改动 |
|------|------|
| `plc/stl/FC15_State_S4_Transfer.stl` L77-79 | `VD384` → `VD324`（MOVR/*R/ROUND 三行） |

#### 6.7.2 完整地址重排（8 个文件）

| 文件 | 改动 | 数量 |
|------|------|------|
| `plc/stl/FC0_SysInit.stl` | 初始化 `MOVR 1800.0, VD382` → `VD444`；`MOVR 10000.0, VD384` → `VD448`；清 `VW380` → `VW414` | ~5 处 |
| `plc/stl/FC11_State_S1_Inlet.stl` | `VW380` → `VW414` | 1 处 |
| `plc/stl/FC15_State_S4_Transfer.stl` | Bug A 修 + `VD380` → `VD440`、`VD382` → `VD444`、`VW380` → `VW414` | ~10 处 |
| `plc/stl/FC16_State_S5_Run.stl` | `VD380` → `VD440` | ~2 处 |
| `plc/stl/FC17_State_S6_Drain.stl` | `VW380` → `VW414` | 1 处 |
| `plc/stl/FC21_ManualSyringePump.stl` | `VD384` → `VD448`（所有引用） | ~8 处 |
| `archive/mcgspro/McgsPro变量导入_单元1.csv` | `VDF382` → `VDF444`、`VDF384` → `VDF448` | 2 行 |
| `archive/mcgspro/gen_mcgs_csv.py` | CSV 生成脚本中 VD382/VD384 → VD444/VD448 | 2 行 |

**总计约 33 处修改，6 个 STL 文件 + 1 个 CSV + 1 个 Python 脚本**。

#### 6.7.3 MCGS 画面脚本

无需改动！MCGS 脚本使用变量名（`U1_VD_S4WaitTimeout`、`U1_VD_ManualDose_Target`），不直接使用地址。CSV 重导后变量名不变，仅底层地址更新。

#### 6.7.4 断电保持配置变更

STEP 7-Micro/WIN SMART 系统块 → 断电保持 → 需新增：

| 区段 | 字节数 | 内容 |
|------|--------|------|
| VB444 ~ VB451 | 8 字节 | VD444（S4WaitTimeout）+ VD448（ManualDose_Target） |

原断电保持区（VB350~VB373）**不变**。

### 6.8 验证方法

#### 6.8.1 Bug A 单独修复后验证

1. STEP7 下装修复后的 FC15
2. STEP7 在线监视 VD384
3. MCGS 参数设置页面，手动注射泵总加药量设为 5000，保存
4. **进入 S4 状态**（VW2=5）且 V1.7=1（下缸未排空）
5. 观察 VD384 是否被覆盖 → **修复后应保持 5000.0 不变**

#### 6.8.2 完整地址重排后验证

```bash
# 1. 静态分析器验证新地址无冲突
grep -rnE "\b(VD440|VD444|VD448|VW414)\b" plc/stl/

# 2. 残留旧地址验证
grep -rnE "\b(VD380|VD382|VD384)\b" plc/stl/
# 预期：仅 FC4/FC0 的 MBUS Error 字节声明和 FC15 Bug A 修复前的注释出现

# 3. CSV 验证
grep -n "VD382\|VD384\|VDF382\|VDF384" archive/mcgspro/*.csv
# 预期：无输出（所有 CSV 已更新为 VDF444/VDF448）
```

**现场硬件验证**：

1. STEP7 下装全部修复后的程序
2. MCGS 重导 CSV，画面上确认三个变量的地址已更新
3. MCGS 手动写 VD444=1800、VD448=5000，点保存
4. STEP7 监视 VD444/VD448 → 确认值被写入
5. MCGS 运行环境等 1 分钟（MBUS_MSG 轮询多次）
6. STEP7 再看 VD444/VD448 → **应保持写入值不变**
7. 触发 S4 状态，观察 VD448（ManualDose_Target）→ **应不被覆盖**

### 6.9 回滚方案

1. 还原 6 个 STL 文件至修复前版本（git checkout）
2. MCGS 重新导入修复前的 CSV
3. STEP7 断电保持配置删除 VB444~VB451 区段
4. 重新规划迁移目标（确认新地址不与任何 MBUS 库、Modbus 缓冲区、报警日志冲突）

---

**文档版本**：v1.0 → v2.0
**编制人**：PLC工程组
**审核状态**：待审核（v1.0 基础上追加 v2.0 第六章）
**下次更新触发**：本次 Bug 修复现场验证闭环后
