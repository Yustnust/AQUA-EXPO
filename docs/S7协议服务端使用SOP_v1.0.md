# S7协议服务端使用SOP v1.0

**配套文档**：《PLC逻辑仿真器 v2.0》、《HMI画面架构规划文档 v9.3》、《MCGS通讯配置SOP v1.0》
**用途**：在无硬件环境下,通过S7协议服务端实现MCGS HMI与PLC仿真器联调
**适用范围**：8套缸单元HMI-PLC联调测试
**文件**: `sim/s7_server.py` + `sim/test_s7_server.py`

---

## 一、概述

### 1.1 工作原理

```
[MCGS组态软件]                  [S7协议服务端]                [PLC仿真器]
  电脑运行                        Python脚本                    8个PLCSim实例
     ↓                              ↓                            ↓
  8个S7连接 ──TCP──→ 8端口监听(10200~10207) ──→ 8个独立PLC逻辑
                     (TCP端口)                    (100ms/周期扫描)
```

S7协议服务端模拟8台S7-200 SMART PLC的S7协议响应,让MCGS在不接真实PLC的情况下进行联调测试。

### 1.2 与真实PLC的差异

| 项 | 真实PLC | S7服务端 |
|---|---|---|
| IP地址 | 192.168.2.101~108 | 127.0.0.1 |
| 端口 | TCP 102 (S7标准) | TCP 10200~10207 (避开102特权端口) |
| 协议 | S7comm over ISO-on-TCP | 完全相同 |
| V区数据 | 真实PLC内存 | PLCSim仿真内存 |
| 状态机 | 真实STL执行 | PLCSim按预期语义模拟 |
| 响应延迟 | 1~5ms | <1ms (本机) |

### 1.3 何时使用

**适用场景**:
- HMI组态完成后,无PLC硬件时验证画面/变量/脚本
- HMI-PLC联调测试,提前发现通讯问题
- 回归测试: PLC代码修改后验证HMI不受影响
- 演示与培训: 无需硬件即可演示完整功能

**不适用场景**:
- 验证PLC STL代码本身(用PLCSim直接跑test_sat_cases.py)
- 真实通讯性能测试(本机延迟不准)
- 现场调试(必须用真实PLC)

---

## 二、环境准备

### 2.1 软件依赖

| 软件 | 版本 | 用途 |
|---|---|---|
| Python | 3.8+ | 运行S7服务端 |
| MCGS组态软件 | McgseSet | HMI组态+仿真 |
| 网络工具 | ncat/wireshark | 调试(可选) |

### 2.2 文件清单

```
AQUA-EXPO/sim/
  ├── plc_simulator.py      # PLC仿真器核心(v2.0)
  ├── s7_server.py          # S7协议服务端(本SOP主文件)
  ├── test_s7_server.py     # S7服务端测试用例
  └── test_sat_cases.py     # PLC仿真器SAT测试用例
```

### 2.3 启动前自检

```bash
cd AQUA-EXPO/sim

# 1. 验证Python版本
python3 --version  # 应≥3.8

# 2. 验证PLCSim可加载
python3 -c "from plc_simulator import PLCSim; print('PLCSim OK')"

# 3. 运行S7服务端自测(17项测试全过)
python3 test_s7_server.py
# 预期: 测试完成: ✓17通过 ✗0失败 ⊘0跳过
```

---

## 三、启动S7服务端

### 3.1 基本启动

```bash
cd AQUA-EXPO/sim
python3 s7_server.py
```

**默认配置**:
- 8端口: 10200~10207
- PLC扫描周期: 100ms
- 监控打印: 每5秒
- 日志级别: INFO

### 3.2 启动参数

```bash
python3 s7_server.py [选项]

选项:
  --start-port PORT     起始端口 (默认10200)
  --units N             单元数量 (默认8)
  --scan-ms MS          PLC扫描周期毫秒 (默认100)
  --monitor-interval S  监控打印间隔秒 (默认5)
  --cold-start          启动时执行PLC冷启动
  --log-level LEVEL     日志级别 (DEBUG/INFO/WARNING/ERROR)
```

### 3.3 推荐启动命令

**联调模式(详细日志)**:
```bash
python3 s7_server.py --cold-start --log-level DEBUG --monitor-interval 10
```

**性能模式(最少日志)**:
```bash
python3 s7_server.py --cold-start --log-level WARNING
```

**单元测试模式(仅2单元)**:
```bash
python3 s7_server.py --units 2 --start-port 10200 --cold-start
```

### 3.4 启动后界面

```
======================================================================
  AQUA-EXPO S7协议服务端已启动
======================================================================
  单元数量: 8
  端口范围: 10200~10207
  PLC扫描周期: 100ms
  日志级别: INFO
======================================================================

  MCGS客户端配置:
    协议: S7协议
    IP: 127.0.0.1 (本机) 或 服务器IP
    端口: 10200~10207 (对应8台PLC)
    机架: 0, 槽: 1
    TSAP: 自动协商

  按Ctrl+C停止服务端

======================================================================
单元    端口    VW2     VW6     VW8     扫描周期  连接数
-----------------------------------------------------------------
U1     10200   0       0       0       142       0
U2     10201   0       0       0       142       0
...
======================================================================
```

---

## 四、MCGS客户端配置

### 4.1 修改端口(关键!)

S7-200 SMART标准端口是TCP 102,但S7服务端用10200~10207(避开Linux特权端口)。

**MCGS设备配置**:
1. 打开MCGS组态软件
2. 设备窗口 → 添加设备 → 西门子S7-200 SMART
3. 设备属性:
   - **IP地址**: 127.0.0.1
   - **端口**: 10200 (第1台) / 10201 (第2台) / ... / 10207 (第8台)
   - **机架号**: 0
   - **槽号**: 1
   - **本地TSAP**: 0100
   - **远程TSAP**: 0200
   - **连接类型**: 主动连接

### 4.2 8连接配置

在MCGS中添加8个独立设备:

| 设备名 | IP | 端口 | 对应PLC |
|---|---|---|---|
| PLC_1 | 127.0.0.1 | 10200 | U1 (192.168.2.101模拟) |
| PLC_2 | 127.0.0.1 | 10201 | U2 (192.168.2.102模拟) |
| PLC_3 | 127.0.0.1 | 10202 | U3 (192.168.2.103模拟) |
| PLC_4 | 127.0.0.1 | 10203 | U4 (192.168.2.104模拟) |
| PLC_5 | 127.0.0.1 | 10204 | U5 (192.168.2.105模拟) |
| PLC_6 | 127.0.0.1 | 10205 | U6 (192.168.2.106模拟) |
| PLC_7 | 127.0.0.1 | 10206 | U7 (192.168.2.107模拟) |
| PLC_8 | 127.0.0.1 | 10207 | U8 (192.168.2.108模拟) |

### 4.3 变量绑定

按[MCGS变量导入_8连接版.csv](file:///workspace/AQUA-EXPO/docs/hmi_preparation/MCGS变量导入_8连接版.csv)导入变量,每个变量绑定到对应PLC设备。

---

## 五、联调测试流程

### 5.1 第一阶段: 通讯验证

**目标**: 确认MCGS能连接8端口并读写V区

| 步骤 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| 1 | 启动S7服务端 | 8端口监听 | □ |
| 2 | MCGS配置PLC_1设备(127.0.0.1:10200) | 配置完成 | □ |
| 3 | MCGS设备窗口点击"设备测试" | 连接成功,在线状态=绿色 | □ |
| 4 | 读取VW2(状态机) | 返回0(S0) | □ |
| 5 | 写入V0.0=1(启动命令) | 写入成功 | □ |
| 6 | 读取V1.0(启动确认) | 1秒内变1 | □ |
| 7 | 读取VW2 | 1秒后变1(S1) | □ |
| 8 | 重复步骤2~7,配置PLC_2~8 | 全部8端口正常 | □ |

### 5.2 第二阶段: 画面显示验证

**目标**: 验证8画面数据刷新

| 步骤 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| 1 | MCGS仿真运行 | 画面1总览显示8单元 | □ |
| 2 | 卡片1~8颜色 | 全部绿色(通讯正常) | □ |
| 3 | 卡片1显示VW2=0 | 显示"S0 初始化" | □ |
| 4 | 点击卡片1 | 进入画面2详情页 | □ |
| 5 | 画面2显示实时数据 | VD10/VD14等参数显示 | □ |
| 6 | 返回画面1,点击其他单元 | 各单元数据独立 | □ |

### 5.3 第三阶段: 控制功能验证

**目标**: 验证HMI命令下发与PLC响应

| 步骤 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| 1 | 画面2点击"启动实验"按钮 | V0.0=1下发 | □ |
| 2 | 1秒后查看VW2 | 变为1(S1) | □ |
| 3 | 画面2显示状态 | 显示"S1 上缸进水" | □ |
| 4 | 点击"停止"按钮 | V0.2=1,VW2变8(S7) | □ |
| 5 | 触发急停(仿真器) | 见5.5节 | □ |

### 5.4 第四阶段: 报警显示验证

**目标**: 验证报警页+全局横幅

| 步骤 | 操作 | 预期结果 | 通过 |
|---|---|---|---|
| 1 | 通过Python直接置位V300.5 | PLC仿真器报警 | □ |
| 2 | 画面1卡片1 | 变红色闪烁 | □ |
| 3 | 全局报警横幅 | 显示"安全继电器故障" | □ |
| 4 | 进入画面5报警页 | 显示报警码99 | □ |
| 5 | 点击"报警确认" | V0.3=1下发 | □ |

**直接置位报警**(在S7服务端运行时):
```bash
# 在另一终端执行
cd AQUA-EXPO/sim
python3 -c "
import socket, struct
# 连接10200端口, 写V300.5=1
# (实际可用s7_client工具, 见附录)
"
```

### 5.5 第五阶段: 故障场景验证

| 场景 | 操作 | 预期结果 |
|---|---|---|
| 急停 | 仿真器执行 `plc.trigger_estop()` | VW2=99, 卡片红色 |
| 通讯中断 | 停止某个端口的PLC扫描线程 | 卡片黄色 |
| 单元未使能 | MCGS画面7关闭某单元 | 卡片灰色 |
| 多单元报警 | 多个PLC同时触发报警 | 横幅显示最高级 |

---

## 六、调试技巧

### 6.1 日志级别切换

**DEBUG模式**: 显示所有S7帧细节
```bash
python3 s7_server.py --log-level DEBUG
```

**典型DEBUG日志**:
```
09:30:15 [S7Conn-U1-127.0.0.1:54012] DEBUG [U1] Setup完成, PDU=480
09:30:15 [S7Conn-U1-127.0.0.1:54012] DEBUG [U1] Read Request: area=0x85 db=1 addr=10 len=4
09:30:15 [S7Conn-U1-127.0.0.1:54012] DEBUG [U1] Write Request: area=0x85 db=1 addr=20 len=2
```

### 6.2 抓包分析

用Wireshark抓包,过滤条件: `tcp.port == 10200`

可观察:
- COTP连接握手过程
- S7comm读写请求/响应
- 异常响应(返回码≠0xFF)

### 6.3 直接读写PLC(绕过MCGS)

```python
# 在Python中直接读写PLC仿真器(无需走S7协议)
from plc_simulator import PLCSim

plc = server.units[1]['plc']  # 获取1号单元PLC
with server.units[1]['lock']:
    print(f"VW2={plc.vw2}")           # 读状态机
    plc.set_v_bit(0, 0, True)         # 置V0.0=1(启动命令)
    plc.set_vd(10, 5.0)               # 设置浓度参数
```

### 6.4 故障排查

| 现象 | 可能原因 | 解决 |
|---|---|---|
| MCGS连接失败 | 端口未监听 | 检查S7服务端是否启动 |
| 连接成功但读不到数据 | 区域类型错误 | 检查area=0x85, db=1 |
| 数据错误 | 字节序问题 | 大端(S7标准) |
| 响应超时 | PLC扫描卡住 | 检查PLCSim异常 |
| 部分单元连不上 | 端口被占用 | 检查10200~10207端口 |

---

## 七、性能指标

### 7.1 实测性能(参考)

| 指标 | 数值 | 说明 |
|---|---|---|
| 单连接响应时间 | <2ms | 本机环回 |
| 8连接并发响应 | <5ms | 全部同时请求 |
| PLC扫描周期 | 100ms±5ms | 含FC逻辑 |
| 内存占用 | ~50MB | 8单元PLCSim |
| CPU占用 | <10% | 空闲时 |
| 单端口最大连接 | 4 | 限制(MCGS通常1连接/单元) |

### 7.2 容量限制

| 项 | 限制 | 说明 |
|---|---|---|
| 单次读字节数 | 480 | PDU大小 |
| 单次写字节数 | 480 | PDU大小 |
| 单元数 | 8 | 8端口 |
| 每端口连接数 | 4 | 可调 |
| V区地址范围 | VB0~VB599 | PLCSim限制 |

---

## 八、停止服务端

### 8.1 正常停止

按 `Ctrl+C`,服务端会:
1. 停止所有PLC扫描线程
2. 关闭所有客户端连接
3. 关闭监听socket
4. 退出

### 8.2 异常停止

若Ctrl+C无响应:
```bash
# 找到进程
ps aux | grep s7_server

# 强制终止
kill -9 <PID>
```

---

## 九、与SAT测试的关系

### 9.1 两种测试的区别

| 测试类型 | 工具 | 目的 | 验证内容 |
|---|---|---|---|
| PLC逻辑测试 | test_sat_cases.py | 验证STL逻辑正确性 | 状态机/FC/报警 |
| S7协议测试 | test_s7_server.py | 验证S7协议栈正确性 | 通讯/读写/并发 |
| HMI联调测试 | MCGS+S7服务端 | 验证HMI-PLC端到端 | 画面/变量/脚本 |

### 9.2 联合测试流程

```
1. python3 test_sat_cases.py    # PLC逻辑测试(78用例)
2. python3 test_s7_server.py    # S7协议测试(17用例)
3. python3 s7_server.py         # 启动服务端
4. MCGS组态软件配置8连接         # HMI联调
5. 执行第5节5阶段联调测试         # 端到端验证
```

---

## 十、附录

### 附录A: S7客户端工具脚本

```python
"""s7_client.py - 简易S7客户端,用于调试"""
import socket, struct

def s7_connect(host, port):
    """连接S7服务端,返回socket"""
    sock = socket.socket()
    sock.connect((host, port))
    # COTP CR
    cr = (b'\x03\x00\x00\x16'  # TPKT
          b'\x11\xe0\x00\x00\x01\x00\x01\x00'
          b'\xc0\x01\x0a\xc1\x02\x01\x00\xc2\x02\x02\x00')
    sock.sendall(cr)
    sock.recv(1024)  # COTP CC
    # Setup
    setup = (b'\x03\x00\x00\x19'
             b'\x02\xf0\x80'
             b'\x32\x01\x00\x00\x00\x01\x00\x04\x00\x06'
             b'\x28\x00\x01\x00'
             b'\x00\x08\x01\xc0\x01\xc0')
    sock.sendall(setup)
    sock.recv(1024)
    return sock

def s7_read(sock, area, db, addr, length):
    """读V区(area=0x85, db=1)"""
    item = bytes([0x12, 0x0A, length, db, area,
                  (addr>>16)&0xFF, (addr>>8)&0xFF, addr&0xFF,
                  0,0,0,0])
    req = (b'\x03\x00\x00\x1f'
           b'\x02\xf0\x80'
           b'\x32\x01\x00\x00\x00\x02\x00\x0e\x00\x00'
           b'\x04\x01') + item
    sock.sendall(req)
    resp = sock.recv(1024)
    # 解析: TPKT(4)+COTP(3)+S7头(12)+参数(2)+数据项(4+length)
    return resp[7+12+2+4:7+12+2+4+length]

# 使用示例
sock = s7_connect('127.0.0.1', 10200)
vb10 = s7_read(sock, 0x85, 1, 10, 1)
print(f"VB10 = 0x{vb10[0]:02X}")
```

### 附录B: S7协议帧结构速查

```
TPKT (4字节):
  03 00 LL LL          版本=3, 总长度(大端)

COTP DT (3字节):
  02 F0 80             length=2, type=DT(0xF0), EOT=0x80

S7 Header (10~12字节):
  32                   Protocol ID
  01/03                ROSCTR (1=Job, 3=Ack-Data)
  00 00                Reserved
  RR RR                PDU Reference
  PP PP                Parameter length
  DD DD                Data length
  [EE EE]              Error (仅Ack-Data, 2字节)

Read Item (12字节):
  12 0A LL DD AA AA AA AA 00 00 00 00
  itemhdr len db area addr24bit      padding

Read Response Data Item:
  FF 09 LL LL data...
  rc tsize length data

Write Response:
  FF/85                Return code per item
```

### 附录C: 常见错误码

| 错误码 | 含义 | 解决 |
|---|---|---|
| 0xFF | 成功 | — |
| 0x85 | 资源/区域错误 | 检查area/db/addr |
| 0x87 | 数据格式错误 | 检查transport_size |
| 0xD2 | 变量不存在 | 检查地址范围 |
| 0xD6 | 写入冲突 | 检查PLC锁 |

### 附录D: 测试用例清单

`test_s7_server.py` 包含17项测试:

| ID | 测试 | 说明 |
|---|---|---|
| S7-SR-01/02 | 服务端启动/停止 | 8端口监听 |
| S7-CT-01/02 | COTP连接 | Connect Request/Confirm |
| S7-ST-01 | Setup协商 | PDU大小协商 |
| S7-WR-01~04 | V区写入 | VB/VW + PLC内部验证 |
| S7-RD-01~03 | V区读取 | VB/VW/VD |
| S7-8P-01/02 | 8端口并发 | 连接+数据隔离 |
| S7-IQ-01 | I/Q区读取 | IB0读取 |
| S7-MC-01/02 | 多连接并发 | 同端口3连接 |

---

**文档结束**

**待办**:
1. MCGS组态软件中按4.2节配置8连接
2. 执行第5节5阶段联调测试
3. 实际测试中若发现协议差异,反馈至s7_server.py更新
4. 联调完成后,记录HMI-PLC联调测试报告
