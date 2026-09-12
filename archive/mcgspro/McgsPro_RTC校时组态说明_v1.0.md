# McgsPro RTC 校时组态说明

## 1. 任务说明

- **任务编号**：AQEX-51

- **任务名称**：PLC 长时间停机后 HMI 校时

- **关联 PLC 修改**：FC0\_SysInit.stl、FC22\_RTC\_Sync.stl（新增）、OB1\_MAIN.stl

- **适用单元**：单元 1\~8（每单元独立，以下以单元 1 为例）

- **功能目标**：PLC 停机再启动后，若 RTC 时间异常，McgsPro 弹窗提示操作员同步 PLC 时间。

## 2. 原理概述

1. PLC 上电或 STOP→RUN 时，FC0 读取 PLC 实时时钟（RTC）到 VB900\~VB905。
2. 若 RTC 自身非法（如分>59、月>12）或 RTC 早于 DT10（下缸变满时间戳），FC0 置位 **V303.7 = 1**（请求校时）。
3. McgsPro 检测到 **V303.7 = 1** 后弹出校时提示窗口。
4. 操作员点击"同步"按钮，McgsPro 将本机时间写入 VB900\~VB905（BCD 格式），并置位 **V0.6 = 1**。
5. FC22 检测到 V0.6 上升沿，调用 `TODW` 将 VB900\~VB905 写入 PLC RTC，随后清除 V303.7 和 V0.6。
6. 若 V303.7 = 1 持续 **5 分钟** 未同步，FC22 置 **V303.5 = 1** 并将 VW2 置 99（S\_ERROR），报警码 VW6 = 65。

## 3. 新增 PLC 变量

| PLC 地址 | 名称（建议）                         | 类型     | 读写 | 说明               |
| ------ | ------------------------------ | ------ | -- | ---------------- |
| V303.7 | U{N}\_V303\_7\_Need\_RTC\_Sync | 位      | R  | PLC 请求 HMI 校时标志  |
| V0.6   | U{N}\_V0\_6\_RTC\_Sync\_Cmd    | 位      | RW | HMI 校时命令位（上升沿触发） |
| VB900  | U{N}\_VB900\_RTC\_Year         | 8 位无符号 | RW | 年（BCD，00\~99）    |
| VB901  | U{N}\_VB901\_RTC\_Month        | 8 位无符号 | RW | 月（BCD，01\~12）    |
| VB902  | U{N}\_VB902\_RTC\_Day          | 8 位无符号 | RW | 日（BCD，01\~31）    |
| VB903  | U{N}\_VB903\_RTC\_Hour         | 8 位无符号 | RW | 时（BCD，00\~23）    |
| VB904  | U{N}\_VB904\_RTC\_Minute       | 8 位无符号 | RW | 分（BCD，00\~59）    |
| VB905  | U{N}\_VB905\_RTC\_Second       | 8 位无符号 | RW | 秒（BCD，00\~59）    |

> 注：`{N}` 为单元号，如单元 1 为 `U1_V303_7_Need_RTC_Sync`。

## 4. 需要更新的技术文档

完成本组态后，需同步更新以下文档：

1. **McgsPro 变量导入 CSV**

   - 文件：`McgsPro变量导入_单元{N}.csv`

   - 内容：添加第 3 节中的 8 个变量。

   - 注意：VB900\~VB905 为 8 位无符号二进制；V0.6、V303.7 为位变量。

2. **HMI 组态导入说明.md**

   - 更新变量导入章节的变量清单。

3. **McgsPro 工程搭建总 SOP**

   - 在"报警与状态指示"或"系统功能"章节增加 RTC 校时窗口的组态要求。

4. **McgsPro 脚本代码文档**

   - 将第 7 节的循环策略脚本和第 8 节的按钮脚本纳入脚本代码库。

## 5. McgsPro 组态步骤

### 5.1 导入新增变量

1. 打开 McgsPro 工程。
2. 打开`工具`→`变量导入`，选择对应单元的 CSV 文件。
3. 确认以下变量已导入（以单元 1 为例）：

   - `U1_V303_7_Need_RTC_Sync`

   - `U1_V0_6_RTC_Sync_Cmd`

   - `U1_VB900_RTC_Year`

   - `U1_VB901_RTC_Month`

   - `U1_VB902_RTC_Day`

   - `U1_VB903_RTC_Hour`

   - `U1_VB904_RTC_Minute`

   - `U1_VB905_RTC_Second`

### 5.2 新建校时提示窗口

1. 在`用户窗口`中新建窗口，命名为 `RTC_Sync_Wnd`。
2. 窗口属性：

   - 大小：400 x 200

   - 标题：`PLC 时钟异常`

   - 边框：对话框边框

   - 是否可移动：是

   - 弹出方式：模态/非模态均可（建议模态，强制操作员处理）
3. 窗口内添加控件：

   - **标签**：显示文本`PLC 实时时钟异常，请同步时间。`

   - **按钮**：文本`同步`，命名为`btn_RTC_Sync`。

   - （可选）**标签**：显示当前将要写入的时间，绑定脚本变量。

### 5.3 设置循环策略

1. 打开`运行策略`→`循环策略`。
2. 新增或编辑一个循环策略（建议命名为`RTC_Sync_Poll`）。
3. 在策略中添加脚本：

