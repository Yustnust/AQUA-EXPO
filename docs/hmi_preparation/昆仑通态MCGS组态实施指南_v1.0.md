# 药液配置加注控制系统 — 昆仑通态MCGS组态实施指南 v1.0

**项目**: 药液配置加注控制系统
**适用HMI**: 昆仑通态MCGS 12寸触摸屏(初步选型,具体型号待二轮确认)
**用途**: 将"选型无关"的HMI准备材料升级为"昆仑通态MCGS具体"的组态实施指南,组态工程师按此可直接上手
**配套文档**: HMI画面布局线框图v1.0、画面变量绑定清单v1.0、HMI变量导入CSV模板、HMI用户权限矩阵v1.0、报警字32位解析映射表
**前提假设**: 供应商二轮确认S7协议可用(若改Modbus TCP见附录B)

---

## 一、McgsPro工程创建

### 1.1 软件准备

| 项 | 说明 |
|---|---|
| 组态软件 | McgsPro(昆仑通态官方,免费) |
| 下载 | http://www.mcgs.com.cn/ |
| 安装环境 | Windows 7/10 PC |
| 工程文件扩展名 | .mcp |

### 1.2 新建工程

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | 文件→新建工程 | □ |
| 2 | 触摸屏型号选择(待二轮确认具体型号) | □ |
| 3 | 工程名称: AQUA-EXPO_HMI | □ |
| 4 | 保存路径: 项目/HMI工程/ | □ |

---

## 二、8连接S7驱动配置(关键)

### 2.1 添加S7-200 SMART驱动

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | 设备窗口→设备工具箱→添加设备 | □ |
| 2 | 选择"西门子S7-200 SMART TCP/IP"驱动 | □ |
| 3 | 添加8个设备实例: PLC_1~PLC_8 | □ |

### 2.2 8台PLC连接配置

| 设备名 | IP地址 | 机架号 | 槽号 | 站名 | 确认 |
|---|---|---|---|---|---|
| PLC_1 | 192.168.2.101 | 0 | 1 | 1号单元 | □ |
| PLC_2 | 192.168.2.102 | 0 | 1 | 2号单元 | □ |
| PLC_3 | 192.168.2.103 | 0 | 1 | 3号单元 | □ |
| PLC_4 | 192.168.2.104 | 0 | 1 | 4号单元 | □ |
| PLC_5 | 192.168.2.105 | 0 | 1 | 5号单元 | □ |
| PLC_6 | 192.168.2.106 | 0 | 1 | 6号单元 | □ |
| PLC_7 | 192.168.2.107 | 0 | 1 | 7号单元 | □ |
| PLC_8 | 192.168.2.108 | 0 | 1 | 8号单元 | □ |

### 2.3 通讯参数

| 参数 | 值 | 确认 |
|---|---|---|
| 协议 | TCP/IP | □ |
| 端口 | 102(S7标准) | □ |
| 连接数 | 8(待供应商确认上限) | □ |
| 超时 | 3000ms | □ |
| 重试 | 3次 | □ |

---

## 三、变量导入(适配McgsPro)

### 3.1 变量命名规范(8单元前缀)

McgsPro变量按"单元号_变量符号"命名,便于脚本动态寻址:

| 单元 | 前缀 | 示例 |
|---|---|---|
| 1号 | U1_ | U1_VW2(1号单元状态机) |
| 2号 | U2_ | U2_VW2(2号单元状态机) |
| ... | ... | ... |
| 8号 | U8_ | U8_VW2(8号单元状态机) |

### 3.2 变量导入步骤

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | 实时数据库→批量导入 | □ |
| 2 | 选择CSV模板(适配McgsPro格式,见3.3) | □ |
| 3 | 导入8×91=728个变量 | □ |
| 4 | 验证变量连接(每个变量绑定到对应PLC设备) | □ |

### 3.3 McgsPro CSV模板格式(适配现有CSV模板)

现有CSV模板7字段需映射为McgsPro格式:

| 现有模板字段 | McgsPro字段 | 示例 |
|---|---|---|
| 变量名 | 名称 | U1_VW2 |
| 地址 | PLC地址(设备.寄存器) | PLC_1.VW2 |
| 数据类型 | 类型 | INT |
| 读写 | 读写属性 | 读写 |
| 单元 | (并入名称前缀) | U1 |
| 描述 | 备注 | 状态机当前状态 |
| 范围 | (McgsPro无此字段,用报警限值实现) | — |

**McgsPro CSV格式示例**:
```
名称,PLC地址,类型,读写属性,备注
U1_VW2,PLC_1.VW2,INT,读写,状态机当前状态
U1_VW6,PLC_1.VW6,INT,读写,当前报警码
U1_VD10,PLC_1.VD10,REAL,读写,目标浓度设定值
...
U8_VW2,PLC_8.VW2,INT,读写,状态机当前状态
```

