# 跨FC变量访问数据流分析报告

| 项目 | 内容 |
|---|---|
| 分析对象 | S7-200 SMART STL代码(20个FC) |
| 分析工具 | cross_fc_dataflow_analyzer.py v1.0 |
| 分析日期 | 2026-07-18 |

## 一、分析概览

- **变量总数**(V区): 154 个
- **跨FC共享变量**(被≥2个FC访问): 78 个
- **写入-读取链变量**(被某FC写且被另一FC读): 83 个

## 二、FC清单与访问统计

| FC名称 | 引用变量数 | 写入变量数 | 读取变量数 |
|---|---|---|---|
| FC0_SysInit | 30 | 17 | 16 |
| FC10_State_S0_Init | 5 | 4 | 2 |
| FC11_State_S1_Inlet | 30 | 23 | 10 |
| FC12_State_S2_PreMix | 13 | 10 | 8 |
| FC13_State_S3_Dosing | 12 | 11 | 2 |
| FC14_State_S35_Rest | 5 | 4 | 3 |
| FC15_State_S4_Transfer | 30 | 20 | 11 |
| FC16_State_S5_Run | 17 | 11 | 10 |
| FC17_State_S6_Drain | 11 | 10 | 4 |
| FC18_State_S7_End | 4 | 3 | 1 |
| FC19_State_Error | 9 | 9 | 2 |
| FC1_StateDispatcher | 3 | 2 | 1 |
| FC2_EStopHandling | 6 | 6 | 2 |
| FC30_ValveA_Diag | 21 | 15 | 13 |
| FC31_ValveB_Diag | 13 | 11 | 2 |
| FC32_ValveC_Diag | 12 | 10 | 2 |
| FC3_AlarmHandling | 42 | 32 | 37 |
| FC40_RhythmCorrection | 19 | 15 | 12 |
| FC4_ModbusPolling | 1 | 0 | 1 |
| OB1_MAIN | 0 | 0 | 0 |

## 三、高耦合变量Top20(被最多FC访问)

这些变量被多个FC读写,是系统核心数据流节点,变更时影响范围大。

| 排名 | 变量 | 符号 | 类型 | 读取FC数 | 写入FC数 | 总FC数 | FC列表 |
|---|---|---|---|---|---|---|---|
| 1 | VB2 | — | VB | 0 | 17 | 17 | FC0_SysInit, FC10_State_S0_Init, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC13_State_S3_Dosing... (+12) |
| 2 | VB3 | — | VB | 0 | 16 | 16 | FC0_SysInit, FC10_State_S0_Init, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC13_State_S3_Dosing... (+11) |
| 3 | V1.6 | M_TankA_State | Vbit | 2 | 5 | 7 | FC0_SysInit, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC15_State_S4_Transfer, FC16_State_S5_Run... (+2) |
| 4 | V1.7 | M_TankB_State | Vbit | 2 | 4 | 5 | FC0_SysInit, FC15_State_S4_Transfer, FC16_State_S5_Run, FC17_State_S6_Drain, FC19_State_Error |
| 5 | V300.4 | M_EStop_Latch | Vbit | 2 | 3 | 4 | FC0_SysInit, FC19_State_Error, FC2_EStopHandling, FC3_AlarmHandling |
| 6 | VD178 | VD_S5_Elapsed | VD | 1 | 4 | 4 | FC0_SysInit, FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC16_State_S5_Run |
| 7 | VD150 | VD_Available | VD | 2 | 3 | 3 | FC11_State_S1_Inlet, FC16_State_S5_Run, FC40_RhythmCorrection |
| 8 | V300.5 | M_Alarm_SafetyRelay | Vbit | 3 | 2 | 3 | FC19_State_Error, FC2_EStopHandling, FC3_AlarmHandling |
| 9 | V301.0 | — | Vbit | 2 | 2 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| 10 | V301.1 | — | Vbit | 2 | 2 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| 11 | V301.2 | — | Vbit | 2 | 2 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| 12 | V301.3 | — | Vbit | 2 | 2 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| 13 | VB6 | — | VB | 0 | 3 | 3 | FC0_SysInit, FC19_State_Error, FC2_EStopHandling |
| 14 | VB7 | — | VB | 0 | 3 | 3 | FC0_SysInit, FC19_State_Error, FC2_EStopHandling |
| 15 | V1.0 | STA_StartAck | Vbit | 0 | 3 | 3 | FC0_SysInit, FC10_State_S0_Init, FC18_State_S7_End |
| 16 | V303.5 | M_Alarm_RTC_Lost | Vbit | 1 | 2 | 2 | FC0_SysInit, FC3_AlarmHandling |
| 17 | V0.0 | CMD_Start | Vbit | 2 | 1 | 2 | FC10_State_S0_Init, FC18_State_S7_End |
| 18 | VW6 | 报警码 | VW | 2 | 1 | 2 | FC10_State_S0_Init, FC3_AlarmHandling |
| 19 | VD116 | — | VD | 0 | 3 | 3 | FC11_State_S1_Inlet, FC16_State_S5_Run, FC17_State_S6_Drain |
| 20 | VD120 | VD_S2_Target | VD | 2 | 1 | 3 | FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC40_RhythmCorrection |

