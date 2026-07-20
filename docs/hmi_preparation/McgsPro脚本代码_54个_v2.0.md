# AQUA-EXPO McgsPro 3.3.6 脚本代码 v2.0

**项目**: 8套缸单元药液配置加注控制系统
**HMI**: 昆仑通态 McgsPro 3.3.6 (TPC 触摸屏)
**配套文档**: McgsPro变量导入_8单元_v2.0.csv / HMI用户权限矩阵_v1.0.md / HMI画面架构规划文档.md
**用途**: 直接粘贴到 McgsPro 脚本编辑器,完成8画面+策略+子窗口的脚本组态
**Story**: AQEX-12 Story 2.1 (8画面组态) — v2.0 重写为纯正 McgsPro 类Basic语法

---

## 〇、重要说明:McgsPro 脚本语言与 VBScript 的差异

> **本版 v2.0 与 v1.0 的根本区别**:v1.0 误用 VBScript 语法(For...Next / Execute / MsgBox / !SwitchWindow / !CheckUser 等),这些在 McgsPro 3.3.6 中**均不支持**。v2.0 严格按 docs/reference/McgsProHelp_text/ 官方文档重写为类 Basic 语法。

### 1. 语言定位

McgsPro 脚本程序是**类 Basic 脚本语言**,不是 VBScript,也不是 VBA。它只是"类似普通的 Basic 语言",但功能子集远小于 VBScript。

### 2. 不支持的 VBScript / VBA 语法(必须避免)

| 不支持语法 | 替代方案 |
|---|---|
| `For i = 1 To 8 ... Next` | 用 `While...EndWhile` + 整型索引,或直接展开为 8 条赋值语句 |
| `Exit For` / `Exit Sub` / `Exit Function` | 用 `Exit` (退出整个脚本) 或 `Break` (跳出 While) |
| `Sub ... End Sub` / `Function ... End Function` | McgsPro 不支持自定义子程序/子函数,所有逻辑必须内联 |
| `ElseIf ... Then` | 用嵌套 `If...Then...Else...EndIf` 实现多分支 |
| `Execute("U" & i & "_CMD_Mute = 1")` | **无法动态构造变量名**,必须显式写出 8 个单元的赋值语句 |
| `MsgBox(...)` / `InputBox(...)` | 用子窗口(!OpenSubWnd)实现确认/选择对话框 |
| `!OpenWindow` / `!SwitchWindow` | 用 `!SetWindow(窗口,1)` 打开、`!CloseAllWindow(name)` 关闭并切换 |
| `!CheckUser` | 用 `!CheckUserGroup("组名")` (返回 0=属于 / 1=不属于) |
| `GetValue(name)` / `SetValue(name,v)` | 直接引用变量名 `U1_CMD_Start = 1` |
| `Format(...)` / `CDate(...)` / `DateDiff(...)` | 用 `!TimeStr2I` / `!TimeI2Str` / `!TimeGetSpan` 等时间函数 |
| `Dim x` (无类型) | 必须写 `DIM x AS integer` (4 种类型: byte/integer/single/string) |
| 数组下标从 0 开始 | McgsPro 数组下标**从 1 开始** |

### 3. McgsPro 支持的语法子集

- **赋值**: `变量 = 表达式`
- **条件**: `If 表达式 Then 语句` / `If 表达式 Then ... EndIf` / `If 表达式 Then ... Else ... EndIf`
- **循环**: `While 条件表达式 ... EndWhile`
- **跳出**: `Break` (跳出 While) / `Exit` (退出整个脚本)
- **注释**: `' 单引号开头
- **声明**: `DIM <变量名> AS <类型>` (类型: byte / integer / single / string)
- **数组**: `DIM <变量名>(<长度>) AS <类型>`,访问 `arr[index]`,index 从 1 开始
- **多语句同行**: 用 `:` 分隔
- **联行符**: 行尾 `_` 连接下一行
- **运算符**: `^ * / \ + - MOD AND OR NOT XOR > >= = <= < <>`

### 4. 关键系统函数(本工程使用)

| 函数 | 用途 |
|---|---|
| `!OpenSubWnd(窗口,X,Y,宽,高,模式)` | 打开子窗口(模式位:1=模态/2=菜单/16=边框/32=跟随鼠标/64=自动尺寸) |
| `!CloseAllSubWnd()` | 关闭当前标准窗口下所有子窗口 |
| `!CloseSubWnd(窗口对象)` | 关闭指定子窗口 |
| `!CloseAllWindow(WndName)` | 关闭所有窗口(WndName 非空则保留并打开它) |
| `!SetWindow(窗口对象,Op)` | Op=1打开可见/2打开不可见/3关闭/4打印/5刷新 |
| `!SetDevice(设备名,Op,"")` | Op=1启动设备/2停止/3测状态/4启动一次/5改周期/6命令 |
| `!SetStgy(策略名)` | 异步启动用户策略 |
| `!SetStgyMode(策略名)` | 同步启动用户策略 |
| `!Beep()` | 蜂鸣 |
| `!Sleep(毫秒)` | 延时 |
| `!LogOn()` / `!LogOff()` | 弹登录框 / 注销 |
| `!CheckUserGroup("组名")` | 返回 0=属于,1=不属于 |
| `!GetCurrentUser()` / `!GetCurrentGroup()` | 当前用户名 / 当前用户组(多组用 0x01 分隔) |
| `!Editusers()` / `!ChangePassword()` | 用户管理窗口 / 修改密码窗口 |
| `!EnableExitLogon(n)` | n=0不检查/1检查/2超时提示/3超时静默 |
| `!SaveData(数据对象)` | 立即存盘(组对象需勾选存盘属性,60秒后自动刷盘或 !FreshDataSave) |
| `!FreshDataSave()` | 立即刷盘 |
| `!SetAlmInfo(对象,报警序号,报警信息)` | 设置报警信息 |
| `!SetAlmValue(对象,报警序号,值,标志)` | 设置报警限值 |
| `!AnswerAlm(对象,报警序号)` | 应答报警(-1=全部) |
| `!ClearHistoryAlarmData()` | 清除历史报警数据 |
| `!OperationLogClear()` | 清除操作日志 |
| `!TimeStr2I("YYYY-MM-DD HH:MM:SS")` | 时间字符串转整数 |
| `!TimeI2Str(iTime,格式)` | 整数转时间字符串 |
| `!TimeGetCurrentTime()` | 当前时间整数 |
| `!TimeGetSpan(t1,t2)` | 时间差(秒) |

### 5. 系统变量(以 `$` 开头,只读)

`$Year $Month $Day $Hour $Minute $Second $Week $Date $Time $Timer $RunTime $UserName`

### 6. 用户组命名(对应权限矩阵)

- `操作员组` — L1 (日常监控+基础操作)
- `维护组` — L2 (手动控制+参数时间组)
- `管理员组` — L3 (浓度参数+单元使能+系统维护)

### 7. 8单元变量扩展约定

本工程 8 套单元变量命名规则:`U<单元号>_XXX`,如 `U1_CMD_Start` ~ `U8_CMD_Start`。由于 McgsPro **不支持 Execute 动态构造变量名**,凡涉及"对 8 个单元循环操作"的脚本,本文件采用**显式展开 8 条赋值语句**的写法,而非 For 循环。涉及"以 1 号为例"的相似脚本,会给出 1 号完整代码 + 2~8 号扩展说明。

### 8. 脚本编号索引(共 57 个)

| 分区 | 编号 | 数量 | 位置 |
|---|---|---|---|
| A. 工程启动策略 | 1 | 1 | 启动策略 |
| B. 周期策略 | 2~3 | 2 | 循环策略 |
| C. 画面1_总览 | 4~9 | 6 | 窗口/构件 |
| D. 画面2_单元详情 | 10~17 | 8 | 窗口/构件 |
| E. 画面3_手动控制 | 18~26 | 9 | 窗口/构件 |
| F. 画面4_参数设置 | 27~32 | 6 | 窗口/构件 |
| G. 画面5_报警日志 | 33~36 | 4 | 窗口/构件 |
| H. 画面6_趋势曲线 | 37~39 | 3 | 窗口/构件 |
| I. 画面7_通讯维护 | 40~43 | 4 | 窗口/构件 |
| J. 画面8_系统设置 | 44~49 | 6 | 窗口/构件 |
| K. 二次确认子窗口 | 50~57 | 8 | 子窗口构件 |

> 说明:任务标题"54个"按 A~J(共 49 个主脚本)+ K 中 6 个二次确认子窗口(50~55)计;实际 K 区还包含 56 单元选择和 57 复制参数确认 2 个子窗口,合计 57 个。本文件全部列出。

---

## 一、A. 工程启动策略脚本

### 脚本 1:启动策略脚本

- **编号**: 1
- **用途**: 工程启动时初始化内部变量、启动所有 PLC 设备、加载用户配置
- **位置**: 运行策略 → 启动策略 (系统固有策略块)
- **触发方式**: 系统启动时自动执行一次

```
' ============================================
' AQUA-EXPO 启动策略脚本
' 功能: 初始化内部变量 + 启动8台PLC设备 + 加载用户配置
' 依赖变量: SelectedUnit / GlobalAlarmActive / GlobalMuteState /
'           U1_Enable~U8_Enable / U1_Online~U8_Online / CommStatus /
'           LoginTime / ExitLogonEnabled
' ============================================

' --- 1. 初始化选中单元(默认1号) ---
SelectedUnit = 1

' --- 2. 初始化全局状态 ---
GlobalAlarmActive = 0
GlobalMuteState = 0
GlobalAckPending = 0
LoginTime = 0
ExitLogonEnabled = 1

' --- 3. 初始化单元使能(从断电保持区读取,首次启动默认1号使能) ---
' U1_Enable~U8_Enable 已配置为断电保持内部变量,此处仅在值为0时给默认值
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

' --- 4. 初始化通讯在线状态(待首次轮询后更新) ---
U1_Online = 0
U2_Online = 0
U3_Online = 0
U4_Online = 0
U5_Online = 0
U6_Online = 0
U7_Online = 0
U8_Online = 0

' --- 5. 初始化通讯状态汇总 ---
CommStatus = 0

' --- 6. 启动8台PLC设备(设备名: PLC_01~PLC_08) ---
!SetDevice(PLC_01, 1, "")
!SetDevice(PLC_02, 1, "")
!SetDevice(PLC_03, 1, "")
!SetDevice(PLC_04, 1, "")
!SetDevice(PLC_05, 1, "")
!SetDevice(PLC_06, 1, "")
!SetDevice(PLC_07, 1, "")
!SetDevice(PLC_08, 1, "")

' --- 7. 启动16个Modbus从站设备(每套PLC 2个: 注射泵+流量计) ---
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

' --- 8. 开启操作日志 + 退出权限检查 ---
!OperationLogEnable()
!EnableExitLogon(ExitLogonEnabled)

' --- 9. 打开画面1_总览 ---
!SetWindow(画面1_总览, 1)
```

---

## 二、B. 周期策略脚本

### 脚本 2:500ms 周期策略

- **编号**: 2
- **用途**: 周期清零命令位(模拟上升沿) + 更新通讯在线状态 + 更新 CommStatus 汇总
- **位置**: 运行策略 → 循环策略 (用户创建,命名"循环策略_500ms")
- **触发方式**: 定时循环,周期 500ms

```
' ============================================
' 500ms 周期策略
' 功能1: 清零8个单元的命令位(模拟脉冲上升沿,PLC侧用下降沿检测)
' 功能2: 检测8台PLC通讯状态,更新 U1_Online~U8_Online 和 CommStatus
' 注意: McgsPro 不支持 For...Next,8 个单元显式展开
' ============================================

' --- 1. 清零1号单元命令位 ---
If U1_CMD_Start = 1 Then
    U1_CMD_Start = 0
EndIf
If U1_CMD_Stop = 1 Then
    U1_CMD_Stop = 0
EndIf
If U1_CMD_Ack = 1 Then
    U1_CMD_Ack = 0
EndIf
If U1_CMD_Mute = 1 Then
    U1_CMD_Mute = 0
EndIf
If U1_CMD_RelayAck = 1 Then
    U1_CMD_RelayAck = 0
EndIf

' --- 2. 清零2号单元命令位 ---
If U2_CMD_Start = 1 Then
    U2_CMD_Start = 0
EndIf
If U2_CMD_Stop = 1 Then
    U2_CMD_Stop = 0
EndIf
If U2_CMD_Ack = 1 Then
    U2_CMD_Ack = 0
EndIf
If U2_CMD_Mute = 1 Then
    U2_CMD_Mute = 0
EndIf
If U2_CMD_RelayAck = 1 Then
    U2_CMD_RelayAck = 0