### 3.4 变量点数确认

| 项 | 数量 | 确认 |
|---|---|---|
| 每单元变量数 | 91 | □ |
| 8单元总变量数 | 728 | □ |
| McgsPro变量点数上限 | (待供应商确认) | □ |

---

## 四、8画面组态映射

按《HMI画面布局线框图v1.0》在McgsPro中创建8个画面,控件绑定按《画面变量绑定清单v1.0》。

### 4.1 画面创建顺序(按价值)

| 顺序 | 画面名 | McgsPro画面ID | 优先级 | 确认 |
|---|---|---|---|---|
| 1 | 单元详情 | page_detail | 高 | □ |
| 2 | 报警与日志 | page_alarm | 高 | □ |
| 3 | 总览首页 | page_overview | 高 | □ |
| 4 | 参数设置 | page_param | 中 | □ |
| 5 | 系统设置 | page_system | 中 | □ |
| 6 | 手动控制 | page_manual | 中 | □ |
| 7 | 趋势曲线 | page_trend | 低 | □ |
| 8 | 通讯维护 | page_comm | 低 | □ |

### 4.2 单元选择器实现(画面2~7共用)

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | 画面顶部放置8个按钮(1~8号单元) | □ |
| 2 | 每按钮点击脚本: 设置全局变量GW_SelectedUnit=1~8 | □ |
| 3 | 当前选中按钮高亮(用GW_SelectedUnit判断) | □ |
| 4 | 画面所有控件绑定变量按GW_SelectedUnit动态切换(见4.3) | □ |

### 4.3 动态变量切换脚本(VBScript)

**关键**: 8单元共用1个画面,通过脚本动态切换绑定变量

```vbscript
' 画面加载时执行: 根据GW_SelectedUnit切换所有控件绑定
Sub OnLoad()
    Dim unit, prefix
    unit = GetVar("GW_SelectedUnit")
    prefix = "U" & unit & "_"
    
    ' 状态显示控件
    SetCtrlBind("txt_Status", prefix & "VW2")
    SetCtrlBind("txt_AlarmCode", prefix & "VW6")
    SetCtrlBind("txt_TankA", prefix & "V1.6")
    SetCtrlBind("txt_TankB", prefix & "V1.7")
    SetCtrlBind("txt_Round", prefix & "VW8")
    SetCtrlBind("txt_Duration", prefix & "VD96")
    
    ' 实时数据控件
    SetCtrlBind("txt_InletVol", prefix & "VD90")
    SetCtrlBind("txt_FlowRate", prefix & "VD94")
    SetCtrlBind("txt_S1Actual", prefix & "VD70")
    SetCtrlBind("txt_S4Actual", prefix & "VD74")
    SetCtrlBind("txt_S6Actual", prefix & "VD78")
    
    ' 命令按钮(写入对应单元)
    SetCtrlBind("btn_Start", prefix & "V0.0")
    SetCtrlBind("btn_Stop", prefix & "V0.2")
    SetCtrlBind("btn_Ack", prefix & "V0.3")
    SetCtrlBind("btn_Mute", prefix & "V0.4")
End Sub
```

**注**: `SetCtrlBind`为McgsPro控件绑定函数,实际函数名以McgsPro文档为准(待二轮确认脚本能力)。

---

## 五、32位报警配置

### 5.1 报警位定义导入

按《报警字32位解析映射表》在McgsPro报警配置中添加32个报警:

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | 报警配置→报警数据源 | □ |
| 2 | 添加8组报警(每组32位,对应8单元) | □ |
| 3 | 每组报警源: U{N}_VW300~VW303(32位) | □ |
| 4 | 配置每位报警的文本/级别/处置建议 | □ |

### 5.2 报警级别配置

| 级别 | 报警码 | 颜色 | 声音 | 确认方式 |
|---|---|---|---|---|
| 最高级 | 99 | 红闪 | 急促 | 密码+长按 |
| 漫溢级 | 10~14 | 红 | 持续 | 弹窗确认 |
| 节奏级 | 20 | 橙 | 间歇 | 弹窗确认 |
| 一般级 | 21,30~66 | 黄 | 单次 | 点击确认 |

### 5.3 报警二次确认弹窗实现

**最高级报警(99)二次确认脚本**:

```vbscript
' 继电器故障确认按钮点击
Sub btn_SafetyRelayAck_Click()
    Dim ret
    ret = InputBox("请输入管理员密码:", "继电器故障高权限确认")
    If ret = "admin_password" Then
        ' 二次确认
        If MsgBox("确认清除继电器故障报警?", vbYesNo) = vbYes Then
            SetVar "U" & GetVar("GW_SelectedUnit") & "_V0.7", 1
        End If
    Else
        MsgBox "密码错误", vbExclamation
    End If
End Sub
```

