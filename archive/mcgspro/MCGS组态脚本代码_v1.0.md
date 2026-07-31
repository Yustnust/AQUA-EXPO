# MCGS组态脚本代码 v1.0

**配套文档**：《HMI画面布局线框图 v1.0》、《画面变量绑定清单 v1.0》、《HMI用户权限矩阵 v1.0》
**用途**：MCGS组态脚本代码,可直接粘贴到MCGS脚本编辑器
**适用范围**：昆仑通态MCGS组态环境(McgseSet)
**Story**：AQEX-12 Story 2.1 8个画面组态开发

---

## 一、脚本语言说明

MCGS脚本语言类似VBScript,特点:
- 不区分大小写
- 变量无需声明,直接赋值
- 注释用单引号 `'`
- 条件语句: `If...Then...Else...EndIf`
- 循环语句: `For...Next` / `Do...Loop`
- 系统函数: `!SetDevice` / `!GetDevice` / `!Sleep` / `!Timer`

**脚本类型**:
1. **窗口脚本** — 画面加载/退出时执行(每画面OnLoad/OnUnload)
2. **按钮脚本** — 按钮点击事件(OnClick)
3. **周期脚本** — 定时执行(每秒/每分钟)
4. **数据变化脚本** — 变量变化时触发

---

> ⚠️ **v2.0 更新提示**：本文件为 v1.0 版本，使用 VBScript 语法。当前工程已升级为两级菜单导航，新增菜单窗口脚本和返回按钮脚本请参见《McgsPro脚本代码_54个_v2.0.md》（已更新为66个脚本）。本文件中的画面切换脚本（!OpenWindow）已被 !CloseAllWindow 替代，返回按钮目标已从画面1_总览改为各自上级菜单窗口。详见《McgsPro两级菜单改造方案_v1.0》。

## 二、全局初始化脚本(工程启动时执行一次)

**位置**：MCGS组态→主控窗口→启动脚本

```vbscript
' ============================================
' AQUA-EXPO MCGS工程启动脚本
' 功能: 初始化HMI内部变量,加载单元使能配置
' ============================================

' 初始化选中单元(默认1号)
SelectedUnit = 1

' 初始化登录状态(未登录)
LoginLevel = 0
LoginTime = ""

' 初始化单元使能(默认8套全使能,实际按配置页设置)
UnitEnabled_01 = 1
UnitEnabled_02 = 1
UnitEnabled_03 = 1
UnitEnabled_04 = 1
UnitEnabled_05 = 1
UnitEnabled_06 = 1
UnitEnabled_07 = 1
UnitEnabled_08 = 1

' 初始化全局状态
GlobalAlarmActive = 0
GlobalMuteState = 0

' 初始化通讯状态(待首次轮询后更新)
CommStatus_01 = 0
CommStatus_02 = 0
CommStatus_03 = 0
CommStatus_04 = 0
CommStatus_05 = 0
CommStatus_06 = 0
CommStatus_07 = 0
CommStatus_08 = 0

' 记录启动时间
Dim startTime
startTime = Now()

' 初始化当前菜单组(0=主菜单)
CurrentMenuGroup = 0
```

---

## 三、周期脚本(每秒执行)

**位置**：MCGS组态→主控窗口→循环策略→每1秒

### 3.1 通讯状态检测脚本

```vbscript
' ============================================
' 通讯状态检测(每秒执行)
' 检测8个PLC连接状态,更新CommStatus_01~08
' ============================================
Dim i
For i = 1 To 8
    Dim connName, statusVar
    connName = "PLC_" & Format(i, "00")
    statusVar = "CommStatus_" & Format(i, "00")

    ' 检测连接状态(MCGS提供!GetDeviceState函数)
    Dim state
    state = !GetDeviceState(connName)

    ' state=0在线,非0离线
    If state = 0 Then
        Execute(statusVar & " = 1")  ' 在线
    Else
        Execute(statusVar & " = 0")  ' 离线
    End If
Next

' 全局报警检测(任一使能单元有报警→GlobalAlarmActive)
GlobalAlarmActive = 0
For i = 1 To 8
    Dim enabledVar, alarmVar
    enabledVar = "UnitEnabled_" & Format(i, "00")
    alarmVar = "U" & i & "_VW6_AlarmCode"

    If GetValue(enabledVar) = 1 Then
        Dim alarmCode
        alarmCode = GetValue(alarmVar)
        If alarmCode <> 0 Then
            GlobalAlarmActive = 1
            Exit For
        End If
    End If
Next
```

