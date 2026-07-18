# PLC代码静态分析报告

| 项目 | 内容 |
|---|---|
| 分析对象 | S7-200 SMART STL代码(20个FC) |
| 分析工具 | stl_static_analyzer.py v1.0 |
| 变量表来源 | HMI-PLC变量地址表v1.0 + STL注释 |
| 分析日期 | 2026-07-18 |

## 一、分析摘要

- **问题总数**: 225 个
- **严重**: 3 个
- **警告**: 59 个
- **提示**: 163 个

## 二、STL文件统计

| FC名称 | 引用数 | 写入数 |
|---|---|---|
| FC0_SysInit | 98 | 42 |
| FC10_State_S0_Init | 7 | 4 |
| FC11_State_S1_Inlet | 44 | 34 |
| FC12_State_S2_PreMix | 27 | 18 |
| FC13_State_S3_Dosing | 16 | 13 |
| FC14_State_S35_Rest | 8 | 5 |
| FC15_State_S4_Transfer | 33 | 21 |
| FC16_State_S5_Run | 36 | 22 |
| FC17_State_S6_Drain | 17 | 13 |
| FC18_State_S7_End | 4 | 3 |
| FC19_State_Error | 11 | 9 |
| FC1_StateDispatcher | 13 | 2 |
| FC2_EStopHandling | 13 | 8 |
| FC30_ValveA_Diag | 52 | 32 |
| FC31_ValveB_Diag | 46 | 38 |
| FC32_ValveC_Diag | 41 | 33 |
| FC3_AlarmHandling | 182 | 83 |
| FC40_RhythmCorrection | 63 | 40 |
| FC4_ModbusPolling | 2 | 0 |
| OB1_MAIN | 0 | 0 |
| **合计** | **713** | **420** |

## 三、变量定义统计

- VB(字节): 0 个
- VW(字): 19 个
- VD(双字): 22 个
- Vbit(位): 17 个
- **合计**: 58 个变量定义

## 四、问题清单

### 严重(3个)

#### VD编址冲突(3个)

1. **[严重]** VD18(VB18~VB21) 与 VD20(VB20~VB23) 地址重叠
   - VD18引用: ['FC13_State_S3_Dosing:L19(VD18)']
   - VD20引用: ['FC16_State_S5_Run:L83(VD20)', 'FC11_State_S1_Inlet:L75(VD20)', 'FC16_State_S5_Run:L36(VD20)']
   - 重叠字节: VB20~VB21

2. **[严重]** VD48(VB48~VB51) 与 VD50(VB50~VB53) 地址重叠
   - VD48引用: ['FC11_State_S1_Inlet:L41(VD48)']
   - VD50引用: ['FC15_State_S4_Transfer:L34(VD50)']
   - 重叠字节: VB50~VB51

3. **[严重]** VD96(VB96~VB99) 与 VD98(VB98~VB101) 地址重叠
   - VD96引用: ['FC16_State_S5_Run:L76(VD96)', 'FC16_State_S5_Run:L97(VD96)']
   - VD98引用: ['FC13_State_S3_Dosing:L17(VD98)']
   - 重叠字节: VB98~VB99

### 警告(59个)

#### 跨FC写入冲突(48个)

1. **[警告]** 变量 VB2 被 17 个FC写入: ['FC0_SysInit', 'FC10_State_S0_Init', 'FC11_State_S1_Inlet', 'FC12_State_S2_PreMix', 'FC13_State_S3_Dosing', 'FC14_State_S35_Rest', 'FC15_State_S4_Transfer', 'FC16_State_S5_Run', 'FC17_State_S6_Drain', 'FC18_State_S7_End', 'FC19_State_Error', 'FC1_StateDispatcher', 'FC2_EStopHandling', 'FC30_ValveA_Diag', 'FC31_ValveB_Diag', 'FC32_ValveC_Diag', 'FC40_RhythmCorrection']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

