# AQUA-EXPO McgsPro 3.3.6 脚本代码 v2.0

**项目**: 8套缸单�
�药液�
�置加注控制系统
**HMI**: 昆仑通�?McgsPro 3.3.6 (TPC 触摸�?
**�
�套文档**: McgsPro变量导�
�_单�
�1.csv ~ 单�
�8.csv / HMI用户权限矩阵_v1.0.md / HMI画面架构规划文档.md / McgsPro两级菜单改造方案_v1.0.html
**用�?*: 直接粘贴�?McgsPro 脚本编辑�?完成4菜单窗口+9画面+策略+子窗口的脚本组�?
**Story**: AQEX-12 Story 2.1 (8画面组�? �?v2.0 重写为纯�?McgsPro 类Basic语法 �?v2.1 新增两级菜单导航脚本

> **v2.1 更新**: 新增两级菜单导航(主菜�?标签→子菜单→画�?,新增9个菜单窗口脚�?所有返回按钮目标从画面1_总览改为各自上级菜单窗口,画面8拆分为画�?a_单�
�使能和画�?b_权限管理。详见《McgsPro两级菜单改造方案_v1.0》�?

---

## 〇、重要说�?McgsPro 脚本语言�?VBScript 的差�?

> **本版 v2.0 �?v1.0 的根本区�?*:v1.0 误用 VBScript 语法(For...Next / Execute / MsgBox / !SwitchWindow / !CheckUser �?,这些�?McgsPro 3.3.6 �?*均不支持**。v2.0 严格�?docs/reference/McgsProHelp_text/ 官方文档重写为类 Basic 语法�?

### 1. 语言定位

McgsPro 脚本程序�?*�?Basic 脚本语言**,不是 VBScript,也不�?VBA。它只是"类似普通的 Basic 语言",但功能子集远小于 VBScript�?

### 2. 不支持的 VBScript / VBA 语法(�
须避�
�)

| 不支持语�?| 替代方案 |
|---|---|
| `For i = 1 To 8 ... Next` | �?`While...EndWhile` + 整型索引,或直接展开�?8 条赋值语�?|
| `Exit For` / `Exit Sub` / `Exit Function` | �?`Exit` (退出整个脚�? �?`Break` (跳出 While) |
| `Sub ... End Sub` / `Function ... End Function` | McgsPro 不支持自定义子程�?子函�?所有逻辑�
须�
联 |
| `ElseIf ... Then` | 用嵌�?`If...Then...Else...EndIf` 实现多分�?|
| `Execute("U" & i & "_CMD_Mute = 1")` | **无法动态构造变量名**,�
须显式写出 8 个单�
�的赋值语�?|
| `MsgBox(...)` / `InputBox(...)` | 用子窗口(!OpenSubWnd)实现确认/选择对话�?|
| `!OpenWindow` / `!SwitchWindow` | �?`!SetWindow(窗口,1)` 打开、`!CloseAllWindow(name)` �
�闭并切�?|
| `!CheckUser` | �?`!CheckUserGroup("组名")` (返回 0=属于 / 1=不属�? |
| `GetValue(name)` / `SetValue(name,v)` | 直接引用变量�?`U1_CMD_Start = 1` |
| `Format(...)` / `CDate(...)` / `DateDiff(...)` | �?`!TimeStr2I` / `!TimeI2Str` / `!TimeGetSpan` 等时间函�?|
| `Dim x` (无类�? | �
须�?`DIM x AS integer` (4 种类�? byte/integer/single/string) |
| 数组下标�?0 开�?| McgsPro 数组下标**�?1 开�?* |

### 3. McgsPro 支持的语法子�?

- **赋�?*: `变量 = 表达式`
- **条件**: `If 表达�?Then 语句` / `If 表达�?Then ... EndIf` / `If 表达�?Then ... Else ... EndIf`
- **循环**: `While 条件表达�?... EndWhile`
- **跳出**: `Break` (跳出 While) / `Exit` (退出整个脚�?
- **注释**: `' 单引号开�?
- **声明**: `DIM <变量�? AS <类型>` (类型: byte / integer / single / string)
- **数组**: `DIM <变量�?(<长度>) AS <类型>`,访问 `arr[index]`,index �?1 开�?
- **多语句同�?*: �?`:` 分隔
- **联行�?*: 行尾 `_` 连接下一�?
- **运算�?*: `^ * / \ + - MOD AND OR NOT XOR > >= = <= < <>`

### 4. �
�键系统函数(本工程使�?

| 函数 | 用�?|
|---|---|
| `!OpenSubWnd(窗口,X,Y,�?�?模式)` | 打开子窗�?模式�?1=模�?2=菜单/16=边框/32=跟随鼠标/64=自动尺寸) |
| `!CloseAllSubWnd()` | �
�闭当前标准窗口下所有子窗口 |
| `!CloseSubWnd(窗口对象)` | �
�闭指定子窗�?|
| `!CloseAllWindow(WndName)` | �
�闭所有窗�?WndName 非空则保留并打开�? |
| `!SetWindow(窗口对象,Op)` | Op=1打开可见/2打开不可�?3�
�闭/4打印/5刷新 |
| `!SetDevice(设备�?Op,"")` | Op=1启动设备/2停止/3测状�?4启动一�?5改周�?6命令 |
| `!SetStgy(策略�?` | 异步启动用户策略 |
| `!SetStgyMode(策略�?` | 同步启动用户策略 |
| `!Beep()` | 蜂鸣 |
| `!Sleep(毫秒)` | 延时 |
| `!LogOn()` / `!LogOff()` | 弹登录框 / 注销 |
| `!CheckUserGroup("组名")` | 返回 0=属于,1=不属�?|
| `!GetCurrentUser()` / `!GetCurrentGroup()` | 当前用户�?/ 当前用户�?多组�?0x01 分隔) |
| `!Editusers()` / `!ChangePassword()` | 用户管理窗口 / 修改密码窗口 |
| `!EnableExitLogon(n)` | n=0不检�?1检�?2�
时提示/3�
时静默 |
| `!SaveData(数据对象)` | 立即存盘(组对象需勾选存盘属�?60秒后自动刷盘�?!FreshDataSave) |
| `!FreshDataSave()` | 立即刷盘 |
| `!SetAlmInfo(对象,报警序号,报警信息)` | 设置报警信息 |
| `!SetAlmValue(对象,报警序号,�?标志)` | 设置报警限�?|
| `!AnswerAlm(对象,报警序号)` | 应答报警(-1=�
�部) |
| `!ClearHistoryAlarmData()` | �
除历史报警数据 |
| `!OperationLogClear()` | �
除操作日志 |
| `!TimeStr2I("YYYY-MM-DD HH:MM:SS")` | 时间字符串转整数 |
| `!TimeI2Str(iTime,格式)` | 整数转时间字符串 |
| `!TimeGetCurrentTime()` | 当前时间整数 |
| `!TimeGetSpan(t1,t2)` | 时间�?�? |

### 5. 系统变量(�?`$` 开�?只读)

`$Year $Month $Day $Hour $Minute $Second $Week $Date $Time $Timer $RunTime $UserName`

### 6. 用户组命�?对应权限矩阵)

- `操作员组` �?L1 (日常监控+基础操作)
- `维护组` �?L2 (手动控制+参数时间�?
- `管理员组` �?L3 (单�
�使能+系统维护+设为默认)

### 7. 8单�
�变量扩展约定

本工�?8 套单�
�变量命名规�?`U<单�
��?_XXX`,�?`U1_CMD_Start` ~ `U8_CMD_Start`。由�?McgsPro **不支�?Execute 动态构造变量名**,凡涉�?�?8 个单�
�循环操�?的脚�?本文件采�?*显式展开 8 条赋值语�?*的写�?而非 For 循环。涉�?�?1 号为�?的相似脚�?会给�?1 号完整代�?+ 2~8 号扩展说明�?

### 8. 脚本编号索引(�
?66 �?

| 分区 | 编号 | 数量 | 位置 |
|---|---|---|---|
| A. 工程启动策略 | 1 | 1 | 启动策略 |
| B. 周期策略 | 2~3 | 2 | 循环策略 |
| **B2. 菜单窗口脚本(新增)** | **M1~M9** | **9** | **菜单窗口构件** |
| C. 画面1_总览 | 4~9 | 6 | 窗口/构件 |
| D. 画面2_单�
�详�
 | 10~17 | 8 | 窗口/构件 |
| E. 画面3_手动控制 | 18~26 | 9 | 窗口/构件 |
| F. 画面4_参数设置 | 27~32 | 6 | 窗口/构件 |
| G. 画面5_报警日志 | 33~36 | 4 | 窗口/构件 |
| H. 画面6_趋势曲线 | 37~39 | 3 | 窗口/构件 |
| I. 画面7_通讯维护 | 40~43 | 4 | 窗口/构件 |
| J. 画面8a_单�
�使能 + 画面8b_权限管理 | 44~49 | 6 | 窗口/构件 |
| K. 二次确认子窗�?| 50~57 | 8 | 子窗口构�?|

> 说明:v2.1 新增 B2 �?菜单窗口脚本 M1~M9,�
?�?,含主菜单4个按钮脚本�?个子菜单的画面按钮脚本�?个子菜单的返回按钮脚�?返回逻辑相同合并�?�?。原 J �?画面8_系统设置"拆分为画�?a_单�
�使能(脚本44~45)和画�?b_权限管理(脚本46~49)。合�?57+9=66 个�?

---

## 一、A. 工程启动策略脚本

### 脚本 1:启动策略脚本

- **编号**: 1
- **用�?*: 工程启动时初始化�
部变量、启动所�?PLC 设备、加载用户�
��?
- **位置**: 运行策略 �?启动策略 (系统固有策略�?
- **触发方式**: 系统启动时自动执行一�?

```
' ============================================
' AQUA-EXPO 启动策略脚本
' 功能: 初始化�
部变�?+ 启动8台PLC设备 + 加载用户�
�置
' 依赖变量: SelectedUnit / GlobalAlarmActive / GlobalMuteState /
'           U1_Enable~U8_Enable / U1_Online~U8_Online / CommStatus /
'           LoginTime / ExitLogonEnabled
' ============================================

' --- 1. 初始化选中单�
�(默认1�? ---
SelectedUnit = 1

' --- 2. 初始化�
�局状�?---
GlobalAlarmActive = 0
GlobalMuteState = 0
GlobalAckPending = 0
LoginTime = 0
ExitLogonEnabled = 1

' --- 3. 初始化单�
�使�?从断电保持区读取,首次启动默认1号使�? ---
' U1_Enable~U8_Enable 已�
�置为断电保持�
部变量,此处�
在值为0时给默认�?
If U1_Enable = 0 Then
    If U2_Enable = 0 Then
        If U3_Enable = 0 Then
            If U4_Enable = 0 Then
                If U5_Enable = 0 Then
                    If U6_Enable = 0 Then
                        If U7_Enable = 0 Then
                            If U8_Enable = 0 Then
                                U1_Enable = 1
                            EndIf
                        EndIf
                    EndIf
                EndIf
            EndIf
        EndIf
    EndIf
EndIf

' --- 4. 初始化通讯在线状�?�
首次轮询后更新) ---
U1_Online = 0
U2_Online = 0
U3_Online = 0
U4_Online = 0
U5_Online = 0
U6_Online = 0
U7_Online = 0
U8_Online = 0

' --- 5. 初始化通讯状态汇�?---
CommStatus = 0

' --- 6. 启动8台PLC设备(设备�? PLC_01~PLC_08) ---
!SetDevice(PLC_01, 1, "")
!SetDevice(PLC_02, 1, "")
!SetDevice(PLC_03, 1, "")
!SetDevice(PLC_04, 1, "")
!SetDevice(PLC_05, 1, "")
!SetDevice(PLC_06, 1, "")
!SetDevice(PLC_07, 1, "")
!SetDevice(PLC_08, 1, "")

' --- 7. 启动16个Modbus从站设备(每套PLC 2�? 注射�?流量�? ---
!SetDevice(MB_Pump_01, 1, "")
!SetDevice(MB_Flow_01, 1, "")
!SetDevice(MB_Pump_02, 1, "")
!SetDevice(MB_Flow_02, 1, "")
!SetDevice(MB_Pump_03, 1, "")
!SetDevice(MB_Flow_03, 1, "")
!SetDevice(MB_Pump_04, 1, "")
!SetDevice(MB_Flow_04, 1, "")
!SetDevice(MB_Pump_05, 1, "")
!SetDevice(MB_Flow_05, 1, "")
!SetDevice(MB_Pump_06, 1, "")
!SetDevice(MB_Flow_06, 1, "")
!SetDevice(MB_Pump_07, 1, "")
!SetDevice(MB_Flow_07, 1, "")
!SetDevice(MB_Pump_08, 1, "")
!SetDevice(MB_Flow_08, 1, "")

' --- 8. 开启操作日�?+ 退出权限检�?---
!OperationLogEnable()
!EnableExitLogon(ExitLogonEnabled)

' --- 9. 初始化菜单系�?v2.1新增) ---
CurrentMenuGroup = 0

' --- 10. 打开菜单_主菜�?两级菜单导航�
�口) ---
!SetWindow(菜单_主菜�? 1)
```

---

## 二、B. 周期策略脚本

### 脚本 2:500ms 周期策略

- **编号**: 2
- **用�?*: 周期�
零命令�?模拟上升�? + 更新通讯在线状�?+ 更新 CommStatus 汇�?
- **位置**: 运行策略 �?循环策略 (用户创建,命名"循环策略_500ms")
- **触发方式**: 定时循环,周期 500ms

```
' ============================================
' 500ms 周期策略
' 功能1: �
零8个单�
�的命令�?模拟脉冲上升�?PLC侧用下降沿检�?
' 功能2: 检�?台PLC通讯状�?更新 U1_Online~U8_Online �?CommStatus
' 注意: McgsPro 不支�?For...Next,8 个单�
�显式展开
' ============================================

' --- 1. �
零1号单�
�命令位 ---
If U1_CMD_Start = 1 Then
    U1_CMD_Start = 0
EndIf
If U1_CMD_Stop = 1 Then
    U1_CMD_Stop = 0
EndIf
If U1_CMD_AckAlarm = 1 Then
    U1_CMD_AckAlarm = 0
EndIf
If U1_CMD_Mute = 1 Then
    U1_CMD_Mute = 0
EndIf
If U1_CMD_SafetyRelayAck = 1 Then
    U1_CMD_SafetyRelayAck = 0
EndIf

' --- 2. �
零2号单�
�命令位 ---
If U2_CMD_Start = 1 Then
    U2_CMD_Start = 0
EndIf
If U2_CMD_Stop = 1 Then
    U2_CMD_Stop = 0
EndIf
If U2_CMD_AckAlarm = 1 Then
    U2_CMD_AckAlarm = 0
EndIf
If U2_CMD_Mute = 1 Then
    U2_CMD_Mute = 0
EndIf
If U2_CMD_SafetyRelayAck = 1 Then
    U2_CMD_SafetyRelayAck = 0
EndIf

' --- 3. �
零3号单�
�命令位 ---
If U3_CMD_Start = 1 Then
    U3_CMD_Start = 0
EndIf
If U3_CMD_Stop = 1 Then
    U3_CMD_Stop = 0
EndIf
If U3_CMD_AckAlarm = 1 Then
    U3_CMD_AckAlarm = 0
EndIf
If U3_CMD_Mute = 1 Then
    U3_CMD_Mute = 0
EndIf
If U3_CMD_SafetyRelayAck = 1 Then
    U3_CMD_SafetyRelayAck = 0
EndIf

' --- 4. �
零4号单�
�命令位 ---
If U4_CMD_Start = 1 Then
    U4_CMD_Start = 0
EndIf
If U4_CMD_Stop = 1 Then
    U4_CMD_Stop = 0
EndIf
If U4_CMD_AckAlarm = 1 Then
    U4_CMD_AckAlarm = 0
EndIf
If U4_CMD_Mute = 1 Then
    U4_CMD_Mute = 0
EndIf
If U4_CMD_SafetyRelayAck = 1 Then
    U4_CMD_SafetyRelayAck = 0
EndIf

' --- 5. �
零5号单�
�命令位 ---
If U5_CMD_Start = 1 Then
    U5_CMD_Start = 0
EndIf
If U5_CMD_Stop = 1 Then
    U5_CMD_Stop = 0
EndIf
If U5_CMD_AckAlarm = 1 Then
    U5_CMD_AckAlarm = 0
EndIf
If U5_CMD_Mute = 1 Then
    U5_CMD_Mute = 0
EndIf
If U5_CMD_SafetyRelayAck = 1 Then
    U5_CMD_SafetyRelayAck = 0
EndIf

' --- 6. �
零6号单�
�命令位 ---
If U6_CMD_Start = 1 Then
    U6_CMD_Start = 0
EndIf
If U6_CMD_Stop = 1 Then
    U6_CMD_Stop = 0
EndIf
If U6_CMD_AckAlarm = 1 Then
    U6_CMD_AckAlarm = 0
EndIf
If U6_CMD_Mute = 1 Then
    U6_CMD_Mute = 0
EndIf
If U6_CMD_SafetyRelayAck = 1 Then
    U6_CMD_SafetyRelayAck = 0
EndIf

' --- 7. �
零7号单�
�命令位 ---
If U7_CMD_Start = 1 Then
    U7_CMD_Start = 0
EndIf
If U7_CMD_Stop = 1 Then
    U7_CMD_Stop = 0
EndIf
If U7_CMD_AckAlarm = 1 Then
    U7_CMD_AckAlarm = 0
EndIf
If U7_CMD_Mute = 1 Then
    U7_CMD_Mute = 0
EndIf
If U7_CMD_SafetyRelayAck = 1 Then
    U7_CMD_SafetyRelayAck = 0
EndIf

' --- 8. �
零8号单�
�命令位 ---
If U8_CMD_Start = 1 Then
    U8_CMD_Start = 0
EndIf
If U8_CMD_Stop = 1 Then
    U8_CMD_Stop = 0
EndIf
If U8_CMD_AckAlarm = 1 Then
    U8_CMD_AckAlarm = 0
EndIf
If U8_CMD_Mute = 1 Then
    U8_CMD_Mute = 0
EndIf
If U8_CMD_SafetyRelayAck = 1 Then
    U8_CMD_SafetyRelayAck = 0
EndIf

' --- 9. 更新8台PLC通讯在线状�?---
' !SetDevice(name,3,"") 返回 1=启动状�?在线), 0=停止状�?离线)
If !SetDevice(PLC_01, 3, "") = 1 Then
    U1_Online = 1
Else
    U1_Online = 0
EndIf
If !SetDevice(PLC_02, 3, "") = 1 Then
    U2_Online = 1
Else
    U2_Online = 0
EndIf
If !SetDevice(PLC_03, 3, "") = 1 Then
    U3_Online = 1
Else
    U3_Online = 0
EndIf
If !SetDevice(PLC_04, 3, "") = 1 Then
    U4_Online = 1
Else
    U4_Online = 0
EndIf
If !SetDevice(PLC_05, 3, "") = 1 Then
    U5_Online = 1
Else
    U5_Online = 0
EndIf
If !SetDevice(PLC_06, 3, "") = 1 Then
    U6_Online = 1
Else
    U6_Online = 0
EndIf
If !SetDevice(PLC_07, 3, "") = 1 Then
    U7_Online = 1
Else
    U7_Online = 0
EndIf
If !SetDevice(PLC_08, 3, "") = 1 Then
    U8_Online = 1
Else
    U8_Online = 0
EndIf

' --- 10. 更新通讯状态汇�?CommStatus (0~8,在线单�
��? ---
CommStatus = U1_Online + U2_Online + U3_Online + U4_Online + U5_Online + U6_Online + U7_Online + U8_Online

' --- 11. 更新�
�局报警状�?任一使能+在线单�
�有报警则�?) ---
GlobalAlarmActive = 0
If U1_Enable = 1 Then
    If U1_Online = 1 Then
        If U1_VW6_AlarmCode <> 0 Then
            GlobalAlarmActive = 1
        EndIf
    EndIf
EndIf
If U2_Enable = 1 Then
    If U2_Online = 1 Then
        If U2_VW6_AlarmCode <> 0 Then
            GlobalAlarmActive = 1
        EndIf
    EndIf
EndIf
If U3_Enable = 1 Then
    If U3_Online = 1 Then
        If U3_VW6_AlarmCode <> 0 Then
            GlobalAlarmActive = 1
        EndIf
    EndIf
EndIf
If U4_Enable = 1 Then
    If U4_Online = 1 Then
        If U4_VW6_AlarmCode <> 0 Then
            GlobalAlarmActive = 1
        EndIf
    EndIf
EndIf
If U5_Enable = 1 Then
    If U5_Online = 1 Then
        If U5_VW6_AlarmCode <> 0 Then
            GlobalAlarmActive = 1
        EndIf
    EndIf
EndIf
If U6_Enable = 1 Then
    If U6_Online = 1 Then
        If U6_VW6_AlarmCode <> 0 Then
            GlobalAlarmActive = 1
        EndIf
    EndIf
EndIf
If U7_Enable = 1 Then
    If U7_Online = 1 Then
        If U7_VW6_AlarmCode <> 0 Then
            GlobalAlarmActive = 1
        EndIf
    EndIf
EndIf
If U8_Enable = 1 Then
    If U8_Online = 1 Then
        If U8_VW6_AlarmCode <> 0 Then
            GlobalAlarmActive = 1
        EndIf
    EndIf
EndIf
```

### 脚本 3:1 秒周期策�?

- **编号**: 3
- **用�?*: 更新系统时间显示 + 检查登录�
�?
- **位置**: 运行策略 �?循环策略 (用户创建,命名"循环策略_1s")
- **触发方式**: 定时循环,周期 1000ms

```
' ============================================
' 1秒周期策�?
' 功能1: 拼接 $Date + $Time 写�
� SysTimeString (供画面顶部显�?
' 功能2: 检查登录�
�?15分钟无操作自动注销)
' ============================================

' --- 1. 更新系统时间显示字符�?---
SysTimeString = $Date + " " + $Time

' --- 2. 检查登录�
�?---
If $UserName <> "" Then
    DIM nowSec AS integer
    DIM lastSec AS integer
    DIM spanSec AS integer
    nowSec = !TimeGetCurrentTime()
    lastSec = LoginTime
    If lastSec > 0 Then
        spanSec = nowSec - lastSec
        If spanSec < 0 Then
            spanSec = 0
        EndIf
        ' 15分钟 = 900�?
        If spanSec > 900 Then
            !LogOff()
            LoginTime = 0
            !Beep()
        EndIf
    EndIf
EndIf

' --- 3. 检�?EnableExitLogon �
时模式(2=�
时提示,3=�
时静默) ---
' �?!EnableExitLogon �
部处理,此处�
记录最近操作时�?
LastMouseTime = !GetLastMouseActionTime()
```

---

## 二B、B2. 菜单窗口脚本(两级菜单导航,v2.1新增)

> **菜单导航原理**:主菜�?个标签→子菜单→画面。所有窗口切换使�?`!CloseAllWindow("窗口�?)` (�
�闭除指定外所有窗�?若指定窗口未打开则同时打开�?。`CurrentMenuGroup` 变量记录当前所在菜单组(0=主菜�?1=单�
�操作/2=监控诊断/3=系统)�?

### 脚本 M1:主菜�?�?总览按钮

- **编号**: M1
- **用�?*: 从主菜单进�
�画面1_总览
- **位置**: 用户窗口 �?菜单_主菜�?�?btnOverview 构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 主菜�?- 总览按钮脚本
' 功能: 切换到画�?_总览
' ============================================

CurrentMenuGroup = 0
!CloseAllWindow("画面1_总览")
```

### 脚本 M2:主菜�?�?单�
�操作按钮

- **编号**: M2
- **用�?*: 从主菜单进�
�菜单_单�
�操作子菜�?
- **位置**: 用户窗口 �?菜单_主菜�?�?btnUnitOps 构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 主菜�?- 单�
�操作按钮脚本
' 功能: 切换到菜单_单�
�操作子菜�?
' ============================================

CurrentMenuGroup = 1
!CloseAllWindow("菜单_单�
�操作")
```

### 脚本 M3:主菜�?�?监控诊断按钮

- **编号**: M3
- **用�?*: 从主菜单进�
�菜单_监控诊断子菜�?
- **位置**: 用户窗口 �?菜单_主菜�?�?btnDiag 构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 主菜�?- 监控诊断按钮脚本
' 功能: 切换到菜单_监控诊断子菜�?
' ============================================

CurrentMenuGroup = 2
!CloseAllWindow("菜单_监控诊断")
```

### 脚本 M4:主菜�?�?系统按钮

- **编号**: M4
- **用�?*: 从主菜单进�
�菜单_系统子菜�?
- **位置**: 用户窗口 �?菜单_主菜�?�?btnSystem 构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 主菜�?- 系统按钮脚本
' 功能: 切换到菜单_系统子菜�?
' ============================================

CurrentMenuGroup = 3
!CloseAllWindow("菜单_系统")
```

### 脚本 M5:菜单_单�
�操作 �?画面按钮(详�
/手动/参数)

- **编号**: M5
- **用�?*: 从子菜单进�
�对应业务画面
- **位置**: 用户窗口 �?菜单_单�
�操作 �?btnDetail / btnManual / btnParam 构件 �?Click 事件
- **触发方式**: 按钮单击

**详�
按钮(btnDetail)**:
```
' ============================================
' 子菜�?- 详�
按钮脚本
' 功能: 切换到画�?_单�
�详�

' ============================================

!CloseAllWindow("画面2_单�
�详�
")
```

**手动按钮(btnManual)**:
```
' ============================================
' 子菜�?- 手动按钮脚本
' 功能: 切换到画�?_手动控制
' ============================================

!CloseAllWindow("画面3_手动控制")
```

**参数按钮(btnParam)**:
```
' ============================================
' 子菜�?- 参数按钮脚本
' 功能: 切换到画�?_参数设置
' ============================================

!CloseAllWindow("画面4_参数设置")
```

### 脚本 M6:菜单_监控诊断 �?画面按钮(报警/趋势/通讯)

- **编号**: M6
- **用�?*: 从子菜单进�
�对应业务画面
- **位置**: 用户窗口 �?菜单_监控诊断 �?btnAlarm / btnTrend / btnComm 构件 �?Click 事件
- **触发方式**: 按钮单击

**报警按钮(btnAlarm)**:
```
' ============================================
' 子菜�?- 报警按钮脚本
' 功能: 切换到画�?_报警日志
' ============================================

!CloseAllWindow("画面5_报警日志")
```

**趋势按钮(btnTrend)**:
```
' ============================================
' 子菜�?- 趋势按钮脚本
' 功能: 切换到画�?_趋势曲线
' ============================================

!CloseAllWindow("画面6_趋势曲线")
```

**通讯按钮(btnComm)**:
```
' ============================================
' 子菜�?- 通讯按钮脚本
' 功能: 切换到画�?_通讯维护
' ============================================

!CloseAllWindow("画面7_通讯维护")
```

### 脚本 M7:菜单_系统 �?画面按钮(单�
�使能/权限管理)

- **编号**: M7
- **用�?*: 从子菜单进�
�对应业务画面
- **位置**: 用户窗口 �?菜单_系统 �?btnEnConfig / btnUserMgmt 构件 �?Click 事件
- **触发方式**: 按钮单击

**单�
�使能按钮(btnEnConfig)**:
```
' ============================================
' 子菜�?- 单�
�使能按钮脚本
' 功能: 切换到画�?a_单�
�使能
' ============================================

!CloseAllWindow("画面8a_单�
�使能")
```

**权限管理按钮(btnUserMgmt)**:
```
' ============================================
' 子菜�?- 权限管理按钮脚本
' 功能: 切换到画�?b_权限管理
' ============================================

!CloseAllWindow("画面8b_权限管理")
```

### 脚本 M8:子菜单返回主菜单(菜单_单�
�操作/监控诊断/系统通用)

- **编号**: M8
- **用�?*: 从任意子菜单返回主菜�?
- **位置**: 用户窗口 �?菜单_单�
�操作 / 菜单_监控诊断 / 菜单_系统 �?btnBack 构件 �?Click 事件(3个子菜单�
�用相同脚本)
- **触发方式**: 按钮单击

```
' ============================================
' 子菜�?- 返回主菜单脚�?
' 功能: �
�闭当前子菜�?返回菜单_主菜�?
' ============================================

CurrentMenuGroup = 0
!CloseAllWindow("菜单_主菜�?)
```

---

## 三、C. 画面1_总览脚本

### 脚本 4:画面1 窗口打开脚本

- **编号**: 4
- **用�?*: 初始化画�?变量,�
�闭所有子窗口,刷新8单�
�卡片状�?
- **位置**: 用户窗口 �?画面1_总览 �?Load 事件
- **触发方式**: 窗口�
载�?

```
' ============================================
' 画面1_总览 Load 脚本
' 功能: �
�闭残留子窗�?+ 刷新总览显示
' ============================================

' --- 1. �
�闭所有子窗口(防止跨画面残�? ---
!CloseAllSubWnd()

' --- 2. 初始化选中单�
��?(未选中) ---
SelectedUnit = 0

' --- 3. 更新系统时间显示 ---
SysTimeString = $Date + " " + $Time

' --- 4. 刷新�
�局报警/消音状�?�?00ms周期策略持续更新,此处只读) ---
' GlobalAlarmActive / GlobalMuteState 由周期策略维�?
```

### 脚本 5:1号单�
�卡片点�?

- **编号**: 5
- **用�?*: 点击1号单�
�卡�?设置 SelectedUnit=1,打开画面2_单�
�详�
子窗�?
- **位置**: 用户窗口 �?画面1_总览 �?1号单�
�卡片构�?�?Click 事件
- **触发方式**: 卡片鼠标单击

```
' ============================================
' 1号单�
�卡片点击脚�?
' 功能: �
在使能+在线时�
�许进�
�详�
页
' ============================================

' --- 1. 检查单�
�使�?在线状�?---
If U1_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U1_Online = 0 Then
    !Beep()
    Exit
EndIf

' --- 2. 设置选中单�
��?---
SelectedUnit = 1

' --- 3. �
�闭所有子窗口,打开画面2_单�
�详�
 ---
!CloseAllSubWnd()
!CloseAllWindow("画面2_单�
�详�
")
```

### 脚本 6:2~8号单�
�卡片点�?合并写法)

- **编号**: 6
- **用�?*: 2~8号单�
�卡片点�?逻辑同脚�?,�
单�
�号不同
- **位置**: 用户窗口 �?画面1_总览 �?2~8号单�
�卡片构�?�?Click 事件(7个独立脚�?
- **触发方式**: 卡片鼠标单击
- **扩展方法**: 将脚�?中的 `U1_Enable` / `U1_Online` / `SelectedUnit = 1` 替换为对应单�
�号

**2号单�
�卡片点�?*:
```
If U2_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U2_Online = 0 Then
    !Beep()
    Exit
EndIf
SelectedUnit = 2
!CloseAllSubWnd()
!CloseAllWindow("画面2_单�
�详�
")
```

**3号单�
�卡片点�?*:
```
If U3_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U3_Online = 0 Then
    !Beep()
    Exit
EndIf
SelectedUnit = 3
!CloseAllSubWnd()
!CloseAllWindow("画面2_单�
�详�
")
```

**4号单�
�卡片点�?*:
```
If U4_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U4_Online = 0 Then
    !Beep()
    Exit
EndIf
SelectedUnit = 4
!CloseAllSubWnd()
!CloseAllWindow("画面2_单�
�详�
")
```

**5号单�
�卡片点�?*:
```
If U5_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U5_Online = 0 Then
    !Beep()
    Exit
EndIf
SelectedUnit = 5
!CloseAllSubWnd()
!CloseAllWindow("画面2_单�
�详�
")
```

**6号单�
�卡片点�?*:
```
If U6_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U6_Online = 0 Then
    !Beep()
    Exit
EndIf
SelectedUnit = 6
!CloseAllSubWnd()
!CloseAllWindow("画面2_单�
�详�
")
```

**7号单�
�卡片点�?*:
```
If U7_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U7_Online = 0 Then
    !Beep()
    Exit
EndIf
SelectedUnit = 7
!CloseAllSubWnd()
!CloseAllWindow("画面2_单�
�详�
")
```

**8号单�
�卡片点�?*:
```
If U8_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U8_Online = 0 Then
    !Beep()
    Exit
EndIf
SelectedUnit = 8
!CloseAllSubWnd()
!CloseAllWindow("画面2_单�
�详�
")
```

### 脚本 7:�
�局消音按钮

- **编号**: 7
- **用�?*: 对所有使�?在线单�
�下发消音命令(直接执行,无需二次确认)
- **位置**: 用户窗口 �?画面1_总览 �?�
�局消音按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' �
�局消音按钮脚本
' 功能: 对所有使�?在线单�
��?CMD_Mute=1 (500ms周期策略会自动�
�?
' ============================================

' --- 1. 蜂鸣提示 ---
!Beep()

' --- 2. �?个使�?在线单�
�下发消音命令 ---
If U1_Enable = 1 Then
    If U1_Online = 1 Then
        U1_CMD_Mute = 1
    EndIf
EndIf
If U2_Enable = 1 Then
    If U2_Online = 1 Then
        U2_CMD_Mute = 1
    EndIf
EndIf
If U3_Enable = 1 Then
    If U3_Online = 1 Then
        U3_CMD_Mute = 1
    EndIf
EndIf
If U4_Enable = 1 Then
    If U4_Online = 1 Then
        U4_CMD_Mute = 1
    EndIf
EndIf
If U5_Enable = 1 Then
    If U5_Online = 1 Then
        U5_CMD_Mute = 1
    EndIf
EndIf
If U6_Enable = 1 Then
    If U6_Online = 1 Then
        U6_CMD_Mute = 1
    EndIf
EndIf
If U7_Enable = 1 Then
    If U7_Online = 1 Then
        U7_CMD_Mute = 1
    EndIf
EndIf
If U8_Enable = 1 Then
    If U8_Online = 1 Then
        U8_CMD_Mute = 1
    EndIf
EndIf

' --- 3. 更新�
�局消音状�?---
GlobalMuteState = 1
```

### 脚本 8:�
�局报警确认按钮

- **编号**: 8
- **用�?*: 对所有使�?在线单�
�下发报警确认命令(直接执行)
- **位置**: 用户窗口 �?画面1_总览 �?�
�局报警确认按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' �
�局报警确认按钮脚本
' 功能: 对所有使�?在线单�
��?CMD_AckAlarm=1
' 注意: �
确认当前激活报�?不影响历史日�?
' ============================================

' --- 1. 蜂鸣提示 ---
!Beep()

' --- 2. �?个使�?在线单�
�下发报警确认命令 ---
If U1_Enable = 1 Then
    If U1_Online = 1 Then
        U1_CMD_AckAlarm = 1
    EndIf
EndIf
If U2_Enable = 1 Then
    If U2_Online = 1 Then
        U2_CMD_AckAlarm = 1
    EndIf
EndIf
If U3_Enable = 1 Then
    If U3_Online = 1 Then
        U3_CMD_AckAlarm = 1
    EndIf
EndIf
If U4_Enable = 1 Then
    If U4_Online = 1 Then
        U4_CMD_AckAlarm = 1
    EndIf
EndIf
If U5_Enable = 1 Then
    If U5_Online = 1 Then
        U5_CMD_AckAlarm = 1
    EndIf
EndIf
If U6_Enable = 1 Then
    If U6_Online = 1 Then
        U6_CMD_AckAlarm = 1
    EndIf
EndIf
If U7_Enable = 1 Then
    If U7_Online = 1 Then
        U7_CMD_AckAlarm = 1
    EndIf
EndIf
If U8_Enable = 1 Then
    If U8_Online = 1 Then
        U8_CMD_AckAlarm = 1
    EndIf
EndIf

' --- 3. 更新�
�局确认状�?---
GlobalAckPending = 0
```

### 脚本 9:急停按钮

- **编号**: 9
- **用�?*: 急停按钮,弹出二次确认子窗�?确认后对8个单�
�下�?CMD_Stop=1
- **位置**: 用户窗口 �?画面1_总览 �?急停按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 急停按钮脚本
' 功能: 弹出急停确认子窗�?脚本52负责执行)
' 子窗口模�? 模�?1) + 边框(16) = 17
' ============================================

' --- 1. 蜂鸣强提�?---
!Beep()

' --- 2. 打开急停确认子窗�?模�?边框,�
中位置 240,180,400,180) ---
!OpenSubWnd(子窗口_急停确认, 240, 180, 400, 180, 17)
```

---

## 四、D. 画面2_单�
�详�
脚本

### 脚本 10:画面2 窗口打开脚本

- **编号**: 10
- **用�?*: 根据 SelectedUnit 加载对应单�
�的数�?显示"当前操作:X号单�
?
- **位置**: 用户窗口 �?画面2_单�
�详�
 �?Load 事件
- **触发方式**: 窗口�
载�?

```
' ============================================
' 画面2_单�
�详�
 Load 脚本
' 功能: 根据 SelectedUnit 切换数据绑定上下�?
' 注意: McgsPro 不支持动态变量名,构件的数据绑定通过组态时
'       �?表达�?引用 SelectedUnit 选择显示,或用8套独立组�?显隐切换
' ============================================

' --- 1. �
�闭残留子窗�?---
!CloseAllSubWnd()

' --- 2. 校验 SelectedUnit 范围(1~8) ---
If SelectedUnit < 1 Then
    !CloseAllWindow("菜单_主菜�?)
    Exit
EndIf
If SelectedUnit > 8 Then
    !CloseAllWindow("菜单_主菜�?)
    Exit
EndIf

' --- 3. 拼接当前操作字符�?---
If SelectedUnit = 1 Then
    CurrentUnitStr = "当前操作:1号单�
?
EndIf
If SelectedUnit = 2 Then
    CurrentUnitStr = "当前操作:2号单�
?
EndIf
If SelectedUnit = 3 Then
    CurrentUnitStr = "当前操作:3号单�
?
EndIf
If SelectedUnit = 4 Then
    CurrentUnitStr = "当前操作:4号单�
?
EndIf
If SelectedUnit = 5 Then
    CurrentUnitStr = "当前操作:5号单�
?
EndIf
If SelectedUnit = 6 Then
    CurrentUnitStr = "当前操作:6号单�
?
EndIf
If SelectedUnit = 7 Then
    CurrentUnitStr = "当前操作:7号单�
?
EndIf
If SelectedUnit = 8 Then
    CurrentUnitStr = "当前操作:8号单�
?
EndIf

' --- 4. 更新系统时间显示 ---
SysTimeString = $Date + " " + $Time
```

### 脚本 11:启动按钮

- **编号**: 11
- **用�?*: 启动当前选中单�
�(需维护组权�?二次确认)
- **位置**: 用户窗口 �?画面2_单�
�详�
 �?启动按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 启动按钮脚本
' 功能: 权限校验 �?打开启动确认子窗�?脚本50负责执行)
' ============================================

' --- 1. 校验维护组权�?L2以上) ---
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 打开启动确认子窗�?模�?边框) ---
!OpenSubWnd(子窗口_启动确认, 240, 180, 400, 180, 17)
```

### 脚本 12:停止按钮

- **编号**: 12
- **用�?*: 停止当前选中单�
�(二次确认子窗�?
- **位置**: 用户窗口 �?画面2_单�
�详�
 �?停止按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 停止按钮脚本
' 功能: 弹出停止确认子窗�?脚本51负责执行)
' ============================================

' --- 1. 蜂鸣提示 ---
!Beep()

' --- 2. 打开停止确认子窗�?模�?边框) ---
!OpenSubWnd(子窗口_停止确认, 240, 180, 400, 180, 17)
```

### 脚本 13:报警确认按钮

- **编号**: 13
- **用�?*: 对当前选中单�
�下发报警确认命令
- **位置**: 用户窗口 �?画面2_单�
�详�
 �?报警确认按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 报警确认按钮脚本(以当前选中单�
�为例)
' 功能: �?SelectedUnit 对应单�
��?CMD_AckAlarm=1
' ============================================

!Beep()

If SelectedUnit = 1 Then
    U1_CMD_AckAlarm = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_AckAlarm = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_AckAlarm = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_AckAlarm = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_AckAlarm = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_AckAlarm = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_AckAlarm = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_AckAlarm = 1
EndIf
```

### 脚本 14:消音按钮

- **编号**: 14
- **用�?*: 对当前选中单�
�下发消音命令
- **位置**: 用户窗口 �?画面2_单�
�详�
 �?消音按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 消音按钮脚本
' 功能: �?SelectedUnit 对应单�
��?CMD_Mute=1
' ============================================

!Beep()

If SelectedUnit = 1 Then
    U1_CMD_Mute = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Mute = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Mute = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Mute = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Mute = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Mute = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Mute = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Mute = 1
EndIf

GlobalMuteState = 1
```

### 脚本 15:手动控制按钮

- **编号**: 15
- **用�?*: 打开画面3_手动控制子窗�?需维护组权�?
- **位置**: 用户窗口 �?画面2_单�
�详�
 �?手动控制按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 手动控制按钮脚本
' 功能: 权限校验(L2维护�? �?打开画面3_手动控制子窗�?
' ============================================

' --- 1. 校验维护组权�?---
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 打开画面3_手动控制子窗�?模�?边框,800x600) ---
!OpenSubWnd(画面3_手动控制, 80, 60, 800, 600, 17)
```

### 脚本 16:参数设置按钮

- **编号**: 16
- **用�?*: 打开画面4_参数设置子窗�?需维护组权�?
- **位置**: 用户窗口 �?画面2_单�
�详�
 �?参数设置按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 参数设置按钮脚本
' 功能: 权限校验(L2维护�? �?打开画面4_参数设置子窗�?
' ============================================

' --- 1. 校验维护组权�?---
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 打开画面4_参数设置子窗�?模�?边框,800x600) ---
!OpenSubWnd(画面4_参数设置, 80, 60, 800, 600, 17)
```

### 脚本 17:返回按钮

- **编号**: 17
- **用�?*: �
�闭所有子窗口,返回菜单_单�
�操作(v2.1改为两级菜单)
- **位置**: 用户窗口 �?画面2_单�
�详�
 �?返回按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本
' 功能: �
�闭所有子窗口,�
�闭当前画面,返回菜单_单�
�操作
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("菜单_单�
�操作")
```

---

## 五、E. 画面3_手动控制脚本

### 脚本 18:画面3 窗口打开脚本

- **编号**: 18
- **用�?*: 初始化手动控制画�?显示当前选中单�
�
- **位置**: 用户窗口 �?画面3_手动控制 �?Load 事件
- **触发方式**: 子窗口�
载时

```
' ============================================
' 画面3_手动控制 Load 脚本
' 功能: 显示"当前操作:X号单�
?手动模式)"
' ============================================

If SelectedUnit = 1 Then
    CurrentUnitStr = "当前操作:1号单�
?(手动模式)"
EndIf
If SelectedUnit = 2 Then
    CurrentUnitStr = "当前操作:2号单�
?(手动模式)"
EndIf
If SelectedUnit = 3 Then
    CurrentUnitStr = "当前操作:3号单�
?(手动模式)"
EndIf
If SelectedUnit = 4 Then
    CurrentUnitStr = "当前操作:4号单�
?(手动模式)"
EndIf
If SelectedUnit = 5 Then
    CurrentUnitStr = "当前操作:5号单�
?(手动模式)"
EndIf
If SelectedUnit = 6 Then
    CurrentUnitStr = "当前操作:6号单�
?(手动模式)"
EndIf
If SelectedUnit = 7 Then
    CurrentUnitStr = "当前操作:7号单�
?(手动模式)"
EndIf
If SelectedUnit = 8 Then
    CurrentUnitStr = "当前操作:8号单�
?(手动模式)"
EndIf
```

### 脚本 19:阀A 手动开/�
?

- **编号**: 19
- **用�?*: 手动开/�
�阀A(需维护组权�?。开按钮�?CMD_Manual_ValveA_Open=1,�
�按钮置 CMD_Manual_ValveA_Close=1
- **位置**: 用户窗口 �?画面3_手动控制 �?阀A开按钮 / 阀A�
�按�?�?Click 事件
- **触发方式**: 按钮单击

**阀A 开按钮**(以当前选中单�
�为例):
```
' --- 1. 校验维护组权�?---
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. �?CMD_Manual_ValveA_Open=1 ---
If SelectedUnit = 1 Then
    U1_CMD_Manual_ValveA_Open = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_ValveA_Open = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_ValveA_Open = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_ValveA_Open = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_ValveA_Open = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_ValveA_Open = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_ValveA_Open = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_ValveA_Open = 1
EndIf

!Beep()
```

**阀A �
�按�?*(以当前选中单�
�为例):
```
' --- 1. 校验维护组权�?---
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. �?CMD_Manual_ValveA_Close=1 ---
If SelectedUnit = 1 Then
    U1_CMD_Manual_ValveA_Close = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_ValveA_Close = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_ValveA_Close = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_ValveA_Close = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_ValveA_Close = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_ValveA_Close = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_ValveA_Close = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_ValveA_Close = 1
EndIf

!Beep()
```

### 脚本 20:阀B 手动开/�
?

- **编号**: 20
- **用�?*: 手动开/�
�阀B(需维护组权�?
- **位置**: 用户窗口 �?画面3_手动控制 �?阀B开按钮 / 阀B�
�按�?�?Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 将脚�?9中的 `CMD_Manual_ValveA_Open/Close` 替换�?`CMD_Manual_ValveB_Open/Close`

**阀B 开按钮**:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_CMD_Manual_ValveB_Open = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_ValveB_Open = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_ValveB_Open = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_ValveB_Open = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_ValveB_Open = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_ValveB_Open = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_ValveB_Open = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_ValveB_Open = 1
EndIf

!Beep()
```

**阀B �
�按�?*:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_CMD_Manual_ValveB_Close = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_ValveB_Close = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_ValveB_Close = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_ValveB_Close = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_ValveB_Close = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_ValveB_Close = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_ValveB_Close = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_ValveB_Close = 1
EndIf

!Beep()
```

### 脚本 21:阀C 手动开/�
?

- **编号**: 21
- **用�?*: 手动开/�
�阀C(需维护组权�?
- **位置**: 用户窗口 �?画面3_手动控制 �?阀C开按钮 / 阀C�
�按�?�?Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 将脚�?9中的 `CMD_Manual_ValveA_Open/Close` 替换�?`CMD_Manual_ValveC_Open/Close`

**阀C 开按钮**:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_CMD_Manual_ValveC_Open = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_ValveC_Open = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_ValveC_Open = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_ValveC_Open = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_ValveC_Open = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_ValveC_Open = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_ValveC_Open = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_ValveC_Open = 1
EndIf

!Beep()
```

**阀C �
�按�?*:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_CMD_Manual_ValveC_Close = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_ValveC_Close = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_ValveC_Close = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_ValveC_Close = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_ValveC_Close = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_ValveC_Close = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_ValveC_Close = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_ValveC_Close = 1
EndIf

!Beep()
```

### 脚本 22:�? 手动开/�
?

- **编号**: 22
- **用�?*: 手动开/�
�潜水泵1(需维护组权�?
- **位置**: 用户窗口 �?画面3_手动控制 �?�?开按钮 / �?�
�按�?�?Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 将脚�?9中的 `CMD_Manual_ValveA_Open/Close` 替换�?`CMD_Manual_Pump1_On/Off`

**�? 开按钮**:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_CMD_Manual_Pump1_On = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_Pump1_On = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_Pump1_On = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_Pump1_On = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_Pump1_On = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_Pump1_On = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_Pump1_On = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_Pump1_On = 1
EndIf

!Beep()
```

**�? �
�按�?*:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_CMD_Manual_Pump1_Off = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_Pump1_Off = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_Pump1_Off = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_Pump1_Off = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_Pump1_Off = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_Pump1_Off = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_Pump1_Off = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_Pump1_Off = 1
EndIf

!Beep()
```

### 脚本 23:�? 手动开/�
?

- **编号**: 23
- **用�?*: 手动开/�
�潜水泵2(需维护组权�?
- **位置**: 用户窗口 �?画面3_手动控制 �?�?开按钮 / �?�
�按�?�?Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 将脚�?2中的 `CMD_Manual_Pump1_On/Off` 替换�?`CMD_Manual_Pump2_On/Off`

**�? 开按钮**:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_CMD_Manual_Pump2_On = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_Pump2_On = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_Pump2_On = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_Pump2_On = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_Pump2_On = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_Pump2_On = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_Pump2_On = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_Pump2_On = 1
EndIf

!Beep()
```

**�? �
�按�?*:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_CMD_Manual_Pump2_Off = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Manual_Pump2_Off = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Manual_Pump2_Off = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Manual_Pump2_Off = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Manual_Pump2_Off = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Manual_Pump2_Off = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Manual_Pump2_Off = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Manual_Pump2_Off = 1
EndIf

!Beep()
```

### 脚本 24:注射�?抽液/排液

- **编号**: 24
- **用�?*: 注射泵抽�?排液(需维护组权�?
- **位置**: 用户窗口 �?画面3_手动控制 �?抽液按钮 / 排液按钮 �?Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 抽液�?`MB_Pump_Aspirate`,排液�?`MB_Pump_Dispense`

**抽液按钮**:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_MB_Pump_Aspirate = 1
EndIf
If SelectedUnit = 2 Then
    U2_MB_Pump_Aspirate = 1
EndIf
If SelectedUnit = 3 Then
    U3_MB_Pump_Aspirate = 1
EndIf
If SelectedUnit = 4 Then
    U4_MB_Pump_Aspirate = 1
EndIf
If SelectedUnit = 5 Then
    U5_MB_Pump_Aspirate = 1
EndIf
If SelectedUnit = 6 Then
    U6_MB_Pump_Aspirate = 1
EndIf
If SelectedUnit = 7 Then
    U7_MB_Pump_Aspirate = 1
EndIf
If SelectedUnit = 8 Then
    U8_MB_Pump_Aspirate = 1
EndIf

!Beep()
```

**排液按钮**:
```
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_MB_Pump_Dispense = 1
EndIf
If SelectedUnit = 2 Then
    U2_MB_Pump_Dispense = 1
EndIf
If SelectedUnit = 3 Then
    U3_MB_Pump_Dispense = 1
EndIf
If SelectedUnit = 4 Then
    U4_MB_Pump_Dispense = 1
EndIf
If SelectedUnit = 5 Then
    U5_MB_Pump_Dispense = 1
EndIf
If SelectedUnit = 6 Then
    U6_MB_Pump_Dispense = 1
EndIf
If SelectedUnit = 7 Then
    U7_MB_Pump_Dispense = 1
EndIf
If SelectedUnit = 8 Then
    U8_MB_Pump_Dispense = 1
EndIf

!Beep()
```

### 脚本 25:复位按钮

- **编号**: 25
- **用�?*: 手动复位(需管理员组权限)
- **位置**: 用户窗口 �?画面3_手动控制 �?复位按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 复位按钮脚本
' 功能: 校验管理员组权限 �?对选中单�
��?MB_Pump_Reset=1
' ============================================

' --- 1. 校验管理员组权限(L3) ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. �?MB_Pump_Reset=1 ---
If SelectedUnit = 1 Then
    U1_MB_Pump_Reset = 1
EndIf
If SelectedUnit = 2 Then
    U2_MB_Pump_Reset = 1
EndIf
If SelectedUnit = 3 Then
    U3_MB_Pump_Reset = 1
EndIf
If SelectedUnit = 4 Then
    U4_MB_Pump_Reset = 1
EndIf
If SelectedUnit = 5 Then
    U5_MB_Pump_Reset = 1
EndIf
If SelectedUnit = 6 Then
    U6_MB_Pump_Reset = 1
EndIf
If SelectedUnit = 7 Then
    U7_MB_Pump_Reset = 1
EndIf
If SelectedUnit = 8 Then
    U8_MB_Pump_Reset = 1
EndIf

!Beep()
```

### 脚本 26:返回按钮

- **编号**: 26
- **用�?*: �
�闭手动控制画面,返回菜单_单�
�操作(v2.1改为两级菜单)
- **位置**: 用户窗口 �?画面3_手动控制 �?返回按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面3)
' 功能: �
�闭当前画面,返回菜单_单�
�操作
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("菜单_单�
�操作")
```

---

## �
�、F. 画面4_参数设置脚本

### 脚本 27:画面4 窗口打开脚本

- **编号**: 27
- **用�?*: 加载当前选中单�
�的参数到编辑缓冲�?
- **位置**: 用户窗口 �?画面4_参数设置 �?Load 事件
- **触发方式**: 子窗口�
载时

```
' ============================================
' 画面4_参数设置 Load 脚本
' 功能: �?SelectedUnit 对应单�
��?VD 参数读到编辑缓冲变量
'       (供输�
�框编辑,保存时由脚本28写回 PLC)
' 注意: 浓度组参�?VD10/VD14)�
管理员可见可改,这里统一加载,
'       组态时通过权限位隐藏浓度输�
�框
' ============================================

If SelectedUnit = 1 Then
    Param_StepRes = U1_VD_StepResolution
    Param_24h_Target = U1_VD_24h_Target
' [v2.2 added Transfer/Safety]
Param_Transfer_Margin = U1_VD_Transfer_Margin
Param_Safety_Margin = U1_VD_Safety_Margin
    Param_ExpTarget = U1_VD_ExperimentTarget
    Param_PreMixTime = U1_VD_PreMixTime
' [v2.2 removed Param_PreMixTime_MinSafe]
' [v2.2 removed Param_RestTime]
' [v2.2 removed Param_RestTime_Min]
' [v2.2 removed Param_CycleExtend_Max]
    Param_Timeout_ValveA = U1_VD_Timeout_ValveA
    Param_Timeout_ValveB = U1_VD_Timeout_ValveB
    Param_Timeout_ValveC = U1_VD_Timeout_ValveC
    Param_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 2 Then
    Param_StepRes = U2_VD_StepResolution
    Param_24h_Target = U2_VD_24h_Target
' [v2.2 added Transfer/Safety]
Param_Transfer_Margin = U2_VD_Transfer_Margin
Param_Safety_Margin = U2_VD_Safety_Margin
    Param_ExpTarget = U2_VD_ExperimentTarget
    Param_PreMixTime = U2_VD_PreMixTime
' [v2.2 removed Param_PreMixTime_MinSafe]
' [v2.2 removed Param_RestTime]
' [v2.2 removed Param_RestTime_Min]
' [v2.2 removed Param_CycleExtend_Max]
    Param_Timeout_ValveA = U2_VD_Timeout_ValveA
    Param_Timeout_ValveB = U2_VD_Timeout_ValveB
    Param_Timeout_ValveC = U2_VD_Timeout_ValveC
    Param_Delay_ValveA_Verify = U2_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 3 Then
    Param_StepRes = U3_VD_StepResolution
    Param_24h_Target = U3_VD_24h_Target
' [v2.2 added Transfer/Safety]
Param_Transfer_Margin = U3_VD_Transfer_Margin
Param_Safety_Margin = U3_VD_Safety_Margin
    Param_ExpTarget = U3_VD_ExperimentTarget
    Param_PreMixTime = U3_VD_PreMixTime
' [v2.2 removed Param_PreMixTime_MinSafe]
' [v2.2 removed Param_RestTime]
' [v2.2 removed Param_RestTime_Min]
' [v2.2 removed Param_CycleExtend_Max]
    Param_Timeout_ValveA = U3_VD_Timeout_ValveA
    Param_Timeout_ValveB = U3_VD_Timeout_ValveB
    Param_Timeout_ValveC = U3_VD_Timeout_ValveC
    Param_Delay_ValveA_Verify = U3_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 4 Then
    Param_StepRes = U4_VD_StepResolution
    Param_24h_Target = U4_VD_24h_Target
' [v2.2 added Transfer/Safety]
Param_Transfer_Margin = U4_VD_Transfer_Margin
Param_Safety_Margin = U4_VD_Safety_Margin
    Param_ExpTarget = U4_VD_ExperimentTarget
    Param_PreMixTime = U4_VD_PreMixTime
' [v2.2 removed Param_PreMixTime_MinSafe]
' [v2.2 removed Param_RestTime]
' [v2.2 removed Param_RestTime_Min]
' [v2.2 removed Param_CycleExtend_Max]
    Param_Timeout_ValveA = U4_VD_Timeout_ValveA
    Param_Timeout_ValveB = U4_VD_Timeout_ValveB
    Param_Timeout_ValveC = U4_VD_Timeout_ValveC
    Param_Delay_ValveA_Verify = U4_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 5 Then
    Param_StepRes = U5_VD_StepResolution
    Param_24h_Target = U5_VD_24h_Target
' [v2.2 added Transfer/Safety]
Param_Transfer_Margin = U5_VD_Transfer_Margin
Param_Safety_Margin = U5_VD_Safety_Margin
    Param_ExpTarget = U5_VD_ExperimentTarget
    Param_PreMixTime = U5_VD_PreMixTime
' [v2.2 removed Param_PreMixTime_MinSafe]
' [v2.2 removed Param_RestTime]
' [v2.2 removed Param_RestTime_Min]
' [v2.2 removed Param_CycleExtend_Max]
    Param_Timeout_ValveA = U5_VD_Timeout_ValveA
    Param_Timeout_ValveB = U5_VD_Timeout_ValveB
    Param_Timeout_ValveC = U5_VD_Timeout_ValveC
    Param_Delay_ValveA_Verify = U5_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 6 Then
    Param_StepRes = U6_VD_StepResolution
    Param_24h_Target = U6_VD_24h_Target
' [v2.2 added Transfer/Safety]
Param_Transfer_Margin = U6_VD_Transfer_Margin
Param_Safety_Margin = U6_VD_Safety_Margin
    Param_ExpTarget = U6_VD_ExperimentTarget
    Param_PreMixTime = U6_VD_PreMixTime
' [v2.2 removed Param_PreMixTime_MinSafe]
' [v2.2 removed Param_RestTime]
' [v2.2 removed Param_RestTime_Min]
' [v2.2 removed Param_CycleExtend_Max]
    Param_Timeout_ValveA = U6_VD_Timeout_ValveA
    Param_Timeout_ValveB = U6_VD_Timeout_ValveB
    Param_Timeout_ValveC = U6_VD_Timeout_ValveC
    Param_Delay_ValveA_Verify = U6_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 7 Then
    Param_StepRes = U7_VD_StepResolution
    Param_24h_Target = U7_VD_24h_Target
' [v2.2 added Transfer/Safety]
Param_Transfer_Margin = U7_VD_Transfer_Margin
Param_Safety_Margin = U7_VD_Safety_Margin
    Param_ExpTarget = U7_VD_ExperimentTarget
    Param_PreMixTime = U7_VD_PreMixTime
' [v2.2 removed Param_PreMixTime_MinSafe]
' [v2.2 removed Param_RestTime]
' [v2.2 removed Param_RestTime_Min]
' [v2.2 removed Param_CycleExtend_Max]
    Param_Timeout_ValveA = U7_VD_Timeout_ValveA
    Param_Timeout_ValveB = U7_VD_Timeout_ValveB
    Param_Timeout_ValveC = U7_VD_Timeout_ValveC
    Param_Delay_ValveA_Verify = U7_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 8 Then
    Param_StepRes = U8_VD_StepResolution
    Param_24h_Target = U8_VD_24h_Target
' [v2.2 added Transfer/Safety]
Param_Transfer_Margin = U8_VD_Transfer_Margin
Param_Safety_Margin = U8_VD_Safety_Margin
    Param_ExpTarget = U8_VD_ExperimentTarget
    Param_PreMixTime = U8_VD_PreMixTime
' [v2.2 removed Param_PreMixTime_MinSafe]
' [v2.2 removed Param_RestTime]
' [v2.2 removed Param_RestTime_Min]
' [v2.2 removed Param_CycleExtend_Max]
    Param_Timeout_ValveA = U8_VD_Timeout_ValveA
    Param_Timeout_ValveB = U8_VD_Timeout_ValveB
    Param_Timeout_ValveC = U8_VD_Timeout_ValveC
    Param_Delay_ValveA_Verify = U8_VD_Delay_ValveA_Verify
EndIf

ParamTargetUnit = SelectedUnit
```

### 脚本 28:保存参数按钮

- **编号**: 28
- **用�?*: 校验参数范围 �?写�
�选中单�
��?VD 参数(需维护组权�?浓度组需管理�?
- **位置**: 用户窗口 �?画面4_参数设置 �?保存参数按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 保存参数按钮脚本
' 功能: 1.校验维护组权�?2.范围校验 3.写回 PLC
' 依赖脚本31: 参数范围校验(本脚本调用前应�
�执行校验,这里再次�
�底)
' ============================================

' --- 1. 校验维护组权�?---
If !CheckUserGroup("维护�?) = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 范围校验(完整规则见脚�?1,此处�
�
�键项) ---
' 浓度参数已移�?
    !Beep()
    Exit
EndIf
    !Beep()
    Exit
EndIf
' 预循环最小安�
�值约�?
' 静止时间约束
' �
时�
须>0
If Param_Timeout_ValveA <= 0 Then
    !Beep()
    Exit
EndIf
If Param_Timeout_ValveB <= 0 Then
    !Beep()
    Exit
EndIf
If Param_Timeout_ValveC <= 0 Then
    !Beep()
    Exit
EndIf

' --- 4. 写回 PLC (�?SelectedUnit 选择目标) ---
If SelectedUnit = 1 Then
    U1_VD_StepResolution = Param_StepRes
    U1_VD_24h_Target = Param_24h_Target
    U1_VD_ExperimentTarget = Param_ExpTarget
    U1_VD_PreMixTime = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U1_VD_Timeout_ValveA = Param_Timeout_ValveA
    U1_VD_Timeout_ValveB = Param_Timeout_ValveB
    U1_VD_Timeout_ValveC = Param_Timeout_ValveC
    U1_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 2 Then
    U2_VD_StepResolution = Param_StepRes
    U2_VD_24h_Target = Param_24h_Target
    U2_VD_ExperimentTarget = Param_ExpTarget
    U2_VD_PreMixTime = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U2_VD_Timeout_ValveA = Param_Timeout_ValveA
    U2_VD_Timeout_ValveB = Param_Timeout_ValveB
    U2_VD_Timeout_ValveC = Param_Timeout_ValveC
    U2_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 3 Then
    U3_VD_StepResolution = Param_StepRes
    U3_VD_24h_Target = Param_24h_Target
    U3_VD_ExperimentTarget = Param_ExpTarget
    U3_VD_PreMixTime = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U3_VD_Timeout_ValveA = Param_Timeout_ValveA
    U3_VD_Timeout_ValveB = Param_Timeout_ValveB
    U3_VD_Timeout_ValveC = Param_Timeout_ValveC
    U3_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 4 Then
    U4_VD_StepResolution = Param_StepRes
    U4_VD_24h_Target = Param_24h_Target
    U4_VD_ExperimentTarget = Param_ExpTarget
    U4_VD_PreMixTime = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U4_VD_Timeout_ValveA = Param_Timeout_ValveA
    U4_VD_Timeout_ValveB = Param_Timeout_ValveB
    U4_VD_Timeout_ValveC = Param_Timeout_ValveC
    U4_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 5 Then
    U5_VD_StepResolution = Param_StepRes
    U5_VD_24h_Target = Param_24h_Target
    U5_VD_ExperimentTarget = Param_ExpTarget
    U5_VD_PreMixTime = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U5_VD_Timeout_ValveA = Param_Timeout_ValveA
    U5_VD_Timeout_ValveB = Param_Timeout_ValveB
    U5_VD_Timeout_ValveC = Param_Timeout_ValveC
    U5_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 6 Then
    U6_VD_StepResolution = Param_StepRes
    U6_VD_24h_Target = Param_24h_Target
    U6_VD_ExperimentTarget = Param_ExpTarget
    U6_VD_PreMixTime = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U6_VD_Timeout_ValveA = Param_Timeout_ValveA
    U6_VD_Timeout_ValveB = Param_Timeout_ValveB
    U6_VD_Timeout_ValveC = Param_Timeout_ValveC
    U6_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 7 Then
    U7_VD_StepResolution = Param_StepRes
    U7_VD_24h_Target = Param_24h_Target
    U7_VD_ExperimentTarget = Param_ExpTarget
    U7_VD_PreMixTime = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U7_VD_Timeout_ValveA = Param_Timeout_ValveA
    U7_VD_Timeout_ValveB = Param_Timeout_ValveB
    U7_VD_Timeout_ValveC = Param_Timeout_ValveC
    U7_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 8 Then
    U8_VD_StepResolution = Param_StepRes
    U8_VD_24h_Target = Param_24h_Target
    U8_VD_ExperimentTarget = Param_ExpTarget
    U8_VD_PreMixTime = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U8_VD_Timeout_ValveA = Param_Timeout_ValveA
    U8_VD_Timeout_ValveB = Param_Timeout_ValveB
    U8_VD_Timeout_ValveC = Param_Timeout_ValveC
    U8_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

!Beep()
```

### 脚本 29:复制到�
�他单�
�按�?

- **编号**: 29
- **用�?*: 弹出单�
�选择子窗�?选择目标单�
�后复制参�?需管理员组权限)
- **位置**: 用户窗口 �?画面4_参数设置 �?复制到�
�他单�
�按钮构�?�?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 复制到�
�他单�
�按钮脚�?
' 功能: 权限校验 �?弹出单�
�选择子窗�?脚本56负责选目标单�
?
'       脚本57负责确认后执行复�?
' ============================================

' --- 1. 校验管理员组权限(跨单�
�复制属敏感操作) ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 记录源单�
?供复制确认子窗口使用) ---
ParamSrcUnit = SelectedUnit

' --- 3. 打开单�
�选择子窗�?脚本56) ---
!OpenSubWnd(子窗口_单�
�选择, 240, 180, 400, 240, 17)
```

### 脚本 30:恢复默认按钮

- **编号**: 30
- **用�?*: 二次确认后重置参数为默认�?需管理员组权限)
- **位置**: 用户窗口 �?画面4_参数设置 �?恢复默认按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 恢复默认按钮脚本
' 功能: 权限校验 �?弹出恢复默认确认子窗�?脚本53负责执行)
' 默认值�
�?参�?McgsPro变量导�
�_单�
�1.csv ~ 单�
�8.csv 备注):
' StepRes=4.1667  CycleSet=30.0  (出厂默认值参考FC0)
' Timeout_ValveA/B/C=60.0s  (出厂默认值参考FC0)
'   Delay_ValveA_Verify=0.5
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 打开恢复默认确认子窗�?脚本53) ---
!OpenSubWnd(子窗口_恢复默认确认, 240, 180, 400, 180, 17)
```


### 脚本 30.5:存为默认按钮(+确认弹窗)

- **编号**: 30.5
- **用�?*: 范围校验 �?二次确认 �?把当前参数存为用户默�?(U1_UD_*)
- **位置**: 用户窗口 �?画面4_参数设置 �?存为默认按钮构件 �?Click 事件
- **触发方式**: 按钮单击
- **前置**: MCGS 需�
�导�
?McgsPro变量导�
�_单�
�1_v3.0.csv (新增 21 �?U1_UD_ 变量)
- **PLC�
�置**: STEP7 断电保持 VB456~VB539 (84 字节)

**存为默认按钮 Click 脚本**:
```
' ============================================
' 存为默认按钮脚本
' 功能: 范围校验(和保存参数一�? �?二次确认弹窗 �?Param缓冲写U1_UD_*存储�?
' 存储位置: PLC VB456~VB539 (断电保持)
'   VB456=用户默认有效标志, VD460~VD528=18个REAL, VB532=VW388, VB536=V200.0
' ============================================

' --- 范围校验 ---

IF  Param_TargetInletVolume < 0  THEN
    Param_Confirm_Text = "错误：注水量设定值范�?0"
    Param_Pending_Save = 0
    !OpenSubWnd(用户窗口.保存默认二次确认, 400, 300, 400, 200, 0)
    EXIT
ENDIF

IF  Param_VD_Vol_Target < 0  THEN
    Param_Confirm_Text = "错误：加药量设定值范�?0"
    Param_Pending_Save = 0
    !OpenSubWnd(用户窗口.保存默认二次确认, 400, 300, 400, 200, 0)
    EXIT
ENDIF

IF Param_24h_Target < 1 OR Param_24h_Target > 48 THEN
    Param_Confirm_Text = "错误：换水周期�
范围(1~48min)"
    Param_Pending_Save = 0
    !OpenSubWnd(用户窗口.保存默认二次确认, 400, 300, 400, 200, 0)
    EXIT
ENDIF




IF Param_T_Default < 1 OR Param_T_Default > 600 THEN
    Param_Confirm_Text = "错误：首轮�
�液总时长T�
范�?1~600min)"
    Param_Pending_Save = 0
    !OpenSubWnd(用户窗口.保存默认二次确认, 400, 300, 400, 200, 0)
    EXIT
ENDIF

IF Param_S6_Default < 1 OR Param_S6_Default > 600 THEN
    Param_Confirm_Text = "错误：首轮S6排水时长�
范�?1~600min)"
    Param_Pending_Save = 0
    !OpenSubWnd(用户窗口.保存默认二次确认, 400, 300, 400, 200, 0)
    EXIT
ENDIF

' --- 校验通过 ---
Param_Pending_Save = 1
Param_Confirm_Text = "将参�? + "保存�?号默认设置，确认保存�?
!OpenSubWnd(用户窗口.保存默认二次确认, 400, 300, 400, 200, 0)
```

**保存默认二次确认 - 确认按钮 Click 脚本**:
```
' ============================================
' 保存默认二次确认 - 确认按钮
' 功能: �?Param_* 编辑缓冲变量 �?U1_UD_* 用户存储�?+ 置标�?1
' FC0 冷启动检�?VB456=1 时自动用这些值覆盖出厂硬编码默认�?
' ============================================

IF Param_Pending_Save = 1 THEN
    U1_UD_VD24_ExpTarget     = Param_ExpTarget
    U1_UD_VD28_PreMixTime    = Param_PreMixTime
' [v2.2 removed PreMixTime_MinSafe write]
' [v2.2 removed RestTime write]
' [v2.2 removed RestTime_Min write]
' [v2.2 removed CycleExtend_Max write]
    U1_UD_VD54_TimeoutC      = Param_Timeout_ValveC
    U1_UD_VD66_DelayA        = Param_Delay_ValveA_Verify
    U1_UD_VD108_S6Default    = Param_S6_Default
    U1_UD_VD144_TDefault     = Param_T_Default
    U1_UD_VD316_InletVol     = Param_TargetInletVolume
    U1_UD_VD350_StepRes      = Param_StepRes
    U1_UD_VD414_24h_Target     = Param_24h_Target
' [v2.2 added VD426 VD430]
U1_UD_VD426_TransferMargin = Param_Transfer_Margin
U1_UD_VD430_SafetyMargin = Param_Safety_Margin
    U1_UD_VD358_TimeoutA     = Param_Timeout_ValveA
    U1_UD_VD362_TimeoutB     = Param_Timeout_ValveB
    U1_UD_VD370_VolTarget    = Param_VD_Vol_Target
    U1_UD_VD448_WaitTimeout  = Param_S4WaitTimeout
    U1_UD_VD452_ManualDose   = Param_ManualDose_Target
    U1_UD_VW388_Mode         = Param_ManualDose_Mode
    U1_UD_V200_0_AckMode     = Param_AlarmAckMode

    U1_UD_Flag = 1
ENDIF

Param_Pending_Save = 0
!SetWindow(用户窗口.保存默认二次确认, 3)
```

**保存默认二次确认 - 取消按钮 Click 脚本**:
```
Param_Pending_Save = 0
!SetWindow(用户窗口.保存默认二次确认, 3)
```

### 脚本 31:参数范围校验脚本

- **编号**: 31
- **用�?*: 完整校验时间/�
时/工艺参数上下�?失败时蜂�?退�?
- **位置**: 用户窗口 �?画面4_参数设置 �?输�
�框构�?�?ContentChanged 事件(或保存前调用)
- **触发方式**: 参数变化�?可作为保存按钮前置校验段)

```
' ============================================
' 参数范围校验脚本
' 功能: 校验 Param_* 编辑缓冲变量范围,失败�?ParamValid=0
' 校验规则(参�?HMI画面架构规划文档 + PLC设计文档):
' 浓度参数已移�?(VD10/VD14 -> RTC DT10)
'   步进: 0 < StepRes <= 5
'   周期: 0.5 <= CycleSet <= 60
'   实验目标: 1 <= ExpTarget <= 120
'   预循�? PreMixTime(3.0) <= PreMixTime <= 60
'   静止: PreMixTime(1.5) <= RestTime <= 30
'   顺延上限: 0 < PreMixTime <= 2
'   �
时: 0.5 <= Timeout_* <= 30
'   阀A�
�闭延时验证: 0 < Delay_ValveA_Verify <= 5
' ============================================

ParamValid = 1
ParamInvalidStr = ""

' --- 1. 步进/周期/目标 ---
If Param_StepRes <= 0 Then
    ParamValid = 0
    ParamInvalidStr = "步进分辨率�
�?0"
EndIf
If Param_StepRes > 5 Then
    ParamValid = 0
    ParamInvalidStr = "步进分辨率上�?"
EndIf
If Param_24h_Target < 1 Then  ' [v2.2 range 1-48]
    ParamValid = 0
    ParamInvalidStr = "换水周期下限0.5min"
EndIf
If Param_24h_Target > 48 Then  ' [v2.2 range 1-48]
    ParamValid = 0
    ParamInvalidStr = "换水周期上限60min"
EndIf
If Param_ExpTarget < 1 Then
    ParamValid = 0
    ParamInvalidStr = "实验目标下限1min"
EndIf
If Param_ExpTarget > 120 Then
    ParamValid = 0
    ParamInvalidStr = "实验目标上限120min"
EndIf

' --- 2. 预循�?静止 ---
EndIf
If Param_PreMixTime > 60 Then
    ParamValid = 0
    ParamInvalidStr = "预循环时间上�?0min"
EndIf

' --- 3. 顺延上限 ---

' --- 4. �
时组校�?---
If Param_Timeout_ValveA < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "阀A�
时下限0.5s"
EndIf
If Param_Timeout_ValveA > 30 Then
    ParamValid = 0
    ParamInvalidStr = "阀A�
时上限30s"
EndIf
If Param_Timeout_ValveB < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "阀B�
时下限0.5s"
EndIf
If Param_Timeout_ValveB > 30 Then
    ParamValid = 0
    ParamInvalidStr = "阀B�
时上限30s"
EndIf
If Param_Timeout_ValveC < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "阀C�
时下限0.5s"
EndIf
If Param_Timeout_ValveC > 30 Then
    ParamValid = 0
    ParamInvalidStr = "阀C�
时上限30s"
EndIf
    ParamValid = 0
    ParamInvalidStr = "�?�
时下限0.5s"
EndIf
    ParamValid = 0
    ParamInvalidStr = "�?�
时上限30s"
EndIf
    ParamValid = 0
    ParamInvalidStr = "�?�
时下限0.5s"
EndIf
    ParamValid = 0
    ParamInvalidStr = "�?�
时上限30s"
EndIf

' --- 5. 阀A�
�闭延时验证 ---
If Param_Delay_ValveA_Verify <= 0 Then
    ParamValid = 0
    ParamInvalidStr = "阀A�
�闭延时验证�
须>0"
EndIf
If Param_Delay_ValveA_Verify > 5 Then
    ParamValid = 0
    ParamInvalidStr = "阀A�
�闭延时验证上限5s"
EndIf

' --- 6. 校验失败蜂鸣 ---
If ParamValid = 0 Then
    !Beep()
EndIf
```

### 脚本 32:返回按钮

- **编号**: 32
- **用�?*: �
�闭参数设置画面,返回菜单_单�
�操作(v2.1改为两级菜单)
- **位置**: 用户窗口 �?画面4_参数设置 �?返回按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面4)
' 功能: �
�闭当前画面,返回菜单_单�
�操作
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("菜单_单�
�操作")
```

---

## 七、G. 画面5_报警日志脚本

### 脚本 33:画面5 窗口打开脚本

- **编号**: 33
- **用�?*: 加载当前激活报�?+ 历史日志,初始化筛选条�?
- **位置**: 用户窗口 �?画面5_报警日志 �?Load 事件
- **触发方式**: 窗口�
载�?

```
' ============================================
' 画面5_报警日志 Load 脚本
' 功能: 初始化筛选单�
�号=0(�
�部) + 刷新报警浏览构件时间范围
' ============================================

' --- 1. �
�闭残留子窗�?---
!CloseAllSubWnd()

' --- 2. 初始化筛选单�
�号(0=�
�部8个单�
? ---
AlmFilterUnit = 0

' --- 3. 拼接筛选描�?---
AlmFilterStr = "�
�部单�
�"

' --- 4. 更新系统时间显示 ---
SysTimeString = $Date + " " + $Time
```

### 脚本 34:按单�
�筛选按�?

- **编号**: 34
- **用�?*: 弹出单�
�选择子窗�?选择目标单�
�号筛选报�?
- **位置**: 用户窗口 �?画面5_报警日志 �?按单�
�筛选按钮构�?�?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 按单�
�筛选按钮脚�?
' 功能: 打开单�
�选择子窗�?脚本56),用户选择后更�?AlmFilterUnit
' ============================================

' --- 1. 标记筛选模�?供子窗口区分用�? ---
SubWndMode = 1

' --- 2. 打开单�
�选择子窗�?---
!OpenSubWnd(子窗口_单�
�选择, 240, 180, 400, 240, 17)
```

### 脚本 34.5:导出历史报警日志按钮(U�?

- **编号**: 34.5 (画面5区域,插�
�于脚�?4�?5之间)
- **用�?*: 二次确认后将历史报警日志导出至U盘CSV文件
- **位置**: 用户窗口 �?画面5_报警日志 �?导出U盘按钮构�?�?Click 事件
- **触发方式**: 按钮单击
- **二次确认**: 按钮安�
�属�?�?安�
�控制 �?弹窗确认(需在构件属性中�
�置,提示文本="将导出�
�部历史报警日志到U�?确认?")

```
' ============================================
' 导出历史报警日志到U�?(McgsPro 3.3.6)
' 官方函数: !ExportHisDataToCSV
' 组对象名: "Mcgs_HistoryAlarm" (McgsPro�
置,不需手动�?
' 说明:
'   本脚本使�?方案A"固定起始时间("1970-01-01 00:00:00"),
'   避开 McgsPro 不支持的 DateAdd/DateDiff 函数�?
'   二次确认由按钮安�
�属性弹窗实�?本脚本不做确认�?
' ============================================

DIM fileName AS string
DIM ret AS integer

' 生成文件�? AlarmLog_YYYYMMDD_HHMMSS.csv
fileName = "AlarmLog_" + Str($Year) + Str($Month) + Str($Day) + "_" + Str($Hour) + Str($Minute) + ".csv"

' 导出�
�部历史报警到CSV
' 参数:
'   (文件�? Mcgs_HistoryAlarm, 空字段名=�
�部,
'    "1970-01-01 00:00:00", 当前时间, 最�?0万条,
'    1=覆盖, �? 进度指示, 控制标志)
'
' 注意: 进度指示 / 控制标志 �
须是实时数据库中已存在�?integer 变量
'       (需要预�
�在 McgsPro �?实时数据 �?新建)
'
' 错误�?
'   0=成功, -1021=U盘未插�
�, -1023=该时间段无记�? �
�他=文件操作失败
ret = !ExportHisDataToCSV(fileName, "Mcgs_HistoryAlarm", "", "1970-01-01 00:00:00", $Date + " " + $Time, 100000, 1, "", 进度指示, 控制标志)
```

**�
须预建�?HMI �
部变量**（实时数�?�?新建 �?integer）：

| 变量�?| 类型 | 用�?|
|---|---|---|
| 进度指示 | integer | 导出过程中显示进度条�?导出结束自动归零 |
| 控制标志 | integer | 导出结束自动�?;导出中途手动置负值可取消 |

---

### 脚本 35:�
除历史日志按钮

- **编号**: 35
- **用�?*: 二次确认后�
除报警历史记�?需管理员组权限)
- **位置**: 用户窗口 �?画面5_报警日志 �?�
除历史日志按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' �
除历史日志按钮脚本
' 功能: 权限校验 �?弹出�
除日志确认子窗�?脚本54负责执行)
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 打开�
除日志确认子窗�?---
!OpenSubWnd(子窗口_�
除日志确认, 240, 180, 400, 180, 17)
```

### 脚本 36:返回按钮

- **编号**: 36
- **用�?*: �
�闭画面5,返回菜单_监控诊断(v2.1改为两级菜单)
- **位置**: 用户窗口 �?画面5_报警日志 �?返回按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面5)
' 功能: �
�闭所有子窗口,返回菜单_监控诊断
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("菜单_监控诊断")
```

---

## �
�、H. 画面6_趋势曲线脚本

### 脚本 37:画面6 窗口打开脚本

- **编号**: 37
- **用�?*: 初始化历史曲线构件时间范�?默认1小时)+曲线变量绑定
- **位置**: 用户窗口 �?画面6_趋势曲线 �?Load 事件
- **触发方式**: 窗口�
载�?

```
' ============================================
' 画面6_趋势曲线 Load 脚本
' 功能: 设置默认时间范围=1小时 + 默认显示1号单�
�流�?压力
' ============================================

' --- 1. �
�闭残留子窗�?---
!CloseAllSubWnd()

' --- 2. 初始化时间范�?1=1h / 8=8h / 24=24h) ---
TrendTimeRange = 1

' --- 3. 默认显示单�
� ---
TrendDisplayUnit = 1

' --- 4. 拼接时间范围描述 ---
If TrendTimeRange = 1 Then
    TrendRangeStr = "最�?小时"
EndIf
If TrendTimeRange = 8 Then
    TrendRangeStr = "最�?小时"
EndIf
If TrendTimeRange = 24 Then
    TrendRangeStr = "最�?4小时"
EndIf
```

### 脚本 38:时间范围切换按钮

- **编号**: 38
- **用�?*: 1小时/8小时/24小时三档切换(单按钮循环切�?
- **位置**: 用户窗口 �?画面6_趋势曲线 �?时间范围切换按钮构件 �?Click 事件
- **触发方式**: 按钮单击
- **前置条件**: 画面上预�
�放3个历史曲线构�?分别对应1h/8h/24h,每个构件�?高级属性→时间范围"在属性对话框�?*静态�
��?*(不能用变量绑�?
- **变量依赖**: 预建 `TrendHis_1h_Visible` / `TrendHis_8h_Visible` / `TrendHis_24h_Visible` (integer�?

```
' ============================================
' 时间范围切换按钮脚本
' 功能: 1h �?8h �?24h �?1h 循环切换
'
' 重要 (2026-08-30 修订):
'   McgsPro 历史曲线构件**不支�?*运行时动态改变时间范�?
'   (构件属性里的时间范围是静态数�?不能用变量绑�?,
'   也不支持 VBScript 风格 Call hisTrend.SetXLength()�?
'
'   正确做法:
'   画面上预�
�放3个历史曲线构�?HisCurve_1h / HisCurve_8h / HisCurve_24h),
'   每个构件�?高级属性→时间范围"分别写死�?3600/28800/86400 秒�?
'   切换按钮�
改�?个构件的 Visible 绑定变量值�?
'   每个构件�?基本属性→可见性→显示表达�?绑定对应变量:
'     HisCurve_1h �?Visible 绑定 TrendHis_1h_Visible
'     HisCurve_8h �?Visible 绑定 TrendHis_8h_Visible
'     HisCurve_24h �?Visible 绑定 TrendHis_24h_Visible
' ============================================

If TrendTimeRange = 1 Then
    TrendTimeRange = 8
    TrendRangeStr = "最�?小时"
    TrendHis_1h_Visible = 0
    TrendHis_8h_Visible = 1
    TrendHis_24h_Visible = 0
Else
    If TrendTimeRange = 8 Then
        TrendTimeRange = 24
        TrendRangeStr = "最�?4小时"
        TrendHis_1h_Visible = 0
        TrendHis_8h_Visible = 0
        TrendHis_24h_Visible = 1
    Else
        TrendTimeRange = 1
        TrendRangeStr = "最�?小时"
        TrendHis_1h_Visible = 1
        TrendHis_8h_Visible = 0
        TrendHis_24h_Visible = 0
    EndIf
EndIf

!Beep()
```

### 脚本 39:返回按钮

- **编号**: 39
- **用�?*: �
�闭画面6,返回菜单_监控诊断(v2.1改为两级菜单)
- **位置**: 用户窗口 �?画面6_趋势曲线 �?返回按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面6)
' 功能: �
�闭所有子窗口,返回菜单_监控诊断
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("菜单_监控诊断")
```

---

## 九、I. 画面7_通讯维护脚本

### 脚本 40:画面7 窗口打开脚本

- **编号**: 40
- **用�?*: 加载8台PLC + 16�?85从站状�?
- **位置**: 用户窗口 �?画面7_通讯维护 �?Load 事件
- **触发方式**: 窗口�
载�?

```
' ============================================
' 画面7_通讯维护 Load 脚本
' 功能: 刷新8台PLC设备状�?+ 16个Modbus从站状�?
' ============================================

' --- 1. �
�闭残留子窗�?---
!CloseAllSubWnd()

' --- 2. 检�?台PLC设备状�?(!SetDevice(name,3,"") 返回 1=启动 / 0=停止) ---
If !SetDevice(PLC_01, 3, "") = 1 Then
    PLC01_Status = 1
Else
    PLC01_Status = 0
EndIf
If !SetDevice(PLC_02, 3, "") = 1 Then
    PLC02_Status = 1
Else
    PLC02_Status = 0
EndIf
If !SetDevice(PLC_03, 3, "") = 1 Then
    PLC03_Status = 1
Else
    PLC03_Status = 0
EndIf
If !SetDevice(PLC_04, 3, "") = 1 Then
    PLC04_Status = 1
Else
    PLC04_Status = 0
EndIf
If !SetDevice(PLC_05, 3, "") = 1 Then
    PLC05_Status = 1
Else
    PLC05_Status = 0
EndIf
If !SetDevice(PLC_06, 3, "") = 1 Then
    PLC06_Status = 1
Else
    PLC06_Status = 0
EndIf
If !SetDevice(PLC_07, 3, "") = 1 Then
    PLC07_Status = 1
Else
    PLC07_Status = 0
EndIf
If !SetDevice(PLC_08, 3, "") = 1 Then
    PLC08_Status = 1
Else
    PLC08_Status = 0
EndIf

' --- 3. 检�?6个Modbus从站状�?注射�?流量�?× 8�? ---
If !SetDevice(MB_Pump_01, 3, "") = 1 Then
    MBPump01_Status = 1
Else
    MBPump01_Status = 0
EndIf
If !SetDevice(MB_Flow_01, 3, "") = 1 Then
    MBFlow01_Status = 1
Else
    MBFlow01_Status = 0
EndIf
If !SetDevice(MB_Pump_02, 3, "") = 1 Then
    MBPump02_Status = 1
Else
    MBPump02_Status = 0
EndIf
If !SetDevice(MB_Flow_02, 3, "") = 1 Then
    MBFlow02_Status = 1
Else
    MBFlow02_Status = 0
EndIf
If !SetDevice(MB_Pump_03, 3, "") = 1 Then
    MBPump03_Status = 1
Else
    MBPump03_Status = 0
EndIf
If !SetDevice(MB_Flow_03, 3, "") = 1 Then
    MBFlow03_Status = 1
Else
    MBFlow03_Status = 0
EndIf
If !SetDevice(MB_Pump_04, 3, "") = 1 Then
    MBPump04_Status = 1
Else
    MBPump04_Status = 0
EndIf
If !SetDevice(MB_Flow_04, 3, "") = 1 Then
    MBFlow04_Status = 1
Else
    MBFlow04_Status = 0
EndIf
If !SetDevice(MB_Pump_05, 3, "") = 1 Then
    MBPump05_Status = 1
Else
    MBPump05_Status = 0
EndIf
If !SetDevice(MB_Flow_05, 3, "") = 1 Then
    MBFlow05_Status = 1
Else
    MBFlow05_Status = 0
EndIf
If !SetDevice(MB_Pump_06, 3, "") = 1 Then
    MBPump06_Status = 1
Else
    MBPump06_Status = 0
EndIf
If !SetDevice(MB_Flow_06, 3, "") = 1 Then
    MBFlow06_Status = 1
Else
    MBFlow06_Status = 0
EndIf
If !SetDevice(MB_Pump_07, 3, "") = 1 Then
    MBPump07_Status = 1
Else
    MBPump07_Status = 0
EndIf
If !SetDevice(MB_Flow_07, 3, "") = 1 Then
    MBFlow07_Status = 1
Else
    MBFlow07_Status = 0
EndIf
If !SetDevice(MB_Pump_08, 3, "") = 1 Then
    MBPump08_Status = 1
Else
    MBPump08_Status = 0
EndIf
If !SetDevice(MB_Flow_08, 3, "") = 1 Then
    MBFlow08_Status = 1
Else
    MBFlow08_Status = 0
EndIf

' --- 4. 更新系统时间显示 ---
SysTimeString = $Date + " " + $Time
```

### 脚本 41:重启通讯按钮

- **编号**: 41
- **用�?*: 权限校验后停止所�?PLC + Modbus 设备,延时 500ms 再�
�部启�?�
�量重启)
- **位置**: 用户窗口 �?画面7_通讯维护 �?重启通讯按钮构件 �?Click 事件
- **触发方式**: 按钮单击
- **二次确认**: 按钮安�
�属�?�?安�
�控制 �?弹窗确认(需在构件属性中�
�置,提示文本="将重启所有单�
�通讯连接,期间数据采集暂停,确认?")
- **权限**: 按钮安�
�属性�
��?LoginLevel >= 3 �?!CheckUserGroup("管理员组")
- **设备命名约定**: McgsPro 设备窗口中设备名需与脚本一致。`PLC_01`~`PLC_08` �?S7-200 SMART 单�
� PLC 设备,`MB_Pump_01`~`MB_Pump_08` �?8 台注射泵 Modbus 从站,`MB_Flow_01`~`MB_Flow_08` �?8 台流量计 Modbus 从站。如工程实�
命名不同(�?`PLC_1` 无前导零),请同步修改脚�?

```
' ============================================
' 重启通讯按钮脚本
' 功能: 权限校验 �?停止所有PLC+Modbus设备 �?延时500ms �?启动所有设�?
' 注意: �
�量重启会影�?套单�
�通讯,�?秒采集暂�?
' 二次确认由按钮安�
�属性弹窗实�?本脚本不做确�?
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 蜂鸣提示开始重�?---
!Beep()

' --- 3. 停止8台PLC设备 ---
!SetDevice(PLC_01, 2, "")
!SetDevice(PLC_02, 2, "")
!SetDevice(PLC_03, 2, "")
!SetDevice(PLC_04, 2, "")
!SetDevice(PLC_05, 2, "")
!SetDevice(PLC_06, 2, "")
!SetDevice(PLC_07, 2, "")
!SetDevice(PLC_08, 2, "")

' --- 4. 停止16个Modbus从站 ---
!SetDevice(MB_Pump_01, 2, "")
!SetDevice(MB_Flow_01, 2, "")
!SetDevice(MB_Pump_02, 2, "")
!SetDevice(MB_Flow_02, 2, "")
!SetDevice(MB_Pump_03, 2, "")
!SetDevice(MB_Flow_03, 2, "")
!SetDevice(MB_Pump_04, 2, "")
!SetDevice(MB_Flow_04, 2, "")
!SetDevice(MB_Pump_05, 2, "")
!SetDevice(MB_Flow_05, 2, "")
!SetDevice(MB_Pump_06, 2, "")
!SetDevice(MB_Flow_06, 2, "")
!SetDevice(MB_Pump_07, 2, "")
!SetDevice(MB_Flow_07, 2, "")
!SetDevice(MB_Pump_08, 2, "")
!SetDevice(MB_Flow_08, 2, "")

' --- 5. 延时500ms确保停止完成 ---
!Sleep(500)

' --- 6. 启动8台PLC设备 ---
!SetDevice(PLC_01, 1, "")
!SetDevice(PLC_02, 1, "")
!SetDevice(PLC_03, 1, "")
!SetDevice(PLC_04, 1, "")
!SetDevice(PLC_05, 1, "")
!SetDevice(PLC_06, 1, "")
!SetDevice(PLC_07, 1, "")
!SetDevice(PLC_08, 1, "")

' --- 7. 启动16个Modbus从站 ---
!SetDevice(MB_Pump_01, 1, "")
!SetDevice(MB_Flow_01, 1, "")
!SetDevice(MB_Pump_02, 1, "")
!SetDevice(MB_Flow_02, 1, "")
!SetDevice(MB_Pump_03, 1, "")
!SetDevice(MB_Flow_03, 1, "")
!SetDevice(MB_Pump_04, 1, "")
!SetDevice(MB_Flow_04, 1, "")
!SetDevice(MB_Pump_05, 1, "")
!SetDevice(MB_Flow_05, 1, "")
!SetDevice(MB_Pump_06, 1, "")
!SetDevice(MB_Flow_06, 1, "")
!SetDevice(MB_Pump_07, 1, "")
!SetDevice(MB_Flow_07, 1, "")
!SetDevice(MB_Pump_08, 1, "")
!SetDevice(MB_Flow_08, 1, "")

' --- 8. 再次蜂鸣提示完成 ---
!Beep()
```

### 脚本 42:查看详细日志按钮

- **编号**: 42
- **用�?*: 打开操作日志浏览子窗�?
- **位置**: 用户窗口 �?画面7_通讯维护 �?查看详细日志按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 查看详细日志按钮脚本
' 功能: 打开日志浏览子窗�?组态中使用存盘数据浏览构件显示操作日志)
' ============================================

!OpenSubWnd(子窗口_日志浏览, 80, 60, 800, 600, 17)
```

### 脚本 43:返回按钮

- **编号**: 43
- **用�?*: �
�闭画面7,返回菜单_监控诊断(v2.1改为两级菜单)
- **位置**: 用户窗口 �?画面7_通讯维护 �?返回按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面7)
' 功能: �
�闭所有子窗口,返回菜单_监控诊断
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("菜单_监控诊断")
```

---

## 十、J. 画面8a_单�
�使能 + 画面8b_权限管理脚本

> **v2.1 拆分说明**:�?画面8_系统设置"拆分为两个独立画�?画面8a_单�
�使能(单�
�使能开�
?状态指�?和画�?b_权限管理(登录/注销/修改密码/退出系�?。两画面均返回菜单_系统�?

### 脚本 44:画面8a 窗口打开脚本

- **编号**: 44
- **用�?*: 加载8个单�
�使能状�?v2.1从画�?拆出)
- **位置**: 用户窗口 �?画面8a_单�
�使能 �?Load 事件
- **触发方式**: 窗口�
载�?

```
' ============================================
' 画面8a_单�
�使能 Load 脚本
' 功能: �
�闭残留子窗�?+ 加载单�
�使能状�?从断电保持变�?
' ============================================

' --- 1. �
�闭残留子窗�?---
!CloseAllSubWnd()

' --- 2. 显示当前登录用户 ---
CurrentUserStr = $UserName
If CurrentUserStr = "" Then
    CurrentUserStr = "未登�?
EndIf

' --- 3. 显示当前用户�?---
CurrentUserGroupStr = !GetCurrentGroup()
If CurrentUserGroupStr = "" Then
    CurrentUserGroupStr = "�?
EndIf

' --- 4. 拼接单�
�使能状态汇�?供画面显�? ---
' U1_Enable~U8_Enable 为断电保持�
部变�?这里只读汇�?
UnitEnableSummary = ""
If U1_Enable = 1 Then
    UnitEnableSummary = UnitEnableSummary + "1 "
EndIf
If U2_Enable = 1 Then
    UnitEnableSummary = UnitEnableSummary + "2 "
EndIf
If U3_Enable = 1 Then
    UnitEnableSummary = UnitEnableSummary + "3 "
EndIf
If U4_Enable = 1 Then
    UnitEnableSummary = UnitEnableSummary + "4 "
EndIf
If U5_Enable = 1 Then
    UnitEnableSummary = UnitEnableSummary + "5 "
EndIf
If U6_Enable = 1 Then
    UnitEnableSummary = UnitEnableSummary + "6 "
EndIf
If U7_Enable = 1 Then
    UnitEnableSummary = UnitEnableSummary + "7 "
EndIf
If U8_Enable = 1 Then
    UnitEnableSummary = UnitEnableSummary + "8 "
EndIf

' --- 5. 更新系统时间显示 ---
SysTimeString = $Date + " " + $Time
```

### 脚本 45:单�
�使能开�
�切�?

- **编号**: 45
- **用�?*: 切换单�
�使能状�?0�?) + !SaveData 存盘(需管理员组权限)
- **位置**: 用户窗口 �?画面8a_单�
�使能 �?单�
�使能开�
�构�?8�? �?Click 事件
- **触发方式**: 开�
�单�?
- **扩展方法**: 8个开�
�独立脚�?�?号为�?

**1号单�
�使能开�
�切�?*:
```
' ============================================
' 1号单�
�使能开�
�切换脚�?
' 功能: 权限校验 �?翻转 U1_Enable �?存盘
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 翻转 U1_Enable ---
If U1_Enable = 0 Then
    U1_Enable = 1
Else
    U1_Enable = 0
EndIf

' --- 3. 立即存盘(单�
�使能�
�置组对�?需组态为组对象并勾选存�? ---
!SaveData(UnitEnableGroup)
!FreshDataSave()

!Beep()
```

**2~8号单�
�使能开�
�切�?*(扩展方法:把脚本中 `U1_Enable` 替换为对应单�
�号):
```
' 2�?
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf
If U2_Enable = 0 Then
    U2_Enable = 1
Else
    U2_Enable = 0
EndIf
!SaveData(UnitEnableGroup)
!FreshDataSave()
!Beep()

' 3�?
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf
If U3_Enable = 0 Then
    U3_Enable = 1
Else
    U3_Enable = 0
EndIf
!SaveData(UnitEnableGroup)
!FreshDataSave()
!Beep()

' 4�?
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf
If U4_Enable = 0 Then
    U4_Enable = 1
Else
    U4_Enable = 0
EndIf
!SaveData(UnitEnableGroup)
!FreshDataSave()
!Beep()

' 5�?
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf
If U5_Enable = 0 Then
    U5_Enable = 1
Else
    U5_Enable = 0
EndIf
!SaveData(UnitEnableGroup)
!FreshDataSave()
!Beep()

' 6�?
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf
If U6_Enable = 0 Then
    U6_Enable = 1
Else
    U6_Enable = 0
EndIf
!SaveData(UnitEnableGroup)
!FreshDataSave()
!Beep()

' 7�?
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf
If U7_Enable = 0 Then
    U7_Enable = 1
Else
    U7_Enable = 0
EndIf
!SaveData(UnitEnableGroup)
!FreshDataSave()
!Beep()

' 8�?
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf
If U8_Enable = 0 Then
    U8_Enable = 1
Else
    U8_Enable = 0
EndIf
!SaveData(UnitEnableGroup)
!FreshDataSave()
!Beep()
```

### 脚本 46:用户管理按钮

- **编号**: 46
- **用�?*: 弹出 McgsPro �
置用户管理窗口
- **位置**: 用户窗口 �?画面8b_权限管理 �?用户管理按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 用户管理按钮脚本
' 功能: 弹出�
置用户管理窗口(�
负责人或拥有子组的用户可见子组�
�置)
' ============================================

!Editusers()
```

### 脚本 47:修改密码按钮

- **编号**: 47
- **用�?*: 弹出 McgsPro �
置修改密码窗口
- **位置**: 用户窗口 �?画面8b_权限管理 �?修改密码按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 修改密码按钮脚本
' 功能: 弹出�
置修改密码窗口,供当前登录用户修改密�?
' ============================================

!ChangePassword()
```

### 脚本 48:退出系统按�?

- **编号**: 48
- **用�?*: 二次确认后退�?McgsPro 运行环境(需管理员组权限)
- **位置**: 用户窗口 �?画面8b_权限管理 �?退出系统按钮构�?�?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 退出系统按钮脚�?
' 功能: 权限校验 �?弹出退出确认子窗口(脚本55负责执行)
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 打开退出系统确认子窗口 ---
!OpenSubWnd(子窗口_退出系统确�? 240, 180, 400, 180, 17)
```

### 脚本 49:返回按钮(画面8b)

- **编号**: 49
- **用�?*: �
�闭画面8b_权限管理,返回菜单_系统(v2.1改为两级菜单)
- **位置**: 用户窗口 �?画面8b_权限管理 �?返回按钮构件 �?Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面8b_权限管理)
' 功能: �
�闭所有子窗口,返回菜单_系统
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("菜单_系统")
```

> **�?*:画面8a_单�
�使能的返回按钮使用相同逻辑,脚本�?`!CloseAllSubWnd()` + `!CloseAllWindow("菜单_系统")`�?

---

## 十一、K. 二次确认子窗口脚�?

> **子窗口组态约�?*:每个二次确认子窗口�
�?确认"�?取消"两个按钮,确认按钮执行实�
操作并调�?`!CloseAllSubWnd()` �
�闭子窗�?取消按钮�
调�?`!CloseAllSubWnd()`。子窗口模式参数 `17 = 1(模�? + 16(边框)`�?

### 脚本 50:启动确认子窗�?

- **编号**: 50
- **用�?*: 启动二次确认。确认→�?CMD_Start=1 + �
�闭;取消→�
��?
- **位置**: 用户窗口 �?子窗口_启动确认 �?确认按钮 / 取消按钮 �?Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 启动确认子窗�?- 确认按钮
' 功能: 对当前选中单�
��?CMD_Start=1,然后�
�闭子窗�?
' ============================================

If SelectedUnit = 1 Then
    U1_CMD_Start = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Start = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Start = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Start = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Start = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Start = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Start = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Start = 1
EndIf

!Beep()
!CloseAllSubWnd()
```

**取消按钮**:
```
' ============================================
' 启动确认子窗�?- 取消按钮
' ============================================

!CloseAllSubWnd()
```

### 脚本 51:停止确认子窗�?

- **编号**: 51
- **用�?*: 停止二次确认。确认→�?CMD_Stop=1 + �
�闭;取消→�
��?
- **位置**: 用户窗口 �?子窗口_停止确认 �?确认按钮 / 取消按钮 �?Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 停止确认子窗�?- 确认按钮
' 功能: 对当前选中单�
��?CMD_Stop=1,然后�
�闭子窗�?
' ============================================

If SelectedUnit = 1 Then
    U1_CMD_Stop = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Stop = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Stop = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Stop = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Stop = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Stop = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Stop = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Stop = 1
EndIf

!Beep()
!CloseAllSubWnd()
```

**取消按钮**:
```
!CloseAllSubWnd()
```

### 脚本 52:急停确认子窗�?

- **编号**: 52
- **用�?*: 急停二次确认。确认→�?个使�?在线单�
��?CMD_Stop=1 + �
�闭;取消→�
��?
- **位置**: 用户窗口 �?子窗口_急停确认 �?确认按钮 / 取消按钮 �?Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 急停确认子窗�?- 确认按钮
' 功能: 对所有使�?在线单�
�下发急停(CMD_Stop=1)
' 注意: 急停是�
�局操作,不限�?SelectedUnit
' ============================================

If U1_Enable = 1 Then
    If U1_Online = 1 Then
        U1_CMD_Stop = 1
    EndIf
EndIf
If U2_Enable = 1 Then
    If U2_Online = 1 Then
        U2_CMD_Stop = 1
    EndIf
EndIf
If U3_Enable = 1 Then
    If U3_Online = 1 Then
        U3_CMD_Stop = 1
    EndIf
EndIf
If U4_Enable = 1 Then
    If U4_Online = 1 Then
        U4_CMD_Stop = 1
    EndIf
EndIf
If U5_Enable = 1 Then
    If U5_Online = 1 Then
        U5_CMD_Stop = 1
    EndIf
EndIf
If U6_Enable = 1 Then
    If U6_Online = 1 Then
        U6_CMD_Stop = 1
    EndIf
EndIf
If U7_Enable = 1 Then
    If U7_Online = 1 Then
        U7_CMD_Stop = 1
    EndIf
EndIf
If U8_Enable = 1 Then
    If U8_Online = 1 Then
        U8_CMD_Stop = 1
    EndIf
EndIf

!Beep()
!CloseAllSubWnd()
```

**取消按钮**:
```
!CloseAllSubWnd()
```

### 脚本 53:恢复默认确认子窗�?

- **编号**: 53
- **用�?*: 恢复默认参数二次确认。确认→重置 Param_* 为默认�?+ �
�闭;取消→�
��?
- **位置**: 用户窗口 �?子窗口_恢复默认确认 �?确认按钮 / 取消按钮 �?Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 恢复默认确认子窗�?- 确认按钮
' 功能: �?U1_UD_Flag=0 (用户默认失效)
'       PLC 下次冷启动会�?FC0 出厂硬编码默认�?
' 注意: 当前运行参数不变,需要重启PLC生效
' ============================================

U1_UD_Flag = 0

!Beep()
!CloseAllSubWnd()
**取消按钮**:
```
!CloseAllSubWnd()
```

### 脚本 54:�
除日志确认子窗�?

- **编号**: 54
- **用�?*: �
除报警历史日志二次确认。确认→!ClearHistoryAlarmData + !OperationLogClear + �
�闭;取消→�
��?
- **位置**: 用户窗口 �?子窗口_�
除日志确认 �?确认按钮 / 取消按钮 �?Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' �
除日志确认子窗�?- 确认按钮
' 功能: �
除历史报警数据 + �
除操作日志
' ============================================

!ClearHistoryAlarmData()
!OperationLogClear()

!Beep()
!CloseAllSubWnd()
```

**取消按钮**:
```
!CloseAllSubWnd()
```

### 脚本 55:退出系统确认子窗口

- **编号**: 55
- **用�?*: 退出系统二次确认。确认→�
�闭所有窗�?退出运行环�?取消→�
��?
- **位置**: 用户窗口 �?子窗口_退出系统确�?�?确认按钮 / 取消按钮 �?Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 退出系统确认子窗口 - 确认按钮
' 功能: �
�闭所有窗�?�
括子窗�? �?触发退出策�?
' 注意: McgsPro 通过 !CloseAllWindow("") �
�闭所有窗口后,
'       组态中"主控窗口→退�?设置�?退出运行环�?即可实现退出�?
'       若需权限检�?ExitLogonEnabled 已在启动策略中设置为1�?
' ============================================

!Beep()

' �
�闭所有子窗口
!CloseAllSubWnd()

' �
�闭所有标准窗�?空串=�
�闭�
�部,触发退出流�?
!CloseAllWindow("")
```

**取消按钮**:
```
!CloseAllSubWnd()
```

### 脚本 56:单�
�选择子窗�?

- **编号**: 56
- **用�?*: 选择目标单�
�号�?个数字按�?1~8)+ 1�?�
�部"按钮,点击后写�
�目标单�
�变量并�
�闭
- **位置**: 用户窗口 �?子窗口_单�
�选择 �?1~8号单�
�按�?/ �
�部按钮 �?Click 事件
- **触发方式**: 按钮单击
- **使用场景**: 脚本29(复制参数选择目标单�
�) / 脚本34(报警按单�
�筛�?

**1号单�
�按�?*(�?号为�?2~8号同�?:
```
' ============================================
' 单�
�选择子窗�?- 1号按�?
' 功能: 根据 SubWndMode 写�
�不同目标变量
'   SubWndMode=0: 复制参数目标 �?ParamDstUnit
'   SubWndMode=1: 报警筛选单�
?�?AlmFilterUnit
' ============================================

If SubWndMode = 0 Then
    ParamDstUnit = 1
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 1
    AlmFilterStr = "1号单�
?
EndIf

!CloseAllSubWnd()
```

**2号单�
�按�?*:
```
If SubWndMode = 0 Then
    ParamDstUnit = 2
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 2
    AlmFilterStr = "2号单�
?
EndIf
!CloseAllSubWnd()
```

**3号单�
�按�?*:
```
If SubWndMode = 0 Then
    ParamDstUnit = 3
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 3
    AlmFilterStr = "3号单�
?
EndIf
!CloseAllSubWnd()
```

**4号单�
�按�?*:
```
If SubWndMode = 0 Then
    ParamDstUnit = 4
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 4
    AlmFilterStr = "4号单�
?
EndIf
!CloseAllSubWnd()
```

**5号单�
�按�?*:
```
If SubWndMode = 0 Then
    ParamDstUnit = 5
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 5
    AlmFilterStr = "5号单�
?
EndIf
!CloseAllSubWnd()
```

**6号单�
�按�?*:
```
If SubWndMode = 0 Then
    ParamDstUnit = 6
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 6
    AlmFilterStr = "6号单�
?
EndIf
!CloseAllSubWnd()
```

**7号单�
�按�?*:
```
If SubWndMode = 0 Then
    ParamDstUnit = 7
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 7
    AlmFilterStr = "7号单�
?
EndIf
!CloseAllSubWnd()
```

**8号单�
�按�?*:
```
If SubWndMode = 0 Then
    ParamDstUnit = 8
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 8
    AlmFilterStr = "8号单�
?
EndIf
!CloseAllSubWnd()
```

**�
�部按钮**(�
报警筛选场景使�?:
```
If SubWndMode = 1 Then
    AlmFilterUnit = 0
    AlmFilterStr = "�
�部单�
�"
EndIf
!CloseAllSubWnd()
```

### 脚本 57:复制参数确认子窗�?

- **编号**: 57
- **用�?*: 跨单�
�复制参数二次确认。确认→�?ParamSrcUnit �?VD 参数复制�?ParamDstUnit + �
�闭;取消→�
��?
- **位置**: 用户窗口 �?子窗口_复制参数确认 �?确认按钮 / 取消按钮 �?Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 复制参数确认子窗�?- 确认按钮
' 功能: �?ParamSrcUnit 单�
�的�
��?VD 参数复制�?ParamDstUnit 单�
�
' 前置条件: 脚本29已设�?ParamSrcUnit,脚本56已设�?ParamDstUnit
' 注意: McgsPro 不支持动态变量名,用嵌�?If 选择�?目标单�
�
' ============================================

' --- 1. 校验�?目标单�
�有效 ---
If ParamSrcUnit < 1 Then
    !Beep()
    !CloseAllSubWnd()
    Exit
EndIf
If ParamSrcUnit > 8 Then
    !Beep()
    !CloseAllSubWnd()
    Exit
EndIf
If ParamDstUnit < 1 Then
    !Beep()
    !CloseAllSubWnd()
    Exit
EndIf
If ParamDstUnit > 8 Then
    !Beep()
    !CloseAllSubWnd()
    Exit
EndIf
If ParamSrcUnit = ParamDstUnit Then
    !Beep()
    !CloseAllSubWnd()
    Exit
EndIf

' --- 2. �?�?�?目标2~8�?---
If ParamSrcUnit = 1 Then
    If ParamDstUnit = 2 Then
                U2_VD_StepResolution = U1_VD_StepResolution
        U2_VD_24h_Target = U1_VD_24h_Target
        U2_VD_ExperimentTarget = U1_VD_ExperimentTarget
        U2_VD_PreMixTime = U1_VD_PreMixTime
' [v2.2 removed U2 sync]
' [v2.2 removed U2 sync]
' [v2.2 removed U2 sync]
' [v2.2 removed U2 sync]
        U2_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U2_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U2_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U2_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 3 Then
                U3_VD_StepResolution = U1_VD_StepResolution
        U3_VD_24h_Target = U1_VD_24h_Target
        U3_VD_ExperimentTarget = U1_VD_ExperimentTarget
        U3_VD_PreMixTime = U1_VD_PreMixTime
' [v2.2 removed U3 sync]
' [v2.2 removed U3 sync]
' [v2.2 removed U3 sync]
' [v2.2 removed U3 sync]
        U3_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U3_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U3_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U3_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 4 Then
                U4_VD_StepResolution = U1_VD_StepResolution
        U4_VD_24h_Target = U1_VD_24h_Target
        U4_VD_ExperimentTarget = U1_VD_ExperimentTarget
        U4_VD_PreMixTime = U1_VD_PreMixTime
' [v2.2 removed U4 sync]
' [v2.2 removed U4 sync]
' [v2.2 removed U4 sync]
' [v2.2 removed U4 sync]
        U4_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U4_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U4_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U4_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 5 Then
                U5_VD_StepResolution = U1_VD_StepResolution
        U5_VD_24h_Target = U1_VD_24h_Target
        U5_VD_ExperimentTarget = U1_VD_ExperimentTarget
        U5_VD_PreMixTime = U1_VD_PreMixTime
' [v2.2 removed U5 sync]
' [v2.2 removed U5 sync]
' [v2.2 removed U5 sync]
' [v2.2 removed U5 sync]
        U5_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U5_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U5_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U5_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 6 Then
                U6_VD_StepResolution = U1_VD_StepResolution
        U6_VD_24h_Target = U1_VD_24h_Target
        U6_VD_ExperimentTarget = U1_VD_ExperimentTarget
        U6_VD_PreMixTime = U1_VD_PreMixTime
' [v2.2 removed U6 sync]
' [v2.2 removed U6 sync]
' [v2.2 removed U6 sync]
' [v2.2 removed U6 sync]
        U6_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U6_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U6_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U6_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 7 Then
                U7_VD_StepResolution = U1_VD_StepResolution
        U7_VD_24h_Target = U1_VD_24h_Target
        U7_VD_ExperimentTarget = U1_VD_ExperimentTarget
        U7_VD_PreMixTime = U1_VD_PreMixTime
' [v2.2 removed U7 sync]
' [v2.2 removed U7 sync]
' [v2.2 removed U7 sync]
' [v2.2 removed U7 sync]
        U7_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U7_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U7_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U7_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 8 Then
                U8_VD_StepResolution = U1_VD_StepResolution
        U8_VD_24h_Target = U1_VD_24h_Target
        U8_VD_ExperimentTarget = U1_VD_ExperimentTarget
        U8_VD_PreMixTime = U1_VD_PreMixTime
' [v2.2 removed U8 sync]
' [v2.2 removed U8 sync]
' [v2.2 removed U8 sync]
' [v2.2 removed U8 sync]
        U8_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U8_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U8_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U8_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
EndIf

' --- 3. �?~8�?�?目标单�
�(扩展方法) ---
' �?ParamSrcUnit = 2~8 �?把上面源1号块中的:
'   - 外层 If ParamSrcUnit = 1 改为对应源单�
�号
'   - �
层 U1_VD_* (源读�? �
�部替换�?U<src>_VD_*
'   - �
层 U<n>_VD_* (目标写�
�) 保持目标单�
��?
' �? �?号→目标5号的�
�键�?
'   ... (�
�余18项同�?完整展开见组态实�?
' 完整脚本应在组态时�?8x7=56 种组合�
�部展开,本文件以�?号为代表�?

!Beep()
!CloseAllSubWnd()
```

**取消按钮**:
```
!CloseAllSubWnd()
```

---

## 十二、组态实施注意事�?

### 1. 子窗口模式参数说�?

本文件中 `!OpenSubWnd` 的第6个参数统一�?`17`,计算方式:
- `1` (bit0) = 模态模�?子窗口外鼠标不响�?�
须 CloseSubWnd �
�闭)
- `16` (bit4) = 显示边框
- 17 = 1 + 16

如需菜单模式(子窗口外按下鼠标自动�
�闭),改用 `2` �?`18` (2+16)。如需跟随鼠标位置弹出,�?`32` (bit5),例如 `49 = 1+16+32`�?

### 2. �
部变量�
单(需在实时数据库预�
�组�?

本文件涉及的�
部变量(�?PLC 通道变量):

| 变量�?| 类型 | 用�?| 断电保持 |
|---|---|---|---|
| SelectedUnit | integer | 当前选中单�
��?1~8 | �?|
| GlobalAlarmActive | integer | �
�局报警激活标�?| �?|
| GlobalMuteState | integer | �
�局消音状�?| �?|
| GlobalAckPending | integer | �
�局�
确认标�?| �?|
| CommStatus | integer | 在线单�
�计数 0~8 | �?|
| SysTimeString | string | 系统时间显示�?| �?|
| LoginTime | integer | 登录时间�?�? | �?|
| LastMouseTime | integer | 最后鼠标操作时�?| �?|
| ExitLogonEnabled | integer | 退出权限检查模�?| �?|
| U1_Online ~ U8_Online | integer | 8单�
�通讯在线状�?| �?|
| U1_Enable ~ U8_Enable | integer | 8单�
�使能�
�置 | **�?* |
| CurrentMenuGroup | integer | 当前菜单�?0=主菜�?1=单�
�操作/2=监控诊断/3=系统) | **�?* |
| CurrentUnitStr | string | "当前操作:X号单�
? | �?|
| Param_* (20�? | single/integer/bit | 参数编辑缓冲�?| �?|
| ParamValid / ParamInvalidStr | integer/string | 校验结果 | �?|
| ParamSrcUnit / ParamDstUnit | integer | 复制参数�?目标 | �?|
| SubWndMode | integer | 子窗口模�?0=复制/1=筛�?| �?|
| AlmFilterUnit / AlmFilterStr | integer/string | 报警筛�?| �?|
| TrendTimeRange / TrendRangeStr | integer/string | 趋势时间范围 | �?|
| TrendDisplayUnit | integer | 趋势显示单�
� | �?|
| PLC01~08_Status | integer | 8台PLC状�?| �?|
| MBPump01~08_Status | integer | 8个注射泵状�?| �?|
| MBFlow01~08_Status | integer | 8个流量计状�?| �?|
| CurrentUserStr / CurrentUserGroupStr | string | 当前用户/组显�?| �?|
| UnitEnableSummary | string | 使能单�
�汇总串 | �?|

### 3. 用户组组�?对应权限矩阵)

McgsPro 用户管理需在组态环境中预�
�建立 3 个用户组:
- `操作员组` (L1) �?含操作员子用�?4位数字密�?
- `维护组` (L2) �?含维护工程师子用�?6位数字密�?
- `管理员组` (L3) �?含管理员子用�?8位字符密�?

`!CheckUserGroup("维护�?) = 0` 表示当前用户属于维护�?或更高权限组,如果维护组是管理员组的子�?。本文件采用"维护�?OR 管理员组"嵌套 If 实现向下�
�容�?

### 4. 组对象存盘�
��?

脚本45�?`!SaveData(UnitEnableGroup)` 要求:
- 在实时数据库创建组对�?`UnitEnableGroup`
- �?U1_Enable~U8_Enable 加�
�该组对象
- 勾�?定时存储到磁�?+ 存盘周期
- `!FreshDataSave()` 立即刷盘(否则需�?0�?

### 5. 二次确认子窗口组�?

8个二次确认子窗口(脚本50~57)需�?McgsPro 用户窗口中分别创�?
- 子窗口_启动确认 / 子窗口_停止确认 / 子窗口_急停确认
- 子窗口_恢复默认确认 / 子窗口_�
除日志确认 / 子窗口_退出系统确�?
- 子窗口_单�
�选择 / 子窗口_复制参数确认 / 子窗口_日志浏览

每个子窗口�
组�?确认"�?取消"两个标准按钮构件,分别绑定对应 Click 脚本。子窗口尺寸建议 400×180(确认�?�?400×240(选择�?�?

### 6. �?v1.0 的主要差�?

| 差异�?| v1.0 (VBScript,错误) | v2.0 (McgsPro 类Basic,正确) |
|---|---|---|
| 循环 | `For i = 1 To 8 ... Next` | 显式展开 8 条赋值语�?|
| 多分�?| `ElseIf` | 嵌套 `If...Then...Else...EndIf` |
| 动态变量名 | `Execute("U" & i & "_CMD_Start = 1")` | `If SelectedUnit = 1 Then U1_CMD_Start = 1 EndIf` (8路分�? |
| 确认对话�?| `MsgBox(...)` | `!OpenSubWnd(子窗口_xxx确认, ..., 17)` |
| 打开窗口 | `!SwitchWindow("画面2")` (不存�? | `!CloseAllWindow("画面2_单�
�详�
")` |
| 权限检�?| `!CheckUser` (不存�? | `!CheckUserGroup("维护�?)` |
| 时间函数 | `Now()` / `DateDiff()` | `!TimeGetCurrentTime()` / 直接相减 |
| 变量声明 | `Dim x` (无类�? | `DIM x AS integer` |

### 7. 8单�
�扩展统一约定

凡涉�?�?个单�
�相同操�?的脚�?本文件采用以下两种写法之一:
1. **显式展开**(用于�
须同时操作8单�
�的场�?如脚�?/7/8/52):直接�?段If块或8条赋�?
2. **�?号为�?*(用于�?SelectedUnit 选择单单�
�操作的场景,如脚�?3/14/19~25/50/51):给出1号完整代�?+ 2~8号扩展说�?替换单�
��?

这是因为 McgsPro **不支�?Execute 动态构造变量名**,无法用循�?字符串拼接访�?U1_XXX~U8_XXX。组态时�
须�?8 套代码�
�部粘贴到对应�?8 个按�?Click 事件中�?

---



---

## L ������RTC Уʱ�ű���AQEX-51 ������

> �� 2026-09-13 ����ͨ����CSV �� VB900~VB905 ���ͱ��� INTEGER����ֹ SINGLE����
> BCD ת�������� McgsPro ϵͳ���� + `\` ������������ֹ `/` ��������������ر����������͡�

---

### �ű� 55��RTC �Զ�Уʱѭ�����ԣ�ѭ������ / RTC_Sync_Poll��

- **λ��**�����в��� -> ѭ������
- **ִ������**��1000 ms
- **��������**��MCGS CSV ���ͱ����� INTEGER����
  - U1_Need_RTC_Sync��V303.7��λ��ֻ����
  - U1_CMD_RTC_Sync��V0.6��λ����д��
  - U1_VB900_RTC_Year~U1_VB905_RTC_Second��VB900~VB905����������д��
- **���ر���**��y, m, d, h, mi, s��ȫ�����ͣ�
- **����**��PLC ����Уʱ��V303.7=1��ʱȫ�Զ�ȡ MCGS ����ʱ�� -> BCD -> д VB900~VB905 -> �� V0.6 ���� TODW��ͬʱ������ʾ��
- **MCGS ϵͳ����**��$Year/$Month/$Day/$Hour/$Minute/$Second ���ظ��������� 2026.0������ֵ������ʱ�Զ��ضϡ�

```vb
' RTC �Զ�Уʱѭ������ (����C: ȫ�Զ�+����ʾ)
' �� ����ʵ����Ŀ����֤ͨ�� (2026-09-13)

IF U1_Need_RTC_Sync = 1 THEN
    y = $Year - 2000
    U1_VB900_RTC_Year = (y \ 10) * 16 + (y - (y \ 10) * 10)

    m = $Month
    U1_VB901_RTC_Month = (m \ 10) * 16 + (m - (m \ 10) * 10)

    d = $Day
    U1_VB902_RTC_Day = (d \ 10) * 16 + (d - (d \ 10) * 10)

    h = $Hour
    U1_VB903_RTC_Hour = (h \ 10) * 16 + (h - (h \ 10) * 10)

    mi = $Minute
    U1_VB904_RTC_Minute = (mi \ 10) * 16 + (mi - (mi \ 10) * 10)

    s = $Second
    U1_VB905_RTC_Second = (s \ 10) * 16 + (s - (s \ 10) * 10)

    U1_CMD_RTC_Sync = 1
    !OpenSubWnd("RTC_Sync_Wnd", 200, 150, 400, 200)
ELSE
    !CloseSubWnd("RTC_Sync_Wnd")
END IF
```

---

### �ű� 56��RTC �ֶ�Уʱͬ����ť����ţ̌���¼� / btn_RTC_Sync��

- **λ��**��RTC_Sync_Wnd ���� -> btn_RTC_Sync ��ť -> ̧��ű�
- **����**��ѭ��������ȫ�Զ����˰�ť���������ס�BCD ת��ͬ�ű� 55��

```vb
' RTC �ֶ�Уʱͬ����ť (������)
' �� ����ʵ����Ŀ����֤ͨ�� (2026-09-13)

y = $Year - 2000
U1_VB900_RTC_Year = (y \ 10) * 16 + (y - (y \ 10) * 10)

m = $Month
U1_VB901_RTC_Month = (m \ 10) * 16 + (m - (m \ 10) * 10)

d = $Day
U1_VB902_RTC_Day = (d \ 10) * 16 + (d - (d \ 10) * 10)

h = $Hour
U1_VB903_RTC_Hour = (h \ 10) * 16 + (h - (h \ 10) * 10)

mi = $Minute
U1_VB904_RTC_Minute = (mi \ 10) * 16 + (mi - (mi \ 10) * 10)

s = $Second
U1_VB905_RTC_Second = (s \ 10) * 16 + (s - (s \ 10) * 10)

U1_CMD_RTC_Sync = 1
```

> ע���൥Ԫ���̱���ǰ׺ U1_ �滻Ϊ��Ӧ��Ԫ�ţ�U2_~U8_�������������䡣

---

**�ĵ�����** �� �� 57 �νű������ű�30.5��ΪĬ�ϰ�ť, L�����ű�55ȫ�Զ�+�ű�56�ֶ����ף�,���� A~L 12 ��������
