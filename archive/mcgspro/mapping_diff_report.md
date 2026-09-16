# HMI-PLC 地址映射差异报告

## 1. 通道处理.csv中有但PLC代码中未使用的地址（建议删除或标记为保留）
共 39 个：

| 通道 | HMI变量名 | 通道地址 | PLC地址 |
|------|-----------|----------|---------|
| 20 | U1_Reserved_CMD_Pause | 读写V000.1 | V0.1 |
| 28 | U1_Reserved_STA_PauseAck | 只读V001.1 | V1.1 |
| 29 | U1_STA_StopAck | 只读V001.2 | V1.2 |
| 41 | U1_VD_PreMixTime_MinSafe | 读写VDF032 | VD32 |
| 42 | U1_VD_RestTime | 读写VDF036 | VD36 |
| 43 | U1_VD_RestTime_Min | 读写VDF040 | VD40 |
| 44 | U1_VD_CycleExtend_Max | 读写VDF044 | VD44 |
| 50 | U1_VD_S4_Actual | 只读VDF074 | VD74 |
| 51 | U1_VD_S6_Actual | 只读VDF078 | VD78 |
| 58 | U1_VD_T_Rolling | 读写VDF112 | VD112 |
| 60 | U1_VD_S2_Target | 读写VDF120 | VD120 |
| 61 | U1_VD_RestTime_Target | 读写VDF124 | VD124 |
| 62 | U1_VD_PumpSpeed_Start | 读写VDF132 | VD132 |
| 63 | U1_VD_PumpSpeed_Max | 读写VDF136 | VD136 |
| 64 | U1_VD_PumpSpeed_Cutoff | 读写VDF140 | VD140 |
| 65 | U1_VD_T_Default | 读写VDF144 | VD144 |
| 66 | U1_VD_Available | 只读VDF150 | VD150 |
| 67 | U1_VD_Corr_Needed | 只读VDF154 | VD154 |
| 68 | U1_VD_S3_Estimate | 读写VDF174 | VD174 |
| 70 | U1_VW_Corr_Mode | 读写VWB182 | VW182 |
| 71 | U1_VW_Corr_Result | 读写VWB184 | VW184 |
| 73 | U1_MB_Pump_Reset | 读写VWB202 | VW202 |
| 76 | U1_MB_Pump_SpeedStart | 读写VWB208 | VW208 |
| 77 | U1_MB_Pump_SpeedMax | 读写VWB210 | VW210 |
| 78 | U1_MB_Pump_SpeedCutoff | 读写VWB212 | VW212 |
| 97 | U1_Alarm_Reserved_301_7 | 只读V301.7 | V301.7 |
| 113 | U1_M_InitDone | 只读V304.0 | V304.0 |
| 114 | U1_CommStatus_Syringe | 只读V304.1 | V304.1 |
| 115 | U1_CommStatus_Flow | 只读V304.2 | V304.2 |
| 131 | U1_VD_LeakDiff | 只读VDF312 | VD312 |
| 135 | U1_VD_CycleSetpoint | 读写VDF354 | VD354 |
| 152 | U1_UD_VD32_PreMixMin | 读写VDF468 | VD468 |
| 153 | U1_UD_VD36_RestTime | 读写VDF472 | VD472 |
| 154 | U1_UD_VD40_RestMin | 读写VDF476 | VD476 |
| 155 | U1_UD_VD44_CycleExtend | 读写VDF480 | VD480 |
| 159 | U1_UD_VD144_TDefault | 读写VDF496 | VD496 |
| 162 | U1_UD_VD354_CycleSet | 读写VDF508 | VD508 |
| 168 | U1_UD_VW388_Mode | 读写VWB532 | VW532 |
| 169 | U1_UD_V200_0_AckMode | 读写V536.0 | V536.0 |

## 2. PLC代码中使用但通道处理.csv中缺失的地址（需要补充到HMI）
共 171 个：

