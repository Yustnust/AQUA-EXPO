# Story 2.2 分期接入动态显隐机制 v1.0

**配套文档**：《HMI画面架构规划文档 v9.3》第九章、《MCGS组态脚本代码 v1.0》、《MCGS画面组态详细SOP v1.0》
**适用范围**：8套缸单元HMI画面动态显隐与三态显示
**Story**：AQEX-13 Story 2.2 分期接入动态显隐机制实现

---

## 一、设计目标

### 1.1 业务需求

8套缸单元分期上线(首期1~4号,二期5~8号),HMI需根据单元使能状态动态显示:
- **使能的单元**:正常显示,可操作,实时数据刷新
- **未使能的单元**:画面1卡片灰色,不可点击,不显示数据
- **通讯中断的使能单元**:卡片黄色,提示通讯中断
- **报警中的使能单元**:卡片红色/橙色,显示报警级别

### 1.2 三态显示判定机制

每个单元显示状态由三个维度组合判定:

| 维度 | 变量 | 取值 | 来源 |
|---|---|---|---|
| 使能 | UnitEnabled_XX | 0/1 | HMI内部(画面7配置) |
| 通讯 | CommStatus_XX | 0/1 | 周期脚本检测 |
| 报警 | UXX_VW6_AlarmCode | 0/10~14/20~21/30~66/99 | PLC读取 |

### 1.3 显示状态矩阵

| 使能 | 通讯 | 报警码 | 显示状态 | 卡片颜色 | 可点击 | 数据刷新 |
|---|---|---|---|---|---|---|
| 0 | — | — | 未使能 | 灰色(&H808080) | 否 | 否 |
| 1 | 0 | — | 通讯中断 | 黄色(&H00FFFF) | 是(显示提示) | 否 |
| 1 | 1 | 0 | 正常运行 | 绿色(&H00FF00) | 是 | 是 |
| 1 | 1 | 10~14 | 漫溢级报警 | 红色(&H0000FF) | 是 | 是 |
| 1 | 1 | 99 | 最高级报警 | 红色闪烁 | 是 | 是 |
| 1 | 1 | 20~21 | 节奏级报警 | 橙色(&H0080FF) | 是 | 是 |
| 1 | 1 | 30~66 | 一般级报警 | 橙色(&H0080FF) | 是 | 是 |

---

## 二、画面1卡片动态显隐机制

### 2.1 卡片可见性控制

```vbscript
' ============================================
' 画面1卡片可见性控制(每秒执行)
' 未使能单元卡片隐藏,改为灰色占位
' ============================================
Dim i
For i = 1 To 8
    Dim enabled, cardName
    enabled = GetValue("UnitEnabled_" & Format(i, "00"))
    cardName = "UnitCard_" & Format(i, "00")

    If enabled = 1 Then
        ' 使能: 显示卡片
        !SetObjectProperty(cardName, "Visible", 1)
        !SetObjectProperty(cardName & "_Label", "Visible", 1)
        !SetObjectProperty(cardName & "_Data", "Visible", 1)
    Else
        ' 未使能: 卡片灰色,数据隐藏,仅显示"未启用"文字
        !SetObjectProperty(cardName, "Visible", 1)
        !SetObjectProperty(cardName, "BackColor", &H808080)  ' 灰色
        !SetObjectProperty(cardName & "_Label", "Caption", i & "号单元 (未启用)")
        !SetObjectProperty(cardName & "_Data", "Visible", 0)  ' 隐藏数据
    End If
Next
```

### 2.2 卡片颜色与点击拦截

```vbscript
' ============================================
' 卡片颜色刷新+点击拦截(每秒执行)
' ============================================
Dim i
For i = 1 To 8
    Dim enabled, comm, alarm, bgColor, clickable
    enabled = GetValue("UnitEnabled_" & Format(i, "00"))
    comm = GetValue("CommStatus_" & Format(i, "00"))
    alarm = GetValue("U" & i & "_VW6_AlarmCode")
    bgColor = &H00FF00  ' 默认绿色
    clickable = 1

    If enabled = 0 Then
        bgColor = &H808080  ' 灰色(未使能)
        clickable = 0
    ElseIf comm = 0 Then
        bgColor = &H00FFFF  ' 黄色(通讯中断)
    ElseIf alarm = 99 Then
        bgColor = &H0000FF  ' 红色(最高级)
        ' 闪烁逻辑: 用秒计数器奇偶切换
        Dim sec
        sec = Second(Now())
        If sec Mod 2 = 0 Then
            bgColor = &H0000FF  ' 红
        Else
            bgColor = &HFFFFFF  ' 白
        End If
    ElseIf alarm >= 10 And alarm <= 14 Then
        bgColor = &H0000FF  ' 红色(漫溢级)
    ElseIf alarm >= 20 And alarm <= 66 Then
        bgColor = &H0080FF  ' 橙色(节奏/一般级)
    End If

    Dim cardName
    cardName = "UnitCard_" & Format(i, "00")
    !SetObjectProperty(cardName, "BackColor", bgColor)
    !SetObjectProperty(cardName, "Enabled", clickable)
Next
```

