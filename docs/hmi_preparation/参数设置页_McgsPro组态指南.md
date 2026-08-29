# 参数设置页（画面4）McgsPro 组态指南

**版本**: v2.7（整合版）
**创建日期**: 2026-08-23
**更新日期**: 2026-08-25 (v2.7: 合并远程 v1.2 新增 S4 等待时长 VD380 只读显示 + S4 等待超时阈值 VD382 可调；v2.6: 修正v2.5——该版本McgsPro中!MsgBox/!OpenWindow/!SetWindow均不兼容（字符串参数被识别为非法或类型不匹配），二次确认改为"页面内隐藏确认面板"方案，通过控件Visible属性控制显示/隐藏。v2.5: 修正v2.4——McgsPro该版本安全属性页无"操作确认"，改回"输入框绑定Param_*缓冲变量+保存按钮汇总写入PLC"；v2.4: 参数写入架构改为"输入框直接绑定PLC变量+操作确认"；v2.3: T/S6改回HMI设定参数（时间周期组）；VD_T_Default由VD104迁移至VD144——VD104与VD102字节重叠VB104~105，FC13/FC21写加药步数会破坏T值；实验启动时FC10播种VD112←VD144、VD116←VD108)
**说明**: 本文件整合了项目中所有关于参数设置页的组态工作，包括画面布局、控件属性、脚本代码、安全机制等，作为McgsPro组态工程师的唯一参考。

**配套文档**:
- 《McgsPro画面组态SOP_8画面_v2.0.md》— 8画面总体SOP
- 《McgsPro脚本代码_54个_v2.0.md》— 完整脚本库
- 《画面变量绑定清单.md》— 变量绑定详细列表
- 《HMI-PLC变量地址表_v1.0.md》— PLC变量地址映射

---

## 一、画面概述

### 1.1 画面基本信息

| 属性 | 取值 |
|---|---|
| 画面编号 | 4 |
| 画面名称 | 参数设置 |
| McgsPro画面ID | `画面4_参数设置` |
| 窗口类型 | 用户窗口，标准窗口 |
| 窗口尺寸 | 1280 × 800 |
| 进入权限 | `LoginLevel >= 2`（维护组及以上） |

### 1.2 功能概述

集中管理8套单元的HMI可调工艺参数：
- 顶部单元选择器（1~8号单元）切换操作对象
- 参数分组显示：浓度组、时间周期组、超时组、注射泵组、报警模式
- **输入框绑定HMI内部缓冲变量，点击【保存参数】按钮后校验并写入PLC**（v2.6架构）
- 二次确认采用**页面内隐藏确认面板**（非弹窗），通过Visible属性显示/隐藏
- 保存前范围校验与二次确认，取消则不写入PLC
- 支持"恢复默认"、"复制到其他单元"操作
- 跨参数关联越限实时警告提示（如"下限>标称"）

### 1.3 参数分组

| 分组 | 标签页名 | 参数数量 | 权限要求 |
|---|---|---|---|
| 浓度与配液 | Tab_Conc | 3 | L3（管理员） |
| 时间与周期 | Tab_Time | 7 | L2（维护） |
| 超时与验证 | Tab_Timeout | 6 | L2（维护） |
| 注射泵 | Tab_Pump | 5 | L2（维护） |
| 报警模式 | Tab_AlarmMode | 1 | L2（维护） |
| **合计** | | **22** | |

---

## 二、画面布局图

### 2.1 总体布局