---

## 六、趋势曲线配置

### 6.1 趋势对象添加

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | 画面7添加"趋势曲线"控件 | □ |
| 2 | 添加7条曲线(对应7个变量) | □ |
| 3 | 采样间隔: 60秒(1分钟) | □ |
| 4 | 存储策略: 循环覆盖 | □ |

### 6.2 曲线绑定(动态切换单元)

```vbscript
' 趋势画面加载时切换单元
Sub OnLoad()
    Dim unit, prefix
    unit = GetVar("GW_SelectedUnit")
    prefix = "U" & unit & "_"
    
    Trend.SetCurve 1, prefix & "VD96", "实验时长", RGB(52,152,219)
    Trend.SetCurve 2, prefix & "VD112", "T滚动", RGB(39,174,96)
    Trend.SetCurve 3, prefix & "VD116", "S6滚动", RGB(243,156,18)
    Trend.SetCurve 4, prefix & "VD70", "S1实测", RGB(230,126,34)
    Trend.SetCurve 5, prefix & "VD74", "S4实测", RGB(155,89,182)
    Trend.SetCurve 6, prefix & "VD78", "S6实测", RGB(231,76,60)
    Trend.SetCurve 7, prefix & "VD90", "进水量", RGB(26,188,156)
End Sub
```

### 6.3 存储容量配置

| 项 | 配置 | 确认 |
|---|---|---|
| 历史数据存储 | 启用 | □ |
| 存储路径 | \HardDisk\History\ | □ |
| 存储格式 | MCGS默认(待确认压缩) | □ |
| 循环覆盖 | 启用 | □ |
| 预估容量 | 241MB/年(见数据量测算) | □ |

---

## 七、3级用户权限配置

### 7.1 用户组创建

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | 用户管理→添加用户组 | □ |
| 2 | 创建3个组: 操作员/维护/管理员 | □ |
| 3 | 每组配置密码策略 | □ |

### 7.2 权限分配(对应权限矩阵)

| 用户组 | 可见画面 | 可操作控件 | 确认 |
|---|---|---|---|
| 操作员(L1) | 1/2/5/6/8(仅登录) | 启停/消音/确认 | □ |
| 维护(L2) | 全部(3/4/7可见) | +手动/时间参数 | □ |
| 管理员(L3) | 全部 | +浓度参数/单元使能/RTC/继电器确认 | □ |

### 7.3 控件权限绑定

每个写入类控件设置"操作权限等级":
- L1控件: 等级1
- L2控件: 等级2(手动/时间参数)
- L3控件: 等级3(浓度/单元使能/RTC/继电器确认)

### 7.4 超时自动注销脚本

```vbscript
' 全局循环脚本: 15分钟无操作降级
Dim lastOpTime
Sub OnCycle()
    If GetUserLevel() > 1 Then  ' L2/L3
        If DateDiff("n", lastOpTime, Now) > 15 Then
            Logout()
            MsgBox "权限已超时降级为操作员", vbInformation
        End If
    End If
End Sub

' 任意操作触发时更新
Sub OnOperation()
    lastOpTime = Now
End Sub
```

---

## 八、动态显隐(单元使能)

### 8.1 总览画面8卡片显隐

```vbscript
' 总览画面加载时根据单元使能状态显隐卡片
Sub OnLoad()
    Dim i
    For i = 1 To 8
        Dim enabled, online
        enabled = GetVar("U" & i & "_UnitEnabled")  ' 单元使能标志(HMI本地)
        online = GetVar("U" & i & "_CommOnline")     ' 通讯在线状态
        
        If enabled = 1 And online = 1 Then
            SetCtrlVisible("card_Unit" & i, True)   ' 显示彩色卡片
        ElseIf enabled = 1 And online = 0 Then
            SetCtrlVisible("card_Unit" & i, True)   ' 显示黄色通讯中断
        Else
            SetCtrlVisible("card_Unit" & i, True)   ' 显示灰色未使能
        End If
    Next
End Sub
```

**注**: 单元使能标志为HMI本地变量(非PLC),存储在HMI配方中。

---

## 九、RTC同步脚本

