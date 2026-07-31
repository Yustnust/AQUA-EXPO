"""
SQLite 历史数据记录与查询
关联 JIRA: AQEX-52

- 按变量分组采样（快采样 1s、慢采样 10s）
- 客户可配置保留时长（默认 30 天）
- 定时清理超期数据
- 支持按单元、变量、时间范围查询趋势
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import aiosqlite

from app.plc import VARIABLES, VARIABLE_MAP

logger = logging.getLogger(__name__)

# 快采样变量（1s 周期，需高频记录）
FAST_SAMPLE_VARS = [
    "state_machine",
    "alarm_code",
    "alarm_byte_0", "alarm_byte_1", "alarm_byte_2", "alarm_byte_3",
    "flowrate_instant",
    "current_inlet_volume",
    "flowmeter_current",
    "sta_tank_a_state", "sta_tank_b_state",
    "pump_status",
]

# 慢采样变量（10s 周期，变化缓慢的参数）
SLOW_SAMPLE_VARS = [
    "c_set", "c_stock",
    "round_count",
    "s1_actual", "s4_actual", "s6_actual",
    "s5_elapsed",
    "t_rolling", "s6_rolling",
    "s2_target", "resttime_target",
    "available", "corr_needed",
    "s3_estimate",
    "experiment_duration_accum",
    "dose_steps",
    "vol_target",
    "corr_mode", "corr_result",
    "leak_diff", "target_inlet_volume",
    "flowmeter_close_snapshot",
    "flowmeter_snapshot",
]


class HistoryStore:
    """SQLite 历史数据存储。"""

    def __init__(self, db_path: str = "data/history.db",
                 retention_days: int = 30,
                 fast_interval: int = 1,
                 slow_interval: int = 10):
        self.db_path = db_path
        self.retention_days = retention_days
        self.fast_interval = fast_interval
        self.slow_interval = slow_interval
        self._last_fast: Dict[int, float] = {}
        self._last_slow: Dict[int, float] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def initialize(self):
        """初始化数据库，创建表结构。"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_id INTEGER NOT NULL,
                    var_name TEXT NOT NULL,
                    value REAL,
                    ts TIMESTAMP NOT NULL DEFAULT (datetime('now'))
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_unit_ts
                ON history(unit_id, ts)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_var_ts
                ON history(var_name, ts)
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS history_config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            await db.execute("""
                INSERT OR IGNORE INTO history_config (key, value)
                VALUES ('retention_days', ?)
            """, (str(self.retention_days),))
            await db.commit()
        logger.info("History database initialized: %s", self.db_path)

    async def record(self, unit_id: int, data: Dict[str, Any]):
        """根据采样策略决定是否记录当前轮数据。"""
        now = time.monotonic()

        # 快采样
        last_fast = self._last_fast.get(unit_id, 0)
        if now - last_fast >= self.fast_interval:
            self._last_fast[unit_id] = now
            await self._insert_batch(unit_id, data, FAST_SAMPLE_VARS)

        # 慢采样
        last_slow = self._last_slow.get(unit_id, 0)
        if now - last_slow >= self.slow_interval:
            self._last_slow[unit_id] = now
            await self._insert_batch(unit_id, data, SLOW_SAMPLE_VARS)

    async def _insert_batch(self, unit_id: int, data: Dict[str, Any], var_names: List[str]):
        """批量插入一组变量的历史记录。"""
        ts = datetime.now(timezone.utc).isoformat()
        rows = []
        for name in var_names:
            val = data.get(name)
            if val is None:
                continue
            if isinstance(val, bool):
                val = 1.0 if val else 0.0
            elif isinstance(val, (int, float)):
                val = float(val)
            else:
                continue
            rows.append((unit_id, name, val, ts))

        if not rows:
            return

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.executemany(
                    "INSERT INTO history (unit_id, var_name, value, ts) VALUES (?, ?, ?, ?)",
                    rows,
                )
                await db.commit()
        except Exception:
            logger.exception("History insert error")

    async def query(self,
                    unit_id: int,
                    var_names: List[str],
                    start: datetime,
                    end: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """查询指定单元、变量、时间范围的历史数据。

        :return: {var_name: [{"ts": "...", "value": 1.23}, ...]}
        """
        result: Dict[str, List[Dict[str, Any]]] = {name: [] for name in var_names}

        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                placeholders = ",".join("?" * len(var_names))
                cursor = await db.execute(
                    f"""SELECT var_name, value, ts FROM history
                        WHERE unit_id = ? AND var_name IN ({placeholders})
                        AND ts >= ? AND ts <= ?
                        ORDER BY ts ASC""",
                    (unit_id, *var_names, start.isoformat(), end.isoformat()),
                )
                rows = await cursor.fetchall()
                for row in rows:
                    var_name = row["var_name"]
                    if var_name in result:
                        result[var_name].append({
                            "ts": row["ts"],
                            "value": row["value"],
                        })
        except Exception:
            logger.exception("History query error")

        return result

    async def get_recent_data(self, unit_id: int, minutes: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """获取最近 N 分钟的历史数据（所有变量）。"""
        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=minutes)
        all_vars = list(set(FAST_SAMPLE_VARS + SLOW_SAMPLE_VARS))
        return await self.query(unit_id, all_vars, start, end)

    async def cleanup(self):
        """清理超期数据。"""
        cut_off = (datetime.now(timezone.utc) - timedelta(days=self.retention_days)).isoformat()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("DELETE FROM history WHERE ts < ?", (cut_off,))
                deleted = cursor.rowcount
                await db.commit()
                if deleted > 0:
                    logger.info("History cleanup: deleted %d records before %s", deleted, cut_off)
        except Exception:
            logger.exception("History cleanup error")

    async def get_retention_days(self) -> int:
        """获取当前保留天数设置。"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT value FROM history_config WHERE key = 'retention_days'")
                row = await cursor.fetchone()
                if row:
                    return int(row[0])
        except Exception:
            logger.exception("Get retention_days error")
        return self.retention_days

    async def set_retention_days(self, days: int):
        """设置保留天数。"""
        self.retention_days = days
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO history_config (key, value) VALUES ('retention_days', ?)",
                    (str(days),),
                )
                await db.commit()
        except Exception:
            logger.exception("Set retention_days error")

    async def start(self):
        """启动历史记录任务（定时清理）。"""
        self._running = True
        self._task = asyncio.create_task(self._cleanup_loop())
        logger.info("History store started, retention: %d days", self.retention_days)

    async def stop(self):
        """停止历史记录任务。"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("History store stopped")

    async def _cleanup_loop(self):
        """定时清理超期数据（每小时执行一次）。"""
        while self._running:
            try:
                await self.cleanup()
            except Exception:
                logger.exception("History cleanup loop error")
            await asyncio.sleep(3600)  # 1 小时


def get_available_trend_variables() -> List[Dict[str, Any]]:
    """获取所有支持趋势曲线的变量列表。"""
    all_vars = list(set(FAST_SAMPLE_VARS + SLOW_SAMPLE_VARS))
    result = []
    for name in all_vars:
        var = VARIABLE_MAP.get(name)
        if var:
            result.append({
                "name": name,
                "note": var.note,
                "dtype": var.dtype.value,
                "group": "fast" if name in FAST_SAMPLE_VARS else "slow",
            })
    return result