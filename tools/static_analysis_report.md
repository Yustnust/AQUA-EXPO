# PLC代码静态分析报告

| 项目 | 内容 |
|---|---|
| 分析对象 | S7-200 SMART STL代码(25个FC) |
| 分析工具 | stl_static_analyzer.py v1.0 |
| 变量表来源 | HMI-PLC变量地址表v1.0 + STL注释 |
| 分析日期 | 2026-07-18 |

## 一、分析摘要

- **问题总数**: 339 个
- **严重**: 3 个
- **警告**: 92 个
- **提示**: 244 个

## 二、STL文件统计

| FC名称 | 引用数 | 写入数 |
|---|---|---|
| FC0_SysInit | 11 | 9 |
| FC10_State_S0_Init | 9 | 5 |
| FC11_State_S1_Inlet | 54 | 36 |
| FC12_State_S2_PreMix | 9 | 6 |
| FC13_State_S3_Dosing | 104 | 46 |
| FC14_State_S35_Rest | 7 | 4 |
| FC15_State_S4_Transfer | 52 | 29 |
| FC16_State_S5_Run | 29 | 16 |
| FC17_State_S6_Drain | 19 | 13 |
| FC18_State_S7_End | 5 | 5 |
| FC19_State_Error | 20 | 13 |
| FC1_StateDispatcher | 12 | 1 |
| FC20_ManualControl | 25 | 10 |
| FC21_ManualSyringePump | 93 | 34 |
| FC22_RTC_Sync | 9 | 6 |
| FC2_EStopHandling | 10 | 5 |
| FC30_ValveA_Diag | 41 | 27 |
| FC31_ValveB_Diag | 39 | 31 |
| FC32_ValveC_Diag | 35 | 27 |
| FC3_AlarmHandling | 156 | 72 |
| FC40_RhythmCorrection | 63 | 40 |
| FC4_ModbusPolling | 81 | 27 |
| OB1_MAIN | 20 | 7 |
| SBR25_ColdStart | 110 | 79 |
| SBR26_WarmRecovery | 83 | 29 |
| **合计** | **1096** | **577** |

## 三、变量定义统计

- VB(字节): 1 个
- VW(字): 23 个
- VD(双字): 25 个
- Vbit(位): 34 个
- **合计**: 83 个变量定义

## 四、问题清单

### 严重(3个)

#### VD编址冲突(3个)

1. **[严重]** VD362(VB362~VB365) 与 VD364(VB364~VB367) 地址重叠
   - VD362引用: ['SBR25_ColdStart:L71(VD362)', 'FC15_State_S4_Transfer:L53(VD362)', 'SBR25_ColdStart:L39(VD362)']
   - VD364引用: ['FC11_State_S1_Inlet:L112(VD364)', 'SBR25_ColdStart:L154(VD364)', 'FC18_State_S7_End:L44(VD364)']
   - 重叠字节: VB364~VB365

2. **[严重]** VD364(VB364~VB367) 与 VD366(VB366~VB369) 地址重叠
   - VD364引用: ['FC11_State_S1_Inlet:L112(VD364)', 'SBR25_ColdStart:L154(VD364)', 'FC18_State_S7_End:L44(VD364)']
   - VD366引用: ['FC16_State_S5_Run:L78(VD366)', 'FC16_State_S5_Run:L105(VD366)']
   - 重叠字节: VB366~VB367

3. **[严重]** VD372(VB372~VB375) 与 VD374(VB374~VB377) 地址重叠
   - VD372引用: ['FC18_State_S7_End:L46(VD372)', 'FC13_State_S3_Dosing:L358(VD372)', 'FC13_State_S3_Dosing:L99(VD372)', 'FC13_State_S3_Dosing:L52(VD372)', 'SBR25_ColdStart:L163(VD372)']
   - VD374引用: ['SBR25_ColdStart:L199(VD374)']
   - 重叠字节: VB374~VB375

### 警告(92个)

#### 跨FC写入冲突(72个)

