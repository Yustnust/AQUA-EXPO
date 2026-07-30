#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析PLC STL源文件中的地址，输出结构化结果供HMI-PLC文档校核。
"""
import os
import re
import json
import csv
from collections import defaultdict

STL_DIR = r"d:\work\CTI\plc\stl"
OUT_JSON = r"d:\work\CTI\stl_address_extract.json"
OUT_CSV = r"d:\work\CTI\stl_address_extract.csv"

# 地址正则（按优先级排序：先匹配长的类型，再匹配短的位）
# 注意：必须避免将 VD10 拆成 V + D10，因此先匹配 VD/VW/VB/SM/DT/AC，再匹配 V/I/Q/M/L 位
ADDRESS_PATTERNS = [
    # 双字/字/字节/特殊
    ("VD", r"\bVD\d+\b"),
    ("VW", r"\bVW\d+\b"),
    ("VB", r"\bVB\d+\b"),
    ("SM", r"\bSM\d+(?:\.\d+)?\b"),
    ("DT", r"\bDT\d+\b"),
    ("AC", r"\bAC\d+\b"),
    ("T",  r"\bT\d+\b"),
    ("C",  r"\bC\d+\b"),
    # 位地址
    ("V_bit",  r"\bV\d+\.\d+\b"),
    ("I_bit",  r"\bI\d+\.\d+\b"),
    ("Q_bit",  r"\bQ\d+\.\d+\b"),
    ("M_bit",  r"\bM\d+\.\d+\b"),
    ("L_bit",  r"\bL\d+\.\d+\b"),
    ("L_word", r"\bLB\d+\b"),
    ("L_word", r"\bLW\d+\b"),
    ("L_dword",r"\bLD\d+\b"),
]


def normalize_address(addr_type, addr):
    """统一地址格式，用于后续对比"""
    return f"{addr_type}:{addr}"


def parse_file(path):
    results = []
    filename = os.path.basename(path)
    with open(path, 'r', encoding='utf-8') as f:
        for line_no, raw_line in enumerate(f, 1):
            line = raw_line.rstrip('\n')
            # 跳过纯注释行，但保留NETWORK/LBL等上下文信息
            if line.strip().startswith('//') or not line.strip():
                continue
            # 去掉行尾注释部分，避免注释中的地址干扰（如符号说明里重复出现）
            code_part = line.split('//')[0]
            for addr_type, pattern in ADDRESS_PATTERNS:
                for m in re.finditer(pattern, code_part, flags=re.IGNORECASE):
                    addr = m.group(0).upper()
                    # 局部变量 L60.0/L63.7 等属于STL临时中转，单独标记
                    results.append({
                        "file": filename,
                        "line": line_no,
                        "type": addr_type,
                        "address": addr,
                        "context": line.strip()
                    })
    return results


def main():
    all_results = []
    for fname in sorted(os.listdir(STL_DIR)):
        if fname.lower().endswith('.stl'):
            fpath = os.path.join(STL_DIR, fname)
            all_results.extend(parse_file(fpath))

    # 写JSON
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 写CSV
    with open(OUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["file", "line", "type", "address", "context"])
        writer.writeheader()
        writer.writerows(all_results)

    print(f"已解析 {len(all_results)} 条地址记录")
    print(f"JSON: {OUT_JSON}")
    print(f"CSV:  {OUT_CSV}")

    # 打印统计
    by_file = defaultdict(int)
    by_type = defaultdict(int)
    unique_addrs = set()
    for r in all_results:
        by_file[r["file"]] += 1
        by_type[r["type"]] += 1
        unique_addrs.add((r["type"], r["address"]))

    print("\n=== 按文件统计 ===")
    for k, v in sorted(by_file.items()):
        print(f"  {k}: {v}")
    print("\n=== 按类型统计 ===")
    for k, v in sorted(by_type.items()):
        print(f"  {k}: {v}")
    print(f"\n唯一地址数: {len(unique_addrs)}")


if __name__ == "__main__":
    main()
