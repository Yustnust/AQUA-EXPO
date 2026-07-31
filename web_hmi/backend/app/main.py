"""
Web HMI 后端入口
关联 JIRA: AQEX-50, AQEX-51, AQEX-53, AQEX-54

启动方式：
    cd web_hmi/backend
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import yaml
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.plc import PlcClient, VARIABLES, get_variable
from app.ws_manager import ws_manager, build_update_message, build_status_message, build_alarm_message
from app.history import HistoryStore, get_available_trend_variables
from app.alarm import AlarmStore, get_active_alarms, ALARM_DEFINITIONS
from app.auth import (
    user_store, TokenResponse, LoginRequest, ChangePasswordRequest, UserInfo,
    create_access_token, get_current_user, require_permission, require_role,
    ROLE_ADMIN,
)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 全局状态
plc_clients: Dict[int, PlcClient] = {}  # unit_id -> PlcClient
history_store: Optional[HistoryStore] = None
alarm_store: Optional[AlarmStore] = None
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
        # 报警处理（检测状态变化，记录事件）
        if alarm_store:
            asyncio.ensure_future(alarm_store.process(unit_id, data))

        # 历史数据记录（每条都记录，内部有采样节流）
        if history_store:
            asyncio.ensure_future(history_store.record(unit_id, data))

        # 避免过于频繁的 WebSocket 广播
        import time as _time
        now = _time.monotonic()
        if unit_id in _last_broadcast and now - _last_broadcast[unit_id] < BROADCAST_MIN_INTERVAL:
            return
        _last_broadcast[unit_id] = now

        client = plc_clients.get(unit_id)
        msg = build_update_message(unit_id, data, client.connected if client else False)
        # 非阻塞广播
        asyncio.ensure_future(ws_manager.broadcast(msg))

        # 若有活动报警，单独推送报警消息
        active_alarms = get_active_alarms(data)
        if active_alarms:
            alarm_msg = build_alarm_message(unit_id, active_alarms, data)
            asyncio.ensure_future(ws_manager.broadcast(alarm_msg))

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
    global plc_clients, history_store, alarm_store, app_config

    config_path = os.environ.get("WEB_HMI_CONFIG", "config.yaml")
    app_config = load_config(config_path)

    # 初始化历史数据库
    hist_cfg = app_config.get("history", {})
    history_store = HistoryStore(
        db_path=hist_cfg.get("db_path", "data/history.db"),
        retention_days=hist_cfg.get("default_retention_days", 30),
        fast_interval=hist_cfg.get("fast_sample_interval", 1),
        slow_interval=hist_cfg.get("slow_sample_interval", 10),
    )
    await history_store.initialize()
    await history_store.start()

    # 初始化报警存储
    alarm_store = AlarmStore(db_path=hist_cfg.get("db_path", "data/history.db"))
    await alarm_store.initialize()
    await alarm_store.start()

    # 初始化用户存储
    await user_store.initialize()

    plc_clients = await _create_plc_clients(app_config)
    logger.info("Web HMI backend started, %d PLC clients", len(plc_clients))

    yield

    for client in plc_clients.values():
        await client.stop()
    plc_clients.clear()
    if history_store:
        await history_store.stop()
    if alarm_store:
        await alarm_store.stop()
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


class RetentionRequest(BaseModel):
    days: int


# ============================================================
# API 路由
# ============================================================
@app.get("/")
async def root():
    return {"message": "AQUA-EXPO Web HMI Backend", "version": "1.0.0"}


# ============================================================
# 认证 API
# ============================================================
@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """用户登录，返回 JWT 访问令牌。"""
    user = await user_store.authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user["username"], user["role"], user["password_changed"])
    return TokenResponse(
        access_token=token,
        username=user["username"],
        role=user["role"],
        expires_in=8 * 3600,  # 8 小时
        password_changed=user["password_changed"],
    )


@app.post("/api/v1/auth/change-password")
async def change_password(
    req: ChangePasswordRequest,
    user: Dict[str, Any] = Depends(get_current_user),
):
    """修改当前用户密码。"""
    ok = await user_store.change_password(user["username"], req.old_password, req.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    return {"success": True, "message": "Password changed successfully"}


@app.get("/api/v1/auth/me", response_model=UserInfo)
async def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return UserInfo(
        username=user["username"],
        role=user["role"],
        password_changed=user["password_changed"],
    )


@app.get("/api/v1/auth/users")
async def list_users(user: Dict[str, Any] = Depends(require_role(ROLE_ADMIN))):
    """获取所有用户列表（仅管理员）。"""
    return await user_store.get_all_users()


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "operator"


@app.post("/api/v1/auth/users")
async def create_user(
    req: CreateUserRequest,
    user: Dict[str, Any] = Depends(require_role(ROLE_ADMIN)),
):
    """创建新用户（仅管理员）。"""
    ok = await user_store.create_user(req.username, req.password, req.role)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to create user (duplicate or invalid role)")
    return {"success": True, "username": req.username}


@app.delete("/api/v1/auth/users/{username}")
async def delete_user(
    username: str,
    current_user: Dict[str, Any] = Depends(require_role(ROLE_ADMIN)),
):
    """删除用户（仅管理员，不能删除自己）。"""
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    ok = await user_store.delete_user(username)
    if not ok:
        raise HTTPException(status_code=400, detail="Failed to delete user (not found or last admin)")
    return {"success": True, "username": username}


# ============================================================
# PLC 状态与数据 API
# ============================================================


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
async def write_variable(
    req: WriteRequest,
    user: Dict[str, Any] = Depends(require_permission("param_write")),
):
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
async def write_pulse(
    req: WritePulseRequest,
    user: Dict[str, Any] = Depends(require_permission("start_stop")),
):
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
# 历史数据 API
# ============================================================
@app.get("/api/v1/history/variables")
async def get_history_variables():
    """获取所有支持趋势曲线的变量列表。"""
    return get_available_trend_variables()


@app.get("/api/v1/history/query/{unit_id}")
async def query_history(
    unit_id: int,
    vars: str = "",
    start: str = "",
    end: str = "",
    minutes: int = 60,
):
    """查询历史数据。

    Query params:
    - vars: 逗号分隔的变量名（如 "state_machine,alarm_code"）
    - start: 开始时间 ISO 格式
    - end: 结束时间 ISO 格式
    - minutes: 如未指定 start/end，默认查最近 N 分钟
    """
    if not history_store:
        raise HTTPException(status_code=503, detail="History store not initialized")

    if vars:
        var_names = [v.strip() for v in vars.split(",") if v.strip()]
    else:
        var_names = list(get_available_trend_variables())

    if start and end:
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start/end format, use ISO 8601")
    else:
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(minutes=minutes)

    data = await history_store.query(unit_id, var_names, start_dt, end_dt)
    return {
        "unit": unit_id,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "variables": var_names,
        "data": data,
    }


@app.get("/api/v1/history/retention")
async def get_retention():
    """获取历史数据保留天数。"""
    if not history_store:
        raise HTTPException(status_code=503, detail="History store not initialized")
    days = await history_store.get_retention_days()
    return {"retention_days": days}


@app.post("/api/v1/history/retention")
async def set_retention(req: RetentionRequest):
    """设置历史数据保留天数。"""
    if not history_store:
        raise HTTPException(status_code=503, detail="History store not initialized")
    allowed = app_config.get("history", {}).get("allowed_retention_days", [7, 30, 90, 365])
    if req.days not in allowed:
        raise HTTPException(status_code=400, detail=f"Allowed values: {allowed}")
    await history_store.set_retention_days(req.days)
    return {"retention_days": req.days}


# ============================================================
# 报警 API
# ============================================================
@app.get("/api/v1/alarm/definitions")
async def get_alarm_definitions():
    """获取所有 32 位报警定义（用于前端报警指示灯阵列）。"""
    return [
        {
            "bit_index": d.bit_index,
            "symbol": d.symbol,
            "alarm_code": d.alarm_code,
            "level": d.level,
            "color": d.color,
            "forced_ack": d.forced_ack,
            "text": d.text,
        }
        for d in ALARM_DEFINITIONS
    ]


@app.get("/api/v1/alarm/active/{unit_id}")
async def get_active_alarms_api(unit_id: int):
    """获取指定单元当前活动报警列表。"""
    if not alarm_store:
        raise HTTPException(status_code=503, detail="Alarm store not initialized")
    alarms = await alarm_store.get_active_summary(unit_id)
    return {"unit": unit_id, "active_alarms": alarms}


@app.get("/api/v1/alarm/active")
async def get_all_active_alarms():
    """获取所有单元当前活动报警列表。"""
    if not alarm_store:
        raise HTTPException(status_code=503, detail="Alarm store not initialized")
    all_alarms = {}
    for unit_id in plc_clients:
        all_alarms[str(unit_id)] = await alarm_store.get_active_summary(unit_id)
    return {"active_alarms": all_alarms}


@app.get("/api/v1/alarm/events")
async def query_alarm_events(
    unit_id: int = None,
    level: str = None,
    action: str = None,
    start: str = "",
    end: str = "",
    minutes: int = 60,
    limit: int = 100,
):
    """查询报警事件日志。

    Query params:
    - unit_id: 单元过滤（可选）
    - level: 级别过滤（critical/overflow/rhythm/general）
    - action: 动作过滤（trigger/reset/mute）
    - start/end: 时间范围 ISO 格式
    - minutes: 默认查最近 N 分钟
    - limit: 最大返回条数
    """
    if not alarm_store:
        raise HTTPException(status_code=503, detail="Alarm store not initialized")

    if start and end:
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start/end format, use ISO 8601")
    else:
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(minutes=minutes)

    events = await alarm_store.query(
        unit_id=unit_id,
        level=level,
        action=action,
        start=start_dt,
        end=end_dt,
        limit=limit,
    )
    return {
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "count": len(events),
        "events": events,
    }


# ============================================================
# WebSocket 端点
# ============================================================
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket 端点，实时推送 PLC 数据更新。

    前端连接后，可接收以下消息类型：
    - plc_update:    PLC 变量数据更新
    - plc_status:    PLC 连接状态变化
    - plc_alarm:     报警状态更新（活动报警 + 声光状态）

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