### 3.2 登录超时检测脚本(每秒执行)

```vbscript
' ============================================
' 登录超时检测(每秒执行)
' L1/L2/L3权限15分钟无操作自动注销
' ============================================
If LoginLevel > 0 Then
    Dim lastOp, elapsed
    lastOp = CDate(LoginTime)
    elapsed = DateDiff("s", lastOp, Now())

    ' 15分钟=900秒无操作自动注销
    If elapsed > 900 Then
        LoginLevel = 0
        LoginTime = ""
        !Beep(200, 100)  ' 提示音
    End If
End If
```

---

## 四、画面1｜8套总览首页脚本

### 4.1 画面加载脚本(OnLoad)

```vbscript
' 画面1加载: 初始化总览数据
' 显示8个单元卡片状态
```

### 4.2 单元卡片点击脚本(OnClick)

**每张卡片(8张)的点击脚本相同,仅单元号不同**:

```vbscript
' 1号单元卡片点击
SelectedUnit = 1
!SwitchWindow("画面2_单元详情")
```

```vbscript
' 2号单元卡片点击
SelectedUnit = 2
!SwitchWindow("画面2_单元详情")
```

(3~8号同理)

### 4.3 全局消音按钮脚本(OnClick)

```vbscript
' ============================================
' 全局消音按钮(二次确认)
' 循环写入所有使能单元的CMD_Mute=1
' ============================================

' 二次确认弹窗
Dim result
result = !MsgBox("确认对所有报警单元执行消音?", 1, "消音确认")
If result = 1 Then  ' 1=确认
    Dim i
    For i = 1 To 8
        Dim enabledVar, muteVar
        enabledVar = "UnitEnabled_" & Format(i, "00")
        muteVar = "U" & i & "_CMD_Mute"

        If GetValue(enabledVar) = 1 Then
            Execute(muteVar & " = 1")  ' 写入消音命令
        End If
    Next
    GlobalMuteState = 1
End If
```

### 4.4 单元卡片状态颜色脚本(每秒执行)

```vbscript
' ============================================
' 单元卡片颜色刷新(每秒)
' 根据:使能×通讯×报警 三态显示
' ============================================
Dim i
For i = 1 To 8
    Dim enabled, comm, alarm, bgColor

    enabled = GetValue("UnitEnabled_" & Format(i, "00"))
    comm = GetValue("CommStatus_" & Format(i, "00"))
    alarm = GetValue("U" & i & "_VW6_AlarmCode")

    If enabled = 0 Then
        bgColor = &H808080  ' 灰色(未使能)
    ElseIf comm = 0 Then
        bgColor = &H00FFFF  ' 黄色(通讯中断)
    ElseIf alarm = 99 Then
        bgColor = &H0000FF  ' 红色闪烁(最高级报警)
    ElseIf alarm >= 10 And alarm <= 14 Then
        bgColor = &H0000FF  ' 红色(漫溢级)
    ElseIf alarm >= 20 And alarm <= 66 Then
        bgColor = &H0080FF  ' 橙色(一般级)
    Else
        bgColor = &H00FF00  ' 绿色(正常)
    End If

    ' 设置卡片背景色(假设卡片名为UnitCard_01~08)
    Dim cardName
    cardName = "UnitCard_" & Format(i, "00")
    !SetObjectProperty(cardName, "BackColor", bgColor)
Next
```

---

## 五、画面2｜单元详情页脚本

### 5.1 画面加载脚本(OnLoad)

```vbscript
' 画面2加载: 根据SelectedUnit显示对应单元数据
Dim unit
unit = SelectedUnit

' 显示"当前操作:X号单元"
!SetObjectProperty("lblCurrentUnit", "Caption", "当前操作:" & unit & "号单元")
```

### 5.2 单元选择器切换脚本(OnClick)

**8个单元按钮(1~8号)点击脚本**:

```vbscript
' 1号单元按钮
SelectedUnit = 1
' 刷新画面2所有数据绑定
!RefreshWindow()
```

(2~8号同理)

### 5.3 状态机文本映射脚本(每秒执行)

