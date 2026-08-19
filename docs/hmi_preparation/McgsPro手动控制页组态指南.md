# 昆仑通态 McgsPro 手动控制页组态指南

**JIRA Story**: AQEX-12（手动控制命令位响应）/ 关联 AQEX-60（HMI 变量同步）  
**适用范围**: 药液配置与加注控制系统 — 8 套缸单元集中 HMI，画面 3「手动控制」  
**组态软件**: 昆仑通态 McgsPro 3.3+，西门子 S7-200 SMART 以太网驱动  
**配套文档**: [HMI画面布局线框图_v1.0.md](file:///d:/work/CTI/docs/hmi_preparation/HMI画面布局线框图_v1.0.md)、[画面变量绑定清单.md](file:///d:/work/CTI/docs/hmi_preparation/画面变量绑定清单.md)、[HMI-PLC变量地址表_v1.0.md](file:///d:/work/CTI/docs/HMI-PLC变量地址表_v1.0.md)  
**配套脚本/数据**: [gen_mcgs_csv.py](file:///d:/work/CTI/archive/mcgspro/gen_mcgs_csv.py)、`archive/mcgspro/csv_output/McgsPro变量导入_单元{1~8}.csv`

---

## 1. 变量准备

手动控制页需要两类 PLC 变量：**HMI→PLC 手动命令位**和 **PLC→HMI 状态反馈位**。  
所有变量已在 [gen_mcgs_csv.py](file:///d:/work/CTI/archive/mcgspro/gen_mcgs_csv.py) 中导出，8 单元 CSV 文件见 `archive/mcgspro/csv_output/`。

### 1.1 手动命令位（V2.4 ~ V3.5，HMI 写，PLC 上升沿触发 + 清零握手）

| 变量名（1 号单元示例） | PLC 地址 | 说明 |
|---|---|---|
| U1_CMD_Manual_ValveA_Open | V2.4 | 手动开阀 A |
| U1_CMD_Manual_ValveA_Close | V2.5 | 手动关阀 A |
| U1_CMD_Manual_ValveB_Open | V2.6 | 手动开阀 B |
| U1_CMD_Manual_ValveB_Close | V2.7 | 手动关阀 B |
| U1_CMD_Manual_ValveC_Open | V3.0 | 手动开阀 C |
| U1_CMD_Manual_ValveC_Close | V3.1 | 手动关阀 C |
| U1_CMD_Manual_Pump1_On | V3.2 | 手动启动潜水泵 1 |
| U1_CMD_Manual_Pump1_Off | V3.3 | 手动停止潜水泵 1 |
| U1_CMD_Manual_Pump2_On | V3.4 | 手动启动潜水泵 2（预留） |
| U1_CMD_Manual_Pump2_Off | V3.5 | 手动停止潜水泵 2（预留） |

### 1.2 状态反馈位（HMI 只读）

| 变量名（1 号单元示例） | PLC 地址 | 说明 |
|---|---|---|
| U1_VW2_StateMachine | VW2 | 状态机，仅 0（S0）允许手动 |
| U1_STA_TankA_State | V1.6 | 上缸状态：0=空，1=满 |
| U1_STA_TankB_State | V1.7 | 下缸状态：0=空，1=满 |
| U1_VW6_AlarmCode | VW6 | 当前最高优先级报警码，≠0 时建议禁用手动 |
| U1_DI_EStop | I1.1 | 急停反馈：1=正常，0=急停触发 |
| U1_DI_SafetyRelay_FB | I1.2 | 安全继电器反馈：1=正常 |
| U1_DI_ValveA_Open ~ U1_DI_ValveC_Close | I1.3 ~ I2.0 | 阀门开/关到位反馈 |
| U1_DI_FlowSwitch_A/B/C | I0.0 ~ I0.2 | 阀 A/B/C 流量开关状态 |

> **导入提示**：原 `archive/mcgspro/McgsPro变量导入_单元*.csv` 当前被 MCGS 占用，本次更新生成到 `csv_output/` 目录。如果你是从 MCGS 导出的单设备表，可直接使用合并后的 `csv_output/西门子_S7_Smart200_以太网_合并导入_最新.csv` 做覆盖导入，原有变量名和通道都会保留。

---

## 2. 画面布局

参考 [HMI画面布局线框图_v1.0.md — 画面3](file:///d:/work/CTI/docs/hmi_preparation/HMI画面布局线框图_v1.0.md#画面3手动控制页)。  
分辨率 1280×800，主内容区 620px 高，左右分栏：

```
┌────────────────────────────────────────────────────────────┐
│ 单元:[1][2][3][4][5][6][7][8]  当前手动操作:1号单元          │
├────────────────────────────────────────────────────────────┤
│  ┌────────── 阀门控制 ──────────┐ ┌────────── 泵控制 ──────┐│
│  │ 阀A(上缸进水)                  │ │ 潜水泵1(上缸搅拌)       ││
│  │ 状态: ●关  反馈:关到位         │ │ 状态: ●停              ││
│  │ [手动开阀A]  [手动关阀A]       │ │ [手动启动] [手动停止]   ││
│  │                                │ │                        ││
│  │ 阀B(上→下转移)                │ │ 潜水泵2                 ││
│  │ 状态: ●关  反馈:关到位         │ │ 状态: ●停              ││
│  │ [手动开阀B]  [手动关阀B]       │ │ [手动启动] [手动停止]   ││
│  │                                │ │                        ││
│  │ 阀C(下缸排水)                  │ │                        ││
│  │ 状态: ●关  反馈:关到位         │ │                        ││
│  │ [手动开阀C]  [手动关阀C]       │ │                        ││
│  └───────────────────────────────┘ └────────────────────────┘│
│  ⚠ 手动操作仅 S0 态可用；阀B需上缸满+下缸空；阀C需下缸满 │
└────────────────────────────────────────────────────────────┘
```

---

## 3. 控件与变量绑定

| 画面元素 | MCGS 控件建议 | 绑定变量（1 号单元示例） | 读写 | 备注 |
|---|---|---|---|---|
| 当前单元号 | 标签 | HMI 内部 `SelectedUnit` | — | 1~8 |
| 上缸状态 | 指示灯 | U1_STA_TankA_State | R | 0=灰/空，1=蓝/满 |
| 下缸状态 | 指示灯 | U1_STA_TankB_State | R | 同上 |
| 急停状态 | 指示灯 | U1_DI_EStop | R | OFF 时红色闪烁 |
| 报警状态 | 标签/指示灯 | U1_VW6_AlarmCode | R | ≠0 时按级别着色 |
| 阀A 开到位 | 指示灯 | U1_DI_ValveA_Open | R | — |
| 阀A 关到位 | 指示灯 | U1_DI_ValveA_Close | R | — |
| 手动开阀A | 标准按钮/位按钮 | U1_CMD_Manual_ValveA_Open | W | 二次确认 + 脉冲 |
| 手动关阀A | 标准按钮/位按钮 | U1_CMD_Manual_ValveA_Close | W | 二次确认 + 脉冲 |
| 阀B 开/关到位 | 指示灯 | U1_DI_ValveB_Open/Close | R | — |
| 手动开/关阀B | 标准按钮/位按钮 | U1_CMD_Manual_ValveB_Open/Close | W | 开阀B 需联锁 |
| 阀C 开/关到位 | 指示灯 | U1_DI_ValveC_Open/Close | R | — |
| 手动开/关阀C | 标准按钮/位按钮 | U1_CMD_Manual_ValveC_Open/Close | W | 开阀C 需联锁 |
| 流量开关 A/B/C | 指示灯 | U1_DI_FlowSwitch_A/B/C | R | 调试观察 |
| 手动启/停泵1 | 标准按钮/位按钮 | U1_CMD_Manual_Pump1_On/Off | W | 二次确认 + 脉冲 |
| 手动启/停泵2 | 标准按钮/位按钮 | U1_CMD_Manual_Pump2_On/Off | W | 二次确认 + 脉冲 |
| 联锁提示文本 | 标签 | HMI 内部 `Manual_InterlockMsg` | — | 动态显示 |

---

## 4. 手动按钮/开关配置要点

### 4.1 控件选择

- **推荐**：使用 MCGS **标准按钮** 或 **位操作按钮**。
- **不推荐**：使用保持型开关（Toggle Switch），因为 PLC 在扫描周期内会清零命令位，保持型开关会导致 HMI 与 PLC 状态不一致。

### 4.2 按钮操作模式

配置为 **「按下时置 1，松开时置 0」**（脉冲模式）：

1. 双击按钮 → 操作属性 → 数据对象值操作。
2. 选择关联变量（如 `U1_CMD_Manual_ValveA_Open`）。
3. 操作方式选择 **「按 1 松 0」**（或「置 1」后由 PLC 清零，若 MCGS 无脉冲模式，则用脚本实现）。

### 4.3 为什么不能用长置 1

PLC 程序 [FC20_ManualControl.stl](file:///d:/work/CTI/plc/stl/FC20_ManualControl.stl) 采用 **上升沿触发 + M 位锁存 + PLC 清零握手**：

```python
LD     L60.1
A      V2.4           // 开阀A命令
EU                    // 上升沿触发
S      M12.0, 1       // 锁存阀A开状态
R      V2.4, 1        // PLC 立即清零

LD     M12.0
=      Q0.2           // 每个扫描周期刷新输出
```

- 一个脉冲把阀打开后，**M 位会保持**，Q 输出每个周期都被刷新，阀门保持打开。
- 若 HMI 长时间置 1，PLC 每个扫描周期都会检测到上升沿，导致锁存位反复置位，但因为是同一个位，不会反复开关。

---

## 5. 二次确认弹窗组态

### 5.1 创建确认窗口

新建用户窗口：`手动二次确认`（尺寸建议 400×200）。

窗口内元素：

| 元素 | 类型 | 绑定变量 | 说明 |
|---|---|---|---|
| 提示文本 | 标签 | HMI 内部 `Manual_Confirm_Text` | 例如「确认对 1 号单元执行手动开阀A？」 |
| 确认按钮 | 标准按钮 | — | 点击后执行命令 |
| 取消按钮 | 标准按钮 | — | 点击后关闭窗口 |

### 5.2 HMI 内部变量

| 变量名 | 类型 | 用途 |
|---|---|---|
| `SelectedUnit` | 数值型/整数 | 当前选中单元 1~8 |
| `Manual_Pending_Cmd` | 字符型 | 待执行的命令标识，如 `ValveA_Open` |
| `Manual_Confirm_Text` | 字符型 | 确认窗口显示文本 |

### 5.3 手动按钮点击脚本（示例）

以「手动开阀A」按钮为例，在其 **按下时** 执行：

```vb
Manual_Pending_Cmd = "ValveA_Open"
Manual_Confirm_Text = "确认对 " + !str(SelectedUnit) + " 号单元执行【手动开阀A】？"
!OpenWindow("手动二次确认")
```

> 注：`!OpenWindow`、`!str` 等函数请按实际 McgsPro 版本调整。若版本不支持字符变量拼接，可预置多行静态文本 + 可见性切换。

### 5.4 确认窗口「确认」按钮脚本

```vb
SELECT CASE Manual_Pending_Cmd
    CASE "ValveA_Open"
        U1_CMD_Manual_ValveA_Open = 1
    CASE "ValveA_Close"
        U1_CMD_Manual_ValveA_Close = 1
    CASE "ValveB_Open"
        U1_CMD_Manual_ValveB_Open = 1
    CASE "ValveB_Close"
        U1_CMD_Manual_ValveB_Close = 1
    CASE "ValveC_Open"
        U1_CMD_Manual_ValveC_Open = 1
    CASE "ValveC_Close"
        U1_CMD_Manual_ValveC_Close = 1
    CASE "Pump1_On"
        U1_CMD_Manual_Pump1_On = 1
    CASE "Pump1_Off"
        U1_CMD_Manual_Pump1_Off = 1
END SELECT

!CloseWindow("手动二次确认")
```

> 实际 8 单元工程中，需根据 `SelectedUnit` 切换写入目标变量（如 U2_CMD_Manual_ValveA_Open）。可使用脚本条件分支或 MCGS 画面窗口模板按单元实例化。

---

## 6. 使能与联锁

### 6.1 全局使能条件（所有手动按钮）

在按钮的 **可见性/可用性** 表达式中设置：

```
U1_VW2_StateMachine == 0
&& U1_DI_EStop == 1
&& U1_DI_SafetyRelay_FB == 1
&& U1_VW6_AlarmCode == 0
```

含义：

- 仅 S0（初始化）状态允许手动；
- 急停未触发；
- 安全继电器反馈正常；
- 当前无报警。

### 6.2 阀B 开按钮额外联锁

```
...（全局条件）
&& U1_STA_TankA_State == 1   // 上缸满
&& U1_STA_TankB_State == 0   // 下缸空
```

### 6.3 阀C 开按钮额外联锁

```
...（全局条件）
&& U1_STA_TankB_State == 1   // 下缸满
```

### 6.4 联锁提示文本

在画面底部放置一个标签，按以下表达式显示提示：

```
IF U1_VW2_StateMachine != 0 THEN
    "当前状态不允许手动操作"
ELSEIF U1_DI_EStop == 0 THEN
    "急停触发，禁止手动"
ELSEIF U1_VW6_AlarmCode != 0 THEN
    "存在报警，请先确认/消音"
ELSEIF 开阀B按钮被按下且 (U1_STA_TankA_State == 0 || U1_STA_TankB_State == 1) THEN
    "阀B开启需满足：上缸满、下缸空"
ELSEIF 开阀C按钮被按下且 U1_STA_TankB_State == 0 THEN
    "阀C开启需满足：下缸满"
ELSE
    ""
ENDIF
```

> 注：最终表达式需按 MCGS 脚本语法改写；若标签不支持复杂表达式，可在循环策略中计算并写入 `Manual_InterlockMsg`。

---

## 7. 权限控制

- 进入「手动控制」画面需 **维护级及以上权限**。
- 所有手动按钮必须配置二次确认弹窗。
- 操作员权限（无维护权限）进入画面时，所有手动按钮置为 **不可用/隐藏**。

---

## 8. 组态验证清单

| 序号 | 验证项 | 期望结果 |
|---|---|---|
| 1 | 导入 CSV 后，手动命令位变量类型为 INTEGER，通道地址正确 | 无导入错误 |
| 2 | 状态机 VW2 = 0 时，手动按钮可用 | 按钮为彩色可点击 |
| 3 | 状态机 VW2 = 1~8 或 99 时，手动按钮禁用 | 按钮为灰色 |
| 4 | 急停 I1.1 = 0 时，手动按钮禁用 | 按钮为灰色 |
| 5 | 报警 VW6 ≠ 0 时，手动按钮禁用 | 按钮为灰色 |
| 6 | 阀B 开按钮：上缸空或下缸满时禁用 | 按钮为灰色 |
| 7 | 阀C 开按钮：下缸空时禁用 | 按钮为灰色 |
| 8 | 点击手动开阀A，弹出二次确认窗口 | 弹窗显示正确命令文本 |
| 9 | 确认后，V2.4 被置 1，PLC 立即清零，阀A 实际打开 | 阀A 开到位反馈变 ON |
| 10 | 点击手动关阀A，V2.5被置 1，阀A 关闭 | 阀A 关到位反馈变 ON |
| 11 | 8 个单元切换时，变量绑定随 `SelectedUnit` 切换 | 每个单元独立操作 |

---

## 9. 已知限制与后续

- **NC 球阀串联主路**：手动开阀 A 时 PLC 自动打开上缸 NC 阀（Q0.5），开阀 B/C 时自动打开下缸 NC 阀（Q0.6），关阀后自动关闭。HMI 无需单独控制 NC 阀，但可添加状态指示灯观察 Q0.5/Q0.6。
- **注射泵手动抽/排液**：当前仅通过 [画面变量绑定清单.md](file:///d:/work/CTI/docs/hmi_preparation/画面变量绑定清单.md) 预留 VW204/VW206，PLC 侧手动逻辑待补充，不建议在手动控制页直接开放。
- **声音/灯光测试按钮**：PLC 侧无专用测试位，本期不建议添加。

---

**文档版本**: v1.0  
**创建日期**: 2026-08-17  
**下次更新触发**: MCGS 选型确认、PLC 手动命令扩展、I/Q CSV 导入验证结果反馈
