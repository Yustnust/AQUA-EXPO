# PLC代码静态分析报告

| 项目 | 内容 |
|---|---|
| 分析对象 | S7-200 SMART STL代码(27个FC) |
| 分析工具 | stl_static_analyzer.py v1.0 |
| 变量表来源 | HMI-PLC变量地址表v1.0 + STL注释 |
| 分析日期 | 2026-07-18 |

## 一、分析摘要

- **问题总数**: 259 个
- **严重**: 1 个
- **警告**: 76 个
- **提示**: 182 个

## 二、STL文件统计

| FC名称 | 引用数 | 写入数 |
|---|---|---|
| FC0_SysInit | 5 | 5 |
| FC10_State_S0_Init | 11 | 4 |
| FC11_State_S1_Inlet | 40 | 19 |
| FC13A_PumpErrExit | 3 | 3 |
| FC13_State_S3_Dosing | 1 | 0 |
| FC15_State_S4_Transfer | 74 | 24 |
| FC16_State_S5_Run | 7 | 2 |
| FC17_State_S6_Drain | 46 | 17 |
| FC18_State_S7_End | 5 | 5 |
| FC19_State_Error | 63 | 31 |
| FC1A_State_S2_MixDose | 28 | 8 |
| FC1_StateDispatcher | 8 | 1 |
| FC20_ManualControl | 25 | 10 |
| FC21_ManualSyringePump | 30 | 9 |
| FC22_RTC_Sync | 9 | 6 |
| FC23_PumpEngine | 195 | 54 |
| FC2_EStopHandling | 9 | 3 |
| FC30_ValveA_Diag | 46 | 23 |
| FC31_ValveB_Diag | 43 | 26 |
| FC32_ValveC_Diag | 37 | 18 |
| FC3A_AlarmReset_Common | 30 | 14 |
| FC3_AlarmHandling | 101 | 34 |
| FC40_RhythmCorrection | 57 | 18 |
| FC4_ModbusPolling | 104 | 26 |
| OB1_MAIN | 38 | 17 |
| SBR25_ColdStart | 98 | 70 |
| SBR26_WarmRecovery | 103 | 39 |
| **合计** | **1216** | **486** |

## 三、变量定义统计

- VB(字节): 1 个
- VW(字): 22 个
- VD(双字): 21 个
- Vbit(位): 41 个
- **合计**: 85 个变量定义

## 四、问题清单

### 严重(1个)

#### VD编址冲突(1个)

1. **[严重]** VD372(VB372~VB375) 与 VD374(VB374~VB377) 地址重叠
   - VD372引用: ['SBR25_ColdStart:L177(VD372)', 'FC18_State_S7_End:L46(VD372)', 'FC1A_State_S2_MixDose:L55(VD372)', 'FC23_PumpEngine:L215(VD372)', 'FC23_PumpEngine:L195(VD372)', 'FC23_PumpEngine:L446(VD372)', 'FC21_ManualSyringePump:L33(VD372)', 'FC21_ManualSyringePump:L46(VD372)']
   - VD374引用: ['SBR25_ColdStart:L206(VD374)']
   - 重叠字节: VB374~VB375

### 警告(76个)

#### 跨FC写入冲突(61个)

