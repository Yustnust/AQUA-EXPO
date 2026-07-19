"""
药液配置加注控制系统 — S7协议服务端 v1.0

功能: 为PLC仿真器提供S7comm协议服务端,让MCGS等HMI客户端可
     通过以太网(S7协议)连接仿真器,实现无硬件HMI-PLC联调。

架构:
  - 单进程多线程
  - 8端口监听 (TCP 10200~10207, 对应8台PLC)
  - 每端口绑定独立PLCSim实例
  - 每连接独立线程处理
  - 周期扫描线程驱动PLC逻辑(100ms/周期)

协议栈:
  TCP (102)
    └─ TPKT (RFC 1006)
        └─ COTP (ISO 8073)
            └─ S7comm
                ├─ 连接建立 (Connect Request/Confirm)
                ├─ 读变量 (Read Request/Response)
                └─ 写变量 (Write Request/Response)

支持S7协议特性:
  - PDU大小协商 (480字节, S7-200 SMART标准)
  - V区读写 (VB/VW/VD/V位 通过字节偏移+位偏移+长度访问)
  - I/Q区读取 (按字节偏移)
  - 定时器/计数器读取 (返回0, 仿真器不支持)
  - 多客户端并发 (每端口支持≤4连接)

用法:
  # 启动8端口S7服务端
  python s7_server.py

  # MCGS侧配置:
  # - 8个S7连接, IP=127.0.0.1, 端口=10200~10207
  # - 机架=0, 槽=1
  # - TSAP自动协商

依赖:
  - plc_simulator.PLCSim (仿真器核心)
  - Python 3.8+ 标准库 (socket, threading, struct)

参考:
  - Siemens S7 Communication Protocol Specification
  - ISO-on-TCP (RFC 1006)
  - S7-200 SMART System Manual
"""

import socket
import threading
import struct
import time
import logging
from typing import Optional, Tuple, Dict
from plc_simulator import PLCSim

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("S7Server")


# ============================================================
# 协议常量
# ============================================================

# TPKT 头 (RFC 1006)
# 版本=3, 长度=总长度(含TPKT头4字节)

# COTP (ISO 8073)
COTP_CONNECT_REQUEST = 0xE0  # 连接请求
COTP_CONNECT_CONFIRM = 0xD0  # 连接确认
COTP_DATA = 0xF0              # 数据传输

# S7comm 头
S7_PROTOCOL_ID = 0x32
S7_JOB = 1                    # Job (请求)
S7_ACK = 2                    # Ack (确认)
S7_ACK_DATA = 3               # Ack-Data (响应)

# S7comm 功能码
S7_FUNC_READ = 0x04           # 读变量
S7_FUNC_WRITE = 0x05          # 写变量
S7_FUNC_SETUP = 0x28          # 通信参数协商
S7_FUNC_USERDATA = 0x07       # 用户数据(时钟等)

# S7 数据区 (Area)
S7_AREA_PE = 0x01   # 过程输入 (I区)
S7_AREA_PA = 0x02   # 过程输出 (Q区)
S7_AREA_MK = 0x03   # M区 (标志位)
S7_AREA_TM = 0x1D   # 定时器
S7_AREA_CT = 0x1C   # 计数器
S7_AREA_DB = 0x85   # 数据块 (V区在S7-200 SMART用DB1)
S7_AREA_VA = 0x84   # 直接V区 (S7-300/400风格)

# S7-200 SMART V区通过DB1访问
# V区字节偏移 = DB号(1) × 1 + 字节偏移
# 简化: 直接用Area=DB, DBNumber=1, ByteOffset=V区字节地址

# PDU大小
PDU_SIZE = 480  # S7-200 SMART标准PDU


class S7ProtocolError(Exception):
    """S7协议错误"""
    pass


