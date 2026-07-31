"""
报警处理与声光联动
关联 JIRA: AQEX-53

- 解析 VB300~VB303 32位报警字节
- 跟踪报警状态变化（触发/确认/消音/复位）
- 记录报警事件到 SQLite alarms 表
- 提供报警查询与统计 API
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

import aiosqlite

logger = logging.getLogger(__name__)


# ============================================================
# 报警颜色与级别定义
# ============================================================
@dataclass
class AlarmDef:
    """单个报警位定义。"""
    bit_index: int        # 0~31，对应 V300.0~V303.7
    symbol: str           # PLC 符号名
    alarm_code: int       # VW6 报警码
    level: str            # critical / overflow / rhythm / general
    color: str            # CSS 颜色名
    forced_ack: bool      # 是否强制人工确认
    text: str             # HMI 显示文本


# 报警级别 → 前端显示颜色
LEVEL_COLORS = {
    "critical": "#FF0000",   # 红色闪烁（最高级）
    "overflow": "#FF0000",   # 红色（漫溢级）
    "rhythm":   "#FF8C00",   # 橙色（节奏级）
    "general":  "#FFD700",   # 黄色（一般级）
}

# 报警级别优先级（用于排序）
LEVEL_PRIORITY = {"critical": 0, "overflow": 1, "rhythm": 2, "general": 3}


# 32 位报警定义（基于 docs/hmi_preparation/报警字32位解析映射表.md）
ALARM_DEFINITIONS: List[AlarmDef] = [
    # ---- VB300: 高优先级区 ----
    AlarmDef(0,  "M_Alarm_Overflow_AHigh",      10, "overflow",  "#FF0000", True,  "上缸漫溢-立即检查液位计A与进水阀A"),
    AlarmDef(1,  "M_Alarm_Overflow_BHigh",      11, "overflow",  "#FF0000", True,  "下缸漫溢-立即检查液位计B与转移阀B"),
    AlarmDef(2,  "M_Alarm_NCValve_Top",         12, "overflow",  "#FF0000", True,  "上缸NC阀已动作-阀A失效保护触发，检查阀A"),
    AlarmDef(3,  "M_Alarm_NCValve_Bottom",      13, "overflow",  "#FF0000", True,  "下缸NC阀已动作-阀B/液位计B故障保护触发"),
    AlarmDef(4,  "M_EStop_Latch",               14, "overflow",  "#FF0000", True,  "急停触发-现场已急停，等待物理系统复位"),
    AlarmDef(5,  "M_Alarm_SafetyRelay",         99, "critical",  "#FF0000", True,  "安全继电器故障-立即检查动力回路"),
    AlarmDef(6,  "M_Alarm_ScheduleLag",         20, "rhythm",    "#FF8C00", True,  "配液节奏严重滞后-三层纠偏已用尽，请人工介入"),
    AlarmDef(7,  "M_Alarm_ScheduleLag_Warn",    21, "general",   "#FFD700", False, "配液节奏滞后提示-已启用第2层顺延"),

    # ---- VB301: 阀门A类一般故障 ----
    AlarmDef(8,  "M_Alarm_ValveA_CloseFlow",    30, "general",   "#FFD700", False, "阀A关闭后延时验证仍有流-检查阀A内漏"),
    AlarmDef(9,  "M_Alarm_ValveA_Leak",         31, "general",   "#FFD700", False, "阀A内漏-已关但流量计计量值仍增长"),
    AlarmDef(10, "M_Alarm_ValveA_CloseTimeout", 32, "general",   "#FFD700", False, "阀A关到位超时-检查阀A机械或限位"),
    AlarmDef(11, "M_Alarm_ValveA_CloseLeak",    33, "general",   "#FFD700", False, "阀A关到位仍有流-内漏"),
    AlarmDef(12, "M_Alarm_ValveA_OpenTimeout",  34, "general",   "#FFD700", False, "阀A开到位超时-检查阀A机械或限位"),
    AlarmDef(13, "M_Alarm_ValveA_OpenNoFlow",   35, "general",   "#FFD700", False, "阀A开到位但无流-检查上游供水/堵塞"),
    AlarmDef(14, "M_Alarm_ValveA_S1Start",      36, "general",   "#FFD700", False, "S5触发新一轮S1时上缸状态≠空-检查上缸排空"),
    # V301.7 预留，跳过 bit 15

    # ---- VB302: 阀门B/C类一般故障 ----
    AlarmDef(16, "M_Alarm_ValveB_Diag",         40, "general",   "#FFD700", False, "阀B四态诊断异常-检查阀B与液位"),
    AlarmDef(17, "M_Alarm_ValveB_OpenTimeout",  41, "general",   "#FFD700", False, "阀B开到位超时-检查阀B机械或限位"),
    AlarmDef(18, "M_Alarm_ValveB_OpenNoFlow",   42, "general",   "#FFD700", False, "阀B开到位但无流-检查管路"),
    AlarmDef(19, "M_Alarm_ValveB_CloseTimeout", 43, "general",   "#FFD700", False, "阀B关到位超时-检查阀B机械或限位"),
    AlarmDef(20, "M_Alarm_ValveB_CloseLeak",    44, "general",   "#FFD700", False, "阀B关到位但仍有流-内漏"),
    AlarmDef(21, "M_Alarm_ValveC_Diag",         45, "general",   "#FFD700", False, "阀C四态诊断异常-检查阀C与液位"),
    AlarmDef(22, "M_Alarm_ValveC_OpenTimeout",  46, "general",   "#FFD700", False, "阀C开到位超时-检查阀C机械或限位"),
    AlarmDef(23, "M_Alarm_ValveC_OpenNoFlow",   47, "general",   "#FFD700", False, "阀C开到位但无流-检查排水管路"),

    # ---- VB303: 其他一般故障 ----
    AlarmDef(24, "M_Alarm_ValveC_CloseTimeout", 60, "general",   "#FFD700", False, "阀C关到位超时-检查阀C机械或限位"),
    AlarmDef(25, "M_Alarm_ValveC_CloseLeak",    61, "general",   "#FFD700", False, "阀C关到位但仍有流-内漏"),
    AlarmDef(26, "M_Alarm_Pump1_Abnormal",      62, "general",   "#FFD700", False, "潜水泵1启动后超时无流-检查泵1或管路"),
    AlarmDef(27, "M_Alarm_Pump2_Abnormal",      63, "general",   "#FFD700", False, "潜水泵2启动后超时无流-检查泵2或管路"),
    AlarmDef(28, "M_Alarm_SyringePump",         64, "general",   "#FFD700", False, "注射泵通讯/动作异常-检查Modbus与泵状态"),
    AlarmDef(29, "M_Alarm_RTC_Lost",            65, "general",   "#FFD700", False, "RTC时钟丢失-开机时间早于记录，请校时"),
    AlarmDef(30, "M_Alarm_FlowSwitch_Instant",  66, "general",   "#FFD700", False, "流量开关瞬时异常-检查流量开关信号"),
    # V303.7 预留，跳过 bit 31
]

# 快速索引
ALARM_DEF_MAP: Dict[int, AlarmDef] = {d.bit_index: d for d in ALARM_DEFINITIONS}
ALARM_CODE_MAP: Dict[int, AlarmDef] = {d.alarm_code: d for d in ALARM_DEFINITIONS}


def get_alarm_level_color(level: str) -> str:
    """获取报警级别对应的颜色。"""
    return LEVEL_COLORS.get(level, "#FFD700")


def parse_alarm_bits(data: Dict[str, Any]) -> Dict[int, bool]:
    """从 PLC 数据中解析 32 位报警状态。

    :param data: PLC 解析后的数据字典
    :return: {bit_index: is_active}
    """
    bits: Dict[int, bool] = {}
    byte_names = ["alarm_byte_0", "alarm_byte_1", "alarm_byte_2", "alarm_byte_3"]
    for byte_idx, name in enumerate(byte_names):
        byte_val = data.get(name)
        if byte_val is None or not isinstance(byte_val, int):
            continue
        for bit in range(8):
            bit_index = byte_idx * 8 + bit
            bits[bit_index] = bool((byte_val >> bit) & 1)
    return bits


def get_active_alarms(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """获取当前所有活动报警列表。

    :return: 按优先级排序的活动报警列表
    """
    bits = parse_alarm_bits(data)
    active = []
    for bit_index, is_active in bits.items():
        if not is_active:
            continue
        alarm_def = ALARM_DEF_MAP.get(bit_index)
        if not alarm_def:
            continue
        active.append({
            "bit_index": bit_index,
            "symbol": alarm_def.symbol,
            "alarm_code": alarm_def.alarm_code,
            "level": alarm_def.level,
            "color": alarm_def.color,
            "forced_ack": alarm_def.forced_ack,
            "text": alarm_def.text,
        })
    active.sort(key=lambda a: LEVEL_PRIORITY.get(a["level"], 99))
    return active


# ============================================================
# 报警事件记录器
# ============================================================
class AlarmStore:
    """报警事件 SQLite 存储。"""

    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path
        # 每个单元的上一轮报警位状态，用于检测变化
        self._prev_bits: Dict[int, Dict[int, bool]] = {}
        # 每个单元的消音状态
        self._muted: Dict[int, bool] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def initialize(self):
        """初始化 alarms 表。"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS alarms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    alarm_code INTEGER NOT NULL,
                    bit_index INTEGER NOT NULL,
                    level TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    alarm_text TEXT NOT NULL,
                    action TEXT NOT NULL,
                    ts TIMESTAMP NOT NULL DEFAULT (datetime('now'))
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_alarms_unit_ts
                ON alarms(unit_id, ts)
            """)
            await db.commit()
        logger.info("Alarm store initialized")

    async def process(self, unit_id: int, data: Dict[str, Any]):
        """处理一轮 PLC 数据，检测报警状态变化并记录事件。

        同时跟踪声光报警器状态（Q0.7 声音、Q2.0 灯光）。
        """
        bits = parse_alarm_bits(data)
        prev = self._prev_bits.get(unit_id, {})
        ts = datetime.now(timezone.utc).isoformat()

        events = []

        # 检测报警位变化
        for bit_index, is_active in bits.items():
            was_active = prev.get(bit_index, False)
            if is_active and not was_active:
                # 新报警触发
                alarm_def = ALARM_DEF_MAP.get(bit_index)
                if alarm_def:
                    events.append((unit_id, alarm_def.alarm_code, bit_index,
                                   alarm_def.level, alarm_def.symbol, alarm_def.text,
                                   "trigger", ts))
            elif not is_active and was_active:
                # 报警复位
                alarm_def = ALARM_DEF_MAP.get(bit_index)
                if alarm_def:
                    events.append((unit_id, alarm_def.alarm_code, bit_index,
                                   alarm_def.level, alarm_def.symbol, alarm_def.text,
                                   "reset", ts))

        # 检测消音状态变化
        sound_on = data.get("sta_mute_done", False)
        was_muted = self._muted.get(unit_id, False)
        if sound_on and not was_muted:
            events.append((unit_id, 0, -1, "info", "SYSTEM", "消音已执行", "mute", ts))
        self._muted[unit_id] = sound_on

        # 保存当前状态
        self._prev_bits[unit_id] = bits

        # 批量写入事件
        if events:
            await self._insert_events(events)

    async def _insert_events(self, events: List[tuple]):
        """批量插入报警事件。"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.executemany(
                    """INSERT INTO alarms (unit_id, alarm_code, bit_index, level, symbol, alarm_text, action, ts)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    events,
                )
                await db.commit()
        except Exception:
            logger.exception("Alarm event insert error")

    async def query(self,
                    unit_id: Optional[int] = None,
                    level: Optional[str] = None,
                    action: Optional[str] = None,
                    start: Optional[datetime] = None,
                    end: Optional[datetime] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """查询报警事件。

        :param unit_id: 单元过滤（None=全部）
        :param level: 级别过滤
        :param action: 动作过滤（trigger/ack/mute/reset）
        :param start: 开始时间
        :param end: 结束时间
        :param limit: 最大返回条数
        """
        conditions = []
        params: List[Any] = []

        if unit_id is not None:
            conditions.append("unit_id = ?")
            params.append(unit_id)
        if level:
            conditions.append("level = ?")
            params.append(level)
        if action:
            conditions.append("action = ?")
            params.append(action)
        if start:
            conditions.append("ts >= ?")
            params.append(start.isoformat())
        if end:
            conditions.append("ts <= ?")
            params.append(end.isoformat())

        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        params.append(limit)

        result = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    f"""SELECT id, unit_id, alarm_code, bit_index, level, symbol, alarm_text, action, ts
                        FROM alarms {where}
                        ORDER BY ts DESC LIMIT ?""",
                    params,
                )
                rows = await cursor.fetchall()
                for row in rows:
                    result.append(dict(row))
        except Exception:
            logger.exception("Alarm query error")

        return result

    async def get_active_summary(self, unit_id: int) -> List[Dict[str, Any]]:
        """获取指定单元当前活动报警摘要（基于最近一次记录的状态）。"""
        bits = self._prev_bits.get(unit_id, {})
        active = []
        for bit_index, is_active in bits.items():
            if not is_active:
                continue
            alarm_def = ALARM_DEF_MAP.get(bit_index)
            if not alarm_def:
                continue
            active.append({
                "bit_index": bit_index,
                "symbol": alarm_def.symbol,
                "alarm_code": alarm_def.alarm_code,
                "level": alarm_def.level,
                "color": alarm_def.color,
                "forced_ack": alarm_def.forced_ack,
                "text": alarm_def.text,
            })
        active.sort(key=lambda a: LEVEL_PRIORITY.get(a["level"], 99))
        return active

    async def start(self):
        """启动报警存储（预留后台任务）。"""
        self._running = True
        logger.info("Alarm store started")

    async def stop(self):
        """停止报警存储。"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Alarm store stopped")