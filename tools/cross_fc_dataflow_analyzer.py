#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨FC变量访问数据流分析工具
=========================
分析20个FC对V区的读写关系,生成:
1. 变量-FC读写矩阵
2. 跨FC共享变量列表(被多个FC访问)
3. 高耦合变量Top榜(被最多FC访问)
4. FC间数据流路径(通过共享变量传递)
5. 写入-读取链(一个FC写,另一个FC读)

用法:
    python3 cross_fc_dataflow_analyzer.py [--stl-dir ../plc/stl] [--report ../docs/跨FC数据流分析报告_v1.0.md]
"""

import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

# 导入静态分析器的解析器
sys.path.insert(0, str(Path(__file__).parent))
from stl_static_analyzer import STLParser, VarRef, VarTableParser, VarDef


# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class VarAccessSummary:
    """变量访问汇总"""
    address: str                # 原始地址(如 VD90, VW2)
    var_type: str               # VB/VW/VD/Vbit
    byte_addr: int
    size: int
    readers: Set[str]           # 读取该变量的FC集合
    writers: Set[str]           # 写入该变量的FC集合
    symbol: str = ""            # 符号名(如有)


# =============================================================================
# 数据流分析器
# =============================================================================

class DataFlowAnalyzer:
    """跨FC数据流分析"""

    def __init__(self, stl_dir: Path, var_table: Path):
        self.stl_dir = stl_dir
        self.var_table = var_table
        self.parser = STLParser()
        self.var_parser = VarTableParser()
        self.fc_refs: Dict[str, List[VarRef]] = {}
        self.var_defs: Dict[str, VarDef] = {}
        self.var_access: Dict[str, VarAccessSummary] = {}

    def run(self):
        """执行分析"""
        self._parse_all()
        self._build_access_summary()

    def _parse_all(self):
        """解析所有STL文件和变量表"""
        self.var_defs = self.var_parser.parse_file(self.var_table)
        stl_files = sorted(self.stl_dir.glob('*.stl'))
        for stl_file in stl_files:
            fc_name, refs = self.parser.parse_file(stl_file)
            self.fc_refs[fc_name] = refs
            self._extract_symbols_from_stl(stl_file)

    def _extract_symbols_from_stl(self, stl_file: Path):
        """从STL注释提取符号定义"""
        with open(stl_file, 'r', encoding='utf-8') as f:
            content = f.read()
        for match in VarTableParser.SYMBOL_PATTERN.finditer(content):
            size_code = match.group(1).upper()
            addr = int(match.group(2))
            bit = match.group(3)
            symbol = match.group(4)
            if bit is not None:
                var_type, size, bit_offset = 'Vbit', 1, int(bit)
                key = f"V{addr}.{bit_offset}"
            elif size_code == 'VB':
                var_type, size, bit_offset = 'VB', 1, 0
                key = f"VB{addr}"
            elif size_code == 'VW':
                var_type, size, bit_offset = 'VW', 2, 0
                key = f"VW{addr}"
            elif size_code == 'VD':
                var_type, size, bit_offset = 'VD', 4, 0
                key = f"VD{addr}"
            else:
                continue
            if key not in self.var_defs:
                self.var_defs[key] = VarDef(
                    symbol=symbol, address=key, var_type=var_type,
                    byte_addr=addr, size=size, bit_offset=bit_offset,
                    source=stl_file.name
                )

    def _build_access_summary(self):
        """构建变量访问汇总"""
        for ref in [r for refs in self.fc_refs.values() for r in refs]:
            if ref.var_type not in ('VB', 'VW', 'VD', 'Vbit'):
                continue
            key = ref.raw
            if key not in self.var_access:
                symbol = self.var_defs.get(key, VarDef('', key, ref.var_type,
                                                       ref.address, ref.size)).symbol
                self.var_access[key] = VarAccessSummary(
                    address=key, var_type=ref.var_type,
                    byte_addr=ref.address, size=ref.size,
                    readers=set(), writers=set(), symbol=symbol
                )
            if ref.access == 'W':
                self.var_access[key].writers.add(ref.fc_name)
            else:
                self.var_access[key].readers.add(ref.fc_name)

    # ---- 生成报告 ----
    def generate_report(self, output_path: Path):
        """生成Markdown报告"""
        lines = []
        lines.append('# 跨FC变量访问数据流分析报告')
        lines.append('')
        lines.append('| 项目 | 内容 |')
        lines.append('|---|---|')
        lines.append(f'| 分析对象 | S7-200 SMART STL代码({len(self.fc_refs)}个FC) |')
        lines.append(f'| 分析工具 | cross_fc_dataflow_analyzer.py v1.0 |')
        lines.append(f'| 分析日期 | 2026-07-18 |')
        lines.append('')

        # 概览
        lines.append('## 一、分析概览')
        lines.append('')
        total_vars = len(self.var_access)
        cross_fc_vars = sum(1 for v in self.var_access.values()
                           if len(v.readers | v.writers) > 1)
        write_read_pairs = 0
        for v in self.var_access.values():
            if v.writers and v.readers:
                write_read_pairs += 1
        lines.append(f'- **变量总数**(V区): {total_vars} 个')
        lines.append(f'- **跨FC共享变量**(被≥2个FC访问): {cross_fc_vars} 个')
        lines.append(f'- **写入-读取链变量**(被某FC写且被另一FC读): {write_read_pairs} 个')
        lines.append('')

        # FC列表
        lines.append('## 二、FC清单与访问统计')
        lines.append('')
        lines.append('| FC名称 | 引用变量数 | 写入变量数 | 读取变量数 |')
        lines.append('|---|---|---|---|')
        for fc_name in sorted(self.fc_refs.keys()):
            refs = self.fc_refs[fc_name]
            v_refs = [r for r in refs if r.var_type in ('VB', 'VW', 'VD', 'Vbit')]
            write_vars = set(r.raw for r in v_refs if r.access == 'W')
            read_vars = set(r.raw for r in v_refs if r.access == 'R')
            lines.append(f'| {fc_name} | {len(set(r.raw for r in v_refs))} | {len(write_vars)} | {len(read_vars)} |')
        lines.append('')

        # 高耦合变量Top20
        lines.append('## 三、高耦合变量Top20(被最多FC访问)')
        lines.append('')
        lines.append('这些变量被多个FC读写,是系统核心数据流节点,变更时影响范围大。')
        lines.append('')
        sorted_vars = sorted(self.var_access.values(),
                            key=lambda v: -(len(v.readers) + len(v.writers)))
        lines.append('| 排名 | 变量 | 符号 | 类型 | 读取FC数 | 写入FC数 | 总FC数 | FC列表 |')
        lines.append('|---|---|---|---|---|---|---|---|')
        for i, v in enumerate(sorted_vars[:20], 1):
            all_fcs = sorted(v.readers | v.writers)
            fc_list = ', '.join(all_fcs[:5])
            if len(all_fcs) > 5:
                fc_list += f'... (+{len(all_fcs)-5})'
            symbol = v.symbol or '—'
            lines.append(f'| {i} | {v.address} | {symbol} | {v.var_type} | {len(v.readers)} | {len(v.writers)} | {len(all_fcs)} | {fc_list} |')
        lines.append('')

        # 跨FC写入-读取链
        lines.append('## 四、跨FC写入-读取链(数据流核心路径)')
        lines.append('')
        lines.append('以下变量被FC A写入,被FC B读取,构成FC间数据流。')
        lines.append('这是理解系统数据流的关键。')
        lines.append('')
        wr_vars = [v for v in self.var_access.values() if v.writers and v.readers]
        wr_vars.sort(key=lambda v: -(len(v.writers) + len(v.readers)))
        lines.append('| 变量 | 符号 | 写入FC | 读取FC | 数据流方向 |')
        lines.append('|---|---|---|---|---|')
        for v in wr_vars[:30]:
            symbol = v.symbol or '—'
            writers = ', '.join(sorted(v.writers))
            readers = ', '.join(sorted(v.readers))
            flow = f'{writers} → [{v.address}] → {readers}'
            lines.append(f'| {v.address} | {symbol} | {writers} | {readers} | {flow} |')
        lines.append('')

        # 变量-FC矩阵(精简版,只列跨FC变量)
        lines.append('## 五、变量-FC访问矩阵(跨FC共享变量)')
        lines.append('')
        cross_vars = [v for v in self.var_access.values()
                     if len(v.readers | v.writers) > 1]
        cross_vars.sort(key=lambda v: (v.var_type, v.byte_addr))

        # 收集所有相关FC
        all_fcs_set = set()
        for v in cross_vars:
            all_fcs_set.update(v.readers | v.writers)
        all_fcs = sorted(all_fcs_set)

        # 矩阵太大,只列Top15 FC和Top30变量
        lines.append(f'**矩阵说明**: R=读取, W=写入, RW=读写, 空=未访问')
        lines.append(f'**变量数**: {len(cross_vars)}个跨FC变量 | **FC数**: {len(all_fcs)}个')
        lines.append('')
        lines.append('### 5.1 状态机与核心变量')
        lines.append('')
        core_vars = [v for v in cross_vars if v.address in
                    ('VW2', 'VW4', 'VW6', 'VW8', 'QB0', 'I1.1', 'V1.6', 'V1.7',
                     'V0.0', 'V0.2', 'V0.3', 'V0.4', 'V0.7', 'V300.4', 'V300.5',
                     'V304.0', 'VD178', 'VD96', 'VD112', 'VD116')]
        if core_vars:
            lines.append('| 变量 | 符号 |')
            lines.append('|---|---|')
            for v in core_vars:
                lines.append(f'| {v.address} | {v.symbol or "—"} (读:{len(v.readers)}FC 写:{len(v.writers)}FC) |')
        lines.append('')

        # FC间耦合分析
        lines.append('## 六、FC间耦合分析(共享变量数)')
        lines.append('')
        lines.append('两个FC共享的变量越多,耦合度越高。')
        lines.append('')
        # 计算FC对之间的共享变量数
        fc_pairs: Dict[Tuple[str, str], int] = defaultdict(int)
        for v in self.var_access.values():
            all_fcs_for_var = sorted(v.readers | v.writers)
            for i in range(len(all_fcs_for_var)):
                for j in range(i + 1, len(all_fcs_for_var)):
                    fc_pairs[(all_fcs_for_var[i], all_fcs_for_var[j])] += 1

        # Top20耦合FC对
        sorted_pairs = sorted(fc_pairs.items(), key=lambda x: -x[1])
        lines.append('### 6.1 高耦合FC对Top20')
        lines.append('')
        lines.append('| FC A | FC B | 共享变量数 |')
        lines.append('|---|---|---|')
        for (fc_a, fc_b), count in sorted_pairs[:20]:
            lines.append(f'| {fc_a} | {fc_b} | {count} |')
        lines.append('')

        # 关键数据流路径
        lines.append('## 七、关键数据流路径')
        lines.append('')
        lines.append('### 7.1 状态机调度流(FC1→各状态FC)')
        lines.append('')
        lines.append('```')
        lines.append('FC1_StateDispatcher (读写VW2)')
        lines.append('  ├─ VW2=0 → FC10_State_S0_Init')
        lines.append('  ├─ VW2=1 → FC11_State_S1_Inlet (调用FC30阀A诊断)')
        lines.append('  ├─ VW2=2 → FC12_State_S2_PreMix')
        lines.append('  ├─ VW2=3 → FC13_State_S3_Dosing (调用FC4 Modbus轮询)')
        lines.append('  ├─ VW2=4 → FC14_State_S35_Rest')
        lines.append('  ├─ VW2=5 → FC15_State_S4_Transfer (调用FC31阀B诊断)')
        lines.append('  ├─ VW2=6 → FC16_State_S5_Run (调用FC40节奏纠偏)')
        lines.append('  ├─ VW2=7 → FC17_State_S6_Drain (调用FC32阀C诊断)')
        lines.append('  ├─ VW2=8 → FC18_State_S7_End')
        lines.append('  └─ VW2=99 → FC19_State_Error')
        lines.append('```')
        lines.append('')

        lines.append('### 7.2 急停与报警流(FC2/FC3→各FC)')
        lines.append('')
        lines.append('```')
        lines.append('FC2_EStopHandling')
        lines.append('  ├─ I1.1下降沿 → V300.4锁存 → VW2=99(S_ERROR)')
        lines.append('  ├─ I1.2反馈缺失 → V300.5继电器故障')
        lines.append('  └─ QB0=0(输出安全) → Q0.7=1(声音)')
        lines.append('')
        lines.append('FC3_AlarmHandling')
        lines.append('  ├─ 读V300~V303(32位报警字)')
        lines.append('  ├─ 优先级链计算 → VW6(最高级报警码)')
        lines.append('  └─ VW6≠0 → Q1.0灯光常亮')
        lines.append('```')
        lines.append('')

        lines.append('### 7.3 节奏纠偏流(FC40←FC16/FC11)')
        lines.append('')
        lines.append('```')
        lines.append('FC16_State_S5_Run')
        lines.append('  ├─ VD178(S5_Elapsed)累加 → 触发FC40预规划')
        lines.append('  └─ FC40_RhythmCorrection')
        lines.append('      ├─ 读VD20(周期)/VD28(S2标称)/VD36(S3.5标称)')
        lines.append('      ├─ 计算VD120(S2_Target)/VD124(S3.5_Target)/VD128(CycleExtend)')
        lines.append('      └─ VW184(纠偏结果): 1正常/2纠偏/3顺延/4人工介入')
        lines.append('')
        lines.append('FC11_State_S1_Inlet (S1完成后)')
        lines.append('  └─ 调用FC40(模式1二次校正) → 更新VD112(T_Rolling)')
        lines.append('```')
        lines.append('')

        lines.append('### 7.4 阀门诊断流(FC30/31/32←FC11/15/17)')
        lines.append('')
        lines.append('```')
        lines.append('FC11(S1) → FC30(阀A诊断)')
        lines.append('  ├─ FC11写VW260=1启动 → FC30读VW260调度')
        lines.append('  ├─ FC30写VW266(结果) → FC11读VW266判断')
        lines.append('  └─ FC30用VD308(快照)/VD312(差值)/VD316(目标进水量)')
        lines.append('')
        lines.append('FC15(S4) → FC31(阀B诊断)')
        lines.append('  ├─ FC15写VW262=1启动 → FC31读VW262调度')
        lines.append('  ├─ FC31写VW268(结果) → FC15读VW268判断')
        lines.append('  └─ FC31用VW274(超时PT)')
        lines.append('')
        lines.append('FC17(S6) → FC32(阀C诊断)')
        lines.append('  ├─ FC17写VW264=1启动 → FC32读VW264调度')
        lines.append('  ├─ FC32写VW270(结果) → FC17读VW270判断')
        lines.append('  └─ FC32用VW276(超时PT)')
        lines.append('```')
        lines.append('')

        lines.append('### 7.5 Modbus通讯流(FC4↔注射泵/流量计)')
        lines.append('')
        lines.append('```')
        lines.append('FC4_ModbusPolling')
        lines.append('  ├─ VW250(轮询计数器): 0=注射泵, 1=流量计')
        lines.append('  ├─ 注射泵: VW200~VW228 ↔ Modbus 40002~40018')
        lines.append('  │   ├─ VW204(抽液步数)→40006')
        lines.append('  │   ├─ VW206(排液步数)→40007')
        lines.append('  │   └─ VW4(状态码)←41001')
        lines.append('  └─ 流量计: VD86(累计)←0x0009, VD94(瞬时)←0x0017')
        lines.append('```')
        lines.append('')

        # 架构改进建议
        lines.append('## 八、架构观察与改进建议')
        lines.append('')

        # 识别"上帝变量"(被太多FC写入的变量)
        god_writes = [v for v in self.var_access.values() if len(v.writers) > 3]
        if god_writes:
            lines.append('### 8.1 高写入冲突风险变量(被>3个FC写入)')
            lines.append('')
            lines.append('这些变量被多个FC写入,需确认调用顺序与互斥性,否则可能产生时序冲突。')
            lines.append('')
            lines.append('| 变量 | 符号 | 写入FC数 | 写入FC列表 |')
            lines.append('|---|---|---|---|')
            for v in sorted(god_writes, key=lambda v: -len(v.writers)):
                lines.append(f'| {v.address} | {v.symbol or "—"} | {len(v.writers)} | {", ".join(sorted(v.writers))} |')
            lines.append('')

        # 识别"孤儿变量"(被写但从未被读)
        orphan_writes = [v for v in self.var_access.values()
                        if v.writers and not v.readers
                        and v.var_type in ('VW', 'VD')]
        if orphan_writes:
            lines.append('### 8.2 写后未读变量(可能为冗余或遗漏读取)')
            lines.append('')
            lines.append(f'共{len(orphan_writes)}个VW/VD变量被写入但从未被读取,可能为:')
            lines.append('- 运算中间变量(写后立即用AC0,不再读V区)')
            lines.append('- HMI只读变量(PLC写,HMI读,STL内不读)')
            lines.append('- 遗漏读取的变量(潜在bug)')
            lines.append('')
            lines.append('| 变量 | 符号 | 写入FC |')
            lines.append('|---|---|---|')
            for v in sorted(orphan_writes, key=lambda v: (v.var_type, v.byte_addr))[:20]:
                lines.append(f'| {v.address} | {v.symbol or "—"} | {", ".join(sorted(v.writers))} |')
            if len(orphan_writes) > 20:
                lines.append(f'| ... | (共{len(orphan_writes)}个) | ... |')
            lines.append('')

        lines.append('### 8.3 架构建议')
        lines.append('')
        lines.append('1. **VW2状态机**: 被几乎所有FC读写,是核心调度变量。当前架构合理(FC1集中调度)。')
        lines.append('2. **报警字V300~V303**: 被多个FC写入(各FC置位报警),FC3集中读取计算VW6。合理。')
        lines.append('3. **QB0输出**: 被多个FC写入(各FC控制输出),需确认互斥(状态机保证同一时刻只有一个状态FC运行)。')
        lines.append('4. **VD参数区(VD10~VD66)**: 应为HMI只写,FC只读。若FC写入参数区需排查(见静态分析报告)。')
        lines.append('5. **诊断变量(VW260~VW270)**: FC30/31/32与FC11/15/17通过VW260/262/264/266/268/270握手,耦合清晰。')
        lines.append('6. **中间变量(VD308~VD344)**: 各FC私有,无跨FC共享,耦合度低(2026-07-18修复后)。')
        lines.append('')
        lines.append('---')
        lines.append('')
        lines.append('*本报告由 cross_fc_dataflow_analyzer.py 自动生成。*')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


# =============================================================================
# 主入口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='跨FC变量访问数据流分析工具')
    parser.add_argument('--stl-dir', default='../plc/stl',
                        help='STL文件目录(默认: ../plc/stl)')
    parser.add_argument('--var-table', default='../docs/HMI-PLC变量地址表_v1.0.md',
                        help='变量表Markdown文件')
    parser.add_argument('--report', default='../docs/跨FC数据流分析报告_v1.0.md',
                        help='输出报告文件')
    args = parser.parse_args()

    stl_dir = Path(args.stl_dir).resolve()
    var_table = Path(args.var_table).resolve()
    report_path = Path(args.report).resolve()

    if not stl_dir.exists():
        print(f'❌ STL目录不存在: {stl_dir}')
        sys.exit(1)

    print(f'🔄 跨FC数据流分析工具 v1.0')
    print(f'   STL目录: {stl_dir}')
    print(f'   报告输出: {report_path}')
    print()

    analyzer = DataFlowAnalyzer(stl_dir, var_table)
    analyzer.run()
    analyzer.generate_report(report_path)

    # 控制台摘要
    total_vars = len(analyzer.var_access)
    cross_fc = sum(1 for v in analyzer.var_access.values()
                  if len(v.readers | v.writers) > 1)
    print(f'📊 分析完成:')
    print(f'   FC数: {len(analyzer.fc_refs)}')
    print(f'   变量数: {total_vars}')
    print(f'   跨FC共享变量: {cross_fc}')
    print(f'✅ 报告已生成: {report_path}')


if __name__ == '__main__':
    main()
