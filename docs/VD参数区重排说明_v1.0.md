# VD参数区重排说明 v1.0

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

**文档版本**：v1.0
**编制人**：PLC工程组
**审核状态**：待审核
**下次更新触发**：AQEX-36闭环确认、断电保持配置现场实施后
