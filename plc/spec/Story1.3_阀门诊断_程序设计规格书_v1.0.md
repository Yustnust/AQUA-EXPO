# PLC程序设计规格书 — Story 1.3 阀门诊断

**配套文档**：《药液配置加注控制系统_PLC设计文档》v9.3（第五/六/八章）、《HMI-PLC变量地址表》v1.0
**Jira Issue**：AQEX-7
**前置依赖**：Story 1.2 状态机骨架（已完成）
**本规格书范围**：阀A/B/C的完整诊断逻辑实现（四态诊断、限位反馈交叉诊断、内漏检测、超时保护）
**不含**：节奏纠偏（Story 1.4）、急停详细（Story 1.5）、报警详细（Story 1.6）

---

## 一、设计决策与待确认项闭环

基于变量地址表v1.0和状态机骨架，对文档"待确认项"做以下决策：

| 待确认项 | 决策 | 依据 |
|---|---|---|
| S_ERROR状态是否存在 | **存在**，VW2=99 | 变量表5.1+骨架FC19已定义 |
| 阀门诊断报警M_Alarm_xxx命名 | **已定义** | 变量表9.1：V301.x阀A、V302.x阀B/C、V303.x其他 |
| 阀A关到位超时延时变量 | 复用 **VD_Delay_ValveA_Verify**(VD66) | 第五章"延时内"即指此变量 |
| 阀B/C关到位超时延时变量 | 复用 **VD_Timeout_ValveB/C**(VD50/54) | 阀B/C无专用延时变量，统一用超时变量 |
| 阀A开启超时变量 | 用 **VD_Timeout_ValveA**(VD48) | 合理推断 |
| 诊断报警分级 | 全部归**一般故障级**（漫溢除外） | 第八章8.1上下文推断 |
| 诊断报警后状态机处理 | 转入 **S_ERROR**(VW2=99) | 故障锁定，安全优先 |

---

## 二、程序架构

### 2.1 新增POU清单

| POU | 类型 | 名称 | 调用方 | 功能 |
|---|---|---|---|---|
| FC30 | 功能块 | ValveA_Diag | FC11(S1) | 阀A诊断：差值法计量+延时验证4项并行 |
| FC31 | 功能块 | ValveB_Diag | FC15(S4) | 阀B诊断：四态诊断+开关到位+超时保护 |
| FC32 | 功能块 | ValveC_Diag | FC17(S6) | 阀C诊断：四态诊断+开关到位+超时保护 |

### 2.2 新增变量分配

| 地址 | 符号 | 类型 | 用途 |
|---|---|---|---|
| VW260 | Diag_State_A | INT | 阀A诊断子状态(0~5) |
| VW262 | Diag_State_B | INT | 阀B诊断子状态(0~5) |
| VW264 | Diag_State_C | INT | 阀C诊断子状态(0~5) |
| VD260 | VD_FlowMeter_CloseSnapshot | DWORD | 阀A关阀瞬间流量计快照(内漏检测基准) |
| VD264 | VD_FlowMeter_CloseDelta | REAL | 阀A关阀后流量计差值(内漏判断) |
| VW266 | Diag_Result_A | INT | 阀A诊断结果(0=进行中,1=正常完成,2=故障) |
| VW268 | Diag_Result_B | INT | 阀B诊断结果 |
| VW270 | Diag_Result_C | INT | 阀C诊断结果 |

### 2.3 计时器分配

| 计时器 | 类型 | 用途 | 时基 |
|---|---|---|---|
| T50 | TON | 阀A开到位超时(对比VD_Timeout_ValveA) | 100ms |
| T51 | TON | 阀A关阀后延时验证(对比VD_Delay_ValveA_Verify) | 100ms |
| T52 | TON | 阀A内漏检测保持计时 | 100ms |
| T53 | TON | 阀B开到位超时(对比VD_Timeout_ValveB) | 100ms |
| T54 | TON | 阀B流量开关超时保护 | 100ms |
| T55 | TON | 阀B关到位超时(对比VD_Timeout_ValveB) | 100ms |
| T56 | TON | 阀C开到位超时(对比VD_Timeout_ValveC) | 100ms |
| T57 | TON | 阀C流量开关超时保护 | 100ms |
| T58 | TON | 阀C关到位超时(对比VD_Timeout_ValveC) | 100ms |

### 2.4 诊断子状态机定义（通用）