```vbscript
' ============================================
' 状态机VW2→中文文本映射
' ============================================
Dim stateCode, stateText
stateCode = GetValue("U" & SelectedUnit & "_VW2_StateMachine")

Select Case stateCode
    Case 0: stateText = "S0 初始化"
    Case 1: stateText = "S1 上缸进水"
    Case 2: stateText = "S2 预循环搅拌"
    Case 3: stateText = "S3 加药"
    Case 4: stateText = "S3.5 静止等候"
    Case 5: stateText = "S4 上→下转移"
    Case 6: stateText = "S5 实验运行中"
    Case 7: stateText = "S6 下缸排水"
    Case 8: stateText = "S7 实验结束"
    Case 99: stateText = "故障锁定"
    Case Else: stateText = "未知状态(" & stateCode & ")"
End Select

!SetObjectProperty("lblStateMachine", "Caption", stateText)
```

### 5.4 注射泵状态映射脚本

```vbscript
' 注射泵状态码VW4→文本
Dim pumpCode, pumpText
pumpCode = GetValue("U" & SelectedUnit & "_VW4_PumpStatus")

Select Case pumpCode
    Case 0: pumpText = "空闲/完成"
    Case 1: pumpText = "运行中"
    Case 2: pumpText = "抽液中"
    Case 3: pumpText = "排液中"
    Case Else: pumpText = "错误码:" & pumpCode
End Select

!SetObjectProperty("lblPumpStatus", "Caption", pumpText)
```

---

## 六、画面3｜手动控制页脚本

### 6.1 权限检查脚本(画面加载)

```vbscript
' ============================================
' 手动控制页权限检查
' 需L2(维护)或L3(管理员)权限
' ============================================
If LoginLevel < 2 Then
    !MsgBox("权限不足!手动控制需维护(L2)或管理员(L3)权限", 0, "权限提示")
    !CloseAllWindow("菜单_单元操作")
    Exit Sub
End If

' 刷新操作时间(权限检查通过视为操作)
LoginTime = CStr(Now())
```

### 6.2 手动开阀A按钮脚本(OnClick)

```vbscript
' ============================================
' 手动开阀A(二次确认+联锁提示)
' ============================================
Dim unit, stateCode
unit = SelectedUnit
stateCode = GetValue("U" & unit & "_VW2_StateMachine")

' 联锁检查: 仅S0或S_ERROR态允许手动
If stateCode <> 0 And stateCode <> 99 Then
    !MsgBox("运行中不允许手动操作!当前状态:" & stateCode, 0, "联锁提示")
    Exit Sub
End If

' 二次确认
Dim result
result = !MsgBox("确认手动开启阀A?", 1, "手动操作确认")
If result = 1 Then
    Execute("U" & unit & "_CMD_Manual_ValveA_Open = 1")
    LoginTime = CStr(Now())  ' 刷新操作时间
End If
```

### 6.3 手动开阀B按钮脚本(OnClick,含联锁)

```vbscript
' ============================================
' 手动开阀B(联锁:上缸=满 AND 下缸=空)
' ============================================
Dim unit, stateCode, tankA, tankB
unit = SelectedUnit
stateCode = GetValue("U" & unit & "_VW2_StateMachine")
tankA = GetValue("U" & unit & "_STA_TankA_State")
tankB = GetValue("U" & unit & "_STA_TankB_State")

' 状态联锁
If stateCode <> 0 And stateCode <> 99 Then
    !MsgBox("运行中不允许手动操作!", 0, "联锁提示")
    Exit Sub
End If

' 工艺联锁
If tankA <> 1 Or tankB <> 0 Then
    !MsgBox("联锁条件不满足!阀B开启需:上缸=满 AND 下缸=空", 0, "联锁提示")
    Exit Sub
End If

Dim result
result = !MsgBox("确认手动开启阀B?", 1, "手动操作确认")
If result = 1 Then
    Execute("U" & unit & "_CMD_Manual_ValveB_Open = 1")
    LoginTime = CStr(Now())
End If
```

### 6.4 手动开阀C按钮脚本(OnClick,含联锁)

