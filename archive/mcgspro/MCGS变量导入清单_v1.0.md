# MCGS 变量导入清单 v1.0

**配套文档**：《HMI-PLC变量地址表 v1.0》、《昆仑通态MCGS组态实施指南 v1.0》
**用途**：MCGS组态软件批量导入PLC变量,避免手工逐个建立73个变量
**适用范围**：昆仑通态MCGS组态环境(McgseSet)
**Story**：AQEX-12 Story 2.1 8个画面组态开发

---

## 一、导入操作SOP

### 1.1 MCGS变量导入步骤

1. 打开MCGS组态软件,加载AQUA_EXPO工程
2. 工作台→实时数据库→导入数据
3. 选择本目录下 `MCGS变量导入_8连接版.csv`
4. 导入选项:
   - 编码:UTF-8
   - 分隔符:逗号
   - 覆盖同名变量:是
5. 导入完成后,应显示73个变量
6. 检查变量类型/地址/连接是否正确

### 1.2 连接配置(导入变量前需先建8个连接)

在MCGS组态窗口→设备窗口→设备组态中,先建立8个连接:

| 连接名 | 设备类型 | 协议 | IP地址 | 端口 | 说明 |
|---|---|---|---|---|---|
| PLC_01 | S7-200 SMART | S7协议(TSAP) | 192.168.2.101 | 102 | 1号单元 |
| PLC_02 | S7-200 SMART | S7协议 | 192.168.2.102 | 102 | 2号单元 |
| PLC_03 | S7-200 SMART | S7协议 | 192.168.2.103 | 102 | 3号单元 |
| PLC_04 | S7-200 SMART | S7协议 | 192.168.2.104 | 102 | 4号单元 |
| PLC_05 | S7-200 SMART | S7协议 | 192.168.2.105 | 102 | 5号单元 |
| PLC_06 | S7-200 SMART | S7协议 | 192.168.2.106 | 102 | 6号单元 |
| PLC_07 | S7-200 SMART | S7协议 | 192.168.2.107 | 102 | 7号单元 |
| PLC_08 | S7-200 SMART | S7协议 | 192.168.2.108 | 102 | 8号单元 |

**协议参数**(S7-200 SMART以太网):
- 本地TSAP: 10.00
- 远程TSAP: 02.00
- 机架号: 0
- 槽号: 1

### 1.3 备选方案:Modbus TCP(若S7协议不支持8连接)

若MCGS标准版S7协议连接数限制<8,改用Modbus TCP:

| 连接名 | 设备类型 | 协议 | IP地址 | 端口 |
|---|---|---|---|---|
| PLC_01~08 | 通用Modbus TCP | Modbus TCP Client | 192.168.2.101~108 | 502 |

PLC侧需在STEP7系统块→通讯端口→启用"Modbus TCP服务器",映射V区到保持寄存器(40001~49999)。

---

## 二、变量导入CSV格式说明

MCGS变量导入CSV格式(与HMI变量导入CSV模板.csv兼容,增加了MCGS专用列):

| 列名 | 说明 | 示例 |
|---|---|---|
| 变量名 | MCGS变量名(含单元前缀) | U1_VW2_StateMachine |
| 数据类型 | MCGS类型(Bool/Int/Float/String) | Int |
| 连接名 | MCGS连接名 | PLC_01 |
| PLC地址 | S7地址 | VW2 |
| 读写属性 | R/RW | R |
| 断电保持 | 是/否 | 是 |
| 注释 | 变量说明 | 状态机当前状态 |
| 画面编号 | 主要使用画面 | 1 |

**单元前缀规则**:
- 1号单元变量: U1_XXX (连接PLC_01)
- 2号单元变量: U2_XXX (连接PLC_02)
- ...
- 8号单元变量: U8_XXX (连接PLC_08)

---

## 三、8套单元变量汇总(73变量 × 8套 = 584个MCGS变量)

### 3.1 每套单元73个变量清单(以1号单元为例)

完整CSV见本目录下 `MCGS变量导入_8连接版.csv`,包含8套共584个变量。

### 3.2 HMI内部变量(不读PLC,18个)

