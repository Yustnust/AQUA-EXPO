# Story 2.3 单元使能配置功能 v1.0

**配套文档**：《HMI画面架构规划文档 v9.3》第十章、《Story 2.2 分期接入动态显隐机制 v1.0》、《MCGS组态脚本代码 v1.0》
**适用范围**：8套缸单元使能配置的UI/脚本/存储/联动机制
**Story**：AQEX-14 Story 2.3 单元使能配置功能

---

## 一、设计目标

### 1.1 业务需求

8套缸单元分期上线,运维人员需在HMI上配置:
- 哪些单元已物理安装并接入PLC(使能)
- 哪些单元暂未安装(未使能)
- 使能配置需**断电保持**(HMI重启后恢复)
- 使能变更需**联动画面显隐**(Story 2.2机制)
- 使能变更需**记录操作日志**(审计追踪)

### 1.2 功能边界

**本Story实现**:
- 画面7的8单元使能切换UI
- 使能状态持久化存储(MCGS内部变量断电保持)
- 使能变更联动画面显隐(通过UnitEnabled_XX变量)
- 使能变更操作日志(记录时间/用户/操作)
- L3管理员权限限制

**不在本Story范围**:
- 单元使能后自动启停PLC(由运维人员现场操作)
- 单元使能的远程管理(本HMI仅本地配置)
- 单元使能与PLC程序的联动(PLC程序不区分使能,统一运行)

### 1.3 与Story 2.2的关系

| Story | 职责 | 接口 |
|---|---|---|
| Story 2.2 | 读取UnitEnabled_XX,驱动画面显隐 | 只读 |
| Story 2.3 | 配置UnitEnabled_XX,持久化存储 | 读写 |

---

## 二、画面7使能配置UI设计

### 2.1 画面布局

```
┌──────────────────────────────────────────────────────────────┐
│ [总览][详情][手动][参数][报警][趋势][通讯][设置]   L3管理员 │  ← 顶部导航80px
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  单元使能配置                                       │    │
│  │  ┌────────────────────────────────────────────┐    │    │
│  │  │ 1号单元  IP:192.168.2.101  [✓使能] 在线    │    │    │
│  │  ├────────────────────────────────────────────┤    │    │
│  │  │ 2号单元  IP:192.168.2.102  [✓使能] 在线    │    │    │
│  │  ├────────────────────────────────────────────┤    │    │
│  │  │ 3号单元  IP:192.168.2.103  [✓使能] 离线    │    │    │
│  │  ├────────────────────────────────────────────┤    │    │
│  │  │ 4号单元  IP:192.168.2.104  [✓使能] 在线    │    │    │
│  │  ├────────────────────────────────────────────┤    │    │
│  │  │ 5号单元  IP:192.168.2.105  [□未使能] —     │    │    │
│  │  ├────────────────────────────────────────────┤    │    │
│  │  │ 6号单元  IP:192.168.2.106  [□未使能] —     │    │    │
│  │  ├────────────────────────────────────────────┤    │    │
│  │  │ 7号单元  IP:192.168.2.107  [□未使能] —     │    │    │
│  │  ├────────────────────────────────────────────┤    │    │
│  │  │ 8号单元  IP:192.168.2.108  [□未使能] —     │    │    │
│  │  └────────────────────────────────────────────┘    │    │
│  │                                                     │    │
│  │  [保存配置]  [恢复默认(全使能)]  [刷新状态]        │    │
│  │                                                     │    │
│  │  操作日志:                                          │    │
│  │  ┌────────────────────────────────────────────┐    │    │
│  │  │ 2025-XX-XX 14:30:15 L3admin 关闭5号使能     │    │    │
│  │  │ 2025-XX-XX 14:28:10 L3admin 开启4号使能     │    │    │
│  │  └────────────────────────────────────────────┘    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ 通讯:1✓ 2✓ 3✗ 4✓ 5— 6— 7— 8—  | 报警:1号 漫溢  | 14:35:25 │  ← 底部状态栏60px
└──────────────────────────────────────────────────────────────┘
```

### 2.2 控件清单

