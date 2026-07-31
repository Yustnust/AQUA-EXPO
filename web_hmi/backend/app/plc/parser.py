"""
Modbus 原始寄存器数据解析器
将 pymodbus 读取到的保持寄存器列表转换为结构化 Python 字典
"""

import struct
from typing import Dict, List, Any, Optional

from .registers import VARIABLES, DataType, RegisterDef


def _word_to_bool(word: int, bit_index: int) -> bool:
    """从 16 位字中提取某一位的布尔值。"""
    return bool((word >> bit_index) & 0x1)


def _registers_to_int32(reg0: int, reg1: int) -> int:
    """两个保持寄存器（大端）转 32 位有符号整数。"""
    val = (reg0 << 16) | reg1
    if val & 0x80000000:
        val -= 0x100000000
    return val


def _registers_to_uint32(reg0: int, reg1: int) -> int:
    """两个保持寄存器（大端）转 32 位无符号整数。"""
    return (reg0 << 16) | reg1


def _registers_to_float32(reg0: int, reg1: int) -> float:
    """两个保持寄存器（大端）转 IEEE 754 32 位浮点数。"""
    packed = struct.pack(">HH", reg0, reg1)
    return struct.unpack(">f", packed)[0]


def parse_all(registers: Dict[int, int]) -> Dict[str, Any]:
    """
    根据 VARIABLES 定义解析整个寄存器字典。

    :param registers: 键为 pymodbus 0-based 寄存器地址，值为寄存器值（0~65535）
    :return: 键为变量名，值为解析后的 Python 类型
    """
    result: Dict[str, Any] = {}

    for var in VARIABLES:
        addr = var.reg_addr
        value: Any = None

        if var.dtype == DataType.BOOL:
            if addr in registers:
                value = _word_to_bool(registers[addr], var.bit_index)

        elif var.dtype == DataType.INT16:
            if addr in registers:
                val = registers[addr]
                if val >= 0x8000:
                    val -= 0x10000
                value = val

        elif var.dtype == DataType.UINT16:
            if addr in registers:
                value = registers[addr]

        elif var.dtype == DataType.INT32:
            if addr in registers and addr + 1 in registers:
                value = _registers_to_int32(registers[addr], registers[addr + 1])

        elif var.dtype == DataType.UINT32:
            if addr in registers and addr + 1 in registers:
                value = _registers_to_uint32(registers[addr], registers[addr + 1])

        elif var.dtype == DataType.FLOAT32:
            if addr in registers and addr + 1 in registers:
                value = _registers_to_float32(registers[addr], registers[addr + 1])

        elif var.dtype == DataType.BYTE:
            if addr in registers:
                word = registers[addr]
                # V 地址偶数 -> 高字节；奇数 -> 低字节
                if var.v_addr % 2 == 0:
                    value = (word >> 8) & 0xFF
                else:
                    value = word & 0xFF

        result[var.name] = value

    return result


def encode_value(var: RegisterDef, current_word: int, value: Any) -> int:
    """
    将待写入值编码为单个 16 位保持寄存器值（用于位变量、字变量）。

    :param var: 变量定义
    :param current_word: 该寄存器当前值（位变量需要读-改-写）
    :param value: 待写入的值
    :return: 编码后的 16 位寄存器值
    """
    if var.dtype == DataType.BOOL:
        bit = 1 << var.bit_index
        if value:
            return current_word | bit
        else:
            return current_word & ~bit

    elif var.dtype == DataType.INT16:
        val = int(value)
        if val < 0:
            val += 0x10000
        return val & 0xFFFF

    elif var.dtype == DataType.UINT16:
        return int(value) & 0xFFFF

    raise ValueError(f"encode_value 暂不支持类型 {var.dtype}")


def encode_float32(value: float) -> List[int]:
    """将 32 位浮点数编码为两个 16 位寄存器值（大端）。"""
    packed = struct.pack(">f", float(value))
    return [struct.unpack(">H", packed[0:2])[0], struct.unpack(">H", packed[2:4])[0]]


def encode_int32(value: int) -> List[int]:
    """将 32 位有符号整数编码为两个 16 位寄存器值（大端）。"""
    if value < 0:
        value += 0x100000000
    return [(value >> 16) & 0xFFFF, value & 0xFFFF]