## 四、跨FC写入-读取链(数据流核心路径)

以下变量被FC A写入,被FC B读取,构成FC间数据流。
这是理解系统数据流的关键。

| 变量 | 符号 | 写入FC | 读取FC | 数据流方向 |
|---|---|---|---|---|
| V1.6 | M_TankA_State | FC0_SysInit, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC15_State_S4_Transfer, FC19_State_Error | FC16_State_S5_Run, FC3_AlarmHandling | FC0_SysInit, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC15_State_S4_Transfer, FC19_State_Error → [V1.6] → FC16_State_S5_Run, FC3_AlarmHandling |
| V1.7 | M_TankB_State | FC0_SysInit, FC15_State_S4_Transfer, FC17_State_S6_Drain, FC19_State_Error | FC0_SysInit, FC16_State_S5_Run | FC0_SysInit, FC15_State_S4_Transfer, FC17_State_S6_Drain, FC19_State_Error → [V1.7] → FC0_SysInit, FC16_State_S5_Run |
| V300.4 | M_EStop_Latch | FC0_SysInit, FC19_State_Error, FC2_EStopHandling | FC2_EStopHandling, FC3_AlarmHandling | FC0_SysInit, FC19_State_Error, FC2_EStopHandling → [V300.4] → FC2_EStopHandling, FC3_AlarmHandling |
| VD178 | VD_S5_Elapsed | FC0_SysInit, FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC16_State_S5_Run | FC16_State_S5_Run | FC0_SysInit, FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC16_State_S5_Run → [VD178] → FC16_State_S5_Run |
| VD150 | VD_Available | FC11_State_S1_Inlet, FC16_State_S5_Run, FC40_RhythmCorrection | FC16_State_S5_Run, FC40_RhythmCorrection | FC11_State_S1_Inlet, FC16_State_S5_Run, FC40_RhythmCorrection → [VD150] → FC16_State_S5_Run, FC40_RhythmCorrection |
| V300.5 | M_Alarm_SafetyRelay | FC19_State_Error, FC2_EStopHandling | FC19_State_Error, FC2_EStopHandling, FC3_AlarmHandling | FC19_State_Error, FC2_EStopHandling → [V300.5] → FC19_State_Error, FC2_EStopHandling, FC3_AlarmHandling |
| V301.0 | — | FC30_ValveA_Diag, FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling → [V301.0] → FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.1 | — | FC30_ValveA_Diag, FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling → [V301.1] → FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.2 | — | FC30_ValveA_Diag, FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling → [V301.2] → FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.3 | — | FC30_ValveA_Diag, FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling → [V301.3] → FC30_ValveA_Diag, FC3_AlarmHandling |
| V303.5 | M_Alarm_RTC_Lost | FC0_SysInit, FC3_AlarmHandling | FC3_AlarmHandling | FC0_SysInit, FC3_AlarmHandling → [V303.5] → FC3_AlarmHandling |
| V0.0 | CMD_Start | FC10_State_S0_Init | FC10_State_S0_Init, FC18_State_S7_End | FC10_State_S0_Init → [V0.0] → FC10_State_S0_Init, FC18_State_S7_End |
| VW6 | 报警码 | FC3_AlarmHandling | FC10_State_S0_Init, FC3_AlarmHandling | FC3_AlarmHandling → [VW6] → FC10_State_S0_Init, FC3_AlarmHandling |
| VD120 | VD_S2_Target | FC40_RhythmCorrection | FC11_State_S1_Inlet, FC12_State_S2_PreMix | FC40_RhythmCorrection → [VD120] → FC11_State_S1_Inlet, FC12_State_S2_PreMix |
| VD154 | VD_Needed | FC11_State_S1_Inlet, FC16_State_S5_Run | FC40_RhythmCorrection | FC11_State_S1_Inlet, FC16_State_S5_Run → [VD154] → FC40_RhythmCorrection |
| VD124 | VD_RestTime_Target | FC11_State_S1_Inlet, FC40_RhythmCorrection | FC14_State_S35_Rest | FC11_State_S1_Inlet, FC40_RhythmCorrection → [VD124] → FC14_State_S35_Rest |
| VW184 | VW_Corr_Result | FC40_RhythmCorrection | FC11_State_S1_Inlet, FC16_State_S5_Run | FC40_RhythmCorrection → [VW184] → FC11_State_S1_Inlet, FC16_State_S5_Run |
| V303.2 | — | FC12_State_S2_PreMix, FC3_AlarmHandling | FC3_AlarmHandling | FC12_State_S2_PreMix, FC3_AlarmHandling → [V303.2] → FC3_AlarmHandling |
| V303.3 | — | FC12_State_S2_PreMix, FC3_AlarmHandling | FC3_AlarmHandling | FC12_State_S2_PreMix, FC3_AlarmHandling → [V303.3] → FC3_AlarmHandling |
| VD90 | — | FC13_State_S3_Dosing, FC30_ValveA_Diag | FC30_ValveA_Diag | FC13_State_S3_Dosing, FC30_ValveA_Diag → [VD90] → FC30_ValveA_Diag |
| V303.4 | — | FC13_State_S3_Dosing, FC3_AlarmHandling | FC3_AlarmHandling | FC13_State_S3_Dosing, FC3_AlarmHandling → [V303.4] → FC3_AlarmHandling |
| V301.6 | — | FC16_State_S5_Run, FC3_AlarmHandling | FC3_AlarmHandling | FC16_State_S5_Run, FC3_AlarmHandling → [V301.6] → FC3_AlarmHandling |
| VW270 | 0进行中/1正常完成/2故障 | FC17_State_S6_Drain, FC32_ValveC_Diag | FC17_State_S6_Drain | FC17_State_S6_Drain, FC32_ValveC_Diag → [VW270] → FC17_State_S6_Drain |
| V300.0 | — | FC30_ValveA_Diag, FC3_AlarmHandling | FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling → [V300.0] → FC3_AlarmHandling |
| V301.4 | — | FC30_ValveA_Diag, FC3_AlarmHandling | FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling → [V301.4] → FC3_AlarmHandling |
| V301.5 | — | FC30_ValveA_Diag, FC3_AlarmHandling | FC3_AlarmHandling | FC30_ValveA_Diag, FC3_AlarmHandling → [V301.5] → FC3_AlarmHandling |
| V300.1 | — | FC31_ValveB_Diag, FC3_AlarmHandling | FC3_AlarmHandling | FC31_ValveB_Diag, FC3_AlarmHandling → [V300.1] → FC3_AlarmHandling |
| V302.1 | — | FC31_ValveB_Diag, FC3_AlarmHandling | FC3_AlarmHandling | FC31_ValveB_Diag, FC3_AlarmHandling → [V302.1] → FC3_AlarmHandling |
| V302.2 | — | FC31_ValveB_Diag, FC3_AlarmHandling | FC3_AlarmHandling | FC31_ValveB_Diag, FC3_AlarmHandling → [V302.2] → FC3_AlarmHandling |
| V302.0 | — | FC31_ValveB_Diag, FC3_AlarmHandling | FC3_AlarmHandling | FC31_ValveB_Diag, FC3_AlarmHandling → [V302.0] → FC3_AlarmHandling |