### 2.3 卡片点击拦截脚本

```vbscript
' ============================================
' 1号卡片点击(OnClick) - 含拦截逻辑
' ============================================
Dim enabled, comm
enabled = UnitEnabled_01
comm = CommStatus_01

If enabled = 0 Then
    !MsgBox("1号单元未启用,请在画面7配置使能", 0, "提示")
    Exit Sub
End If

If comm = 0 Then
    Dim result
    result = !MsgBox("1号单元通讯中断,是否仍进入详情页?", 1, "通讯中断")
    If result <> 1 Then Exit Sub
End If

SelectedUnit = 1
!SwitchWindow("画面2_单元详情")
```

(2~8号卡片同理,仅单元号不同)

---

## 三、画面2详情页动态显隐

### 3.1 通讯中断时的显示策略

当CommStatus_XX=0时,画面2详情页应:
- 显示"通讯中断"红色横幅
- 实测值数据显示"—"(无效)
- 命令按钮禁用
- 报警区域显示"通讯中断,无法获取报警状态"

```vbscript
' ============================================
' 画面2通讯中断处理(每秒执行)
' ============================================
Dim unit, comm
unit = SelectedUnit
comm = GetValue("CommStatus_" & Format(unit, "00"))

If comm = 0 Then
    ' 显示通讯中断横幅
    !SetObjectProperty("CommErrorBanner", "Visible", 1)
    !SetObjectProperty("CommErrorBanner", "Caption", "⚠️ " & unit & "号单元通讯中断")

    ' 实测值显示"—"
    !SetObjectProperty("lbl_S1_Actual", "Caption", "—")
    !SetObjectProperty("lbl_S4_Actual", "Caption", "—")
    !SetObjectProperty("lbl_S6_Actual", "Caption", "—")
    !SetObjectProperty("lbl_FlowRate", "Caption", "—")
    !SetObjectProperty("lbl_InletVolume", "Caption", "—")

    ' 命令按钮禁用
    !SetObjectProperty("btnStart", "Enabled", 0)
    !SetObjectProperty("btnStop", "Enabled", 0)
    !SetObjectProperty("btnAckAlarm", "Enabled", 0)
    !SetObjectProperty("btnMute", "Enabled", 0)
Else
    ' 通讯正常: 隐藏横幅,启用按钮
    !SetObjectProperty("CommErrorBanner", "Visible", 0)
    !SetObjectProperty("btnStart", "Enabled", 1)
    !SetObjectProperty("btnStop", "Enabled", 1)
    !SetObjectProperty("btnAckAlarm", "Enabled", 1)
    !SetObjectProperty("btnMute", "Enabled", 1)
End If
```

### 3.2 未使能单元的访问拦截

```vbscript
' 画面2加载时检查单元使能
Dim unit, enabled
unit = SelectedUnit
enabled = GetValue("UnitEnabled_" & Format(unit, "00"))

If enabled = 0 Then
    !MsgBox(unit & "号单元未启用,无法访问详情", 0, "提示")
    !SwitchWindow("画面1_总览")
    Exit Sub
End If
```

---

## 四、画面3手动控制动态显隐

### 4.1 未使能单元的手动控制拦截

```vbscript
' 画面3加载时检查
Dim unit, enabled
unit = SelectedUnit
enabled = GetValue("UnitEnabled_" & Format(unit, "00"))

If enabled = 0 Then
    !MsgBox(unit & "号单元未启用,无法手动控制", 0, "提示")
    !SwitchWindow("画面1_总览")
    Exit Sub
End If

' 权限检查(原有逻辑)
If LoginLevel < 2 Then
    !MsgBox("权限不足!需维护(L2)或管理员(L3)权限", 0, "权限提示")
    !SwitchWindow("画面1_总览")
    Exit Sub
End If
```

### 4.2 通讯中断时的手动控制禁用