```vb
' RTC 校时弹窗控制
IF U1_V303_7_Need_RTC_Sync = 1 THEN
    !OpenSubWnd("RTC_Sync_Wnd", 200, 150, 400, 200)
ELSE
    !CloseSubWnd("RTC_Sync_Wnd")
END IF
```

1. 设置策略执行周期：1000 ms（1 秒）。

## 6. 同步按钮脚本

双击`btn_RTC_Sync`按钮，在`按钮动作`→`抬起脚本`中添加以下脚本：

```vb
' 取本机日期
DIM dateStr, year, month, day
DIM yearHigh, yearLow, monthHigh, monthLow, dayHigh, dayLow

DIM timeStr, hour, minute, second
DIM hourHigh, hourLow, minHigh, minLow, secHigh, secLow

dateStr = !Date()
year  = !Str2I(!Left(dateStr, 4)) - 2000
month = !Str2I(!Mid(dateStr, 6, 2))
day   = !Str2I(!Mid(dateStr, 9, 2))

timeStr = !Time()
hour   = !Str2I(!Left(timeStr, 2))
minute = !Str2I(!Mid(timeStr, 4, 2))
second = !Str2I(!Right(timeStr, 2))

' 十进制转 BCD
yearHigh = year / 10
yearLow  = year - yearHigh * 10
U1_VB900_RTC_Year = yearHigh * 16 + yearLow

monthHigh = month / 10
monthLow  = month - monthHigh * 10
U1_VB901_RTC_Month = monthHigh * 16 + monthLow

dayHigh = day / 10
dayLow  = day - dayHigh * 10
U1_VB902_RTC_Day = dayHigh * 16 + dayLow

hourHigh = hour / 10
hourLow  = hour - hourHigh * 10
U1_VB903_RTC_Hour = hourHigh * 16 + hourLow

minHigh = minute / 10
minLow  = minute - minHigh * 10
U1_VB904_RTC_Minute = minHigh * 16 + minLow

secHigh = second / 10
secLow  = second - secHigh * 10
U1_VB905_RTC_Second = secHigh * 16 + secLow

' 触发 PLC 写入 RTC
U1_V0_6_RTC_Sync_Cmd = 1
```

## 7. 变量 CSV 格式示例

以单元 1 为例，CSV 中新增行如下：

```csv
U1_V303_7_Need_RTC_Sync,V,303.7,位,0,0,0,0,0,0,0,0,0
U1_V0_6_RTC_Sync_Cmd,V,0.6,位,0,0,0,0,0,0,0,0,0
U1_VB900_RTC_Year,V,VB900,8位无符号二进制,0,0,0,0,0,0,0,0,0
U1_VB901_RTC_Month,V,VB901,8位无符号二进制,0,0,0,0,0,0,0,0,0
U1_VB902_RTC_Day,V,VB902,8位无符号二进制,0,0,0,0,0,0,0,0,0
U1_VB903_RTC_Hour,V,VB903,8位无符号二进制,0,0,0,0,0,0,0,0,0
U1_VB904_RTC_Minute,V,VB904,8位无符号二进制,0,0,0,0,0,0,0,0,0
U1_VB905_RTC_Second,V,VB905,8位无符号二进制,0,0,0,0,0,0,0,0,0
```

> 具体列顺序以现有 CSV 模板为准。

## 8. 测试验证

### 8.1 正常流程测试

1. 将 PLC 时钟设置为非法值（如分=70）。
2. STOP→RUN，观察：

   - V303.7 = 1

   - VW2 = 0（S0，不进 S\_ERROR）

   - McgsPro 弹出`RTC_Sync_Wnd`窗口。
3. 点击"同步"按钮，观察：

   - VB900\~VB905 被写入当前时间（BCD 格式）。

   - V0.6 由 1 变 0。

   - V303.7 = 0。

   - 弹窗关闭。
4. 读取 PLC RTC，确认时间已更新。

### 8.2 超时保护测试

1. 将 PLC 时钟设置为非法值。
2. STOP→RUN，V303.7 = 1。
3. **5 分钟内不点击同步**。
4. 观察：

   - T59 计时到后，V303.5 = 1。

   - VW2 = 99（S\_ERROR）。

   - VW6 = 65（RTC 丢失报警码）。
5. HMI 报警确认 + 系统复位后，应能回 S0。

### 8.3 断电恢复测试

1. PLC 正常供电，时钟已校准。
2. 进入 S0 状态后 STOP PLC。
3. 断电一段时间（让超级电容放电，或手动清除 V304.0 模拟冷启动）。
4. 重新上电 RUN，观察不应再因 RTC 问题进 S\_ERROR。

## 9. 注意事项

1. **V0.6 是脉冲命令**：FC22 在检测到 V0.6 上升沿后会自动复位 V0.6，McgsPro 只需置 1 即可，无需手动清 0。
2. **BCD 格式**：McgsPro 脚本中已将十进制转换为 BCD，禁止在通道处理中再次缩放或转换。
3. **弹窗位置**：`!OpenSubWnd` 的 x、y 坐标根据实际分辨率调整，避免遮挡关键操作区域。
4. **多单元工程**：每单元使用独立的 V 区地址，本方案中所有地址为全局固定地址（V0.6、V303.7、VB900\~VB905），不随单元变化。如多单元共用同一 PLC，需考虑地址冲突。
5. **后续维护**：若调整超时时间，同步修改 FC22 中 T59 的 PT 值（当前 3000，即 5 分钟）。