EndIf

' --- 3. 清零3号单元命令位 ---
If U3_CMD_Start = 1 Then
    U3_CMD_Start = 0
EndIf
If U3_CMD_Stop = 1 Then
    U3_CMD_Stop = 0
EndIf
If U3_CMD_Ack = 1 Then
    U3_CMD_Ack = 0
EndIf
If U3_CMD_Mute = 1 Then
    U3_CMD_Mute = 0
EndIf
If U3_CMD_RelayAck = 1 Then
    U3_CMD_RelayAck = 0
EndIf

' --- 4. 清零4号单元命令位 ---
If U4_CMD_Start = 1 Then
    U4_CMD_Start = 0
EndIf
If U4_CMD_Stop = 1 Then
    U4_CMD_Stop = 0
EndIf
If U4_CMD_Ack = 1 Then
    U4_CMD_Ack = 0
EndIf
If U4_CMD_Mute = 1 Then
    U4_CMD_Mute = 0
EndIf
If U4_CMD_RelayAck = 1 Then
    U4_CMD_RelayAck = 0
EndIf

' --- 5. 清零5号单元命令位 ---
If U5_CMD_Start = 1 Then
    U5_CMD_Start = 0
EndIf
If U5_CMD_Stop = 1 Then
    U5_CMD_Stop = 0
EndIf
If U5_CMD_Ack = 1 Then
    U5_CMD_Ack = 0
EndIf
If U5_CMD_Mute = 1 Then
    U5_CMD_Mute = 0
EndIf
If U5_CMD_RelayAck = 1 Then
    U5_CMD_RelayAck = 0
EndIf

' --- 6. 清零6号单元命令位 ---
If U6_CMD_Start = 1 Then
    U6_CMD_Start = 0
EndIf
If U6_CMD_Stop = 1 Then
    U6_CMD_Stop = 0
EndIf
If U6_CMD_Ack = 1 Then
    U6_CMD_Ack = 0
EndIf
If U6_CMD_Mute = 1 Then
    U6_CMD_Mute = 0
EndIf
If U6_CMD_RelayAck = 1 Then
    U6_CMD_RelayAck = 0
EndIf

' --- 7. 清零7号单元命令位 ---
If U7_CMD_Start = 1 Then
    U7_CMD_Start = 0
EndIf
If U7_CMD_Stop = 1 Then
    U7_CMD_Stop = 0
EndIf
If U7_CMD_Ack = 1 Then
    U7_CMD_Ack = 0
EndIf
If U7_CMD_Mute = 1 Then
    U7_CMD_Mute = 0
EndIf
If U7_CMD_RelayAck = 1 Then
    U7_CMD_RelayAck = 0
EndIf

' --- 8. 清零8号单元命令位 ---
If U8_CMD_Start = 1 Then
    U8_CMD_Start = 0
EndIf
If U8_CMD_Stop = 1 Then
    U8_CMD_Stop = 0
EndIf
If U8_CMD_Ack = 1 Then
    U8_CMD_Ack = 0
EndIf
If U8_CMD_Mute = 1 Then
    U8_CMD_Mute = 0
EndIf
If U8_CMD_RelayAck = 1 Then
    U8_CMD_RelayAck = 0
EndIf

' --- 9. 更新8台PLC通讯在线状态 ---
' !SetDevice(name,3,"") 返回 1=启动状态(在线), 0=停止状态(离线)
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

' --- 10. 更新通讯状态汇总 CommStatus (0~8,在线单元数) ---
CommStatus = U1_Online + U2_Online + U3_Online + U4_Online + U5_Online + U6_Online + U7_Online + U8_Online

' --- 11. 更新全局报警状态(任一使能+在线单元有报警则置1) ---
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

### 脚本 3:1 秒周期策略

- **编号**: 3
- **用途**: 更新系统时间显示 + 检查登录超时
- **位置**: 运行策略 → 循环策略 (用户创建,命名"循环策略_1s")
- **触发方式**: 定时循环,周期 1000ms

```
' ============================================
' 1秒周期策略
' 功能1: 拼接 $Date + $Time 写入 SysTimeString (供画面顶部显示)
' 功能2: 检查登录超时(15分钟无操作自动注销)
' ============================================

' --- 1. 更新系统时间显示字符串 ---
SysTimeString = $Date + " " + $Time

' --- 2. 检查登录超时 ---
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
        ' 15分钟 = 900秒
        If spanSec > 900 Then
            !LogOff()
            LoginTime = 0
            !Beep()
        EndIf
    EndIf
EndIf

' --- 3. 检查 EnableExitLogon 超时模式(2=超时提示,3=超时静默) ---
' 由 !EnableExitLogon 内部处理,此处仅记录最近操作时间
LastMouseTime = !GetLastMouseActionTime()
```

---

## 三、C. 画面1_总览脚本

### 脚本 4:画面1 窗口打开脚本

- **编号**: 4
- **用途**: 初始化画面1变量,关闭所有子窗口,刷新8单元卡片状态
- **位置**: 用户窗口 → 画面1_总览 → Load 事件
- **触发方式**: 窗口装载时

```
' ============================================
' 画面1_总览 Load 脚本
' 功能: 关闭残留子窗口 + 刷新总览显示
' ============================================

' --- 1. 关闭所有子窗口(防止跨画面残留) ---
!CloseAllSubWnd()

' --- 2. 初始化选中单元为0(未选中) ---
SelectedUnit = 0

' --- 3. 更新系统时间显示 ---
SysTimeString = $Date + " " + $Time

' --- 4. 刷新全局报警/消音状态(由500ms周期策略持续更新,此处只读) ---
' GlobalAlarmActive / GlobalMuteState 由周期策略维护
```

### 脚本 5:1号单元卡片点击

- **编号**: 5
- **用途**: 点击1号单元卡片,设置 SelectedUnit=1,打开画面2_单元详情子窗口
- **位置**: 用户窗口 → 画面1_总览 → 1号单元卡片构件 → Click 事件
- **触发方式**: 卡片鼠标单击

```
' ============================================
' 1号单元卡片点击脚本
' 功能: 仅在使能+在线时允许进入详情页
' ============================================

' --- 1. 检查单元使能+在线状态 ---
If U1_Enable = 0 Then
    !Beep()
    Exit
EndIf
If U1_Online = 0 Then
    !Beep()
    Exit
EndIf

' --- 2. 设置选中单元号 ---
SelectedUnit = 1

' --- 3. 关闭所有子窗口,打开画面2_单元详情 ---
!CloseAllSubWnd()
!SetWindow(画面2_单元详情, 1)
```

### 脚本 6:2~8号单元卡片点击(合并写法)

- **编号**: 6
- **用途**: 2~8号单元卡片点击,逻辑同脚本5,仅单元号不同
- **位置**: 用户窗口 → 画面1_总览 → 2~8号单元卡片构件 → Click 事件(7个独立脚本)
- **触发方式**: 卡片鼠标单击
- **扩展方法**: 将脚本5中的 `U1_Enable` / `U1_Online` / `SelectedUnit = 1` 替换为对应单元号

**2号单元卡片点击**:
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
!SetWindow(画面2_单元详情, 1)
```

**3号单元卡片点击**:
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
!SetWindow(画面2_单元详情, 1)
```

**4号单元卡片点击**:
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
!SetWindow(画面2_单元详情, 1)
```

**5号单元卡片点击**:
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
!SetWindow(画面2_单元详情, 1)
```

**6号单元卡片点击**:
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
!SetWindow(画面2_单元详情, 1)
```

**7号单元卡片点击**:
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
!SetWindow(画面2_单元详情, 1)
```

**8号单元卡片点击**:
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
!SetWindow(画面2_单元详情, 1)
```

### 脚本 7:全局消音按钮

- **编号**: 7
- **用途**: 对所有使能+在线单元下发消音命令(直接执行,无需二次确认)
- **位置**: 用户窗口 → 画面1_总览 → 全局消音按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 全局消音按钮脚本
' 功能: 对所有使能+在线单元置 CMD_Mute=1 (500ms周期策略会自动清零)
' ============================================

' --- 1. 蜂鸣提示 ---
!Beep()

' --- 2. 对8个使能+在线单元下发消音命令 ---
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

' --- 3. 更新全局消音状态 ---
GlobalMuteState = 1
```

### 脚本 8:全局报警确认按钮

- **编号**: 8
- **用途**: 对所有使能+在线单元下发报警确认命令(直接执行)
- **位置**: 用户窗口 → 画面1_总览 → 全局报警确认按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 全局报警确认按钮脚本
' 功能: 对所有使能+在线单元置 CMD_Ack=1
' 注意: 仅确认当前激活报警,不影响历史日志
' ============================================

' --- 1. 蜂鸣提示 ---
!Beep()

' --- 2. 对8个使能+在线单元下发报警确认命令 ---
If U1_Enable = 1 Then
    If U1_Online = 1 Then
        U1_CMD_Ack = 1
    EndIf
EndIf
If U2_Enable = 1 Then
    If U2_Online = 1 Then
        U2_CMD_Ack = 1
    EndIf
EndIf
If U3_Enable = 1 Then
    If U3_Online = 1 Then
        U3_CMD_Ack = 1
    EndIf
EndIf
If U4_Enable = 1 Then
    If U4_Online = 1 Then
        U4_CMD_Ack = 1
    EndIf
EndIf
If U5_Enable = 1 Then
    If U5_Online = 1 Then
        U5_CMD_Ack = 1
    EndIf
EndIf
If U6_Enable = 1 Then
    If U6_Online = 1 Then
        U6_CMD_Ack = 1
    EndIf
EndIf
If U7_Enable = 1 Then
    If U7_Online = 1 Then
        U7_CMD_Ack = 1
    EndIf
EndIf
If U8_Enable = 1 Then
    If U8_Online = 1 Then
        U8_CMD_Ack = 1
    EndIf
EndIf

' --- 3. 更新全局确认状态 ---
GlobalAckPending = 0
```

### 脚本 9:急停按钮

- **编号**: 9
- **用途**: 急停按钮,弹出二次确认子窗口,确认后对8个单元下发 CMD_Stop=1
- **位置**: 用户窗口 → 画面1_总览 → 急停按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 急停按钮脚本
' 功能: 弹出急停确认子窗口(脚本52负责执行)
' 子窗口模式: 模态(1) + 边框(16) = 17
' ============================================

' --- 1. 蜂鸣强提示 ---
!Beep()

' --- 2. 打开急停确认子窗口(模态+边框,居中位置 240,180,400,180) ---
!OpenSubWnd(子窗口_急停确认, 240, 180, 400, 180, 17)
```

---

## 四、D. 画面2_单元详情脚本

### 脚本 10:画面2 窗口打开脚本

- **编号**: 10
- **用途**: 根据 SelectedUnit 加载对应单元的数据,显示"当前操作:X号单元"
- **位置**: 用户窗口 → 画面2_单元详情 → Load 事件
- **触发方式**: 窗口装载时

```
' ============================================
' 画面2_单元详情 Load 脚本
' 功能: 根据 SelectedUnit 切换数据绑定上下文
' 注意: McgsPro 不支持动态变量名,构件的数据绑定通过组态时
'       用"表达式"引用 SelectedUnit 选择显示,或用8套独立组态+显隐切换
' ============================================

' --- 1. 关闭残留子窗口 ---
!CloseAllSubWnd()

' --- 2. 校验 SelectedUnit 范围(1~8) ---
If SelectedUnit < 1 Then
    !CloseAllWindow("画面1_总览")
    Exit
EndIf
If SelectedUnit > 8 Then
    !CloseAllWindow("画面1_总览")
    Exit
EndIf

' --- 3. 拼接当前操作字符串 ---
If SelectedUnit = 1 Then
    CurrentUnitStr = "当前操作:1号单元"
EndIf
If SelectedUnit = 2 Then
    CurrentUnitStr = "当前操作:2号单元"
EndIf
If SelectedUnit = 3 Then
    CurrentUnitStr = "当前操作:3号单元"
EndIf
If SelectedUnit = 4 Then
    CurrentUnitStr = "当前操作:4号单元"
EndIf
If SelectedUnit = 5 Then
    CurrentUnitStr = "当前操作:5号单元"
EndIf
If SelectedUnit = 6 Then
    CurrentUnitStr = "当前操作:6号单元"
EndIf
If SelectedUnit = 7 Then
    CurrentUnitStr = "当前操作:7号单元"
EndIf
If SelectedUnit = 8 Then
    CurrentUnitStr = "当前操作:8号单元"
EndIf

' --- 4. 更新系统时间显示 ---
SysTimeString = $Date + " " + $Time
```

### 脚本 11:启动按钮