## 五、变量-FC访问矩阵(跨FC共享变量)

**矩阵说明**: R=读取, W=写入, RW=读写, 空=未访问
**变量数**: 78个跨FC变量 | **FC数**: 18个

### 5.1 状态机与核心变量

| 变量 | 符号 |
|---|---|
| VD112 | VD_T_Rolling (读:1FC 写:1FC) |
| VD116 | — (读:0FC 写:3FC) |
| VD178 | VD_S5_Elapsed (读:1FC 写:4FC) |
| VW2 | 状态机状态(FC19写0回S0) (读:2FC 写:0FC) |
| VW4 | 注射泵状态码 (读:2FC 写:0FC) |
| VW6 | 报警码 (读:2FC 写:1FC) |
| V0.0 | CMD_Start (读:2FC 写:1FC) |
| V1.6 | M_TankA_State (读:2FC 写:5FC) |
| V1.7 | M_TankB_State (读:2FC 写:4FC) |
| V300.4 | M_EStop_Latch (读:2FC 写:3FC) |
| V300.5 | M_Alarm_SafetyRelay (读:3FC 写:2FC) |

## 六、FC间耦合分析(共享变量数)

两个FC共享的变量越多,耦合度越高。

### 6.1 高耦合FC对Top20

| FC A | FC B | 共享变量数 |
|---|---|---|
| FC0_SysInit | FC15_State_S4_Transfer | 17 |
| FC11_State_S1_Inlet | FC16_State_S5_Run | 11 |
| FC11_State_S1_Inlet | FC30_ValveA_Diag | 9 |
| FC11_State_S1_Inlet | FC40_RhythmCorrection | 8 |
| FC0_SysInit | FC19_State_Error | 7 |
| FC30_ValveA_Diag | FC3_AlarmHandling | 7 |
| FC15_State_S4_Transfer | FC31_ValveB_Diag | 6 |
| FC17_State_S6_Drain | FC32_ValveC_Diag | 6 |
| FC19_State_Error | FC2_EStopHandling | 6 |
| FC31_ValveB_Diag | FC3_AlarmHandling | 6 |
| FC0_SysInit | FC16_State_S5_Run | 5 |
| FC0_SysInit | FC2_EStopHandling | 5 |
| FC15_State_S4_Transfer | FC16_State_S5_Run | 5 |
| FC32_ValveC_Diag | FC3_AlarmHandling | 5 |
| FC0_SysInit | FC11_State_S1_Inlet | 4 |
| FC10_State_S0_Init | FC18_State_S7_End | 4 |
| FC11_State_S1_Inlet | FC12_State_S2_PreMix | 4 |
| FC11_State_S1_Inlet | FC15_State_S4_Transfer | 4 |
| FC15_State_S4_Transfer | FC19_State_Error | 4 |
| FC16_State_S5_Run | FC17_State_S6_Drain | 4 |