```
┌─────────────────────────────────────────────────────────────────┐
│ [←返回]  参数设置 - X号单元                        时钟      │ 80px
├─────────────────────────────────────────────────────────────────┤
│ 单元:[1][2][3][4][5][6][7][8]  当前操作:X号单元                 │ 40px
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [浓度组] [时间周期组] [超时组] [注射泵] [报警模式]              │ 40px
│                                                                 │
│  ┌──────浓度参数组(1240×120px)────────────────────┐            │
│  │ 目标浓度 VD_C_Set:    [ 5.0 ] %                │            │
│  │ 母液浓度 VD_C_Stock:  [100.0] %                │            │
│  │ 单步分辨率 VD_StepRes:[4.1667] µL/步            │            │
│  └───────────────────────────────────────────────┘            │
│                                                                 │
│  ┌──────时间周期组(1240×280px)────────────────────┐            │
│  │ 换水周期 VD_CycleSetpoint: [30.0] min          │            │
│  │ 实验目标 VD_ExperimentTarget:[480.0] min       │            │
│  │ 预循环时长 VD_PreMixTime:  [120.0] s           │            │
│  │ 预循环下限 VD_PreMixTime_MinSafe:[30.0]s       │            │
│  │ 静止等候 VD_RestTime:      [ 60.0] s           │            │
│  │ 静止下限 VD_RestTime_Min:  [ 15.0] s           │            │
│  │ 顺延上限 VD_CycleExtend_Max:[  5.0] min        │            │
│  │ 首轮T时长 VD_T_Default:  [300.0] s             │            │
│  │ 首轮S6时长 VD_S6_Default:[180.0] s             │            │
  │ S4等待时长 VD_S4Wait_Time:    [  0.0] s (只读)  │
  │ S4等待超时 VD_S4WaitTimeout:  [1800.0] s        │
│  └───────────────────────────────────────────────┘            │
│                                                                 │
│  ┌──────超时参数组(1240×180px)────────────────────┐            │
│  │ 阀A超时 VD_Timeout_ValveA:[60.0] s             │            │
│  │ 阀B超时 VD_Timeout_ValveB:[60.0] s             │            │
│  │ 阀C超时 VD_Timeout_ValveC:[60.0] s             │            │
│  │ 阀A延时 VD_Delay_ValveA_Verify:[5.0] s         │            │
│  │ 泵1超时 VD_Timeout_Pump1:[10.0] s  (预留)      │            │
│  │ 泵2超时 VD_Timeout_Pump2:[10.0] s  (预留)      │            │
│  └───────────────────────────────────────────────┘            │
│                                                                 │
│  ┌──────注射泵组(1240×140px)──────────────────────┐            │
│  │ 手动总量 VD_ManualDose_Target:[  0.0 ] mL  │            │
│  │ 注射泵模式: [0单次 ▼]                          │            │
│  │ 启动速度 VD_PumpSpeed_Start:[450.0] Hz         │            │
│  │ 最高速度 VD_PumpSpeed_Max :[700.0] Hz          │            │
│  │ 截止速度 VD_PumpSpeed_Cutoff:[450.0] Hz        │            │
│  └───────────────────────────────────────────────┘            │
│                                                                 │
│  ┌──────报警模式(1240×40px)───────────────────────┐            │
│  │ 报警模式: [0人工确认 ▼] 或 [1自动恢复 ▼]       │            │
│  └───────────────────────────────────────────────┘            │
│                                                                 │
│  [保存参数] [恢复默认] [复制到其他单元] [返回]                   │
├─────────────────────────────────────────────────────────────────┤
│ ⚠ 无报警 | 2026-07-15 14:30:25 | 权限:管理员                   │ 60px
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 布局尺寸说明

| 区域 | 高度 | 说明 |
|---|---|---|
| 顶部导航栏 | 80px | 返回按钮+标题+时钟 |
| 单元选择条 | 40px | 8个单元按钮+当前单元显示 |
| 标签页选择栏 | 40px | 5个标签页切换按钮 |
| 浓度参数组 | 120px | 3个输入框（带标签+单位） |
| 时间周期组 | 280px | 9个输入框 |
| 超时参数组 | 180px | 6个输入框 |
| 注射泵组 | 140px | 4个输入框+1个组合框 |
| 报警模式组 | 40px | 1个组合框 |
| 操作按钮栏 | 50px | 4个按钮 |
| 底部状态栏 | 60px | 报警/时间/权限 |

---

## 三、元素清单（详细版）

### 3.1 公共元素（复制自其他画面，13个）

| 编号 | 构件类型 | 名称 | 位置(x,y,w,h) | 属性 |
|---|---|---|---|---|
| 4-001 | 标准按钮 | btnReturn | (20,15,60,50) | ←返回，黑体18pt |
| 4-002 | 标签 | lblPageTitle | (100,15,900,50) | "参数设置 - " + Str(SelectedUnit) + "号单元"，20pt加粗 |
| 4-003 | 标签 | lblClock | (1100,20,160,40) | 实时时钟，12pt |
| 4-004~4-013 | 公共元素 | | | 底部状态栏等，复制粘贴 |

### 3.2 单元选择器（16个）

| 编号 | 构件类型 | 名称 | 位置 | 文字 | 绑定变量 |
|---|---|---|---|---|---|
| 4-014 | 标签 | lbl_UnitSel | (20,85,80,35) | "单元:" | — |
| 4-015 | 按钮 | btn_Unit1 | (105,85,55,35) | "1" | SelectedUnit=1 |
| 4-016 | 按钮 | btn_Unit2 | (165,85,55,35) | "2" | SelectedUnit=2 |
| 4-017 | 按钮 | btn_Unit3 | (225,85,55,35) | "3" | SelectedUnit=3 |
| 4-018 | 按钮 | btn_Unit4 | (285,85,55,35) | "4" | SelectedUnit=4 |
| 4-019 | 按钮 | btn_Unit5 | (345,85,55,35) | "5" | SelectedUnit=5 |
| 4-020 | 按钮 | btn_Unit6 | (405,85,55,35) | "6" | SelectedUnit=6 |
| 4-021 | 按钮 | btn_Unit7 | (465,85,55,35) | "7" | SelectedUnit=7 |
| 4-022 | 按钮 | btn_Unit8 | (525,85,55,35) | "8" | SelectedUnit=8 |
| 4-023 | 标签 | lbl_CurrentUnit | (600,85,300,35) | "当前操作:X号单元" | SelectedUnit |

### 3.3 标签页选择器（5个）

| 编号 | 构件类型 | 名称 | 位置 | 文字 |
|---|---|---|---|---|
| 4-024 | 按钮 | btnTab_Conc | (20,130,200,40) | 浓度组 |
| 4-025 | 按钮 | btnTab_Time | (225,130,200,40) | 时间周期组 |
| 4-026 | 按钮 | btnTab_Timeout | (430,130,200,40) | 超时组 |
| 4-027 | 按钮 | btnTab_Pump | (635,130,200,40) | 注射泵 |
| 4-028 | 按钮 | btnTab_Alarm | (840,130,200,40) | 报警模式 |

### 3.4 浓度参数组（3个输入框）

| 编号 | 控件类型 | 名称 | 位置(x,y,w,h) | 标签 | 输入框位置 | 绑定变量 | 范围 | 权限 |
|---|---|---|---|---|---|---|---|---|
| 4-030 | 标签 | lbl_C_Set | (60,185,280,32) | "目标浓度 VD_C_Set:" | num_C_Set (350,185,100,32) | U{N}_VD_C_Set | 0~50 | L3 |
| 4-031 | 标签 | lbl_C_Stock | (60,220,280,32) | "母液浓度 VD_C_Stock:" | num_C_Stock (350,220,100,32) | U{N}_VD_C_Stock | 0~100 | L3 |
| 4-032 | 标签 | lbl_StepRes | (60,255,280,32) | "单步分辨率 VD_StepRes:" | num_StepRes (350,255,120,32) | U{N}_VD_StepResolution | 0.0001~10 | L3 |

### 3.5 时间周期组（9个输入框）

| 编号 | 控件类型 | 名称 | 标签 | 绑定变量 | 范围 | 单位 |
|---|---|---|---|---|---|---|
| 4-040 | 标签+输入框 | lbl_CycleSet / num_CycleSet | 换水周期 | U{N}_VD_CycleSetpoint | 1~1440 | min |
| 4-040a | 标签 | lbl_S4WaitTime | S4等待时长(只读) | U{N}_VD_S4Wait_Time(VD380) | 0~86400 | s |
| 4-040b | 标签+输入框 | lbl_S4WaitTimeout / num_S4WaitTimeout | S4等待超时阈值 | U{N}_VD_S4WaitTimeout(VD382) | 60~7200 | s |
| 4-041 | 标签+输入框 | lbl_ExpTarget / num_ExpTarget | 实验时长目标 | U{N}_VD_ExperimentTarget | 1~10000 | min |
| 4-042 | 标签+输入框 | lbl_PreMix / num_PreMix | 预循环标称S2 | U{N}_VD_PreMixTime | 1~600 | s |
| 4-043 | 标签+输入框 | lbl_PreMixMin / num_PreMixMin | 预循环压缩下限 | U{N}_VD_PreMixTime_MinSafe | 1~300 | s |
| 4-044 | 标签+输入框 | lbl_Rest / num_Rest | 静止等候标称S3.5 | U{N}_VD_RestTime | 1~300 | s |
| 4-045 | 标签+输入框 | lbl_RestMin / num_RestMin | 静止等候压缩下限 | U{N}_VD_RestTime_Min | 1~120 | s |
| 4-046 | 标签+输入框 | lbl_CycleExt / num_CycleExt | 换水周期顺延上限 | U{N}_VD_CycleExtend_Max | 0~30 | min |
| 4-047 | 标签+输入框 | lbl_TDefault / num_TDefault | 首轮配液总时长T | U{N}_VD_T_Default | 60~900 | s |
| 4-048 | 标签+输入框 | lbl_S6Default / num_S6Default | 首轮S6排水时长 | U{N}_VD_S6_Default | 30~600 | s |

**位置说明**：每行标签在(60, y, 280, 32)，输入框在(350, y, 100~120, 32)，y依次为300, 340, 380, 420, 460, 500, 540, 580, 620。

**T/S6参数说明（操作员帮助提示）**：
- 首轮配液总时长T：仅首轮换水使用（首轮无实测数据时预估"何时开始配液"），首轮结束后系统自动学习实测值，此设置不再生效。T ≈ 上缸进水时长 + 预循环时长(120s) + 加药时长(可忽略) + 静止等候(60s)。典型值300s；设置偏小仅导致首轮换水顺延1~2分钟，不会出错。
- 首轮S6排水时长：仅首轮下缸排水预估用（用于计算下一轮预规划时机），首轮排水完成后自动学习实测值。典型值180s（下缸容积÷排水流量）。

### 3.6 超时参数组（6个输入框）

| 编号 | 控件类型 | 名称 | 标签 | 绑定变量 | 范围 | 单位 |
|---|---|---|---|---|---|---|
| 4-050 | 标签+输入框 | lbl_ValveA_T / num_ValveA_T | 阀A动作超时 | U{N}_VD_Timeout_ValveA | 1~300 | s |
| 4-051 | 标签+输入框 | lbl_ValveB_T / num_ValveB_T | 阀B动作超时 | U{N}_VD_Timeout_ValveB | 1~300 | s |
| 4-052 | 标签+输入框 | lbl_ValveC_T / num_ValveC_T | 阀C动作超时 | U{N}_VD_Timeout_ValveC | 1~300 | s |
| 4-053 | 标签+输入框 | lbl_DelayA / num_DelayA | 阀A关闭延时验证 | U{N}_VD_Delay_ValveA_Verify | 1~30 | s |
| 4-054 | 标签+输入框 | lbl_Pump1_T / num_Pump1_T | 预留-泵1超时 | U{N}_VD_Timeout_Pump1 | 1~120 | s |
| 4-055 | 标签+输入框 | lbl_Pump2_T / num_Pump2_T | 预留-泵2超时 | U{N}_VD_Timeout_Pump2 | 1~120 | s |

### 3.7 注射泵参数组（4输入框+1组合框）

| 编号 | 控件类型 | 名称 | 标签 | 绑定变量 | 范围 | 单位 |
|---|---|---|---|---|---|---|
| 4-060 | 标签+输入框 | lbl_ManualDose / num_ManualDose | 手动注射泵总加药量 | U{N}_VD_ManualDose_Target | 0~50 | mL |
| 4-061 | 标签+组合框 | lbl_ManualMode / cmb_ManualMode | 注射泵模式 | U{N}_VW_ManualDose_Mode | 0单次/1循环 | — |
| 4-062 | 标签+输入框 | lbl_PumpStart / num_PumpStart | 注射泵启动速度 | U{N}_VD_PumpSpeed_Start | 100~6000 | Hz |
| 4-063 | 标签+输入框 | lbl_PumpMax / num_PumpMax | 注射泵最高速度 | U{N}_VD_PumpSpeed_Max | 100~6000 | Hz |
| 4-064 | 标签+输入框 | lbl_PumpCutoff / num_PumpCutoff | 注射泵截止速度 | U{N}_VD_PumpSpeed_Cutoff | 50~5400 | Hz |

### 3.8 报警模式（1组合框）

| 编号 | 控件类型 | 名称 | 标签 | 绑定变量 | 选项 |
|---|---|---|---|---|---|
| 4-070 | 标签+组合框 | lbl_AckMode / cmb_AckMode | 报警确认模式 | U{N}_M_AlarmAckMode | 0=自动恢复, 1=人工确认 |

### 3.9 操作按钮（4个）

| 编号 | 控件类型 | 名称 | 位置(x,y,w,h) | 文字 | 权限 |
|---|---|---|---|---|---|
| 4-080 | 标准按钮 | btnSaveParam | (50,680,200,50) | 保存参数 | L2+ |
| 4-081 | 标准按钮 | btnRestoreDefault | (260,680,200,50) | 恢复默认 | L3 |
| 4-082 | 标准按钮 | btnCopyToOthers | (470,680,200,50) | 复制到其他单元 | L3 |
| 4-083 | 标准按钮 | btnReturn | (680,680,150,50) | 返回 | L1+ |

### 3.10 二次确认面板（v2.6新增，默认隐藏）

| 编号 | 控件类型 | 名称 | 位置(x,y,w,h) | 文字 | 初始Visible |
|---|---|---|---|---|---|
| 4-090 | 矩形/标签（背景） | pnlConfirmBG | (340,300,600,200) | — | 0 |
| 4-091 | 标签 | lblConfirmText | (360,330,560,60) | "" | 0 |
| 4-092 | 标准按钮 | btnConfirmOK | (440,420,120,50) | 确定 | 0 |
| 4-093 | 标准按钮 | btnConfirmCancel | (600,420,120,50) | 取消 | 0 |

**v2.6架构说明**：
- 输入框绑定HMI内部缓冲变量 `Param_*`，保存按钮负责校验范围、显示确认面板、将缓冲变量汇总写入PLC。
- 该版本McgsPro中 `!MsgBox` / `!OpenWindow` / `!SetWindow` 均不兼容字符串参数，因此二次确认不用弹窗/子窗口，改用页面内隐藏面板。
- 面板显示时屏蔽下方输入框（可通过背景矩形覆盖+置于顶层实现），避免误操作。

### 3.11 元素汇总

| 类别 | 数量 | 说明 |
|---|---|---|
| 公共元素 | 13 | 顶部/底部导航，复制粘贴 |
| 单元选择器 | 10 | 8按钮+2标签 |
| 标签页选择器 | 5 | 标签切换按钮 |
| 输入框 | 22 | 浓度3+时间9+超时6+注射泵4 |
| 组合框 | 2 | 注射泵模式+报警模式 |
| 标签（参数名） | 24 | 与输入框一一对应 |
| 操作按钮 | 4 | 保存/恢复/复制/返回 |
| 警告提示标签 | 3 | lbl_Warning1~3（动态显隐） |
| **合计** | **~84** | |

---

## 四、控件属性详细配置

### 4.1 输入框属性配置（以 `num_C_Set` 为例）

| 属性页 | 字段 | 取值 | 说明 |
|---|---|---|---|
| 基本属性 | 水平对齐 | 居中 | |
| 基本属性 | 垂直对齐 | 居中 | |
| 基本属性 | 边界类型 | 三维边框 | |
| 基本属性 | 背景颜色 | #FFFFFF | 白色 |
| 基本属性 | 字符颜色 | #2C3E50 | 深蓝灰色 |
| 基本属性 | 字体 | 黑体 14pt | |
| 操作属性 | 对应数据对象的名称 | Param_C_Set | HMI内部缓冲变量（v2.5） |
| 操作属性 | 数据单位 | % | |
| 操作属性 | 数据格式 | 浮点数 | REAL类型 |
| 操作属性 | 自然小数 | 取消勾选 | |
| 操作属性 | 固定小数位数 | 1 | 显示x.x |
| 操作属性 | 最小值 | 0 | |
| 操作属性 | 最大值 | 50 | |
| 键盘属性 | 键盘类型 | 系统默认键盘 | |
| 安全属性 | 表达式 | `LoginLevel >= 3 AND U{N}_VW2_StateMachine == 0` | L3+且状态机=S0 |
| 安全属性 | 条件设置 | 表达式非0时构件可操作 | |
| 安全属性 | 失效样式 | 变灰不可用 | |

**v2.5绑定规则变更**：所有输入框不再直接绑定PLC变量，而是绑定 `Param_*` HMI内部缓冲变量。画面打开/单元切换时由Load脚本（脚本27）从PLC读入缓冲；参数修改在缓冲中暂存；只有点击【保存参数】按钮（脚本28）时才汇总写回PLC，从而实现真正的二次确认和批量保存。

**其他输入框差异点**：
- 浓度/步分辨率（4-030~4-032）：权限要求 `LoginLevel >= 3`
- 时间/超时/注射泵（除浓度）：权限要求 `LoginLevel >= 2`
- 运行中所有参数：附加条件 `U{N}_VW2_StateMachine == 0`（仅S0状态可编辑）
- 范围值、单位按元素清单中对应列设置

### 4.1.1 数据缩放配置说明

**背景**：PLC 内部变量 `VD_ManualDose_Target` (VD384) 单位为 **µL（微升）**，为方便操作员理解，HMI 输入框以 **mL（毫升）** 为单位显示。

#### 手动加药量输入框数据缩放设置

**适用控件**：`num_ManualDose`（4-060）

**配置步骤**：
1. 双击 `num_ManualDose` 打开属性对话框
2. 切换到"操作属性"页
3. 找到"数据缩放"区域，勾选"启用缩放"
4. 设置缩放参数：

| 配置项 | 取值 | 说明 |
|---|---|---|
| 缩放公式 | `PLC值 = 输入值 × 1000` | mL → µL |
| 系数 | 1000 | 1mL = 1000µL |

**效果说明**：
| 操作 | 用户输入 | PLC 存储值 |
|---|---|---|
| 输入 5.0 mL | 5.0 | 5000 µL |
| 输入 2.5 mL | 2.5 | 2500 µL |
| 显示 | 自动换算回 mL | — |

⚠️ **注意**：此设置仅影响 HMI 显示/输入，PLC 内部仍以 µL 为单位存储和计算。

#### 注射泵速度输入框说明

注射泵速度变量 (`VD_PumpSpeed_Start/Max/Cutoff`) 在 HMI 和 PLC 中均以 **Hz** 为单位，**无需数据缩放**。直接绑定即可。

### 4.2 组合框属性配置

| 属性页 | 字段 | 取值（注射泵模式） | 取值（报警模式） |
|---|---|---|---|
| 基本属性 | 控件名称 | cmb_ManualMode | cmb_AckMode |
| 基本属性 | 内容关联 | U{N}_VW_ManualDose_Mode | U{N}_M_AlarmAckMode |
| 基本属性 | 奇行背景 | #FFFFFF | #FFFFFF |
| 基本属性 | 偶行背景 | #ECF0F1 | #ECF0F1 |
| 基本属性 | 文本颜色 | #2C3E50 | #2C3E50 |
| 基本属性 | 行高 | 30 | 30 |
| 基本属性 | 弹出方向 | 向下 | 向下 |
| 基本属性 | 构件类型 | 下拉列表框 | 下拉列表框 |
| 选项设置 | 选项1 | ID=0, "0 单次" | ID=0, "0 人工确认" |
| 选项设置 | 选项2 | ID=1, "1 循环" | ID=1, "1 自动恢复" |
| 安全属性 | 表达式 | LoginLevel >= 2 | LoginLevel >= 2 |
| 安全属性 | 弹框确认 | 勾选，确认等待=30 | 勾选 |

### 4.3 按钮属性配置

#### 4.3.1 保存按钮（btnSaveParam）

**v2.6机制**：输入框绑定HMI内部缓冲变量 `Param_*`，点击保存按钮后执行脚本28：范围校验 → 显示页面内确认面板 → 点击【确定】后将缓冲变量直接赋值给PLC变量。

| 属性 | 取值 |
|---|---|
| 字体 | 黑体 18pt |
| 文字颜色 | #FFFFFF |
| 背景色（正常） | #3498DB（蓝色） |
| 背景色（禁用） | #BDC3C7（灰色） |
| 操作权限 | LoginLevel >= 2 |
| 操作属性 | 抬起时执行脚本28 |

**典型操作流**：操作员修改输入框（改的是缓冲变量）→ 点击【保存参数】→ 脚本校验全部参数范围 → 页面内显示确认面板（lblConfirmText显示"将修改X号单元25个参数，确认保存？"，btnConfirmOK/btnConfirmCancel可见）→ 点【确定】后逐参数赋值给PLC变量并隐藏面板 → 点【取消】仅隐藏面板。

**McgsPro脚本约束**：
- 不能使用自定义Sub/Function，不能动态拼接变量名，只能直接赋值（`U1_VD_C_Set = Param_C_Set`）。
- 该版本不支持 `!MsgBox` / `!OpenWindow` / `!SetWindow` 字符串参数，因此二次确认通过页面内面板实现。
- 首期仅U1，8单元实施时复制画面后把U1_前缀改成对应单元前缀。

#### 4.3.2 恢复默认按钮（btnRestoreDefault）

| 属性 | 取值 |
|---|---|
| 字体 | 黑体 18pt |
| 背景色（正常） | #E74C3C（红色） |
| 操作权限 | LoginLevel >= 3 |
| 操作属性 | 抬起时执行脚本29 |

#### 4.3.3 复制到其他单元按钮（btnCopyToOthers）

| 属性 | 取值 |
|---|---|
| 字体 | 黑体 18pt |
| 背景色（正常） | #F39C12（橙色） |
| 操作权限 | LoginLevel >= 3 |
| 操作属性 | 抬起时执行脚本30 |

#### 4.3.4 返回按钮（btnReturn）

| 属性 | 取值 |
|---|---|
| 字体 | 黑体 18pt |
| 背景色 | #7F8C8D（灰色） |
| 操作属性 | `!CloseAllWindow("画面4_参数设置")` |

### 4.4 标签页切换按钮

| 状态 | 字体 | 背景色 | 文字颜色 |
|---|---|---|---|
| 选中 | 黑体 18pt | #3498DB（蓝） | #FFFFFF（白） |
| 未选中 | 黑体 18pt | #BDC3C7（灰） | #FFFFFF（白） |

**切换脚本**（以浓度组为例）：
```
btnTab_Conc.BackColor = RGB(52, 152, 219)
btnTab_Time.BackColor = RGB(189, 195, 199)
btnTab_Timeout.BackColor = RGB(189, 195, 199)
btnTab_Pump.BackColor = RGB(189, 195, 199)
btnTab_Alarm.BackColor = RGB(189, 195, 199)
' 显示浓度组面板，隐藏其他
```

---

## 五、完整 McgsPro 脚本

### 脚本 27：画面4 Load 脚本（窗口打开事件）

**用途**: 画面打开时从PLC读取当前单元参数，填充到缓冲变量
**位置**: 用户窗口 → 画面4_参数设置 → Load 事件

```vb
' ============================================
' 画面4_参数设置 Load 脚本 (v2.5: 读PLC到缓冲)
' 功能: 把 U1 单元的 PLC 参数读到 Param_* 缓冲变量供输入框显示
' 注: McgsPro不支持动态变量名拼接,首期写死U1;8单元时复制画面改前缀
' ============================================

