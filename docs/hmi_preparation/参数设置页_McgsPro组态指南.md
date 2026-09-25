# 参数设置页（画面4）McgsPro 组态指南

**版本**: v2.9（整合版）
**创建日期**: 2026-08-23
**更新日期**: 2026-09-17 (v2.9: 脚本重写与 v2.2 时间参数补全 —
  (1) 脚本 27 (Load) / 脚本 28a (保存执行) / 脚本 33 (RefreshParamBuffer) 三段中
      所有 `U1_VD_xxx = Param_xxx` / `Param_xxx = U1_VD_xxx` 改为对用户默认镜像
      `U1_UD_VDxxx` / `Param_xxx = U1_UD_VDxxx`,符合 v2.2 双阶段保存语义;
  (2) 删除 v2.1 已废弃的三层纠偏 / 静止等候 / 旧 S6 等待 / 预循环下限 等
      变量 (VD32/36/40/44/112/120/124/128/144/354 等);
  (3) 新增 v2.2 时间参数三个: 24h 换水次数 (VD414, 镜像 VD468),
      周期尾端转移余量 (VD426, 镜像 VD476), 上缸配液安全余量 (VD430, 镜像 VD480);
      v2.2 后 PLC 端 SBR25_ColdStart.stl 已补对应 MOVR 覆盖行。
  (4) 校验段 / 恢复默认 / 复制参数列表 / 关联校验 / Param_缓冲表 / 默认值与范围表
      / PLC 自动计算参数段 / 验收 Checklist / 版本历史 全部同步重写);
  v2.8 (2026-09-16): 修正 v2.7 地址错位 — `VD380/VD382` 改为 `VD444/VD448`;
  v2.7: 合并远程 v1.2 新增 S4 等待时长显示与超时阈值; v2.6: 页面内隐藏确认面板;
  v2.5: 输入框绑定 Param_* 缓冲变量 + 保存按钮; v2.4: 直接绑定 + 操作确认;
  v2.3: T/S6 改回 HMI 设定参数, VD_T_Default 迁移至 VD144
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
| 4-040a | 标签 | lbl_S4WaitTime | S4等待时长(只读) | U{N}_VD_S4Wait_Time(VD444) | 0~86400 | s |
| 4-040b | 标签+输入框 | lbl_S4WaitTimeout / num_S4WaitTimeout | S4等待超时阈值 | U{N}_VD_S4WaitTimeout(VD448) | 60~7200 | s |
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

**用途**: 画面打开时从 PLC 读取**用户默认镜像**到 Param_* 缓冲变量
**位置**: 用户窗口 → 画面4_参数设置 → Load 事件
**v2.9 变更**: 从读真值 `U1_VD_xxx` 改为读用户默认镜像 `U1_UD_VDxxx`,符合 SBR25 双阶段保存语义;
            并删除全部 v2.1 已删变量 (C_Set/C_Stock/PreMixMinSafe/RestTime 等)。

