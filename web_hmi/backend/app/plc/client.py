"""
Modbus TCP 客户端
负责与 S7-200 SMART PLC 建立连接、轮询读取、写入命令
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException

from .registers import READ_BLOCKS, VARIABLES, VARIABLE_MAP, DataType, RegisterDef
from .parser import parse_all, encode_value, encode_float32, encode_int32

logger = logging.getLogger(__name__)


class PlcClient:
    """S7-200 SMART Modbus TCP 客户端。"""

    def __init__(
        self,
        host: str,
        port: int = 502,
        unit_id: int = 1,
        poll_interval: float = 0.5,
        reconnect_interval: float = 3.0,
        timeout: float = 1.0,
        max_failures: int = 5,
        on_data: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_status: Optional[Callable[[bool], None]] = None,
    ):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.poll_interval = poll_interval
        self.reconnect_interval = reconnect_interval
        self.timeout = timeout
        self.max_failures = max_failures
        self.on_data = on_data
        self.on_status = on_status

        self._client: Optional[ModbusTcpClient] = None
        self._connected = False
        self._failures = 0
        self._latest_data: Dict[str, Any] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

        # 写队列，避免写操作与轮询冲突
        self._write_queue: asyncio.Queue = asyncio.Queue()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def latest_data(self) -> Dict[str, Any]:
        return self._latest_data.copy()

    async def start(self):
        """启动轮询任务。"""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("PLC client started: %s:%s", self.host, self.port)

    async def stop(self):
        """停止轮询任务并断开连接。"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False
        logger.info("PLC client stopped")

    async def _poll_loop(self):
        """主轮询循环：连接、读取、处理写入队列、断线重连。"""
        while self._running:
            try:
                if not self._connected:
                    await self._connect()
                    if not self._connected:
                        await asyncio.sleep(self.reconnect_interval)
                        continue

                # 批量读取所有寄存器块
                registers = await self._read_all_blocks()
                if registers is not None:
                    data = parse_all(registers)
                    self._latest_data = data
                    self._failures = 0
                    if self.on_data:
                        try:
                            self.on_data(data)
                        except Exception:
                            logger.exception("on_data callback error")
                else:
                    self._failures += 1
                    if self._failures >= self.max_failures:
                        logger.warning("PLC communication failure count %d, disconnect", self._failures)
                        self._set_connected(False)

                # 处理写入队列（每次轮询最多处理 5 条，避免阻塞读取）
                for _ in range(min(5, self._write_queue.qsize())):
                    if not self._connected:
                        break
                    try:
                        write_item = self._write_queue.get_nowait()
                        await self._execute_write(write_item)
                    except asyncio.QueueEmpty:
                        break

                await asyncio.sleep(self.poll_interval)

            except Exception:
                logger.exception("Unexpected error in poll loop")
                self._set_connected(False)
                await asyncio.sleep(self.reconnect_interval)

    async def _connect(self) -> bool:
        """尝试连接 PLC（同步调用放到线程池，避免阻塞事件循环）。"""
        try:
            if self._client:
                self._client.close()
            self._client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout,
            )
            ok = await asyncio.to_thread(self._client.connect)
            self._set_connected(bool(ok))
            if ok:
                logger.info("Connected to PLC %s:%s", self.host, self.port)
                self._failures = 0
            else:
                logger.warning("Failed to connect PLC %s:%s", self.host, self.port)
            return bool(ok)
        except Exception:
            logger.exception("PLC connect error")
            self._set_connected(False)
            return False

    def _set_connected(self, status: bool):
        if self._connected != status:
            self._connected = status
            logger.info("PLC connection status: %s", "online" if status else "offline")
            if self.on_status:
                try:
                    self.on_status(status)
                except Exception:
                    logger.exception("on_status callback error")

    async def _read_all_blocks(self) -> Optional[Dict[int, int]]:
        """读取所有寄存器块（同步调用放到线程池，避免阻塞事件循环）。"""
        if not self._client:
            return None

        registers: Dict[int, int] = {}
        try:
            for block in READ_BLOCKS:
                start_v = block["start_v"]
                end_v = block["end_v"]
                start_addr = start_v // 2
                count = (end_v - start_v) // 2 + 1

                resp = await asyncio.to_thread(
                    self._client.read_holding_registers,
                    address=start_addr,
                    count=count,
                    slave=self.unit_id,
                )
                if resp is None or resp.isError():
                    logger.warning("Read holding registers error: start=%s count=%s", start_addr, count)
                    return None

                for i, val in enumerate(resp.registers):
                    registers[start_addr + i] = val

            return registers
        except ModbusIOException as e:
            logger.warning("Modbus IO error: %s", e)
            return None
        except Exception:
            logger.exception("Read registers error")
            return None

    async def write_variable(self, name: str, value: Any) -> bool:
        """异步写入单个变量（入队，由轮询线程执行）。"""
        var = VARIABLE_MAP.get(name)
        if not var:
            logger.error("Unknown variable: %s", name)
            return False
        if not var.writable:
            logger.error("Variable not writable: %s", name)
            return False
        await self._write_queue.put({"name": name, "value": value})
        return True

    async def _execute_write(self, item: Dict[str, Any]):
        """执行实际的 Modbus 写入。"""
        name = item["name"]
        value = item["value"]
        var = VARIABLE_MAP[name]

        if not self._client or not self._connected:
            logger.warning("Skip write %s: not connected", name)
            return

        try:
            if var.dtype in (DataType.BOOL, DataType.INT16, DataType.UINT16):
                # 位变量需要先读-改-写
                if var.dtype == DataType.BOOL:
                    read_resp = await asyncio.to_thread(
                        self._client.read_holding_registers,
                        address=var.reg_addr, count=1, slave=self.unit_id
                    )
                    if read_resp is None or read_resp.isError():
                        logger.warning("Read before write failed: %s", name)
                        return
                    current_word = read_resp.registers[0]
                else:
                    current_word = 0

                new_word = encode_value(var, current_word, value)
                resp = await asyncio.to_thread(
                    self._client.write_register,
                    address=var.reg_addr, value=new_word, slave=self.unit_id
                )
                if resp is None or resp.isError():
                    logger.warning("Write register error: %s", name)
                else:
                    logger.info("Written %s = %s", name, value)

            elif var.dtype == DataType.FLOAT32:
                regs = encode_float32(value)
                resp = await asyncio.to_thread(
                    self._client.write_registers,
                    address=var.reg_addr, values=regs, slave=self.unit_id
                )
                if resp is None or resp.isError():
                    logger.warning("Write registers error: %s", name)
                else:
                    logger.info("Written %s = %s", name, value)

            elif var.dtype == DataType.INT32:
                regs = encode_int32(value)
                resp = await asyncio.to_thread(
                    self._client.write_registers,
                    address=var.reg_addr, values=regs, slave=self.unit_id
                )
                if resp is None or resp.isError():
                    logger.warning("Write registers error: %s", name)
                else:
                    logger.info("Written %s = %s", name, value)

            else:
                logger.warning("Write not implemented for type %s: %s", var.dtype, name)

        except Exception:
            logger.exception("Write variable error: %s", name)

    async def write_bit_pulse(self, name: str, duration: float = 0.5):
        """
        写入位变量脉冲（置位 -> 等待 -> 复位）。
        适用于启动/停止/消音等命令位。
        """
        await self.write_variable(name, True)
        await asyncio.sleep(duration)
        await self.write_variable(name, False)