| 子状态 | 名称 | 说明 |
|---|---|---|
| 0 | 空闲 | 诊断未启动，等待状态FC触发 |
| 1 | 等待开到位 | 开阀指令已下，T50/53/56计时等开到位反馈 |
| 2 | 开启完成检查 | 开到位已ON，检查流量开关是否ON(无流→报警) |
| 3 | 运行中 | 阀门开启运行中：阀A差值法持续计量/阀B/C四态持续扫描 |
| 4 | 等待关到位 | 关阀指令已下，T55/58计时等关到位反馈 |
| 5 | 关闭后验证 | 仅阀A：T51延时验证，4项并行校验内漏 |

---

## 三、FC30 阀A诊断规格（S1调用）

### 3.1 触发与调用

由FC11(S1上缸进水)在S1状态每周期调用。FC11负责：
- 进入S1时置 Diag_State_A=1（启动开到位诊断）
- 进水量达标时下达关阀指令，置 Diag_State_A=4（启动关到位诊断+内漏验证）

### 3.2 子状态1：等待开到位

**进入条件**：FC11开阀A(Q0.2=1)时置VW260=1

**动作**：
- T50计时（PT=VD_Timeout_ValveA转换值）

**判定**：
| 条件 | 动作 | 子状态转移 |
|---|---|---|
| I1.3(开到位)=ON | 开启完成 | →2 |
| T50超时(未开到位) | 报警M_Alarm_ValveA_OpenTimeout(V301.4)，转S_ERROR | 结果=2故障 |

### 3.3 子状态2：开启完成检查

**进入条件**：I1.3=ON

**动作**：检查流量开关A(I0.0)

**判定**：
| 条件 | 动作 | 子状态转移 |
|---|---|---|
| I0.0(流量开关A)=ON | 正常有流 | →3(运行中) |
| I0.0=OFF(开到位但无流) | 报警M_Alarm_ValveA_OpenNoFlow(V301.5)，转S_ERROR | 结果=2故障 |

**注**：为避免瞬时波动，可加2秒延时确认无流后再报警（T52复用或新增，骨架阶段直接判定）。

### 3.4 子状态3：运行中（差值法持续计量）

**进入条件**：流量开关A=ON

**动作**：
- 持续计算 VD_Current_InletVolume(VD90) = VD86 − VD82
- 持续监测漫溢（I0.5液位计A高位）

**判定**：
| 条件 | 动作 |
|---|---|
| I0.5=ON(漫溢) | 报警M_Alarm_Overflow_AHigh(V300.0)+NC阀Q0.5动作，转S_ERROR |
| VD90 ≥ 目标进水量(VD250) | 下达关阀(Q0.2=0)，快照VD_FlowMeter_CloseSnapshot=VD86，置VW260=5(跳过4，阀A用延时验证替代关到位等待) |

**说明**：阀A关阀后直接进子状态5（延时验证），因为阀A的关到位诊断融入延时验证4项中。

### 3.5 子状态5：关闭后延时验证（4项并行）

**进入条件**：FC11下达关阀指令，VW260=5

**进入动作**：
- 快照 VD_FlowMeter_CloseSnapshot(VD260) = VD86（关阀瞬间累计值）
- T51计时（PT=VD_Delay_ValveA_Verify转换值）

**T51延时到达后，4项并行校验**：

| # | 校验项 | 判定条件 | 报警标志 |
|---|---|---|---|
| 1 | 关后仍有流(流量开关) | I0.0=ON | M_Alarm_ValveA_CloseFlow(V301.0) |
| 2 | 内漏(流量计差值) | VD264=(VD86−VD260) > 阈值(持续增长) | M_Alarm_ValveA_Leak(V301.1) |
| 3 | 关到位反馈超时 | I1.4=OFF | M_Alarm_ValveA_CloseTimeout(V301.2) |
| 4 | 关到位但仍有流(交叉) | I1.4=ON AND I0.0=ON | M_Alarm_ValveA_CloseLeak(V301.3) |

**判定**：
| 条件 | 动作 |
|---|---|
| 4项全部通过(I0.0=OFF AND 差值不增 AND I1.4=ON) | 诊断结果=1(正常完成)，VW260=0，FC11转S2 |
| 任一项报警 | 对应M_Alarm置位，转S_ERROR |