| 变量名 | 类型 | 说明 |
|---|---|---|
| SelectedUnit | Int | 当前选中单元号(1~8) |
| UnitEnabled_01~08 | Bool | 8个单元使能标志(配置页设置) |
| LoginLevel | Int | 当前登录权限(0=未登录,1=L1,2=L2,3=L3) |
| LoginTime | String | 登录时间(用于15分钟超时判断) |
| GlobalAlarmActive | Bool | 全局报警活动标志 |
| GlobalMuteState | Bool | 全局消音状态 |
| CommStatus_01~08 | Bool | 8个连接通讯状态 |

---

## 四、变量分组(便于画面组态引用)

### 4.1 命令位组(V0区,8个/单元)

U1_CMD_Start, U1_CMD_Pause, U1_CMD_Stop, U1_CMD_AckAlarm, U1_CMD_Mute, U1_CMD_ForceTankA_Empty, U1_CMD_ForceTankA_Full, U1_CMD_SafetyRelayAck

### 4.2 状态位组(V1区,8个/单元)

U1_STA_StartAck, U1_STA_PauseAck, U1_STA_StopAck, U1_STA_AlarmAckDone, U1_STA_MuteDone, U1_STA_ForceDone, U1_STA_TankA_State, U1_STA_TankB_State

### 4.3 状态机组(VW2/4/6/8,4个/单元)

U1_VW2_StateMachine, U1_VW4_PumpStatus, U1_VW6_AlarmCode, U1_VW8_RoundCount

### 4.4 HMI设定参数组(VD10~VD140,24个/单元)

U1_VD_C_Set, U1_VD_C_Stock, U1_VD_StepResolution, U1_VD_CycleSetpoint, ... (共24个)

### 4.5 PLC实测值组(VD70~VD128,9个/单元)

U1_VD_S1_Actual, U1_VD_S4_Actual, U1_VD_S6_Actual, U1_VD_FlowMeter_Snapshot, U1_VD_FlowMeter_Current, U1_VD_Current_InletVolume, U1_VD_FlowRate_Instant, U1_VD_ExperimentDuration_Accum, U1_VD_Vol_Target

### 4.6 纠偏参数组(VD104~VD140,9个/单元)

U1_VD_T_Default, U1_VD_S6_Default, U1_VD_T_Rolling, U1_VD_S6_Rolling, U1_VD_S2_Target, U1_VD_RestTime_Target, U1_VD_CycleExtend_Target, U1_VD_PumpSpeed_Start, U1_VD_PumpSpeed_Max, U1_VD_PumpSpeed_Cutoff

### 4.7 报警字组(VB300~303,4字节32位/单元)

U1_V300_0到U1_V303_7共32个报警位(详见报警字32位解析映射表.md),**v1.2 新增** V303.2 S4 转移等待超时(原 V303.2 空闲,现已用于过程级一般报警)

### 4.8 手动控制命令组(V2.4~V3.3,8个/单元)

U1_CMD_Manual_ValveA_Open, U1_CMD_Manual_ValveA_Close, U1_CMD_Manual_ValveB_Open, U1_CMD_Manual_ValveB_Close, U1_CMD_Manual_ValveC_Open, U1_CMD_Manual_ValveC_Close, U1_CMD_Manual_Pump1_On, U1_CMD_Manual_Pump1_Off

### 4.9 时间戳组(DT10~DT17,8字节/单元)

U1_DT_TankB_FullTime等(由S7协议DT数据类型映射)

---

## 五、导入后验证

### 5.1 变量数量验证

- 导入后实时数据库应显示: 584(PLC变量) + 18(HMI内部) = **602个变量**
- 若数量不符,检查CSV是否有空行或格式错误

### 5.2 连接验证

- 设备窗口→每个连接右键→测试连接
- 8个连接均应显示"连接成功"(PLC在线时)
- PLC离线时显示"连接超时"(正常,组态阶段可忽略)

### 5.3 变量类型验证

随机抽查10个变量,确认:
- Bool型: 命令位/状态位/报警位
- Int型: VW状态机/报警码/轮次/泵状态
- Float型: VD参数/实测值/纠偏值

---

## 附录:变量导入CSV生成方法

如需重新生成CSV(变量地址变更时),执行:

```bash
cd /workspace/AQUA-EXPO/tools
python3 generate_mcgsv_ari_csv.py
```

该脚本读取变量地址表,自动生成8套单元的MCGS变量CSV。

---

**文档结束**

**待办**:
1. MCGS组态环境实际导入测试(需安装MCGS软件)
2. 若S7协议8连接不支持,切换Modbus TCP方案
3. 变量地址变更时重新生成CSV