## 七、关键数据流路径

### 7.1 状态机调度流(FC1→各状态FC)

```
FC1_StateDispatcher (读写VW2)
  ├─ VW2=0 → FC10_State_S0_Init
  ├─ VW2=1 → FC11_State_S1_Inlet (调用FC30阀A诊断)
  ├─ VW2=2 → FC12_State_S2_PreMix
  ├─ VW2=3 → FC13_State_S3_Dosing (调用FC4 Modbus轮询)
  ├─ VW2=4 → FC14_State_S35_Rest
  ├─ VW2=5 → FC15_State_S4_Transfer (调用FC31阀B诊断)
  ├─ VW2=6 → FC16_State_S5_Run (调用FC40节奏纠偏)
  ├─ VW2=7 → FC17_State_S6_Drain (调用FC32阀C诊断)
  ├─ VW2=8 → FC18_State_S7_End
  └─ VW2=99 → FC19_State_Error
```

### 7.2 急停与报警流(FC2/FC3→各FC)

```
FC2_EStopHandling
  ├─ I1.1下降沿 → V300.4锁存 → VW2=99(S_ERROR)
  ├─ I1.2反馈缺失 → V300.5继电器故障
  └─ QB0=0(输出安全) → Q0.7=1(声音)

FC3_AlarmHandling
  ├─ 读V300~V303(32位报警字)
  ├─ 优先级链计算 → VW6(最高级报警码)
  └─ VW6≠0 → Q8.0灯光常亮
```

### 7.3 节奏纠偏流(FC40←FC16/FC11)

```
FC16_State_S5_Run
  ├─ VD178(S5_Elapsed)累加 → 触发FC40预规划
  └─ FC40_RhythmCorrection
      ├─ 读VD20(周期)/VD28(S2标称)/VD36(S3.5标称)
      ├─ 计算VD120(S2_Target)/VD124(S3.5_Target)/VD128(CycleExtend)
      └─ VW184(纠偏结果): 1正常/2纠偏/3顺延/4人工介入

FC11_State_S1_Inlet (S1完成后)
  └─ 调用FC40(模式1二次校正) → 更新VD112(T_Rolling)
```

### 7.4 阀门诊断流(FC30/31/32←FC11/15/17)

```
FC11(S1) → FC30(阀A诊断)
  ├─ FC11写VW260=1启动 → FC30读VW260调度
  ├─ FC30写VW266(结果) → FC11读VW266判断
  └─ FC30用VD308(快照)/VD312(差值)/VD316(目标进水量)

FC15(S4) → FC31(阀B诊断)
  ├─ FC15写VW262=1启动 → FC31读VW262调度
  ├─ FC31写VW268(结果) → FC15读VW268判断
  └─ FC31用VW274(超时PT)

FC17(S6) → FC32(阀C诊断)
  ├─ FC17写VW264=1启动 → FC32读VW264调度
  ├─ FC32写VW270(结果) → FC17读VW270判断
  └─ FC32用VW276(超时PT)
```

