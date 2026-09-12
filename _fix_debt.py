with open('docs/技术债务清单_v1.0.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 更新总览统计数字
content = content.replace(
    '共登记技术债务 **34 项**:代码债务 16 / 测试债务 5 / 文档债务 5 / 设计债务 4 / 基础设施债务 2。其中P0立即 **3 项**(TD025/TD026 为 2026-09-11 现场联机新发现),P1高 **13 项**,P2中 **10 项**,P3低 **6 项**。已修复 1 项(TD004/AQEX-36),已删除 2 项(TD002/TD013)。',
    '共登记技术债务 **35 项**:代码债务 17 / 测试债务 5 / 文档债务 5 / 设计债务 4 / 基础设施债务 2。其中P0立即 **0 项**(v2.0全部已修复),P1高 **13 项**,P2中 **11 项**,P3低 **6 项**。**已修复 4 项**(TD004/AQEX-36 + TD025/026/027/AQEX-49 + TD029/AQEX-49),已删除 2 项(TD002/TD013)。'
)

# 2. TD025 标记已修复
content = content.replace(
    '| TD025     | FC15借用VD384当临时变量覆盖手动注射泵参数:FC15 L77-79用`MOVR VD382,VD384`/`*R 10.0,VD384`/`ROUND VD384,AC0`计算T61 PT,但VD384是HMI参数ManualDose_Target | 2026-09-11现场联机调试:手动注射泵总加药量设5000后,进S4状态被覆盖为VD382×10≈18000 | 手动注射泵参数保存后丢失,FC21启动时取错误剩余药量 | **P0** | PLC工程师 | v1.0 | 待修复(AQEX-49)',
    '| TD025     | FC15借用VD384当临时变量覆盖手动注射泵参数:FC15 L77-79用`MOVR VD382,VD384`/`*R 10.0,VD384`/`ROUND VD384,AC0`计算T61 PT,但VD384是HMI参数ManualDose_Target | 2026-09-11现场联机调试:手动注射泵总加药量设5000后,进S4状态被覆盖为VD382×10≈18000 | 手动注射泵参数保存后丢失,FC21启动时取错误剩余药量 | **P0** | PLC工程师 | v1.0 | **✅已修复(AQEX-49, 2026-09-12)** | 改 FC15 用 VD324 (3行) |'
)

# 3. TD026 标记已修复
content = content.replace(
    '| TD026     | VB380~VB383(MBUS_MSG Error)与VD380/382/384(V区变量)物理重叠:FC4 4个CALL MBUS_MSG Error输出到VB380~383,同时VD382(VB382~VB385)是HMI参数S4WaitTimeout,VD384是ManualDose_Target,VB380~381还被VW380(FC11/15/17定时器暂存)覆盖 | 2026-09-11现场联机调试:VD382写入1800后被MBUS_MSG Error=0改写VB382,浮点指数位清零→值变4.23E-37;VD384被FC15 Bug A叠加破坏 | HMI参数无法保存,MBUS_MSG每轮询一次就污染一次(200~500ms周期),IEEE-754浮点指数位被Error=0清零是确定性破坏 | **P0** | PLC工程师 | v1.0 | 待修复(AQEX-49)',
    '| TD026     | VB380~VB383(MBUS_MSG Error)与VD380/382/384/VW380(V区变量)物理重叠:FC4 4个CALL MBUS_MSG Error输出到VB380~383,同时VD382(VB382~VB385)是HMI参数S4WaitTimeout,VD384是ManualDose_Target,VB380~381还被VW380(FC11/15/17定时器暂存)覆盖 | 2026-09-11现场联机调试:VD382写入1800后被MBUS_MSG Error=0改写VB382,浮点指数位清零→值变4.23E-37;VD384被FC15 Bug A叠加破坏 | HMI参数无法保存,MBUS_MSG每轮询一次就污染一次(200~500ms周期),IEEE-754浮点指数位被Error=0清零是确定性破坏 | **P0** | PLC工程师 | v1.0 | **✅已修复(AQEX-49, 2026-09-12)** | MBUS Error原地独占,5个冲突变量迁到VB414~VB499空闲区 |'
)

# 4. TD027 标记已修复 — 用 RunCommand 之前看到的精确行
# 直接找 "待修复(AQEX-49,改CSV即可)" 替换
content = content.replace(
    '待修复(AQEX-49,改CSV即可)',
    '**✅已修复(AQEX-49, 2026-09-11)** | CSV改为读写,MCGS重导'
)

# 5. 在 "| TD028 | 参数范围校验" 之前加 TD029/TD030
old_block = '| TD028 | 参数范围校验未实现'
new_block = '''| **TD029** | **【⚠v2.0 Python扫描新发现, 2026-09-12】** VD378(累计加药量Dosed_Volume_Total, FC13写)与MBUS_CTRL Error(VB378)物理重叠:MBUS_CTRL Error写VB378,同时VD378(VB378~VB381)是累计加药量REAL(4字节) | VD378=VB378~VB381的前2字节被MBUS Error每周期覆盖 | 累计加药量永远不准,HMI显示污染值 | **P0** | PLC工程师 | v1.0 | **✅已修复(AQEX-49, 2026-09-12)** | VD378迁到VD440 |
| **TD030** | **【⚠v2.0 新增, 2026-09-12】** VD10/VD14浓度参数与DT10 RTC时间戳(VB10~VB17)物理重叠:FC15写RTC覆盖浓度 | 每次S4完成时DT10写VB10~17,覆盖VD10/VD14,虽然冷启动重新初始化但运行中可能丢失 | 浓度计算FC13可能使用被RTC污染的VD10/VD14值 | **P0** | PLC工程师 | v1.0 | **✅已修复(AQEX-49, 2026-09-12)** | 浓度参数删除,DT10原地独占 |
| TD028 | 参数范围校验未实现'''

content = content.replace(old_block, new_block)

with open('docs/技术债务清单_v1.0.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ 技术债务清单 更新完成')
print('  - 总览: P0从3→0, 已修复从1→4')
print('  - TD025/026/027 标记已修复(AQEX-49)')
print('  - 新增 TD029: P0-4 VD378 vs MBUS_CTRL Error')
print('  - 新增 TD030: P0-1 DT10 vs VD10/VD14 (浓度删除解决)')