| 控件类型 | 名称 | 位置(x,y,w,h) | 属性 | 说明 |
|---|---|---|---|---|
| Label | lblTitle | (20,90,400,30) | 字号16粗体 | "单元使能配置" |
| Label | lblUnit_01~08 | (40,Y,60,25) | 字号12 | "1号单元"~"8号单元" |
| Label | lblIP_01~08 | (110,Y,140,25) | 字号12 | "IP:192.168.2.10X" |
| CheckBox | chkEnable_01~08 | (260,Y,80,25) | 字号12 | "使能"/"未使能" |
| Label | lblComm_01~08 | (350,Y,60,25) | 字号12 | "在线"/"离线"/"—" |
| Button | btnSave | (40,520,100,35) | 字号12 | "保存配置" |
| Button | btnDefault | (160,520,140,35) | 字号12 | "恢复默认(全使能)" |
| Button | btnRefresh | (320,520,100,35) | 字号12 | "刷新状态" |
| TextBox | txtLog | (40,570,760,150) | 多行只读 | 操作日志显示 |

Y坐标公式: 130 + (i-1)×40 (i=1~8)

---

## 三、使能配置脚本

### 3.1 画面加载脚本(OnLoad)

```vbscript
' ============================================
' 画面7加载: 权限检查+加载使能状态到CheckBox
' ============================================
' 权限检查: 需L3管理员
If LoginLevel < 3 Then
    !MsgBox("权限不足!单元使能配置需管理员(L3)权限", 0, "权限提示")
    !SwitchWindow("画面1_总览")
    Exit Sub
End If

LoginTime = CStr(Now())

' 加载使能状态到CheckBox
Dim i
For i = 1 To 8
    Dim enabled, chkName
    enabled = GetValue("UnitEnabled_" & Format(i, "00"))
    chkName = "chkEnable_" & Format(i, "00")
    !SetObjectProperty(chkName, "Value", enabled)
Next

' 加载操作日志
Call LoadOperationLog()
```

### 3.2 保存配置按钮(OnClick)

```vbscript
' ============================================
' 保存配置(二次确认+写入变量+持久化+日志)
' ============================================
Dim result
result = !MsgBox("确认保存使能配置?配置将断电保持,影响画面显示。", 1, "保存确认")
If result <> 1 Then Exit Sub

' 收集变更项
Dim changes, i
changes = ""
For i = 1 To 8
    Dim chkName, oldVal, newVal
    chkName = "chkEnable_" & Format(i, "00")
    oldVal = GetValue("UnitEnabled_" & Format(i, "00"))
    newVal = !GetObjectProperty(chkName, "Value")

    If oldVal <> newVal Then
        ' 写入变量(MCGS内部变量已配置断电保持)
        Execute("UnitEnabled_" & Format(i, "00") & " = " & newVal)

        ' 记录变更
        Dim opText
        If newVal = 1 Then
            opText = "开启" & i & "号使能"
        Else
            opText = "关闭" & i & "号使能"
        End If
        changes = changes & Now() & " " & GetUserText() & " " & opText & Chr(13) & Chr(10)
    End If
Next

If changes = "" Then
    !MsgBox("无变更,无需保存", 0, "提示")
Else
    ' 写入操作日志文件
    Call AppendOperationLog(changes)
    !MsgBox("配置已保存,变更项:" & Chr(13) & changes, 0, "保存成功")
End If

LoginTime = CStr(Now())
```

### 3.3 恢复默认按钮(OnClick)

```vbscript
' ============================================
' 恢复默认(全使能) - 二次确认
' ============================================
Dim result
result = !MsgBox("确认恢复默认配置(8套全部使能)?此操作不可撤销!", 1, "恢复默认")
If result <> 1 Then Exit Sub

' 二次确认(危险操作)
result = !MsgBox("再次确认:8套全部使能将显示所有单元,确定?", 1, "二次确认")
If result <> 1 Then Exit Sub

Dim i
For i = 1 To 8
    Execute("UnitEnabled_" & Format(i, "00") & " = 1")
    Dim chkName
    chkName = "chkEnable_" & Format(i, "00")
    !SetObjectProperty(chkName, "Value", 1)
Next

' 记录日志
Dim logEntry
logEntry = Now() & " " & GetUserText() & " 恢复默认(全使能)" & Chr(13) & Chr(10)
Call AppendOperationLog(logEntry)

!MsgBox("已恢复默认配置", 0, "完成")
LoginTime = CStr(Now())
```

### 3.4 刷新状态按钮(OnClick)

```vbscript
' ============================================
' 刷新通讯状态显示
' ============================================
Dim i
For i = 1 To 8
    Dim enabled, comm, lblName, commText
    enabled = GetValue("UnitEnabled_" & Format(i, "00"))
    comm = GetValue("CommStatus_" & Format(i, "00"))
    lblName = "lblComm_" & Format(i, "00")

    If enabled = 0 Then
        commText = "—"
    ElseIf comm = 1 Then
        commText = "在线"
    Else
        commText = "离线"
    End If

    !SetObjectProperty(lblName, "Caption", commText)
Next

LoginTime = CStr(Now())
```