### 7.5 Modbus通讯流(FC4↔注射泵/流量计)

```
FC4_ModbusPolling
  ├─ VW250(轮询计数器): 0=注射泵, 1=流量计
  ├─ 注射泵: VW200~VW228 ↔ Modbus 40002~40018
  │   ├─ VW204(抽液步数)→40006
  │   ├─ VW206(排液步数)→40007
  │   └─ VW4(状态码)←41001
  └─ 流量计: VD86(累计)←0x0009, VD94(瞬时)←0x0017
```

## 八、架构观察与改进建议

### 8.1 高写入冲突风险变量(被>3个FC写入)

这些变量被多个FC写入,需确认调用顺序与互斥性,否则可能产生时序冲突。

| 变量 | 符号 | 写入FC数 | 写入FC列表 |
|---|---|---|---|
| VB2 | — | 17 | FC0_SysInit, FC10_State_S0_Init, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC13_State_S3_Dosing, FC14_State_S35_Rest, FC15_State_S4_Transfer, FC16_State_S5_Run, FC17_State_S6_Drain, FC18_State_S7_End, FC19_State_Error, FC1_StateDispatcher, FC2_EStopHandling, FC30_ValveA_Diag, FC31_ValveB_Diag, FC32_ValveC_Diag, FC40_RhythmCorrection |
| VB3 | — | 16 | FC0_SysInit, FC10_State_S0_Init, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC13_State_S3_Dosing, FC14_State_S35_Rest, FC15_State_S4_Transfer, FC16_State_S5_Run, FC17_State_S6_Drain, FC18_State_S7_End, FC19_State_Error, FC1_StateDispatcher, FC2_EStopHandling, FC30_ValveA_Diag, FC31_ValveB_Diag, FC32_ValveC_Diag |
| V1.6 | M_TankA_State | 5 | FC0_SysInit, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC15_State_S4_Transfer, FC19_State_Error |
| V1.7 | M_TankB_State | 4 | FC0_SysInit, FC15_State_S4_Transfer, FC17_State_S6_Drain, FC19_State_Error |
| VD178 | VD_S5_Elapsed | 4 | FC0_SysInit, FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC16_State_S5_Run |

### 8.2 写后未读变量(可能为冗余或遗漏读取)

共14个VW/VD变量被写入但从未被读取,可能为:
- 运算中间变量(写后立即用AC0,不再读V区)
- HMI只读变量(PLC写,HMI读,STL内不读)
- 遗漏读取的变量(潜在bug)

| 变量 | 符号 | 写入FC |
|---|---|---|
| VD10 | — | FC13_State_S3_Dosing |
| VD14 | — | FC13_State_S3_Dosing |
| VD18 | — | FC13_State_S3_Dosing |
| VD74 | — | FC15_State_S4_Transfer |
| VD98 | — | FC13_State_S3_Dosing |
| VD116 | — | FC11_State_S1_Inlet, FC16_State_S5_Run, FC17_State_S6_Drain |
| VD128 | VD_CycleExtend_Target | FC40_RhythmCorrection |
| VD174 | — | FC11_State_S1_Inlet |
| VD190 | VD_DT10_Sec | FC0_SysInit |
| VW182 | VW_Corr_Mode | FC11_State_S1_Inlet, FC16_State_S5_Run |
| VW198 | VW_Init_Step | FC0_SysInit |
| VW204 | — | FC13_State_S3_Dosing |
| VW206 | — | FC13_State_S3_Dosing |
| VW300 | — | FC0_SysInit |

### 8.3 架构建议

1. **VW2状态机**: 被几乎所有FC读写,是核心调度变量。当前架构合理(FC1集中调度)。
2. **报警字V300~V303**: 被多个FC写入(各FC置位报警),FC3集中读取计算VW6。合理。
3. **QB0输出**: 被多个FC写入(各FC控制输出),需确认互斥(状态机保证同一时刻只有一个状态FC运行)。
4. **VD参数区(VD10~VD66)**: 应为HMI只写,FC只读。若FC写入参数区需排查(见静态分析报告)。
5. **诊断变量(VW260~VW270)**: FC30/31/32与FC11/15/17通过VW260/262/264/266/268/270握手,耦合清晰。
6. **中间变量(VD308~VD344)**: 各FC私有,无跨FC共享,耦合度低(2026-07-18修复后)。

---

*本报告由 cross_fc_dataflow_analyzer.py 自动生成。*