- **编号**: 11
- **用途**: 启动当前选中单元(需维护组权限+二次确认)
- **位置**: 用户窗口 → 画面2_单元详情 → 启动按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 启动按钮脚本
' 功能: 权限校验 → 打开启动确认子窗口(脚本50负责执行)
' ============================================

' --- 1. 校验维护组权限(L2以上) ---
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 打开启动确认子窗口(模态+边框) ---
!OpenSubWnd(子窗口_启动确认, 240, 180, 400, 180, 17)
```

### 脚本 12:停止按钮

- **编号**: 12
- **用途**: 停止当前选中单元(二次确认子窗口)
- **位置**: 用户窗口 → 画面2_单元详情 → 停止按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 停止按钮脚本
' 功能: 弹出停止确认子窗口(脚本51负责执行)
' ============================================

' --- 1. 蜂鸣提示 ---
!Beep()

' --- 2. 打开停止确认子窗口(模态+边框) ---
!OpenSubWnd(子窗口_停止确认, 240, 180, 400, 180, 17)
```

### 脚本 13:报警确认按钮

- **编号**: 13
- **用途**: 对当前选中单元下发报警确认命令
- **位置**: 用户窗口 → 画面2_单元详情 → 报警确认按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 报警确认按钮脚本(以当前选中单元为例)
' 功能: 对 SelectedUnit 对应单元置 CMD_Ack=1
' ============================================

!Beep()

If SelectedUnit = 1 Then
    U1_CMD_Ack = 1
EndIf
If SelectedUnit = 2 Then
    U2_CMD_Ack = 1
EndIf
If SelectedUnit = 3 Then
    U3_CMD_Ack = 1
EndIf
If SelectedUnit = 4 Then
    U4_CMD_Ack = 1
EndIf
If SelectedUnit = 5 Then
    U5_CMD_Ack = 1
EndIf
If SelectedUnit = 6 Then
    U6_CMD_Ack = 1
EndIf
If SelectedUnit = 7 Then
    U7_CMD_Ack = 1
EndIf
If SelectedUnit = 8 Then
    U8_CMD_Ack = 1
EndIf
```

### 脚本 14:消音按钮

- **编号**: 14
- **用途**: 对当前选中单元下发消音命令
- **位置**: 用户窗口 → 画面2_单元详情 → 消音按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 消音按钮脚本
' 功能: 对 SelectedUnit 对应单元置 CMD_Mute=1
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
- **用途**: 打开画面3_手动控制子窗口(需维护组权限)
- **位置**: 用户窗口 → 画面2_单元详情 → 手动控制按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 手动控制按钮脚本
' 功能: 权限校验(L2维护组) → 打开画面3_手动控制子窗口
' ============================================

' --- 1. 校验维护组权限 ---
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 打开画面3_手动控制子窗口(模态+边框,800x600) ---
!OpenSubWnd(画面3_手动控制, 80, 60, 800, 600, 17)
```

### 脚本 16:参数设置按钮

- **编号**: 16
- **用途**: 打开画面4_参数设置子窗口(需维护组权限)
- **位置**: 用户窗口 → 画面2_单元详情 → 参数设置按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 参数设置按钮脚本
' 功能: 权限校验(L2维护组) → 打开画面4_参数设置子窗口
' ============================================

' --- 1. 校验维护组权限 ---
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 打开画面4_参数设置子窗口(模态+边框,800x600) ---
!OpenSubWnd(画面4_参数设置, 80, 60, 800, 600, 17)
```

### 脚本 17:返回按钮

- **编号**: 17
- **用途**: 关闭所有子窗口,返回画面1_总览
- **位置**: 用户窗口 → 画面2_单元详情 → 返回按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本
' 功能: 关闭所有子窗口,关闭当前画面,打开画面1_总览
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("画面1_总览")
```

---

## 五、E. 画面3_手动控制脚本

### 脚本 18:画面3 窗口打开脚本

- **编号**: 18
- **用途**: 初始化手动控制画面,显示当前选中单元
- **位置**: 用户窗口 → 画面3_手动控制 → Load 事件
- **触发方式**: 子窗口装载时

```
' ============================================
' 画面3_手动控制 Load 脚本
' 功能: 显示"当前操作:X号单元(手动模式)"
' ============================================

If SelectedUnit = 1 Then
    CurrentUnitStr = "当前操作:1号单元 (手动模式)"
EndIf
If SelectedUnit = 2 Then
    CurrentUnitStr = "当前操作:2号单元 (手动模式)"
EndIf
If SelectedUnit = 3 Then
    CurrentUnitStr = "当前操作:3号单元 (手动模式)"
EndIf
If SelectedUnit = 4 Then
    CurrentUnitStr = "当前操作:4号单元 (手动模式)"
EndIf
If SelectedUnit = 5 Then
    CurrentUnitStr = "当前操作:5号单元 (手动模式)"
EndIf
If SelectedUnit = 6 Then
    CurrentUnitStr = "当前操作:6号单元 (手动模式)"
EndIf
If SelectedUnit = 7 Then
    CurrentUnitStr = "当前操作:7号单元 (手动模式)"
EndIf
If SelectedUnit = 8 Then
    CurrentUnitStr = "当前操作:8号单元 (手动模式)"
EndIf
```

### 脚本 19:阀A 手动开/关

- **编号**: 19
- **用途**: 手动开/关阀A(需维护组权限)。开按钮置 Manual_ValveA=1,关按钮置 0
- **位置**: 用户窗口 → 画面3_手动控制 → 阀A开按钮 / 阀A关按钮 → Click 事件
- **触发方式**: 按钮单击

**阀A 开按钮**(以当前选中单元为例):
```
' --- 1. 校验维护组权限 ---
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 置 Manual_ValveA=1 ---
If SelectedUnit = 1 Then
    U1_Manual_ValveA = 1
EndIf
If SelectedUnit = 2 Then
    U2_Manual_ValveA = 1
EndIf
If SelectedUnit = 3 Then
    U3_Manual_ValveA = 1
EndIf
If SelectedUnit = 4 Then
    U4_Manual_ValveA = 1
EndIf
If SelectedUnit = 5 Then
    U5_Manual_ValveA = 1
EndIf
If SelectedUnit = 6 Then
    U6_Manual_ValveA = 1
EndIf
If SelectedUnit = 7 Then
    U7_Manual_ValveA = 1
EndIf
If SelectedUnit = 8 Then
    U8_Manual_ValveA = 1
EndIf

!Beep()
```

**阀A 关按钮**(以当前选中单元为例):
```
' --- 1. 校验维护组权限 ---
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 置 Manual_ValveA=0 ---
If SelectedUnit = 1 Then
    U1_Manual_ValveA = 0
EndIf
If SelectedUnit = 2 Then
    U2_Manual_ValveA = 0
EndIf
If SelectedUnit = 3 Then
    U3_Manual_ValveA = 0
EndIf
If SelectedUnit = 4 Then
    U4_Manual_ValveA = 0
EndIf
If SelectedUnit = 5 Then
    U5_Manual_ValveA = 0
EndIf
If SelectedUnit = 6 Then
    U6_Manual_ValveA = 0
EndIf
If SelectedUnit = 7 Then
    U7_Manual_ValveA = 0
EndIf
If SelectedUnit = 8 Then
    U8_Manual_ValveA = 0
EndIf

!Beep()
```

### 脚本 20:阀B 手动开/关

- **编号**: 20
- **用途**: 手动开/关阀B(需维护组权限)
- **位置**: 用户窗口 → 画面3_手动控制 → 阀B开按钮 / 阀B关按钮 → Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 将脚本19中的 `Manual_ValveA` 替换为 `Manual_ValveB`

**阀B 开按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_ValveB = 1
EndIf
If SelectedUnit = 2 Then
    U2_Manual_ValveB = 1
EndIf
If SelectedUnit = 3 Then
    U3_Manual_ValveB = 1
EndIf
If SelectedUnit = 4 Then
    U4_Manual_ValveB = 1
EndIf
If SelectedUnit = 5 Then
    U5_Manual_ValveB = 1
EndIf
If SelectedUnit = 6 Then
    U6_Manual_ValveB = 1
EndIf
If SelectedUnit = 7 Then
    U7_Manual_ValveB = 1
EndIf
If SelectedUnit = 8 Then
    U8_Manual_ValveB = 1
EndIf

!Beep()
```

**阀B 关按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_ValveB = 0
EndIf
If SelectedUnit = 2 Then
    U2_Manual_ValveB = 0
EndIf
If SelectedUnit = 3 Then
    U3_Manual_ValveB = 0
EndIf
If SelectedUnit = 4 Then
    U4_Manual_ValveB = 0
EndIf
If SelectedUnit = 5 Then
    U5_Manual_ValveB = 0
EndIf
If SelectedUnit = 6 Then
    U6_Manual_ValveB = 0
EndIf
If SelectedUnit = 7 Then
    U7_Manual_ValveB = 0
EndIf
If SelectedUnit = 8 Then
    U8_Manual_ValveB = 0
EndIf

!Beep()
```

### 脚本 21:阀C 手动开/关

- **编号**: 21
- **用途**: 手动开/关阀C(需维护组权限)
- **位置**: 用户窗口 → 画面3_手动控制 → 阀C开按钮 / 阀C关按钮 → Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 将脚本19中的 `Manual_ValveA` 替换为 `Manual_ValveC`

**阀C 开按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_ValveC = 1
EndIf
If SelectedUnit = 2 Then
    U2_Manual_ValveC = 1
EndIf
If SelectedUnit = 3 Then
    U3_Manual_ValveC = 1
EndIf
If SelectedUnit = 4 Then
    U4_Manual_ValveC = 1
EndIf
If SelectedUnit = 5 Then
    U5_Manual_ValveC = 1
EndIf
If SelectedUnit = 6 Then
    U6_Manual_ValveC = 1
EndIf
If SelectedUnit = 7 Then
    U7_Manual_ValveC = 1
EndIf
If SelectedUnit = 8 Then
    U8_Manual_ValveC = 1
EndIf

!Beep()
```

**阀C 关按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_ValveC = 0
EndIf
If SelectedUnit = 2 Then
    U2_Manual_ValveC = 0
EndIf
If SelectedUnit = 3 Then
    U3_Manual_ValveC = 0
EndIf
If SelectedUnit = 4 Then
    U4_Manual_ValveC = 0
EndIf
If SelectedUnit = 5 Then
    U5_Manual_ValveC = 0
EndIf
If SelectedUnit = 6 Then
    U6_Manual_ValveC = 0
EndIf
If SelectedUnit = 7 Then
    U7_Manual_ValveC = 0
EndIf
If SelectedUnit = 8 Then
    U8_Manual_ValveC = 0
EndIf

!Beep()
```

### 脚本 22:泵1 手动开/关

- **编号**: 22
- **用途**: 手动开/关潜水泵1(需维护组权限)
- **位置**: 用户窗口 → 画面3_手动控制 → 泵1开按钮 / 泵1关按钮 → Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 将脚本19中的 `Manual_ValveA` 替换为 `Manual_Pump1`

**泵1 开按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_Pump1 = 1
EndIf
If SelectedUnit = 2 Then
    U2_Manual_Pump1 = 1
EndIf
If SelectedUnit = 3 Then
    U3_Manual_Pump1 = 1
EndIf
If SelectedUnit = 4 Then
    U4_Manual_Pump1 = 1
EndIf
If SelectedUnit = 5 Then
    U5_Manual_Pump1 = 1
EndIf
If SelectedUnit = 6 Then
    U6_Manual_Pump1 = 1
EndIf
If SelectedUnit = 7 Then
    U7_Manual_Pump1 = 1
EndIf
If SelectedUnit = 8 Then
    U8_Manual_Pump1 = 1
EndIf

!Beep()
```

**泵1 关按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_Pump1 = 0
EndIf
If SelectedUnit = 2 Then
    U2_Manual_Pump1 = 0
EndIf
If SelectedUnit = 3 Then
    U3_Manual_Pump1 = 0
EndIf
If SelectedUnit = 4 Then
    U4_Manual_Pump1 = 0
EndIf
If SelectedUnit = 5 Then
    U5_Manual_Pump1 = 0
EndIf
If SelectedUnit = 6 Then
    U6_Manual_Pump1 = 0
EndIf
If SelectedUnit = 7 Then
    U7_Manual_Pump1 = 0
EndIf
If SelectedUnit = 8 Then
    U8_Manual_Pump1 = 0
EndIf

!Beep()
```

### 脚本 23:泵2 手动开/关

- **编号**: 23
- **用途**: 手动开/关潜水泵2(需维护组权限)
- **位置**: 用户窗口 → 画面3_手动控制 → 泵2开按钮 / 泵2关按钮 → Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 将脚本22中的 `Manual_Pump1` 替换为 `Manual_Pump2`