1. **[警告]** 变量 VW198 被 3 个FC写入: ['FC0_SysInit', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

2. **[警告]** 变量 VW378 被 2 个FC写入: ['FC0_SysInit', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

3. **[警告]** 变量 VW390 被 4 个FC写入: ['FC0_SysInit', 'FC21_ManualSyringePump', 'OB1_MAIN', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

4. **[警告]** 变量 VW418 被 8 个FC写入: ['FC10_State_S0_Init', 'FC11_State_S1_Inlet', 'FC15_State_S4_Transfer', 'FC19_State_Error', 'FC1A_State_S2_MixDose', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

5. **[警告]** 变量 VW2 被 17 个FC写入: ['FC10_State_S0_Init', 'FC13A_PumpErrExit', 'FC15_State_S4_Transfer', 'FC16_State_S5_Run', 'FC17_State_S6_Drain', 'FC18_State_S7_End', 'FC19_State_Error', 'FC1_StateDispatcher', 'FC22_RTC_Sync', 'FC2_EStopHandling', 'FC30_ValveA_Diag', 'FC31_ValveB_Diag', 'FC32_ValveC_Diag', 'FC40_RhythmCorrection', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

6. **[警告]** 变量 V1.0 被 4 个FC写入: ['FC10_State_S0_Init', 'FC18_State_S7_End', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

7. **[警告]** 变量 V0.0 被 2 个FC写入: ['FC10_State_S0_Init', 'FC19_State_Error']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

8. **[警告]** 变量 V1.6 被 3 个FC写入: ['FC11_State_S1_Inlet', 'FC19_State_Error', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

9. **[警告]** 变量 VD82 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

10. **[警告]** 变量 VW260 被 6 个FC写入: ['FC11_State_S1_Inlet', 'FC19_State_Error', 'FC30_ValveA_Diag', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

11. **[警告]** 变量 VB266 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

12. **[警告]** 变量 VD252 被 7 个FC写入: ['FC11_State_S1_Inlet', 'FC19_State_Error', 'FC3_AlarmHandling', 'FC40_RhythmCorrection', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

13. **[警告]** 变量 VD248 被 7 个FC写入: ['FC11_State_S1_Inlet', 'FC19_State_Error', 'FC3_AlarmHandling', 'FC40_RhythmCorrection', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

14. **[警告]** 变量 VD444 被 4 个FC写入: ['FC11_State_S1_Inlet', 'FC15_State_S4_Transfer', 'FC17_State_S6_Drain', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

15. **[警告]** 变量 VD406 被 3 个FC写入: ['FC11_State_S1_Inlet', 'FC18_State_S7_End', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

16. **[警告]** 变量 V303.4 被 4 个FC写入: ['FC13A_PumpErrExit', 'FC1A_State_S2_MixDose', 'FC3A_AlarmReset_Common', 'FC4_ModbusPolling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

17. **[警告]** 变量 VW226 被 6 个FC写入: ['FC13A_PumpErrExit', 'FC1A_State_S2_MixDose', 'FC21_ManualSyringePump', 'FC23_PumpEngine', 'OB1_MAIN', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

18. **[警告]** 变量 VD116 被 3 个FC写入: ['FC15_State_S4_Transfer', 'FC17_State_S6_Drain', 'FC40_RhythmCorrection']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

19. **[警告]** 变量 V1.7 被 4 个FC写入: ['FC15_State_S4_Transfer', 'FC17_State_S6_Drain', 'FC19_State_Error', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

20. **[警告]** 变量 VD178 被 3 个FC写入: ['FC15_State_S4_Transfer', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

21. **[警告]** 变量 VW270 被 2 个FC写入: ['FC17_State_S6_Drain', 'FC32_ValveC_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

22. **[警告]** 变量 VD440 被 5 个FC写入: ['FC18_State_S7_End', 'FC1A_State_S2_MixDose', 'FC21_ManualSyringePump', 'FC23_PumpEngine', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

23. **[警告]** 变量 VD372 被 5 个FC写入: ['FC18_State_S7_End', 'FC1A_State_S2_MixDose', 'FC21_ManualSyringePump', 'FC23_PumpEngine', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

24. **[警告]** 变量 V300.4 被 4 个FC写入: ['FC19_State_Error', 'FC2_EStopHandling', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

25. **[警告]** 变量 V300.0 被 3 个FC写入: ['FC19_State_Error', 'FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

26. **[警告]** 变量 V301.0 被 3 个FC写入: ['FC19_State_Error', 'FC30_ValveA_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

27. **[警告]** 变量 V302.0 被 3 个FC写入: ['FC19_State_Error', 'FC31_ValveB_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

28. **[警告]** 变量 V303.0 被 3 个FC写入: ['FC19_State_Error', 'FC32_ValveC_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

29. **[警告]** 变量 VW6 被 3 个FC写入: ['FC19_State_Error', 'FC3_AlarmHandling', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

30. **[警告]** 变量 VW400 被 4 个FC写入: ['FC19_State_Error', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

31. **[警告]** 变量 VD256 被 5 个FC写入: ['FC19_State_Error', 'FC40_RhythmCorrection', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

32. **[警告]** 变量 VD244 被 5 个FC写入: ['FC19_State_Error', 'FC40_RhythmCorrection', 'OB1_MAIN', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

33. **[警告]** 变量 V300.5 被 2 个FC写入: ['FC19_State_Error', 'FC2_EStopHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

34. **[警告]** 变量 VD392 被 2 个FC写入: ['FC21_ManualSyringePump', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

35. **[警告]** 变量 VD396 被 2 个FC写入: ['FC21_ManualSyringePump', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

36. **[警告]** 变量 V62.5 被 2 个FC写入: ['FC21_ManualSyringePump', 'FC23_PumpEngine']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

37. **[警告]** 变量 V307.2 被 2 个FC写入: ['FC21_ManualSyringePump', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

38. **[警告]** 变量 V303.7 被 3 个FC写入: ['FC22_RTC_Sync', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

39. **[警告]** 变量 VW230 被 3 个FC写入: ['FC23_PumpEngine', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

40. **[警告]** 变量 VD232 被 3 个FC写入: ['FC23_PumpEngine', 'SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

41. **[警告]** 变量 VD350 被 2 个FC写入: ['FC23_PumpEngine', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

42. **[警告]** 变量 V301.4 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

43. **[警告]** 变量 V301.5 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

44. **[警告]** 变量 V301.2 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

45. **[警告]** 变量 V301.3 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

46. **[警告]** 变量 V300.1 被 3 个FC写入: ['FC31_ValveB_Diag', 'FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

47. **[警告]** 变量 V302.1 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

48. **[警告]** 变量 V302.2 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

49. **[警告]** 变量 V302.4 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

50. **[警告]** 变量 V302.3 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

51. **[警告]** 变量 V302.6 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3A_AlarmReset_Common']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

52. **[警告]** 变量 V303.6 被 2 个FC写入: ['FC3_AlarmHandling', 'FC40_RhythmCorrection']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

53. **[警告]** 变量 VD186 被 2 个FC写入: ['FC40_RhythmCorrection', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

54. **[警告]** 变量 VD414 被 2 个FC写入: ['FC40_RhythmCorrection', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

55. **[警告]** 变量 VD426 被 2 个FC写入: ['FC40_RhythmCorrection', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

56. **[警告]** 变量 VD430 被 2 个FC写入: ['FC40_RhythmCorrection', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

57. **[警告]** 变量 VD28 被 2 个FC写入: ['FC40_RhythmCorrection', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

58. **[警告]** 变量 VW290 被 2 个FC写入: ['FC4_ModbusPolling', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

59. **[警告]** 变量 VD24 被 2 个FC写入: ['OB1_MAIN', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

60. **[警告]** 变量 VW8 被 2 个FC写入: ['OB1_MAIN', 'SBR25_ColdStart']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

61. **[警告]** 变量 VD472 被 2 个FC写入: ['SBR25_ColdStart', 'SBR26_WarmRecovery']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

#### 参数区写入(15个)

1. **[警告]** FC直接写入HMI参数区 VD82(VD82)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC11_State_S1_Inlet 第38行

2. **[警告]** FC直接写入HMI参数区 VD70(VD70)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC11_State_S1_Inlet 第87行

3. **[警告]** FC直接写入HMI参数区 VD70(VD70)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC11_State_S1_Inlet 第88行

4. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC23_PumpEngine 第215行

5. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC23_PumpEngine 第216行

6. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC23_PumpEngine 第218行

7. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC23_PumpEngine 第222行

8. **[警告]** FC直接写入HMI参数区 VD82(VD82)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC30_ValveA_Diag 第125行

9. **[警告]** FC直接写入HMI参数区 VD90(VD90)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC30_ValveA_Diag 第126行

10. **[警告]** FC直接写入HMI参数区 VD86(VD86)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC4_ModbusPolling 第119行

11. **[警告]** FC直接写入HMI参数区 VD94(VD94)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC4_ModbusPolling 第184行

12. **[警告]** FC直接写入HMI参数区 VD54(VD54)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第40行

13. **[警告]** FC直接写入HMI参数区 VD66(VD66)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第41行

14. **[警告]** FC直接写入HMI参数区 VD54(VD54)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第65行

15. **[警告]** FC直接写入HMI参数区 VD66(VD66)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: SBR25_ColdStart 第66行

### 提示(182个)

#### 对齐建议(85个)

1. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第38行

2. **[提示]** VD地址非4字节对齐: VD82(地址82)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第38行

3. **[提示]** VD地址非4字节对齐: VD358(地址358)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第40行

4. **[提示]** VD地址非4字节对齐: VD66(地址66)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第45行

5. **[提示]** VD地址非4字节对齐: VD70(地址70)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第87行

6. **[提示]** VD地址非4字节对齐: VD70(地址70)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第88行

7. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第104行

8. **[提示]** VD地址非4字节对齐: VD406(地址406)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第105行

9. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC15_State_S4_Transfer 第132行

10. **[提示]** VD地址非4字节对齐: VD366(地址366)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第27行

11. **[提示]** VD地址非4字节对齐: VD366(地址366)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第38行

12. **[提示]** VD地址非4字节对齐: VD414(地址414)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第41行

13. **[提示]** VD地址非4字节对齐: VD54(地址54)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第34行

14. **[提示]** VD地址非4字节对齐: VD366(地址366)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第84行

15. **[提示]** VD地址非4字节对齐: VD414(地址414)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第89行

16. **[提示]** VD地址非4字节对齐: VD406(地址406)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC18_State_S7_End 第44行

17. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第215行

18. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第216行

19. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第216行

20. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第217行

21. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第218行

22. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第221行

23. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第222行

24. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第225行

25. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第227行

26. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第420行

27. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第440行

28. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC23_PumpEngine 第442行

29. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第124行

30. **[提示]** VD地址非4字节对齐: VD82(地址82)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第125行

31. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第126行

32. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第132行

33. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第139行

34. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第42行

35. **[提示]** VD地址非4字节对齐: VD414(地址414)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第43行

36. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第43行

37. **[提示]** VD地址非4字节对齐: VD426(地址426)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第44行

38. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第44行

39. **[提示]** VD地址非4字节对齐: VD430(地址430)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第45行

40. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第45行

41. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第50行

42. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第109行

43. **[提示]** VD地址非4字节对齐: VD70(地址70)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第138行

44. **[提示]** VD地址非4字节对齐: VD430(地址430)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第140行

45. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第141行

46. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第170行

47. **[提示]** VD地址非4字节对齐: VD410(地址410)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC4_ModbusPolling 第119行

48. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC4_ModbusPolling 第119行

49. **[提示]** VD地址非4字节对齐: VD410(地址410)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC4_ModbusPolling 第184行

50. **[提示]** VD地址非4字节对齐: VD94(地址94)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC4_ModbusPolling 第184行

51. **[提示]** VD地址非4字节对齐: VD414(地址414)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: OB1_MAIN 第212行

52. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第21行

53. **[提示]** VD地址非4字节对齐: VD414(地址414)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第29行

54. **[提示]** VD地址非4字节对齐: VD426(地址426)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第30行

55. **[提示]** VD地址非4字节对齐: VD430(地址430)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第31行

56. **[提示]** VD地址非4字节对齐: VD358(地址358)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第38行

57. **[提示]** VD地址非4字节对齐: VD362(地址362)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第39行

58. **[提示]** VD地址非4字节对齐: VD54(地址54)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第40行

59. **[提示]** VD地址非4字节对齐: VD66(地址66)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第41行

60. **[提示]** VD地址非4字节对齐: VD54(地址54)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第65行

61. **[提示]** VD地址非4字节对齐: VD66(地址66)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第66行

62. **[提示]** VD地址非4字节对齐: VD350(地址350)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第72行

63. **[提示]** VD地址非4字节对齐: VD358(地址358)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第73行

64. **[提示]** VD地址非4字节对齐: VD362(地址362)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第74行

65. **[提示]** VD地址非4字节对齐: VD414(地址414)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第78行

66. **[提示]** VD地址非4字节对齐: VD426(地址426)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第79行

67. **[提示]** VD地址非4字节对齐: VD430(地址430)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第80行

68. **[提示]** VD地址非4字节对齐: VD414(地址414)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第101行

69. **[提示]** VD地址非4字节对齐: VD406(地址406)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第168行

70. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第180行

71. **[提示]** VD地址非4字节对齐: VD374(地址374)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR25_ColdStart 第206行

72. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第111行

73. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第121行

74. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第126行

75. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第131行

76. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第135行

77. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第138行

78. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第143行

79. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第148行

80. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第152行

81. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第158行

82. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第158行

83. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第159行

84. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第159行

85. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: SBR26_WarmRecovery 第165行

#### 未使用变量(3个)

1. **[提示]** 变量 VW266(0进行中/1正常完成/2故障) 定义但未在STL中引用
   - 来源: FC11_State_S1_Inlet.stl

2. **[提示]** 变量 VD312(已删除(原阀A内漏差值,2026-09-14废弃)) 定义但未在STL中引用
   - 来源: FC30_ValveA_Diag.stl

3. **[提示]** 变量 VW268(Diag_Result_B) 定义但未在STL中引用
   - 来源: FC31_ValveB_Diag.stl

#### 未定义变量(94个)

1. **[提示]** 变量 VW600 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 31
   - 位置: FC0_SysInit 第31行

2. **[提示]** 变量 VW378 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 32
   - 位置: FC0_SysInit 第32行

3. **[提示]** 变量 VW390 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 35
   - 位置: FC0_SysInit 第35行

4. **[提示]** 变量 VD86 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 38
   - 位置: FC11_State_S1_Inlet 第38行

5. **[提示]** 变量 VD82 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 38
   - 位置: FC11_State_S1_Inlet 第38行

6. **[提示]** 变量 VD358 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 40
   - 位置: FC11_State_S1_Inlet 第40行

7. **[提示]** 变量 VD66 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 45
   - 位置: FC11_State_S1_Inlet 第45行

8. **[提示]** 变量 VD320 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 45
   - 位置: FC11_State_S1_Inlet 第45行

9. **[提示]** 变量 VB266 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 51
   - 位置: FC11_State_S1_Inlet 第51行

10. **[提示]** 变量 VB267 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 52
   - 位置: FC11_State_S1_Inlet 第52行

11. **[提示]** 变量 VW236 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 85
   - 位置: FC11_State_S1_Inlet 第85行

12. **[提示]** 变量 VD444 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 86
   - 位置: FC11_State_S1_Inlet 第86行

13. **[提示]** 变量 VD90 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 104
   - 位置: FC11_State_S1_Inlet 第104行

14. **[提示]** 变量 VD406 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 105
   - 位置: FC11_State_S1_Inlet 第105行

15. **[提示]** 变量 VW288 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 40
   - 位置: FC15_State_S4_Transfer 第40行

16. **[提示]** 变量 VD448 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 66
   - 位置: FC15_State_S4_Transfer 第66行

17. **[提示]** 变量 VD324 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 66
   - 位置: FC15_State_S4_Transfer 第66行

18. **[提示]** 变量 VW286 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 69
   - 位置: FC15_State_S4_Transfer 第69行

19. **[提示]** 变量 VB268 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 102
   - 位置: FC15_State_S4_Transfer 第102行

20. **[提示]** 变量 VB900 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 121
   - 位置: FC15_State_S4_Transfer 第121行

21. **[提示]** 变量 VB10 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 122
   - 位置: FC15_State_S4_Transfer 第122行

22. **[提示]** 变量 VB901 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 123
   - 位置: FC15_State_S4_Transfer 第123行

23. **[提示]** 变量 VB11 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 123
   - 位置: FC15_State_S4_Transfer 第123行

24. **[提示]** 变量 VB902 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 124
   - 位置: FC15_State_S4_Transfer 第124行

25. **[提示]** 变量 VB12 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 124
   - 位置: FC15_State_S4_Transfer 第124行

26. **[提示]** 变量 VB903 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 125
   - 位置: FC15_State_S4_Transfer 第125行

27. **[提示]** 变量 VB13 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 125
   - 位置: FC15_State_S4_Transfer 第125行

28. **[提示]** 变量 VB904 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 126
   - 位置: FC15_State_S4_Transfer 第126行

29. **[提示]** 变量 VB14 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 126
   - 位置: FC15_State_S4_Transfer 第126行

30. **[提示]** 变量 VB905 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 127
   - 位置: FC15_State_S4_Transfer 第127行

31. **[提示]** 变量 VB15 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 127
   - 位置: FC15_State_S4_Transfer 第127行

32. **[提示]** 变量 VB906 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 128
   - 位置: FC15_State_S4_Transfer 第128行

33. **[提示]** 变量 VB16 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 128
   - 位置: FC15_State_S4_Transfer 第128行

34. **[提示]** 变量 VB908 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 129
   - 位置: FC15_State_S4_Transfer 第129行

35. **[提示]** 变量 VB17 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 129
   - 位置: FC15_State_S4_Transfer 第129行

36. **[提示]** 变量 VD178 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 132
   - 位置: FC15_State_S4_Transfer 第132行

37. **[提示]** 变量 VD366 在STL中引用但变量表/注释未定义
   - FC: FC16_State_S5_Run, 行: 27
   - 位置: FC16_State_S5_Run 第27行

38. **[提示]** 变量 VD24 在STL中引用但变量表/注释未定义
   - FC: FC16_State_S5_Run, 行: 38
   - 位置: FC16_State_S5_Run 第38行

39. **[提示]** 变量 VB264 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 27
   - 位置: FC17_State_S6_Drain 第27行

40. **[提示]** 变量 VB265 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 29
   - 位置: FC17_State_S6_Drain 第29行

41. **[提示]** 变量 VD54 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 34
   - 位置: FC17_State_S6_Drain 第34行

42. **[提示]** 变量 VD328 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 34
   - 位置: FC17_State_S6_Drain 第34行

43. **[提示]** 变量 VD472 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 42
   - 位置: FC17_State_S6_Drain 第42行

44. **[提示]** 变量 VB270 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 56
   - 位置: FC17_State_S6_Drain 第56行

45. **[提示]** 变量 VD336 在STL中引用但变量表/注释未定义
   - FC: FC1A_State_S2_MixDose, 行: 39
   - 位置: FC1A_State_S2_MixDose 第39行

46. **[提示]** 变量 VD392 在STL中引用但变量表/注释未定义
   - FC: FC21_ManualSyringePump, 行: 32
   - 位置: FC21_ManualSyringePump 第32行

47. **[提示]** 变量 VD396 在STL中引用但变量表/注释未定义
   - FC: FC21_ManualSyringePump, 行: 33
   - 位置: FC21_ManualSyringePump 第33行

48. **[提示]** 变量 VD232 在STL中引用但变量表/注释未定义
   - FC: FC23_PumpEngine, 行: 143
   - 位置: FC23_PumpEngine 第143行

49. **[提示]** 变量 VW204 在STL中引用但变量表/注释未定义
   - FC: FC23_PumpEngine, 行: 229
   - 位置: FC23_PumpEngine 第229行

50. **[提示]** 变量 VW388 在STL中引用但变量表/注释未定义
   - FC: FC23_PumpEngine, 行: 469
   - 位置: FC23_PumpEngine 第469行

51. **[提示]** 变量 VW274 在STL中引用但变量表/注释未定义
   - FC: FC31_ValveB_Diag, 行: 49
   - 位置: FC31_ValveB_Diag 第49行

52. **[提示]** 变量 VB378 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 9
   - 位置: FC4_ModbusPolling 第9行

53. **[提示]** 变量 VW290 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 20
   - 位置: FC4_ModbusPolling 第20行

54. **[提示]** 变量 VB410 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 26
   - 位置: FC4_ModbusPolling 第26行

55. **[提示]** 变量 VB379 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 26
   - 位置: FC4_ModbusPolling 第26行

56. **[提示]** 变量 VB380 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 35
   - 位置: FC4_ModbusPolling 第35行

57. **[提示]** 变量 VB381 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 44
   - 位置: FC4_ModbusPolling 第44行

58. **[提示]** 变量 VB382 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 53
   - 位置: FC4_ModbusPolling 第53行

59. **[提示]** 变量 VW410 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 63
   - 位置: FC4_ModbusPolling 第63行

60. **[提示]** 变量 VW224 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 63
   - 位置: FC4_ModbusPolling 第63行

61. **[提示]** 变量 VW292 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 65
   - 位置: FC4_ModbusPolling 第65行

62. **[提示]** 变量 VD410 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 119
   - 位置: FC4_ModbusPolling 第119行

63. **[提示]** 变量 VW294 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 121
   - 位置: FC4_ModbusPolling 第121行

64. **[提示]** 变量 VW222 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 155
   - 位置: FC4_ModbusPolling 第155行

65. **[提示]** 变量 VW296 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 157
   - 位置: FC4_ModbusPolling 第157行

66. **[提示]** 变量 VD94 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 184
   - 位置: FC4_ModbusPolling 第184行

67. **[提示]** 变量 VW298 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 186
   - 位置: FC4_ModbusPolling 第186行

68. **[提示]** 变量 VB383 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 232
   - 位置: FC4_ModbusPolling 第232行

69. **[提示]** 变量 VB305 在STL中引用但变量表/注释未定义
   - FC: OB1_MAIN, 行: 194
   - 位置: OB1_MAIN 第194行

70. **[提示]** 变量 VD362 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 39
   - 位置: SBR25_ColdStart 第39行

71. **[提示]** 变量 VB456 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 52
   - 位置: SBR25_ColdStart 第52行

72. **[提示]** 变量 VD460 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 63
   - 位置: SBR25_ColdStart 第63行

73. **[提示]** 变量 VD464 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 64
   - 位置: SBR25_ColdStart 第64行

74. **[提示]** 变量 VD484 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 65
   - 位置: SBR25_ColdStart 第65行

75. **[提示]** 变量 VD488 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 66
   - 位置: SBR25_ColdStart 第66行

76. **[提示]** 变量 VD492 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 69
   - 位置: SBR25_ColdStart 第69行

77. **[提示]** 变量 VD500 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 71
   - 位置: SBR25_ColdStart 第71行

78. **[提示]** 变量 VD504 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 72
   - 位置: SBR25_ColdStart 第72行

79. **[提示]** 变量 VD512 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 73
   - 位置: SBR25_ColdStart 第73行

80. **[提示]** 变量 VD516 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 74
   - 位置: SBR25_ColdStart 第74行

81. **[提示]** 变量 VD520 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 75
   - 位置: SBR25_ColdStart 第75行

82. **[提示]** 变量 VD524 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 76
   - 位置: SBR25_ColdStart 第76行

83. **[提示]** 变量 VD528 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 77
   - 位置: SBR25_ColdStart 第77行

84. **[提示]** 变量 VD468 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 78
   - 位置: SBR25_ColdStart 第78行

85. **[提示]** 变量 VD476 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 79
   - 位置: SBR25_ColdStart 第79行

86. **[提示]** 变量 VD480 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 80
   - 位置: SBR25_ColdStart 第80行

87. **[提示]** 变量 VB532 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 83
   - 位置: SBR25_ColdStart 第83行

88. **[提示]** 变量 VB388 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 83
   - 位置: SBR25_ColdStart 第83行

89. **[提示]** 变量 VB389 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 84
   - 位置: SBR25_ColdStart 第84行

90. **[提示]** 变量 VB536 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 87
   - 位置: SBR25_ColdStart 第87行

91. **[提示]** 变量 VW300 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 156
   - 位置: SBR25_ColdStart 第156行

92. **[提示]** 变量 VB0 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 164
   - 位置: SBR25_ColdStart 第164行

93. **[提示]** 变量 VD374 在STL中引用但变量表/注释未定义
   - FC: SBR25_ColdStart, 行: 206
   - 位置: SBR25_ColdStart 第206行

94. **[提示]** 变量 VD190 在STL中引用但变量表/注释未定义
   - FC: SBR26_WarmRecovery, 行: 138
   - 位置: SBR26_WarmRecovery 第138行

## 五、跨FC变量访问矩阵(写入)

以下变量被多个FC写入(需确认调用顺序与互斥性):

| 变量 | 写入FC数 | FC列表 |
|---|---|---|
| VW2 | 17 | FC10_State_S0_Init, FC13A_PumpErrExit, FC15_State_S4_Transfer, FC16_State_S5_Run, FC17_State_S6_Drain, FC18_State_S7_End, FC19_State_Error, FC1_StateDispatcher, FC22_RTC_Sync, FC2_EStopHandling, FC30_ValveA_Diag, FC31_ValveB_Diag, FC32_ValveC_Diag, FC40_RhythmCorrection, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VW6 | 3 | FC19_State_Error, FC3_AlarmHandling, SBR25_ColdStart |
| VW8 | 2 | OB1_MAIN, SBR25_ColdStart |
| V0.0 | 2 | FC10_State_S0_Init, FC19_State_Error |
| V1.0 | 4 | FC10_State_S0_Init, FC18_State_S7_End, SBR25_ColdStart, SBR26_WarmRecovery |
| V1.6 | 3 | FC11_State_S1_Inlet, FC19_State_Error, SBR25_ColdStart |
| V1.7 | 4 | FC15_State_S4_Transfer, FC17_State_S6_Drain, FC19_State_Error, SBR25_ColdStart |
| VD24 | 2 | OB1_MAIN, SBR25_ColdStart |
| VD28 | 2 | FC40_RhythmCorrection, SBR25_ColdStart |
| VD82 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| V62.5 | 2 | FC21_ManualSyringePump, FC23_PumpEngine |
| VB266 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| VD116 | 3 | FC15_State_S4_Transfer, FC17_State_S6_Drain, FC40_RhythmCorrection |
| VD178 | 3 | FC15_State_S4_Transfer, SBR25_ColdStart, SBR26_WarmRecovery |
| VD186 | 2 | FC40_RhythmCorrection, SBR26_WarmRecovery |
| VD232 | 3 | FC23_PumpEngine, SBR25_ColdStart, SBR26_WarmRecovery |
| VD244 | 5 | FC19_State_Error, FC40_RhythmCorrection, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VD248 | 7 | FC11_State_S1_Inlet, FC19_State_Error, FC3_AlarmHandling, FC40_RhythmCorrection, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VD252 | 7 | FC11_State_S1_Inlet, FC19_State_Error, FC3_AlarmHandling, FC40_RhythmCorrection, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VD256 | 5 | FC19_State_Error, FC40_RhythmCorrection, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VD350 | 2 | FC23_PumpEngine, SBR25_ColdStart |
| VD372 | 5 | FC18_State_S7_End, FC1A_State_S2_MixDose, FC21_ManualSyringePump, FC23_PumpEngine, SBR25_ColdStart |
| VD392 | 2 | FC21_ManualSyringePump, SBR25_ColdStart |
| VD396 | 2 | FC21_ManualSyringePump, SBR25_ColdStart |
| VD406 | 3 | FC11_State_S1_Inlet, FC18_State_S7_End, SBR25_ColdStart |
| VD414 | 2 | FC40_RhythmCorrection, SBR25_ColdStart |
| VD426 | 2 | FC40_RhythmCorrection, SBR25_ColdStart |
| VD430 | 2 | FC40_RhythmCorrection, SBR25_ColdStart |
| VD440 | 5 | FC18_State_S7_End, FC1A_State_S2_MixDose, FC21_ManualSyringePump, FC23_PumpEngine, SBR25_ColdStart |
| VD444 | 4 | FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC17_State_S6_Drain, SBR25_ColdStart |
| VD472 | 2 | SBR25_ColdStart, SBR26_WarmRecovery |
| VW198 | 3 | FC0_SysInit, SBR25_ColdStart, SBR26_WarmRecovery |
| VW226 | 6 | FC13A_PumpErrExit, FC1A_State_S2_MixDose, FC21_ManualSyringePump, FC23_PumpEngine, OB1_MAIN, SBR25_ColdStart |
| VW230 | 3 | FC23_PumpEngine, SBR25_ColdStart, SBR26_WarmRecovery |
| VW260 | 6 | FC11_State_S1_Inlet, FC19_State_Error, FC30_ValveA_Diag, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VW270 | 2 | FC17_State_S6_Drain, FC32_ValveC_Diag |
| VW290 | 2 | FC4_ModbusPolling, SBR25_ColdStart |
| VW378 | 2 | FC0_SysInit, SBR25_ColdStart |
| VW390 | 4 | FC0_SysInit, FC21_ManualSyringePump, OB1_MAIN, SBR25_ColdStart |
| VW400 | 4 | FC19_State_Error, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| VW418 | 8 | FC10_State_S0_Init, FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC19_State_Error, FC1A_State_S2_MixDose, OB1_MAIN, SBR25_ColdStart, SBR26_WarmRecovery |
| V300.0 | 3 | FC19_State_Error, FC30_ValveA_Diag, FC3_AlarmHandling |
| V300.1 | 3 | FC31_ValveB_Diag, FC32_ValveC_Diag, FC3_AlarmHandling |
| V300.4 | 4 | FC19_State_Error, FC2_EStopHandling, SBR25_ColdStart, SBR26_WarmRecovery |
| V300.5 | 2 | FC19_State_Error, FC2_EStopHandling |
| V301.0 | 3 | FC19_State_Error, FC30_ValveA_Diag, FC3A_AlarmReset_Common |
| V301.2 | 2 | FC30_ValveA_Diag, FC3A_AlarmReset_Common |
| V301.3 | 2 | FC30_ValveA_Diag, FC3A_AlarmReset_Common |
| V301.4 | 2 | FC30_ValveA_Diag, FC3A_AlarmReset_Common |
| V301.5 | 2 | FC30_ValveA_Diag, FC3A_AlarmReset_Common |
| V302.0 | 3 | FC19_State_Error, FC31_ValveB_Diag, FC3A_AlarmReset_Common |
| V302.1 | 2 | FC31_ValveB_Diag, FC3A_AlarmReset_Common |
| V302.2 | 2 | FC31_ValveB_Diag, FC3A_AlarmReset_Common |
| V302.3 | 2 | FC31_ValveB_Diag, FC3A_AlarmReset_Common |
| V302.4 | 2 | FC31_ValveB_Diag, FC3A_AlarmReset_Common |
| V302.6 | 2 | FC32_ValveC_Diag, FC3A_AlarmReset_Common |
| V303.0 | 3 | FC19_State_Error, FC32_ValveC_Diag, FC3A_AlarmReset_Common |
| V303.4 | 4 | FC13A_PumpErrExit, FC1A_State_S2_MixDose, FC3A_AlarmReset_Common, FC4_ModbusPolling |
| V303.6 | 2 | FC3_AlarmHandling, FC40_RhythmCorrection |
| V303.7 | 3 | FC22_RTC_Sync, SBR25_ColdStart, SBR26_WarmRecovery |
| V307.2 | 2 | FC21_ManualSyringePump, SBR26_WarmRecovery |

## 六、V区使用热力图(引用次数Top20)

| 字节地址 | 引用次数 |
|---|---|
| VB61 | 117 |
| VB226 | 84 |
| VB227 | 84 |
| VB2 | 69 |
| VB3 | 69 |
| VB6 | 66 |
| VB7 | 66 |
| VB62 | 49 |
| VB60 | 45 |
| VB303 | 40 |
| VB300 | 34 |
| VB301 | 29 |
| VB302 | 27 |
| VB1 | 26 |
| VB418 | 23 |
| VB419 | 23 |
| VB63 | 23 |
| VB260 | 20 |
| VB261 | 20 |
| VB4 | 19 |

## 七、结论与建议

❌ 发现 1 个严重问题,必须立即修复后方可交付。
ℹ️ 另有 182 个提示项,可择机处理。

---

*本报告由 stl_static_analyzer.py 自动生成,可重复执行以跟踪问题修复进度。*