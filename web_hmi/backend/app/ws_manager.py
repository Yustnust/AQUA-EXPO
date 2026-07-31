"""
WebSocket 连接管理器
关联 JIRA: AQEX-51

管理所有前端 WebSocket 连接，支持广播 PLC 数据更新。
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket 连接管理器，负责广播数据到所有连接的客户端。"""

    def __init__(self):
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self._connections.add(ws)
        logger.info("WebSocket client connected, total: %d", len(self._connections))

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self._connections.discard(ws)
        logger.info("WebSocket client disconnected, total: %d", len(self._connections))

    async def broadcast(self, message: Dict[str, Any]):
        """广播消息到所有已连接的客户端。"""
        # 序列化一次，避免重复
        try:
            payload = json.dumps(message, ensure_ascii=False, default=str)
        except Exception:
            logger.exception("WebSocket broadcast serialization error")
            return

        disconnected: List[WebSocket] = []
        async with self._lock:
            for ws in list(self._connections):
                try:
                    await ws.send_text(payload)
                except Exception:
                    logger.warning("WebSocket send failed, marking for disconnect")
                    disconnected.append(ws)

        # 清理断开的连接
        for ws in disconnected:
            await self.disconnect(ws)

    @property
    def active_count(self) -> int:
        return len(self._connections)


# 全局 WebSocket 管理器实例
ws_manager = WebSocketManager()


def build_update_message(
    unit_id: int,
    data: Dict[str, Any],
    connected: bool,
) -> Dict[str, Any]:
    """构建 WebSocket 推送消息。"""
    return {
        "type": "plc_update",
        "unit": unit_id,
        "connected": connected,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def build_status_message(
    unit_id: int,
    online: bool,
) -> Dict[str, Any]:
    """构建连接状态变化消息。"""
    return {
        "type": "plc_status",
        "unit": unit_id,
        "online": online,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def build_alarm_message(
    unit_id: int,
    active_alarms: List[Dict[str, Any]],
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """构建报警状态推送消息（含声光联动状态）。"""
    return {
        "type": "plc_alarm",
        "unit": unit_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alarm_code": data.get("alarm_code", 0),
        "alarm_ack_mode": data.get("m_alarm_ack_mode", False),
        "sound_active": data.get("do_alarm_sound", False),
        "light_active": data.get("do_alarm_light", False),
        "mute_done": data.get("sta_mute_done", False),
        "active_alarms": active_alarms,
    }