```vbscript
' 通讯中断时所有手动按钮禁用
Dim comm
comm = GetValue("CommStatus_" & Format(SelectedUnit, "00"))

If comm = 0 Then
    !SetObjectProperty("btnValveA_Open", "Enabled", 0)
    !SetObjectProperty("btnValveA_Close", "Enabled", 0)
    !SetObjectProperty("btnValveB_Open", "Enabled", 0)
    !SetObjectProperty("btnValveB_Close", "Enabled", 0)
    !SetObjectProperty("btnValveC_Open", "Enabled", 0)
    !SetObjectProperty("btnValveC_Close", "Enabled", 0)
    !SetObjectProperty("btnPump1_On", "Enabled", 0)
    !SetObjectProperty("btnPump1_Off", "Enabled", 0)
Else
    ' 通讯恢复: 按状态机状态决定是否启用(仅S0/S_ERROR允许手动)
    Dim stateCode
    stateCode = GetValue("U" & SelectedUnit & "_VW2_StateMachine")
    If stateCode = 0 Or stateCode = 99 Then
        !SetObjectProperty("btnValveA_Open", "Enabled", 1)
        ' ...其他按钮启用
    End If
End If
```

---

## 五、画面5报警页动态显隐

### 5.1 报警列表按使能过滤

```vbscript
' ============================================
' 画面5报警列表仅显示使能单元的报警
' ============================================
Dim alarmText, i
alarmText = ""

For i = 1 To 8
    Dim enabled, alarmCode
    enabled = GetValue("UnitEnabled_" & Format(i, "00"))
    alarmCode = GetValue("U" & i & "_VW6_AlarmCode")

    If enabled = 1 And alarmCode <> 0 Then
        alarmText = alarmText & "【" & i & "号单元】报警码:" & alarmCode & Chr(13) & Chr(10)

        ' 解析32位报警字,列出活动报警
        Dim j
        For j = 0 To 31
            Dim bitVar
            bitVar = "U" & i & "_" & GetAlarmBitVar(j)
            If GetValue(bitVar) = 1 Then
                alarmText = alarmText & "  • " & GetAlarmText(j) & Chr(13) & Chr(10)
            End If
        Next
        alarmText = alarmText & Chr(13) & Chr(10)
    End If
Next

If alarmText = "" Then
    alarmText = "无活动报警(仅显示使能单元)"
End If

!SetObjectProperty("lblAlarmList", "Caption", alarmText)
```

### 5.2 报警确认按使能过滤

```vbscript
' 报警确认仅对使能单元生效
Dim unit, enabled
unit = SelectedUnit
enabled = GetValue("UnitEnabled_" & Format(unit, "00"))

If enabled = 0 Then
    !MsgBox(unit & "号单元未启用,无法确认报警", 0, "提示")
    Exit Sub
End If
' ...原有报警确认逻辑
```

---

## 六、画面6趋势曲线动态显隐

### 6.1 趋势曲线按使能切换

```vbscript
' 画面6加载时根据使能状态配置曲线
Dim unit, enabled
unit = SelectedUnit
enabled = GetValue("UnitEnabled_" & Format(unit, "00"))

If enabled = 0 Then
    !SetObjectProperty("TrendChart", "Visible", 0)
    !SetObjectProperty("lblTrendDisabled", "Visible", 1)
    !SetObjectProperty("lblTrendDisabled", "Caption", unit & "号单元未启用,无趋势数据")
Else
    !SetObjectProperty("TrendChart", "Visible", 1)
    !SetObjectProperty("lblTrendDisabled", "Visible", 0)
    ' 配置曲线变量(原有逻辑)
End If
```

---

## 七、画面7使能配置页(详见Story 2.3)

画面7是单元使能配置入口,详见Story 2.3实现文档。

---

## 八、画面8系统设置页动态显示

### 8.1 登录状态显示

```vbscript
' 画面8加载时显示登录状态
Dim levelText
Select Case LoginLevel
    Case 0: levelText = "未登录"
    Case 1: levelText = "L1 操作员"
    Case 2: levelText = "L2 维护"
    Case 3: levelText = "L3 管理员"
End Select

!SetObjectProperty("lblLoginStatus", "Caption", "当前权限:" & levelText)

' 根据权限显示/隐藏功能按钮
!SetObjectProperty("btnLogin", "Visible", IIf(LoginLevel = 0, 1, 0))
!SetObjectProperty("btnLogout", "Visible", IIf(LoginLevel > 0, 1, 0))
!SetObjectProperty("btnTimeSync", "Visible", IIf(LoginLevel = 3, 1, 0))
!SetObjectProperty("btnResetPwd", "Visible", IIf(LoginLevel = 3, 1, 0))
```