### 3.5 CheckBox变更即时提示(OnChangeEvent)

每个CheckBox变更时,提示"需点击保存才生效":

```vbscript
' chkEnable_01 OnChange
Dim oldVal, newVal
oldVal = UnitEnabled_01
newVal = !GetObjectProperty("chkEnable_01", "Value")

If oldVal <> newVal Then
    !SetObjectProperty("lblPendingSave", "Visible", 1)
    !SetObjectProperty("lblPendingSave", "Caption", "⚠ 有未保存的变更,请点击[保存配置]")
End If
```

---

## 四、使能状态持久化机制

### 4.1 MCGS内部变量断电保持配置

UnitEnabled_01~08共8个变量,在MCGS组态中配置为**断电保持**:

**MCGS配置路径**: 实时数据库→UnitEnabled_01→属性→断电保持=是

| 变量名 | 类型 | 断电保持 | 初始值 | 说明 |
|---|---|---|---|---|
| UnitEnabled_01 | Bool | 是 | 1 | 1号单元使能 |
| UnitEnabled_02 | Bool | 是 | 1 | 2号单元使能 |
| ... | ... | ... | ... | ... |
| UnitEnabled_08 | Bool | 是 | 1 | 8号单元使能 |

### 4.2 持久化验证

**验证方法**:
1. 配置UnitEnabled_05=0(关闭5号)
2. 点击保存
3. 关闭MCGS运行环境
4. 重新启动MCGS
5. 检查UnitEnabled_05应为0(保持)

### 4.3 备份与恢复

**配置备份**:
- MCGS工程文件(.mcgs)本身包含变量配置
- 建议定期备份.mcg文件到外部存储

**配置恢复**:
- 恢复.mcg文件即可恢复使能配置
- 或在画面7手动重新配置

---

## 五、操作日志机制

### 5.1 日志存储

**存储位置**: MCGS工程目录下 `EnableConfig.log`

**日志格式**: 纯文本,每行一条记录
```
2025-XX-XX 14:30:15 L3admin 关闭5号使能
2025-XX-XX 14:28:10 L3admin 开启4号使能
2025-XX-XX 14:25:00 L3admin 恢复默认(全使能)
```

### 5.2 日志写入脚本

```vbscript
' ============================================
' AppendOperationLog: 追加操作日志
' 入参: logText - 要追加的日志文本(可多行)
' ============================================
Sub AppendOperationLog(logText)
    Dim logFile
    logFile = !GetProjectPath() & "\EnableConfig.log"

    ' 追加写入(MCGS提供!FileAppend函数)
    !FileAppend(logFile, logText)

    ' 刷新画面显示
    Call LoadOperationLog()
End Sub

' ============================================
' LoadOperationLog: 加载日志到文本框
' ============================================
Sub LoadOperationLog()
    Dim logFile, content
    logFile = !GetProjectPath() & "\EnableConfig.log"

    ' 读取最后50行(避免日志过大卡顿)
    content = !FileReadTail(logFile, 50)

    !SetObjectProperty("txtLog", "Text", content)
End Sub
```

### 5.3 日志轮转

当日志文件>1MB时,自动轮转:

```vbscript
' 检查日志大小,超过1MB则轮转
Dim logFile, fileSize
logFile = !GetProjectPath() & "\EnableConfig.log"
fileSize = !GetFileSize(logFile)

If fileSize > 1048576 Then  ' 1MB
    ' 重命名为带日期的备份
    Dim backupName
    backupName = !GetProjectPath() & "\EnableConfig_" & Format(Now(), "yyyymmdd") & ".log"
    !FileRename(logFile, backupName)
    ' 新建空日志文件
    !FileWrite(logFile, "")
End If
```

---

## 六、联动机制(与Story 2.2)

### 6.1 使能变更的联动流程

```
画面7保存配置
  ↓
写入UnitEnabled_XX变量
  ↓ (MCGS变量变化触发)
画面1周期脚本检测变化
  ↓
卡片Visible/BackColor/Enabled更新
  ↓
画面2/3/5/6显隐状态更新
  ↓
全局报警横幅过滤更新
```

### 6.2 实时联动验证