```vbscript
' 手动开阀C(联锁:下缸=满)
Dim unit, stateCode, tankB
unit = SelectedUnit
stateCode = GetValue("U" & unit & "_VW2_StateMachine")
tankB = GetValue("U" & unit & "_STA_TankB_State")

If stateCode <> 0 And stateCode <> 99 Then
    !MsgBox("运行中不允许手动操作!", 0, "联锁提示")
    Exit Sub
End If

If tankB <> 1 Then
    !MsgBox("联锁条件不满足!阀C开启需:下缸=满", 0, "联锁提示")
    Exit Sub
End If

Dim result
result = !MsgBox("确认手动开启阀C?", 1, "手动操作确认")
If result = 1 Then
    Execute("U" & unit & "_CMD_Manual_ValveC_Open = 1")
    LoginTime = CStr(Now())
End If
```

### 6.5 其他手动按钮(结构相同)

手动关阀A/B/C、开泵1/停泵1的结构与6.2相同,仅变量名和确认文本不同:
- `CMD_Manual_ValveA_Close` → "确认手动关闭阀A?"
- `CMD_Manual_ValveB_Close` → "确认手动关闭阀B?"
- `CMD_Manual_ValveC_Close` → "确认手动关闭阀C?"
- `CMD_Manual_Pump1_On` → "确认手动启动潜水泵1?"
- `CMD_Manual_Pump1_Off` → "确认手动停止潜水泵1?"

---

## 七、画面4｜参数设置页脚本

### 7.1 权限检查(画面加载)

```vbscript
' 参数设置需L2或L3权限
If LoginLevel < 2 Then
    !MsgBox("权限不足!参数设置需维护(L2)或管理员(L3)权限", 0, "权限提示")
    !CloseAllWindow("菜单_单元操作")
    Exit Sub
End If
LoginTime = CStr(Now())
```

### 7.2 参数保存按钮(OnClick)

```vbscript
' ============================================
' 参数保存(二次确认+范围校验)
' ============================================
Dim result
result = !MsgBox("确认保存参数到PLC?参数变更可能影响实验进程", 1, "参数保存确认")
If result <> 1 Then Exit Sub

Dim unit
unit = SelectedUnit

' 范围校验
Dim cSet, cycleSet, timeoutA
cSet = GetValue("U" & unit & "_VD_C_Set")
cycleSet = GetValue("U" & unit & "_VD_CycleSetpoint")
timeoutA = GetValue("U" & unit & "_VD_Timeout_ValveA")

If cSet <= 0 Or cSet > 50 Then
    !MsgBox("浓度设定值超范围(0~50%)!", 0, "校验失败")
    Exit Sub
End If

If cycleSet < 5 Or cycleSet > 120 Then
    !MsgBox("换水周期超范围(5~120min)!", 0, "校验失败")
    Exit Sub
End If

If timeoutA < 10 Or timeoutA > 300 Then
    !MsgBox("阀A超时超范围(10~300s)!", 0, "校验失败")
    Exit Sub
End If

' 参数已通过双向绑定自动写入PLC,MCGS变量变化即触发写入
' 此处仅做保存日志记录
!MsgBox("参数已保存到" & unit & "号单元PLC", 0, "保存成功")
LoginTime = CStr(Now())
```

### 7.3 参数恢复默认按钮(OnClick)

```vbscript
' 恢复默认参数(L3管理员权限)
If LoginLevel < 3 Then
    !MsgBox("权限不足!恢复默认需管理员(L3)权限", 0, "权限提示")
    Exit Sub
End If

Dim result
result = !MsgBox("确认恢复所有参数为默认值?此操作不可撤销!", 1, "恢复默认确认")
If result <> 1 Then Exit Sub

Dim unit
unit = SelectedUnit

' 写入默认值
Execute("U" & unit & "_VD_C_Set = 5.0")
Execute("U" & unit & "_VD_C_Stock = 100.0")
Execute("U" & unit & "_VD_StepResolution = 0.2083")
Execute("U" & unit & "_VD_CycleSetpoint = 30.0")
Execute("U" & unit & "_VD_ExperimentTarget = 480.0")
Execute("U" & unit & "_VD_PreMixTime = 120.0")
Execute("U" & unit & "_VD_RestTime = 60.0")
Execute("U" & unit & "_VD_Timeout_ValveA = 60.0")
Execute("U" & unit & "_VD_Timeout_ValveB = 60.0")
Execute("U" & unit & "_VD_Timeout_ValveC = 60.0")

!MsgBox("参数已恢复默认", 0, "完成")
LoginTime = CStr(Now())
```

---

## 八、画面5｜报警页脚本

