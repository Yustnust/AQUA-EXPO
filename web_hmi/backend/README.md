# Web HMI 后端

关联 JIRA: [AQEX-50](https://yusongtao.atlassian.net/browse/AQEX-50), [AQEX-51](https://yusongtao.atlassian.net/browse/AQEX-51)

基于 FastAPI + pymodbus 的 Web HMI 后端，通过 Modbus TCP 与 8 台 S7-200 SMART PLC 通信。

## 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口（8 PLC + WebSocket）
│   ├── ws_manager.py        # WebSocket 连接管理器
│   └── plc/
│       ├── __init__.py
│       ├── client.py        # Modbus TCP 客户端（轮询、写入、重连）
│       ├── parser.py        # 寄存器数据解析/编码
│       └── registers.py     # PLC 变量映射表
├── config.yaml              # 配置文件（8 单元 PLC IP）
├── requirements.txt
└── README.md
```

## 快速启动

```bash
cd web_hmi/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 修改 config.yaml 中的 PLC IP
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 主要 API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 服务状态 |
| GET | `/api/v1/plc/status` | 所有单元 PLC 连接状态 |
| GET | `/api/v1/plc/status/{unit_id}` | 指定单元 PLC 连接状态 |
| GET | `/api/v1/plc/data` | 所有单元最新变量值 |
| GET | `/api/v1/plc/data/{unit_id}` | 指定单元最新变量值 |
| GET | `/api/v1/plc/variables` | 变量清单 |
| POST | `/api/v1/plc/write` | 写入单个变量（需指定 unit） |
| POST | `/api/v1/plc/write-pulse` | 写入位变量脉冲（需指定 unit） |
| GET | `/api/v1/config` | 当前配置 |
| WS | `/ws` | WebSocket 实时数据推送 |

## WebSocket 协议

连接 `ws://localhost:8000/ws`，接收以下消息类型：

### plc_update（数据更新）
```json
{
  "type": "plc_update",
  "unit": 1,
  "connected": true,
  "timestamp": "2026-07-30T12:00:00.000Z",
  "data": {
    "state_machine": 2,
    "alarm_code": 0,
    "alarm_byte_0": 0,
    "c_set": 0.5,
    "flowrate_instant": 12.3
  }
}
```

### plc_status（连接状态变化）
```json
{
  "type": "plc_status",
  "unit": 1,
  "online": true,
  "timestamp": "2026-07-30T12:00:00.000Z"
}
```

## 写入示例

```bash
# 写参数（单元1）
curl -X POST http://localhost:8000/api/v1/plc/write \
  -H "Content-Type: application/json" \
  -d '{"unit":1,"name":"c_set","value":0.5}'

# 写启动命令脉冲（单元1）
curl -X POST http://localhost:8000/api/v1/plc/write-pulse \
  -H "Content-Type: application/json" \
  -d '{"unit":1,"name":"cmd_start","duration":0.5}'
```