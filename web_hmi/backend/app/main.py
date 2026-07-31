"""
Web HMI 后端入口
关联 JIRA: AQEX-50

启动方式：
    cd web_hmi/backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.plc import PlcClient, VARIABLES, get_variable

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 全局状态
plc_client: Optional[PlcClient] = None
app_config: Dict[str, Any] = {}


def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    """加载 YAML 配置文件。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _on_plc_data(data: Dict[str, Any]):
    """PLC 数据更新回调（后续可扩展 WebSocket 推送）。"""
    logger.debug("PLC data updated, vars count: %d", len(data))


def _on_plc_status(online: bool):
    """PLC 连接状态变化回调。"""
    logger.info("PLC status changed: %s", "online" if online else "offline")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时连接 PLC，关闭时断开。"""
    global plc_client, app_config

    config_path = os.environ.get("WEB_HMI_CONFIG", "config.yaml")
    app_config = load_config(config_path)

    plc_cfg = app_config.get("plc", {})
    plc_client = PlcClient(
        host=plc_cfg.get("host", "192.168.2.101"),
        port=plc_cfg.get("port", 502),
        unit_id=plc_cfg.get("unit_id", 1),
        poll_interval=plc_cfg.get("poll_interval", 0.5),
        reconnect_interval=plc_cfg.get("reconnect_interval", 3.0),
        timeout=plc_cfg.get("timeout", 1.0),
        max_failures=plc_cfg.get("max_failures", 5),
        on_data=_on_plc_data,
        on_status=_on_plc_status,
    )
    await plc_client.start()
    logger.info("Web HMI backend started")

    yield

    if plc_client:
        await plc_client.stop()
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
    connected: bool
    host: str
    port: int
    poll_interval: float


class VariableValue(BaseModel):
    name: str
    value: Any


class WriteRequest(BaseModel):
    name: str
    value: Any


class WritePulseRequest(BaseModel):
    name: str
    duration: float = 0.5


# ============================================================
# API 路由
# ============================================================
@app.get("/")
async def root():
    return {"message": "AQUA-EXPO Web HMI Backend", "version": "1.0.0"}


@app.get("/api/v1/plc/status", response_model=PlcStatus)
async def get_plc_status():
    """获取 PLC 连接状态。"""
    if not plc_client:
        raise HTTPException(status_code=503, detail="PLC client not initialized")
    return PlcStatus(
        connected=plc_client.connected,
        host=plc_client.host,
        port=plc_client.port,
        poll_interval=plc_client.poll_interval,
    )


@app.get("/api/v1/plc/data")
async def get_plc_data():
    """获取当前所有 PLC 变量的最新值。"""
    if not plc_client:
        raise HTTPException(status_code=503, detail="PLC client not initialized")
    return {
        "connected": plc_client.connected,
        "timestamp": None,  # 后续补充
        "data": plc_client.latest_data,
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
    """写入单个 PLC 变量。"""
    if not plc_client:
        raise HTTPException(status_code=503, detail="PLC client not initialized")
    if not plc_client.connected:
        raise HTTPException(status_code=503, detail="PLC not connected")

    var = get_variable(req.name)
    if not var:
        raise HTTPException(status_code=400, detail=f"Unknown variable: {req.name}")
    if not var.writable:
        raise HTTPException(status_code=403, detail=f"Variable not writable: {req.name}")

    ok = await plc_client.write_variable(req.name, req.value)
    if not ok:
        raise HTTPException(status_code=500, detail="Write failed")
    return {"success": True, "name": req.name, "value": req.value}


@app.post("/api/v1/plc/write-pulse")
async def write_pulse(req: WritePulseRequest):
    """写入位变量脉冲（如启动/停止/消音命令）。"""
    if not plc_client:
        raise HTTPException(status_code=503, detail="PLC client not initialized")
    if not plc_client.connected:
        raise HTTPException(status_code=503, detail="PLC not connected")

    var = get_variable(req.name)
    if not var:
        raise HTTPException(status_code=400, detail=f"Unknown variable: {req.name}")
    if var.dtype.value != "bool":
        raise HTTPException(status_code=400, detail="Pulse write only supports bool variables")
    if not var.writable:
        raise HTTPException(status_code=403, detail=f"Variable not writable: {req.name}")

    asyncio.create_task(plc_client.write_bit_pulse(req.name, req.duration))
    return {"success": True, "name": req.name, "duration": req.duration}


@app.get("/api/v1/config")
async def get_config():
    """获取当前配置（敏感信息已过滤）。"""
    safe_config = {
        "plc": {
            "host": app_config.get("plc", {}).get("host"),
            "port": app_config.get("plc", {}).get("port"),
            "poll_interval": app_config.get("plc", {}).get("poll_interval"),
        },
        "server": app_config.get("server", {}),
        "history": app_config.get("history", {}),
    }
    return safe_config