Param_C_Set = U1_VD_C_Set
Param_C_Stock = U1_VD_C_Stock
Param_StepRes = U1_VD_StepResolution
Param_CycleSet = U1_VD_CycleSetpoint
Param_ExpTarget = U1_VD_ExperimentTarget
Param_PreMixTime = U1_VD_PreMixTime
Param_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
Param_RestTime = U1_VD_RestTime
Param_RestTime_Min = U1_VD_RestTime_Min
Param_CycleExtend_Max = U1_VD_CycleExtend_Max
Param_T_Default = U1_VD_T_Default
Param_S6_Default = U1_VD_S6_Default
Param_S4WaitTimeout = U1_VD_S4WaitTimeout
Param_Timeout_ValveA = U1_VD_Timeout_ValveA
Param_Timeout_ValveB = U1_VD_Timeout_ValveB
Param_Timeout_ValveC = U1_VD_Timeout_ValveC
Param_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
Param_Timeout_Pump1 = U1_VD_Timeout_Pump1
Param_Timeout_Pump2 = U1_VD_Timeout_Pump2
Param_ManualDose_Target = U1_VD_ManualDose_Target
Param_ManualDose_Mode = U1_VW_ManualDose_Mode
Param_PumpSpeed_Start = U1_VD_PumpSpeed_Start
Param_PumpSpeed_Max = U1_VD_PumpSpeed_Max
Param_PumpSpeed_Cutoff = U1_VD_PumpSpeed_Cutoff
Param_AlarmAckMode = U1_M_AlarmAckMode