```vb
' ============================================
' 画面4_参数设置 Load 脚本 (v2.9: 读用户默认镜像到缓冲)
' 功能: 把 U1 单元的 PLC 用户默认镜像区读到 Param_* 缓冲变量供输入框显示
' 注: McgsPro不支持动态变量名拼接,首期写死U1;8单元时复制画面改前缀
'     SBR25冷启动时按 VD456=1 检查镜像区是否有效,有效则覆盖到真值
' ============================================

' 实验工艺参数 (工艺 + 进水 + 加药 + 单步分辨率)
Param_ExpTarget       = U1_UD_VD24_ExpTarget            ' VD24 实验时长目标 (min)
Param_PreMixTime      = U1_UD_VD28_PreMixTime           ' VD28 S2 搅拌+加药固定时长 (s)
Param_InletVol        = U1_UD_VD316_InletVol            ' VD316 目标进水量 (L)
Param_VolTarget       = U1_UD_VD584_VolTarget           ' VD584 本轮目标加药量 (µL)
Param_StepRes         = U1_UD_VD350_StepRes             ' VD350 注射泵单步分辨率 (µL/步)

' v2.2 时间周期参数 (双倒计时器体系)
Param_24h_Target      = U1_UD_VD414_24h_Target          ' VD414 24h换水目标次数 (新增)
Param_TransferMargin  = U1_UD_VD426_Transfer_Margin     ' VD426 周期尾端转移余量 (s) (新增)
Param_SafetyMargin    = U1_UD_VD430_Safety_Margin       ' VD430 上缸配液安全余量 (s) (新增)
Param_S4WaitTimeout   = U1_UD_VD448_S4WaitTimeout       ' VD448 S4 等待超时阈值 (s)

' 超时保护参数
Param_Timeout_ValveA    = U1_UD_VD358_TimeoutA          ' VD358 阀A动作超时 (s)
Param_Timeout_ValveB    = U1_UD_VD362_TimeoutB          ' VD362 阀B动作超时 (s)
Param_Timeout_ValveC    = U1_UD_VD54_TimeoutC           ' VD54  阀C动作超时 (s)
Param_Delay_ValveA      = U1_UD_VD66_DelayA             ' VD66  阀A关闭延时验证 (s)
Param_Delay_ValveC      = U1_UD_VD60_DelayC             ' VD472 排液完成验证延时 (s) (v3.1新增, UD存VD492; 工作地址2026-09-24由VD60迁VD472, 原地址与V6x位缓存区冲突)

' 手动模式
Param_ManualDose_Target = U1_UD_VD452_ManualDose         ' VD452 手动注射泵总加药量 (µL)

' 状态位 / 报警模式 (从 PLC 读真值)
Param_ManualDose_Mode = U1_VW_ManualDose_Mode           ' VW388 手动模式 0=单次/1=循环 (读真值)
Param_AlarmAckMode    = U1_M_AlarmAckMode              ' V200.0 报警确认模式 (读真值)

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
' 保存参数按钮脚本 (v2.9: 页面内确认面板版, 改写为校验镜像参数)
' 功能: 1.范围校验 2.显示确认面板 3.用户点"确定"后将 Param_* 写入用户默认镜像 U1_UD_VDxxx
'       HMI 不再写真值 (U1_VD_xxx); 冷启动时 SBR25 按 VD456 标志将镜像覆盖到真值
' 约束: 无自定义函数、无动态变量名、块IF必须ENDIF
'       该版本McgsPro不支持!MsgBox/!OpenWindow/!SetWindow字符串参数
' ============================================

' --- 1. 范围校验（越限时只显示错误提示，不显示"确定"按钮） ---

' 实验工艺参数
IF Param_ExpTarget < 1 OR Param_ExpTarget > 10000 THEN
    lblConfirmText.Caption = "错误：实验时长目标超范围(1~10000min)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_PreMixTime < 5 OR Param_PreMixTime > 120 THEN
    lblConfirmText.Caption = "错误：S2搅拌+加药固定时长超范围(5~120s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_InletVol < 1 OR Param_InletVol > 50 THEN
    lblConfirmText.Caption = "错误：目标进水量超范围(1~50L)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_VolTarget < 100 OR Param_VolTarget > 10000 THEN
    lblConfirmText.Caption = "错误：本轮目标加药量超范围(100~10000µL)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_StepRes < 0.0001 OR Param_StepRes > 10 THEN
    lblConfirmText.Caption = "错误：单步分辨率超范围(0.0001~10µL/步)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF

' v2.2 时间周期参数 (双倒计时器体系)
IF Param_24h_Target < 1 OR Param_24h_Target > 48 THEN
    lblConfirmText.Caption = "错误：24h换水目标次数超范围(1~48次)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_TransferMargin < 10 OR Param_TransferMargin > 60 THEN
    lblConfirmText.Caption = "错误：周期尾端转移余量超范围(10~60s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_SafetyMargin < 5 OR Param_SafetyMargin > 30 THEN
    lblConfirmText.Caption = "错误：上缸配液安全余量超范围(5~30s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_S4WaitTimeout < 60 OR Param_S4WaitTimeout > 7200 THEN
    lblConfirmText.Caption = "错误：S4等待超时阈值超范围(60~7200s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF

' v2.2 跨参数关联校验：避免 T_single - Transfer_Margin - Safety_Margin <= 0
' T_single = 86400 / 24h_Target (秒). 当 T_cycle ≤ 0 时 FC40 NETWORK 1 报警 V303.6.
IF Param_TransferMargin + Param_SafetyMargin >= 86400.0 / Param_24h_Target THEN
    lblConfirmText.Caption = "错误：转移余量+配液余量已超过单次周期，禁止保存"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF

' 超时保护参数
IF Param_Timeout_ValveA < 10 OR Param_Timeout_ValveA > 600 THEN
    lblConfirmText.Caption = "错误：阀A动作超时超范围(10~600s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_Timeout_ValveB < 10 OR Param_Timeout_ValveB > 600 THEN
    lblConfirmText.Caption = "错误：阀B动作超时超范围(10~600s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_Timeout_ValveC < 10 OR Param_Timeout_ValveC > 600 THEN
    lblConfirmText.Caption = "错误：阀C动作超时超范围(10~600s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_Delay_ValveA < 1 OR Param_Delay_ValveA > 30 THEN
    lblConfirmText.Caption = "错误：阀A关闭延时验证超范围(1~30s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF
IF Param_Delay_ValveC < 0 OR Param_Delay_ValveC > 60 THEN
    lblConfirmText.Caption = "错误：排液完成验证延时超范围(0~60s)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF

' 手动加药
IF Param_ManualDose_Target < 0 OR Param_ManualDose_Target > 50000 THEN
    lblConfirmText.Caption = "错误：手动注射泵总加药量超范围(0~50000µL)"
    btnConfirmOK.Visible = 0 : btnConfirmCancel.Visible = 1
    pnlConfirmBG.Visible = 1 : lblConfirmText.Visible = 1
    EXIT
ENDIF

' --- 2. 校验通过，显示确认面板 ---
lblConfirmText.Caption = "将修改" + !Str(SelectedUnit) + "号单元16个参数（含3个v2.2时间参数），确认保存？"
btnConfirmOK.Visible = 1
btnConfirmCancel.Visible = 1
pnlConfirmBG.Visible = 1
lblConfirmText.Visible = 1
```

