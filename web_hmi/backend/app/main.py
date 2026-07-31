"""
Web HMI 后端入口
关联 JIRA: AQEX-50, AQEX-51

启动方式：
    cd web_hmi/backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import yaml
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.plc import PlcClient, VARIABLES, get_variable
from app.ws_manager import ws_manager, build_update_message, build_status_message

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 全局状态
plc_clients: Dict[int, PlcClient] = {}  # unit_id -> PlcClient
app_config: Dict[str, Any] = {}

# 数据节流：记录每个单元上次推送时间，避免过于频繁的 WebSocket 广播
_last_broadcast: Dict[int, float] = {}
BROADCAST_MIN_INTERVAL = 0.2  # 秒


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    """加载 YAML 配置文件。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _make_plc_data_callback(unit_id: int):
    """为指定单元创建 PLC 数据更新回调——广播到 WebSocket。"""

    def _on_data(data: Dict[str, Any]):
        # 避免过于频繁的广播
        import time as _time
        now = _time.monotonic()
        if unit_id in _last_broadcast and now - _last_broadcast[unit_id] < BROADCAST_MIN_INTERVAL:
            return
        _last_broadcast[unit_id] = now

        client = plc_clients.get(unit_id)
        msg = build_update_message(unit_id, data, client.connected if client else False)
        # 非阻塞广播
        asyncio.ensure_future(ws_manager.broadcast(msg))

    return _on_data


def _make_plc_status_callback(unit_id: int):
    """为指定单元创建 PLC 连接状态变化回调。"""

    def _on_status(online: bool):
        msg = build_status_message(unit_id, online)
        asyncio.ensure_future(ws_manager.broadcast(msg))

    return _on_status


