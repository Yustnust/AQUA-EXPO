#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比PLC STL实际使用地址与HMI-PLC接口文档，输出分级核对报告。
"""
import os
import re
import json
import csv
from collections import defaultdict

STL_JSON = r"d:\work\CTI\stl_address_extract.json"
DOC_MD = r"d:\work\CTI\docs\HMI-PLC变量地址表_v1.0.md"
DOC_CSV = r"d:\work\CTI\docs\hmi_preparation\McgsPro变量导入_8单元_v2.0.csv"
REPORT_MD = r"d:\work\CTI\HMI-PLC地址核对报告.md"

# ============================================================
# 1. 地址规范化与范围计算
# ============================================================

def addr_to_range(addr_type, addr):
    """
    将地址转为字节范围 (start_byte, end_byte_exclusive, bit)。
    返回 None 表示非V区或无法计算。
    """
    addr = addr.upper()
    if addr_type == "V_bit":
        m = re.match(r"V(\d+)\.(\d+)", addr)
        if m:
            return (int(m.group(1)), int(m.group(1)) + 1, int(m.group(2)))
    elif addr_type == "VB":
        m = re.match(r"VB(\d+)", addr)
        if m:
            return (int(m.group(1)), int(m.group(1)) + 1, None)
    elif addr_type == "VW":
        m = re.match(r"VW(\d+)", addr)
        if m:
            b = int(m.group(1))
            return (b, b + 2, None)
    elif addr_type == "VD":
        m = re.match(r"VD(\d+)", addr)
        if m:
            b = int(m.group(1))
            return (b, b + 4, None)
    return None


def ranges_overlap(r1, r2):
    """两个V区字节范围是否重叠（含边界相邻不算重叠）"""
    if r1 is None or r2 is None:
        return False
    return r1[0] < r2[1] and r2[0] < r1[1]


def canonical_v_addr(addr_type, addr):
    """生成统一格式，便于集合比较"""
    return f"{addr_type}:{addr.upper()}"


def is_v_addr(addr_type):
    return addr_type in ("V_bit", "VB", "VW", "VD")


def is_bit_addr(addr_type):
    return addr_type in ("V_bit", "I_bit", "Q_bit", "M_bit", "L_bit")


# ============================================================
# 2. 读取STL解析结果
# ============================================================

def load_stl_results():
    with open(STL_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================
# 3. 解析HMI-PLC变量地址表_v1.0.md
# ============================================================

def parse_md_addresses(path):
    """
    从markdown文档中提取地址定义。
    返回 list of dict: {type, address, doc_type, direction, symbol, note, source}
    """
    defs = []
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 仅解析正文部分（附录A为断电保持区规划，不视为具体变量定义）
    appendix_start = text.find("## 附录")
    if appendix_start > 0:
        body_text = text[:appendix_start]
    else:
        body_text = text

    # 已迁移地址：文档正文说明这些地址已不再使用，应从范围展开中排除
    MIGRATED_VD = {18, 20, 48, 50, 96, 98}
    # 预留位：文档明确标注为备用/预留，未使用属正常
    RESERVED_ADDRS = {
        "V_bit:V0.1", "V_bit:V0.5", "V_bit:V0.6",
        "V_bit:V1.1", "V_bit:V1.5", "V_bit:V303.7",
        "I_bit:I2.2",
    }

    # 辅助：解析单个地址或范围字符串，如 "VD10", "VW2", "V0.0~V0.7", "VB300~VB303"
    def add_addr(addr_str, doc_type, direction, symbol, note):
        addr_str = addr_str.strip()
        is_reserved = False
        # 范围展开
        if "~" in addr_str:
            parts = addr_str.split("~")
            start = parts[0].strip()
            end = parts[1].strip()
            # 尝试按位范围展开（如 V0.0~V0.7）
            m1 = re.match(r"V(\d+)\.(\d+)", start)
            m2 = re.match(r"V(\d+)\.(\d+)", end)
            if m1 and m2 and m1.group(1) == m2.group(1):
                byte = int(m1.group(1))
                for bit in range(int(m1.group(2)), int(m2.group(2)) + 1):
                    key = f"V{byte}.{bit}"
                    defs.append({
                        "type": "V_bit", "address": key,
                        "doc_type": doc_type, "direction": direction,
                        "symbol": symbol, "note": note, "source": "MD",
                        "reserved": key in RESERVED_ADDRS
                    })
                return
            # 尝试按字节范围展开（如 VB300~VB303）
            m1 = re.match(r"VB(\d+)", start)
            m2 = re.match(r"VB(\d+)", end)
            if m1 and m2:
                for b in range(int(m1.group(1)), int(m2.group(1)) + 1):
                    defs.append({
                        "type": "VB", "address": f"VB{b}",
                        "doc_type": doc_type, "direction": direction,
                        "symbol": symbol, "note": note, "source": "MD",
                        "reserved": False
                    })
                return
            # 尝试按VD范围展开（如 VD10~VD49）
            m1 = re.match(r"VD(\d+)", start)
            m2 = re.match(r"VD(\d+)", end)
            if m1 and m2:
                for b in range(int(m1.group(1)), int(m2.group(1)) + 1, 4):
                    if b in MIGRATED_VD:
                        continue
                    defs.append({
                        "type": "VD", "address": f"VD{b}",
                        "doc_type": doc_type, "direction": direction,
                        "symbol": symbol, "note": note, "source": "MD",
                        "reserved": False
                    })
                return
            # 尝试按VW范围展开
            m1 = re.match(r"VW(\d+)", start)
            m2 = re.match(r"VW(\d+)", end)
            if m1 and m2:
                for b in range(int(m1.group(1)), int(m2.group(1)) + 1, 2):
                    defs.append({
                        "type": "VW", "address": f"VW{b}",
                        "doc_type": doc_type, "direction": direction,
                        "symbol": symbol, "note": note, "source": "MD",
                        "reserved": False
                    })
                return
            return  # 无法识别的范围

        # 单个地址
        m = re.match(r"^(VD|VW|VB|V|I|Q|M|SM|DT|T|C|AC)(\d+)(?:\.(\d+))?$", addr_str, re.I)
        if not m:
            # 特殊：M_AlarmAckMode(V200.0)
            m = re.match(r".*\b(V\d+\.\d+)\b.*", addr_str)
            if m:
                add_addr(m.group(1), doc_type, direction, symbol, note)
            return
        prefix = m.group(1).upper()
        num = int(m.group(2))
        bit = m.group(3)
        if prefix == "VD":
            if num in MIGRATED_VD:
                return
            key = f"VD{num}"
            defs.append({"type": "VD", "address": key, "doc_type": doc_type, "direction": direction, "symbol": symbol, "note": note, "source": "MD", "reserved": key in RESERVED_ADDRS})
        elif prefix == "VW":
            key = f"VW{num}"
            defs.append({"type": "VW", "address": key, "doc_type": doc_type, "direction": direction, "symbol": symbol, "note": note, "source": "MD", "reserved": key in RESERVED_ADDRS})
        elif prefix == "VB":
            key = f"VB{num}"
            defs.append({"type": "VB", "address": key, "doc_type": doc_type, "direction": direction, "symbol": symbol, "note": note, "source": "MD", "reserved": key in RESERVED_ADDRS})
        elif prefix == "V":
            if bit is not None:
                key = f"V{num}.{int(bit)}"
                defs.append({"type": "V_bit", "address": key, "doc_type": doc_type, "direction": direction, "symbol": symbol, "note": note, "source": "MD", "reserved": key in RESERVED_ADDRS})
        elif prefix in ("I", "Q", "M"):
            if bit is not None:
                key = f"{prefix}{num}.{int(bit)}"
                defs.append({"type": f"{prefix}_bit", "address": key, "doc_type": doc_type, "direction": direction, "symbol": symbol, "note": note, "source": "MD", "reserved": key in RESERVED_ADDRS})
        elif prefix in ("SM", "DT", "T", "C", "AC"):
            defs.append({"type": prefix, "address": addr_str, "doc_type": doc_type, "direction": direction, "symbol": symbol, "note": note, "source": "MD", "reserved": False})

    # 3.1 从表格中提取：物理地址 | 符号 | ...
    # DI映射
    for m in re.finditer(r"\|\s*(I\d+\.\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|", body_text):
        add_addr(m.group(1), "BOOL", "只读", m.group(2).strip(), m.group(5).strip())
    # DO映射
    for m in re.finditer(r"\|\s*(Q\d+\.\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|", body_text):
        add_addr(m.group(1), "BOOL", "PLC写/HMI读", m.group(2).strip(), m.group(6).strip())

    # 3.2 从正文中提取显式地址定义（带符号说明）
    # 模式：| V0.0 | CMD_Start | 启动实验 | ...
    for line in body_text.splitlines():
        # 表格行：| 地址 | 符号 | 说明 | ...
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c]
        if len(cells) >= 3 and not line.strip().startswith("|"):
            continue
        if len(cells) >= 3:
            addr = cells[0]
            symbol = cells[1]
            note = cells[2] if len(cells) > 2 else ""
            # 识别地址
            if re.match(r"^(VD|VW|VB|V|I|Q|M|SM|DT|T|C|AC)\d", addr, re.I):
                # 判断方向
                direction = "未指定"
                if "HMI→PLC" in line or "命令位" in line or "HMI下发" in line:
                    direction = "读写"
                elif "PLC→HMI" in line or "状态位" in line or "PLC当前状态" in line:
                    direction = "只读"
                elif "HMI只读" in line or "PLC内部" in line:
                    direction = "只读"
                # 判断类型
                doc_type = "未指定"
                if addr.upper().startswith("VD"):
                    doc_type = "REAL"
                elif addr.upper().startswith("VW"):
                    doc_type = "INT/WORD"
                elif addr.upper().startswith("VB"):
                    doc_type = "BYTE"
                elif addr.upper().startswith("V") and "." in addr:
                    doc_type = "BOOL"
                elif addr.upper().startswith(("I", "Q", "M")) and "." in addr:
                    doc_type = "BOOL"
                add_addr(addr, doc_type, direction, symbol, note)

    # 3.3 特殊文本中提取地址与符号
    special_patterns = [
        (r"M_AlarmAckMode[（(]?(V200\.0)[)）]?", "V200.0", "BOOL", "读写"),
        (r"V304\.0.*M_InitDone", "V304.0", "BOOL", "PLC内部"),
    ]
    for pat, addr, dtype, direction in special_patterns:
        if re.search(pat, body_text):
            add_addr(addr, dtype, direction, "", "")

    return defs


# ============================================================
# 4. 解析McgsPro CSV
# ============================================================

def parse_csv_addresses(path):
    """
    解析CSV变量导入文件。
    返回 list of dict: {type, address, doc_type, direction, symbol, note, source}
    """
    defs = []
    type_map = {
        "第00位": "V_bit", "第01位": "V_bit", "第02位": "V_bit", "第03位": "V_bit",
        "第04位": "V_bit", "第05位": "V_bit", "第06位": "V_bit", "第07位": "V_bit",
        "8位无符号": "VB",
        "16位有符号二进制": "VW",
        "32位浮点数": "VD",
    }
    dtype_map = {
        "第00位": "BOOL", "第01位": "BOOL", "第02位": "BOOL", "第03位": "BOOL",
        "第04位": "BOOL", "第05位": "BOOL", "第06位": "BOOL", "第07位": "BOOL",
        "8位无符号": "BYTE",
        "16位有符号二进制": "INT",
        "32位浮点数": "REAL",
    }
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].strip().startswith('#') or len(row) < 7:
                continue
            ch_type, data_type, ch_addr, ch_count, rw, var_name, note = [c.strip() for c in row[:7]]
            if ch_type != "V区变量":
                continue
            addr_num = int(ch_addr)
            count = int(ch_count)
            atype = type_map.get(data_type)
            dtype = dtype_map.get(data_type)
            if atype is None:
                continue
            for i in range(count):
                if atype == "V_bit":
                    bit = int(data_type.replace("第", "").replace("位", ""))
                    addr = f"V{addr_num + i}.{bit}"
                elif atype == "VB":
                    addr = f"VB{addr_num + i}"
                elif atype == "VW":
                    addr = f"VW{addr_num + i * 2}"
                elif atype == "VD":
                    addr = f"VD{addr_num + i * 4}"
                else:
                    continue
                defs.append({
                    "type": atype, "address": addr, "doc_type": dtype,
                    "direction": rw, "symbol": var_name, "note": note, "source": "CSV"
                })
    return defs


# ============================================================
# 5. 判断PLC指令读写方向
# ============================================================

# 指令助记符 -> 写操作数的索引集合（0-based，按逗号分隔操作数）。
# 未列出的指令默认未知。
WRITE_OPERAND_INDICES = {
    "=": {0}, "S": {0}, "R": {0},
    "MOV": {1}, "MOVB": {1}, "MOVW": {1}, "MOVD": {1}, "MOVR": {1},
    "FILL": {1},
    "TODR": {0}, "TODW": {0},
    "INCW": {0}, "DECW": {0}, "INCB": {0}, "DECB": {0}, "INCD": {0}, "DECD": {0},
    "+R": {1}, "-R": {1}, "*R": {1}, "/R": {1},
    "+I": {1}, "-I": {1}, "*I": {1}, "/I": {1},
    "+D": {1}, "-D": {1}, "*D": {1}, "/D": {1},
    "BTI": {1}, "ITB": {0}, "ITD": {1}, "DTI": {0}, "DTR": {1}, "RTD": {1},
    "ROUND": {1}, "TRUNC": {1},
    "TON": set(), "TOF": set(), "TONR": set(), "TOFT": set(),
    "TONT": set(), "TOFRT": set(), "TONRT": set(),
}
READ_MNEMONICS = {
    "LD", "LDN", "A", "AN", "O", "ON", "LPS", "LPP", "LRD", "LDS",
    "ALD", "OLD", "NOT", "EU", "ED", "XORB", "XORW", "XORD",
    "LDB=", "LDW=", "LDD=", "LDR=", "AW=", "AD=", "AR=",
    "LDB<>", "LDW<>", "LDD<>", "LDR<>", "AW<>", "AD<>", "AR<>",
    "LDB<", "LDW<", "LDD<", "LDR<", "AW<", "AD<", "AR<",
    "LDB>", "LDW>", "LDD>", "LDR>", "AW>", "AD>", "AR>",
    "LDB<=", "LDW<=", "LDD<=", "LDR<=", "AW<=", "AD<=", "AR<=",
    "LDB>=", "LDW>=", "LDD>=", "LDR>=", "AW>=", "AD>=", "AR>=",
    "JMP", "LBL",
}


def get_mnemonic(context):
    """从上下文中提取指令助记符"""
    stripped = context.lstrip()
    # 取第一个空白或逗号前的部分
    m = re.match(r"([A-Za-z_][A-Za-z0-9_+=<>\-]*)", stripped)
    if m:
        return m.group(1).upper()
    return ""


def _operand_index(context, address):
    """返回地址在上下文操作数列表中的索引；找不到返回 None"""
    # 去掉注释，按逗号分隔
    parts = []
    for p in context.split(','):
        # 去掉每个操作数自身的行内注释
        p = p.split('//')[0].strip()
        parts.append(p)
    addr_norm = address.upper()
    for idx, op in enumerate(parts):
        # 允许 DataPtr 前的 &
        op_clean = op.lstrip('&').upper()
        if re.search(r'(?:^|[^A-Z0-9_])' + re.escape(addr_norm) + r'(?:$|[^A-Z0-9_])', op_clean):
            return idx
    return None


def is_write_context(context, addr_type, address):
    """根据上下文判断该地址是否被PLC写入"""
    upper_ctx = context.upper()
    mnemonic = get_mnemonic(context)

    # 特殊处理 MBUS 库调用：SBR20/SBR21 的输出/缓冲区地址视为写入
    if "CALL" in upper_ctx:
        if "SBR21" in upper_ctx:
            # CALL SBR21, First, Slave, RW, Addr, Count, DataPtr, Done, Error
            idx = _operand_index(context, address)
            if idx is not None:
                return idx >= 6  # DataPtr/Done/Error
            return None
        if "SBR20" in upper_ctx:
            # CALL SBR20, EN, Mode, Baud, Parity, Port, Timeout, Done, Error
            idx = _operand_index(context, address)
            if idx is not None:
                return idx >= 7  # Done/Error
            return None
        # 其他子程序调用无明确方向，返回 None
        return None

    if mnemonic in WRITE_OPERAND_INDICES:
        idx = _operand_index(context, address)
        if idx is None:
            return None
        return idx in WRITE_OPERAND_INDICES[mnemonic]

    if mnemonic in READ_MNEMONICS:
        return False

    # 默认保守：未知指令视为读写都可能
    return None


# ============================================================
# 6. 主对比逻辑
# ============================================================

def main():
    stl_results = load_stl_results()
    md_defs = parse_md_addresses(DOC_MD)
    csv_defs = parse_csv_addresses(DOC_CSV)

    # 合并文档定义，以MD为准，CSV补充；冲突时记录
    doc_addr_map = {}  # canonical -> dict
    for d in md_defs:
        key = canonical_v_addr(d["type"], d["address"]) if is_v_addr(d["type"]) else f"{d['type']}:{d['address']}"
        doc_addr_map[key] = d
        doc_addr_map[key]["sources"] = ["MD"]
    for d in csv_defs:
        key = canonical_v_addr(d["type"], d["address"])
        if key in doc_addr_map:
            doc_addr_map[key]["sources"].append("CSV")
            # 若CSV方向更明确则保留
            if d["direction"] in ("读写", "只读") and doc_addr_map[key]["direction"] in ("未指定", ""):
                doc_addr_map[key]["direction"] = d["direction"]
        else:
            doc_addr_map[key] = d
            doc_addr_map[key]["sources"] = ["CSV"]

    # PLC使用地址集合
    plc_used = defaultdict(list)  # canonical -> list of occurrences
    plc_writes = set()  # canonical addresses written by PLC
    for r in stl_results:
        key = canonical_v_addr(r["type"], r["address"])
        plc_used[key].append(r)
        w = is_write_context(r["context"], r["type"], r["address"])
        if w is True:
            plc_writes.add(key)

    plc_used_keys = set(plc_used.keys())
    doc_keys = set(doc_addr_map.keys())

    # 6.1 PLC用了但文档未定义（仅关注V/I/Q/M区；T/C/SM/L/AC/DT为系统/内部变量，不纳入HMI接口）
    hmi_interface_types = ("V_bit", "VB", "VW", "VD", "I_bit", "Q_bit", "M_bit")
    in_plc_not_doc = {k for k in plc_used_keys - doc_keys if k.split(":")[0] in hmi_interface_types}
    internal_unused = (plc_used_keys - doc_keys) - in_plc_not_doc  # T/C/SM/L/AC/DT等
    # 6.2 文档定义了但PLC未使用
    in_doc_not_plc = doc_keys - plc_used_keys

    # 6.3 数据类型不一致（同一地址在文档和PLC中的类型）
    # 由于PLC中实际使用类型由上下文决定，这里主要检查：
    # - 文档中的VD/VW/VB与实际代码中的VD/VW/VB是否一致
    type_mismatch = []
    for key in plc_used_keys & doc_keys:
        r0 = plc_used[key][0]
        doc = doc_addr_map[key]
        # 如果PLC解析类型与文档类型不同（例如文档VD，PLC代码中用VW）
        if r0["type"] != doc["type"]:
            type_mismatch.append({
                "address": key, "plc_type": r0["type"], "doc_type": doc["type"],
                "symbol": doc.get("symbol", ""), "contexts": plc_used[key][:3]
            })

    # 6.4 读写方向不一致
    # 以下地址是PLC内部计算/状态/统计值，文档对HMI标记为只读是正常的，PLC必须写入，不视为冲突
    PLC_INTERNAL_WRITE_OK = {
        "V_bit:V1.0", "V_bit:V1.1", "V_bit:V1.2", "V_bit:V1.3",
        "V_bit:V1.4", "V_bit:V1.5", "V_bit:V1.6", "V_bit:V1.7",
        "VW:VW2", "VW:VW4", "VW:VW6", "VW:VW8",
        "VD:VD70", "VD:VD74", "VD:VD78",
        "VD:VD90", "VD:VD102", "VD:VD150", "VD:VD154",
        "VD:VD178", "VD:VD312", "VD:VD328", "VD:VD370",
    }
    direction_issues = []
    for key in plc_used_keys & doc_keys:
        doc = doc_addr_map[key]
        if key in plc_writes and doc["direction"] == "只读" and key not in PLC_INTERNAL_WRITE_OK:
            direction_issues.append({
                "address": key, "issue": "PLC写入但文档标记为只读",
                "symbol": doc.get("symbol", ""), "contexts": [o for o in plc_used[key] if is_write_context(o["context"], o["type"], o["address"])][:3]
            })

    # 6.5 地址重叠/冲突
    # 只报告不同粒度之间的重叠：位-字/双字、字节-字/双字、字-双字
    # 同字节内的不同位（如V300.0与V300.1）属于正常按位编码，不视为冲突
    v_ranges = []
    for key in plc_used_keys:
        if not is_v_addr(plc_used[key][0]["type"]):
            continue
        r = addr_to_range(plc_used[key][0]["type"], plc_used[key][0]["address"])
        if r:
            v_ranges.append((key, r, plc_used[key][0]["type"]))

    def granularity(t):
        return {"V_bit": 0, "VB": 1, "VW": 2, "VD": 3}[t]

    def classify_overlap(t1, t2):
        """根据粒度差异对重叠进行分类"""
        g1, g2 = granularity(t1), granularity(t2)
        smaller, larger = (t1, t2) if g1 < g2 else (t2, t1)
        if smaller == "V_bit":
            return "位打包（通常正常）"
        if smaller == "VB":
            return "字节打包（通常正常）"
        if smaller == "VW" and larger == "VD":
            return "字-双字重叠（需重点排查）"
        return "其他粒度重叠"

    overlaps = []
    seen_pairs = set()
    for i in range(len(v_ranges)):
        for j in range(i + 1, len(v_ranges)):
            k1, r1, t1 = v_ranges[i]
            k2, r2, t2 = v_ranges[j]
            if ranges_overlap(r1, r2):
                # 同粒度不报告（同字节内的位属于正常编码）
                if granularity(t1) == granularity(t2):
                    continue
                pair = tuple(sorted([k1, k2]))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                overlaps.append({"addr1": k1, "range1": r1, "type1": t1,
                                 "addr2": k2, "range2": r2, "type2": t2,
                                 "category": classify_overlap(t1, t2)})

    severe_overlaps = [o for o in overlaps if "需重点排查" in o["category"]]
    packed_overlaps = [o for o in overlaps if "打包" in o["category"]]

    # 6.6 命名不一致（简单检查：PLC注释中的用途与文档符号名差异）
    # 此部分较主观，仅列出CSV/MD中符号名带有明显差异的地址
    naming_issues = []

    # ============================================================
    # 7. 生成报告
    # ============================================================
    lines = []
    lines.append("# AQUA-EXPO 项目 HMI-PLC 地址核对报告")
    lines.append("")
    lines.append(f"**生成日期**：2026-07-29")
    lines.append(f"**核对范围**：`d:\\work\\CTI\\plc\\stl` 下全部 {len(set(r['file'] for r in stl_results))} 个 STL 源文件")
    lines.append(f"**接口基准**：")
    lines.append(f"- `{DOC_MD}`")
    lines.append(f"- `{DOC_CSV}`")
    lines.append("")
    lines.append("## 一、核对概览")
    lines.append("")
    lines.append("| 项目 | 数量 | 说明 |")
    lines.append("|---|---|---|")
    lines.append(f"| PLC实际使用地址记录 | {len(stl_results)} | 含重复出现 |")
    lines.append(f"| PLC实际使用唯一地址 | {len(plc_used_keys)} | 去重后 |")
    lines.append(f"| 文档/CSV定义地址 | {len(doc_keys)} | MD+CSV合并去重 |")
    lines.append(f"| PLC用但文档未定义 | {len(in_plc_not_doc)} | 需重点核查 |")
    lines.append(f"| 文档定义但PLC未使用 | {len(in_doc_not_plc)} | 可能已废弃或预留 |")
    lines.append(f"| 类型不一致 | {len(type_mismatch)} | VD/VW/VB 混用 |")
    lines.append(f"| 读写方向冲突 | {len(direction_issues)} | 文档只读但PLC写 |")
    lines.append(f"| 地址重叠/冲突（疑似真正冲突） | {len(severe_overlaps)} | 字-双字等需重点排查 |")
    lines.append(f"| 地址重叠/冲突（位/字节打包） | {len(packed_overlaps)} | 状态字/报警字/时间戳/Modbus缓冲区等打包使用，通常正常 |")
    lines.append("")

    # 严重不一致：读写方向冲突、类型不一致、地址重叠
    lines.append("## 二、严重不一致")
    lines.append("")
    if not direction_issues and not type_mismatch and not severe_overlaps:
        lines.append("未发现严重不一致项。")
    else:
        if direction_issues:
            lines.append("### 2.1 读写方向冲突（文档只读，PLC实际写入）")
            lines.append("")
            lines.append("| 地址 | 文档符号 | 问题描述 | 涉及文件/行号/上下文 | 建议修正 |")
            lines.append("|---|---|---|---|---|")
            for item in direction_issues:
                ctxs = item["contexts"]
                ctx_str = "; ".join([f"{c['file']}:{c['line']} `{c['context']}`" for c in ctxs])
                lines.append(f"| {item['address']} | {item['symbol']} | {item['issue']} | {ctx_str} | 确认文档方向应为'读写'或检查PLC是否误写 |")
            lines.append("")
        if type_mismatch:
            lines.append("### 2.2 数据类型不一致")
            lines.append("")
            lines.append("| 地址 | 文档类型 | PLC实际类型 | 文档符号 | 涉及文件/行号/上下文 | 建议修正 |")
            lines.append("|---|---|---|---|---|---|")
            for item in type_mismatch:
                ctxs = item["contexts"]
                ctx_str = "; ".join([f"{c['file']}:{c['line']} `{c['context']}`" for c in ctxs])
                lines.append(f"| {item['address']} | {item['doc_type']} | {item['plc_type']} | {item['symbol']} | {ctx_str} | 统一文档与代码中的数据类型 |")
            lines.append("")
        if severe_overlaps:
            lines.append("### 2.3 地址重叠/冲突（疑似真正冲突）")
            lines.append("")
            lines.append("| 地址1 | 字节范围1 | 地址2 | 字节范围2 | 重叠类型 | 建议修正 |")
            lines.append("|---|---|---|---|---|---|")
            for item in severe_overlaps:
                r1 = item["range1"]
                r2 = item["range2"]
                range1 = f"VB{r1[0]}~VB{r1[1]-1}" if r1[2] is None else f"V{r1[0]}.{r1[2]}"
                range2 = f"VB{r2[0]}~VB{r2[1]-1}" if r2[2] is None else f"V{r2[0]}.{r2[2]}"
                lines.append(f"| {item['addr1']} | {range1} | {item['addr2']} | {range2} | {item['category']} | 重新分配地址或确认不会同时有效 |")
            lines.append("")

    # 一般不一致：PLC用了但文档未定义
    lines.append("## 三、一般不一致")
    lines.append("")
    if in_plc_not_doc:
        lines.append("### 3.1 PLC程序使用但文档未定义/未说明的地址")
        lines.append("")
        lines.append("> 注：下表包含大量PLC内部中间变量、状态机变量、Modbus缓冲区、定时器转换值等，这些通常无需写入HMI接口文档。建议优先关注V区参数、M区HMI交互位以及与CSV变量命名不一致的地址。")
        lines.append("")
        lines.append("| 地址 | PLC类型 | 出现次数 | 涉及文件/行号（样例） | 建议修正 |")
        lines.append("|---|---|---|---|---|")
        # 按类型分组，优先显示V区/M区/T/C/AC等
        for key in sorted(in_plc_not_doc, key=lambda k: (not k.startswith("VD"), not k.startswith("VW"), not k.startswith("VB"), not k.startswith("V_bit"), k)):
            occs = plc_used[key]
            # 去重文件
            files = sorted(set(o["file"] for o in occs))
            sample = occs[0]
            lines.append(f"| {key} | {sample['type']} | {len(occs)} | {sample['file']}:{sample['line']} `{sample['context']}` | 补充到地址表/CSV或删除无用引用 |")
        lines.append("")
    else:
        lines.append("未发现PLC使用但文档未定义的地址。")
        lines.append("")

    # 文档定义但PLC未使用
    if in_doc_not_plc:
        lines.append("### 3.2 文档/CSV定义但PLC程序未见使用的地址")
        lines.append("")
        lines.append("| 地址 | 文档类型 | 方向 | 符号/备注 | 来源 | 建议修正 |")
        lines.append("|---|---|---|---|---|---|")
        for key in sorted(in_doc_not_plc):
            d = doc_addr_map[key]
            lines.append(f"| {key} | {d['doc_type']} | {d['direction']} | {d.get('symbol', '')} / {d.get('note', '')} | {','.join(d.get('sources', []))} | 确认是否预留/废弃；若废弃则从文档/CSV移除 |")
        lines.append("")

    # 仅文档待更新
    lines.append("## 四、仅文档待更新")
    lines.append("")
    lines.append("### 4.1 注释/命名与文档符号不一致（需澄清）")
    lines.append("")
    lines.append("以下地址在代码注释或CSV变量名中的称呼与地址表符号存在差异，建议统一命名。")
    lines.append("")
    lines.append("| 地址 | 文档符号 | CSV/代码称呼 | 说明 | 建议 |")
    lines.append("|---|---|---|---|---|")
    # 例如 CSV 中 U1_VD_FlowCum 对应文档 VD_FlowMeter_Current
    naming_candidates = [
        ("VD:VD86", "VD_FlowMeter_Current", "U1_VD_FlowCum", "文档称Current，CSV称Cum"),
        ("VW:VW4", "MB_Pump_Status", "U1_VW4_PumpStatus", "CSV未体现Modbus来源"),
        ("VD:VD90", "VD_Current_InletVolume", "U1_VD_FlowDiff", "文档为进水量，CSV为差值"),
    ]
    for key, doc_sym, csv_sym, note in naming_candidates:
        if key in doc_addr_map:
            lines.append(f"| {key} | {doc_sym} | {csv_sym} | {note} | 统一变量命名 |")
    lines.append("")

    lines.append("### 4.2 默认值差异")
    lines.append("")
    lines.append("CSV中部分参数默认值与地址表不一致，需核实：")
    lines.append("")
    lines.append("| 地址 | CSV默认值 | 地址表默认值 | 建议 |")
    lines.append("|---|---|---|---|")
    default_diffs = [
        ("VD:VD350", "0.5", "0.2083", "以地址表0.2083为准，CSV需更新"),
        ("VD:VD354", "3.0", "30.0", "以地址表30.0为准，CSV需更新"),
        ("VD:VD24", "5.0", "480.0", "以地址表480.0为准，CSV需更新"),
        ("VD:VD28", "12.0", "120.0", "以地址表120.0为准，CSV需更新"),
        ("VD:VD32", "3.0", "30.0", "以地址表30.0为准，CSV需更新"),
        ("VD:VD36", "6.0", "60.0", "以地址表60.0为准，CSV需更新"),
        ("VD:VD40", "1.5", "15.0", "以地址表15.0为准，CSV需更新"),
        ("VD:VD44", "0.5", "5.0", "以地址表5.0为准，CSV需更新"),
        ("VD:VD358", "2.0", "60.0", "以地址表60.0为准，CSV需更新"),
        ("VD:VD362", "2.0", "60.0", "以地址表60.0为准，CSV需更新"),
        ("VD:VD54", "2.0", "60.0", "以地址表60.0为准，CSV需更新"),
        ("VD:VD58", "2.0", "10.0", "以地址表10.0为准，CSV需更新"),
        ("VD:VD62", "2.0", "10.0", "以地址表10.0为准，CSV需更新"),
        ("VD:VD66", "0.5", "5.0", "以地址表5.0为准，CSV需更新"),
        ("VD:VD112", "20.0", "—", "CSV有默认值但地址表未列，需补充"),
        ("VD:VD116", "0.0", "—", "CSV有默认值但地址表未列，需补充"),
        ("VD:VD120", "12.0", "—", "CSV有默认值但地址表未列，需补充"),
        ("VD:VD124", "6.0", "—", "地址表已迁移至VD128，CSV未同步"),
        ("VD:VD174", "5.0", "—", "CSV中S3估算，地址表未定义"),
        ("VD:VD316", "10.0", "—", "CSV中目标进水量，地址表未定义"),
        ("VD:VD308", "0.0", "—", "CSV中关阀快照，地址表未定义"),
        ("VD:VD150", "—", "—", "PLC实测值，CSV只读，地址表未定义"),
        ("VD:VD154", "—", "—", "PLC中间值，CSV只读，地址表未定义"),
        ("VD:VD178", "—", "—", "PLC实测值S5_Elapsed，CSV只读，地址表未定义"),
        ("VD:VD312", "—", "—", "PLC中间值LeakDiff，CSV只读，地址表未定义"),
        ("VD:VD328", "—", "—", "PLC中间值Timeout_ValveC_x10，CSV只读，地址表未定义"),
    ]
    for key, csv_val, doc_val, note in default_diffs:
        lines.append(f"| {key} | {csv_val} | {doc_val} | {note} |")
    lines.append("")

    # 建议澄清
    lines.append("## 五、建议澄清")
    lines.append("")
    lines.append("### 5.1 关键 recently changed 地址核查")
    lines.append("")
    lines.append("以下地址在FC4/FC0/OB1中 recently changed，建议逐一确认文档已同步：")
    lines.append("")
    lines.append("| 地址 | 涉及文件 | 状态 | 建议 |")
    lines.append("|---|---|---|---|")
    recent_addrs = ["M_bit:M10.0", "M_bit:M10.1", "M_bit:M10.2", "M_bit:M10.3", "M_bit:M10.4", "M_bit:M10.5",
                    "VB:VB378", "VB:VB379", "VB:VB384",
                    "VW:VW290", "VW:VW292", "VW:VW294", "VW:VW296"]
    for key in recent_addrs:
        if key in plc_used:
            files = sorted(set(o["file"] for o in plc_used[key]))
            in_doc = "✅ 已定义" if key in doc_keys else "❌ 未定义"
            lines.append(f"| {key} | {', '.join(files)} | {in_doc} | {'文档已同步，保持' if key in doc_keys else '需补充到地址表/CSV'} |")
    lines.append("")

    lines.append("### 5.2 未解析或异常地址")
    lines.append("")
    lines.append("以下地址类型在STL中出现但文档未明确规划，或属于内部临时变量：")
    lines.append("")
    lines.append("| 类型 | 示例地址 | 说明 | 建议 |")
    lines.append("|---|---|---|---|")
    type_examples = defaultdict(set)
    for key in plc_used:
        t = plc_used[key][0]["type"]
        type_examples[t].add(key)
    for t in sorted(type_examples):
        if t in ("L_bit", "L_word", "L_dword", "AC"):
            examples = sorted(type_examples[t])[:5]
            lines.append(f"| {t} | {', '.join(examples)}{'...' if len(type_examples[t])>5 else ''} | STL局部变量/累加器 | 无需进入HMI文档 |")
        elif t == "SM":
            examples = sorted(type_examples[t])[:5]
            lines.append(f"| {t} | {', '.join(examples)}{'...' if len(type_examples[t])>5 else ''} | 系统特殊存储器 | 无需进入HMI文档，但应在PLC设计文档说明 |")
    lines.append("")

    if packed_overlaps:
        lines.append("### 5.3 地址重叠/冲突（位/字节打包使用，通常正常）")
        lines.append("")
        lines.append("以下地址存在不同粒度重叠，但多为状态字/报警字/时间戳/Modbus缓冲区位打包使用，通常正常，建议人工复核确认：")
        lines.append("")
        lines.append("| 地址1 | 字节范围1 | 地址2 | 字节范围2 | 重叠类型 | 涉及文件（样例） | 建议 |")
        lines.append("|---|---|---|---|---|---|---|")
        for item in packed_overlaps:
            r1 = item["range1"]
            r2 = item["range2"]
            range1 = f"VB{r1[0]}~VB{r1[1]-1}" if r1[2] is None else f"V{r1[0]}.{r1[2]}"
            range2 = f"VB{r2[0]}~VB{r2[1]-1}" if r2[2] is None else f"V{r2[0]}.{r2[2]}"
            sample = plc_used[item['addr1']][0]
            lines.append(f"| {item['addr1']} | {range1} | {item['addr2']} | {range2} | {item['category']} | {sample['file']}:{sample['line']} | 确认属于位/字节打包后保持现状 |")
        lines.append("")

    lines.append("## 六、附录：核对方法说明")
    lines.append("")
    lines.append("1. **地址提取**：使用正则表达式从STL源码中提取V/I/Q/M/SM/T/C/DT/AC/L区地址，保留文件、行号、指令上下文。")
    lines.append("2. **文档基准**：合并 `HMI-PLC变量地址表_v1.0.md` 与 `McgsPro变量导入_8单元_v2.0.csv` 中的地址定义。")
    lines.append("3. **读写方向判断**：根据STL指令助记符（=、S、R、MOVx、MOVR、FILL、+R/-R/*R等）判断PLC是否写入该地址。")
    lines.append("4. **地址重叠**：将V区地址统一换算为字节范围，检测范围交集。")
    lines.append("5. **分级原则**：")
    lines.append("   - **严重不一致**：读写方向冲突、数据类型不一致、地址重叠冲突。")
    lines.append("   - **一般不一致**：PLC使用但文档未定义、文档定义但PLC未使用。")
    lines.append("   - **仅文档待更新**：命名差异、默认值差异。")
    lines.append("   - **建议澄清**：recently changed地址、内部/系统变量等需人工确认项。")
    lines.append("")

    with open(REPORT_MD, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"报告已生成: {REPORT_MD}")


if __name__ == "__main__":
    main()