ParamTargetUnit = SelectedUnit

' 更新页面标题
lblPageTitle.Caption = "参数设置 - " + !str(SelectedUnit) + "号单元"
```

> 注：McgsPro不支持动态变量名拼接，输入框绑定固定变量名（如U1_VD_C_Set）。8单元完整实施时采用**画面复制法**：复制8份参数设置画面（画面4_参数设置_U1~U8），每份改绑对应单元变量，单元选择器按钮直接打开对应画面。

### 脚本 28：保存参数按钮

**用途**: 校验缓冲参数范围 → 显示页面内确认面板 → 等待用户点击【确定】后写回PLC
**位置**: 用户窗口 → 画面4_参数设置 → btnSaveParam → Click 事件

```vb
' ============================================
' 保存参数按钮脚本 (v2.6: 页面内确认面板版)
' 功能: 1.范围校验 2.显示确认面板 3.用户点"确定"后将 Param_* 写入 U1_*
' 约束: 无自定义函数、无动态变量名、块IF必须ENDIF
'       该版本McgsPro不支持!MsgBox/!OpenWindow/!SetWindow字符串参数
' ============================================

' --- 1. 范围校验（越限时只显示错误提示，不显示"确定"按钮） ---
IF Param_C_Set < 0 OR Param_C_Set > 50 THEN
    lblConfirmText.Caption = "错误：浓度设定值超范围(0~50%)"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

IF Param_C_Stock < 0 OR Param_C_Stock > 100 THEN
    lblConfirmText.Caption = "错误：母液浓度超范围(0~100%)"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

IF Param_CycleSet < 1 OR Param_CycleSet > 1440 THEN
    lblConfirmText.Caption = "错误：换水周期超范围(1~1440min)"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

IF Param_PreMixTime_MinSafe > Param_PreMixTime THEN
    lblConfirmText.Caption = "错误：预循环压缩下限不得大于标称时长"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