async def _create_plc_clients(cfg: Dict[str, Any]) -> Dict[int, PlcClient]:
    """根据配置创建所有 PLC 客户端并启动。"""
    clients: Dict[int, PlcClient] = {}
    defaults = cfg.get("plc_defaults", {})

    for i, plc_cfg in enumerate(cfg.get("plcs", []), start=1):
        if not plc_cfg.get("enabled", True):
            logger.info("Unit %d disabled, skip", i)
            continue

        client = PlcClient(
            host=plc_cfg["host"],
            port=plc_cfg.get("port", 502),
            unit_id=plc_cfg.get("unit_id", 1),
            poll_interval=plc_cfg.get("poll_interval", defaults.get("poll_interval", 0.5)),
            reconnect_interval=plc_cfg.get("reconnect_interval", defaults.get("reconnect_interval", 3.0)),
            timeout=plc_cfg.get("timeout", defaults.get("timeout", 1.0)),
            max_failures=plc_cfg.get("max_failures", defaults.get("max_failures", 5)),
            on_data=_make_plc_data_callback(i),
            on_status=_make_plc_status_callback(i),
        )
        await client.start()
        clients[i] = client
        logger.info("PLC client %d started: %s:%s", i, plc_cfg["host"], plc_cfg.get("port", 502))

    return clients


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时连接所有 PLC，关闭时断开。"""
    global plc_clients, app_config

    config_path = os.environ.get("WEB_HMI_CONFIG", "config.yaml")
    app_config = load_config(config_path)

    plc_clients = await _create_plc_clients(app_config)
    logger.info("Web HMI backend started, %d PLC clients", len(plc_clients))

    yield

    for client in plc_clients.values():
        await client.stop()
    plc_clients.clear()
    logger.info("Web HMI backend stopped")


app = FastAPI(
    title="AQUA-EXPO Web HMI Backend",
    description="药液配置与加注控制系统 Web HMI 后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS：允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 请求/响应模型
# ============================================================
class PlcStatus(BaseModel):
    unit: int
    connected: bool
    host: str
    port: int


class WriteRequest(BaseModel):
    unit: int = 1
    name: str
    value: Any


class WritePulseRequest(BaseModel):
    unit: int = 1
    name: str
    duration: float = 0.5


# ============================================================
# API 路由
# ============================================================
@app.get("/")
async def root():
    return {"message": "AQUA-EXPO Web HMI Backend", "version": "1.0.0"}


@app.get("/api/v1/plc/status")
async def get_plc_status():
    """获取所有单元 PLC 连接状态。"""
    units = []
    for unit_id, client in plc_clients.items():
        units.append(PlcStatus(
            unit=unit_id,
            connected=client.connected,
            host=client.host,
            port=client.port,
        ))
    return {"units": units}


@app.get("/api/v1/plc/status/{unit_id}")
async def get_plc_unit_status(unit_id: int):
    """获取指定单元 PLC 连接状态。"""
    client = plc_clients.get(unit_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"Unit {unit_id} not found")
    return PlcStatus(
        unit=unit_id,
        connected=client.connected,
        host=client.host,
        port=client.port,
    )


@app.get("/api/v1/plc/data")
async def get_plc_data():
    """获取所有单元 PLC 变量的最新值。"""
    units = {}
    for unit_id, client in plc_clients.items():
        units[str(unit_id)] = {
            "connected": client.connected,
            "data": client.latest_data,
        }
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "units": units,
    }


@app.get("/api/v1/plc/data/{unit_id}")
async def get_plc_unit_data(unit_id: int):
    """获取指定单元 PLC 变量的最新值。"""
    client = plc_clients.get(unit_id)
    if not client:
        raise HTTPException(status_code=404, detail=f"Unit {unit_id} not found")
    return {
        "unit": unit_id,
        "connected": client.connected,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": client.latest_data,
    }


@app.get("/api/v1/plc/variables")
async def get_variables():
    """获取所有支持的 PLC 变量清单。"""
    result = []
    for v in VARIABLES:
        result.append({
            "name": v.name,
            "v_addr": v.v_addr,
            "reg_addr": v.reg_addr,
            "reg_count": v.reg_count,
            "dtype": v.dtype.value,
            "writable": v.writable,
            "note": v.note,
        })
    return result


@app.post("/api/v1/plc/write")
async def write_variable(req: WriteRequest):
    """写入指定单元的 PLC 变量。"""
    client = plc_clients.get(req.unit)
    if not client:
        raise HTTPException(status_code=404, detail=f"Unit {req.unit} not found")
    if not client.connected:
        raise HTTPException(status_code=503, detail=f"Unit {req.unit} PLC not connected")

    var = get_variable(req.name)
    if not var:
        raise HTTPException(status_code=400, detail=f"Unknown variable: {req.name}")
    if not var.writable:
        raise HTTPException(status_code=403, detail=f"Variable not writable: {req.name}")

    ok = await client.write_variable(req.name, req.value)
    if not ok:
        raise HTTPException(status_code=500, detail="Write failed")
    return {"success": True, "unit": req.unit, "name": req.name, "value": req.value}


@app.post("/api/v1/plc/write-pulse")
async def write_pulse(req: WritePulseRequest):
    """写入位变量脉冲（如启动/停止/消音命令）。"""
    client = plc_clients.get(req.unit)
    if not client:
        raise HTTPException(status_code=404, detail=f"Unit {req.unit} not found")
    if not client.connected:
        raise HTTPException(status_code=503, detail=f"Unit {req.unit} PLC not connected")

    var = get_variable(req.name)
    if not var:
        raise HTTPException(status_code=400, detail=f"Unknown variable: {req.name}")
    if var.dtype.value != "bool":
        raise HTTPException(status_code=400, detail="Pulse write only supports bool variables")
    if not var.writable:
        raise HTTPException(status_code=403, detail=f"Variable not writable: {req.name}")

    asyncio.create_task(client.write_bit_pulse(req.name, req.duration))
    return {"success": True, "unit": req.unit, "name": req.name, "duration": req.duration}


@app.get("/api/v1/config")
async def get_config():
    """获取当前配置（敏感信息已过滤）。"""
    safe_config = {
        "plcs": [
            {
                "unit": i,
                "host": plc_cfg["host"],
                "port": plc_cfg.get("port", 502),
                "name": plc_cfg.get("name", f"单元{i}"),
                "enabled": plc_cfg.get("enabled", True),
            }
            for i, plc_cfg in enumerate(app_config.get("plcs", []), start=1)
        ],
        "server": app_config.get("server", {}),
        "history": app_config.get("history", {}),
    }
    return safe_config


# ============================================================
# WebSocket 端点
# ============================================================
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket 端点，实时推送 PLC 数据更新。

    前端连接后，可接收以下消息类型：
    - plc_update:    PLC 变量数据更新
    - plc_status:    PLC 连接状态变化

    消息格式：
    {
      "type": "plc_update",
      "unit": 1,
      "connected": true,
      "timestamp": "2026-07-30T...",
      "data": { "state_machine": 2, "alarm_code": 0, ... }
    }
    """
    await ws_manager.connect(ws)
    try:
        # 首次连接时发送全量数据
        for unit_id, client in plc_clients.items():
            if client.latest_data:
                msg = build_update_message(unit_id, client.latest_data, client.connected)
                await ws.send_json(msg)

        # 保持连接，接收客户端消息（如心跳、订阅过滤等）
        while True:
            try:
                data = await ws.receive_text()
                # 预留：客户端可发送订阅过滤条件
                logger.debug("WebSocket received: %s", data[:100])
            except WebSocketDisconnect:
                break
            except Exception:
                logger.warning("WebSocket receive error")
                break
    finally:
        await ws_manager.disconnect(ws)