### 脚本 28a：确认按钮（btnConfirmOK）

**位置**: 画面4_参数设置 → btnConfirmOK → Click 事件

```vb
' --- 写回用户默认镜像（v2.9: 不写真值 U1_VD_xxx，写镜像 U1_UD_VDxxx） ---
' 实验工艺参数
U1_UD_VD24_ExpTarget     = Param_ExpTarget
U1_UD_VD28_PreMixTime    = Param_PreMixTime
U1_UD_VD316_InletVol     = Param_InletVol
U1_UD_VD584_VolTarget    = Param_VolTarget
U1_UD_VD350_StepRes      = Param_StepRes

' v2.2 时间周期参数
U1_UD_VD414_24h_Target   = Param_24h_Target
U1_UD_VD426_Transfer_Margin = Param_TransferMargin
U1_UD_VD430_Safety_Margin = Param_SafetyMargin
U1_UD_VD448_S4WaitTimeout = Param_S4WaitTimeout

' 超时保护参数
U1_UD_VD358_TimeoutA     = Param_Timeout_ValveA
U1_UD_VD362_TimeoutB     = Param_Timeout_ValveB
U1_UD_VD54_TimeoutC      = Param_Timeout_ValveC
U1_UD_VD66_DelayA        = Param_Delay_ValveA
U1_UD_VD60_DelayC        = Param_Delay_ValveC

' 手动加药
U1_UD_VD452_ManualDose   = Param_ManualDose_Target

' 镜像有效标志 (v2.9: 用户实际点保存即视为镜像有效, 等 SBR25 VD456 检查)
' 此前单元 1 CSV 没有 U1_UD_Flag 行, 这里补上 (可选)
U1_UD_Flag = 1

' 注: ManualDose_Mode / AlarmAckMode 从真值读,不参与保存;
'     这两个参数由现场调试工程师通过其他途径(按钮/工具)调节。

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

**用途**: 恢复当前单元参数到默认值（写入用户默认镜像）
**位置**: btnRestoreDefault → Click 事件

> **v2.5实施提示**：以下脚本已改为McgsPro支持的直接赋值语法（参考脚本28），首期U1写死，8单元时复制画面改`U1_`前缀。
> **v2.9变更**：恢复默认写入用户默认镜像 `U1_UD_VDxxx` (非真值)，与 SBR25 双阶段保存语义一致；默认值表与 §8.1 同步。

```vb
' ============================================
' 恢复默认按钮脚本 (v2.9)
' ============================================

If LoginLevel < 3 Then
    !MsgBox("恢复默认需管理员(L3)权限", 0, "权限提示")
    Exit
End If