### 8.1 报警确认按钮(OnClick)

```vbscript
' ============================================
' 报警确认(根据报警等级判断权限)
' 漫溢级/最高级需L2+,节奏级/一般级L1+即可
' ============================================
Dim unit, alarmCode
unit = SelectedUnit
alarmCode = GetValue("U" & unit & "_VW6_AlarmCode")

If alarmCode = 0 Then
    !MsgBox("当前无报警", 0, "提示")
    Exit Sub
End If

' 权限判断
Dim needLevel
If alarmCode = 99 Or (alarmCode >= 10 And alarmCode <= 14) Then
    needLevel = 2  ' 最高级/漫溢级需L2+
ElseIf alarmCode >= 20 And alarmCode <= 21 Then
    needLevel = 2  ' 节奏级需L2+
Else
    needLevel = 1  ' 一般级L1+即可
End If

If LoginLevel < needLevel Then
    !MsgBox("权限不足!此报警需L" & needLevel & "权限确认", 0, "权限提示")
    Exit Sub
End If

Dim result
result = !MsgBox("确认报警?报警码:" & alarmCode, 1, "报警确认")
If result = 1 Then
    Execute("U" & unit & "_CMD_AckAlarm = 1")
    LoginTime = CStr(Now())
End If
```

### 8.2 报警颜色映射脚本(每秒执行)

```vbscript
' ============================================
' 32位报警字解析+颜色映射
' 遍历VB300~VB303共32位,显示活动报警
' ============================================
Dim unit, i, alarmText, alarmColor
unit = SelectedUnit
alarmText = ""
alarmColor = &H00FF00  ' 默认绿色

' 检查32个报警位(按优先级顺序)
Dim alarmBits(31)
alarmBits(0) = "V300_5_Alarm_SafetyRelay"      ' 最高级 99
alarmBits(1) = "V300_0_Alarm_Overflow_AHigh"   ' 漫溢 10
alarmBits(2) = "V300_1_Alarm_Overflow_BHigh"   ' 漫溢 11
alarmBits(3) = "V300_2_Alarm_NCValve_Top"      ' 漫溢 12
alarmBits(4) = "V300_3_Alarm_NCValve_Bottom"   ' 漫溢 13
alarmBits(5) = "V300_4_EStop_Latch"            ' 漫溢 14
alarmBits(6) = "V300_6_Alarm_ScheduleLag"      ' 节奏 20
alarmBits(7) = "V300_7_Alarm_ScheduleLag_Warn" ' 节奏 21
alarmBits(8) = "V301_0_Alarm_ValveA_CloseFlow" ' 一般 30
' ... 其余23位

Dim alarmTexts(31)
alarmTexts(0) = "安全继电器故障(最高级)"
alarmTexts(1) = "上缸漫溢"
alarmTexts(2) = "下缸漫溢"
alarmTexts(3) = "NC电磁阀-上缸动作"
alarmTexts(4) = "NC电磁阀-下缸动作"
alarmTexts(5) = "急停触发"
alarmTexts(6) = "配液节奏严重滞后"
alarmTexts(7) = "配液节奏滞后提示"
alarmTexts(8) = "阀A关后仍有流"
' ... 其余文本

Dim alarmColors(31)
alarmColors(0) = &H0000FF  ' 红色闪烁
alarmColors(1) = &H0000FF  ' 红色
alarmColors(6) = &H0080FF  ' 橙色
alarmColors(7) = &H00FFFF  ' 黄色
alarmColors(8) = &H0080FF  ' 橙色

' 遍历检查
For i = 0 To 31
    Dim bitVar, bitVal
    bitVar = "U" & unit & "_" & alarmBits(i)
    bitVal = GetValue(bitVar)

    If bitVal = 1 Then
        alarmText = alarmText & "• " & alarmTexts(i) & Chr(13) & Chr(10)
        If alarmColors(i) <> 0 Then
            alarmColor = alarmColors(i)
        End If
    End If
Next

If alarmText = "" Then
    alarmText = "无活动报警"
End If

' 更新显示
!SetObjectProperty("lblAlarmList", "Caption", alarmText)
!SetObjectProperty("lblAlarmList", "ForeColor", alarmColor)
```

### 8.3 继电器故障HMI确认按钮(OnClick,需L3)

