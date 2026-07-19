"""
S7协议服务端测试脚本

功能: 验证S7Server的基本功能, 无需外部HMI即可测试。

测试内容:
  1. 服务端启动/停止
  2. 单连接读写V区
  3. 8端口并发连接
  4. V区数据一致性
  5. I/Q区读取
  6. 多线程并发访问

不依赖外部库, 仅用Python标准库socket构造S7协议帧。

用法:
  python test_s7_server.py
"""

import socket
import struct
import threading
import time
import sys
import os

# 添加sim目录到path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from s7_server import S7Server, S7Connection
from plc_simulator import PLCSim


# ============================================================
# S7客户端工具函数 (用于测试)
# ============================================================

def build_connect_request() -> bytes:
    """构建COTP Connect Request"""
    # TPKT + COTP CR
    # COTP CR负载: dst-ref + src-ref + class + 可选参数
    cotp_cr_payload = (
        b'\x00\x01'           # dst-ref
        b'\x00\x01'           # src-ref
        b'\x00'               # class 0
        b'\xC0\x01\x0A'       # TPDU Size = 1024 (0x0A)
        b'\xC1\x02\x01\x00'   # src-TSAP = 0x0100
        b'\xC2\x02\x02\x00'   # dst-TSAP = 0x0200
    )
    cotp_cr = bytes([len(cotp_cr_payload), 0xE0]) + cotp_cr_payload
    tpkt = struct.pack('>BBH', 0x03, 0x00, 4 + len(cotp_cr))
    return tpkt + cotp_cr


def build_setup_request(pdu_ref: int) -> bytes:
    """构建S7 Setup Communication请求"""
    # S7 Job: Setup
    param = bytes([0x28, 0x00, 0x01, 0x00])  # func, reserved, max-amq-caller, max-amq-callee
    data = bytes([0x00, 0x08, 0x01, 0xC0, 0x01, 0xC0])  # PDU=448

    s7_header = struct.pack('>BBHHHH',
        0x32, 1,         # proto, rosctr=Job
        0x0000,          # reserved
        pdu_ref,
        len(param),
        len(data)
    )
    s7 = s7_header + param + data

    # COTP DT包装: length=0x02, type=0xF0, EOT=0x80
    cotp_dt = bytes([0x02, 0xF0, 0x80]) + s7
    tpkt = struct.pack('>BBH', 0x03, 0x00, 4 + len(cotp_dt))
    return tpkt + cotp_dt


def build_read_request(pdu_ref: int, area: int, db: int, byte_addr: int, length: int) -> bytes:
    """构建S7 Read请求

    Item格式 (12字节):
      0x12 0x0A <length> <db> <area> <addr_3bytes>
    """
    # 24位地址编码
    addr_hi = (byte_addr >> 16) & 0xFF
    addr_mid = (byte_addr >> 8) & 0xFF
    addr_lo = byte_addr & 0xFF

    item = bytes([
        0x12, 0x0A,              # item header
        length,                  # read length (bytes)
        db,                      # DB number
        area,                    # area
        addr_hi, addr_mid, addr_lo,  # 24-bit address
        0x00, 0x00, 0x00, 0x00   # padding (S7-200不需要)
    ])

    param = bytes([0x04, 0x01]) + item  # func=read, count=1, +item

    s7_header = struct.pack('>BBHHHH',
        0x32, 1, 0x0000, pdu_ref, len(param), 0
    )
    s7 = s7_header + param

    cotp_dt = bytes([0x02, 0xF0, 0x80]) + s7
    tpkt = struct.pack('>BBH', 0x03, 0x00, 4 + len(cotp_dt))
    return tpkt + cotp_dt


def build_write_request(pdu_ref: int, area: int, db: int, byte_addr: int, data: bytes) -> bytes:
    """构建S7 Write请求"""
    length = len(data)

    addr_hi = (byte_addr >> 16) & 0xFF
    addr_mid = (byte_addr >> 8) & 0xFF
    addr_lo = byte_addr & 0xFF

    item = bytes([
        0x12, 0x0A,
        length,
        db,
        area,
        addr_hi, addr_mid, addr_lo,
        0x00, 0x00, 0x00, 0x00
    ])

    param = bytes([0x05, 0x01]) + item  # func=write, count=1

    # Data item
    data_item = bytes([0x00, 0x09]) + struct.pack('>H', length) + data

    s7_header = struct.pack('>BBHHHH',
        0x32, 1, 0x0000, pdu_ref, len(param), len(data_item)
    )
    s7 = s7_header + param + data_item

    cotp_dt = bytes([0x02, 0xF0, 0x80]) + s7
    tpkt = struct.pack('>BBH', 0x03, 0x00, 4 + len(cotp_dt))
    return tpkt + cotp_dt