| PLC地址 | 标准化 | 读写 | 使用文件 |
|---------|--------|------|----------|
| I0.3 | I000.3 | 读 | FC18_State_S7_End.stl, FC19_State_Error.stl |
| I0.4 | I000.4 | 读 | FC3_AlarmHandling.stl |
| M10.0 | M010.0 | 读写 | FC0_SysInit.stl, FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| M10.1 | M010.1 | 读写 | FC4_ModbusPolling.stl |
| M10.2 | M010.2 | 读写 | FC11_State_S1_Inlet.stl, OB1_MAIN.stl |
| M10.5 | M010.5 | 写 | FC0_SysInit.stl |
| M10.6 | M010.6 | 写 | FC18_State_S7_End.stl |
| M10.7 | M010.7 | 读写 | FC15_State_S4_Transfer.stl, FC16_State_S5_Run.stl, FC17_State_S6_Drain.stl, FC2_EStopHandling.stl, OB1_MAIN.stl, SBR25_ColdStart.stl |
| M11.0 | M011.0 | 读写 | FC0_SysInit.stl, FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| M11.1 | M011.1 | 读写 | FC3_AlarmHandling.stl, SBR25_ColdStart.stl |
| M11.2 | M011.2 | 读写 | FC3_AlarmHandling.stl, SBR25_ColdStart.stl |
| M11.6 | M011.6 | 读写 | FC0_SysInit.stl, FC13A_PumpErrExit.stl, FC13_State_S3_Dosing.stl, FC21_ManualSyringePump.stl, FC4_ModbusPolling.stl, OB1_MAIN.stl, SBR25_ColdStart.stl |
| M11.7 | M011.7 | 读写 | FC13A_PumpErrExit.stl, FC13_State_S3_Dosing.stl, FC21_ManualSyringePump.stl, FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| M12.0 | M012.0 | 读写 | FC13A_PumpErrExit.stl, FC13_State_S3_Dosing.stl, FC21_ManualSyringePump.stl, FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| M12.1 | M012.1 | 读写 | FC13A_PumpErrExit.stl, FC13_State_S3_Dosing.stl, SBR25_ColdStart.stl |
| M12.2 | M012.2 | 读写 | FC13A_PumpErrExit.stl, FC13_State_S3_Dosing.stl, SBR25_ColdStart.stl |
| M13.0 | M013.0 | 读写 | FC20_ManualControl.stl, OB1_MAIN.stl, SBR25_ColdStart.stl |
| M13.1 | M013.1 | 读写 | FC20_ManualControl.stl |
| M13.2 | M013.2 | 读写 | FC20_ManualControl.stl |
| M13.3 | M013.3 | 读写 | FC20_ManualControl.stl |
| M13.4 | M013.4 | 读写 | FC20_ManualControl.stl |
| M13.5 | M013.5 | 读写 | FC21_ManualSyringePump.stl, OB1_MAIN.stl, SBR25_ColdStart.stl |
| M13.6 | M013.6 | 读写 | FC21_ManualSyringePump.stl |
| M13.7 | M013.7 | 读写 | FC21_ManualSyringePump.stl, OB1_MAIN.stl |
| M14.0 | M014.0 | 读写 | FC4_ModbusPolling.stl |
| M14.1 | M014.1 | 读写 | FC4_ModbusPolling.stl |
| M15.0 | M015.0 | 读写 | FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| M15.1 | M015.1 | 读写 | FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| M15.2 | M015.2 | 读写 | FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| M15.3 | M015.3 | 读写 | FC4_ModbusPolling.stl |
| M15.4 | M015.4 | 读写 | FC4_ModbusPolling.stl |
| M16.0 | M016.0 | 读写 | FC10_State_S0_Init.stl, FC11_State_S1_Inlet.stl, FC15_State_S4_Transfer.stl, FC17_State_S6_Drain.stl, FC40_RhythmCorrection.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| M16.1 | M016.1 | 写 | FC10_State_S0_Init.stl, FC15_State_S4_Transfer.stl, FC40_RhythmCorrection.stl |
| M16.2 | M016.2 | 读写 | FC11_State_S1_Inlet.stl |
| M16.3 | M016.3 | 读写 | FC11_State_S1_Inlet.stl, FC1A_State_S2_MixDose.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| M16.4 | M016.4 | 读写 | FC0_SysInit.stl |
| M16.5 | M016.5 | 写 | SBR25_ColdStart.stl |
| M16.6 | M016.6 | 写 | SBR25_ColdStart.stl |
| Q0.2 | Q000.2 | 读写 | FC11_State_S1_Inlet.stl, FC20_ManualControl.stl, FC30_ValveA_Diag.stl |
| Q0.3 | Q000.3 | 读写 | FC15_State_S4_Transfer.stl, FC20_ManualControl.stl, FC31_ValveB_Diag.stl |
| Q0.4 | Q000.4 | 读写 | FC17_State_S6_Drain.stl, FC20_ManualControl.stl, FC32_ValveC_Diag.stl |
| Q0.7 | Q000.7 | 写 | FC19_State_Error.stl, FC2_EStopHandling.stl, FC3_AlarmHandling.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| Q8.0 | Q008.0 | 写 | FC3_AlarmHandling.stl, SBR25_ColdStart.stl |
| Q8.7 | Q008.7 | 写 | SBR25_ColdStart.stl |
| QB0 | QB0 | 写 | FC19_State_Error.stl, FC2_EStopHandling.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| QB8 | QB8 | 写 | SBR25_ColdStart.stl |
| S0 | S0 | 写 | FC19_State_Error.stl, SBR25_ColdStart.stl |
| S1 | S1 | 读写 | FC10_State_S0_Init.stl, FC11_State_S1_Inlet.stl, FC15_State_S4_Transfer.stl, FC40_RhythmCorrection.stl |
| S2 | S2 | 写 | FC11_State_S1_Inlet.stl, FC1A_State_S2_MixDose.stl, OB1_MAIN.stl |
| S3.5 | S3.5 | 写 | FC13_State_S3_Dosing.stl |
| S4 | S4 | 读写 | FC10_State_S0_Init.stl, FC15_State_S4_Transfer.stl, FC17_State_S6_Drain.stl, OB1_MAIN.stl, SBR26_WarmRecovery.stl |
| S5 | S5 | 读写 | FC10_State_S0_Init.stl, FC40_RhythmCorrection.stl, SBR26_WarmRecovery.stl |
| S6 | S6 | 读写 | FC15_State_S4_Transfer.stl, FC16_State_S5_Run.stl, FC17_State_S6_Drain.stl, FC40_RhythmCorrection.stl |
| S7 | S7 | 读写 | FC16_State_S5_Run.stl, FC17_State_S6_Drain.stl, FC40_RhythmCorrection.stl |
| SM0.0 | SM0.0 | 读 | FC0_SysInit.stl, FC10_State_S0_Init.stl, FC11_State_S1_Inlet.stl, FC13_State_S3_Dosing.stl, FC15_State_S4_Transfer.stl, FC16_State_S5_Run.stl, FC17_State_S6_Drain.stl, FC18_State_S7_End.stl, FC19_State_Error.stl, FC1A_State_S2_MixDose.stl, FC20_ManualControl.stl, FC21_ManualSyringePump.stl, FC22_RTC_Sync.stl, FC30_ValveA_Diag.stl, FC31_ValveB_Diag.stl, FC32_ValveC_Diag.stl, FC3_AlarmHandling.stl, FC40_RhythmCorrection.stl, FC4_ModbusPolling.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| SM0.1 | SM0.1 | 读 | FC0_SysInit.stl, FC2_EStopHandling.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| T102 | T102 | 读写 | FC13A_PumpErrExit.stl, FC13_State_S3_Dosing.stl |
| T103 | T103 | 读写 | FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| T104 | T104 | 读写 | FC0_SysInit.stl, FC21_ManualSyringePump.stl |
| T35 | T35 | 读写 | FC2_EStopHandling.stl |
| T37 | T37 | 写 | FC11_State_S1_Inlet.stl, OB1_MAIN.stl |
| T38 | T38 | 读写 | FC11_State_S1_Inlet.stl, FC1A_State_S2_MixDose.stl, OB1_MAIN.stl |
| T39 | T39 | 写 | FC13_State_S3_Dosing.stl |
| T41 | T41 | 写 | FC16_State_S5_Run.stl |
| T42 | T42 | 写 | FC17_State_S6_Drain.stl |
| T46 | T46 | 读写 | FC10_State_S0_Init.stl, FC11_State_S1_Inlet.stl, FC40_RhythmCorrection.stl, OB1_MAIN.stl, SBR26_WarmRecovery.stl |
| T47 | T47 | 读写 | FC16_State_S5_Run.stl, FC18_State_S7_End.stl |
| T48 | T48 | 读写 | FC11_State_S1_Inlet.stl, FC40_RhythmCorrection.stl, OB1_MAIN.stl, SBR26_WarmRecovery.stl |
| T49 | T49 | 写 | FC15_State_S4_Transfer.stl, OB1_MAIN.stl, SBR26_WarmRecovery.stl |
| T50 | T50 | 读写 | FC19_State_Error.stl, FC30_ValveA_Diag.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| T51 | T51 | 读写 | FC30_ValveA_Diag.stl |
| T52 | T52 | 读写 | FC30_ValveA_Diag.stl |
| T53 | T53 | 读写 | FC31_ValveB_Diag.stl |
| T54 | T54 | 读写 | FC31_ValveB_Diag.stl |
| T55 | T55 | 读写 | FC19_State_Error.stl, FC31_ValveB_Diag.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| T56 | T56 | 读写 | FC32_ValveC_Diag.stl |
| T57 | T57 | 读写 | FC32_ValveC_Diag.stl |
| T58 | T58 | 读写 | FC32_ValveC_Diag.stl |
| T59 | T59 | 读写 | FC22_RTC_Sync.stl |
| T60 | T60 | 读写 | FC16_State_S5_Run.stl |
| T61 | T61 | 读写 | FC15_State_S4_Transfer.stl |
| T62 | T62 | 读写 | FC15_State_S4_Transfer.stl |
| V60.0 | V060.0 | 读写 | FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| V60.3 | V060.3 | 读 | FC4_ModbusPolling.stl |
| V60.4 | V060.4 | 读 | FC21_ManualSyringePump.stl |
| V60.5 | V060.5 | 读 | FC3_AlarmHandling.stl |
| VB0 | VBUB000 | 写 | SBR25_ColdStart.stl |
| VB10 | VBUB010 | 读写 | FC15_State_S4_Transfer.stl, SBR26_WarmRecovery.stl |
| VB11 | VBUB011 | 读写 | FC15_State_S4_Transfer.stl, SBR26_WarmRecovery.stl |
| VB12 | VBUB012 | 读写 | FC15_State_S4_Transfer.stl, SBR26_WarmRecovery.stl |
| VB13 | VBUB013 | 读写 | FC15_State_S4_Transfer.stl, SBR26_WarmRecovery.stl |
| VB14 | VBUB014 | 读写 | FC15_State_S4_Transfer.stl, SBR26_WarmRecovery.stl |
| VB15 | VBUB015 | 读写 | FC15_State_S4_Transfer.stl, SBR26_WarmRecovery.stl |
| VB16 | VBUB016 | 写 | FC15_State_S4_Transfer.stl |
| VB17 | VBUB017 | 写 | FC15_State_S4_Transfer.stl |
| VB260 | VBUB260 | 读 | FC19_State_Error.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VB264 | VBUB264 | 写 | FC17_State_S6_Drain.stl |
| VB265 | VBUB265 | 写 | FC17_State_S6_Drain.stl |
| VB266 | VBUB266 | 读写 | FC11_State_S1_Inlet.stl, FC30_ValveA_Diag.stl |
| VB267 | VBUB267 | 写 | FC11_State_S1_Inlet.stl |
| VB268 | VBUB268 | 读写 | FC15_State_S4_Transfer.stl, FC31_ValveB_Diag.stl |
| VB270 | VBUB270 | 读 | FC17_State_S6_Drain.stl |
| VB275 | VBUB275 | 读 | FC19_State_Error.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VB300 | VBUB300 | 读 | SBR25_ColdStart.stl |
| VB378 | VBUB378 | 读 | FC0_SysInit.stl, FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| VB379 | VBUB379 | 读 | FC4_ModbusPolling.stl |
| VB380 | VBUB380 | 读 | FC4_ModbusPolling.stl |
| VB381 | VBUB381 | 读 | FC0_SysInit.stl, FC4_ModbusPolling.stl |
| VB382 | VBUB382 | 读 | FC4_ModbusPolling.stl |
| VB383 | VBUB383 | 读 | FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| VB388 | VBUB388 | 写 | SBR25_ColdStart.stl |
| VB389 | VBUB389 | 写 | SBR25_ColdStart.stl |
| VB410 | VBUB410 | 读 | FC4_ModbusPolling.stl |
| VB456 | VBUB456 | 读 | SBR25_ColdStart.stl |
| VB532 | VBUB532 | 写 | SBR25_ColdStart.stl |
| VB536 | VBUB536 | 读写 | SBR25_ColdStart.stl |
| VB600 | VBUB600 | 读 | FC0_SysInit.stl |
| VB900 | VBUB900 | 读写 | FC15_State_S4_Transfer.stl, FC22_RTC_Sync.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VB901 | VBUB901 | 读写 | FC15_State_S4_Transfer.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VB902 | VBUB902 | 读写 | FC15_State_S4_Transfer.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VB903 | VBUB903 | 读写 | FC15_State_S4_Transfer.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VB904 | VBUB904 | 读写 | FC15_State_S4_Transfer.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VB905 | VBUB905 | 读写 | FC15_State_S4_Transfer.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VB906 | VBUB906 | 写 | FC15_State_S4_Transfer.stl, FC22_RTC_Sync.stl |
| VB907 | VBUB907 | 读写 | FC22_RTC_Sync.stl, SBR26_WarmRecovery.stl |
| VB908 | VBUB908 | 写 | FC15_State_S4_Transfer.stl |
| VD186 | VDF186 | 读写 | FC11_State_S1_Inlet.stl, FC16_State_S5_Run.stl, FC40_RhythmCorrection.stl, SBR26_WarmRecovery.stl |
| VD190 | VDF190 | 写 | FC11_State_S1_Inlet.stl, FC40_RhythmCorrection.stl, SBR26_WarmRecovery.stl |
| VD232 | VDF232 | 读写 | FC13_State_S3_Dosing.stl, FC21_ManualSyringePump.stl, FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| VD244 | VDF244 | 写 | FC40_RhythmCorrection.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VD256 | VDF256 | 写 | FC40_RhythmCorrection.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VD320 | VDF320 | 写 | FC11_State_S1_Inlet.stl |
| VD324 | VDF324 | 写 | FC15_State_S4_Transfer.stl |
| VD332 | VDF332 | 写 | FC11_State_S1_Inlet.stl |
| VD336 | VDF336 | 写 | FC1A_State_S2_MixDose.stl |
| VD346 | VDF346 | 读写 | FC13_State_S3_Dosing.stl |
| VD374 | VDF374 | 写 | SBR25_ColdStart.stl |
| VD410 | VDF410 | 写 | FC4_ModbusPolling.stl |
| VD414 | VDF414 | 读写 | FC16_State_S5_Run.stl, FC17_State_S6_Drain.stl, FC40_RhythmCorrection.stl, SBR25_ColdStart.stl |
| VD426 | VDF426 | 写 | FC40_RhythmCorrection.stl, SBR25_ColdStart.stl |
| VD430 | VDF430 | 写 | FC40_RhythmCorrection.stl, SBR25_ColdStart.stl |
| VW190 | VWB190 | 写 | FC40_RhythmCorrection.stl |
| VW192 | VWB192 | 读写 | FC40_RhythmCorrection.stl |
| VW194 | VWB194 | 读写 | FC40_RhythmCorrection.stl |
| VW198 | VWB198 | 写 | FC0_SysInit.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VW200 | VWB200 | 读写 | FC40_RhythmCorrection.stl |
| VW224 | VWB224 | 读 | FC4_ModbusPolling.stl |
| VW226 | VWB226 | 读写 | FC13A_PumpErrExit.stl, FC13_State_S3_Dosing.stl, FC1A_State_S2_MixDose.stl, SBR25_ColdStart.stl |
| VW230 | VWB230 | 写 | FC13_State_S3_Dosing.stl, FC21_ManualSyringePump.stl, FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| VW236 | VWB236 | 写 | FC11_State_S1_Inlet.stl |
| VW252 | VWB252 | 写 | FC1A_State_S2_MixDose.stl |
| VW260 | VWB260 | 读写 | FC11_State_S1_Inlet.stl, FC19_State_Error.stl, FC30_ValveA_Diag.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VW262 | VWB262 | 读写 | FC31_ValveB_Diag.stl |
| VW264 | VWB264 | 读写 | FC32_ValveC_Diag.stl |
| VW270 | VWB270 | 写 | FC17_State_S6_Drain.stl, FC32_ValveC_Diag.stl |
| VW274 | VWB274 | 写 | FC31_ValveB_Diag.stl |
| VW276 | VWB276 | 写 | FC17_State_S6_Drain.stl, FC32_ValveC_Diag.stl |
| VW278 | VWB278 | 写 | FC11_State_S1_Inlet.stl, FC30_ValveA_Diag.stl |
| VW280 | VWB280 | 写 | FC11_State_S1_Inlet.stl, FC30_ValveA_Diag.stl |
| VW286 | VWB286 | 写 | FC11_State_S1_Inlet.stl, FC15_State_S4_Transfer.stl |
| VW288 | VWB288 | 写 | FC11_State_S1_Inlet.stl |
| VW290 | VWB290 | 读写 | FC15_State_S4_Transfer.stl, FC4_ModbusPolling.stl, SBR25_ColdStart.stl |
| VW292 | VWB292 | 读写 | FC4_ModbusPolling.stl |
| VW298 | VWB298 | 写 | FC4_ModbusPolling.stl |
| VW300 | VWB300 | 读 | SBR25_ColdStart.stl |
| VW304 | VWB304 | 读写 | FC10_State_S0_Init.stl, FC11_State_S1_Inlet.stl, FC15_State_S4_Transfer.stl, FC17_State_S6_Drain.stl, FC1A_State_S2_MixDose.stl, FC40_RhythmCorrection.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VW306 | VWB306 | 读写 | FC16_State_S5_Run.stl, FC17_State_S6_Drain.stl, FC40_RhythmCorrection.stl, OB1_MAIN.stl, SBR25_ColdStart.stl, SBR26_WarmRecovery.stl |
| VW378 | VWB378 | 读 | FC0_SysInit.stl, SBR25_ColdStart.stl |
| VW410 | VWB410 | 写 | FC4_ModbusPolling.stl |
| VW510 | VWB510 | 读写 | FC21_ManualSyringePump.stl, FC4_ModbusPolling.stl |
| VW600 | VWB600 | 读 | FC0_SysInit.stl |