```vbscript
' 安全继电器故障确认(需L3管理员+二次确认)
If LoginLevel < 3 Then
    !MsgBox("权限不足!继电器故障确认需管理员(L3)权限", 0, "权限提示")
    Exit Sub
End If

Dim result
result = !MsgBox("⚠️ 危险操作!确认安全继电器故障已排除?此操作将清除V300.5报警", 1, "继电器故障确认")
If result = 1 Then
    Dim unit
    unit = SelectedUnit
    Execute("U" & unit & "_CMD_SafetyRelayAck = 1")
    LoginTime = CStr(Now())
End If
```

---

## 九、画面6｜趋势曲线页脚本

### 9.1 画面加载脚本(OnLoad)

```vbscript
' 趋势曲线页加载
' 配置曲线变量:实验时长/换水周期/流速
Dim unit
unit = SelectedUnit

' 设置趋势曲线数据源
!SetObjectProperty("TrendChart", "Curve1Var", "U" & unit & "_VD_ExperimentDuration_Accum")
!SetObjectProperty("TrendChart", "Curve1Name", "实验时长(min)")

!SetObjectProperty("TrendChart", "Curve2Var", "U" & unit & "_VD_CycleSetpoint")
!SetObjectProperty("TrendChart", "Curve2Name", "换水周期(min)")

!SetObjectProperty("TrendChart", "Curve3Var", "U" & unit & "_VD_FlowRate_Instant")
!SetObjectProperty("TrendChart", "Curve3Name", "瞬时流速(L/min)")

!SetObjectProperty("TrendChart", "Curve4Var", "U" & unit & "_VD_S6_Rolling")
!SetObjectProperty("TrendChart", "Curve4Name", "S6排水时长(s)")
```

### 9.2 时间范围切换按钮(OnClick)

```vbscript
' 切换时间范围(1小时/4小时/24小时)
Dim range
range = !GetTag("TrendRange")

Select Case range
    Case 1: !SetObjectProperty("TrendChart", "TimeRange", 3600)     ' 1小时
    Case 2: !SetObjectProperty("TrendChart", "TimeRange", 14400)    ' 4小时
    Case 3: !SetObjectProperty("TrendChart", "TimeRange", 86400)    ' 24小时
End Select
```

---

## 十、画面7｜通讯与使能配置页脚本

### 7.1 权限检查(画面加载)

```vbscript
' 通讯与使能配置需L3管理员权限
If LoginLevel < 3 Then
    !MsgBox("权限不足!系统配置需管理员(L3)权限", 0, "权限提示")
    !CloseAllWindow("菜单_监控诊断")
    Exit Sub
End If
LoginTime = CStr(Now())
```

### 7.2 单元使能切换按钮(OnClick,8个按钮相同结构)

```vbscript
' 1号单元使能切换
Dim result
result = !MsgBox("确认切换1号单元使能状态?", 1, "使能切换")
If result = 1 Then
    UnitEnabled_01 = 1 - UnitEnabled_01  ' 翻转
    LoginTime = CStr(Now())
End If
```

### 7.3 保存配置按钮(OnClick)

```vbscript
' 保存使能配置到HMI本地存储(断电保持)
Dim result
result = !MsgBox("保存使能配置?配置将断电保持", 1, "保存确认")
If result = 1 Then
    ' MCGS内部变量已配置为断电保持,无需额外操作
    !MsgBox("配置已保存", 0, "完成")
End If
```

---

## 十一、画面8｜系统设置页脚本

### 8.1 登录按钮(OnClick)

```vbscript
' ============================================
' 用户登录(密码验证)
' L1操作员: 1111
' L2维护: 2222
' L3管理员: 3333
' ============================================
Dim pwd
pwd = !InputBox("请输入密码:", "用户登录", "")

Select Case pwd
    Case "1111"
        LoginLevel = 1
        LoginTime = CStr(Now())
        !MsgBox("登录成功:L1操作员", 0, "登录")
    Case "2222"
        LoginLevel = 2
        LoginTime = CStr(Now())
        !MsgBox("登录成功:L2维护", 0, "登录")
    Case "3333"
        LoginLevel = 3
        LoginTime = CStr(Now())
        !MsgBox("登录成功:L3管理员", 0, "登录")
    Case ""
        ' 取消登录
    Case Else
        !MsgBox("密码错误!", 0, "登录失败")
End Select
```

### 8.2 注销按钮(OnClick)