---

## 九、全局报警横幅动态显示

### 9.1 顶部报警横幅(全局)

```vbscript
' ============================================
' 全局报警横幅(每秒执行,主控窗口)
' 显示所有使能单元中最高级报警
' ============================================
Dim highestAlarm, highestUnit, highestCode
highestCode = 0
highestUnit = 0

' 遍历8个使能单元找最高级报警
Dim i
For i = 1 To 8
    Dim enabled, alarmCode
    enabled = GetValue("UnitEnabled_" & Format(i, "00"))
    alarmCode = GetValue("U" & i & "_VW6_AlarmCode")

    If enabled = 1 And alarmCode <> 0 Then
        ' 优先级: 99 > 10~14 > 20~21 > 30~66
        If highestCode = 0 Then
            highestCode = alarmCode
            highestUnit = i
        ElseIf alarmCode = 99 Then
            highestCode = alarmCode
            highestUnit = i
        ElseIf alarmCode < highestCode And highestCode <> 99 Then
            highestCode = alarmCode
            highestUnit = i
        End If
    End If
Next

' 更新横幅
If highestCode = 0 Then
    !SetObjectProperty("GlobalAlarmBanner", "Visible", 0)
Else
    !SetObjectProperty("GlobalAlarmBanner", "Visible", 1)
    Dim alarmText
    alarmText = "⚠️ " & highestUnit & "号单元报警: " & GetAlarmTextByCode(highestCode)
    !SetObjectProperty("GlobalAlarmBanner", "Caption", alarmText)

    ' 颜色
    Dim bgColor
    If highestCode = 99 Or (highestCode >= 10 And highestCode <= 14) Then
        bgColor = &H0000FF  ' 红
    Else
        bgColor = &H0080FF  ' 橙
    End If
    !SetObjectProperty("GlobalAlarmBanner", "BackColor", bgColor)
End If
```

### 9.2 辅助函数

```vbscript
' GetAlarmTextByCode: 报警码转中文
Function GetAlarmTextByCode(code)
    Select Case code
        Case 99: GetAlarmTextByCode = "安全继电器故障(最高级)"
        Case 10: GetAlarmTextByCode = "上缸漫溢"
        Case 11: GetAlarmTextByCode = "下缸漫溢"
        Case 12: GetAlarmTextByCode = "NC球阀-上缸动作"
        Case 13: GetAlarmTextByCode = "NC球阀-下缸动作"
        Case 14: GetAlarmTextByCode = "急停触发"
        Case 20: GetAlarmTextByCode = "配液节奏严重滞后"
        Case 21: GetAlarmTextByCode = "配液节奏滞后提示"
        Case 30 To 36: GetAlarmTextByCode = "阀A类故障(" & code & ")"
        Case 40 To 44: GetAlarmTextByCode = "阀B类故障(" & code & ")"
        Case 45 To 47: GetAlarmTextByCode = "阀C开类故障(" & code & ")"
        Case 60 To 61: GetAlarmTextByCode = "阀C关类故障(" & code & ")"
        Case 62 To 63: GetAlarmTextByCode = "潜水泵类故障(" & code & ")"
        Case 64: GetAlarmTextByCode = "注射泵故障"
        Case 65: GetAlarmTextByCode = "RTC时钟丢失"
        Case 66: GetAlarmTextByCode = "流量开关瞬时异常"
        Case Else: GetAlarmTextByCode = "未知报警(" & code & ")"
    End Select
End Function
```

---

## 十、动态显隐验证用例

### 10.1 使能切换验证

| 用例 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| EN-01 | 画面7关闭1号使能 | 画面1卡片1变灰,不可点击 | □ |
| EN-02 | 1号未使能,点击卡片1 | 弹窗"未启用" | □ |
| EN-03 | 1号未使能,访问画面2 | 弹窗拦截,返回画面1 | □ |
| EN-04 | 1号未使能,画面5报警列表 | 不显示1号报警 | □ |
| EN-05 | 1号未使能,画面6趋势 | 显示"未启用,无趋势数据" | □ |
| EN-06 | 画面7开启1号使能 | 画面1卡片1恢复正常色 | □ |

### 10.2 通讯中断验证