class S7Connection:
    """单个S7连接处理器

    每个TCP连接创建一个S7Connection实例,在独立线程中运行。
    """

    def __init__(self, client_sock: socket.socket, client_addr, plc: PLCSim, unit_id: int):
        self.sock = client_sock
        self.addr = client_addr
        self.plc = plc
        self.unit_id = unit_id
        self.local_tsap = 0x0100  # 本地TSAP (服务端)
        self.remote_tsap = 0x0200  # 远程TSAP (客户端)
        self.pdu_size = PDU_SIZE
        self.connected = False
        self.running = True
        self.lock = threading.Lock()  # 保护PLC访问

    # ------------------------------------------------------------
    # 主循环
    # ------------------------------------------------------------

    def run(self):
        """连接处理主循环"""
        try:
            logger.info(f"[U{self.unit_id}] 客户端连接: {self.addr}")
            while self.running:
                # 1. 接收TPKT+COTP+S7帧
                frame = self._recv_tpkt()
                if frame is None:
                    break

                # 2. 解析COTP
                cotp_type, cotp_payload = self._parse_cotp(frame)
                if cotp_type is None:
                    logger.warning(f"[U{self.unit_id}] COTP解析失败")
                    break

                # 3. 分发处理
                if cotp_type == COTP_CONNECT_REQUEST:
                    self._handle_connect_request(cotp_payload)
                elif cotp_type == COTP_DATA:
                    self._handle_data(cotp_payload)
                else:
                    logger.warning(f"[U{self.unit_id}] 未知COTP类型: 0x{cotp_type:02X}")

        except ConnectionResetError:
            logger.info(f"[U{self.unit_id}] 客户端断开(连接重置)")
        except Exception as e:
            logger.error(f"[U{self.unit_id}] 连接异常: {e}", exc_info=True)
        finally:
            self.sock.close()
            logger.info(f"[U{self.unit_id}] 连接关闭: {self.addr}")

    def stop(self):
        self.running = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self.sock.close()

    # ------------------------------------------------------------
    # TPKT层 (RFC 1006)
    # ------------------------------------------------------------

    def _recv_tpkt(self) -> Optional[bytes]:
        """接收一个完整TPKT帧

        TPKT头格式 (4字节):
          byte 0: 版本 (0x03)
          byte 1: 保留 (0x00)
          byte 2-3: 总长度 (大端, 含4字节头)
        """
        # 接收4字节头
        header = self._recv_exact(4)
        if header is None:
            return None

        if header[0] != 0x03:
            logger.warning(f"[U{self.unit_id}] TPKT版本错误: 0x{header[0]:02X}")
            return None

        total_len = struct.unpack('>H', header[2:4])[0]
        if total_len < 4:
            return None

        # 接收剩余数据
        body = self._recv_exact(total_len - 4)
        if body is None:
            return None

        return header + body

    def _recv_exact(self, n: int) -> Optional[bytes]:
        """精确接收n字节"""
        data = bytearray()
        while len(data) < n:
            try:
                chunk = self.sock.recv(n - len(data))
                if not chunk:
                    return None
                data.extend(chunk)
            except socket.timeout:
                return None
            except OSError:
                return None
        return bytes(data)

    def _send_tpkt(self, payload: bytes):
        """发送TPKT+COTP帧"""
        total_len = 4 + len(payload)
        frame = struct.pack('>BBH', 0x03, 0x00, total_len) + payload
        try:
            self.sock.sendall(frame)
        except OSError as e:
            logger.warning(f"[U{self.unit_id}] 发送失败: {e}")

    # ------------------------------------------------------------
    # COTP层 (ISO 8073)
    # ------------------------------------------------------------

    def _parse_cotp(self, frame: bytes) -> Tuple[Optional[int], bytes]:
        """解析COTP层

        返回 (COTP类型, 负载)
        COTP类型: 0xE0=连接请求, 0xD0=连接确认, 0xF0=数据
        """
        if len(frame) < 5:
            return None, b''

        # 跳过4字节TPKT头
        cotp = frame[4:]

        if len(cotp) < 2:
            return None, b''

        length = cotp[0]      # COTP头长度(不含length字节本身)
        pdu_type = cotp[1]    # PDU类型(高4位) + credit(低4位)

        # 数据传输 PDU
        if pdu_type == COTP_DATA:
            # 长度字段后就是数据
            return COTP_DATA, cotp[2:]

        # 连接请求/确认 PDU
        elif (pdu_type & 0xF0) == COTP_CONNECT_REQUEST:
            return COTP_CONNECT_REQUEST, cotp[2:]

        elif (pdu_type & 0xF0) == COTP_CONNECT_CONFIRM:
            return COTP_CONNECT_CONFIRM, cotp[2:]

        else:
            return None, b''

    def _handle_connect_request(self, payload: bytes):
        """处理COTP连接请求, 返回连接确认"""
        # 解析连接请求中的TSAP
        # 简化: 直接回连接确认, 不严格校验TSAP
        # payload结构: [dst-ref(2)] [src-ref(2)] [class(1)] [可选参数]

        # 构建连接确认
        # COTP CC格式:
        #   length(1) + PDU类型(1) + dst-ref(2) + src-ref(2) + class(1)
        #   + 可选参数 (TPDU Size等)
        dst_ref = payload[0:2] if len(payload) >= 2 else b'\x00\x00'
        src_ref = payload[2:4] if len(payload) >= 4 else b'\x00\x01'

        # COTP CC负载
        cc_payload = (
            dst_ref +                           # 目标引用(回传客户端src-ref)
            src_ref +                           # 源引用(回传客户端dst-ref)
            b'\x00' +                           # class 0
            b'\xC0\x01\x0B' +                   # 参数: TPDU Size=1024 (0x0B)
            b'\xC1\x02\x01\x00' +               # 参数: src-TSAP=0x0100
            b'\xC2\x02\x02\x00'                 # 参数: dst-TSAP=0x0200
        )
        cc_length = len(cc_payload)
        cc = bytes([cc_length, COTP_CONNECT_CONFIRM]) + cc_payload

        self._send_tpkt(cc)
        self.connected = True
        logger.debug(f"[U{self.unit_id}] COTP连接确认已发送")

    # ------------------------------------------------------------
    # S7comm层
    # ------------------------------------------------------------

    def _handle_data(self, cotp_payload: bytes):
        """处理COTP数据传输PDU (内含S7comm)

        _parse_cotp对DATA类型返回cotp[2:], 即已跳过length(1) + 0xF0(1),
        剩余 [0x80] + S7comm数据。
        """
        if len(cotp_payload) < 2:
            return

        # cotp_payload[0] 应为 0x80 (EOT标志, 表示单包完整数据)
        # 跳过该字节, 取S7comm数据
        if cotp_payload[0] == 0x80:
            s7_data = cotp_payload[1:]
        elif cotp_payload[0] == 0xF0:
            # 兼容: _parse_cotp返回包含0xF0 0x80的情况
            s7_data = cotp_payload[2:] if len(cotp_payload) > 2 else b''
        else:
            s7_data = cotp_payload[1:] if len(cotp_payload) > 1 else b''

        if len(s7_data) < 10:
            logger.warning(f"[U{self.unit_id}] S7帧过短: {len(s7_data)}字节")
            return

        # 解析S7头
        # S7头格式 (10~12字节):
        #   0: Protocol ID (0x32)
        #   1: ROSCTR (Job=1, Ack=2, Ack-Data=3)
        #   2-3: Reserved (0x0000)
        #   4-5: PDU Reference (递增)
        #   6-7: Parameter length
        #   8-9: Data length
        #   10+: 参数字段

        proto_id = s7_data[0]
        rosctr = s7_data[1]

        if proto_id != S7_PROTOCOL_ID:
            logger.warning(f"[U{self.unit_id}] 非S7协议: 0x{proto_id:02X}")
            return

        reserved = struct.unpack('>H', s7_data[2:4])[0]
        pdu_ref = struct.unpack('>H', s7_data[4:6])[0]
        param_len = struct.unpack('>H', s7_data[6:8])[0]
        data_len = struct.unpack('>H', s7_data[8:10])[0]

        param_field = s7_data[10:10 + param_len]
        data_field = s7_data[10 + param_len:10 + param_len + data_len]

        if rosctr == S7_JOB:
            self._handle_job(pdu_ref, param_field, data_field)
        else:
            logger.warning(f"[U{self.unit_id}] 未知ROSCTR: {rosctr}")

    def _handle_job(self, pdu_ref: int, param: bytes, data: bytes):
        """处理S7 Job请求"""
        if len(param) < 1:
            return

        func = param[0]

        if func == S7_FUNC_SETUP:
            # 通信参数协商
            self._handle_setup(pdu_ref, param, data)
        elif func == S7_FUNC_READ:
            # 读变量
            self._handle_read(pdu_ref, param)
        elif func == S7_FUNC_WRITE:
            # 写变量
            self._handle_write(pdu_ref, param, data)
        else:
            logger.warning(f"[U{self.unit_id}] 未支持的功能码: 0x{func:02X}")
            self._send_error_ack(pdu_ref, 0x85)

    def _handle_setup(self, pdu_ref: int, param: bytes, data: bytes):
        """处理通信参数协商 (功能码0x28)

        客户端发送Setup Communication, 协商PDU大小等参数。
        服务端回Ack-Data, 接受客户端参数或返回自己的参数。
        """
        # 简化: 接受客户端参数, 回固定PDU=480
        # 构建响应
        # Ack-Data头: protocol=0x32, rosctr=3, reserved, pdu_ref, param_len, data_len
        # 参数: 0x28, 0x00, 0x01, 0x00 (功能码, 0, max amq caller=1, max amq callee=0)
        # 数据: 0x00, 0x0E, 0x01, 0xE0, 0x01, 0xE0 (pdu length=480)

        param_resp = bytes([S7_FUNC_SETUP, 0x00, 0x01, 0x00])
        # PDU size 480 = 0x01E0
        data_resp = bytes([0x00, 0x0E, 0x01, 0xE0, 0x01, 0xE0])

        self._send_ack_data(pdu_ref, param_resp, data_resp)
        logger.debug(f"[U{self.unit_id}] Setup完成, PDU={self.pdu_size}")

    def _handle_read(self, pdu_ref: int, param: bytes):
        """处理读变量请求 (功能码0x04)

        参数格式 (1+ItemCount + Items):
          byte 0: 功能码 (0x04)
          byte 1: item count
          byte 2+: 每个item 12字节

        Item格式 (12字节):
          byte 0: ItemHeader (0x12)
          byte 1: ItemType (0x0A variable spec)
          byte 2: LengthOfRead (字节数)
          byte 3: DB Number (0=直接, 1=DB1即V区)
          byte 4: Area Type (0x84=直接, 0x85=DB)
          byte 5-7: Address (byte offset, 24位)
        """
        if len(param) < 2:
            self._send_error_ack(pdu_ref, 0x85)
            return

        item_count = param[1]
        items = []
        offset = 2
        for i in range(item_count):
            if offset + 12 > len(param):
                break
            item = param[offset:offset + 12]
            items.append(item)
            offset += 12

        # 构建响应数据
        response_data = b''
        for item in items:
            data_item = self._read_item(item)
            response_data += data_item

        # 构建响应参数
        param_resp = bytes([S7_FUNC_READ, item_count])

        self._send_ack_data(pdu_ref, param_resp, response_data)

    def _read_item(self, item: bytes) -> bytes:
        """读取单个item, 返回响应data-item

        响应item格式:
          byte 0: ReturnCode (0xFF=success)
          byte 1: TransportSize (0x09=byte, 0x04=word, 0x06=dword, 0x03=bit)
          byte 2-3: Length (字节数, 不含bit偏移)
          byte 4+: 数据
        """
        if len(item) < 12:
            return bytes([0x85, 0x00, 0x00, 0x00])  # error

        item_header = item[0]      # 0x12
        item_type = item[1]        # 0x0A
        read_len = item[2]         # 读取字节数
        db_number = item[3]        # DB号
        area = item[4]             # 区域类型
        addr_bytes = item[5:8]     # 24位地址(字节偏移)
        byte_addr = (addr_bytes[0] << 16) | (addr_bytes[1] << 8) | addr_bytes[2]

        # 在S7-200 SMART中, V区通过DB1访问 (area=0x85, db=1)
        # 也可能直接用area=0x84 (DB) 访问

        try:
            with self.lock:
                data = self._read_plc_area(area, db_number, byte_addr, read_len)

            # 返回码: 0xFF=成功
            return_code = 0xFF
            # 传输尺寸: 0x09=BYTE (简化, 都按字节返回)
            transport_size = 0x09
            length = read_len

            return bytes([return_code, transport_size]) + struct.pack('>H', length) + data

        except Exception as e:
            logger.warning(f"[U{self.unit_id}] 读取失败 area=0x{area:02X} db={db_number} addr={byte_addr}: {e}")
            return bytes([0x85, 0x00, 0x00, 0x00])

    def _read_plc_area(self, area: int, db_number: int, byte_addr: int, length: int) -> bytes:
        """从PLC读取指定区域数据

        area:
          0x85 (DB) + db=1 → V区
          0x84 → V区(S7-200 SMART兼容)
          0x01 (PE) → I区
          0x02 (PA) → Q区
          0x03 (MK) → M区
        """
        data = bytearray()

        for i in range(length):
            addr = byte_addr + i

            if area in (S7_AREA_DB, S7_AREA_VA) and db_number in (0, 1):
                # V区
                data.append(self.plc.get_vb(addr) & 0xFF)

            elif area == S7_AREA_PE:
                # I区 (过程输入)
                byte_idx = addr
                bit_idx = 0
                val = 0
                for b in range(8):
                    if self.plc.i.get((byte_idx, b), False):
                        val |= (1 << b)
                data.append(val)

            elif area == S7_AREA_PA:
                # Q区 (过程输出)
                val = 0
                for b in range(8):
                    if self.plc.q.get((addr, b), False):
                        val |= (1 << b)
                data.append(val)

            elif area == S7_AREA_MK:
                # M区
                val = 0
                for b in range(8):
                    if self.plc.m.get((addr, b), False):
                        val |= (1 << b)
                data.append(val)

            else:
                # 不支持的区域, 返回0
                data.append(0x00)

        return bytes(data)

    def _handle_write(self, pdu_ref: int, param: bytes, data: bytes):
        """处理写变量请求 (功能码0x05)

        参数格式: byte 0=0x05, byte 1=item count, byte 2+: items
        数据格式: 每个item对应一个data-item

        Data-item格式:
          byte 0: ReturnCode (0x03=请求)
          byte 1: TransportSize
          byte 2-3: Length
          byte 4+: 数据
        """
        if len(param) < 2:
            self._send_error_ack(pdu_ref, 0x85)
            return

        item_count = param[1]
        items = []
        offset = 2
        for i in range(item_count):
            if offset + 12 > len(param):
                break
            item = param[offset:offset + 12]
            items.append(item)
            offset += 12

        # 解析data-items
        data_offset = 0
        return_codes = []
        for item in items:
            if data_offset + 4 > len(data):
                return_codes.append(0x85)
                continue

            rc = data[data_offset]
            transport_size = data[data_offset + 1]
            length = struct.unpack('>H', data[data_offset + 2:data_offset + 4])[0]
            write_data = data[data_offset + 4:data_offset + 4 + length]
            data_offset += 4 + length

            result_code = self._write_item(item, write_data)
            return_codes.append(result_code)

        # 响应: 参数为 0x05 + item_count, 数据为每个item的return code
        param_resp = bytes([S7_FUNC_WRITE, item_count])
        data_resp = bytes(return_codes)

        self._send_ack_data(pdu_ref, param_resp, data_resp)

    def _write_item(self, item: bytes, data: bytes) -> int:
        """写入单个item, 返回return code (0xFF=成功)"""
        if len(item) < 12:
            return 0x85

        read_len = item[2]        # 写入字节数
        db_number = item[3]
        area = item[4]
        addr_bytes = item[5:8]
        byte_addr = (addr_bytes[0] << 16) | (addr_bytes[1] << 8) | addr_bytes[2]

        try:
            with self.lock:
                self._write_plc_area(area, db_number, byte_addr, data)
            return 0xFF
        except Exception as e:
            logger.warning(f"[U{self.unit_id}] 写入失败 area=0x{area:02X} addr={byte_addr}: {e}")
            return 0x85

    def _write_plc_area(self, area: int, db_number: int, byte_addr: int, data: bytes):
        """写入PLC指定区域"""
        for i, byte_val in enumerate(data):
            addr = byte_addr + i

            if area in (S7_AREA_DB, S7_AREA_VA) and db_number in (0, 1):
                # V区
                self.plc.set_vb(addr, byte_val & 0xFF)

            elif area == S7_AREA_PE:
                # I区
                for b in range(8):
                    self.plc.i[(addr, b)] = bool(byte_val & (1 << b))

            elif area == S7_AREA_PA:
                # Q区
                for b in range(8):
                    self.plc.q[(addr, b)] = bool(byte_val & (1 << b))

            elif area == S7_AREA_MK:
                # M区
                for b in range(8):
                    self.plc.m[(addr, b)] = bool(byte_val & (1 << b))

            else:
                logger.warning(f"[U{self.unit_id}] 不支持的写入区域: 0x{area:02X}")

    # ------------------------------------------------------------
    # 响应发送
    # ------------------------------------------------------------

    def _send_ack_data(self, pdu_ref: int, param: bytes, data: bytes):
        """发送Ack-Data响应

        Ack-Data头 (12字节):
          byte 0: Protocol ID (0x32)
          byte 1: ROSCTR (3=Ack-Data)
          byte 2-3: Reserved (0x0000)
          byte 4-5: PDU Reference (回传客户端的ref)
          byte 6-7: Parameter length
          byte 8-9: Data length
          byte 10: Error Class (0=无错)
          byte 11: Error Code (0=无错)
        """
        param_len = len(param)
        data_len = len(data)

        header = struct.pack('>BBHHHHBB',
            S7_PROTOCOL_ID,
            S7_ACK_DATA,
            0x0000,         # reserved
            pdu_ref,
            param_len,
            data_len,
            0x00,           # error class
            0x00            # error code
        )

        # COTP DT包装: length=0x02, type=0xF0, EOT=0x80
        cotp_dt = bytes([0x02, COTP_DATA, 0x80]) + header + param + data

        self._send_tpkt(cotp_dt)

    def _send_error_ack(self, pdu_ref: int, error_code: int):
        """发送错误响应"""
        # 简化: 发送空数据的Ack-Data, 带错误码
        header = struct.pack('>BBHHHHBB',
            S7_PROTOCOL_ID,
            S7_ACK_DATA,
            0x0000,
            pdu_ref,
            0,
            0,
            0x85,           # error class
            error_code
        )
        cotp_dt = bytes([0x02, COTP_DATA, 0x80]) + header
        self._send_tpkt(cotp_dt)