2. **[警告]** 变量 VB3 被 16 个FC写入: ['FC0_SysInit', 'FC10_State_S0_Init', 'FC11_State_S1_Inlet', 'FC12_State_S2_PreMix', 'FC13_State_S3_Dosing', 'FC14_State_S35_Rest', 'FC15_State_S4_Transfer', 'FC16_State_S5_Run', 'FC17_State_S6_Drain', 'FC18_State_S7_End', 'FC19_State_Error', 'FC1_StateDispatcher', 'FC2_EStopHandling', 'FC30_ValveA_Diag', 'FC31_ValveB_Diag', 'FC32_ValveC_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

3. **[警告]** 变量 V1.6 被 5 个FC写入: ['FC0_SysInit', 'FC11_State_S1_Inlet', 'FC12_State_S2_PreMix', 'FC15_State_S4_Transfer', 'FC19_State_Error']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

4. **[警告]** 变量 V1.7 被 4 个FC写入: ['FC0_SysInit', 'FC15_State_S4_Transfer', 'FC17_State_S6_Drain', 'FC19_State_Error']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

5. **[警告]** 变量 V300.4 被 3 个FC写入: ['FC0_SysInit', 'FC19_State_Error', 'FC2_EStopHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

6. **[警告]** 变量 VB6 被 3 个FC写入: ['FC0_SysInit', 'FC19_State_Error', 'FC2_EStopHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

7. **[警告]** 变量 VB7 被 3 个FC写入: ['FC0_SysInit', 'FC19_State_Error', 'FC2_EStopHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

8. **[警告]** 变量 V1.0 被 3 个FC写入: ['FC0_SysInit', 'FC10_State_S0_Init', 'FC18_State_S7_End']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

9. **[警告]** 变量 VD178 被 4 个FC写入: ['FC0_SysInit', 'FC11_State_S1_Inlet', 'FC15_State_S4_Transfer', 'FC16_State_S5_Run']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

10. **[警告]** 变量 V303.5 被 2 个FC写入: ['FC0_SysInit', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

11. **[警告]** 变量 VB260 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

12. **[警告]** 变量 VB261 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

13. **[警告]** 变量 VB266 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

14. **[警告]** 变量 VD150 被 3 个FC写入: ['FC11_State_S1_Inlet', 'FC16_State_S5_Run', 'FC40_RhythmCorrection']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

15. **[警告]** 变量 VD116 被 3 个FC写入: ['FC11_State_S1_Inlet', 'FC16_State_S5_Run', 'FC17_State_S6_Drain']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

16. **[警告]** 变量 VD154 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC16_State_S5_Run']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

17. **[警告]** 变量 VD124 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC40_RhythmCorrection']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

18. **[警告]** 变量 VW182 被 2 个FC写入: ['FC11_State_S1_Inlet', 'FC16_State_S5_Run']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

19. **[警告]** 变量 V303.2 被 2 个FC写入: ['FC12_State_S2_PreMix', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

20. **[警告]** 变量 V303.3 被 2 个FC写入: ['FC12_State_S2_PreMix', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

21. **[警告]** 变量 VD90 被 2 个FC写入: ['FC13_State_S3_Dosing', 'FC30_ValveA_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

22. **[警告]** 变量 V303.4 被 2 个FC写入: ['FC13_State_S3_Dosing', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

23. **[警告]** 变量 VB262 被 2 个FC写入: ['FC15_State_S4_Transfer', 'FC31_ValveB_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

24. **[警告]** 变量 VB263 被 2 个FC写入: ['FC15_State_S4_Transfer', 'FC31_ValveB_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

25. **[警告]** 变量 VB268 被 2 个FC写入: ['FC15_State_S4_Transfer', 'FC31_ValveB_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

26. **[警告]** 变量 V301.6 被 2 个FC写入: ['FC16_State_S5_Run', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

27. **[警告]** 变量 VB264 被 2 个FC写入: ['FC17_State_S6_Drain', 'FC32_ValveC_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

28. **[警告]** 变量 VB265 被 2 个FC写入: ['FC17_State_S6_Drain', 'FC32_ValveC_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

29. **[警告]** 变量 VW270 被 2 个FC写入: ['FC17_State_S6_Drain', 'FC32_ValveC_Diag']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

30. **[警告]** 变量 V300.5 被 2 个FC写入: ['FC19_State_Error', 'FC2_EStopHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

31. **[警告]** 变量 V300.0 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

32. **[警告]** 变量 V301.4 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

33. **[警告]** 变量 V301.5 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

34. **[警告]** 变量 V301.0 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

35. **[警告]** 变量 V301.1 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

36. **[警告]** 变量 V301.2 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

37. **[警告]** 变量 V301.3 被 2 个FC写入: ['FC30_ValveA_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

38. **[警告]** 变量 V300.1 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

39. **[警告]** 变量 V302.1 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

40. **[警告]** 变量 V302.2 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

41. **[警告]** 变量 V302.0 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

42. **[警告]** 变量 V302.4 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

43. **[警告]** 变量 V302.3 被 2 个FC写入: ['FC31_ValveB_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

44. **[警告]** 变量 V302.6 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

45. **[警告]** 变量 V302.7 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

46. **[警告]** 变量 V302.5 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

47. **[警告]** 变量 V303.1 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

48. **[警告]** 变量 V303.0 被 2 个FC写入: ['FC32_ValveC_Diag', 'FC3_AlarmHandling']
   - 同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性

#### 参数区写入(11个)

1. **[警告]** FC直接写入HMI参数区 VD82(VD82)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC11_State_S1_Inlet 第25行

2. **[警告]** FC直接写入HMI参数区 VD70(VD70)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC11_State_S1_Inlet 第71行

3. **[警告]** FC直接写入HMI参数区 VD10(VD10)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC13_State_S3_Dosing 第14行

4. **[警告]** FC直接写入HMI参数区 VD90(VD90)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC13_State_S3_Dosing 第14行

5. **[警告]** FC直接写入HMI参数区 VD14(VD14)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC13_State_S3_Dosing 第16行

6. **[警告]** FC直接写入HMI参数区 VD98(VD98)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC13_State_S3_Dosing 第17行

7. **[警告]** FC直接写入HMI参数区 VD18(VD18)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC13_State_S3_Dosing 第19行

8. **[警告]** FC直接写入HMI参数区 VD102(VD102)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC13_State_S3_Dosing 第21行

9. **[警告]** FC直接写入HMI参数区 VD74(VD74)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC15_State_S4_Transfer 第54行

10. **[警告]** FC直接写入HMI参数区 VD78(VD78)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC17_State_S6_Drain 第50行

11. **[警告]** FC直接写入HMI参数区 VD90(VD90)
   - VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定
   - 位置: FC30_ValveA_Diag 第114行

### 提示(163个)

#### 对齐建议(87个)

1. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第57行

2. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第125行

3. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第139行

4. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第145行

5. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第151行

6. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第156行

7. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第161行

8. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第167行

9. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第173行

10. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第178行

11. **[提示]** VD地址非4字节对齐: VD186(地址186)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第188行

12. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第188行

13. **[提示]** VD地址非4字节对齐: VD190(地址190)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第189行

14. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第189行

15. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC0_SysInit 第195行

16. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第25行

17. **[提示]** VD地址非4字节对齐: VD82(地址82)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第25行

18. **[提示]** VD地址非4字节对齐: VD66(地址66)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第46行

19. **[提示]** VD地址非4字节对齐: VD70(地址70)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第71行

20. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第75行

21. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第76行

22. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第77行

23. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第78行

24. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第78行

25. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第80行

26. **[提示]** VD地址非4字节对齐: VD174(地址174)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第81行

27. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第81行

28. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第82行

29. **[提示]** VD地址非4字节对齐: VD70(地址70)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第87行

30. **[提示]** VD地址非4字节对齐: VD174(地址174)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC11_State_S1_Inlet 第89行

31. **[提示]** VD地址非4字节对齐: VD58(地址58)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC12_State_S2_PreMix 第34行

32. **[提示]** VD地址非4字节对齐: VD62(地址62)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC12_State_S2_PreMix 第47行

33. **[提示]** VD地址非4字节对齐: VD10(地址10)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第14行

34. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第14行

35. **[提示]** VD地址非4字节对齐: VD14(地址14)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第16行

36. **[提示]** VD地址非4字节对齐: VD98(地址98)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第17行

37. **[提示]** VD地址非4字节对齐: VD18(地址18)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第19行

38. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第21行

39. **[提示]** VD地址非4字节对齐: VD102(地址102)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC13_State_S3_Dosing 第32行

40. **[提示]** VD地址非4字节对齐: VD50(地址50)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC15_State_S4_Transfer 第34行

41. **[提示]** VD地址非4字节对齐: VD74(地址74)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC15_State_S4_Transfer 第54行

42. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC15_State_S4_Transfer 第70行

43. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第28行

44. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第36行

45. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第37行

46. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第38行

47. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第39行

48. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第39行

49. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第44行

50. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第49行

51. **[提示]** VD地址非4字节对齐: VD178(地址178)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC16_State_S5_Run 第85行

52. **[提示]** VD地址非4字节对齐: VD54(地址54)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第30行

53. **[提示]** VD地址非4字节对齐: VD78(地址78)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第50行

54. **[提示]** VD地址非4字节对齐: VD78(地址78)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC17_State_S6_Drain 第52行

55. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第112行

56. **[提示]** VD地址非4字节对齐: VD82(地址82)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第113行

57. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第114行

58. **[提示]** VD地址非4字节对齐: VD90(地址90)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第119行

59. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第122行

60. **[提示]** VD地址非4字节对齐: VD86(地址86)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC30_ValveA_Diag 第140行

61. **[提示]** VD地址非4字节对齐: VD162(地址162)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第30行

62. **[提示]** VD地址非4字节对齐: VD162(地址162)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第31行

63. **[提示]** VD地址非4字节对齐: VD166(地址166)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第33行

64. **[提示]** VD地址非4字节对齐: VD166(地址166)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第34行

65. **[提示]** VD地址非4字节对齐: VD170(地址170)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第36行

66. **[提示]** VD地址非4字节对齐: VD170(地址170)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第37行

67. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第42行

68. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第42行

69. **[提示]** VD地址非4字节对齐: VD154(地址154)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第50行

70. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第50行

71. **[提示]** VD地址非4字节对齐: VD150(地址150)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第51行

72. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第51行

73. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第54行

74. **[提示]** VD地址非4字节对齐: VD162(地址162)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第54行

75. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第59行

76. **[提示]** VD地址非4字节对齐: VD162(地址162)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第60行

77. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第61行

78. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第67行

79. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第77行

80. **[提示]** VD地址非4字节对齐: VD166(地址166)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第77行

81. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第82行

82. **[提示]** VD地址非4字节对齐: VD166(地址166)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第83行

83. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第84行

84. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第90行

85. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第99行

86. **[提示]** VD地址非4字节对齐: VD170(地址170)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第99行

87. **[提示]** VD地址非4字节对齐: VD158(地址158)
   - VD建议从4倍数字节地址起始(非强制)
   - 位置: FC40_RhythmCorrection 第111行

#### 未使用变量(3个)

1. **[提示]** 变量 VD194(VD_RTC_DT_Diff) 定义但未在STL中引用
   - 来源: FC0_SysInit.stl

2. **[提示]** 变量 VD250(目标进水量(HMI设定)) 定义但未在STL中引用
   - 来源: FC11_State_S1_Inlet.stl

3. **[提示]** 变量 VW8(实验轮次计数) 定义但未在STL中引用
   - 来源: OB1_MAIN.stl

#### 未定义变量(73个)

1. **[提示]** 变量 VB2 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 37
   - 位置: FC0_SysInit 第37行

2. **[提示]** 变量 VB3 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 38
   - 位置: FC0_SysInit 第38行

3. **[提示]** 变量 VW300 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 48
   - 位置: FC0_SysInit 第48行

4. **[提示]** 变量 VB6 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 49
   - 位置: FC0_SysInit 第49行

5. **[提示]** 变量 VB7 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 50
   - 位置: FC0_SysInit 第50行

6. **[提示]** 变量 VB8 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 54
   - 位置: FC0_SysInit 第54行

7. **[提示]** 变量 VB9 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 55
   - 位置: FC0_SysInit 第55行

8. **[提示]** 变量 VB900 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 68
   - 位置: FC0_SysInit 第68行

9. **[提示]** 变量 VB10 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 73
   - 位置: FC0_SysInit 第73行

10. **[提示]** 变量 VB901 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 87
   - 位置: FC0_SysInit 第87行

11. **[提示]** 变量 VB11 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 88
   - 位置: FC0_SysInit 第88行

12. **[提示]** 变量 VB902 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 94
   - 位置: FC0_SysInit 第94行

13. **[提示]** 变量 VB12 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 95
   - 位置: FC0_SysInit 第95行

14. **[提示]** 变量 VB903 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 101
   - 位置: FC0_SysInit 第101行

15. **[提示]** 变量 VB13 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 102
   - 位置: FC0_SysInit 第102行

16. **[提示]** 变量 VB904 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 108
   - 位置: FC0_SysInit 第108行

17. **[提示]** 变量 VB14 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 109
   - 位置: FC0_SysInit 第109行

18. **[提示]** 变量 VB905 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 115
   - 位置: FC0_SysInit 第115行

19. **[提示]** 变量 VB15 在STL中引用但变量表/注释未定义
   - FC: FC0_SysInit, 行: 116
   - 位置: FC0_SysInit 第116行

20. **[提示]** 变量 VD86 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 25
   - 位置: FC11_State_S1_Inlet 第25行

21. **[提示]** 变量 VD82 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 25
   - 位置: FC11_State_S1_Inlet 第25行

22. **[提示]** 变量 VB260 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 34
   - 位置: FC11_State_S1_Inlet 第34行

23. **[提示]** 变量 VB261 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 35
   - 位置: FC11_State_S1_Inlet 第35行

24. **[提示]** 变量 VB266 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 37
   - 位置: FC11_State_S1_Inlet 第37行

25. **[提示]** 变量 VB267 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 38
   - 位置: FC11_State_S1_Inlet 第38行

26. **[提示]** 变量 VD48 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 41
   - 位置: FC11_State_S1_Inlet 第41行

27. **[提示]** 变量 VD66 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 46
   - 位置: FC11_State_S1_Inlet 第46行

28. **[提示]** 变量 VD320 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 46
   - 位置: FC11_State_S1_Inlet 第46行

29. **[提示]** 变量 VD70 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 71
   - 位置: FC11_State_S1_Inlet 第71行

30. **[提示]** 变量 VD20 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 75
   - 位置: FC11_State_S1_Inlet 第75行

31. **[提示]** 变量 VD116 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 77
   - 位置: FC11_State_S1_Inlet 第77行

32. **[提示]** 变量 VD174 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 81
   - 位置: FC11_State_S1_Inlet 第81行

33. **[提示]** 变量 VD28 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 88
   - 位置: FC11_State_S1_Inlet 第88行

34. **[提示]** 变量 VD36 在STL中引用但变量表/注释未定义
   - FC: FC11_State_S1_Inlet, 行: 90
   - 位置: FC11_State_S1_Inlet 第90行

35. **[提示]** 变量 VD58 在STL中引用但变量表/注释未定义
   - FC: FC12_State_S2_PreMix, 行: 34
   - 位置: FC12_State_S2_PreMix 第34行

36. **[提示]** 变量 VW282 在STL中引用但变量表/注释未定义
   - FC: FC12_State_S2_PreMix, 行: 37
   - 位置: FC12_State_S2_PreMix 第37行

37. **[提示]** 变量 VD62 在STL中引用但变量表/注释未定义
   - FC: FC12_State_S2_PreMix, 行: 47
   - 位置: FC12_State_S2_PreMix 第47行

38. **[提示]** 变量 VW284 在STL中引用但变量表/注释未定义
   - FC: FC12_State_S2_PreMix, 行: 50
   - 位置: FC12_State_S2_PreMix 第50行

39. **[提示]** 变量 VD10 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 14
   - 位置: FC13_State_S3_Dosing 第14行

40. **[提示]** 变量 VD90 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 14
   - 位置: FC13_State_S3_Dosing 第14行

41. **[提示]** 变量 VD14 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 16
   - 位置: FC13_State_S3_Dosing 第16行

42. **[提示]** 变量 VD98 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 17
   - 位置: FC13_State_S3_Dosing 第17行

43. **[提示]** 变量 VD18 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 19
   - 位置: FC13_State_S3_Dosing 第19行

44. **[提示]** 变量 VD102 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 21
   - 位置: FC13_State_S3_Dosing 第21行

45. **[提示]** 变量 VW204 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 33
   - 位置: FC13_State_S3_Dosing 第33行

46. **[提示]** 变量 VW206 在STL中引用但变量表/注释未定义
   - FC: FC13_State_S3_Dosing, 行: 34
   - 位置: FC13_State_S3_Dosing 第34行

47. **[提示]** 变量 VB262 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 28
   - 位置: FC15_State_S4_Transfer 第28行

48. **[提示]** 变量 VB263 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 29
   - 位置: FC15_State_S4_Transfer 第29行

49. **[提示]** 变量 VB268 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 31
   - 位置: FC15_State_S4_Transfer 第31行

50. **[提示]** 变量 VB269 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 32
   - 位置: FC15_State_S4_Transfer 第32行

51. **[提示]** 变量 VD50 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 34
   - 位置: FC15_State_S4_Transfer 第34行

52. **[提示]** 变量 VD324 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 34
   - 位置: FC15_State_S4_Transfer 第34行

53. **[提示]** 变量 VD74 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 54
   - 位置: FC15_State_S4_Transfer 第54行

54. **[提示]** 变量 VB906 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 66
   - 位置: FC15_State_S4_Transfer 第66行

55. **[提示]** 变量 VB16 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 66
   - 位置: FC15_State_S4_Transfer 第66行

56. **[提示]** 变量 VB908 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 67
   - 位置: FC15_State_S4_Transfer 第67行

57. **[提示]** 变量 VB17 在STL中引用但变量表/注释未定义
   - FC: FC15_State_S4_Transfer, 行: 67
   - 位置: FC15_State_S4_Transfer 第67行

58. **[提示]** 变量 VD96 在STL中引用但变量表/注释未定义
   - FC: FC16_State_S5_Run, 行: 76
   - 位置: FC16_State_S5_Run 第76行

59. **[提示]** 变量 VD24 在STL中引用但变量表/注释未定义
   - FC: FC16_State_S5_Run, 行: 97
   - 位置: FC16_State_S5_Run 第97行

60. **[提示]** 变量 VB264 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 25
   - 位置: FC17_State_S6_Drain 第25行

61. **[提示]** 变量 VB265 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 26
   - 位置: FC17_State_S6_Drain 第26行

62. **[提示]** 变量 VD54 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 30
   - 位置: FC17_State_S6_Drain 第30行

63. **[提示]** 变量 VD328 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 30
   - 位置: FC17_State_S6_Drain 第30行

64. **[提示]** 变量 VD78 在STL中引用但变量表/注释未定义
   - FC: FC17_State_S6_Drain, 行: 50
   - 位置: FC17_State_S6_Drain 第50行

65. **[提示]** 变量 VB500 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 407
   - 位置: FC3_AlarmHandling 第407行

66. **[提示]** 变量 VB509 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 408
   - 位置: FC3_AlarmHandling 第408行

67. **[提示]** 变量 VB510 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 409
   - 位置: FC3_AlarmHandling 第409行

68. **[提示]** 变量 VB508 在STL中引用但变量表/注释未定义
   - FC: FC3_AlarmHandling, 行: 410
   - 位置: FC3_AlarmHandling 第410行

69. **[提示]** 变量 VD40 在STL中引用但变量表/注释未定义
   - FC: FC40_RhythmCorrection, 行: 31
   - 位置: FC40_RhythmCorrection 第31行

70. **[提示]** 变量 VD32 在STL中引用但变量表/注释未定义
   - FC: FC40_RhythmCorrection, 行: 34
   - 位置: FC40_RhythmCorrection 第34行

71. **[提示]** 变量 VD44 在STL中引用但变量表/注释未定义
   - FC: FC40_RhythmCorrection, 行: 36
   - 位置: FC40_RhythmCorrection 第36行

72. **[提示]** 变量 VB184 在STL中引用但变量表/注释未定义
   - FC: FC40_RhythmCorrection, 行: 70
   - 位置: FC40_RhythmCorrection 第70行

73. **[提示]** 变量 VW250 在STL中引用但变量表/注释未定义
   - FC: FC4_ModbusPolling, 行: 27
   - 位置: FC4_ModbusPolling 第27行

## 五、跨FC变量访问矩阵(写入)

以下变量被多个FC写入(需确认调用顺序与互斥性):

| 变量 | 写入FC数 | FC列表 |
|---|---|---|
| VB2 | 17 | FC0_SysInit, FC10_State_S0_Init, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC13_State_S3_Dosing, FC14_State_S35_Rest, FC15_State_S4_Transfer, FC16_State_S5_Run, FC17_State_S6_Drain, FC18_State_S7_End, FC19_State_Error, FC1_StateDispatcher, FC2_EStopHandling, FC30_ValveA_Diag, FC31_ValveB_Diag, FC32_ValveC_Diag, FC40_RhythmCorrection |
| VB3 | 16 | FC0_SysInit, FC10_State_S0_Init, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC13_State_S3_Dosing, FC14_State_S35_Rest, FC15_State_S4_Transfer, FC16_State_S5_Run, FC17_State_S6_Drain, FC18_State_S7_End, FC19_State_Error, FC1_StateDispatcher, FC2_EStopHandling, FC30_ValveA_Diag, FC31_ValveB_Diag, FC32_ValveC_Diag |
| VB6 | 3 | FC0_SysInit, FC19_State_Error, FC2_EStopHandling |
| VB7 | 3 | FC0_SysInit, FC19_State_Error, FC2_EStopHandling |
| V1.0 | 3 | FC0_SysInit, FC10_State_S0_Init, FC18_State_S7_End |
| V1.6 | 5 | FC0_SysInit, FC11_State_S1_Inlet, FC12_State_S2_PreMix, FC15_State_S4_Transfer, FC19_State_Error |
| V1.7 | 4 | FC0_SysInit, FC15_State_S4_Transfer, FC17_State_S6_Drain, FC19_State_Error |
| VD90 | 2 | FC13_State_S3_Dosing, FC30_ValveA_Diag |
| VB260 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| VB261 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| VB262 | 2 | FC15_State_S4_Transfer, FC31_ValveB_Diag |
| VB263 | 2 | FC15_State_S4_Transfer, FC31_ValveB_Diag |
| VB264 | 2 | FC17_State_S6_Drain, FC32_ValveC_Diag |
| VB265 | 2 | FC17_State_S6_Drain, FC32_ValveC_Diag |
| VB266 | 2 | FC11_State_S1_Inlet, FC30_ValveA_Diag |
| VB268 | 2 | FC15_State_S4_Transfer, FC31_ValveB_Diag |
| VD116 | 3 | FC11_State_S1_Inlet, FC16_State_S5_Run, FC17_State_S6_Drain |
| VD124 | 2 | FC11_State_S1_Inlet, FC40_RhythmCorrection |
| VD150 | 3 | FC11_State_S1_Inlet, FC16_State_S5_Run, FC40_RhythmCorrection |
| VD154 | 2 | FC11_State_S1_Inlet, FC16_State_S5_Run |
| VD178 | 4 | FC0_SysInit, FC11_State_S1_Inlet, FC15_State_S4_Transfer, FC16_State_S5_Run |
| VW182 | 2 | FC11_State_S1_Inlet, FC16_State_S5_Run |
| VW270 | 2 | FC17_State_S6_Drain, FC32_ValveC_Diag |
| V300.0 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| V300.1 | 2 | FC31_ValveB_Diag, FC3_AlarmHandling |
| V300.4 | 3 | FC0_SysInit, FC19_State_Error, FC2_EStopHandling |
| V300.5 | 2 | FC19_State_Error, FC2_EStopHandling |
| V301.0 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
| V301.1 | 2 | FC30_ValveA_Diag, FC3_AlarmHandling |
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
| V303.2 | 2 | FC12_State_S2_PreMix, FC3_AlarmHandling |
| V303.3 | 2 | FC12_State_S2_PreMix, FC3_AlarmHandling |
| V303.4 | 2 | FC13_State_S3_Dosing, FC3_AlarmHandling |
| V303.5 | 2 | FC0_SysInit, FC3_AlarmHandling |

## 六、V区使用热力图(引用次数Top20)

| 字节地址 | 引用次数 |
|---|---|
| VB2 | 62 |
| VB3 | 60 |
| VB6 | 50 |
| VB7 | 50 |
| VB302 | 50 |
| VB301 | 47 |
| VB303 | 39 |
| VB300 | 32 |
| VB1 | 22 |
| VB0 | 13 |
| VB158 | 12 |
| VB159 | 12 |
| VB160 | 12 |
| VB161 | 12 |
| VB150 | 11 |
| VB151 | 11 |
| VB152 | 11 |
| VB153 | 11 |
| VB198 | 10 |
| VB199 | 10 |

## 七、结论与建议

❌ 发现 3 个严重问题,必须立即修复后方可交付。
ℹ️ 另有 163 个提示项,可择机处理。

---

*本报告由 stl_static_analyzer.py 自动生成,可重复执行以跟踪问题修复进度。*