Dim ret
ret = !MsgBox("将恢复" + Str(SelectedUnit) + "号单元参数到默认值，确认？", 3)
If ret <> 1 Then Exit Sub

' 实验工艺参数 (5 项)
U1_UD_VD24_ExpTarget  = 480.0    ' min   实验时长目标
U1_UD_VD28_PreMixTime = 10.0     ' s     S2 搅拌+加药固定时长
U1_UD_VD316_InletVol  = 10.0     ' L     目标进水量
U1_UD_VD584_VolTarget = 5000.0   ' µL    本轮目标加药量
U1_UD_VD350_StepRes   = 4.1667   ' µL/步 单步分辨率

' v2.2 时间周期参数 (4 项)
U1_UD_VD414_24h_Target   = 24.0  ' 次    24h换水目标
U1_UD_VD426_Transfer_Margin = 30.0 ' s    周期尾端转移余量
U1_UD_VD430_Safety_Margin = 10.0  ' s    上缸配液安全余量
U1_UD_VD448_S4WaitTimeout = 1800.0 ' s   S4 等待超时阈值

' 超时保护参数 (4 项)
U1_UD_VD358_TimeoutA = 60.0   ' s   阀A动作超时
U1_UD_VD362_TimeoutB = 60.0   ' s   阀B动作超时
U1_UD_VD54_TimeoutC  = 60.0   ' s   阀C动作超时
U1_UD_VD66_DelayA    = 5.0    ' s   阀A关闭延时验证
U1_UD_VD60_DelayC    = 5.0    ' s   排液完成验证延时 (v3.1新增)

' 手动加药 (1 项)
U1_UD_VD452_ManualDose = 10000.0 ' µL  手动注射泵总加药量

' 镜像有效标志
U1_UD_Flag = 1

' 刷新编辑缓冲变量 (从新值读回)
Call RefreshParamBuffer(SelectedUnit)

!MsgBox("参数已恢复默认", 0, "恢复成功")
```

### 脚本 30：复制到其他单元按钮

**用途**: 将当前单元参数复制到其他单元
**位置**: btnCopyToOthers → Click 事件

> **v2.5实施提示**：McgsPro不支持数组和自定义函数，复制功能建议利用McgsPro"配方"组件，或展开为逐参数直接赋值（如`U2_VD_C_Set = U1_VD_C_Set`）。首期仅U1时本按钮可禁用或暂不实施。
> **v2.9变更**：参数列表改为 16 项镜像名（v2.1 的 25 项已废弃项全部删除，新增 v2.2 时间参数 3 项）。

```vb
' ============================================
' 复制到其他单元按钮脚本 (v2.9)
' ============================================

If LoginLevel < 3 Then
    !MsgBox("复制参数需管理员(L3)权限", 0, "权限提示")
    Exit
End If

Dim ret, i
ret = !MsgBox("将" + Str(SelectedUnit) + "号单元参数复制到其他使能单元，确认？", 3)
If ret <> 1 Then Exit Sub

' 15 项镜像名参数列表 (v2.9: 仅含 v2.2 实际有效项, 共 14 个真实镜像 + 1 个标志位)
Dim paramList(15) As String
paramList(0)  = "UD_VD24_ExpTarget"
paramList(1)  = "UD_VD28_PreMixTime"
paramList(2)  = "UD_VD316_InletVol"
paramList(3)  = "UD_VD350_StepRes"
paramList(4)  = "UD_VD584_VolTarget"
paramList(5)  = "UD_VD414_24h_Target"
paramList(6)  = "UD_VD426_Transfer_Margin"
paramList(7)  = "UD_VD430_Safety_Margin"
paramList(8)  = "UD_VD448_S4WaitTimeout"
paramList(9)  = "UD_VD358_TimeoutA"
paramList(10) = "UD_VD362_TimeoutB"
paramList(11) = "UD_VD54_TimeoutC"
paramList(12) = "UD_VD66_DelayA"
paramList(13) = "UD_VD452_ManualDose"
paramList(14) = "UD_VD60_DelayC"
paramList(15) = "UD_Flag"

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
> **v2.9变更**：本节保留 RefreshParamBuffer 作为"恢复默认"按钮的辅助刷新逻辑（脚本29 末尾调用），如未启用可保持空。下列赋值方向同步改为读用户默认镜像，参数集与 §6.1 缓冲变量表一致。