**泵2 开按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_Pump2 = 1
EndIf
If SelectedUnit = 2 Then
    U2_Manual_Pump2 = 1
EndIf
If SelectedUnit = 3 Then
    U3_Manual_Pump2 = 1
EndIf
If SelectedUnit = 4 Then
    U4_Manual_Pump2 = 1
EndIf
If SelectedUnit = 5 Then
    U5_Manual_Pump2 = 1
EndIf
If SelectedUnit = 6 Then
    U6_Manual_Pump2 = 1
EndIf
If SelectedUnit = 7 Then
    U7_Manual_Pump2 = 1
EndIf
If SelectedUnit = 8 Then
    U8_Manual_Pump2 = 1
EndIf

!Beep()
```

**泵2 关按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_Pump2 = 0
EndIf
If SelectedUnit = 2 Then
    U2_Manual_Pump2 = 0
EndIf
If SelectedUnit = 3 Then
    U3_Manual_Pump2 = 0
EndIf
If SelectedUnit = 4 Then
    U4_Manual_Pump2 = 0
EndIf
If SelectedUnit = 5 Then
    U5_Manual_Pump2 = 0
EndIf
If SelectedUnit = 6 Then
    U6_Manual_Pump2 = 0
EndIf
If SelectedUnit = 7 Then
    U7_Manual_Pump2 = 0
EndIf
If SelectedUnit = 8 Then
    U8_Manual_Pump2 = 0
EndIf

!Beep()
```

### 脚本 24:注射泵 抽液/排液

- **编号**: 24
- **用途**: 注射泵抽液/排液(需维护组权限)
- **位置**: 用户窗口 → 画面3_手动控制 → 抽液按钮 / 排液按钮 → Click 事件
- **触发方式**: 按钮单击
- **扩展方法**: 抽液用 `Manual_Aspirate`,排液用 `Manual_Dispense`

**抽液按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_Aspirate = 1
EndIf
If SelectedUnit = 2 Then
    U2_Manual_Aspirate = 1
EndIf
If SelectedUnit = 3 Then
    U3_Manual_Aspirate = 1
EndIf
If SelectedUnit = 4 Then
    U4_Manual_Aspirate = 1
EndIf
If SelectedUnit = 5 Then
    U5_Manual_Aspirate = 1
EndIf
If SelectedUnit = 6 Then
    U6_Manual_Aspirate = 1
EndIf
If SelectedUnit = 7 Then
    U7_Manual_Aspirate = 1
EndIf
If SelectedUnit = 8 Then
    U8_Manual_Aspirate = 1
EndIf

!Beep()
```

**排液按钮**:
```
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

If SelectedUnit = 1 Then
    U1_Manual_Dispense = 1
EndIf
If SelectedUnit = 2 Then
    U2_Manual_Dispense = 1
EndIf
If SelectedUnit = 3 Then
    U3_Manual_Dispense = 1
EndIf
If SelectedUnit = 4 Then
    U4_Manual_Dispense = 1
EndIf
If SelectedUnit = 5 Then
    U5_Manual_Dispense = 1
EndIf
If SelectedUnit = 6 Then
    U6_Manual_Dispense = 1
EndIf
If SelectedUnit = 7 Then
    U7_Manual_Dispense = 1
EndIf
If SelectedUnit = 8 Then
    U8_Manual_Dispense = 1
EndIf

!Beep()
```

### 脚本 25:复位按钮

- **编号**: 25
- **用途**: 手动复位(需管理员组权限)
- **位置**: 用户窗口 → 画面3_手动控制 → 复位按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 复位按钮脚本
' 功能: 校验管理员组权限 → 对选中单元置 Manual_Reset=1
' ============================================

' --- 1. 校验管理员组权限(L3) ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 置 Manual_Reset=1 ---
If SelectedUnit = 1 Then
    U1_Manual_Reset = 1
EndIf
If SelectedUnit = 2 Then
    U2_Manual_Reset = 1
EndIf
If SelectedUnit = 3 Then
    U3_Manual_Reset = 1
EndIf
If SelectedUnit = 4 Then
    U4_Manual_Reset = 1
EndIf
If SelectedUnit = 5 Then
    U5_Manual_Reset = 1
EndIf
If SelectedUnit = 6 Then
    U6_Manual_Reset = 1
EndIf
If SelectedUnit = 7 Then
    U7_Manual_Reset = 1
EndIf
If SelectedUnit = 8 Then
    U8_Manual_Reset = 1
EndIf

!Beep()
```

### 脚本 26:返回按钮

- **编号**: 26
- **用途**: 关闭手动控制子窗口,返回画面2_单元详情
- **位置**: 用户窗口 → 画面3_手动控制 → 返回按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面3)
' 功能: 关闭当前子窗口(画面3_手动控制),返回画面2_单元详情
' ============================================

!CloseAllSubWnd()
```

---

## 六、F. 画面4_参数设置脚本

### 脚本 27:画面4 窗口打开脚本

- **编号**: 27
- **用途**: 加载当前选中单元的参数到编辑缓冲区
- **位置**: 用户窗口 → 画面4_参数设置 → Load 事件
- **触发方式**: 子窗口装载时

```
' ============================================
' 画面4_参数设置 Load 脚本
' 功能: 把 SelectedUnit 对应单元的 VD 参数读到编辑缓冲变量
'       (供输入框编辑,保存时由脚本28写回 PLC)
' 注意: 浓度组参数(VD10/VD14)仅管理员可见可改,这里统一加载,
'       组态时通过权限位隐藏浓度输入框
' ============================================

If SelectedUnit = 1 Then
    Param_C_Set = U1_VD_C_Set
    Param_C_Stock = U1_VD_C_Stock
    Param_StepRes = U1_VD_StepRes
    Param_CycleSet = U1_VD_CycleSet
    Param_ExpTarget = U1_VD_ExpTarget
    Param_PreMixTime = U1_VD_PreMixTime
    Param_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
    Param_RestTime = U1_VD_RestTime
    Param_RestTime_Min = U1_VD_RestTime_Min
    Param_CycleExtend_Max = U1_VD_CycleExtend_Max
    Param_Timeout_ValveA = U1_VD_Timeout_ValveA
    Param_Timeout_ValveB = U1_VD_Timeout_ValveB
    Param_Timeout_ValveC = U1_VD_Timeout_ValveC
    Param_Timeout_Pump1 = U1_VD_Timeout_Pump1
    Param_Timeout_Pump2 = U1_VD_Timeout_Pump2
    Param_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 2 Then
    Param_C_Set = U2_VD_C_Set
    Param_C_Stock = U2_VD_C_Stock
    Param_StepRes = U2_VD_StepRes
    Param_CycleSet = U2_VD_CycleSet
    Param_ExpTarget = U2_VD_ExpTarget
    Param_PreMixTime = U2_VD_PreMixTime
    Param_PreMixTime_MinSafe = U2_VD_PreMixTime_MinSafe
    Param_RestTime = U2_VD_RestTime
    Param_RestTime_Min = U2_VD_RestTime_Min
    Param_CycleExtend_Max = U2_VD_CycleExtend_Max
    Param_Timeout_ValveA = U2_VD_Timeout_ValveA
    Param_Timeout_ValveB = U2_VD_Timeout_ValveB
    Param_Timeout_ValveC = U2_VD_Timeout_ValveC
    Param_Timeout_Pump1 = U2_VD_Timeout_Pump1
    Param_Timeout_Pump2 = U2_VD_Timeout_Pump2
    Param_Delay_ValveA_Verify = U2_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 3 Then
    Param_C_Set = U3_VD_C_Set
    Param_C_Stock = U3_VD_C_Stock
    Param_StepRes = U3_VD_StepRes
    Param_CycleSet = U3_VD_CycleSet
    Param_ExpTarget = U3_VD_ExpTarget
    Param_PreMixTime = U3_VD_PreMixTime
    Param_PreMixTime_MinSafe = U3_VD_PreMixTime_MinSafe
    Param_RestTime = U3_VD_RestTime
    Param_RestTime_Min = U3_VD_RestTime_Min
    Param_CycleExtend_Max = U3_VD_CycleExtend_Max
    Param_Timeout_ValveA = U3_VD_Timeout_ValveA
    Param_Timeout_ValveB = U3_VD_Timeout_ValveB
    Param_Timeout_ValveC = U3_VD_Timeout_ValveC
    Param_Timeout_Pump1 = U3_VD_Timeout_Pump1
    Param_Timeout_Pump2 = U3_VD_Timeout_Pump2
    Param_Delay_ValveA_Verify = U3_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 4 Then
    Param_C_Set = U4_VD_C_Set
    Param_C_Stock = U4_VD_C_Stock
    Param_StepRes = U4_VD_StepRes
    Param_CycleSet = U4_VD_CycleSet
    Param_ExpTarget = U4_VD_ExpTarget
    Param_PreMixTime = U4_VD_PreMixTime
    Param_PreMixTime_MinSafe = U4_VD_PreMixTime_MinSafe
    Param_RestTime = U4_VD_RestTime
    Param_RestTime_Min = U4_VD_RestTime_Min
    Param_CycleExtend_Max = U4_VD_CycleExtend_Max
    Param_Timeout_ValveA = U4_VD_Timeout_ValveA
    Param_Timeout_ValveB = U4_VD_Timeout_ValveB
    Param_Timeout_ValveC = U4_VD_Timeout_ValveC
    Param_Timeout_Pump1 = U4_VD_Timeout_Pump1
    Param_Timeout_Pump2 = U4_VD_Timeout_Pump2
    Param_Delay_ValveA_Verify = U4_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 5 Then
    Param_C_Set = U5_VD_C_Set
    Param_C_Stock = U5_VD_C_Stock
    Param_StepRes = U5_VD_StepRes
    Param_CycleSet = U5_VD_CycleSet
    Param_ExpTarget = U5_VD_ExpTarget
    Param_PreMixTime = U5_VD_PreMixTime
    Param_PreMixTime_MinSafe = U5_VD_PreMixTime_MinSafe
    Param_RestTime = U5_VD_RestTime
    Param_RestTime_Min = U5_VD_RestTime_Min
    Param_CycleExtend_Max = U5_VD_CycleExtend_Max
    Param_Timeout_ValveA = U5_VD_Timeout_ValveA
    Param_Timeout_ValveB = U5_VD_Timeout_ValveB
    Param_Timeout_ValveC = U5_VD_Timeout_ValveC
    Param_Timeout_Pump1 = U5_VD_Timeout_Pump1
    Param_Timeout_Pump2 = U5_VD_Timeout_Pump2
    Param_Delay_ValveA_Verify = U5_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 6 Then
    Param_C_Set = U6_VD_C_Set
    Param_C_Stock = U6_VD_C_Stock
    Param_StepRes = U6_VD_StepRes
    Param_CycleSet = U6_VD_CycleSet
    Param_ExpTarget = U6_VD_ExpTarget
    Param_PreMixTime = U6_VD_PreMixTime
    Param_PreMixTime_MinSafe = U6_VD_PreMixTime_MinSafe
    Param_RestTime = U6_VD_RestTime
    Param_RestTime_Min = U6_VD_RestTime_Min
    Param_CycleExtend_Max = U6_VD_CycleExtend_Max
    Param_Timeout_ValveA = U6_VD_Timeout_ValveA
    Param_Timeout_ValveB = U6_VD_Timeout_ValveB
    Param_Timeout_ValveC = U6_VD_Timeout_ValveC
    Param_Timeout_Pump1 = U6_VD_Timeout_Pump1
    Param_Timeout_Pump2 = U6_VD_Timeout_Pump2
    Param_Delay_ValveA_Verify = U6_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 7 Then
    Param_C_Set = U7_VD_C_Set
    Param_C_Stock = U7_VD_C_Stock
    Param_StepRes = U7_VD_StepRes
    Param_CycleSet = U7_VD_CycleSet
    Param_ExpTarget = U7_VD_ExpTarget
    Param_PreMixTime = U7_VD_PreMixTime
    Param_PreMixTime_MinSafe = U7_VD_PreMixTime_MinSafe
    Param_RestTime = U7_VD_RestTime
    Param_RestTime_Min = U7_VD_RestTime_Min
    Param_CycleExtend_Max = U7_VD_CycleExtend_Max
    Param_Timeout_ValveA = U7_VD_Timeout_ValveA
    Param_Timeout_ValveB = U7_VD_Timeout_ValveB
    Param_Timeout_ValveC = U7_VD_Timeout_ValveC
    Param_Timeout_Pump1 = U7_VD_Timeout_Pump1
    Param_Timeout_Pump2 = U7_VD_Timeout_Pump2
    Param_Delay_ValveA_Verify = U7_VD_Delay_ValveA_Verify