```vbscript
' 注销
Dim result
result = !MsgBox("确认注销当前用户?", 1, "注销确认")
If result = 1 Then
    LoginLevel = 0
    LoginTime = ""
End If
```

### 8.3 系统时间同步按钮(OnClick,需L3)

```vbscript
' 系统时间同步(将HMI时间同步到所有PLC)
If LoginLevel < 3 Then
    !MsgBox("权限不足!时间同步需管理员(L3)权限", 0, "权限提示")
    Exit Sub
End If

Dim result
result = !MsgBox("确认将HMI时间同步到所有使能单元PLC?", 1, "时间同步")
If result = 1 Then
    Dim i
    For i = 1 To 8
        Dim enabledVar
        enabledVar = "UnitEnabled_" & Format(i, "00")
        If GetValue(enabledVar) = 1 Then
            ' 写入PLC时间寄存器(S7协议SetRTC)
            ' MCGS提供!SetPLCTime函数
            Dim connName
            connName = "PLC_" & Format(i, "00")
            !SetPLCTime(connName)
        End If
    Next
    !MsgBox("时间同步完成", 0, "完成")
    LoginTime = CStr(Now())
End If
```

---

## 十二、辅助函数(脚本库)

### 12.1 GetValue函数(动态变量取值)

```vbscript
' ============================================
' GetValue: 按变量名字符串取值
' MCGS内置Execute可赋值,但取值需自定义
' ============================================
Function GetValue(varName)
    ' MCGS通过!GetVarByName函数取值
    GetValue = !GetVarByName(varName)
End Function
```

### 12.2 Format函数(数字格式化)

```vbscript
' Format: 数字格式化为指定位数
' 例: Format(5, "00") = "05"
Function Format(num, fmt)
    Format = Right("00" & CStr(num), Len(fmt))
End Function
```

---

## 十三、脚本调试与验证

### 13.1 脚本调试技巧

1. MCGS组态环境→脚本编辑器→语法检查
2. 用`!MsgBox`输出调试信息
3. 用`!LogWrite`写入日志文件
4. 仿真模式下逐步执行验证

### 13.2 常见错误

| 错误 | 原因 | 解决 |
|---|---|---|
| 变量未定义 | 变量名拼写错误 | 检查变量名与CSV导入一致 |
| 类型不匹配 | Int/Float/Bool混用 | 用CStr/CInt/CSng转换 |
| Execute失败 | 变量名含特殊字符 | 仅用字母数字下划线 |
| 权限检查失败 | LoginTime未刷新 | 每次操作后刷新LoginTime |
| 通讯状态错误 | !GetDeviceState不可用 | 改用读取变量超时判断 |

### 13.3 性能优化

1. 周期脚本执行间隔≥1秒,避免过频
2. For循环≤8次(8套单元),不会卡顿
3. 避免在每秒脚本中调用!MsgBox(阻塞)
4. 趋势曲线变量≤4条,避免刷新过慢

---

## 十四、脚本与画面绑定清单

| 画面 | 脚本类型 | 脚本数量 | 触发频率 |
|---|---|---|---|
| 工程启动 | 启动脚本 | 1 | 1次 |
| 主控窗口 | 周期脚本(通讯+超时) | 2 | 每秒 |
| 画面1 总览 | 卡片点击+消音+颜色 | 11 | 事件/每秒 |
| 画面2 详情 | 加载+选择器+映射 | 11 | 事件/每秒 |
| 画面3 手动 | 权限+8个按钮 | 9 | 事件 |
| 画面4 参数 | 权限+保存+默认 | 3 | 事件 |
| 画面5 报警 | 确认+颜色+继电器 | 3 | 事件/每秒 |
| 画面6 趋势 | 加载+时间范围 | 2 | 事件 |
| 画面7 配置 | 权限+8使能+保存 | 10 | 事件 |
| 画面8 设置 | 登录+注销+同步 | 3 | 事件 |
| **合计** | — | **54** | — |

---

**文档结束**

**待办**:
1. MCGS组态环境中实际粘贴测试每个脚本
2. 部分MCGS专用函数(!GetDeviceState/!SetPLCTime等)需按实际MCGS版本调整
3. 密码存储建议改用MCGS用户管理(加密存储),本脚本是简化示例
4. 趋势曲线变量需在MCGS历史数据组态中配置存档