```vb
' ============================================
' RefreshParamBuffer 子过程 (v2.9: 读用户默认镜像)
' 功能: 从PLC用户默认镜像重新加载参数到编辑缓冲
' ============================================
Sub RefreshParamBuffer(unitNum)
    Dim pfx
    pfx = "U" + Str(unitNum) + "_"

    ' 实验工艺参数
    Param_ExpTarget       = GetValue(pfx + "UD_VD24_ExpTarget")
    Param_PreMixTime      = GetValue(pfx + "UD_VD28_PreMixTime")
    Param_InletVol        = GetValue(pfx + "UD_VD316_InletVol")
    Param_VolTarget       = GetValue(pfx + "UD_VD584_VolTarget")
    Param_StepRes         = GetValue(pfx + "UD_VD350_StepRes")

    ' v2.2 时间周期参数
    Param_24h_Target      = GetValue(pfx + "UD_VD414_24h_Target")
    Param_TransferMargin  = GetValue(pfx + "UD_VD426_Transfer_Margin")
    Param_SafetyMargin    = GetValue(pfx + "UD_VD430_Safety_Margin")
    Param_S4WaitTimeout   = GetValue(pfx + "UD_VD448_S4WaitTimeout")

    ' 超时保护参数
    Param_Timeout_ValveA  = GetValue(pfx + "UD_VD358_TimeoutA")
    Param_Timeout_ValveB  = GetValue(pfx + "UD_VD362_TimeoutB")
    Param_Timeout_ValveC  = GetValue(pfx + "UD_VD54_TimeoutC")
    Param_Delay_ValveA    = GetValue(pfx + "UD_VD66_DelayA")
    Param_Delay_ValveC    = GetValue(pfx + "UD_VD60_DelayC")

    ' 手动加药
    Param_ManualDose_Target = GetValue(pfx + "UD_VD452_ManualDose")

    ' ManualDose_Mode / AlarmAckMode 从真值读
    Param_ManualDose_Mode = GetValue(pfx + "VW_ManualDose_Mode")
    Param_AlarmAckMode    = GetValue(pfx + "M_AlarmAckMode")
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

### 脚本 35：越限校验（周期执行，v2.9读缓冲变量）

**用途**: 实时检查跨参数关联合理性，显示警告（单参数范围校验由输入框min/max属性在保存时承担，此处仅做界面提示）
**触发**: 画面周期脚本（每500ms执行）
**v2.9变更**: 删除 v2.1 三层纠偏相关警告（预循环下限/静止等候下限/顺延上限），替换为 v2.2 双倒计时器关联警告。

```vb
' ============================================
' 参数越限校验脚本 (v2.9: 读缓冲变量 + v2.2 关联校验)
' ============================================

' 警告 1: 转移余量 + 配液余量 ≥ 单次周期 → FC40 V303.6 报警触发
IF Param_TransferMargin + Param_SafetyMargin >= 86400.0 / Param_24h_Target THEN
    lbl_Warning1.Visible = 1
ELSE
    lbl_Warning1.Visible = 0
ENDIF

' 警告 2: 单次倒计时余额已耗尽 (当 Prep_Needed ≥ T_single)
' 即 S1 实测 + S2 固定 + SafetyMargin ≥ T_single - TransferMargin, 极易触发下一轮 S1 但同时 S5 时长不够
IF (Param_PreMixTime + Param_SafetyMargin) >= 86400.0 / Param_24h_Target - Param_TransferMargin THEN
    lbl_Warning2.Visible = 1
ELSE
    lbl_Warning2.Visible = 0
ENDIF

' 警告 3: S4 等待阈值过宽（>3600s）通常意味着下缸排空异常,需关注
IF Param_S4WaitTimeout > 3600 THEN
    lbl_Warning3.Visible = 1
ELSE
    lbl_Warning3.Visible = 0