EndIf

If SelectedUnit = 8 Then
    Param_C_Set = U8_VD_C_Set
    Param_C_Stock = U8_VD_C_Stock
    Param_StepRes = U8_VD_StepRes
    Param_CycleSet = U8_VD_CycleSet
    Param_ExpTarget = U8_VD_ExpTarget
    Param_PreMixTime = U8_VD_PreMixTime
    Param_PreMixTime_MinSafe = U8_VD_PreMixTime_MinSafe
    Param_RestTime = U8_VD_RestTime
    Param_RestTime_Min = U8_VD_RestTime_Min
    Param_CycleExtend_Max = U8_VD_CycleExtend_Max
    Param_Timeout_ValveA = U8_VD_Timeout_ValveA
    Param_Timeout_ValveB = U8_VD_Timeout_ValveB
    Param_Timeout_ValveC = U8_VD_Timeout_ValveC
    Param_Timeout_Pump1 = U8_VD_Timeout_Pump1
    Param_Timeout_Pump2 = U8_VD_Timeout_Pump2
    Param_Delay_ValveA_Verify = U8_VD_Delay_ValveA_Verify
EndIf

ParamTargetUnit = SelectedUnit
```

### 脚本 28:保存参数按钮

- **编号**: 28
- **用途**: 校验参数范围 → 写入选中单元的 VD 参数(需维护组权限;浓度组需管理员)
- **位置**: 用户窗口 → 画面4_参数设置 → 保存参数按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 保存参数按钮脚本
' 功能: 1.校验维护组权限 2.浓度组额外校验管理员 3.范围校验 4.写回 PLC
' 依赖脚本31: 参数范围校验(本脚本调用前应先执行校验,这里再次兜底)
' ============================================

' --- 1. 校验维护组权限 ---
If !CheckUserGroup("维护组") = 1 Then
    If !CheckUserGroup("管理员组") = 1 Then
        !Beep()
        !LogOn()
        Exit
    EndIf
EndIf

' --- 2. 浓度组参数(C_Set / C_Stock)仅管理员可写 ---
If !CheckUserGroup("管理员组") = 0 Then
    ' 管理员: 允许保存全部
Else
    ' 非管理员(维护组): 不允许改浓度,只保留原值
    If SelectedUnit = 1 Then
        Param_C_Set = U1_VD_C_Set
        Param_C_Stock = U1_VD_C_Stock
    EndIf
    If SelectedUnit = 2 Then
        Param_C_Set = U2_VD_C_Set
        Param_C_Stock = U2_VD_C_Stock
    EndIf
    If SelectedUnit = 3 Then
        Param_C_Set = U3_VD_C_Set
        Param_C_Stock = U3_VD_C_Stock
    EndIf
    If SelectedUnit = 4 Then
        Param_C_Set = U4_VD_C_Set
        Param_C_Stock = U4_VD_C_Stock
    EndIf
    If SelectedUnit = 5 Then
        Param_C_Set = U5_VD_C_Set
        Param_C_Stock = U5_VD_C_Stock
    EndIf
    If SelectedUnit = 6 Then
        Param_C_Set = U6_VD_C_Set
        Param_C_Stock = U6_VD_C_Stock
    EndIf
    If SelectedUnit = 7 Then
        Param_C_Set = U7_VD_C_Set
        Param_C_Stock = U7_VD_C_Stock
    EndIf
    If SelectedUnit = 8 Then
        Param_C_Set = U8_VD_C_Set
        Param_C_Stock = U8_VD_C_Stock
    EndIf
EndIf

' --- 3. 范围校验(完整规则见脚本31,此处仅关键项) ---
' 浓度: 0 < C_Set <= C_Stock <= 200
If Param_C_Set <= 0 Then
    !Beep()
    Exit
EndIf
If Param_C_Stock < Param_C_Set Then
    !Beep()
    Exit
EndIf
' 预循环最小安全值约束
If Param_PreMixTime < Param_PreMixTime_MinSafe Then
    !Beep()
    Exit
EndIf
' 静止时间约束
If Param_RestTime < Param_RestTime_Min Then
    !Beep()
    Exit
EndIf
' 超时必须>0
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

' --- 4. 写回 PLC (按 SelectedUnit 选择目标) ---
If SelectedUnit = 1 Then
    U1_VD_C_Set = Param_C_Set
    U1_VD_C_Stock = Param_C_Stock
    U1_VD_StepRes = Param_StepRes
    U1_VD_CycleSet = Param_CycleSet
    U1_VD_ExpTarget = Param_ExpTarget
    U1_VD_PreMixTime = Param_PreMixTime
    U1_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
    U1_VD_RestTime = Param_RestTime
    U1_VD_RestTime_Min = Param_RestTime_Min
    U1_VD_CycleExtend_Max = Param_CycleExtend_Max
    U1_VD_Timeout_ValveA = Param_Timeout_ValveA
    U1_VD_Timeout_ValveB = Param_Timeout_ValveB
    U1_VD_Timeout_ValveC = Param_Timeout_ValveC
    U1_VD_Timeout_Pump1 = Param_Timeout_Pump1
    U1_VD_Timeout_Pump2 = Param_Timeout_Pump2
    U1_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 2 Then
    U2_VD_C_Set = Param_C_Set
    U2_VD_C_Stock = Param_C_Stock
    U2_VD_StepRes = Param_StepRes
    U2_VD_CycleSet = Param_CycleSet
    U2_VD_ExpTarget = Param_ExpTarget
    U2_VD_PreMixTime = Param_PreMixTime
    U2_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
    U2_VD_RestTime = Param_RestTime
    U2_VD_RestTime_Min = Param_RestTime_Min
    U2_VD_CycleExtend_Max = Param_CycleExtend_Max
    U2_VD_Timeout_ValveA = Param_Timeout_ValveA
    U2_VD_Timeout_ValveB = Param_Timeout_ValveB
    U2_VD_Timeout_ValveC = Param_Timeout_ValveC
    U2_VD_Timeout_Pump1 = Param_Timeout_Pump1
    U2_VD_Timeout_Pump2 = Param_Timeout_Pump2
    U2_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 3 Then
    U3_VD_C_Set = Param_C_Set
    U3_VD_C_Stock = Param_C_Stock
    U3_VD_StepRes = Param_StepRes
    U3_VD_CycleSet = Param_CycleSet
    U3_VD_ExpTarget = Param_ExpTarget
    U3_VD_PreMixTime = Param_PreMixTime
    U3_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
    U3_VD_RestTime = Param_RestTime
    U3_VD_RestTime_Min = Param_RestTime_Min
    U3_VD_CycleExtend_Max = Param_CycleExtend_Max
    U3_VD_Timeout_ValveA = Param_Timeout_ValveA
    U3_VD_Timeout_ValveB = Param_Timeout_ValveB
    U3_VD_Timeout_ValveC = Param_Timeout_ValveC
    U3_VD_Timeout_Pump1 = Param_Timeout_Pump1
    U3_VD_Timeout_Pump2 = Param_Timeout_Pump2
    U3_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 4 Then
    U4_VD_C_Set = Param_C_Set
    U4_VD_C_Stock = Param_C_Stock
    U4_VD_StepRes = Param_StepRes
    U4_VD_CycleSet = Param_CycleSet
    U4_VD_ExpTarget = Param_ExpTarget
    U4_VD_PreMixTime = Param_PreMixTime
    U4_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
    U4_VD_RestTime = Param_RestTime
    U4_VD_RestTime_Min = Param_RestTime_Min
    U4_VD_CycleExtend_Max = Param_CycleExtend_Max
    U4_VD_Timeout_ValveA = Param_Timeout_ValveA
    U4_VD_Timeout_ValveB = Param_Timeout_ValveB
    U4_VD_Timeout_ValveC = Param_Timeout_ValveC
    U4_VD_Timeout_Pump1 = Param_Timeout_Pump1
    U4_VD_Timeout_Pump2 = Param_Timeout_Pump2
    U4_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 5 Then
    U5_VD_C_Set = Param_C_Set
    U5_VD_C_Stock = Param_C_Stock
    U5_VD_StepRes = Param_StepRes
    U5_VD_CycleSet = Param_CycleSet
    U5_VD_ExpTarget = Param_ExpTarget
    U5_VD_PreMixTime = Param_PreMixTime
    U5_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
    U5_VD_RestTime = Param_RestTime
    U5_VD_RestTime_Min = Param_RestTime_Min
    U5_VD_CycleExtend_Max = Param_CycleExtend_Max
    U5_VD_Timeout_ValveA = Param_Timeout_ValveA
    U5_VD_Timeout_ValveB = Param_Timeout_ValveB
    U5_VD_Timeout_ValveC = Param_Timeout_ValveC
    U5_VD_Timeout_Pump1 = Param_Timeout_Pump1
    U5_VD_Timeout_Pump2 = Param_Timeout_Pump2
    U5_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 6 Then
    U6_VD_C_Set = Param_C_Set
    U6_VD_C_Stock = Param_C_Stock
    U6_VD_StepRes = Param_StepRes
    U6_VD_CycleSet = Param_CycleSet
    U6_VD_ExpTarget = Param_ExpTarget
    U6_VD_PreMixTime = Param_PreMixTime
    U6_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
    U6_VD_RestTime = Param_RestTime
    U6_VD_RestTime_Min = Param_RestTime_Min
    U6_VD_CycleExtend_Max = Param_CycleExtend_Max
    U6_VD_Timeout_ValveA = Param_Timeout_ValveA
    U6_VD_Timeout_ValveB = Param_Timeout_ValveB
    U6_VD_Timeout_ValveC = Param_Timeout_ValveC
    U6_VD_Timeout_Pump1 = Param_Timeout_Pump1
    U6_VD_Timeout_Pump2 = Param_Timeout_Pump2
    U6_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 7 Then
    U7_VD_C_Set = Param_C_Set
    U7_VD_C_Stock = Param_C_Stock
    U7_VD_StepRes = Param_StepRes
    U7_VD_CycleSet = Param_CycleSet
    U7_VD_ExpTarget = Param_ExpTarget
    U7_VD_PreMixTime = Param_PreMixTime
    U7_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
    U7_VD_RestTime = Param_RestTime
    U7_VD_RestTime_Min = Param_RestTime_Min
    U7_VD_CycleExtend_Max = Param_CycleExtend_Max
    U7_VD_Timeout_ValveA = Param_Timeout_ValveA
    U7_VD_Timeout_ValveB = Param_Timeout_ValveB
    U7_VD_Timeout_ValveC = Param_Timeout_ValveC
    U7_VD_Timeout_Pump1 = Param_Timeout_Pump1
    U7_VD_Timeout_Pump2 = Param_Timeout_Pump2
    U7_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

If SelectedUnit = 8 Then
    U8_VD_C_Set = Param_C_Set
    U8_VD_C_Stock = Param_C_Stock
    U8_VD_StepRes = Param_StepRes
    U8_VD_CycleSet = Param_CycleSet
    U8_VD_ExpTarget = Param_ExpTarget
    U8_VD_PreMixTime = Param_PreMixTime
    U8_VD_PreMixTime_MinSafe = Param_PreMixTime_MinSafe
    U8_VD_RestTime = Param_RestTime
    U8_VD_RestTime_Min = Param_RestTime_Min
    U8_VD_CycleExtend_Max = Param_CycleExtend_Max
    U8_VD_Timeout_ValveA = Param_Timeout_ValveA
    U8_VD_Timeout_ValveB = Param_Timeout_ValveB
    U8_VD_Timeout_ValveC = Param_Timeout_ValveC
    U8_VD_Timeout_Pump1 = Param_Timeout_Pump1
    U8_VD_Timeout_Pump2 = Param_Timeout_Pump2
    U8_VD_Delay_ValveA_Verify = Param_Delay_ValveA_Verify
EndIf

!Beep()
```

### 脚本 29:复制到其他单元按钮

- **编号**: 29
- **用途**: 弹出单元选择子窗口,选择目标单元后复制参数(需管理员组权限)
- **位置**: 用户窗口 → 画面4_参数设置 → 复制到其他单元按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 复制到其他单元按钮脚本
' 功能: 权限校验 → 弹出单元选择子窗口(脚本56负责选目标单元,
'       脚本57负责确认后执行复制)
' ============================================

' --- 1. 校验管理员组权限(跨单元复制属敏感操作) ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 记录源单元(供复制确认子窗口使用) ---
ParamSrcUnit = SelectedUnit