**内漏阈值说明**：VD264>阈值表示关阀后流量计仍增长。阈值暂定0.1L（可调），实际需结合流量计精度现场整定。

### 3.6 漫溢保护（全程，优先级最高）

无论VW260处于何子状态，I0.5=ON立即：
- M_Alarm_Overflow_AHigh(V300.0)=1
- NC电磁阀上缸Q0.5=1
- 转S_ERROR(VW2=99)

---

## 四、FC31 阀B诊断规格（S4调用）

### 4.1 触发与调用

由FC15(S4上→下转移)在S4状态每周期调用。FC15负责：
- 进入S4时置 Diag_State_B=1（启动开到位诊断）

### 4.2 子状态1：等待开到位

**动作**：T53计时（PT=VD_Timeout_ValveB），同时T54流量开关超时保护计时

**判定**：
| 条件 | 动作 |
|---|---|
| I1.5(开到位)=ON | →2 |
| T53超时 | M_Alarm_ValveB_OpenTimeout(V302.1)，转S_ERROR |
| T54超时(流量开关B未ON) | M_Alarm_ValveB_OpenNoFlow(V302.2)或四态诊断异常，转S_ERROR |

**注**：T54为流量开关超时保护，与T53开到位超时是两套独立判据。

### 4.3 子状态2：开启完成检查

**判定**：
| 条件 | 动作 |
|---|---|
| I0.1(流量开关B)=ON | 正常有流 →3 |
| I0.1=OFF(开到位但无流) | M_Alarm_ValveB_OpenNoFlow(V302.2)，转S_ERROR |

### 4.4 子状态3：运行中（四态诊断持续扫描）

**四态诊断逻辑**（持续扫描I0.1+I0.6）：

| 流量开关B(I0.1) | 液位计A低位(I0.6) | 状态 | 处理 |
|---|---|---|---|
| ON | OFF | 1 正常转移中 | 继续 |
| ON | ON | 2 上缸即将排空 | 继续 |
| OFF | ON | 3 上缸已排空 | **关阀触发**：Q0.3=0，置VW262=4(等关到位) |
| OFF | OFF | 4 设备故障 | M_Alarm_ValveB_Diag(V302.0)，转S_ERROR |

**漫溢保护（全程）**：I0.7=ON → M_Alarm_Overflow_BHigh(V300.1)+NC阀Q0.6，转S_ERROR

### 4.5 子状态4：等待关到位

**动作**：T55计时（PT=VD_Timeout_ValveB）

**判定**：
| 条件 | 动作 |
|---|---|
| I1.6(关到位)=ON AND I0.1=OFF | 正常关闭完成，结果=1，VW262=0，FC15转S5 |
| I1.6=ON AND I0.1=ON(关到位但仍有流) | M_Alarm_ValveB_CloseLeak(V302.4)，转S_ERROR |
| T55超时(I1.6未ON) | M_Alarm_ValveB_CloseTimeout(V302.3)，转S_ERROR |

---

## 五、FC32 阀C诊断规格（S6调用）

### 5.1 触发与调用

由FC17(S6下缸排水)在S6状态每周期调用。FC17负责：
- 进入S6时置 Diag_State_C=1

### 5.2 子状态1：等待开到位

**动作**：T56计时（PT=VD_Timeout_ValveC），T57流量开关超时保护

**判定**：
| 条件 | 动作 |
|---|---|
| I1.7(开到位)=ON | →2 |
| T56超时 | M_Alarm_ValveC_OpenTimeout(V302.6)，转S_ERROR |
| T57超时(流量开关C未ON) | 四态诊断异常或M_Alarm_ValveC_OpenNoFlow(V302.7)，转S_ERROR |

### 5.3 子状态2：开启完成检查

**判定**：
| 条件 | 动作 |
|---|---|
| I0.2(流量开关C)=ON | →3 |
| I0.2=OFF | M_Alarm_ValveC_OpenNoFlow(V302.7)，转S_ERROR |

### 5.4 子状态3：运行中（四态诊断持续扫描）

| 流量开关C(I0.2) | 液位计B低位(I1.0) | 状态 | 处理 |
|---|---|---|---|
| ON | OFF | 1 正常排水中 | 继续 |
| ON | ON | 2 下缸即将排空 | 继续 |
| OFF | ON | 3 下缸已排空 | **关阀触发**：Q0.4=0，置VW264=4 |
| OFF | OFF | 4 设备故障 | M_Alarm_ValveC_Diag(V302.5)，转S_ERROR |