```vbscript
' 系统设置画面"RTC校时"按钮
Sub btn_RTCSync_Click()
    If GetUserLevel() < 3 Then
        MsgBox "需管理员权限", vbExclamation
        Exit Sub
    End If
    
    If MsgBox("将HMI时间同步至所有使能单元PLC,确认?", vbYesNo) = vbYes Then
        Dim i, hmiTime
        hmiTime = Now
        For i = 1 To 8
            If GetVar("U" & i & "_UnitEnabled") = 1 Then
                ' 写RTC校时寄存器(S7-200 SMART用SET_RTC)
                ' 需PLC侧配合: 监听某V区标志触发SET_RTC
                SetVar "U" & i & "_V_RTC_Year", Year(hmiTime) - 2000
                SetVar "U" & i & "_V_RTC_Month", Month(hmiTime)
                SetVar "U" & i & "_V_RTC_Day", Day(hmiTime)
                SetVar "U" & i & "_V_RTC_Hour", Hour(hmiTime)
                SetVar "U" & i & "_V_RTC_Minute", Minute(hmiTime)
                SetVar "U" & i & "_V_RTC_Second", Second(hmiTime)
                SetVar "U" & i & "_V_RTC_Trigger", 1  ' 触发PLC侧SET_RTC
            End If
        Next
        MsgBox "RTC同步完成", vbInformation
    End If
End Sub
```

**注**: PLC侧需在FC0或OB1中增加RTC校时逻辑:监听V_RTC_Trigger上升沿→SET_RTC VB_RTC。

---

## 十、U盘导出配置

### 10.1 导出按钮脚本

```vbscript
Sub btn_Export_Click()
    Dim path, startDate, endDate
    path = "\UDisk\Export_" & FormatDateTime(Now, 2) & ".csv"
    startDate = InputBox("起始日期(YYYY-MM-DD):", "导出", DateAdd("m", -1, Date))
    endDate = InputBox("结束日期(YYYY-MM-DD):", "导出", Date)
    
    ' 调用MCGS历史数据导出函数
    ExportHistoryData path, startDate, endDate, "ALL"
    MsgBox "导出完成: " & path, vbInformation
End Sub
```

### 10.2 定时自动导出

| 项 | 配置 | 确认 |
|---|---|---|
| 启用定时导出 | 是 | □ |
| 导出周期 | 每月1日00:00 | □ |
| 导出路径 | \UDisk\Auto\ | □ |
| 导出范围 | 上月全部数据 | □ |

---

## 十一、组态验收checklist

| # | 验收项 | 确认 |
|---|---|---|
| 1 | 8连接S7驱动通讯正常 | □ |
| 2 | 728变量全部导入并绑定 | □ |
| 3 | 8画面按线框图布局完成 | □ |
| 4 | 单元选择器切换正常 | □ |
| 5 | 32位报警指示灯阵列正确 | □ |
| 6 | 报警二次确认弹窗工作 | □ |
| 7 | 7条趋势曲线显示正常 | □ |
| 8 | 3级权限登录/注销正常 | □ |
| 9 | 超时自动注销15分钟生效 | □ |
| 10 | 单元使能显隐正常 | □ |
| 11 | RTC同步至8台PLC | □ |
| 12 | U盘导出CSV正常 | □ |
| 13 | 历史数据存储正常 | □ |
| 14 | 审计日志记录正常 | □ |

---

## 附录A: 变量点数优化策略

若供应商确认McgsPro变量点数受限(如标准版600点),优化策略:

| 策略 | 节省点数 | 说明 |
|---|---|---|
| 只组态使能单元(首期1单元) | 728→91 | 首期仅需1单元,后续扩展 |
| 合并读写变量(同一地址读写共用) | 约20% | McgsPro支持同地址读写 |
| 减少趋势曲线数(7→4) | 约30 | 仅保留核心4条曲线 |
| 报警用字读取而非位读取 | 约200 | 读VW300~303后位运算解析 |

---

## 附录B: Modbus TCP备选方案

若供应商二轮确认S7协议不支持8连接,改用Modbus TCP:

### PLC侧配置(每台PLC)

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | OB1调用MBUS_SERVER指令 | □ |
| 2 | 配置HoldStart=VB0(V区映射到保持寄存器) | □ |
| 3 | MaxHold=200(映射VB0~VB399) | □ |
| 4 | Modbus TCP端口502 | □ |

### HMI侧配置

| 步骤 | 操作 | 确认 |
|---|---|---|
| 1 | 添加"Modbus TCP客户端"驱动 | □ |
| 2 | 8个连接实例,IP 192.168.2.101~108,端口502 | □ |
| 3 | 变量地址映射: V区→保持寄存器40001+x | □ |

### 地址映射规则

| PLC地址 | Modbus寄存器 | 说明 |
|---|---|---|
| VB0 | 40001(高字节) | V区字节0 |
| VW2 | 40002 | V区字2 |
| VD10 | 40003~40004 | V区双字10(2寄存器) |
| V300.0 | 40301.0 | 报警字1第0位 |

**注**: Modbus TCP方案需在PLC侧增加约50行STL(MBUS_SERVER配置+映射),开发量约1天。

---

**文档版本**: v1.0
**创建日期**: 2026-07-15
**说明**: 本指南基于昆仑通态MCGS通用特性编写,供应商二轮确认具体型号与脚本能力后,可能需微调脚本函数名与驱动配置细节。组态工程师可先按此准备,型号确认后即可上手组态。