' --- 3. 打开单元选择子窗口(脚本56) ---
!OpenSubWnd(子窗口_单元选择, 240, 180, 400, 240, 17)
```

### 脚本 30:恢复默认按钮

- **编号**: 30
- **用途**: 二次确认后重置参数为默认值(需管理员组权限)
- **位置**: 用户窗口 → 画面4_参数设置 → 恢复默认按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 恢复默认按钮脚本
' 功能: 权限校验 → 弹出恢复默认确认子窗口(脚本53负责执行)
' 默认值清单(参考 McgsPro变量导入_8单元_v2.0.csv 备注):
'   C_Set=5.0  C_Stock=100.0  StepRes=0.5  CycleSet=3.0
'   ExpTarget=5.0  PreMixTime=12.0  PreMixTime_MinSafe=3.0
'   RestTime=6.0  RestTime_Min=1.5  CycleExtend_Max=0.5
'   Timeout_ValveA/B/C=2.0  Timeout_Pump1/2=2.0
'   Delay_ValveA_Verify=0.5
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 打开恢复默认确认子窗口(脚本53) ---
!OpenSubWnd(子窗口_恢复默认确认, 240, 180, 400, 180, 17)
```

### 脚本 31:参数范围校验脚本

- **编号**: 31
- **用途**: 完整校验浓度/时间/超时上下限,失败时蜂鸣+退出
- **位置**: 用户窗口 → 画面4_参数设置 → 输入框构件 → ContentChanged 事件(或保存前调用)
- **触发方式**: 参数变化时(可作为保存按钮前置校验段)

```
' ============================================
' 参数范围校验脚本
' 功能: 校验 Param_* 编辑缓冲变量范围,失败置 ParamValid=0
' 校验规则(参考 HMI画面架构规划文档 + PLC设计文档):
'   浓度: 0 < C_Set <= C_Stock <= 200
'   步进: 0 < StepRes <= 5
'   周期: 0.5 <= CycleSet <= 60
'   实验目标: 1 <= ExpTarget <= 120
'   预循环: PreMixTime_MinSafe(3.0) <= PreMixTime <= 60
'   静止: RestTime_Min(1.5) <= RestTime <= 30
'   顺延上限: 0 < CycleExtend_Max <= 2
'   超时: 0.5 <= Timeout_* <= 30
'   阀A关闭延时验证: 0 < Delay_ValveA_Verify <= 5
' ============================================

ParamValid = 1
ParamInvalidStr = ""

' --- 1. 浓度组校验 ---
If Param_C_Set <= 0 Then
    ParamValid = 0
    ParamInvalidStr = "目标浓度必须>0"
EndIf
If Param_C_Set > Param_C_Stock Then
    ParamValid = 0
    ParamInvalidStr = "目标浓度不能大于母液浓度"
EndIf
If Param_C_Stock > 200 Then
    ParamValid = 0
    ParamInvalidStr = "母液浓度上限200"
EndIf

' --- 2. 步进/周期/目标 ---
If Param_StepRes <= 0 Then
    ParamValid = 0
    ParamInvalidStr = "步进分辨率必须>0"
EndIf
If Param_StepRes > 5 Then
    ParamValid = 0
    ParamInvalidStr = "步进分辨率上限5"
EndIf
If Param_CycleSet < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "换水周期下限0.5min"
EndIf
If Param_CycleSet > 60 Then
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

' --- 3. 预循环/静止 ---
If Param_PreMixTime < Param_PreMixTime_MinSafe Then
    ParamValid = 0
    ParamInvalidStr = "预循环时间低于最小安全值"
EndIf
If Param_PreMixTime > 60 Then
    ParamValid = 0
    ParamInvalidStr = "预循环时间上限60min"
EndIf
If Param_RestTime < Param_RestTime_Min Then
    ParamValid = 0
    ParamInvalidStr = "静止时间低于最小值"
EndIf
If Param_RestTime > 30 Then
    ParamValid = 0
    ParamInvalidStr = "静止时间上限30min"
EndIf

' --- 4. 顺延上限 ---
If Param_CycleExtend_Max <= 0 Then
    ParamValid = 0
    ParamInvalidStr = "顺延上限必须>0"
EndIf
If Param_CycleExtend_Max > 2 Then
    ParamValid = 0
    ParamInvalidStr = "顺延上限最大2min"
EndIf

' --- 5. 超时组校验 ---
If Param_Timeout_ValveA < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "阀A超时下限0.5s"
EndIf
If Param_Timeout_ValveA > 30 Then
    ParamValid = 0
    ParamInvalidStr = "阀A超时上限30s"
EndIf
If Param_Timeout_ValveB < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "阀B超时下限0.5s"
EndIf
If Param_Timeout_ValveB > 30 Then
    ParamValid = 0
    ParamInvalidStr = "阀B超时上限30s"
EndIf
If Param_Timeout_ValveC < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "阀C超时下限0.5s"
EndIf
If Param_Timeout_ValveC > 30 Then
    ParamValid = 0
    ParamInvalidStr = "阀C超时上限30s"
EndIf
If Param_Timeout_Pump1 < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "泵1超时下限0.5s"
EndIf
If Param_Timeout_Pump1 > 30 Then
    ParamValid = 0
    ParamInvalidStr = "泵1超时上限30s"
EndIf
If Param_Timeout_Pump2 < 0.5 Then
    ParamValid = 0
    ParamInvalidStr = "泵2超时下限0.5s"
EndIf
If Param_Timeout_Pump2 > 30 Then
    ParamValid = 0
    ParamInvalidStr = "泵2超时上限30s"
EndIf

' --- 6. 阀A关闭延时验证 ---
If Param_Delay_ValveA_Verify <= 0 Then
    ParamValid = 0
    ParamInvalidStr = "阀A关闭延时验证必须>0"
EndIf
If Param_Delay_ValveA_Verify > 5 Then
    ParamValid = 0
    ParamInvalidStr = "阀A关闭延时验证上限5s"
EndIf

' --- 7. 校验失败蜂鸣 ---
If ParamValid = 0 Then
    !Beep()
EndIf
```

### 脚本 32:返回按钮

- **编号**: 32
- **用途**: 关闭参数设置子窗口,返回画面2_单元详情
- **位置**: 用户窗口 → 画面4_参数设置 → 返回按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面4)
' 功能: 关闭当前子窗口(画面4_参数设置),返回画面2_单元详情
' ============================================

!CloseAllSubWnd()
```

---

## 七、G. 画面5_报警日志脚本

### 脚本 33:画面5 窗口打开脚本

- **编号**: 33
- **用途**: 加载当前激活报警 + 历史日志,初始化筛选条件
- **位置**: 用户窗口 → 画面5_报警日志 → Load 事件
- **触发方式**: 窗口装载时

```
' ============================================
' 画面5_报警日志 Load 脚本
' 功能: 初始化筛选单元号=0(全部) + 刷新报警浏览构件时间范围
' ============================================

' --- 1. 关闭残留子窗口 ---
!CloseAllSubWnd()

' --- 2. 初始化筛选单元号(0=全部8个单元) ---
AlmFilterUnit = 0

' --- 3. 拼接筛选描述 ---
AlmFilterStr = "全部单元"

' --- 4. 更新系统时间显示 ---
SysTimeString = $Date + " " + $Time
```

### 脚本 34:按单元筛选按钮

- **编号**: 34
- **用途**: 弹出单元选择子窗口,选择目标单元号筛选报警
- **位置**: 用户窗口 → 画面5_报警日志 → 按单元筛选按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 按单元筛选按钮脚本
' 功能: 打开单元选择子窗口(脚本56),用户选择后更新 AlmFilterUnit
' ============================================

' --- 1. 标记筛选模式(供子窗口区分用途) ---
SubWndMode = 1

' --- 2. 打开单元选择子窗口 ---
!OpenSubWnd(子窗口_单元选择, 240, 180, 400, 240, 17)
```

### 脚本 35:清除历史日志按钮

- **编号**: 35
- **用途**: 二次确认后清除报警历史记录(需管理员组权限)
- **位置**: 用户窗口 → 画面5_报警日志 → 清除历史日志按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 清除历史日志按钮脚本
' 功能: 权限校验 → 弹出清除日志确认子窗口(脚本54负责执行)
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 打开清除日志确认子窗口 ---
!OpenSubWnd(子窗口_清除日志确认, 240, 180, 400, 180, 17)
```

### 脚本 36:返回按钮

- **编号**: 36
- **用途**: 关闭画面5,返回画面1_总览
- **位置**: 用户窗口 → 画面5_报警日志 → 返回按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面5)
' 功能: 关闭所有子窗口,返回画面1_总览
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("画面1_总览")
```

---

## 八、H. 画面6_趋势曲线脚本

### 脚本 37:画面6 窗口打开脚本

- **编号**: 37
- **用途**: 初始化历史曲线构件时间范围(默认1小时)+曲线变量绑定
- **位置**: 用户窗口 → 画面6_趋势曲线 → Load 事件
- **触发方式**: 窗口装载时

```
' ============================================
' 画面6_趋势曲线 Load 脚本
' 功能: 设置默认时间范围=1小时 + 默认显示1号单元流量+压力
' ============================================

' --- 1. 关闭残留子窗口 ---
!CloseAllSubWnd()

' --- 2. 初始化时间范围(1=1h / 8=8h / 24=24h) ---
TrendTimeRange = 1

' --- 3. 默认显示单元 ---
TrendDisplayUnit = 1

' --- 4. 拼接时间范围描述 ---
If TrendTimeRange = 1 Then
    TrendRangeStr = "最近1小时"
EndIf
If TrendTimeRange = 8 Then
    TrendRangeStr = "最近8小时"
EndIf
If TrendTimeRange = 24 Then
    TrendRangeStr = "最近24小时"
EndIf
```

### 脚本 38:时间范围切换按钮

- **编号**: 38
- **用途**: 1小时/8小时/24小时三档切换(单按钮循环切换)
- **位置**: 用户窗口 → 画面6_趋势曲线 → 时间范围切换按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 时间范围切换按钮脚本
' 功能: 1h → 8h → 24h → 1h 循环切换
' 注意: 历史曲线构件的时间范围通过其组态属性绑定 TrendTimeRange,
'       此处仅切换变量值,构件会自动刷新
' ============================================

If TrendTimeRange = 1 Then
    TrendTimeRange = 8
    TrendRangeStr = "最近8小时"
Else
    If TrendTimeRange = 8 Then
        TrendTimeRange = 24
        TrendRangeStr = "最近24小时"
    Else
        TrendTimeRange = 1
        TrendRangeStr = "最近1小时"
    EndIf
EndIf

!Beep()
```

### 脚本 39:返回按钮

- **编号**: 39
- **用途**: 关闭画面6,返回画面1_总览
- **位置**: 用户窗口 → 画面6_趋势曲线 → 返回按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面6)
' 功能: 关闭所有子窗口,返回画面1_总览
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("画面1_总览")
```

---

## 九、I. 画面7_通讯维护脚本

### 脚本 40:画面7 窗口打开脚本

- **编号**: 40
- **用途**: 加载8台PLC + 16个485从站状态
- **位置**: 用户窗口 → 画面7_通讯维护 → Load 事件
- **触发方式**: 窗口装载时

```
' ============================================
' 画面7_通讯维护 Load 脚本
' 功能: 刷新8台PLC设备状态 + 16个Modbus从站状态
' ============================================

' --- 1. 关闭残留子窗口 ---
!CloseAllSubWnd()

' --- 2. 检测8台PLC设备状态 (!SetDevice(name,3,"") 返回 1=启动 / 0=停止) ---
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

' --- 3. 检测16个Modbus从站状态(注射泵+流量计 × 8套) ---
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
- **用途**: 二次确认后停止并重新启动指定通讯设备(需管理员组权限)
- **位置**: 用户窗口 → 画面7_通讯维护 → 重启通讯按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 重启通讯按钮脚本
' 功能: 权限校验 → 停止所有PLC+Modbus设备 → 启动所有设备
' 注意: 全量重启会影响8套单元通讯,需管理员权限
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 蜂鸣提示开始重启 ---
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
- **用途**: 打开操作日志浏览子窗口
- **位置**: 用户窗口 → 画面7_通讯维护 → 查看详细日志按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 查看详细日志按钮脚本
' 功能: 打开日志浏览子窗口(组态中使用存盘数据浏览构件显示操作日志)
' ============================================

!OpenSubWnd(子窗口_日志浏览, 80, 60, 800, 600, 17)
```

### 脚本 43:返回按钮