# ============================================================
# PLC扫描线程 (驱动PLC逻辑)
# ============================================================

class PLCScanThread(threading.Thread):
    """PLC周期扫描线程

    每100ms调用一次plc.run_cycle(), 驱动PLC状态机/FC逻辑。
    独立于S7连接线程, 通过锁保护PLC访问。
    """

    def __init__(self, plc: PLCSim, unit_id: int, lock: threading.Lock, interval_ms: int = 100):
        super().__init__(name=f"PLCScan-U{unit_id}", daemon=True)
        self.plc = plc
        self.unit_id = unit_id
        self.lock = lock
        self.interval = interval_ms / 1000.0
        self.running = True
        self.cycle_count = 0

    def run(self):
        logger.info(f"[U{self.unit_id}] PLC扫描线程启动 (周期={self.interval*1000:.0f}ms)")
        while self.running:
            start = time.time()
            try:
                with self.lock:
                    self.plc.run_cycle()
                self.cycle_count += 1
            except Exception as e:
                logger.error(f"[U{self.unit_id}] PLC扫描异常: {e}", exc_info=True)

            # 精确睡眠
            elapsed = time.time() - start
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)

        logger.info(f"[U{self.unit_id}] PLC扫描线程停止 (共{self.cycle_count}周期)")

    def stop(self):
        self.running = False