def recv_tpkt(sock) -> bytes:
    """接收完整TPKT帧"""
    header = b''
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk:
            return b''
        header += chunk

    total_len = struct.unpack('>H', header[2:4])[0]
    body = b''
    while len(body) < total_len - 4:
        chunk = sock.recv(total_len - 4 - len(body))
        if not chunk:
            return b''
        body += chunk

    return header + body


def parse_s7_response(frame: bytes) -> dict:
    """解析S7响应帧"""
    # 跳过TPKT(4) + COTP DT(3: length 0xF0 0x80)
    s7 = frame[7:]

    proto_id = s7[0]
    rosctr = s7[1]
    pdu_ref = struct.unpack('>H', s7[4:6])[0]
    param_len = struct.unpack('>H', s7[6:8])[0]
    data_len = struct.unpack('>H', s7[8:10])[0]
    error_class = s7[10] if len(s7) > 10 else 0
    error_code = s7[11] if len(s7) > 11 else 0

    param = s7[12:12 + param_len]
    data = s7[12 + param_len:12 + param_len + data_len]

    return {
        'proto_id': proto_id,
        'rosctr': rosctr,
        'pdu_ref': pdu_ref,
        'param_len': param_len,
        'data_len': data_len,
        'error_class': error_class,
        'error_code': error_code,
        'param': param,
        'data': data,
    }


def parse_read_response_data(data: bytes, item_count: int = 1) -> list:
    """解析读响应的data字段, 返回每个item的数据"""
    items = []
    offset = 0
    for i in range(item_count):
        if offset + 4 > len(data):
            break
        return_code = data[offset]
        transport_size = data[offset + 1]
        length = struct.unpack('>H', data[offset + 2:offset + 4])[0]
        item_data = data[offset + 4:offset + 4 + length]
        items.append({
            'return_code': return_code,
            'transport_size': transport_size,
            'length': length,
            'data': item_data,
        })
        offset += 4 + length
    return items


# ============================================================
# 测试用例
# ============================================================

