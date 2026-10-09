# -*- coding: utf-8 -*-
import io, re, sys

AWL = r'D:\work\CTI\plc\spec\plc_export_20261009.awl'
t = io.open(AWL, 'r', encoding='gb18030').read()

# 1. 列出所有块
print("=== 块清单 ===")
for m in re.finditer(r'^\s*(ORGANIZATION_BLOCK|FUNCTION_BLOCK|SUBROUTINE_BLOCK|DATA_BLOCK)\s+"?([^":\s]+)"?\s*:?\s*(.*)$', t, re.M):
    print(m.group(1), '|', m.group(2), '|', m.group(3)[:60])

# 2. 按块切分
blocks = {}
parts = re.split(r'(?m)^(ORGANIZATION_BLOCK|FUNCTION_BLOCK|SUBROUTINE_BLOCK|DATA_BLOCK)\s+"?([^":\s]+)"?', t)
# parts: [pre, kind, name, body, kind, name, body, ...]
for i in range(1, len(parts) - 2, 3):
    kind, name, body = parts[i], parts[i+1], parts[i+2]
    blocks[name] = (kind, body)

# 3. 关键标记检查
MARKERS = {
    'PumpEngine':     ['T105', 'V62.5', u'泵未就绪自愈块', u'直接进状态1'],
    'WarmRecovery':   [u'v2.5.1新增', 'V307.2', u'断电恢复清注射泵Modbus'],
    'ManualSyringePump': [u'v2.5.1', 'VD452, VD372', u'直接置VW226=1'],
    'ModbusPolling':  ['VW224, 97', u'初始化瞬态按空闲处理'],
}
print("\n=== v2.5.1 标记检查 ===")
for name, (kind, body) in sorted(blocks.items()):
    for target, markers in MARKERS.items():
        if target.lower() in name.lower():
            print(f"[{name}] ({kind})")
            for mk in markers:
                print('   ', 'FOUND ' if mk in body else 'MISSING', mk)

# 4. 单独打印 PumpEngine 全文(截断)
if 'PumpEngine' in blocks:
    kind, body = blocks['PumpEngine']
    print(f"\n=== PumpEngine 全文 ({len(body)} chars) ===")
    print(body[:8000])
