import os,re,json
from collections import defaultdict

stl_dir = r"d:\work\CTI\plc\stl"

# Patterns for PLC addresses
# V memory: VB, VW, VD, Vx.y bit
# I, Q, M, T, SM, S, AC, HC
addr_pattern = re.compile(r"\b([VQMISMT])([BWD]?)(\d+)(?:\.(\d+))?\b")
sm_pattern = re.compile(r"\b(SM\d+(?:\.\d+)?)\b")

usage = defaultdict(lambda: {"files": set(), "lines": [], "writes": False, "reads": False})

write_ops = ["S", "R", "MOV", "MOVB", "MOVW", "MOVD", "MOVR", "DTR", "ITD", "ROUND", "+R", "-R", "*R", "/R", "INC", "DEC", "TON", "TOF", "TP"]

for fname in sorted(os.listdir(stl_dir)):
    if not fname.endswith(".stl"): continue
    fpath = os.path.join(stl_dir, fname)
    try:
        with open(fpath, "r", encoding="utf-8") as f: lines = f.readlines()
    except:
        with open(fpath, "r", encoding="gbk") as f: lines = f.readlines()
    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith("//"): continue
        # Determine if this is a write-like instruction
        is_write = any(line.startswith(op) or (" " + op + " ") in line for op in write_ops)
        # Extract addresses
        for m in addr_pattern.finditer(line):
            prefix, size, num, bit = m.groups()
            if prefix == "T" and not size: size = ""  # Timer like T49
            if prefix in "MQ" and not size and bit: size = ""  # bit like M16.0
            if prefix == "V" and not size and not bit: continue  # skip bare V
            if bit:
                addr = f"{prefix}{num}.{bit}"
            else:
                addr = f"{prefix}{size}{num}"
            usage[addr]["files"].add(fname)
            usage[addr]["lines"].append((fname, i+1, line[:100]))
            if is_write: usage[addr]["writes"] = True
            else: usage[addr]["reads"] = True
        for m in sm_pattern.finditer(line):
            addr = m.group(1)
            usage[addr]["files"].add(fname)
            usage[addr]["lines"].append((fname, i+1, line[:100]))
            usage[addr]["reads"] = True

output = []
for addr in sorted(usage.keys(), key=lambda x: (x[0], int(re.search(r"\d+", x).group()))):
    info = usage[addr]
    rw = ""
    if info["writes"] and info["reads"]: rw = "读写"
    elif info["writes"]: rw = "写"
    else: rw = "读"
    files = ", ".join(sorted(info["files"]))
    output.append(f"{addr}\t{rw}\t{files}")

with open(r"d:\work\CTI\archive\mcgspro\plc_addresses.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))
print(f"Found {len(output)} addresses")
