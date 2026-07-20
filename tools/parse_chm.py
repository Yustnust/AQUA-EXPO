"""
简易CHM解析器:提取McgsProHelp.chm中的HTML/文本内容
CHM格式=ITSF容器+LZX压缩+HTML文件清单
"""
import struct
import os
import sys
import re

CHM_FILE = '/workspace/AQUA-EXPO/McgsProHelp.chm'

with open(CHM_FILE, 'rb') as f:
    data = f.read()

print(f"文件大小: {len(data)} bytes ({len(data)/1024/1024:.2f} MB)")
print(f"前4字节: {data[:4]}")  # 应为 ITSF

magic = data[:4].decode('ascii', errors='replace')
print(f"魔数: {magic}")

if magic == 'ITSF':
    version = struct.unpack('<I', data[4:8])[0]
    print(f"ITSF版本: {version}")
    
    if version == 3:
        # 查找内容段
        markers = [b'::DataSpace', b'#SYSTEM', b'#STRINGS', b'#URLTBL', b'#URLStr', b'#TOPICS', b'#OBJTYPES']
        for m in markers:
            idx = data.find(m)
            if idx >= 0:
                print(f"  找到标记 {m.decode()}: offset=0x{idx:x}")

print("\n--- 查找HTML文件路径 ---")
html_paths = set()
for m in re.finditer(rb'[\x20-\x7f]+\.html?', data):
    path = m.group().decode('ascii', errors='replace').strip('\x00')
    if 5 < len(path) < 200 and '/' in path:
        html_paths.add(path)

print(f"找到HTML路径数: {len(html_paths)}")
for p in sorted(html_paths)[:30]:
    print(f"  {p}")

print("\n--- 查找中文标题(UTF-16LE) ---")
cn_titles = set()
for m in re.finditer(rb'(?:[\x4e-\x9f][\x00]){2,30}', data):
    try:
        title = m.group().decode('utf-16-le').strip()
        if 2 < len(title) < 80:
            cn_titles.add(title)
    except:
        pass

print(f"找到中文串数: {len(cn_titles)}")
for t in sorted(cn_titles)[:80]:
    print(f"  {t}")

print("\n--- 查找GBK中文标题 ---")
gbk_titles = set()
for m in re.finditer(rb'(?:[\xb0-\xf7][\x40-\xfe]){3,30}', data):
    try:
        title = m.group().decode('gbk').strip()
        if 4 < len(title) < 80:
            gbk_titles.add(title)
    except:
        pass

print(f"找到GBK中文串数: {len(gbk_titles)}")
for t in sorted(gbk_titles)[:80]:
    print(f"  {t}")
