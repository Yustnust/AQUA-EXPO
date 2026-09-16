import os,re,csv
from collections import defaultdict

# Read PLC addresses usage
plc_usage = {}
with open(r"d:\work\CTI\archive\mcgspro\plc_addresses.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        parts = line.split("\t")
        if len(parts) >= 3:
            plc_usage[parts[0]] = {"rw": parts[1], "files": parts[2]}

# Read channel processing CSV
csv_map = {}
csv_rows = []
with open(r"d:\work\CTI\archive\mcgspro\csv_output\西门子_S7_Smart200_以太网_通道处理.csv", "r", encoding="gbk") as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i < 5 or len(row) < 9: continue
        if not row[0].isdigit(): continue
        csv_rows.append(row)
        # Map address from channel_name (e.g. 只读I000.0, 读写V000.0, 只读VDF070, 只读VBUB305)
        chan = row[3]
        # Extract the address part after the rw prefix
        m = re.match(r"(只读|读写)([IQMV]+)(.+)", chan)
        if m:
            rw, area, addr_str = m.groups()
            csv_map[chan] = row[1]

# Normalize address key for comparison
def normalize(addr):
    """Convert PLC scan address to CSV channel name format"""
    # I0.0 -> I000.0, Q0.0 -> Q000.0, V0.0 -> V000.0, VD70 -> VDF070, VB305 -> VBUB305, VW2 -> VWB002
    # For bit addresses: I0.0 -> 只读I000.0
    # For V bits: V0.0 -> V000.0
    # For V bytes: VB305 -> VBUB305
    # For V words: VW2 -> VWB002
    # For V doubles: VD70 -> VDF070
    if re.match(r"^[IQMV]\d+\.\d+$", addr):
        prefix = addr[0]
        num, bit = addr[1:].split(".")
        return f"{prefix}{int(num):03d}.{bit}"
    if addr.startswith("VB"):
        return f"VBUB{int(addr[2:]):03d}"
    if addr.startswith("VW"):
        return f"VWB{int(addr[2:]):03d}"
    if addr.startswith("VD"):
        return f"VDF{int(addr[2:]):03d}"
    return addr

# Build comparison report
report = []
report.append("# HMI-PLC 地址映射差异报告")
report.append("")

# 1. CSV variables not used in PLC code (suspect stale)
report.append("## 1. 通道处理.csv中有但PLC代码中未使用的地址（建议删除或标记为保留）")
stale = []
for row in csv_rows:
    chan = row[3]
    if chan not in csv_map: continue
    name = row[1]
    norm = None
    m = re.match(r"(只读|读写)([IQMV]+)(.+)", chan)
    if m:
        area, addr_str = m.group(2), m.group(3)
        # Convert addr_str to PLC scan format for lookup
        if area in ("I", "Q", "M") and "." in addr_str:
            # I000.0 -> I0.0
            num, bit = addr_str.split(".")
            norm = f"{area}{int(num)}.{bit}"
        elif area == "V" and "." in addr_str:
            num, bit = addr_str.split(".")
            norm = f"V{int(num)}.{bit}"
        elif area == "V" and addr_str.startswith("BUB"):
            norm = f"VB{int(addr_str[3:])}"
        elif area == "V" and addr_str.startswith("WB"):
            norm = f"VW{int(addr_str[2:])}"
        elif area == "V" and addr_str.startswith("DF"):
            norm = f"VD{int(addr_str[2:])}"
    if norm and norm not in plc_usage:
        stale.append((row[0], name, chan, norm))

report.append(f"共 {len(stale)} 个：")
report.append("")
report.append("| 通道 | HMI变量名 | 通道地址 | PLC地址 |")
report.append("|------|-----------|----------|---------|")
for ch, name, chan, norm in stale:
    report.append(f"| {ch} | {name} | {chan} | {norm} |")

# 2. PLC addresses not in CSV (missing in HMI)
report.append("")
report.append("## 2. PLC代码中使用但通道处理.csv中缺失的地址（需要补充到HMI）")
missing = []
for addr in sorted(plc_usage.keys()):
    norm = normalize(addr)
    # Build possible channel names with both 只读 and 读写
    found = False
    for prefix in ["只读", "读写"]:
        if prefix + norm in csv_map:
            found = True
            break
    if not found:
        missing.append((addr, norm, plc_usage[addr]["rw"], plc_usage[addr]["files"]))

report.append(f"共 {len(missing)} 个：")
report.append("")
report.append("| PLC地址 | 标准化 | 读写 | 使用文件 |")
report.append("|---------|--------|------|----------|")
for addr, norm, rw, files in missing:
    report.append(f"| {addr} | {norm} | {rw} | {files} |")

with open(r"d:\work\CTI\archive\mcgspro\mapping_diff_report.md", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print(f"CSV variables not in PLC: {len(stale)}")
print(f"PLC addresses missing in CSV: {len(missing)}")