ENDIF
```

> 注：警告标签文字为静态内容（设计期填好"周期参数过激"等），脚本只控制可见性，红色样式在标签属性中配置。块IF必须ENDIF，单行IF不需要。

---

## 六、HMI 内部变量

### 6.1 编辑缓冲变量（v2.9: 16 项）

输入框绑定到以下HMI内部缓冲变量（类型REAL，除标注INT外），实时数据库中必须创建：

**实验工艺 (5 项)**

| 变量名 | 类型 | 说明 |
|---|---|---|
| Param_ExpTarget | REAL | 实验时长目标编辑缓冲 (min) |
| Param_PreMixTime | REAL | S2 搅拌+加药固定时长编辑缓冲 (s) |
| Param_InletVol | REAL | 目标进水量编辑缓冲 (L) |
| Param_VolTarget | REAL | 本轮目标加药量编辑缓冲 (µL) |
| Param_StepRes | REAL | 单步分辨率编辑缓冲 (µL/步) |

**v2.2 时间周期 (4 项，新参数加粗)**

| 变量名 | 类型 | 说明 |
|---|---|---|
| **Param_24h_Target** | REAL | **24h 换水目标次数编辑缓冲 (1~48次)** |
| **Param_TransferMargin** | REAL | **周期尾端转移余量编辑缓冲 (s)** |
| **Param_SafetyMargin** | REAL | **上缸配液安全余量编辑缓冲 (s)** |
| Param_S4WaitTimeout | REAL | S4 等待超时阈值编辑缓冲 (s) |

**超时保护 (4 项)**

| 变量名 | 类型 | 说明 |
|---|---|---|
| Param_Timeout_ValveA | REAL | 阀A动作超时编辑缓冲 (s) |
| Param_Timeout_ValveB | REAL | 阀B动作超时编辑缓冲 (s) |
| Param_Timeout_ValveC | REAL | 阀C动作超时编辑缓冲 (s) |
| Param_Delay_ValveA | REAL | 阀A关闭延时验证编辑缓冲 (s) |
| Param_Delay_ValveC | REAL | 排液完成验证延时编辑缓冲 (s) (v3.1) |

**手动与报警模式 (2 项)**

| 变量名 | 类型 | 说明 |
|---|---|---|
| Param_ManualDose_Target | REAL | 手动注射泵总加药量编辑缓冲 (µL) |
| Param_AlarmAckMode | INT | 报警确认模式编辑缓冲 (0=自动/1=人工) |

**仅作显示、不经参数设置页写入 (1 项)**

| 变量名 | 类型 | 说明 |
|---|---|---|
| Param_ManualDose_Mode | INT | 手动注射泵模式，只读显示来自 VW388 真值 |

> **v2.9 重大修正**：v2.1 的 25 项变量表中 12 项（VD_C_Set/VD_C_Stock/VD_CycleSetpoint/VD_PreMixTime_MinSafe/VD_RestTime/VD_RestTime_Min/VD_CycleExtend_Max/VD_T_Default/VD_S6_Default/VD_PumpSpeed_Start/Max/Cutoff）对应 PLC 地址已废弃，对应的 Param_* 缓冲变量在本版本中不再定义。

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

### 8.1 参数默认值（v2.9: 仅含 v2.2 实际有效 16 项）

| 参数名 | 默认值 | 单位 | 真值地址 | 镜像地址 |
|---|---|---|---|---|
| **实验工艺** |  |  |  |  |
| VD_ExperimentTarget | 480.0 | min | VD24 | VD460 |
| VD_PreMixTime | 10.0 | s | VD28 | VD464 |
| VD_InletVol | 10.0 | L | VD316 | VD500 |
| VD_VolTarget | 5000.0 | µL | VD584 | VD520 |
| VD_StepResolution | 4.1667 | µL/步 | VD350 | VD504 |
| **v2.2 时间周期（新参数加粗）** |  |  |  |  |
| **VD_24h_Target** | **24.0** | **次** | **VD414** | **VD468** |
| **VD_TransferMargin** | **30.0** | **s** | **VD426** | **VD476** |
| **VD_SafetyMargin** | **10.0** | **s** | **VD430** | **VD480** |
| VD_S4WaitTimeout | 1800.0 | s | VD448 | VD524 |
| **超时保护** |  |  |  |  |
| VD_Timeout_ValveA | 60.0 | s | VD358 | VD512 |
| VD_Timeout_ValveB | 60.0 | s | VD362 | VD516 |
| VD_Timeout_ValveC | 60.0 | s | VD54 | VD484 |
| VD_Delay_ValveA | 5.0 | s | VD66 | VD488 |
| VD_Delay_ValveC | 5.0 | s | VD472 | VD492 |
| **手动与报警模式** |  |  |  |  |
| VD_ManualDose_Target | 10000.0 | µL | VD452 | VD528 |
| VW_ManualDose_Mode | 0 | — | VW388 | VB532 |
| V_AlarmAckMode | 1 | — | V200.0 | VB536 |

> 注：VD_ManualDose_Mode 默认在 v2.9 由 0 改为 1 — 与 PLC 冷启动真实场景一致 (L3 启用时 ALARM_ACK_MODE = 人工确认)。

### 8.2 参数允许范围

| 参数名 | 最小值 | 最大值 | 单位 |
|---|---|---|---|
| **实验工艺** |  |  |  |
| VD_ExperimentTarget | 1 | 10000 | min |
| VD_PreMixTime | 5 | 120 | s |
| VD_InletVol | 1 | 50 | L |
| VD_VolTarget | 100 | 10000 | µL |
| VD_StepResolution | 0.0001 | 10 | µL/步 |
| **v2.2 时间周期** |  |  |  |
| VD_24h_Target | 1 | 48 | 次 |
| VD_TransferMargin | 10 | 60 | s |
| VD_SafetyMargin | 5 | 30 | s |
| VD_S4WaitTimeout | 60 | 7200 | s |
| **超时保护** |  |  |  |
| VD_Timeout_ValveA/B/C | 10 | 600 | s |
| VD_Delay_ValveA | 1 | 30 | s |
| **手动与报警模式** |  |  |  |
| VD_ManualDose_Target | 0 | 50000 | µL |
| VW_ManualDose_Mode | 0 | 1 | — |
| V_AlarmAckMode | 0 | 1 | — |

> **跨参数关联（保存脚本校验 + 周期脚本警告）**：
> - `VD_TransferMargin + VD_SafetyMargin < 86400 / VD_24h_Target` 即 `T_cycle > 0`
> - 否则 FC40 NETWORK 1 报警 V303.6 = 单轮换水周期超时（强制人工确认）

### 8.3 PLC自动计算参数（无需HMI设置）

以下参数由PLC程序自动计算或初始化，**不在HMI参数设置页中提供编辑入口**：

| 地址 | 符号 | 单位 | 计算方式 | 说明 |
|---|---|---|---|---|
| VD366 | VD_ExperimentDuration_Accum | min | S5运行中自动累加 | 实验时长累计值，HMI只读显示 |
| VD256 | VD_TimerA_Display | s | T46_PV/10（每周期更新） | TimerA 当前显示值，HMI 只读 |
| VD244 | VD_TimerB_Display | s | T48_PV/10（每周期更新） | TimerB 当前显示值，HMI 只读 |
| VD116 | VD_S6_Rolling | s | FC15/FC17 实测后赋值 | S6 滚动实测（首轮 = S4 实测），HMI 只读显示 |
| VD444 | VD_S4Wait_Time | s | S4 等待期间 PLC 自动累加（每秒+1），S4 完成时清零 | S4 入口 V1.7=1 持续时间，HMI 只读显示 |
| VW304 | State_UpTank | — | FC1A/FC10/FC15/FC17 维护 | 上缸配液子流程状态（0~4 五态），HMI 只读显示 |
| VW306 | CycleCount | — | FC17 转 S4 时累加 | 已完成下缸换水次数，HMI 只读显示 |

**v2.9 说明**：
- v2.1 时 VD112/VD144 (T 默认值与滚动实测)、VD108 (首轮 S6 默认) 等 v2.1 三层纠偏字段已彻底删除。
- v2.9 引入双倒计时器显示 VD256/VD244（来自 PLC 真空闲区迁移，参 v2.2_实施前置迁移方案_v1.0）。

---

## 九、组态验收 Checklist（v2.9）

| # | 验收项 | 确认 |
|---|---|---|
| 1 | 画面4创建完成，尺寸1280×800 | □ |
| 2 | **16** 个参数输入框全部创建并**绑定 Param_* 缓冲变量**（v2.9 缩减自 v2.7 的 25 项；删除 v2.1 废弃项 + 新增 3 个 v2.2 时间参数 + 1 个 VD_InletVol 与 1 个 VD_VolTarget 重命名）| □ |
| 3 | 16 个 Param_* 缓冲变量在实时数据库中已创建 | □ |
| 4 | 输入框最小值/最大值按 §8.2 设置（保存脚本二次校验） | □ |
| 5 | 输入框权限配置正确（浓度/单步分辨率 L3 / 其他 L2） | □ |
| 6 | 运行中所有输入框灰色不可编辑（VW2==0 条件） | □ |
| 7 | Load 脚本（脚本 27 v2.9）配置完成，画面打开时**从用户默认镜像**加载 Param_* 缓冲 | □ |
| 8 | 保存按钮脚本（脚本 28 v2.9）配置完成，校验包含 v2.2 跨参数关联（TransferMargin+SafetyMargin ≥ 单次周期 报错） | □ |
| 9 | 保存按钮权限 L2+，运行中锁定 | □ |
| 9a | 二次确认面板控件 4-090~4-093 已创建，初始 Visible=0 | □ |
| 9b | 保存按钮脚本 28 能正确显示确认面板（校验通过 / 越限两种状态） | □ |
| 9c | 确认按钮脚本 28a 能正确**写入用户默认镜像 U1_UD_VDxxx** 并隐藏面板（非写真值） | □ |
| 9d | 取消按钮脚本 28b 能正确隐藏面板且不写入镜像 | □ |
| 10 | 参数修改后点"取消"不写入镜像 | □ |
| 11 | 单元选择器 8 按钮创建，点击切换正常 | □ |
| 12 | 标签页切换 5 按钮创建，点击显隐对应面板 | □ |
| 13 | 恢复默认按钮脚本（脚本 29 v2.9）配置完成，写入 14 个镜像 + 设置 UD_Flag=1 | □ |
| 14 | 复制按钮脚本（脚本 30 v2.9）配置完成，15 项镜像名列表 | □ |
| 15 | 越限校验脚本（脚本 35 v2.9）配置完成，3 个 v2.2 关联警告 | □ |
| 16 | 参数越限时红色警告标签显示 | □ |
| 17 | 画面标题动态显示"参数设置 - X号单元" | □ |
| 18 | 1号单元参数加载 / 保存 / 恢复默认正常（含**冷启动 SBR25 覆盖**） | □ |
| 19 | 退出画面无错误 | □ |

---

## 十、版本历史

| 版本 | 日期 | 说明 |
|---|---|---|
| v1.0 | 2026-07-15 | 初始版本（McgsPro画面组态SOP_8画面_v2.0 第七章） |
| v2.0 | 2026-08-15 | 整合McgsPro脚本代码_54个_v2.0 第六章F节 |
| v2.1 | 2026-08-23 | 整合所有版本，补充注射泵参数组、报警模式、完整脚本库 |
| v2.2 | 2026-09-15 | v2.2 PLC 实施 (S2-S4 重构) 后跟进，**新增 v2.2 时间参数输入框 + 脚本 28 校验段补 v2.2 项（preliminary, 仅文档层）** |
| v2.4 | 2026-08-24 | 参数写入架构变更为"输入框直接绑定+操作确认" |
| v2.5 | 2026-08-24 | 修正v2.4：改回"输入框绑定Param_*缓冲变量+保存按钮汇总写入PLC" |
| v2.6 | 2026-08-24 | 修正v2.5：二次确认改为"页面内隐藏确认面板" |
| v2.7 | 2026-08-25 | 合并远程 v1.2：新增 S4 等待时长显示与超时阈值 |
| v2.8 | 2026-09-16 | 修正 v2.7 地址错位：`VD380/VD382` → `VD444/VD448`（FC15_State_S4_Transfer.stl L53 实际引用） |
| **v2.9** | **2026-09-17** | **脚本重写与 v2.2 时间参数补全：脚本 27/28a/33 改写为读写用户默认镜像 `U1_UD_VDxxx`；脚本 28/29/30 同步删 v2.1 废弃项 + 加 v2.2 三项；脚本 35 改 v2.2 双倒计时器关联校验；§6.1 缓冲变量表 / §8.1 默认值表 / §8.2 范围表 / §8.3 PLC自动计算参数表 / §9 验收清单全部同步** |

**关联文件**:
- `archive/mcgspro/McgsPro画面组态SOP_8画面_v2.0.md` — 原画面布局SOP
- `archive/mcgspro/McgsPro脚本代码_54个_v2.0.md` — 原脚本库
- `archive/mcgspro/MCGS画面组态详细SOP_v1.0.md` — 原详细SOP
- `archive/mcgspro/MCGS组态脚本代码_v1.0.md` — 原脚本代码v1.0
- `archive/mcgspro/MCGS通讯配置SOP_v1.0.md` — 通讯配置
- `docs/HMI-PLC变量地址表_v2.1.md` — v2.1 接口契约