# ============================================================
# S7服务端主类
# ============================================================

class S7Server:
    """S7协议服务端

    管理8个端口(对应8台PLC), 每端口独立PLCSim实例+扫描线程。
    """

    def __init__(self, start_port: int = 10200, unit_count: int = 8, scan_interval_ms: int = 100):
        self.start_port = start_port
        self.unit_count = unit_count
        self.scan_interval = scan_interval_ms

        # 每单元: {plc, lock, scan_thread, server_sock, client_conns}
        self.units: Dict[int, dict] = {}
        self.running = False
        self._init_units()

    def _init_units(self):
        """初始化8个单元"""
        for i in range(1, self.unit_count + 1):
            plc = PLCSim()
            lock = threading.Lock()
            self.units[i] = {
                'plc': plc,
                'lock': lock,
                'scan_thread': None,
                'server_sock': None,
                'client_conns': [],
                'listen_thread': None,
            }
            logger.info(f"[U{i}] PLC实例已创建")

    def start(self):
        """启动服务端"""
        self.running = True
        for unit_id in range(1, self.unit_count + 1):
            self._start_unit(unit_id)
        logger.info(f"=== S7服务端已启动, {self.unit_count}个单元 ===")
        logger.info(f"端口范围: {self.start_port}~{self.start_port + self.unit_count - 1}")
        logger.info(f"PLC扫描周期: {self.scan_interval}ms")

    def _start_unit(self, unit_id: int):
        """启动单个单元"""
        unit = self.units[unit_id]
        port = self.start_port + unit_id - 1

        # 创建监听socket
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('0.0.0.0', port))
        server_sock.listen(4)  # 每端口最多4个客户端等待
        server_sock.settimeout(1.0)
        unit['server_sock'] = server_sock

        # 启动PLC扫描线程
        scan_thread = PLCScanThread(unit['plc'], unit_id, unit['lock'], self.scan_interval)
        scan_thread.start()
        unit['scan_thread'] = scan_thread

        # 启动监听线程
        listen_thread = threading.Thread(
            target=self._listen_loop,
            args=(unit_id,),
            name=f"Listen-U{unit_id}",
            daemon=True
        )
        listen_thread.start()
        unit['listen_thread'] = listen_thread

        logger.info(f"[U{unit_id}] 监听端口 {port}, 等待连接...")

    def _listen_loop(self, unit_id: int):
        """监听线程主循环"""
        unit = self.units[unit_id]
        server_sock = unit['server_sock']

        while self.running:
            try:
                client_sock, addr = server_sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            # 创建连接处理线程
            conn = S7Connection(client_sock, addr, unit['plc'], unit_id)
            conn.lock = unit['lock']  # 共享单元锁
            unit['client_conns'].append(conn)

            conn_thread = threading.Thread(
                target=conn.run,
                name=f"S7Conn-U{unit_id}-{addr[0]}:{addr[1]}",
                daemon=True
            )
            conn_thread.start()

    def stop(self):
        """停止服务端"""
        logger.info("正在停止S7服务端...")
        self.running = False

        for unit_id, unit in self.units.items():
            # 停止扫描线程
            if unit['scan_thread']:
                unit['scan_thread'].stop()
                unit['scan_thread'].join(timeout=2)

            # 关闭所有客户端连接
            for conn in unit['client_conns']:
                conn.stop()

            # 关闭监听socket
            if unit['server_sock']:
                try:
                    unit['server_sock'].close()
                except:
                    pass

        logger.info("S7服务端已停止")

    def get_unit_status(self, unit_id: int) -> dict:
        """获取单元状态"""
        if unit_id not in self.units:
            return {}
        unit = self.units[unit_id]
        with unit['lock']:
            return {
                'unit_id': unit_id,
                'vw2': unit['plc'].vw2,
                'vw6': unit['plc'].vw6,
                'vw8': unit['plc'].vw8,
                'cycle_count': unit['scan_thread'].cycle_count if unit['scan_thread'] else 0,
                'client_count': len(unit['client_conns']),
            }

    def get_all_status(self) -> list:
        """获取所有单元状态"""
        return [self.get_unit_status(i) for i in range(1, self.unit_count + 1)]

    def monitor_loop(self, interval: float = 5.0):
        """监控循环, 定期打印状态"""
        try:
            while self.running:
                time.sleep(interval)
                print("\n" + "="*70)
                print(f"{'单元':<6}{'端口':<8}{'VW2':<8}{'VW6':<8}{'VW8':<8}{'扫描周期':<10}{'连接数':<8}")
                print("-"*70)
                for i in range(1, self.unit_count + 1):
                    s = self.get_unit_status(i)
                    port = self.start_port + i - 1
                    print(f"U{i:<5}{port:<8}{s['vw2']:<8}{s['vw6']:<8}{s['vw8']:<8}{s['cycle_count']:<10}{s['client_count']:<8}")
                print("="*70)
        except KeyboardInterrupt:
            pass