IF Param_RestTime_Min > Param_RestTime THEN
    lblConfirmText.Caption = "错误：静止等候压缩下限不得大于标称时长"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

IF Param_CycleExtend_Max > Param_CycleSet THEN
    lblConfirmText.Caption = "错误：换水周期顺延上限不得大于换水周期"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

IF Param_T_Default < 60 OR Param_T_Default > 900 THEN
    lblConfirmText.Caption = "错误：首轮配液总时长T超范围(60~900s)"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

IF Param_S6_Default < 30 OR Param_S6_Default > 600 THEN
    lblConfirmText.Caption = "错误：首轮S6排水时长超范围(30~600s)"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

IF Param_S4WaitTimeout < 60 OR Param_S4WaitTimeout > 7200 THEN
    lblConfirmText.Caption = "错误：S4等待超时阈值超范围(60~7200s)"
    btnConfirmOK.Visible = 0
    btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1
    lblConfirmText.Visible = 1
    EXIT
ENDIF

' --- 2. 校验通过，显示确认面板 ---
lblConfirmText.Caption = "将修改" + !Str(SelectedUnit) + "号单元25个参数，确认保存？"
btnConfirmOK.Visible = 1
btnConfirmCancel.Visible = 1
pnlConfirmBG.Visible = 1
lblConfirmText.Visible = 1
```

### 脚本 28a：确认按钮（btnConfirmOK）

**位置**: 画面4_参数设置 → btnConfirmOK → Click 事件

```vb
' --- 写回PLC（直接赋值，无自定义函数） ---
U1_VD_C_Set = Param_C_Set
U1_VD_C_Stock = Param_C_Stock
U1_VD_StepResolution = Param_StepRes
U1_VD_CycleSetpoint = Param_CycleSet
U1_VD_ExperimentTarget = Param_ExpTarget
U1_VD_PreMixTime = Param_PreMixTime
U1_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
U1_VD_RestTime = Param_RestTime
U1_VD_RestTime_Min = Param_RestTime_Min
U1_VD_CycleExtend_Max = Param_CycleExtend_Max
U1_VD_T_Default = Param_T_Default
U1_VD_S6_Default = Param_S6_Default
U1_VD_S4WaitTimeout = Param_S4WaitTimeout
U1_VD_Timeout_ValveA = Param_Timeout_ValveA
U1_VD_Timeout_ValveB = Param_Timeout_ValveB
U1_VD_Timeout_ValveC = Param_Timeout_ValveC
U1_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
U1_VD_Timeout_Pump1 = Param_Timeout_Pump1
U1_VD_Timeout_Pump2 = Param_Timeout_Pump2
U1_VD_ManualDose_Target = Param_ManualDose_Target
U1_VW_ManualDose_Mode = Param_ManualDose_Mode
U1_VD_PumpSpeed_Start = Param_PumpSpeed_Start
U1_VD_PumpSpeed_Max = Param_PumpSpeed_Max
U1_VD_PumpSpeed_Cutoff = Param_PumpSpeed_Cutoff
U1_M_AlarmAckMode = Param_AlarmAckMode

' --- 隐藏确认面板 ---
pnlConfirmBG.Visible = 0
lblConfirmText.Visible = 0
btnConfirmOK.Visible = 0
btnConfirmCancel.Visible = 0
```

### 脚本 28b：取消按钮（btnConfirmCancel）

**位置**: 画面4_参数设置 → btnConfirmCancel → Click 事件

```vb
' 隐藏确认面板，不写入PLC
pnlConfirmBG.Visible = 0
lblConfirmText.Visible = 0
btnConfirmOK.Visible = 0
btnConfirmCancel.Visible = 0
```

> **McgsPro语法注意**：
> - 块IF必须配对`ENDIF`（如上面所示）；单行IF可写`IF x THEN y`不需要ENDIF。
> - `EXIT`用于退出脚本（若你的McgsPro版本不支持，改用`RETURN`）。
> - 该版本不支持 `!MsgBox` / `!OpenWindow` / `!SetWindow` 字符串参数，因此用控件`Visible`属性实现页面内确认面板。
> - 8单元实施时复制画面，把脚本中所有`U1_`前缀替换为`U2_`…`U8_`。

### 脚本 29：恢复默认按钮

**用途**: 恢复当前单元参数到默认值
**位置**: btnRestoreDefault → Click 事件

> **v2.5实施提示**：以下脚本已改为McgsPro支持的直接赋值语法（参考脚本28），首期U1写死，8单元时复制画面改`U1_`前缀。

```vb
' ============================================
' 恢复默认按钮脚本
' ============================================

If LoginLevel < 3 Then
    !MsgBox("恢复默认需管理员(L3)权限", 0, "权限提示")
    Exit
End If

Dim ret
ret = !MsgBox("将恢复" + Str(SelectedUnit) + "号单元参数到默认值，确认？", 3)
If ret <> 1 Then Exit Sub

' 通过脚本写入默认值
Call SetValueByUnit(SelectedUnit, "VD_C_Set", 5.0)
Call SetValueByUnit(SelectedUnit, "VD_C_Stock", 100.0)
Call SetValueByUnit(SelectedUnit, "VD_StepResolution", 4.1667)
Call SetValueByUnit(SelectedUnit, "VD_CycleSetpoint", 30.0)
Call SetValueByUnit(SelectedUnit, "VD_ExperimentTarget", 480.0)
Call SetValueByUnit(SelectedUnit, "VD_PreMixTime", 120.0)
Call SetValueByUnit(SelectedUnit, "VD_PreMixTime_MinSafe", 30.0)
Call SetValueByUnit(SelectedUnit, "VD_RestTime", 60.0)
Call SetValueByUnit(SelectedUnit, "VD_RestTime_Min", 15.0)
Call SetValueByUnit(SelectedUnit, "VD_CycleExtend_Max", 5.0)
Call SetValueByUnit(SelectedUnit, "VD_T_Default", 300.0)
Call SetValueByUnit(SelectedUnit, "VD_S6_Default", 180.0)
Call SetValueByUnit(SelectedUnit, "VD_S4WaitTimeout", 1800.0)
Call SetValueByUnit(SelectedUnit, "VD_Timeout_ValveA", 60.0)
Call SetValueByUnit(SelectedUnit, "VD_Timeout_ValveB", 60.0)
Call SetValueByUnit(SelectedUnit, "VD_Timeout_ValveC", 60.0)
Call SetValueByUnit(SelectedUnit, "VD_Delay_ValveA_Verify", 5.0)
Call SetValueByUnit(SelectedUnit, "VD_Timeout_Pump1", 10.0)
Call SetValueByUnit(SelectedUnit, "VD_Timeout_Pump2", 10.0)
Call SetValueByUnit(SelectedUnit, "VD_ManualDose_Target", 0.0)
Call SetValueByUnit(SelectedUnit, "VW_ManualDose_Mode", 0)
Call SetValueByUnit(SelectedUnit, "VD_PumpSpeed_Start", 450.0)
Call SetValueByUnit(SelectedUnit, "VD_PumpSpeed_Max", 700.0)
Call SetValueByUnit(SelectedUnit, "VD_PumpSpeed_Cutoff", 450.0)
Call SetValueByUnit(SelectedUnit, "M_AlarmAckMode", 0)

' 刷新编辑缓冲变量
Call RefreshParamBuffer(SelectedUnit)

!MsgBox("参数已恢复默认", 0, "恢复成功")
```

### 脚本 30：复制到其他单元按钮

**用途**: 将当前单元参数复制到其他单元
**位置**: btnCopyToOthers → Click 事件

> **v2.5实施提示**：McgsPro不支持数组和自定义函数，复制功能建议利用McgsPro"配方"组件，或展开为逐参数直接赋值（如`U2_VD_C_Set = U1_VD_C_Set`）。首期仅U1时本按钮可禁用或暂不实施。

```vb
' ============================================
' 复制到其他单元按钮脚本
' ============================================