- **编号**: 43
- **用途**: 关闭画面7,返回画面1_总览
- **位置**: 用户窗口 → 画面7_通讯维护 → 返回按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面7)
' 功能: 关闭所有子窗口,返回画面1_总览
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("画面1_总览")
```

---

## 十、J. 画面8_系统设置脚本

### 脚本 44:画面8 窗口打开脚本

- **编号**: 44
- **用途**: 加载8个单元使能状态 + 用户配置
- **位置**: 用户窗口 → 画面8_系统设置 → Load 事件
- **触发方式**: 窗口装载时

```
' ============================================
' 画面8_系统设置 Load 脚本
' 功能: 关闭残留子窗口 + 显示当前登录用户 + 加载单元使能状态(从断电保持变量)
' ============================================

' --- 1. 关闭残留子窗口 ---
!CloseAllSubWnd()

' --- 2. 显示当前登录用户 ---
CurrentUserStr = $UserName
If CurrentUserStr = "" Then
    CurrentUserStr = "未登录"
EndIf

' --- 3. 显示当前用户组 ---
CurrentUserGroupStr = !GetCurrentGroup()
If CurrentUserGroupStr = "" Then
    CurrentUserGroupStr = "无"
EndIf

' --- 4. 拼接单元使能状态汇总(供画面显示) ---
' U1_Enable~U8_Enable 为断电保持内部变量,这里只读汇总
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

### 脚本 45:单元使能开关切换

- **编号**: 45
- **用途**: 切换单元使能状态(0↔1) + !SaveData 存盘(需管理员组权限)
- **位置**: 用户窗口 → 画面8_系统设置 → 单元使能开关构件(8个) → Click 事件
- **触发方式**: 开关单击
- **扩展方法**: 8个开关独立脚本,以1号为例

**1号单元使能开关切换**:
```
' ============================================
' 1号单元使能开关切换脚本
' 功能: 权限校验 → 翻转 U1_Enable → 存盘
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

' --- 3. 立即存盘(单元使能配置组对象,需组态为组对象并勾选存盘) ---
!SaveData(UnitEnableGroup)
!FreshDataSave()

!Beep()
```

**2~8号单元使能开关切换**(扩展方法:把脚本中 `U1_Enable` 替换为对应单元号):
```
' 2号
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

' 3号
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

' 4号
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

' 5号
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

' 6号
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

' 7号
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

' 8号
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
- **用途**: 弹出 McgsPro 内置用户管理窗口
- **位置**: 用户窗口 → 画面8_系统设置 → 用户管理按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 用户管理按钮脚本
' 功能: 弹出内置用户管理窗口(仅负责人或拥有子组的用户可见子组配置)
' ============================================

!Editusers()
```

### 脚本 47:修改密码按钮

- **编号**: 47
- **用途**: 弹出 McgsPro 内置修改密码窗口
- **位置**: 用户窗口 → 画面8_系统设置 → 修改密码按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 修改密码按钮脚本
' 功能: 弹出内置修改密码窗口,供当前登录用户修改密码
' ============================================

!ChangePassword()
```

### 脚本 48:退出系统按钮

- **编号**: 48
- **用途**: 二次确认后退出 McgsPro 运行环境(需管理员组权限)
- **位置**: 用户窗口 → 画面8_系统设置 → 退出系统按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 退出系统按钮脚本
' 功能: 权限校验 → 弹出退出确认子窗口(脚本55负责执行)
' ============================================

' --- 1. 校验管理员组权限 ---
If !CheckUserGroup("管理员组") = 1 Then
    !Beep()
    !LogOn()
    Exit
EndIf

' --- 2. 打开退出系统确认子窗口 ---
!OpenSubWnd(子窗口_退出系统确认, 240, 180, 400, 180, 17)
```

### 脚本 49:返回按钮

- **编号**: 49
- **用途**: 关闭画面8,打开画面1_总览
- **位置**: 用户窗口 → 画面8_系统设置 → 返回按钮构件 → Click 事件
- **触发方式**: 按钮单击

```
' ============================================
' 返回按钮脚本(画面8)
' 功能: 关闭所有窗口(保留画面1_总览并打开) → 关闭子窗口
' 注意: !CloseAllWindow("画面1_总览") 会关闭其他所有窗口,
'       若画面1_总览未打开则同时打开它
' ============================================

!CloseAllSubWnd()
!CloseAllWindow("画面1_总览")
```

---

## 十一、K. 二次确认子窗口脚本

> **子窗口组态约定**:每个二次确认子窗口包含"确认"和"取消"两个按钮,确认按钮执行实际操作并调用 `!CloseAllSubWnd()` 关闭子窗口,取消按钮仅调用 `!CloseAllSubWnd()`。子窗口模式参数 `17 = 1(模态) + 16(边框)`。

### 脚本 50:启动确认子窗口

- **编号**: 50
- **用途**: 启动二次确认。确认→置 CMD_Start=1 + 关闭;取消→关闭
- **位置**: 用户窗口 → 子窗口_启动确认 → 确认按钮 / 取消按钮 → Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 启动确认子窗口 - 确认按钮
' 功能: 对当前选中单元置 CMD_Start=1,然后关闭子窗口
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
' 启动确认子窗口 - 取消按钮
' ============================================

!CloseAllSubWnd()
```

### 脚本 51:停止确认子窗口

- **编号**: 51
- **用途**: 停止二次确认。确认→置 CMD_Stop=1 + 关闭;取消→关闭
- **位置**: 用户窗口 → 子窗口_停止确认 → 确认按钮 / 取消按钮 → Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 停止确认子窗口 - 确认按钮
' 功能: 对当前选中单元置 CMD_Stop=1,然后关闭子窗口
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

### 脚本 52:急停确认子窗口

- **编号**: 52
- **用途**: 急停二次确认。确认→对8个使能+在线单元置 CMD_Stop=1 + 关闭;取消→关闭
- **位置**: 用户窗口 → 子窗口_急停确认 → 确认按钮 / 取消按钮 → Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 急停确认子窗口 - 确认按钮
' 功能: 对所有使能+在线单元下发急停(CMD_Stop=1)
' 注意: 急停是全局操作,不限于 SelectedUnit
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

### 脚本 53:恢复默认确认子窗口

- **编号**: 53
- **用途**: 恢复默认参数二次确认。确认→重置 Param_* 为默认值 + 关闭;取消→关闭
- **位置**: 用户窗口 → 子窗口_恢复默认确认 → 确认按钮 / 取消按钮 → Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 恢复默认确认子窗口 - 确认按钮
' 功能: 把 Param_* 编辑缓冲变量重置为默认值
'       (实际写回 PLC 由用户再次点击"保存参数"按钮完成,脚本28)
' 默认值参考 McgsPro变量导入_8单元_v2.0.csv 备注
' ============================================

Param_C_Set = 5.0
Param_C_Stock = 100.0
Param_StepRes = 0.5
Param_CycleSet = 3.0
Param_ExpTarget = 5.0
Param_PreMixTime = 12.0
Param_PreMixTime_MinSafe = 3.0
Param_RestTime = 6.0
Param_RestTime_Min = 1.5
Param_CycleExtend_Max = 0.5
Param_Timeout_ValveA = 2.0
Param_Timeout_ValveB = 2.0
Param_Timeout_ValveC = 2.0
Param_Timeout_Pump1 = 2.0
Param_Timeout_Pump2 = 2.0
Param_Delay_ValveA_Verify = 0.5

!Beep()
!CloseAllSubWnd()
```

**取消按钮**:
```
!CloseAllSubWnd()
```

### 脚本 54:清除日志确认子窗口

- **编号**: 54
- **用途**: 清除报警历史日志二次确认。确认→!ClearHistoryAlarmData + !OperationLogClear + 关闭;取消→关闭
- **位置**: 用户窗口 → 子窗口_清除日志确认 → 确认按钮 / 取消按钮 → Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 清除日志确认子窗口 - 确认按钮
' 功能: 清除历史报警数据 + 清除操作日志
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
- **用途**: 退出系统二次确认。确认→关闭所有窗口+退出运行环境;取消→关闭
- **位置**: 用户窗口 → 子窗口_退出系统确认 → 确认按钮 / 取消按钮 → Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 退出系统确认子窗口 - 确认按钮
' 功能: 关闭所有窗口(包括子窗口) → 触发退出策略
' 注意: McgsPro 通过 !CloseAllWindow("") 关闭所有窗口后,
'       组态中"主控窗口→退出"设置为"退出运行环境"即可实现退出。
'       若需权限检查,ExitLogonEnabled 已在启动策略中设置为1。
' ============================================

!Beep()

' 关闭所有子窗口
!CloseAllSubWnd()

' 关闭所有标准窗口(空串=关闭全部,触发退出流程)
!CloseAllWindow("")
```

**取消按钮**:
```
!CloseAllSubWnd()
```

### 脚本 56:单元选择子窗口

- **编号**: 56
- **用途**: 选择目标单元号。8个数字按钮(1~8)+ 1个"全部"按钮,点击后写入目标单元变量并关闭
- **位置**: 用户窗口 → 子窗口_单元选择 → 1~8号单元按钮 / 全部按钮 → Click 事件
- **触发方式**: 按钮单击
- **使用场景**: 脚本29(复制参数选择目标单元) / 脚本34(报警按单元筛选)

**1号单元按钮**(以1号为例,2~8号同理):
```
' ============================================
' 单元选择子窗口 - 1号按钮
' 功能: 根据 SubWndMode 写入不同目标变量
'   SubWndMode=0: 复制参数目标 → ParamDstUnit
'   SubWndMode=1: 报警筛选单元 → AlmFilterUnit
' ============================================

If SubWndMode = 0 Then
    ParamDstUnit = 1
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 1
    AlmFilterStr = "1号单元"
EndIf

!CloseAllSubWnd()
```

**2号单元按钮**:
```
If SubWndMode = 0 Then
    ParamDstUnit = 2
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 2
    AlmFilterStr = "2号单元"
EndIf
!CloseAllSubWnd()
```

**3号单元按钮**:
```
If SubWndMode = 0 Then
    ParamDstUnit = 3
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 3
    AlmFilterStr = "3号单元"
EndIf
!CloseAllSubWnd()
```

**4号单元按钮**:
```
If SubWndMode = 0 Then
    ParamDstUnit = 4
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 4
    AlmFilterStr = "4号单元"
EndIf
!CloseAllSubWnd()
```

**5号单元按钮**:
```
If SubWndMode = 0 Then
    ParamDstUnit = 5
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 5
    AlmFilterStr = "5号单元"
EndIf
!CloseAllSubWnd()
```

**6号单元按钮**:
```
If SubWndMode = 0 Then
    ParamDstUnit = 6
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 6
    AlmFilterStr = "6号单元"
EndIf
!CloseAllSubWnd()
```

**7号单元按钮**:
```
If SubWndMode = 0 Then
    ParamDstUnit = 7
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 7
    AlmFilterStr = "7号单元"
EndIf
!CloseAllSubWnd()
```

**8号单元按钮**:
```
If SubWndMode = 0 Then
    ParamDstUnit = 8
EndIf
If SubWndMode = 1 Then
    AlmFilterUnit = 8
    AlmFilterStr = "8号单元"
EndIf
!CloseAllSubWnd()
```

**全部按钮**(仅报警筛选场景使用):
```
If SubWndMode = 1 Then
    AlmFilterUnit = 0
    AlmFilterStr = "全部单元"
EndIf
!CloseAllSubWnd()
```

### 脚本 57:复制参数确认子窗口

- **编号**: 57
- **用途**: 跨单元复制参数二次确认。确认→把 ParamSrcUnit 的 VD 参数复制到 ParamDstUnit + 关闭;取消→关闭
- **位置**: 用户窗口 → 子窗口_复制参数确认 → 确认按钮 / 取消按钮 → Click 事件
- **触发方式**: 按钮单击

**确认按钮**:
```
' ============================================
' 复制参数确认子窗口 - 确认按钮
' 功能: 把 ParamSrcUnit 单元的全部 VD 参数复制到 ParamDstUnit 单元
' 前置条件: 脚本29已设置 ParamSrcUnit,脚本56已设置 ParamDstUnit
' 注意: McgsPro 不支持动态变量名,用嵌套 If 选择源/目标单元
' ============================================

' --- 1. 校验源/目标单元有效 ---
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