class S7ServerTests:
    """S7服务端测试用例"""

    def __init__(self, start_port=11000, units=8):
        self.start_port = start_port
        self.units = units
        self.server = None
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def _assert(self, condition, msg, test_id):
        if condition:
            self.passed += 1
            print(f"  ✓ {test_id}: {msg}")
        else:
            self.failed += 1
            print(f"  ✗ {test_id}: {msg}")

    def _skip(self, msg, test_id):
        self.skipped += 1
        print(f"  ⊘ {test_id}: {msg} (跳过)")

    # ------------------------------------------------------------
    # 测试1: 服务端启动/停止
    # ------------------------------------------------------------

    def test_server_start_stop(self):
        print("\n[TEST 1] 服务端启动/停止")
        try:
            self.server = S7Server(start_port=self.start_port, unit_count=self.units, scan_interval_ms=100)
            self.server.start()
            time.sleep(0.5)
            self._assert(self.server.running, "服务端启动成功", "S7-SR-01")

            # 验证8端口都在监听
            for i in range(self.units):
                port = self.start_port + i
                try:
                    s = socket.socket()
                    s.settimeout(1)
                    s.connect(('127.0.0.1', port))
                    s.close()
                except:
                    self._assert(False, f"端口{port}未监听", f"S7-SR-0{i+2}")
                    return
            self._assert(True, f"全部{self.units}端口监听正常", "S7-SR-02")

        except Exception as e:
            self._assert(False, f"启动异常: {e}", "S7-SR-EX")

    # ------------------------------------------------------------
    # 测试2: COTP连接建立
    # ------------------------------------------------------------

    def test_cotp_connect(self):
        print("\n[TEST 2] COTP连接建立")
        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect(('127.0.0.1', self.start_port))

            # 发送COTP CR
            sock.sendall(build_connect_request())

            # 接收COTP CC
            resp = recv_tpkt(sock)
            self._assert(len(resp) > 5, f"收到COTP CC响应 (len={len(resp)})", "S7-CT-01")

            cotp_type = resp[5] & 0xF0
            self._assert(cotp_type == 0xD0, f"COTP类型=CC(0xD0), 实际0x{cotp_type:02X}", "S7-CT-02")

            sock.close()
        except Exception as e:
            self._assert(False, f"连接异常: {e}", "S7-CT-EX")

    # ------------------------------------------------------------
    # 测试3: Setup通信参数协商
    # ------------------------------------------------------------

    def test_setup_communication(self):
        print("\n[TEST 3] Setup通信参数协商")
        try:
            sock = self._connect_and_setup()
            if sock:
                self._assert(True, "Setup协商成功", "S7-ST-01")
                sock.close()
        except Exception as e:
            self._assert(False, f"Setup异常: {e}", "S7-ST-EX")

    def _connect_and_setup(self, port_offset=0):
        """建立COTP连接+Setup"""
        sock = socket.socket()
        sock.settimeout(2)
        sock.connect(('127.0.0.1', self.start_port + port_offset))

        # COTP连接
        sock.sendall(build_connect_request())
        recv_tpkt(sock)

        # Setup
        sock.sendall(build_setup_request(1))
        resp = recv_tpkt(sock)
        if len(resp) > 12:
            s7 = parse_s7_response(resp)
            if s7['rosctr'] == 3 and s7['error_class'] == 0:
                return sock
        sock.close()
        return None

    # ------------------------------------------------------------
    # 测试4: V区写入
    # ------------------------------------------------------------

    def test_write_v_area(self):
        print("\n[TEST 4] V区写入")
        try:
            sock = self._connect_and_setup()
            if not sock:
                self._assert(False, "无法建立连接", "S7-WR-01")
                return

            # 写VB10=0x55
            sock.sendall(build_write_request(2, 0x85, 1, 10, bytes([0x55])))
            resp = recv_tpkt(sock)
            s7 = parse_s7_response(resp)
            self._assert(s7['error_class'] == 0, f"写VB10=0x55 响应无错", "S7-WR-01")

            # 写VW12=0x1234 (大端)
            sock.sendall(build_write_request(3, 0x85, 1, 12, struct.pack('>H', 0x1234)))
            resp = recv_tpkt(sock)
            s7 = parse_s7_response(resp)
            self._assert(s7['error_class'] == 0, f"写VW12=0x1234 响应无错", "S7-WR-02")

            # 验证PLC内部值
            with self.server.units[1]['lock']:
                vb10 = self.server.units[1]['plc'].get_vb(10)
                vw12 = self.server.units[1]['plc'].get_vw(12)
            self._assert(vb10 == 0x55, f"PLC内部VB10=0x{vb10:02X} (期望0x55)", "S7-WR-03")
            self._assert(vw12 == 0x1234, f"PLC内部VW12=0x{vw12:04X} (期望0x1234)", "S7-WR-04")

            sock.close()
        except Exception as e:
            self._assert(False, f"写V区异常: {e}", "S7-WR-EX")

    # ------------------------------------------------------------
    # 测试5: V区读取
    # ------------------------------------------------------------

    def test_read_v_area(self):
        print("\n[TEST 5] V区读取")
        try:
            sock = self._connect_and_setup()
            if not sock:
                self._assert(False, "无法建立连接", "S7-RD-01")
                return

            # 先写后读
            with self.server.units[1]['lock']:
                self.server.units[1]['plc'].set_vb(20, 0xAA)
                self.server.units[1]['plc'].set_vw(22, 0xBEEF)

            # 读VB20 (1字节)
            sock.sendall(build_read_request(4, 0x85, 1, 20, 1))
            resp = recv_tpkt(sock)
            s7 = parse_s7_response(resp)
            items = parse_read_response_data(s7['data'], 1)
            if items:
                self._assert(items[0]['data'] == bytes([0xAA]),
                             f"读VB20=0x{items[0]['data'][0]:02X} (期望0xAA)", "S7-RD-01")
            else:
                self._assert(False, "读响应无数据项", "S7-RD-01")

            # 读VW22 (2字节)
            sock.sendall(build_read_request(5, 0x85, 1, 22, 2))
            resp = recv_tpkt(sock)
            s7 = parse_s7_response(resp)
            items = parse_read_response_data(s7['data'], 1)
            if items:
                val = struct.unpack('>H', items[0]['data'])[0]
                self._assert(val == 0xBEEF, f"读VW22=0x{val:04X} (期望0xBEEF)", "S7-RD-02")
            else:
                self._assert(False, "读VW22响应无数据项", "S7-RD-02")

            # 读VD10 (4字节)
            with self.server.units[1]['lock']:
                self.server.units[1]['plc'].set_vd(30, 3.14)
            sock.sendall(build_read_request(6, 0x85, 1, 30, 4))
            resp = recv_tpkt(sock)
            s7 = parse_s7_response(resp)
            items = parse_read_response_data(s7['data'], 1)
            if items and len(items[0]['data']) >= 4:
                val = struct.unpack('>f', items[0]['data'])[0]
                self._assert(abs(val - 3.14) < 0.001, f"读VD30={val:.4f} (期望3.14)", "S7-RD-03")
            else:
                self._assert(False, "读VD30响应异常", "S7-RD-03")

            sock.close()
        except Exception as e:
            self._assert(False, f"读V区异常: {e}", "S7-RD-EX")

    # ------------------------------------------------------------
    # 测试6: 8端口并发连接
    # ------------------------------------------------------------

    def test_8_port_concurrent(self):
        print("\n[TEST 6] 8端口并发连接")
        socks = []
        try:
            for i in range(8):
                sock = self._connect_and_setup(port_offset=i)
                if sock:
                    socks.append(sock)
                else:
                    self._assert(False, f"单元{i+1}连接失败", f"S7-8P-0{i+1}")
                    return

            self._assert(len(socks) == 8, f"8端口全部连接成功", "S7-8P-01")

            # 每个连接写不同V区地址, 验证隔离性
            for i, sock in enumerate(socks):
                val = 0x10 + i
                sock.sendall(build_write_request(10 + i, 0x85, 1, 50, bytes([val])))

            # 等响应
            for sock in socks:
                recv_tpkt(sock)

            # 验证每个单元PLC的VB50都不同
            all_correct = True
            for i in range(8):
                with self.server.units[i + 1]['lock']:
                    vb50 = self.server.units[i + 1]['plc'].get_vb(50)
                if vb50 != 0x10 + i:
                    all_correct = False
                    print(f"    U{i+1} VB50=0x{vb50:02X} (期望0x{0x10+i:02X})")

            self._assert(all_correct, "8单元V区数据隔离正确", "S7-8P-02")

        except Exception as e:
            self._assert(False, f"8端口并发异常: {e}", "S7-8P-EX")
        finally:
            for sock in socks:
                sock.close()

    # ------------------------------------------------------------
    # 测试7: I/Q区读取
    # ------------------------------------------------------------

    def test_read_iq_area(self):
        print("\n[TEST 7] I/Q区读取")
        try:
            sock = self._connect_and_setup()
            if not sock:
                self._assert(False, "无法建立连接", "S7-IQ-01")
                return

            # 设置I0.0=1
            with self.server.units[1]['lock']:
                self.server.units[1]['plc'].i[(0, 0)] = True
                self.server.units[1]['plc'].i[(0, 1)] = True

            # 读IB0 (1字节, area=0x01)
            sock.sendall(build_read_request(10, 0x01, 0, 0, 1))
            resp = recv_tpkt(sock)
            s7 = parse_s7_response(resp)
            items = parse_read_response_data(s7['data'], 1)
            if items:
                val = items[0]['data'][0]
                # I0.0=1, I0.1=1 → IB0 = 0x03
                self._assert(val == 0x03, f"读IB0=0x{val:02X} (期望0x03)", "S7-IQ-01")
            else:
                self._assert(False, "读IB0无数据", "S7-IQ-01")

            sock.close()
        except Exception as e:
            self._assert(False, f"I/Q区读取异常: {e}", "S7-IQ-EX")

    # ------------------------------------------------------------
    # 测试8: 多连接并发(同端口)
    # ------------------------------------------------------------

    def test_multi_connection_same_port(self):
        print("\n[TEST 8] 同端口多连接并发")
        socks = []
        try:
            # 同端口建立3个连接
            for i in range(3):
                sock = self._connect_and_setup(port_offset=0)
                if sock:
                    socks.append(sock)

            self._assert(len(socks) == 3, f"同端口3连接建立成功", "S7-MC-01")

            # 3个连接并发写不同地址
            for i, sock in enumerate(socks):
                sock.sendall(build_write_request(20 + i, 0x85, 1, 60 + i, bytes([0xA0 + i])))

            for sock in socks:
                recv_tpkt(sock)

            # 验证
            all_correct = True
            for i in range(3):
                with self.server.units[1]['lock']:
                    val = self.server.units[1]['plc'].get_vb(60 + i)
                if val != 0xA0 + i:
                    all_correct = False
            self._assert(all_correct, "3连接并发写不同地址正确", "S7-MC-02")

        except Exception as e:
            self._assert(False, f"多连接异常: {e}", "S7-MC-EX")
        finally:
            for sock in socks:
                sock.close()

    # ------------------------------------------------------------
    # 主测试入口
    # ------------------------------------------------------------

    def run_all(self):
        print("=" * 60)
        print("  AQUA-EXPO S7协议服务端测试")
        print("=" * 60)

        self.test_server_start_stop()
        self.test_cotp_connect()
        self.test_setup_communication()
        self.test_write_v_area()
        self.test_read_v_area()
        self.test_8_port_concurrent()
        self.test_read_iq_area()
        self.test_multi_connection_same_port()

        # 停止服务端
        if self.server:
            self.server.stop()

        print("\n" + "=" * 60)
        print(f"  测试完成: ✓{self.passed}通过  ✗{self.failed}失败  ⊘{self.skipped}跳过")
        print("=" * 60)
        return 0 if self.failed == 0 else 1


def main():
    tester = S7ServerTests(start_port=11000, units=8)
    sys.exit(tester.run_all())


if __name__ == '__main__':
    main()