If LoginLevel < 3 Then
    !MsgBox("复制参数需管理员(L3)权限", 0, "权限提示")
    Exit
End If

Dim ret, i
ret = !MsgBox("将" + Str(SelectedUnit) + "号单元参数复制到其他使能单元，确认？", 3)
If ret <> 1 Then Exit Sub

' 定义参数列表
Dim paramList(24) As String
paramList(0) = "VD_C_Set"
paramList(1) = "VD_C_Stock"
paramList(2) = "VD_StepResolution"
paramList(3) = "VD_CycleSetpoint"
paramList(4) = "VD_ExperimentTarget"
paramList(5) = "VD_PreMixTime"
paramList(6) = "VD_PreMixTime_MinSafe"
paramList(7) = "VD_RestTime"
paramList(8) = "VD_RestTime_Min"
paramList(9) = "VD_CycleExtend_Max"
paramList(10) = "VD_T_Default"
paramList(11) = "VD_S6_Default"
paramList(12) = "VD_S4WaitTimeout"
paramList(13) = "VD_Timeout_ValveA"
paramList(14) = "VD_Timeout_ValveB"
paramList(15) = "VD_Timeout_ValveC"
paramList(16) = "VD_Delay_ValveA_Verify"
paramList(17) = "VD_Timeout_Pump1"
paramList(18) = "VD_Timeout_Pump2"
paramList(19) = "VD_ManualDose_Target"
paramList(20) = "VW_ManualDose_Mode"
paramList(21) = "VD_PumpSpeed_Start"
paramList(22) = "VD_PumpSpeed_Max"
paramList(23) = "VD_PumpSpeed_Cutoff"
paramList(24) = "M_AlarmAckMode"

' 复制到其他所有使能单元
For i = 1 To 8
    If i <> SelectedUnit And GetValue("U" + Str(i) + "_UnitEnabled") = 1 Then
        Call CopyParamBetweenUnits(SelectedUnit, i, paramList)
    End If
Next

!MsgBox("参数已复制到其他使能单元", 0, "复制成功")
Call WriteOpLog("复制参数", "源单元" + Str(SelectedUnit))
```

### 脚本 31：`SetValueByUnit` 函数（v2.5不采用）

> McgsPro脚本不支持自定义Sub/Function定义与字符串拼接变量名，本函数无法实施，仅保留为设计说明。实际组态用直接赋值替代（见脚本28）。

```vb
' ============================================
' SetValueByUnit 子过程
' 功能: 向指定单元PLC写入指定参数
' ============================================
Sub SetValueByUnit(unitNum, paramName, value)
    Dim varName
    varName = "U" + Str(unitNum) + "_" + paramName
    Call SetValue(varName, value)
End Sub
```

### 脚本 32：`CopyParamBetweenUnits` 函数（v2.4不采用）

> ⚠ 同脚本31，McgsPro不支持，仅保留为设计说明。

```vb
' ============================================
' CopyParamBetweenUnits 子过程
' 功能: 将源单元参数复制到目标单元
' ============================================
Sub CopyParamBetweenUnits(srcUnit, dstUnit, paramList())
    Dim i, value
    For i = 0 To UBound(paramList)
        value = GetValue("U" + Str(srcUnit) + "_" + paramList(i))
        Call SetValue("U" + Str(dstUnit) + "_" + paramList(i), value)
    Next
End Sub
```

### 脚本 33：`RefreshParamBuffer` 函数（v2.5不采用）

> v2.5采用画面复制法，单元切换即切换画面，Load脚本（脚本27）会自动重新加载，本函数不再需要。

```vb
' ============================================
' RefreshParamBuffer 子过程
' 功能: 从PLC重新加载参数到编辑缓冲
' ============================================
Sub RefreshParamBuffer(unitNum)
    Param_C_Set = GetValue("U" + Str(unitNum) + "_VD_C_Set")
    Param_C_Stock = GetValue("U" + Str(unitNum) + "_VD_C_Stock")
    Param_StepRes = GetValue("U" + Str(unitNum) + "_VD_StepResolution")
    Param_CycleSet = GetValue("U" + Str(unitNum) + "_VD_CycleSetpoint")
    Param_ExpTarget = GetValue("U" + Str(unitNum) + "_VD_ExperimentTarget")
    Param_PreMixTime = GetValue("U" + Str(unitNum) + "_VD_PreMixTime")
    Param_PreMixTime_MinSafe = GetValue("U" + Str(unitNum) + "_VD_PreMixTime_MinSafe")
    Param_RestTime = GetValue("U" + Str(unitNum) + "_VD_RestTime")
    Param_RestTime_Min = GetValue("U" + Str(unitNum) + "_VD_RestTime_Min")
    Param_CycleExtend_Max = GetValue("U" + Str(unitNum) + "_VD_CycleExtend_Max")
    Param_T_Default = GetValue("U" + Str(unitNum) + "_VD_T_Default")
    Param_S6_Default = GetValue("U" + Str(unitNum) + "_VD_S6_Default")
    Param_S4WaitTimeout = GetValue("U" + Str(unitNum) + "_VD_S4WaitTimeout")
    Param_Timeout_ValveA = GetValue("U" + Str(unitNum) + "_VD_Timeout_ValveA")
    Param_Timeout_ValveB = GetValue("U" + Str(unitNum) + "_VD_Timeout_ValveB")
    Param_Timeout_ValveC = GetValue("U" + Str(unitNum) + "_VD_Timeout_ValveC")
    Param_Timeout_Pump1 = GetValue("U" + Str(unitNum) + "_VD_Timeout_Pump1")
    Param_Timeout_Pump2 = GetValue("U" + Str(unitNum) + "_VD_Timeout_Pump2")
    Param_Delay_ValveA_Verify = GetValue("U" + Str(unitNum) + "_VD_Delay_ValveA_Verify")
    Param_ManualDose_Target = GetValue("U" + Str(unitNum) + "_VD_ManualDose_Target")
    Param_ManualDose_Mode = GetValue("U" + Str(unitNum) + "_VW_ManualDose_Mode")
    Param_PumpSpeed_Start = GetValue("U" + Str(unitNum) + "_VD_PumpSpeed_Start")
    Param_PumpSpeed_Max = GetValue("U" + Str(unitNum) + "_VD_PumpSpeed_Max")
    Param_PumpSpeed_Cutoff = GetValue("U" + Str(unitNum) + "_VD_PumpSpeed_Cutoff")
    Param_AlarmAckMode = GetValue("U" + Str(unitNum) + "_M_AlarmAckMode")
End Sub
```

### 脚本 34：单元切换脚本

**用途**: 点击单元按钮时切换到对应单元的参数画面（v2.5画面复制法）
**位置**: 每个单元按钮的 Click 事件

```vb
' 示例：btn_Unit1 点击事件（v2.5缓冲变量+画面复制法）
SelectedUnit = 1
!OpenWindow("画面4_参数设置_U1")
!CloseWindow("画面4_参数设置")
' 注: 8单元实施时,单元按钮直接打开对应单元的画面副本
'     单画面阶段(仅U1)此脚本仅需 SelectedUnit = N + 按钮高亮
```

### 脚本 35：越限校验（周期执行，v2.5读缓冲变量）

**用途**: 实时检查跨参数关联合理性，显示警告（单参数范围校验由输入框min/max属性在保存时承担，此处仅做界面提示）
**触发**: 画面周期脚本（每500ms执行）

```vb
' ============================================
' 参数越限校验脚本 (v2.5: 读缓冲变量)
' ============================================

' 预循环下限 ≤ 预循环时长
IF Param_PreMixTime_MinSafe > Param_PreMixTime THEN
    lbl_Warning1.Visible = 1
ELSE
    lbl_Warning1.Visible = 0
ENDIF

' 静止等候下限 ≤ 静止等候标称
IF Param_RestTime_Min > Param_RestTime THEN
    lbl_Warning2.Visible = 1
