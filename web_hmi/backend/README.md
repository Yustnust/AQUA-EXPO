# Web HMI 后端

关联 JIRA: [AQEX-50](https://yusongtao.atlassian.net/browse/AQEX-50)

基于 FastAPI + pymodbus 的 Web HMI 后端，通过 Modbus TCP 与 S7-200 SMART PLC 通信。

## 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   └── plc/
│       ├── __init__.py
│       ├── client.py        # Modbus TCP 客户端（轮询、写入、重连）
│       ├── parser.py        # 寄存器数据解析/编码
│       └── registers.py     # PLC 变量映射表
├── config.yaml              # 配置文件
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
| GET | `/api/v1/plc/status` | PLC 连接状态 |
| GET | `/api/v1/plc/data` | 当前所有变量最新值 |
| GET | `/api/v1/plc/variables` | 变量清单 |
| POST | `/api/v1/plc/write` | 写入单个变量 |
| POST | `/api/v1/plc/write-pulse` | 写入位变量脉冲 |
| GET | `/api/v1/config` | 当前配置 |

## 写入示例

```bash
# 写浮点参数
curl -X POST http://localhost:8000/api/v1/plc/write \
  -H "Content-Type: application/json" \
  -d '{"name":"c_set","value":0.5}'

# 写启动命令脉冲
curl -X POST http://localhost:8000/api/v1/plc/write-pulse \
  -H "Content-Type: application/json" \
  -d '{"name":"cmd_start","duration":0.5}'
```