# ============================================================
# 主入口
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='AQUA-EXPO S7协议服务端')
    parser.add_argument('--start-port', type=int, default=10200,
                        help='起始端口 (默认10200, 8端口=10200~10207)')
    parser.add_argument('--units', type=int, default=8,
                        help='单元数量 (默认8)')
    parser.add_argument('--scan-ms', type=int, default=100,
                        help='PLC扫描周期毫秒 (默认100ms)')
    parser.add_argument('--monitor-interval', type=float, default=5.0,
                        help='监控打印间隔秒 (默认5秒)')
    parser.add_argument('--cold-start', action='store_true',
                        help='启动时执行PLC冷启动')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='日志级别')
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)

    # 创建并启动服务端
    server = S7Server(
        start_port=args.start_port,
        unit_count=args.units,
        scan_interval_ms=args.scan_ms
    )

    if args.cold_start:
        logger.info("执行8台PLC冷启动...")
        for unit_id in range(1, args.units + 1):
            with server.units[unit_id]['lock']:
                server.units[unit_id]['plc'].run_cold_start()
            logger.info(f"[U{unit_id}] 冷启动完成, VW2={server.units[unit_id]['plc'].vw2}")

    server.start()

    print("\n" + "="*70)
    print("  AQUA-EXPO S7协议服务端已启动")
    print("="*70)
    print(f"  单元数量: {args.units}")
    print(f"  端口范围: {args.start_port}~{args.start_port + args.units - 1}")
    print(f"  PLC扫描周期: {args.scan_ms}ms")
    print(f"  日志级别: {args.log_level}")
    print("="*70)
    print("\n  MCGS客户端配置:")
    print(f"    协议: S7协议")
    print(f"    IP: 127.0.0.1 (本机) 或 服务器IP")
    print(f"    端口: {args.start_port}~{args.start_port + args.units - 1} (对应8台PLC)")
    print(f"    机架: 0, 槽: 1")
    print(f"    TSAP: 自动协商")
    print("\n  按Ctrl+C停止服务端\n")

    try:
        server.monitor_loop(args.monitor_interval)
    except KeyboardInterrupt:
        print("\n接收到中断信号,停止服务端...")
    finally:
        server.stop()


if __name__ == '__main__':
    main()