' --- 2. 源1号 → 目标2~8号 ---
If ParamSrcUnit = 1 Then
    If ParamDstUnit = 2 Then
        U2_VD_C_Set = U1_VD_C_Set
        U2_VD_C_Stock = U1_VD_C_Stock
        U2_VD_StepRes = U1_VD_StepRes
        U2_VD_CycleSet = U1_VD_CycleSet
        U2_VD_ExpTarget = U1_VD_ExpTarget
        U2_VD_PreMixTime = U1_VD_PreMixTime
        U2_VD_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
        U2_VD_RestTime = U1_VD_RestTime
        U2_VD_RestTime_Min = U1_VD_RestTime_Min
        U2_VD_CycleExtend_Max = U1_VD_CycleExtend_Max
        U2_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U2_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U2_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U2_VD_Timeout_Pump1 = U1_VD_Timeout_Pump1
        U2_VD_Timeout_Pump2 = U1_VD_Timeout_Pump2
        U2_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 3 Then
        U3_VD_C_Set = U1_VD_C_Set
        U3_VD_C_Stock = U1_VD_C_Stock
        U3_VD_StepRes = U1_VD_StepRes
        U3_VD_CycleSet = U1_VD_CycleSet
        U3_VD_ExpTarget = U1_VD_ExpTarget
        U3_VD_PreMixTime = U1_VD_PreMixTime
        U3_VD_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
        U3_VD_RestTime = U1_VD_RestTime
        U3_VD_RestTime_Min = U1_VD_RestTime_Min
        U3_VD_CycleExtend_Max = U1_VD_CycleExtend_Max
        U3_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U3_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U3_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U3_VD_Timeout_Pump1 = U1_VD_Timeout_Pump1
        U3_VD_Timeout_Pump2 = U1_VD_Timeout_Pump2
        U3_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 4 Then
        U4_VD_C_Set = U1_VD_C_Set
        U4_VD_C_Stock = U1_VD_C_Stock
        U4_VD_StepRes = U1_VD_StepRes
        U4_VD_CycleSet = U1_VD_CycleSet
        U4_VD_ExpTarget = U1_VD_ExpTarget
        U4_VD_PreMixTime = U1_VD_PreMixTime
        U4_VD_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
        U4_VD_RestTime = U1_VD_RestTime
        U4_VD_RestTime_Min = U1_VD_RestTime_Min
        U4_VD_CycleExtend_Max = U1_VD_CycleExtend_Max
        U4_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U4_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U4_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U4_VD_Timeout_Pump1 = U1_VD_Timeout_Pump1
        U4_VD_Timeout_Pump2 = U1_VD_Timeout_Pump2
        U4_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 5 Then
        U5_VD_C_Set = U1_VD_C_Set
        U5_VD_C_Stock = U1_VD_C_Stock
        U5_VD_StepRes = U1_VD_StepRes
        U5_VD_CycleSet = U1_VD_CycleSet
        U5_VD_ExpTarget = U1_VD_ExpTarget
        U5_VD_PreMixTime = U1_VD_PreMixTime
        U5_VD_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
        U5_VD_RestTime = U1_VD_RestTime
        U5_VD_RestTime_Min = U1_VD_RestTime_Min
        U5_VD_CycleExtend_Max = U1_VD_CycleExtend_Max
        U5_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U5_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U5_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U5_VD_Timeout_Pump1 = U1_VD_Timeout_Pump1
        U5_VD_Timeout_Pump2 = U1_VD_Timeout_Pump2
        U5_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 6 Then
        U6_VD_C_Set = U1_VD_C_Set
        U6_VD_C_Stock = U1_VD_C_Stock
        U6_VD_StepRes = U1_VD_StepRes
        U6_VD_CycleSet = U1_VD_CycleSet
        U6_VD_ExpTarget = U1_VD_ExpTarget
        U6_VD_PreMixTime = U1_VD_PreMixTime
        U6_VD_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
        U6_VD_RestTime = U1_VD_RestTime
        U6_VD_RestTime_Min = U1_VD_RestTime_Min
        U6_VD_CycleExtend_Max = U1_VD_CycleExtend_Max
        U6_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U6_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U6_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U6_VD_Timeout_Pump1 = U1_VD_Timeout_Pump1
        U6_VD_Timeout_Pump2 = U1_VD_Timeout_Pump2
        U6_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 7 Then
        U7_VD_C_Set = U1_VD_C_Set
        U7_VD_C_Stock = U1_VD_C_Stock
        U7_VD_StepRes = U1_VD_StepRes
        U7_VD_CycleSet = U1_VD_CycleSet
        U7_VD_ExpTarget = U1_VD_ExpTarget
        U7_VD_PreMixTime = U1_VD_PreMixTime
        U7_VD_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
        U7_VD_RestTime = U1_VD_RestTime
        U7_VD_RestTime_Min = U1_VD_RestTime_Min
        U7_VD_CycleExtend_Max = U1_VD_CycleExtend_Max
        U7_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U7_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U7_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U7_VD_Timeout_Pump1 = U1_VD_Timeout_Pump1
        U7_VD_Timeout_Pump2 = U1_VD_Timeout_Pump2
        U7_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
    If ParamDstUnit = 8 Then
        U8_VD_C_Set = U1_VD_C_Set
        U8_VD_C_Stock = U1_VD_C_Stock
        U8_VD_StepRes = U1_VD_StepRes
        U8_VD_CycleSet = U1_VD_CycleSet
        U8_VD_ExpTarget = U1_VD_ExpTarget
        U8_VD_PreMixTime = U1_VD_PreMixTime
        U8_VD_PreMixTime_MinSafe = U1_VD_PreMixTime_MinSafe
        U8_VD_RestTime = U1_VD_RestTime
        U8_VD_RestTime_Min = U1_VD_RestTime_Min
        U8_VD_CycleExtend_Max = U1_VD_CycleExtend_Max
        U8_VD_Timeout_ValveA = U1_VD_Timeout_ValveA
        U8_VD_Timeout_ValveB = U1_VD_Timeout_ValveB
        U8_VD_Timeout_ValveC = U1_VD_Timeout_ValveC
        U8_VD_Timeout_Pump1 = U1_VD_Timeout_Pump1
        U8_VD_Timeout_Pump2 = U1_VD_Timeout_Pump2
        U8_VD_Delay_ValveA_Verify = U1_VD_Delay_ValveA_Verify
    EndIf
EndIf

' --- 3. 源2~8号 → 目标单元(扩展方法) ---
' 当 ParamSrcUnit = 2~8 时,把上面源1号块中的:
'   - 外层 If ParamSrcUnit = 1 改为对应源单元号
'   - 内层 U1_VD_* (源读取) 全部替换为 U<src>_VD_*
'   - 内层 U<n>_VD_* (目标写入) 保持目标单元号
' 例: 源2号→目标5号的关键行:
'   U5_VD_C_Set = U2_VD_C_Set
'   U5_VD_C_Stock = U2_VD_C_Stock
'   ... (其余14项同理)
' 完整脚本应在组态时按 8x7=56 种组合全部展开,本文件以源1号为代表。

!Beep()
!CloseAllSubWnd()
```

**取消按钮**:
```
!CloseAllSubWnd()
```

---

## 十二、组态实施注意事项

### 1. 子窗口模式参数说明

本文件中 `!OpenSubWnd` 的第6个参数统一为 `17`,计算方式:
- `1` (bit0) = 模态模式(子窗口外鼠标不响应,必须 CloseSubWnd 关闭)
- `16` (bit4) = 显示边框
- 17 = 1 + 16

如需菜单模式(子窗口外按下鼠标自动关闭),改用 `2` 或 `18` (2+16)。如需跟随鼠标位置弹出,加 `32` (bit5),例如 `49 = 1+16+32`。

### 2. 内部变量清单(需在实时数据库预先组态)

本文件涉及的内部变量(非 PLC 通道变量):

| 变量名 | 类型 | 用途 | 断电保持 |
|---|---|---|---|
| SelectedUnit | integer | 当前选中单元号 1~8 | 否 |
| GlobalAlarmActive | integer | 全局报警激活标志 | 否 |
| GlobalMuteState | integer | 全局消音状态 | 否 |
| GlobalAckPending | integer | 全局待确认标志 | 否 |
| CommStatus | integer | 在线单元计数 0~8 | 否 |
| SysTimeString | string | 系统时间显示串 | 否 |
| LoginTime | integer | 登录时间戳(秒) | 否 |
| LastMouseTime | integer | 最后鼠标操作时间 | 否 |
| ExitLogonEnabled | integer | 退出权限检查模式 | 否 |
| U1_Online ~ U8_Online | integer | 8单元通讯在线状态 | 否 |
| U1_Enable ~ U8_Enable | integer | 8单元使能配置 | **是** |
| CurrentUnitStr | string | "当前操作:X号单元" | 否 |
| Param_* (16个) | single | 参数编辑缓冲区 | 否 |
| ParamValid / ParamInvalidStr | integer/string | 校验结果 | 否 |
| ParamSrcUnit / ParamDstUnit | integer | 复制参数源/目标 | 否 |
| SubWndMode | integer | 子窗口模式 0=复制/1=筛选 | 否 |
| AlmFilterUnit / AlmFilterStr | integer/string | 报警筛选 | 否 |
| TrendTimeRange / TrendRangeStr | integer/string | 趋势时间范围 | 否 |
| TrendDisplayUnit | integer | 趋势显示单元 | 否 |
| PLC01~08_Status | integer | 8台PLC状态 | 否 |
| MBPump01~08_Status | integer | 8个注射泵状态 | 否 |
| MBFlow01~08_Status | integer | 8个流量计状态 | 否 |
| CurrentUserStr / CurrentUserGroupStr | string | 当前用户/组显示 | 否 |
| UnitEnableSummary | string | 使能单元汇总串 | 否 |

### 3. 用户组组态(对应权限矩阵)

McgsPro 用户管理需在组态环境中预先建立 3 个用户组:
- `操作员组` (L1) — 含操作员子用户,4位数字密码
- `维护组` (L2) — 含维护工程师子用户,6位数字密码
- `管理员组` (L3) — 含管理员子用户,8位字符密码

`!CheckUserGroup("维护组") = 0` 表示当前用户属于维护组(或更高权限组,如果维护组是管理员组的子组)。本文件采用"维护组 OR 管理员组"嵌套 If 实现向下兼容。

### 4. 组对象存盘配置

脚本45中 `!SaveData(UnitEnableGroup)` 要求:
- 在实时数据库创建组对象 `UnitEnableGroup`
- 把 U1_Enable~U8_Enable 加入该组对象
- 勾选"定时存储到磁盘"+ 存盘周期
- `!FreshDataSave()` 立即刷盘(否则需等60秒)

### 5. 二次确认子窗口组态

8个二次确认子窗口(脚本50~57)需在 McgsPro 用户窗口中分别创建:
- 子窗口_启动确认 / 子窗口_停止确认 / 子窗口_急停确认
- 子窗口_恢复默认确认 / 子窗口_清除日志确认 / 子窗口_退出系统确认
- 子窗口_单元选择 / 子窗口_复制参数确认 / 子窗口_日志浏览

每个子窗口内组态"确认"和"取消"两个标准按钮构件,分别绑定对应 Click 脚本。子窗口尺寸建议 400×180(确认类)或 400×240(选择类)。

### 6. 与 v1.0 的主要差异

| 差异点 | v1.0 (VBScript,错误) | v2.0 (McgsPro 类Basic,正确) |
|---|---|---|
| 循环 | `For i = 1 To 8 ... Next` | 显式展开 8 条赋值语句 |
| 多分支 | `ElseIf` | 嵌套 `If...Then...Else...EndIf` |
| 动态变量名 | `Execute("U" & i & "_CMD_Start = 1")` | `If SelectedUnit = 1 Then U1_CMD_Start = 1 EndIf` (8路分支) |
| 确认对话框 | `MsgBox(...)` | `!OpenSubWnd(子窗口_xxx确认, ..., 17)` |
| 打开窗口 | `!SwitchWindow("画面2")` (不存在) | `!SetWindow(画面2_单元详情, 1)` |
| 权限检查 | `!CheckUser` (不存在) | `!CheckUserGroup("维护组")` |
| 时间函数 | `Now()` / `DateDiff()` | `!TimeGetCurrentTime()` / 直接相减 |
| 变量声明 | `Dim x` (无类型) | `DIM x AS integer` |

### 7. 8单元扩展统一约定

凡涉及"对8个单元相同操作"的脚本,本文件采用以下两种写法之一:
1. **显式展开**(用于必须同时操作8单元的场景,如脚本2/7/8/52):直接写8段If块或8条赋值
2. **以1号为例**(用于按 SelectedUnit 选择单单元操作的场景,如脚本13/14/19~25/50/51):给出1号完整代码 + 2~8号扩展说明(替换单元号)

这是因为 McgsPro **不支持 Execute 动态构造变量名**,无法用循环+字符串拼接访问 U1_XXX~U8_XXX。组态时必须把 8 套代码全部粘贴到对应的 8 个按钮 Click 事件中。

---

**文档结束** — 共 57 个脚本,覆盖 A~K 11 个分区,符合 McgsPro 3.3.6 类 Basic 脚本语言规范。