1. **[警告]** 变量 VW198 被 3 个FC写入: ['FC0_SysInit', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

2. **[警告]** 变量 VB378 被 2 个FC写入: ['FC0_SysInit', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

3. **[警告]** 变量 VB379 被 2 个FC写入: ['FC0_SysInit', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

4. **[警告]** 变量 VB380 被 2 个FC写入: ['FC0_SysInit', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

5. **[警告]** 变量 VB381 被 2 个FC写入: ['FC0_SysInit', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

6. **[警告]** 变量 VW390 被 4 个FC写入: ['FC0_SysInit', 'FC21_ManualSyringePump', 'OB1_MAIN', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

7. **[警告]** 变量 VD112 被 2 个FC写入: ['FC10_State_S0_Init', 'FC11_State_S1_Inlet']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

8. **[警告]** 变量 VD116 被 4 个FC写入: ['FC10_State_S0_Init', 'FC11_State_S1_Inlet', 'FC16_State_S5_Run', 'FC17_State_S6_Drain']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

9. **[警告]** 变量 VW2 被 20 个FC写入: ['FC10_State_S0_Init', 'FC11_State_S1_Inlet', 'FC12_State_S2_PreMix', 'FC13_State_S3_Dosing', 'FC14_State_S35_Rest', 'FC15_State_S4_Transfer', 'FC16_State_S5_Run', 'FC17_State_S6_Drain', 'FC18_State_S7_End', 'FC19_State_Error', 'FC1_StateDispatcher', 'FC22_RTC_Sync', 'FC2_EStopHandling', 'FC30_ValveA_Diag', 'FC31_ValveB_Diag', 'FC32_ValveC_Diag', 'FC40_RhythmCorrection', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

10. **[警告]** 变量 V1.0 被 4 个FC写入: ['FC10_State_S0_Init', 'FC18_State_S7_End', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

11. **[警告]** 变量 V0.0 被 2 个FC写入: ['FC10_State_S0_Init', 'FC19_State_Error']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

12. **[警告]** 变量 V1.6 被 5 个FC写入: ['FC11_State_S1_Inlet', 'FC12_State_S2_PreMix', 'FC15_State_S4_Transfer', 'FC19_State_Error', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

13. **[警告]** 变量 VD82 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

14. **[警告]** 变量 VB260 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

15. **[警告]** 变量 VB261 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

16. **[警告]** 变量 VB266 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

17. **[警告]** 变量 VW414 被 3 个FC写入: ['FC11_State_S1_Inlet', 'FC15_State_S4_Transfer', 'FC17_State_S6_Drain']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

18. **[警告]** 变量 VD444 被 5 个FC写入: ['FC11_State_S1_Inlet', 'FC15_State_S4_Transfer', 'FC16_State_S5_Run', 'FC17_State_S6_Drain', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

19. **[警告]** 变量 VD150 被 3 个FC写入: ['FC11_State_S1_Inlet', 'FC16_State_S5_Run', 'FC40_RhythmCorrection']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

20. **[警告]** 变量 VD178 被 5 个FC写入: ['FC11_State_S1_Inlet', 'FC15_State_S4_Transfer', 'FC16_State_S5_Run', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

21. **[警告]** 变量 VD154 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC16_State_S5_Run']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

22. **[警告]** 变量 VD124 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC40_RhythmCorrection']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

23. **[警告]** 变量 VW182 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC16_State_S5_Run']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

24. **[警告]** 变量 VD28 被 2 个FC写入: ['FC11_State_S1_Inlet', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

25. **[警告]** 变量 VD36 被 2 个FC写入: ['FC11_State_S1_Inlet', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

26. **[警告]** 变量 VD364 被 3 个FC写入: ['FC11_State_S1_Inlet', 'FC18_State_S7_End', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

27. **[警告]** 变量 VW226 被 3 个FC写入: ['FC12_State_S2_PreMix', 'FC13_State_S3_Dosing', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

28. **[警告]** 变量 VD372 被 3 个FC写入: ['FC13_State_S3_Dosing', 'FC18_State_S7_End', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

29. **[警告]** 变量 V303.4 被 3 个FC写入: ['FC13_State_S3_Dosing', 'FC3_AlarmHandling', 'FC4_ModbusPolling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

30. **[警告]** 变量 VD350 被 3 个FC写入: ['FC13_State_S3_Dosing', 'FC21_ManualSyringePump', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

31. **[警告]** 变量 VD102 被 2 个FC写入: ['FC13_State_S3_Dosing', 'FC21_ManualSyringePump']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

32. **[警告]** 变量 VW204 被 2 个FC写入: ['FC13_State_S3_Dosing', 'FC21_ManualSyringePump']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

33. **[警告]** 变量 VW206 被 2 个FC写入: ['FC13_State_S3_Dosing', 'FC21_ManualSyringePump']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

34. **[警告]** 变量 VW230 被 3 个FC写入: ['FC13_State_S3_Dosing', 'FC21_ManualSyringePump', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

35. **[警告]** 变量 VD232 被 3 个FC写入: ['FC13_State_S3_Dosing', 'FC21_ManualSyringePump', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

36. **[警告]** 变量 VD440 被 3 个FC写入: ['FC13_State_S3_Dosing', 'FC18_State_S7_End', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

37. **[警告]** 变量 VB262 被 2 个FC写入: ['FC15_State_S4_Transfer', 'FC31_ValveB_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

38. **[警告]** 变量 VB263 被 2 个FC写入: ['FC15_State_S4_Transfer', 'FC31_ValveB_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

39. **[警告]** 变量 VB268 被 2 个FC写入: ['FC15_State_S4_Transfer', 'FC31_ValveB_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

40. **[警告]** 变量 V1.7 被 4 个FC写入: ['FC15_State_S4_Transfer', 'FC17_State_S6_Drain', 'FC19_State_Error', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

41. **[警告]** 变量 V301.6 被 2 个FC写入: ['FC16_State_S5_Run', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

42. **[警告]** 变量 VB264 被 2 个FC写入: ['FC17_State_S6_Drain', 'FC32_ValveC_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

43. **[警告]** 变量 VB265 被 2 个FC写入: ['FC17_State_S6_Drain', 'FC32_ValveC_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

44. **[警告]** 变量 VW270 被 2 个FC写入: ['FC17_State_S6_Drain', 'FC32_ValveC_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

45. **[警告]** 变量 V300.4 被 4 个FC写入: ['FC19_State_Error', 'FC2_EStopHandling', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

46. **[警告]** 变量 V300.0 被 3 个FC写入: ['FC19_State_Error', 'FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

47. **[警告]** 变量 VW260 被 4 个FC写入: ['FC19_State_Error', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

48. **[警告]** 变量 VW6 被 4 个FC写入: ['FC19_State_Error', 'FC2_EStopHandling', 'FC3_AlarmHandling', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

49. **[警告]** 变量 V300.5 被 2 个FC写入: ['FC19_State_Error', 'FC2_EStopHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

50. **[警告]** 变量 VD392 被 2 个FC写入: ['FC21_ManualSyringePump', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

51. **[警告]** 变量 VD396 被 2 个FC写入: ['FC21_ManualSyringePump', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

52. **[警告]** 变量 V303.5 被 2 个FC写入: ['FC22_RTC_Sync', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

53. **[警告]** 变量 V303.7 被 3 个FC写入: ['FC22_RTC_Sync', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

54. **[警告]** 变量 V301.4 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

55. **[警告]** 变量 V301.5 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

56. **[警告]** 变量 V301.0 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

57. **[警告]** 变量 V301.2 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

58. **[警告]** 变量 V301.3 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

59. **[警告]** 变量 V300.1 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

60. **[警告]** 变量 V302.1 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

61. **[警告]** 变量 V302.2 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

62. **[警告]** 变量 V302.0 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

63. **[警告]** 变量 V302.4 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

64. **[警告]** 变量 V302.3 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

65. **[警告]** 变量 V302.6 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

66. **[警告]** 变量 V302.7 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

67. **[警告]** 变量 V302.5 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

68. **[警告]** 变量 V303.1 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

69. **[警告]** 变量 V303.0 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

70. **[警告]** 变量 VD40 被 2 个FC写入: ['FC40_RhythmCorrection', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

71. **[警告]** 变量 VD32 被 2 个FC写入: ['FC40_RhythmCorrection', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

72. **[警告]** 变量 VW290 被 2 个FC写入: ['FC4_ModbusPolling', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

#### 参数区写入(20个)

1. **[警告]** FC直接写入HMI参数区 VD82(VD82)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC11_State_S1_Inlet 第33行

2. **[警告]** FC直接写入HMI参数区 VD70(VD70)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC11_State_S1_Inlet 第87行

3. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC13_State_S3_Dosing 第106行

4. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC13_State_S3_Dosing 第109行

5. **[警告]** FC直接写入HMI参数区 VD74(VD74)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC15_State_S4_Transfer 第125行

6. **[警告]** FC直接写入HMI参数区 VD78(VD78)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC17_State_S6_Drain 第55行

7. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC21_ManualSyringePump 第69行

8. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC21_ManualSyringePump 第70行

9. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC21_ManualSyringePump 第74行

10. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC21_ManualSyringePump 第77行

11. **[警告]** FC直接写入HMI参数区 VD82(VD82)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC30_ValveA_Diag 第123行

12. **[警告]** FC直接写入HMI参数区 VD90(VD90)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC30_ValveA_Diag 第124行

13. **[警告]** FC直接写入HMI参数区 VD86(VD86)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC4_ModbusPolling 第105行

14. **[警告]** FC直接写入HMI参数区 VD94(VD94)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC4_ModbusPolling 第156行

15. **[警告]** FC直接写入HMI参数区 VD54(VD54)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第40行

16. **[警告]** FC直接写入HMI参数区 VD58(VD58)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第41行

17. **[警告]** FC直接写入HMI参数区 VD62(VD62)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第42行

18. **[警告]** FC直接写入HMI参数区 VD66(VD66)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第43行

19. **[警告]** FC直接写入HMI参数区 VD54(VD54)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第63行

20. **[警告]** FC直接写入HMI参数区 VD66(VD66)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第64行

### 提示(244个)

#### VD/VW子字访问(1个)

1. **[提示]** VW510位于VD508内部(VB508~VB511)
   - 可能是VD的高字访问(正常),或编址错误。VD508引用: ['SBR25_ColdStart:L69'], VW510引用: ['FC4_ModbusPolling:L228', 'FC4_ModbusPolling:L220', 'FC4_ModbusPolling:L250', 'FC21_ManualSyringePump:L257', 'FC21_ManualSyringePump:L269']

#### 对齐建议(125个)

1. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第33行

2. **[提示]** VD地址非4字节对齐: VD82(地址82)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第33行

3. **[提示]** VD地址非4字节对齐: VD358(地址358)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第40行

4. **[提示]** VD地址非4字节对齐: VD66(地址66)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第50行

5. **[提示]** VD地址非4字节对齐: VD70(地址70)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第87行

6. **[提示]** VD地址非4字节对齐: VD354(地址354)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第91行

7. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第91行

8. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第92行

9. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第93行

10. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第94行

11. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第94行

12. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第96行

13. **[提示]** VD地址非4字节对齐: VD174(地址174)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第97行

14. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第97行

15. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第98行

16. **[提示]** VD地址非4字节对齐: VD70(地址70)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第103行

17. **[提示]** VD地址非4字节对齐: VD174(地址174)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第105行

18. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第111行

19. **[提示]** VD地址非4字节对齐: VD346(地址346)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第99行

20. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第100行

21. **[提示]** VD地址非4字节对齐: VD346(地址346)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第100行

22. **[提示]** VD地址非4字节对齐: VD346(地址346)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第103行

23. **[提示]** VD地址非4字节对齐: VD346(地址346)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第105行

24. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第106行

25. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第109行

26. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第112行

27. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第249行

28. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第353行

29. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第354行

30. **[提示]** VD地址非4字节对齐: VD362(地址362)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC15_State_S4_Transfer 第53行

31. **[提示]** VD地址非4字节对齐: VD74(地址74)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC15_State_S4_Transfer 第125行

32. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC15_State_S4_Transfer 第141行

33. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第29行

34. **[提示]** VD地址非4字节对齐: VD354(地址354)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第38行

35. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第38行

36. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第39行

37. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第40行

38. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第41行

39. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第41行

40. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第46行

41. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第51行

42. **[提示]** VD地址非4字节对齐: VD366(地址366)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第78行

43. **[提示]** VD地址非4字节对齐: VD354(地址354)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第90行

44. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第93行

45. **[提示]** VD地址非4字节对齐: VD366(地址366)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第105行

46. **[提示]** VD地址非4字节对齐: VD54(地址54)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第31行

47. **[提示]** VD地址非4字节对齐: VD78(地址78)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第55行

48. **[提示]** VD地址非4字节对齐: VD78(地址78)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第57行

49. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第69行

50. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第70行

51. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第70行

52. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第71行

53. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第73行

54. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第74行

55. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第77行

56. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第92行

57. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第153行

58. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第191行

59. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC21_ManualSyringePump 第192行

60. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第122行

61. **[提示]** VD地址非4字节对齐: VD82(地址82)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第123行

62. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第124行

63. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第129行

64. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第132行

65. **[提示]** VD地址非4字节对齐: VD162(地址162)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第31行

66. **[提示]** VD地址非4字节对齐: VD162(地址162)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第32行

67. **[提示]** VD地址非4字节对齐: VD166(地址166)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第34行

68. **[提示]** VD地址非4字节对齐: VD166(地址166)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第35行

69. **[提示]** VD地址非4字节对齐: VD170(地址170)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第37行

70. **[提示]** VD地址非4字节对齐: VD170(地址170)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第38行

71. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第44行

72. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第44行

73. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第53行

74. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第53行

75. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第54行

76. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第54行

77. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第57行

78. **[提示]** VD地址非4字节对齐: VD162(地址162)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第57行

79. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第62行

80. **[提示]** VD地址非4字节对齐: VD162(地址162)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第63行

81. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第64行

82. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第70行

83. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第81行

84. **[提示]** VD地址非4字节对齐: VD166(地址166)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第81行

85. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第86行

86. **[提示]** VD地址非4字节对齐: VD166(地址166)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第87行

87. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第88行

88. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第94行

89. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第104行

90. **[提示]** VD地址非4字节对齐: VD170(地址170)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第104行

91. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第116行

92. **[提示]** VD地址非4字节对齐: VD410(地址410)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC4_ModbusPolling 第105行

93. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC4_ModbusPolling 第105行

94. **[提示]** VD地址非4字节对齐: VD410(地址410)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC4_ModbusPolling 第156行

95. **[提示]** VD地址非4字节对齐: VD94(地址94)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC4_ModbusPolling 第156行

96. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第20行

97. **[提示]** VD地址非4字节对齐: VD354(地址354)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第23行

98. **[提示]** VD地址非4字节对齐: VD358(地址358)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第38行

99. **[提示]** VD地址非4字节对齐: VD362(地址362)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第39行

100. **[提示]** VD地址非4字节对齐: VD54(地址54)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第40行

101. **[提示]** VD地址非4字节对齐: VD58(地址58)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第41行

102. **[提示]** VD地址非4字节对齐: VD62(地址62)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第42行

103. **[提示]** VD地址非4字节对齐: VD66(地址66)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第43行

104. **[提示]** VD地址非4字节对齐: VD54(地址54)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第63行

105. **[提示]** VD地址非4字节对齐: VD66(地址66)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第64行

106. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第68行

107. **[提示]** VD地址非4字节对齐: VD354(地址354)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第69行

108. **[提示]** VD地址非4字节对齐: VD358(地址358)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第70行

109. **[提示]** VD地址非4字节对齐: VD362(地址362)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第71行

110. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第166行

111. **[提示]** VD地址非4字节对齐: VD374(地址374)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第199行

112. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第90行

113. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第100行

114. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第105行

115. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第110行

116. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第114行

117. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第117行

118. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第122行

119. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第127行

120. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第131行

121. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第137行

122. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第137行

123. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第138行

124. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第138行

125. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第144行

#### 未使用变量(2个)

1. **[提示]** 变量 VW266(0进行中/1正常完成/2故障) 定义但未在STL中引用
   - 来源: FC11_State_S1_Inlet.stl

2. **[提示]** 变量 VD312(已删除(原阀A内漏差值,2026-09-14废弃)) 定义但未在STL中引用
   - 来源: FC30_ValveA_Diag.stl

#### 未定义变量(116个)

1. **[提示]** 变量 VW600 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 31
   - 位置: FC0_SysInit 第31行

2. **[提示]** 变量 VB378 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 33
   - 位置: FC0_SysInit 第33行

3. **[提示]** 变量 VB379 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 35
   - 位置: FC0_SysInit 第35行

4. **[提示]** 变量 VB380 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 37
   - 位置: FC0_SysInit 第37行

5. **[提示]** 变量 VB381 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 39
   - 位置: FC0_SysInit 第39行

6. **[提示]** 变量 VW390 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 45
   - 位置: FC0_SysInit 第45行

7. **[提示]** 变量 VD144 在STL中引用但变量表/注释未定义
   - FC: FC10_State_S0_Init, 行: 55
   - 位置: FC10_State_S0_Init 第55行

8. **[提示]** 变量 VD108 在STL中引用但变量表/注释未定义
   - FC: FC10_State_S0_Init, 行: 56
   - 位置: FC10_State_S0_Init 第56行

9. **[提示]** 变量 VD116 在STL中引用但变量表/注释未定义
   - FC: FC10_State_S0_Init, 行: 56
   - 位置: FC10_State_S0_Init 第56行

10. **[提示]** 变量 VD86 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 33
   - 位置: FC11_State_S1_Inlet 第33行

11. **[提示]** 变量 VD82 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 33
   - 位置: FC11_State_S1_Inlet 第33行

12. **[提示]** 变量 VD358 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 40
   - 位置: FC11_State_S1_Inlet 第40行

13. **[提示]** 变量 VD66 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 50
   - 位置: FC11_State_S1_Inlet 第50行

14. **[提示]** 变量 VD320 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 50
   - 位置: FC11_State_S1_Inlet 第50行

15. **[提示]** 变量 VB260 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 60
   - 位置: FC11_State_S1_Inlet 第60行

16. **[提示]** 变量 VB261 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 61
   - 位置: FC11_State_S1_Inlet 第61行

17. **[提示]** 变量 VB266 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 62
   - 位置: FC11_State_S1_Inlet 第62行

18. **[提示]** 变量 VB267 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 63
   - 位置: FC11_State_S1_Inlet 第63行

19. **[提示]** 变量 VW414 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 85
   - 位置: FC11_State_S1_Inlet 第85行

20. **[提示]** 变量 VD70 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 87
   - 位置: FC11_State_S1_Inlet 第87行

21. **[提示]** 变量 VD354 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 91
   - 位置: FC11_State_S1_Inlet 第91行

22. **[提示]** 变量 VD174 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 97
   - 位置: FC11_State_S1_Inlet 第97行

23. **[提示]** 变量 VD28 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 104
   - 位置: FC11_State_S1_Inlet 第104行

24. **[提示]** 变量 VD36 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 106
   - 位置: FC11_State_S1_Inlet 第106行

25. **[提示]** 变量 VD364 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 112
   - 位置: FC11_State_S1_Inlet 第112行

26. **[提示]** 变量 VD350 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 100
   - 位置: FC13_State_S3_Dosing 第100行

27. **[提示]** 变量 VD440 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 356
   - 位置: FC13_State_S3_Dosing 第356行

28. **[提示]** 变量 VB262 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 47
   - 位置: FC15_State_S4_Transfer 第47行

29. **[提示]** 变量 VB263 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 48
   - 位置: FC15_State_S4_Transfer 第48行

30. **[提示]** 变量 VB268 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 50
   - 位置: FC15_State_S4_Transfer 第50行

31. **[提示]** 变量 VB269 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 51
   - 位置: FC15_State_S4_Transfer 第51行

32. **[提示]** 变量 VD362 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 53
   - 位置: FC15_State_S4_Transfer 第53行

33. **[提示]** 变量 VD324 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 53
   - 位置: FC15_State_S4_Transfer 第53行

34. **[提示]** 变量 VW274 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 56
   - 位置: FC15_State_S4_Transfer 第56行

35. **[提示]** 变量 VD74 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 125
   - 位置: FC15_State_S4_Transfer 第125行

36. **[提示]** 变量 VB900 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 130
   - 位置: FC15_State_S4_Transfer 第130行

37. **[提示]** 变量 VB10 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 131
   - 位置: FC15_State_S4_Transfer 第131行

38. **[提示]** 变量 VB901 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 132
   - 位置: FC15_State_S4_Transfer 第132行

39. **[提示]** 变量 VB11 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 132
   - 位置: FC15_State_S4_Transfer 第132行

40. **[提示]** 变量 VB902 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 133
   - 位置: FC15_State_S4_Transfer 第133行

41. **[提示]** 变量 VB12 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 133
   - 位置: FC15_State_S4_Transfer 第133行

42. **[提示]** 变量 VB903 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 134
   - 位置: FC15_State_S4_Transfer 第134行

43. **[提示]** 变量 VB13 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 134
   - 位置: FC15_State_S4_Transfer 第134行

44. **[提示]** 变量 VB904 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 135
   - 位置: FC15_State_S4_Transfer 第135行

45. **[提示]** 变量 VB14 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 135
   - 位置: FC15_State_S4_Transfer 第135行

46. **[提示]** 变量 VB905 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 136
   - 位置: FC15_State_S4_Transfer 第136行

47. **[提示]** 变量 VB15 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 136
   - 位置: FC15_State_S4_Transfer 第136行

48. **[提示]** 变量 VB906 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 137
   - 位置: FC15_State_S4_Transfer 第137行

49. **[提示]** 变量 VB16 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 137
   - 位置: FC15_State_S4_Transfer 第137行

50. **[提示]** 变量 VB908 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 138
   - 位置: FC15_State_S4_Transfer 第138行

51. **[提示]** 变量 VB17 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 138
   - 位置: FC15_State_S4_Transfer 第138行

52. **[提示]** 变量 VD366 在STL中引用但变量表/注释未定义
   - FC: FC16_State_S5_Run, 行: 78
   - 位置: FC16_State_S5_Run 第78行

53. **[提示]** 变量 VD24 在STL中引用但变量表/注释未定义
   - FC: FC16_State_S5_Run, 行: 105
   - 位置: FC16_State_S5_Run 第105行

54. **[提示]** 变量 VB264 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 26
   - 位置: FC17_State_S6_Drain 第26行

55. **[提示]** 变量 VB265 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 27
   - 位置: FC17_State_S6_Drain 第27行

56. **[提示]** 变量 VD54 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 31
   - 位置: FC17_State_S6_Drain 第31行

57. **[提示]** 变量 VD328 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 31
   - 位置: FC17_State_S6_Drain 第31行

58. **[提示]** 变量 VD78 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 55
   - 位置: FC17_State_S6_Drain 第55行

59. **[提示]** 变量 VD392 在STL中引用但变量表/注释未定义
   - FC: FC21_ManualSyringePump, 行: 20
   - 位置: FC21_ManualSyringePump 第20行

60. **[提示]** 变量 VD452 在STL中引用但变量表/注释未定义
   - FC: FC21_ManualSyringePump, 行: 21
   - 位置: FC21_ManualSyringePump 第21行

61. **[提示]** 变量 VD396 在STL中引用但变量表/注释未定义
   - FC: FC21_ManualSyringePump, 行: 21
   - 位置: FC21_ManualSyringePump 第21行

62. **[提示]** 变量 VW388 在STL中引用但变量表/注释未定义
   - FC: FC21_ManualSyringePump, 行: 215
   - 位置: FC21_ManualSyringePump 第215行

63. **[提示]** 变量 VW510 在STL中引用但变量表/注释未定义
   - FC: FC21_ManualSyringePump, 行: 257
   - 位置: FC21_ManualSyringePump 第257行

64. **[提示]** 变量 VB500 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 434
   - 位置: FC3_AlarmHandling 第434行

65. **[提示]** 变量 VB7 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 435
   - 位置: FC3_AlarmHandling 第435行

66. **[提示]** 变量 VB509 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 435
   - 位置: FC3_AlarmHandling 第435行

67. **[提示]** 变量 VB510 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 436
   - 位置: FC3_AlarmHandling 第436行

68. **[提示]** 变量 VB508 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 437
   - 位置: FC3_AlarmHandling 第437行

69. **[提示]** 变量 VD40 在STL中引用但变量表/注释未定义
   - FC: FC40_RhythmCorrection, 行: 32
   - 位置: FC40_RhythmCorrection 第32行

70. **[提示]** 变量 VD32 在STL中引用但变量表/注释未定义
   - FC: FC40_RhythmCorrection, 行: 35
   - 位置: FC40_RhythmCorrection 第35行

71. **[提示]** 变量 VD44 在STL中引用但变量表/注释未定义
   - FC: FC40_RhythmCorrection, 行: 37
   - 位置: FC40_RhythmCorrection 第37行

72. **[提示]** 变量 VB184 在STL中引用但变量表/注释未定义
   - FC: FC40_RhythmCorrection, 行: 73
   - 位置: FC40_RhythmCorrection 第73行

73. **[提示]** 变量 VW290 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 22
   - 位置: FC4_ModbusPolling 第22行

74. **[提示]** 变量 VB410 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 28
   - 位置: FC4_ModbusPolling 第28行

75. **[提示]** 变量 VB382 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 58
   - 位置: FC4_ModbusPolling 第58行

76. **[提示]** 变量 VW410 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 64
   - 位置: FC4_ModbusPolling 第64行

77. **[提示]** 变量 VW292 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 66
   - 位置: FC4_ModbusPolling 第66行

78. **[提示]** 变量 VW224 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 70
   - 位置: FC4_ModbusPolling 第70行

79. **[提示]** 变量 VD410 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 105
   - 位置: FC4_ModbusPolling 第105行

80. **[提示]** 变量 VW294 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 107
   - 位置: FC4_ModbusPolling 第107行

81. **[提示]** 变量 VW222 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 131
   - 位置: FC4_ModbusPolling 第131行

82. **[提示]** 变量 VW296 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 133
   - 位置: FC4_ModbusPolling 第133行

83. **[提示]** 变量 VD94 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 156
   - 位置: FC4_ModbusPolling 第156行

84. **[提示]** 变量 VW298 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 158
   - 位置: FC4_ModbusPolling 第158行

85. **[提示]** 变量 VB383 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 211
   - 位置: FC4_ModbusPolling 第211行

86. **[提示]** 变量 VB305 在STL中引用但变量表/注释未定义
   - FC: OB1_MAIN, 行: 146
   - 位置: OB1_MAIN 第146行

87. **[提示]** 变量 VD58 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 41
   - 位置: SBR25_ColdStart 第41行

88. **[提示]** 变量 VD62 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 42
   - 位置: SBR25_ColdStart 第42行

89. **[提示]** 变量 VB456 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 51
   - 位置: SBR25_ColdStart 第51行

90. **[提示]** 变量 VD460 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 57
   - 位置: SBR25_ColdStart 第57行

91. **[提示]** 变量 VD464 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 58
   - 位置: SBR25_ColdStart 第58行

92. **[提示]** 变量 VD468 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 59
   - 位置: SBR25_ColdStart 第59行

93. **[提示]** 变量 VD472 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 60
   - 位置: SBR25_ColdStart 第60行

94. **[提示]** 变量 VD476 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 61
   - 位置: SBR25_ColdStart 第61行

95. **[提示]** 变量 VD480 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 62
   - 位置: SBR25_ColdStart 第62行

96. **[提示]** 变量 VD484 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 63
   - 位置: SBR25_ColdStart 第63行

97. **[提示]** 变量 VD488 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 64
   - 位置: SBR25_ColdStart 第64行

98. **[提示]** 变量 VD492 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 65
   - 位置: SBR25_ColdStart 第65行

99. **[提示]** 变量 VD496 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 66
   - 位置: SBR25_ColdStart 第66行

100. **[提示]** 变量 VD500 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 67
   - 位置: SBR25_ColdStart 第67行

101. **[提示]** 变量 VD504 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 68
   - 位置: SBR25_ColdStart 第68行

102. **[提示]** 变量 VD508 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 69
   - 位置: SBR25_ColdStart 第69行

103. **[提示]** 变量 VD512 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 70
   - 位置: SBR25_ColdStart 第70行

104. **[提示]** 变量 VD516 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 71
   - 位置: SBR25_ColdStart 第71行

105. **[提示]** 变量 VD520 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 72
   - 位置: SBR25_ColdStart 第72行

106. **[提示]** 变量 VD524 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 73
   - 位置: SBR25_ColdStart 第73行

107. **[提示]** 变量 VD528 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 74
   - 位置: SBR25_ColdStart 第74行

108. **[提示]** 变量 VB532 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 77
   - 位置: SBR25_ColdStart 第77行

109. **[提示]** 变量 VB388 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 77
   - 位置: SBR25_ColdStart 第77行

110. **[提示]** 变量 VB389 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 78
   - 位置: SBR25_ColdStart 第78行

111. **[提示]** 变量 VB536 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 81
   - 位置: SBR25_ColdStart 第81行

112. **[提示]** 变量 VW300 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 139
   - 位置: SBR25_ColdStart 第139行

113. **[提示]** 变量 VB0 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 147
   - 位置: SBR25_ColdStart 第147行

114. **[提示]** 变量 VD374 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 199
   - 位置: SBR25_ColdStart 第199行

115. **[提示]** 变量 VD186 在STL中引用但变量表/注释未定义
   - FC: SBR26_WarmRecovery, 行: 100
   - 位置: SBR26_WarmRecovery 第100行

116. **[提示]** 变量 VD190 在STL中引用但变量表/注释未定义
   - FC: SBR26_WarmRecovery, 行: 117
   - 位置: SBR26_WarmRecovery 第117行

## 五、跨FC变量访问矩阵(写入)

以下变量被多个FC写入(需确认调用顺序与互斥性):

| 变量 | 写入FC数 | FC列表 |
|---|---|---|
| VW2 | 20 | FC10_State_S0_Init, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC13_State_S3_Dosing, FC14_State_S35_Rest, FC15_State_S4_Transfer, FC16_State_S5_Run, FC17_State_S6_Drain, FC18_State_S7_End, FC19_State_Error, FC1_StateDispatcher, FC22_RTC_Sync, FC2_EStopHandling, FC30_ValveA_Diag, FC31_ValveB_Diag, FC32_ValveC_Diag, FC40_RhythmCorrection, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VW6 | 4 | FC19_State_Error, FC2_EStopHandling, FC3_AlarmHandling, SBR25_ColdStart |
| V0.0 | 2 | FC10_State_S0_Init, FC19_State_Error |
| V1.0 | 4 | FC10_State_S0_Init, FC18_State_S7_End, SBR25_ColdStart, SBR26_WarmRecovery |
| V1.6 | 5 | FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC15_State_S4_Transfer, FC19_State_Error, SBR25_ColdStart |
| V1.7 | 4 | FC15_State_S4_Transfer, FC17_State_S6_Drain, FC19_State_Error, SBR25_ColdStart |
| VD28 | 2 | FC11_State_S1_Inlet, SBR25_ColdStart |
| VD32 | 2 | FC40_RhythmCorrection, SBR25_ColdStart |
| VD36 | 2 | FC11_State_S1_Inlet, SBR25_ColdStart |
| VD40 | 2 | FC40_RhythmCorrection, SBR25_ColdStart |
| VD82 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| VB260 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| VB261 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| VB262 | 2 | FC15_State_S4_Transfer, FC31_ValveB_Diag |
| VB263 | 2 | FC15_State_S4_Transfer, FC31_ValveB_Diag |
| VB264 | 2 | FC17_State_S6_Drain, FC32_ValveC_Diag |
| VB265 | 2 | FC17_State_S6_Drain, FC32_ValveC_Diag |
| VB266 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| VB268 | 2 | FC15_State_S4_Transfer, FC31_ValveB_Diag |
| VB378 | 2 | FC0_SysInit, SBR25_ColdStart |
| VB379 | 2 | FC0_SysInit, SBR25_ColdStart |
| VB380 | 2 | FC0_SysInit, SBR25_ColdStart |
| VB381 | 2 | FC0_SysInit, SBR25_ColdStart |
| VD102 | 2 | FC13_State_S3_Dosing, FC21_ManualSyringePump |
| VD112 | 2 | FC10_State_S0_Init, FC11_State_S1_Inlet |
| VD116 | 4 | FC10_State_S0_Init, FC11_State_S1_Inlet, FC16_State_S5_Run, FC17_State_S6_Drain |
| VD124 | 2 | FC11_State_S1_Inlet, FC40_RhythmCorrection |
| VD150 | 3 | FC11_State_S1_Inlet, FC16_State_S5_Run, FC40_RhythmCorrection |
| VD154 | 2 | FC11_State_S1_Inlet, FC16_State_S5_Run |
| VD178 | 5 | FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC16_State_S5_Run, SBR25_ColdStart, SBR26_WarmRecovery |
| VD232 | 3 | FC13_State_S3_Dosing, FC21_ManualSyringePump, SBR25_ColdStart |
| VD350 | 3 | FC13_State_S3_Dosing, FC21_ManualSyringePump, SBR25_ColdStart |
| VD364 | 3 | FC11_State_S1_Inlet, FC18_State_S7_End, SBR25_ColdStart |
| VD372 | 3 | FC13_State_S3_Dosing, FC18_State_S7_End, SBR25_ColdStart |
| VD392 | 2 | FC21_ManualSyringePump, SBR25_ColdStart |
| VD396 | 2 | FC21_ManualSyringePump, SBR25_ColdStart |
| VD440 | 3 | FC13_State_S3_Dosing, FC18_State_S7_End, SBR25_ColdStart |
| VD444 | 5 | FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC16_State_S5_Run, FC17_State_S6_Drain, SBR25_ColdStart |
| VW182 | 2 | FC11_State_S1_Inlet, FC16_State_S5_Run |
| VW198 | 3 | FC0_SysInit, SBR25_ColdStart, SBR26_WarmRecovery |
| VW204 | 2 | FC13_State_S3_Dosing, FC21_ManualSyringePump |
| VW206 | 2 | FC13_State_S3_Dosing, FC21_ManualSyringePump |
| VW226 | 3 | FC12_State_S2_PreMix, FC13_State_S3_Dosing, SBR25_ColdStart |
| VW230 | 3 | FC13_State_S3_Dosing, FC21_ManualSyringePump, SBR25_ColdStart |
| VW260 | 4 | FC19_State_Error, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VW270 | 2 | FC17_State_S6_Drain, FC32_ValveC_Diag |
| VW290 | 2 | FC4_ModbusPolling, SBR25_ColdStart |
| VW390 | 4 | FC0_SysInit, FC21_ManualSyringePump, OB1_MAIN, SBR25_ColdStart |
| VW414 | 3 | FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC17_State_S6_Drain |
| V300.0 | 3 | FC19_State_Error, FC30_ValveA_Diag, FC3_AlarmHandling |
| V300.1 | 2 | FC31_ValveB_Diag, FC3_AlarmHandling |
| V300.4 | 4 | FC19_State_Error, FC2_EStopHandling, SBR25_ColdStart, SBR26_WarmRecovery |
| V300.5 | 2 | FC19_State_Error, FC2_EStopHandling |
| V301.0 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.2 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.3 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.4 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.5 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.6 | 2 | FC16_State_S5_Run, FC3_AlarmHandling |
| V302.0 | 2 | FC31_ValveB_Diag, FC3_AlarmHandling |
| V302.1 | 2 | FC31_ValveB_Diag, FC3_AlarmHandling |
| V302.2 | 2 | FC31_ValveB_Diag, FC3_AlarmHandling |
| V302.3 | 2 | FC31_ValveB_Diag, FC3_AlarmHandling |
| V302.4 | 2 | FC31_ValveB_Diag, FC3_AlarmHandling |
| V302.5 | 2 | FC32_ValveC_Diag, FC3_AlarmHandling |
| V302.6 | 2 | FC32_ValveC_Diag, FC3_AlarmHandling |
| V302.7 | 2 | FC32_ValveC_Diag, FC3_AlarmHandling |
| V303.0 | 2 | FC32_ValveC_Diag, FC3_AlarmHandling |
| V303.1 | 2 | FC32_ValveC_Diag, FC3_AlarmHandling |
| V303.4 | 3 | FC13_State_S3_Dosing, FC3_AlarmHandling, FC4_ModbusPolling |
| V303.5 | 2 | FC22_RTC_Sync, FC3_AlarmHandling |
| V303.7 | 3 | FC22_RTC_Sync, SBR25_ColdStart, SBR26_WarmRecovery |

## 六、V区使用热力图(引用次数Top20)

| 字节地址 | 引用次数 |
|---|---|
| VB2 | 70 |
| VB3 | 70 |
| VB303 | 53 |
| VB302 | 50 |
| VB226 | 48 |
| VB227 | 48 |
| VB7 | 45 |
| VB6 | 44 |
| VB300 | 43 |
| VB390 | 42 |
| VB391 | 42 |
| VB301 | 40 |
| VB1 | 30 |
| VB4 | 23 |
| VB5 | 23 |
| VB260 | 21 |
| VB261 | 16 |
| VB306 | 16 |
| VB0 | 14 |
| VB102 | 14 |

## 七、结论与建议

❌ 发现 3 个严重问题,必须立即修复后方可交付。
ℹ️ 另有 244 个提示项,可择机处理。

---

*本报告由 stl_static_analyzer.py 自动生成,可重复执行以跟踪问题修复进度。*