# -*- coding: utf-8 -*-
import io, re

AWL = r'D:\work\CTI\plc\spec\plc_export_20261009.awl'
t = io.open(AWL, 'r', encoding='gb18030').read()
parts = re.split(r'(?m)^(ORGANIZATION_BLOCK|FUNCTION_BLOCK|SUBROUTINE_BLOCK|DATA_BLOCK)\s+"?([^":\s]+)"?', t)
blocks = {}
for i in range(1, len(parts) - 2, 3):
    blocks[parts[i+1]] = (parts[i], parts[i+2])

def code_only(body):
    # 去掉 // 注释行,只看真实指令
    return '\n'.join(l for l in body.splitlines() if not l.strip().startswith('//'))

checks = [
    ('PumpEngine',     'TON    T102',   1, 'T102驱动点(应为1处)'),
    ('PumpEngine',     'TON    T105',   1, 'T105宽限定时器'),
    ('PumpEngine',     'R      V62.5',  3, 'V62.5清除点(NET1/状态99/消费段)'),
    ('WarmRecovery',   'R      M11.6, 3', 1, 'SBR26清写握手'),
    ('WarmRecovery',   'R      V307.2, 2', 1, 'SBR26清手动命令位'),
    ('WarmRecovery',   'MOVD   0, VD232', 1, 'SBR26清写地址缓冲'),
    ('ManualSyringePump', 'MOVW   1, VW226', 1, 'FC21启动直置状态1'),
    ('ModbusPolling',  'LDW=   VW224, 97', 1, 'FC4的97归一化'),
    ('MAIN',           'A      M17.0',  1, 'OB1手动残留清除'),
]
for name, pat, expect, desc in checks:
    if name not in blocks:
        print(f'[{name}] 块不存在!'); continue
    body = code_only(blocks[name][1])
    n = body.count(pat)
    flag = 'OK' if n == expect else '!!MISMATCH!!'
    print(f'{flag} [{name}] {desc}: 实际{n}处 / 预期{expect}处  ({pat})')

# MAIN 里确认 CALL PumpEngine 调用存在
body = code_only(blocks['MAIN'][1])
print('\nMAIN 中 CALL 清单:')
for m in re.finditer(r'CALL\s+(\w+)', body):
    print('  ', m.group(1))