ELSE
    lbl_Warning2.Visible = 0
ENDIF

' 顺延上限 ≤ 换水周期
IF Param_CycleExtend_Max > Param_CycleSet THEN
    lbl_Warning3.Visible = 1
ELSE
    lbl_Warning3.Visible = 0
ENDIF
```

> 注：警告标签文字为静态内容（设计期填好"预循环下限不得大于标称值"等），脚本只控制可见性，红色样式在标签属性中配置。块IF必须ENDIF，单行IF不需要。

---

## 六、HMI 内部变量

### 6.1 编辑缓冲变量（v2.5启用）

输入框绑定到以下HMI内部缓冲变量（类型REAL，除标注INT外），实时数据库中必须创建：

| 变量名 | 类型 | 说明 |
|---|---|---|
| Param_C_Set | REAL | 目标浓度编辑缓冲 |
| Param_C_Stock | REAL | 母液浓度编辑缓冲 |
| Param_StepRes | REAL | 单步分辨率编辑缓冲 |
| Param_CycleSet | REAL | 换水周期编辑缓冲 |
| Param_ExpTarget | REAL | 实验时长目标编辑缓冲 |
| Param_PreMixTime | REAL | 预循环标称编辑缓冲 |
| Param_PreMixTime_MinSafe | REAL | 预循环下限编辑缓冲 |
| Param_RestTime | REAL | 静止等候标称编辑缓冲 |
| Param_RestTime_Min | REAL | 静止等候下限编辑缓冲 |
| Param_CycleExtend_Max | REAL | 顺延上限编辑缓冲 |
| Param_T_Default | REAL | 首轮T时长编辑缓冲 |
| Param_S6_Default | REAL | 首轮S6时长编辑缓冲 |
| Param_S4WaitTimeout | REAL | S4等待超时阈值编辑缓冲 |
| Param_Timeout_ValveA | REAL | 阀A超时编辑缓冲 |
| Param_Timeout_ValveB | REAL | 阀B超时编辑缓冲 |
| Param_Timeout_ValveC | REAL | 阀C超时编辑缓冲 |
| Param_Delay_ValveA_Verify | REAL | 阀A延时编辑缓冲 |
| Param_Timeout_Pump1 | REAL | 泵1超时编辑缓冲 |
| Param_Timeout_Pump2 | REAL | 泵2超时编辑缓冲 |
| Param_ManualDose_Target | REAL | 手动总量编辑缓冲 |
| Param_ManualDose_Mode | INT | 注射泵模式编辑缓冲 |
| Param_PumpSpeed_Start | REAL | 启动速度编辑缓冲 |
| Param_PumpSpeed_Max | REAL | 最高速度编辑缓冲 |
| Param_PumpSpeed_Cutoff | REAL | 截止速度编辑缓冲 |
| Param_AlarmAckMode | INT | 报警模式编辑缓冲 |

### 6.2 控制变量

| 变量名 | 类型 | 初始值 | 说明 |
|---|---|---|---|
| SelectedUnit | INT | 1 | 当前选中单元 |
| ParamTargetUnit | INT | 1 | 参数目标单元 |
| LoginLevel | INT | 0 | 当前登录等级（系统变量） |

### 6.3 变量使用说明（v2.5）

- **编辑缓冲**：输入框绑定到 `Param_*` 缓冲变量，避免编辑过程中直接写入PLC
- **加载时填充**：画面打开/单元切换时，Load脚本（脚本27）从PLC读取值填充到缓冲变量
- **保存时写回**：点击【保存参数】按钮，脚本28校验后把缓冲变量直接赋值给PLC变量

---

## 七、安全机制

### 7.1 三级权限控制

| 操作 | 所需权限 | 实现方式 |
|---|---|---|
| 进入参数设置页 | L2（维护组） | 画面属性→进入权限 |
| 修改浓度/步分辨率 | L3（管理员） | 输入框安全属性→表达式 |
| 修改其他参数 | L2（维护组） | 输入框安全属性→表达式 |
| 保存参数 | L2（维护组） | 按钮权限属性 |
| 恢复默认 | L3（管理员） | 按钮权限属性 |
| 复制参数 | L3（管理员） | 按钮权限属性 |

### 7.2 运行中锁定

所有参数输入框附加条件：
```
LoginLevel >= X AND U{N}_VW2_StateMachine == 0
```
即只有在 S0（初始化/空闲）状态下才允许编辑，运行中（S1~S7、Error）自动变灰锁定。

### 7.3 二次确认（v2.6：页面内确认面板）

- **参数修改**：点击【保存参数】按钮后，页面内显示确认面板（pnlConfirmBG + lblConfirmText + btnConfirmOK + btnConfirmCancel），显示"将修改X号单元25个参数，确认保存？"，点【确定】后脚本28a把缓冲变量写入PLC，点【取消】则隐藏面板（缓冲变量不变，PLC也不变）
- **恢复默认**：同样使用确认面板，显示"将恢复X号单元参数到默认值，确认？"，确定后执行恢复默认脚本
- **复制**：同样使用确认面板，显示"将X号单元参数复制到其他使能单元，确认？"，确定后执行复制脚本
- 所有二次确认均通过页面内隐藏面板实现，不依赖 `!MsgBox` / `!OpenWindow` / `!SetWindow`

### 7.4 越限校验（v2.6：保存按钮脚本承担）

单参数范围校验（脚本28中逐个IF判断，越限则在确认面板显示错误信息并隐藏"确定"按钮，不写入PLC）：
| 校验项 | 规则 |
|---|---|
| 目标浓度 | 0~50% |
| 母液浓度 | 0~100% |
| 换水周期 | 1~1440min |
| 首轮T时长 | 60~900s |
| 首轮S6时长 | 30~600s |
| 其余参数 | 见8.2参数允许范围表 |

跨参数关联校验（脚本35周期校验，实时显示越限警告标签，红色文字）：
| 校验项 | 规则 |
|---|---|
| 预循环下限≤标称 | MinSafe ≤ PreMixTime |
| 静止下限≤标称 | Min ≤ RestTime |
| 顺延上限≤周期 | Extend ≤ CycleSet |

---

## 八、默认值与范围表

### 8.1 参数默认值

| 参数名 | 默认值 | 单位 | PLC地址 |
|---|---|---|---|
| VD_C_Set | 5.0 | % | VD10 |
| VD_C_Stock | 100.0 | % | VD14 |
| VD_StepResolution | 4.1667 | µL/步 | VD350 |
| VD_CycleSetpoint | 30.0 | min | VD354 |
| VD_ExperimentTarget | 480.0 | min | VD24 |
| VD_PreMixTime | 120.0 | s | VD28 |
| VD_PreMixTime_MinSafe | 30.0 | s | VD32 |
| VD_RestTime | 60.0 | s | VD36 |
| VD_RestTime_Min | 15.0 | s | VD40 |
| VD_CycleExtend_Max | 5.0 | min | VD44 |
| VD_T_Default | 300.0 | s | VD144 |
| VD_S6_Default | 180.0 | s | VD108 |
| VD_S4Wait_Time | 0.0 | s | VD380 |
| VD_S4WaitTimeout | 1800.0 | s | VD382 |
| VD_Timeout_ValveA | 60.0 | s | VD358 |
| VD_Timeout_ValveB | 60.0 | s | VD362 |
| VD_Timeout_ValveC | 60.0 | s | VD54 |
| VD_Delay_ValveA_Verify | 5.0 | s | VD66 |
| VD_Timeout_Pump1 | 10.0 | s | VD58 |
| VD_Timeout_Pump2 | 10.0 | s | VD62 |
| VD_ManualDose_Target | 0.0 | mL | VD384 |
| VW_ManualDose_Mode | 0 | — | VW388 |
| VD_PumpSpeed_Start | 450.0 | Hz | VD132 |
| VD_PumpSpeed_Max | 700.0 | Hz | VD136 |
| VD_PumpSpeed_Cutoff | 450.0 | Hz | VD140 |
| M_AlarmAckMode | 0 | — | V200.0 |

### 8.2 参数允许范围

| 参数名 | 最小值 | 最大值 | 单位 |
|---|---|---|---|
| VD_C_Set | 0 | 50 | % |
| VD_C_Stock | 0 | 100 | % |
| VD_StepResolution | 0.0001 | 10 | µL/步 |
| VD_CycleSetpoint | 1 | 1440 | min |
| VD_ExperimentTarget | 1 | 10000 | min |
| VD_PreMixTime | 1 | 600 | s |
| VD_PreMixTime_MinSafe | 1 | 300 | s |
| VD_RestTime | 1 | 300 | s |
| VD_RestTime_Min | 1 | 120 | s |
| VD_CycleExtend_Max | 0 | 30 | min |
| VD_T_Default | 60 | 900 | s |
| VD_S6_Default | 30 | 600 | s |
| VD_Timeout_ValveA/B/C | 1 | 300 | s |
| VD_Delay_ValveA_Verify | 1 | 30 | s |
| VD_Timeout_Pump1/Pump2 | 1 | 120 | s |
| VD_S4Wait_Time | 0 | 86400 | s |
| VD_S4WaitTimeout | 60 | 7200 | s |
| VD_ManualDose_Target | 0 | 50 | mL |
| VD_PumpSpeed_Start | 100 | 6000 | Hz |
| VD_PumpSpeed_Max | 100 | 6000 | Hz |
| VD_PumpSpeed_Cutoff | 50 | 5400 | Hz |
| VW_ManualDose_Mode | 0 | 1 | — |
| M_AlarmAckMode | 0 | 1 | — |

### 8.3 PLC自动计算参数（无需HMI设置）

以下参数由PLC程序自动计算或初始化，**不在HMI参数设置页中提供编辑入口**：

| 地址 | 符号 | 单位 | 计算方式 | 说明 |
|---|---|---|---|---|
| VD350 | VD_StepResolution | µL/步 | 硬编码 `4.1667` | 25mL注射器6000步模式，冷启动时写入，HMI仅显示不可编辑 |
| VD370 | VD_Vol_Target | µL | `C_Set × 进水量 / C_Stock` | 目标加药量，S1完成后自动计算，HMI可只读显示 |
| VD366 | VD_ExperimentDuration_Accum | min | S5运行中自动累加 | 实验时长累计值，HMI只读显示 |
| VD112 | VD_T_Rolling | s | S1实测+S2标称+S3估算+S3.5标称 | 滚动实测T，首轮由VD144播种，之后自动学习，HMI只读显示 |
| VD116 | VD_S6_Rolling | s | S6实测 | 滚动实测S6排水时长，首轮由VD108播种，之后自动学习，HMI只读显示 |
| VD380 | VD_S4Wait_Time | s | S4 等待期间 PLC 自动累加(每秒+1),S4 完成时清零 | S4 入口 V1.7=1 持续时间,HMI 只读显示,操作员可监控 S4 等待 |

**设计说明**：
- T(VD144)/S6(VD108)为HMI设定参数（时间周期组4-047/4-048），**仅首轮生效**：实验启动时FC10播种VD112←VD144、VD116←VD108，首轮完成后由实测值自动学习覆盖
- v2.3地址迁移：VD_T_Default由VD104迁移至VD144。原因：VD104与VD_Dose_Steps(VD102)字节重叠VB104~105，FC13/FC21每次写加药步数都会破坏T值（300.0会被写成0.0），属原设计地址分配缺陷
- 手动加药量(VD384)在HMI以mL输入，PLC内部以µL存储（数据缩放系数1000）

---

## 九、组态验收 Checklist

| # | 验收项 | 确认 |
|---|---|---|
| 1 | 画面4创建完成，尺寸1280×800 | □ |
| 2 | 25个参数输入框全部创建并**绑定Param_*缓冲变量**（v2.5 + v2.7新增 S4WaitTimeout），1 个只读显示(VD_S4Wait_Time) | □ |
| 3 | 25个Param_*缓冲变量在实时数据库中已创建 | □ |
| 4 | 输入框最小值/最大值已设置（保存脚本二次校验） | □ |
| 5 | 输入框权限配置正确（浓度L3/其他L2） | □ |
| 6 | 运行中所有输入框灰色不可编辑（VW2==0条件） | □ |
| 7 | Load脚本（脚本27）配置完成，画面打开时缓冲变量正确加载PLC值 | □ |
| 8 | 保存按钮脚本（脚本28）配置完成，校验/确认/写入PLC正常 | □ |
| 9 | 保存按钮权限L2+，运行中锁定 | □ |
| 9a | 二次确认面板控件4-090~4-093已创建，初始Visible=0 | □ |
| 9b | 保存按钮脚本28能正确显示确认面板（校验通过/越限两种状态） | □ |
| 9c | 确认按钮脚本28a能正确写入PLC并隐藏面板 | □ |
| 9d | 取消按钮脚本28b能正确隐藏面板且不写入PLC | □ |
| 10 | 参数修改后点"取消"不写入PLC | □ |
| 11 | 单元选择器8按钮创建，点击切换正常 | □ |
| 12 | 标签页切换5按钮创建，点击显隐对应面板 | □ |
| 13 | 恢复默认按钮脚本（脚本29）配置完成 | □ |
| 14 | 复制按钮脚本（脚本30，首期可禁用）配置完成 | □ |
| 15 | 越限校验脚本（脚本35读缓冲变量版）配置完成 | □ |
| 16 | 参数越限时红色警告标签显示 | □ |
| 17 | 画面标题动态显示"参数设置 - X号单元" | □ |
| 18 | 1号单元参数加载/保存/恢复默认正常 | □ |
| 19 | 退出画面无错误 | □ |

---

## 十、版本历史

| 版本 | 日期 | 说明 |
|---|---|---|
| v1.0 | 2026-07-15 | 初始版本（McgsPro画面组态SOP_8画面_v2.0 第七章） |
| v2.0 | 2026-08-15 | 整合McgsPro脚本代码_54个_v2.0 第六章F节 |
| v2.1 | 2026-08-23 | 整合所有版本，补充注射泵参数组、报警模式、完整脚本库 |
| v2.4 | 2026-08-24 | 参数写入架构变更为"输入框直接绑定+操作确认"：取消保存按钮及Param_*缓冲变量；脚本28废弃、脚本31/32/33标注不采用；脚本27/34/35按直接绑定重构；范围校验改由输入框min/max属性承担 |
| v2.5 | 2026-08-24 | 修正v2.4：McgsPro该版本安全属性页无"操作确认"，改回"输入框绑定Param_*缓冲变量+保存按钮汇总写入PLC"；恢复保存按钮和Param_*变量；脚本27/28/35重写为McgsPro可用直接赋值语法；脚本29/30/31/32/33标注不采用或需直接赋值改造 |
| v2.6 | 2026-08-24 | 修正v2.5：该版本McgsPro中!MsgBox/!OpenWindow/!SetWindow均不兼容字符串参数，二次确认改为"页面内隐藏确认面板"方案；新增控件4-090~4-093；脚本28拆分为28/28a/28b，通过Visible属性控制显示/隐藏；文档内所有弹窗/子窗口引用同步修正 |

**关联文件**:
- `archive/mcgspro/McgsPro画面组态SOP_8画面_v2.0.md` — 原画面布局SOP
- `archive/mcgspro/McgsPro脚本代码_54个_v2.0.md` — 原脚本库
- `archive/mcgspro/MCGS画面组态详细SOP_v1.0.md` — 原详细SOP
- `archive/mcgspro/MCGS组态脚本代码_v1.0.md` — 原脚本代码v1.0
- `archive/mcgspro/MCGS通讯配置SOP_v1.0.md` — 通讯配置