**测试用例**:
1. 画面7关闭5号使能,保存
2. 立即切换到画面1
3. 验证卡片5变灰,不可点击
4. 切换到画面5报警页
5. 验证5号报警不显示
6. 切换到画面6趋势页
7. 验证5号趋势显示"未启用"

**预期**: 使能变更后,所有画面在下一个1秒周期脚本执行时同步更新。

### 6.3 与通讯状态的协同

| 使能 | 通讯 | 画面1卡片 | 画面2详情 | 画面5报警 |
|---|---|---|---|---|
| 0 | — | 灰色不可点 | 拦截进入 | 不显示 |
| 1→0(刚关闭) | 1 | 立即变灰 | 拦截进入 | 立即移除 |
| 0→1(刚开启) | 1 | 立即变绿 | 允许进入 | 显示报警(如有) |
| 0→1(刚开启) | 0 | 立即变黄 | 允许进入(提示) | 显示"通讯中断" |

---

## 七、安全机制

### 7.1 权限控制

| 操作 | 所需权限 | 说明 |
|---|---|---|
| 进入画面7 | L3管理员 | 画面加载即检查 |
| 修改CheckBox | L3管理员 | CheckBox Enabled=False until L3 |
| 保存配置 | L3管理员 | 保存按钮Enabled=False until L3 |
| 恢复默认 | L3管理员+二次确认 | 危险操作双重确认 |
| 刷新状态 | L3管理员 | 仅读取,无修改 |
| 查看日志 | L3管理员 | 日志文本框只读 |

### 7.2 操作拦截

```vbscript
' 画面加载时,根据权限设置CheckBox Enabled
Dim canEdit
canEdit = IIf(LoginLevel >= 3, 1, 0)

Dim i
For i = 1 To 8
    Dim chkName
    chkName = "chkEnable_" & Format(i, "00")
    !SetObjectProperty(chkName, "Enabled", canEdit)
Next

!SetObjectProperty("btnSave", "Enabled", canEdit)
!SetObjectProperty("btnDefault", "Enabled", canEdit)
!SetObjectProperty("btnRefresh", "Enabled", 1)  ' 刷新始终允许
```

### 7.3 防误操作

1. **二次确认**: 保存/恢复默认均需二次确认
2. **变更提示**: CheckBox变更即显示"未保存"提示
3. **日志审计**: 所有变更记录日志,可追溯
4. **权限超时**: L3登录15分钟无操作自动注销

---

## 八、辅助函数

### 8.1 GetUserText函数

```vbscript
' GetUserText: 获取当前用户文本
Function GetUserText()
    Select Case LoginLevel
        Case 1: GetUserText = "L1operator"
        Case 2: GetUserText = "L2maintenance"
        Case 3: GetUserText = "L3admin"
        Case Else: GetUserText = "Unknown"
    End Select
End Function
```

### 8.2 GetUnitIP函数

```vbscript
' GetUnitIP: 根据单元号返回IP
Function GetUnitIP(unit)
    GetUnitIP = "192.168.2." & (100 + unit)
End Function
```

---

## 九、验证用例

### 9.1 功能验证

| 用例 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| EN-01 | L2登录,进入画面7 | 拦截"权限不足",返回画面1 | □ |
| EN-02 | L3登录,进入画面7 | CheckBox可编辑 | □ |
| EN-03 | 关闭5号CheckBox | 显示"未保存"提示 | □ |
| EN-04 | 点击保存 | 弹窗确认→保存→日志记录 | □ |
| EN-05 | 切换画面1 | 5号卡片变灰 | □ |
| EN-06 | 切换回画面7 | 5号CheckBox保持关闭 | □ |
| EN-07 | 点击恢复默认 | 二次确认→8套全使能 | □ |
| EN-08 | 点击刷新状态 | 通讯状态列更新 | □ |
| EN-09 | 关闭MCGS重启 | 使能配置保持 | □ |
| EN-10 | 查看操作日志 | 显示历史变更 | □ |

### 9.2 联动验证

| 用例 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| LN-01 | 关闭5号使能→画面1 | 5号卡片变灰 | □ |
| LN-02 | 关闭5号使能→画面2 | 5号拦截进入 | □ |
| LN-03 | 关闭5号使能→画面3 | 5号拦截手动 | □ |
| LN-04 | 关闭5号使能→画面5 | 5号报警不显示 | □ |
| LN-05 | 关闭5号使能→画面6 | 5号趋势隐藏 | □ |
| LN-06 | 关闭5号使能→报警横幅 | 5号报警过滤 | □ |
| LN-07 | 开启5号使能→画面1 | 5号卡片恢复 | □ |
| LN-08 | 开启5号使能→画面2 | 5号允许进入 | □ |