| 用例 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| COM-01 | 关闭1号PLC仿真器 | 画面1卡片1变黄 | □ |
| COM-02 | 1号通讯中断,点击卡片1 | 弹窗"通讯中断,是否进入?" | □ |
| COM-03 | 进入1号详情页 | 显示通讯中断横幅,数据"—" | □ |
| COM-04 | 1号详情页按钮 | 全部禁用 | □ |
| COM-05 | 1号通讯中断,画面3手动 | 所有手动按钮禁用 | □ |
| COM-06 | 重启1号PLC仿真器 | 卡片1变绿,数据恢复 | □ |

### 10.3 报警显示验证

| 用例 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| ALM-01 | 1号VW6=99 | 卡片1红色闪烁,顶部横幅红色 | □ |
| ALM-02 | 1号VW6=10 | 卡片1红色,顶部横幅红色 | □ |
| ALM-03 | 1号VW6=20 | 卡片1橙色,顶部横幅橙色 | □ |
| ALM-04 | 1号VW6=30 | 卡片1橙色,顶部横幅橙色 | □ |
| ALM-05 | 1号报警+2号报警 | 横幅显示最高优先级单元 | □ |
| ALM-06 | 1号未使能+有报警 | 横幅不显示1号报警 | □ |

### 10.4 多单元并发验证

| 用例 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| MULTI-01 | 8套全部使能+在线 | 8卡片全绿 | □ |
| MULTI-02 | 1~4使能,5~8未使能 | 1~4绿,5~8灰 | □ |
| MULTI-03 | 1号报警,其他正常 | 横幅显示1号,其他卡片不变色 | □ |
| MULTI-04 | 1号+2号同时报警 | 横幅显示最高级 | □ |
| MULTI-05 | 切换SelectedUnit 1~8 | 各画面数据正确切换 | □ |

---

## 十一、性能优化

### 11.1 脚本执行频率

| 脚本 | 频率 | 说明 |
|---|---|---|
| 卡片颜色刷新 | 每秒 | 8卡片×1次=8次属性设置 |
| 通讯状态检测 | 每秒 | 8连接状态查询 |
| 报警横幅刷新 | 每秒 | 8单元报警码读取 |
| 详情页通讯处理 | 每秒 | 仅当前选中单元 |
| 趋势曲线刷新 | 每5秒 | 历史数据查询 |

### 11.2 优化建议

1. **未选中单元不刷新详情页**: 仅SelectedUnit对应单元的详情页脚本执行
2. **未使能单元跳过数据读取**: 周期脚本中If enabled=0 Then Continue
3. **报警横幅仅在有报警时刷新**: 无报警时跳过颜色设置
4. **趋势曲线按需加载**: 仅画面6可见时刷新

---

## 十二、与Story 2.3的依赖关系

Story 2.2(本Story)实现了使能状态对画面显隐的影响,**Story 2.3**实现使能配置功能本身:
- Story 2.3: 在画面7提供使能切换UI+持久化存储
- Story 2.2: 读取UnitEnabled_XX变量,驱动画面显隐

两者协同工作,Story 2.3是配置入口,Story 2.2是显隐机制。

---

## 附录:动态显隐控件清单

| 画面 | 控件 | 显隐条件 | 属性 |
|---|---|---|---|
| 1 | UnitCard_01~08 | 使能 | Visible/BackColor/Enabled |
| 1 | UnitCard_Data_01~08 | 使能 | Visible |
| 1 | GlobalAlarmBanner | 有报警 | Visible/Caption/BackColor |
| 2 | CommErrorBanner | 通讯中断 | Visible/Caption |
| 2 | lbl_S1_Actual等 | 通讯正常 | Caption |
| 2 | btnStart/btnStop等 | 通讯正常+使能 | Enabled |
| 3 | 8手动按钮 | 通讯正常+使能+权限L2+ | Enabled |
| 4 | 参数输入框 | 使能+权限L2+ | Enabled |
| 5 | 报警列表 | 使能单元 | Caption |
| 6 | TrendChart | 使能 | Visible |
| 6 | lblTrendDisabled | 未使能 | Visible |
| 8 | btnLogin/btnLogout | 登录状态 | Visible |
| 8 | btnTimeSync/btnResetPwd | L3权限 | Visible |

---

**文档结束**

**待办**:
1. MCGS组态环境中实现控件Visible/Enabled属性绑定
2. 周期脚本执行频率按实际性能调整
3. 30个验证用例在MCGS仿真模式中执行
4. 闪烁逻辑(最高级报警)需测试视觉效果