**注**：阀C无漫溢保护（下缸排水不会漫溢）。

### 5.5 子状态4：等待关到位

**动作**：T58计时（PT=VD_Timeout_ValveC）

**判定**：
| 条件 | 动作 |
|---|---|
| I2.0(关到位)=ON AND I0.2=OFF | 正常完成，结果=1，VW264=0，FC17转S5/S7 |
| I2.0=ON AND I0.2=ON | M_Alarm_ValveC_CloseLeak(V303.1)，转S_ERROR |
| T58超时 | M_Alarm_ValveC_CloseTimeout(V303.0)，转S_ERROR |

---

## 六、诊断结果与状态机交互

诊断FC通过 Diag_Result_X(VW266/268/270) 向状态FC反馈：

| 结果值 | 含义 | 状态FC处理 |
|---|---|---|
| 0 | 进行中 | 继续当前状态 |
| 1 | 正常完成 | 执行状态转移(S1→S2, S4→S5, S6→S5/S7) |
| 2 | 故障 | 已由诊断FC转S_ERROR，状态FC无需处理 |

状态FC(FC11/FC15/FC17)在调用诊断FC后，检查 Diag_Result：
- =0：继续等待
- =1：执行转移
- =2：已被诊断FC转S_ERROR，本周期结束

---

## 七、VD参数转换说明

诊断FC中T50~T58的PT值为WORD型(100ms时基)，而VD参数为REAL型(秒)。需转换：

```
PT = VD_xxx × 10  (秒→100ms计数值)
```

由于TON的PT为INT型，转换需用乘法指令。若VD_CycleSetpoint等超过3276.7s(PT上限)，需用计数器+定时器组合。骨架阶段假设各超时参数均在3276.7s内，转换值存入VW270~VW280临时区。

实际编码中，REAL×10→ROUND→MOVW到PT。本规格书STL代码中将展示转换逻辑。

---

## 八、报警汇总

| 报警标志 | 阀门 | 诊断项 | 分级 |
|---|---|---|---|
| V300.0 M_Alarm_Overflow_AHigh | A | 漫溢(液位计A高位) | 漫溢级 |
| V301.0 M_Alarm_ValveA_CloseFlow | A | 关后仍有流(流量开关) | 一般级 |
| V301.1 M_Alarm_ValveA_Leak | A | 内漏(流量计差值) | 一般级 |
| V301.2 M_Alarm_ValveA_CloseTimeout | A | 关到位超时 | 一般级 |
| V301.3 M_Alarm_ValveA_CloseLeak | A | 关到位但仍有流 | 一般级 |
| V301.4 M_Alarm_ValveA_OpenTimeout | A | 开到位超时 | 一般级 |
| V301.5 M_Alarm_ValveA_OpenNoFlow | A | 开到位但无流 | 一般级 |
| V300.1 M_Alarm_Overflow_BHigh | B | 漫溢(液位计B高位) | 漫溢级 |
| V302.0 M_Alarm_ValveB_Diag | B | 四态诊断异常(状态4) | 一般级 |
| V302.1 M_Alarm_ValveB_OpenTimeout | B | 开到位超时 | 一般级 |
| V302.2 M_Alarm_ValveB_OpenNoFlow | B | 开到位但无流 | 一般级 |
| V302.3 M_Alarm_ValveB_CloseTimeout | B | 关到位超时 | 一般级 |
| V302.4 M_Alarm_ValveB_CloseLeak | B | 关到位但仍有流 | 一般级 |
| V302.5 M_Alarm_ValveC_Diag | C | 四态诊断异常(状态4) | 一般级 |
| V302.6 M_Alarm_ValveC_OpenTimeout | C | 开到位超时 | 一般级 |
| V302.7 M_Alarm_ValveC_OpenNoFlow | C | 开到位但无流 | 一般级 |
| V303.0 M_Alarm_ValveC_CloseTimeout | C | 关到位超时 | 一般级 |
| V303.1 M_Alarm_ValveC_CloseLeak | C | 关到位但仍有流 | 一般级 |

所有一般级报警触发后转S_ERROR(VW2=99)，漫溢级报警同样转S_ERROR并动作NC电磁阀。

---

**规格书版本**：v1.0
**编制日期**：2026-07-15