### 9.3 安全验证

| 用例 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| SEC-01 | 未登录进入画面7 | 拦截 | □ |
| SEC-02 | L1进入画面7 | 拦截 | □ |
| SEC-03 | L2进入画面7 | 拦截 | □ |
| SEC-04 | L3进入画面7 | 允许 | □ |
| SEC-05 | L3登录15分钟无操作 | 自动注销 | □ |
| SEC-06 | 注销后停留在画面7 | 下一周期脚本拦截 | □ |
| SEC-07 | 修改CheckBox不保存 | 切换画面后变更丢失 | □ |
| SEC-08 | 恢复默认二次确认取消 | 不执行恢复 | □ |

### 9.4 持久化验证

| 用例 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| PER-01 | 配置5号=0,保存,重启MCGS | 5号保持=0 | □ |
| PER-02 | 配置全使能,保存,重启 | 全部=1 | □ |
| PER-03 | 配置1~4使能,重启 | 1~4=1,5~8=0 | □ |
| PER-04 | 日志文件跨重启保留 | 历史日志可查 | □ |
| PER-05 | 日志>1MB自动轮转 | 生成备份文件 | □ |

---

## 十、初始使能配置建议

### 10.1 首期上线(1~4号)

**建议配置**:
- UnitEnabled_01~04 = 1 (使能)
- UnitEnabled_05~08 = 0 (未使能)

**操作**:
1. L3登录画面8
2. 进入画面7
3. 关闭5~8号CheckBox
4. 点击保存
5. 验证画面1仅显示1~4号绿色卡片,5~8号灰色

### 10.2 二期上线(5~8号)

**操作**:
1. 5~8号硬件安装完成
2. L3登录画面8
3. 进入画面7
4. 开启5~8号CheckBox
5. 点击保存
6. 验证画面1显示8个绿色卡片(通讯正常后)

### 10.3 维护场景

**单台维护**(如3号故障):
1. L3登录,进入画面7
2. 关闭3号使能
3. 保存
4. 3号卡片变灰,不影响其他单元
5. 维护完成后重新开启

---

## 附录A:变量清单

| 变量名 | 类型 | 断电保持 | 初始值 | 说明 |
|---|---|---|---|---|
| UnitEnabled_01~08 | Bool | 是 | 1 | 8单元使能标志 |
| LoginLevel | Int | 否 | 0 | 当前登录权限 |
| LoginTime | String | 否 | "" | 登录时间 |
| SelectedUnit | Int | 否 | 1 | 当前选中单元 |

---

## 附录B:操作日志格式规范

### 日志条目格式

```
YYYY-MM-DD HH:MM:SS <用户> <操作>
```

### 操作类型

| 操作文本 | 说明 |
|---|---|
| 开启X号使能 | 单元使能从0→1 |
| 关闭X号使能 | 单元使能从1→0 |
| 恢复默认(全使能) | 8套全部使能 |
| 批量变更(X项) | 一次保存多个变更 |

### 日志示例

```
2025-11-15 14:25:00 L3admin 开启4号使能
2025-11-15 14:25:00 L3admin 关闭5号使能
2025-11-15 14:25:00 L3admin 关闭6号使能
2025-11-15 14:25:00 L3admin 关闭7号使能
2025-11-15 14:25:00 L3admin 关闭8号使能
2025-11-15 14:28:10 L3admin 恢复默认(全使能)
2025-11-15 14:30:15 L3admin 关闭5号使能
```

---

## 附录C:与PLC程序的边界

**重要说明**: PLC程序不区分单元使能,8套PLC程序完全相同,各自独立运行。

HMI的"使能配置"仅影响:
- HMI画面的显示与隐藏
- HMI对PLC变量的读写(未使能单元不读)
- HMI报警的显示过滤

**不影响**:
- PLC程序的运行(PLC始终按程序运行)
- PLC的通讯(PLC始终响应HMI请求)
- PLC的报警生成(PLC始终生成报警)

**实际效果**:
- 未使能单元的PLC仍在运行,但HMI不显示其数据
- 若需完全停止未安装的PLC,需现场断电(物理操作)

---

**文档结束**

**待办**:
1. MCGS组态环境中实现CheckBox/Button控件+脚本绑定
2. !FileAppend/!FileReadTail等文件操作函数需按MCGS实际版本确认
3. 日志轮转机制需测试实际效果
4. 26个验证用例在MCGS仿真模式中执行
