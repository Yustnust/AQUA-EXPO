#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC代码静态分析工具
===================
扫描S7-200 SMART STL文件,检测:
1. V区编址冲突(不同符号指向重叠地址范围)
2. 地址重叠(VB/VW/VD覆盖字节范围交叉)
3. 未使用变量(变量表定义但STL未引用)
4. 未定义变量(STL引用但变量表未定义)
5. 字/双字对齐检查(VW/VD应偶数地址起始)
6. 跨FC变量写入冲突(同一V区被多个FC写入)

用法:
    python3 stl_static_analyzer.py [--stl-dir ../plc/stl] [--var-table ../docs/HMI-PLC变量地址表_v1.0.md] [--report report.md]

输出:
    - 控制台摘要
    - Markdown分析报告
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional


# =============================================================================
# 数据结构
# =============================================================================

@dataclass
class VarRef:
    """变量引用记录"""
    fc_name: str            # FC名称
    line_no: int            # 行号
    raw: str                # 原始文本(如 VD90, VW2, V300.4)
    var_type: str           # VB/VW/VD/Vbit/I/Q/M/T/C/SM
    address: int            # 起始字节地址(Vbit为字节地址)
    bit_offset: int = 0     # 位偏移(仅Vbit)
    size: int = 1           # 占用字节数(VB=1/VW=2/VD=4/Vbit=1位)
    access: str = "R"       # R读/W写/RW读写(粗略判断)


@dataclass
class VarDef:
    """变量定义(从变量表或STL注释解析)"""
    symbol: str             # 符号名
    address: str            # 原始地址(如 VD90, VW2, V300.4)
    var_type: str           # VB/VW/VD/Vbit
    byte_addr: int          # 起始字节
    size: int               # 字节数
    bit_offset: int = 0     # 位偏移
    desc: str = ""          # 描述
    source: str = ""        # 来源(变量表/STL注释)


@dataclass
class Issue:
    """问题记录"""
    severity: str           # 严重/警告/提示
    category: str           # 类别
    fc_name: str            # 相关FC
    line_no: int            # 行号(0表示全局)
    message: str            # 问题描述
    detail: str = ""        # 详细信息


# =============================================================================
# STL解析器
# =============================================================================

class STLParser:
    """STL文件解析器"""

    # V区变量正则: VBxx, VWxx, VDxx, Vxx.y
    # VB2, VW2, VD90, V300.4, V1.6
    VAR_PATTERN = re.compile(
        r'\b(V)(B|W|D)?(\d+)(?:\.(\d+))?',
        re.IGNORECASE
    )

    # I/Q/M/T/C/SM点
    IO_PATTERN = re.compile(
        r'\b([IQMT]|SM)(\d+)(?:\.(\d+))?',
        re.IGNORECASE
    )

    # 注释行
    COMMENT_PATTERN = re.compile(r'^\s*//')

    # NETWORK分隔
    NETWORK_PATTERN = re.compile(r'^\s*NETWORK\s+(\d+)', re.IGNORECASE)

    def __init__(self):
        self.refs: List[VarRef] = []

    def parse_file(self, file_path: Path) -> Tuple[str, List[VarRef]]:
        """解析单个STL文件,返回(FC名, 引用列表)"""
        fc_name = file_path.stem  # 如 FC0_SysInit
        refs: List[VarRef] = []
        in_comment_block = False

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_no, line in enumerate(lines, 1):
            # 跳过纯注释行(但仍解析其中的变量,因为注释可能含符号说明)
            # 去除行内注释
            code_part = line.split('//')[0] if '//' in line else line
            comment_part = line.split('//', 1)[1] if '//' in line else ''

            # 解析V区变量(代码部分)
            for match in self.VAR_PATTERN.finditer(code_part):
                prefix = match.group(1).upper()
                size_code = match.group(2)
                addr = int(match.group(3))
                bit = match.group(4)

                if size_code is None and bit is not None:
                    # Vx.y 位访问
                    var_type = 'Vbit'
                    size = 1  # 位占用1个位,字节范围仍为该字节
                    bit_offset = int(bit)
                    access = self._guess_access(code_part, match.group(0))
                    refs.append(VarRef(fc_name, line_no, match.group(0),
                                      var_type, addr, bit_offset, 1, access))
                elif size_code is None:
                    # 单独Vxx(可能是VW/VB的简写,或符号表替代,跳过)
                    continue
                else:
                    size_code = size_code.upper()
                    if size_code == 'B':
                        var_type, size = 'VB', 1
                    elif size_code == 'W':
                        var_type, size = 'VW', 2
                    elif size_code == 'D':
                        var_type, size = 'VD', 4
                    else:
                        continue
                    bit_offset = 0
                    access = self._guess_access(code_part, match.group(0))
                    refs.append(VarRef(fc_name, line_no, match.group(0),
                                      var_type, addr, bit_offset, size, access))

            # 解析注释中的符号说明(用于提取变量定义)
            # 暂不在此处理,符号定义单独提取

        return fc_name, refs

    def _guess_access(self, code_line: str, var_text: str) -> str:
        """粗略判断读写: 写入指令的目标操作数为W"""
        # STL写入类指令(目标操作数为最后一个参数,在逗号后)
        # MOVB/MOVW/MOVD/MOVR/S/R/FILL/+R/*R/-R//R/+D/-D/ITD/DTR/BTI
        write_mnemonics = [
            'MOVB', 'MOVW', 'MOVD', 'MOVR', 'MOVR',
            'S', 'R', 'FILL',
            '+R', '*R', '-R', '/R',
            '+D', '-D', '*D', '/D',
            '+I', '-I', '*I', '/I',
            'ITD', 'DTR', 'BTI', 'DTI', 'ITR', 'ROUND', 'TRUNC',
            'WAND_W', 'WOR_W', 'WXOR_W', 'WAND_B', 'WOR_B', 'WXOR_B',
            'SWAP', 'BCDI', 'IBCD',
            'SET_RTC', 'READ_RTC',
        ]
        # 检查变量是否作为目标操作数(出现在逗号后,且前面是写入指令)
        # 简化: 如果变量在逗号之后,且行首是写入指令,则为W
        for mnemonic in write_mnemonics:
            # 转义特殊字符
            esc_mnem = re.escape(mnemonic)
            # 匹配: 指令 源操作数, 变量 (变量作为目标)
            pat = esc_mnem + r'\s+\S+,\s*' + re.escape(var_text) + r'\b'
            if re.search(pat, code_line, re.IGNORECASE):
                return 'W'
            # S/R 指令: S V300.4, 1 (变量是第一个操作数,位+长度)
            if mnemonic in ('S', 'R', 'SI', 'RI'):
                pat = r'\b' + esc_mnem + r'\s+' + re.escape(var_text) + r'\b'
                if re.search(pat, code_line, re.IGNORECASE):
                    return 'W'
            # FILL: FILL 0, VW300, 4 (变量是第二个操作数)
            if mnemonic == 'FILL':
                pat = r'\b' + esc_mnem + r'\s+\S+,\s*' + re.escape(var_text) + r'\b'
                if re.search(pat, code_line, re.IGNORECASE):
                    return 'W'
        return 'R'


# =============================================================================
# 变量表解析器
# =============================================================================

class VarTableParser:
    """从HMI-PLC变量地址表Markdown解析变量定义"""

    # 匹配表格行: | 符号 | 地址 | ... |
    # 也匹配注释中的符号说明: VW2 : StateMachine
    SYMBOL_PATTERN = re.compile(
        r'(VB|VW|VD|V)\s*(\d+)(?:\.(\d+))?\s*[:：]\s*(\S+)',
        re.IGNORECASE
    )

    def __init__(self):
        self.defs: Dict[str, VarDef] = {}  # key=原始地址文本

    def parse_file(self, file_path: Path) -> Dict[str, VarDef]:
        """解析变量表Markdown"""
        if not file_path.exists():
            return {}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析注释中的符号说明(常见于STL文件头注释和变量表)
        for match in self.SYMBOL_PATTERN.finditer(content):
            size_code = match.group(1).upper()
            addr = int(match.group(2))
            bit = match.group(3)
            symbol = match.group(4)

            if bit is not None:
                var_type = 'Vbit'
                size = 1
                bit_offset = int(bit)
                key = f"V{addr}.{bit_offset}"
            elif size_code == 'VB':
                var_type, size = 'VB', 1
                key = f"VB{addr}"
            elif size_code == 'VW':
                var_type, size = 'VW', 2
                key = f"VW{addr}"
            elif size_code == 'VD':
                var_type, size = 'VD', 4
                key = f"VD{addr}"
            else:
                continue

            if key not in self.defs:
                self.defs[key] = VarDef(
                    symbol=symbol, address=key, var_type=var_type,
                    byte_addr=addr, size=size, bit_offset=bit_offset,
                    source=str(file_path.name)
                )

        return self.defs


# =============================================================================
# 分析器
# =============================================================================

class STLAnalyzer:
    """静态分析主类"""

    def __init__(self, stl_dir: Path, var_table: Path):
        self.stl_dir = stl_dir
        self.var_table = var_table
        self.parser = STLParser()
        self.var_parser = VarTableParser()
        self.all_refs: List[VarRef] = []
        self.fc_refs: Dict[str, List[VarRef]] = {}
        self.var_defs: Dict[str, VarDef] = {}
        self.issues: List[Issue] = []

    def run(self) -> List[Issue]:
        """执行全部分析"""
        self._parse_all()
        self._check_address_overlap()
        self._check_alignment()
        self._check_cross_fc_write_conflict()
        self._check_unused_vars()
        self._check_undefined_vars()
        self._check_write_to_param_region()
        return self.issues

    def _parse_all(self):
        """解析所有STL文件和变量表"""
        # 解析变量表
        self.var_defs = self.var_parser.parse_file(self.var_table)

        # 解析STL文件(同时从STL注释提取符号定义)
        stl_files = sorted(self.stl_dir.glob('*.stl'))
        for stl_file in stl_files:
            fc_name, refs = self.parser.parse_file(stl_file)
            self.fc_refs[fc_name] = refs
            self.all_refs.extend(refs)
            # 从STL文件头注释提取符号定义
            self._extract_symbols_from_stl(stl_file)

    def _extract_symbols_from_stl(self, stl_file: Path):
        """从STL文件头注释提取符号说明,补充变量定义"""
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

    # ---- 检查1: V区编址冲突/地址重叠 ----
    def _check_address_overlap(self):
        """检测V区变量地址范围重叠(真正的编址冲突)

        判定规则:
        - VD vs VD: 起始地址不同但范围交叉 → 冲突(严重)
        - VW vs VW: 起始地址不同但范围交叉 → 冲突(严重)
        - VD vs VW: VW跨越VD边界 或 VW起始与VD起始不同且VW不全在VD内 → 冲突(警告)
        - VB vs VW/VD: 跳过(字节级访问同变量正常)
        """
        # 收集所有VW/VD引用范围(去重)
        vd_refs = set()  # (地址, FC, 行号)
        vw_refs = set()
        for ref in self.all_refs:
            if ref.var_type == 'VD':
                vd_refs.add((ref.address, ref.fc_name, ref.line_no, ref.raw))
            elif ref.var_type == 'VW':
                vw_refs.add((ref.address, ref.fc_name, ref.line_no, ref.raw))

        # VD vs VD 重叠检测
        vd_list = sorted(set((a, r) for a, _, _, r in vd_refs))
        reported_pairs = set()
        for i in range(len(vd_list)):
            for j in range(i + 1, len(vd_list)):
                a1, r1 = vd_list[i]
                a2, r2 = vd_list[j]
                if a1 == a2:
                    continue  # 相同起始,跳过(同变量)
                # 范围: [a1, a1+4) vs [a2, a2+4)
                if a1 < a2 + 4 and a2 < a1 + 4:
                    pair_key = (min(a1, a2), max(a1, a2))
                    if pair_key in reported_pairs:
                        continue
                    reported_pairs.add(pair_key)
                    # 收集引用该地址的FC
                    fcs1 = [f"{fc}:L{ln}({raw})" for a, fc, ln, raw in vd_refs if a == a1]
                    fcs2 = [f"{fc}:L{ln}({raw})" for a, fc, ln, raw in vd_refs if a == a2]
                    self.issues.append(Issue(
                        severity='严重',
                        category='VD编址冲突',
                        fc_name='全局',
                        line_no=0,
                        message=f'VD{a1}(VB{a1}~VB{a1+3}) 与 VD{a2}(VB{a2}~VB{a2+3}) 地址重叠',
                        detail=f'VD{a1}引用: {fcs1}\nVD{a2}引用: {fcs2}\n重叠字节: VB{max(a1,a2)}~VB{min(a1+3,a2+3)}'
                    ))

        # VW vs VW 重叠检测
        vw_list = sorted(set((a, r) for a, _, _, r in vw_refs))
        for i in range(len(vw_list)):
            for j in range(i + 1, len(vw_list)):
                a1, r1 = vw_list[i]
                a2, r2 = vw_list[j]
                if a1 == a2:
                    continue
                if a1 < a2 + 2 and a2 < a1 + 2:
                    pair_key = (min(a1, a2), max(a1, a2))
                    if pair_key in reported_pairs:
                        continue
                    reported_pairs.add(pair_key)
                    fcs1 = [f"{fc}:L{ln}({raw})" for a, fc, ln, raw in vw_refs if a == a1]
                    fcs2 = [f"{fc}:L{ln}({raw})" for a, fc, ln, raw in vw_refs if a == a2]
                    self.issues.append(Issue(
                        severity='严重',
                        category='VW编址冲突',
                        fc_name='全局',
                        line_no=0,
                        message=f'VW{a1}(VB{a1}~VB{a1+1}) 与 VW{a2}(VB{a2}~VB{a2+1}) 地址重叠',
                        detail=f'VW{a1}引用: {fcs1}\nVW{a2}引用: {fcs2}'
                    ))

        # VD vs VW 重叠检测(只报跨越边界的)
        for vd_addr, _, _, _ in vd_refs:
            for vw_addr, _, _, _ in vw_refs:
                if vw_addr == vd_addr:
                    continue  # 同起始,可能是VD的低字,跳过
                # VD范围: [vd_addr, vd_addr+4), VW范围: [vw_addr, vw_addr+2)
                # 如果VW完全在VD内且起始不同 → VD的高字访问,提示
                # 如果VW跨越VD边界 → 冲突
                if vw_addr < vd_addr + 4 and vd_addr < vw_addr + 2:
                    pair_key = (min(vd_addr, vw_addr), max(vd_addr, vw_addr), 'vd-vw')
                    if pair_key in reported_pairs:
                        continue
                    reported_pairs.add(pair_key)
                    # 判断是跨越还是包含
                    vw_end = vw_addr + 2
                    vd_end = vd_addr + 4
                    if vw_addr >= vd_addr and vw_end <= vd_end:
                        # VW在VD内,可能是高字访问,提示
                        fcs_vd = [f"{fc}:L{ln}" for a, fc, ln, _ in vd_refs if a == vd_addr]
                        fcs_vw = [f"{fc}:L{ln}" for a, fc, ln, _ in vw_refs if a == vw_addr]
                        self.issues.append(Issue(
                            severity='提示',
                            category='VD/VW子字访问',
                            fc_name='全局',
                            line_no=0,
                            message=f'VW{vw_addr}位于VD{vd_addr}内部(VB{vd_addr}~VB{vd_addr+3})',
                            detail=f'可能是VD的高字访问(正常),或编址错误。VD{vd_addr}引用: {fcs_vd}, VW{vw_addr}引用: {fcs_vw}'
                        ))
                    else:
                        # VW跨越VD边界,冲突
                        fcs_vd = [f"{fc}:L{ln}" for a, fc, ln, _ in vd_refs if a == vd_addr]
                        fcs_vw = [f"{fc}:L{ln}" for a, fc, ln, _ in vw_refs if a == vw_addr]
                        self.issues.append(Issue(
                            severity='警告',
                            category='VD/VW编址冲突',
                            fc_name='全局',
                            line_no=0,
                            message=f'VW{vw_addr}(VB{vw_addr}~VB{vw_addr+1}) 跨越 VD{vd_addr}(VB{vd_addr}~VB{vd_addr+3}) 边界',
                            detail=f'VD{vd_addr}引用: {fcs_vd}\nVW{vw_addr}引用: {fcs_vw}'
                        ))

    # ---- 检查2: VW/VD对齐检查 ----
    def _check_alignment(self):
        """VW应偶数地址,VD应4倍数地址"""
        for ref in self.all_refs:
            if ref.var_type == 'VW' and ref.address % 2 != 0:
                self.issues.append(Issue(
                    severity='警告',
                    category='对齐错误',
                    fc_name=ref.fc_name,
                    line_no=ref.line_no,
                    message=f'VW地址非偶数对齐: {ref.raw}(地址{ref.address})',
                    detail='VW应从偶数字节地址起始,否则部分指令可能异常'
                ))
            elif ref.var_type == 'VD' and ref.address % 4 != 0:
                # VD不强制4对齐,但建议(某些CPU有性能差异),仅提示
                self.issues.append(Issue(
                    severity='提示',
                    category='对齐建议',
                    fc_name=ref.fc_name,
                    line_no=ref.line_no,
                    message=f'VD地址非4字节对齐: {ref.raw}(地址{ref.address})',
                    detail='VD建议从4倍数字节地址起始(非强制)'
                ))

    # ---- 检查3: 跨FC写入冲突 ----
    def _check_cross_fc_write_conflict(self):
        """检测同一V区变量被多个FC写入(潜在冲突)"""
        write_map: Dict[str, Set[str]] = defaultdict(set)  # 地址→FC集合
        for ref in self.all_refs:
            if ref.access == 'W':
                write_map[ref.raw].add(ref.fc_name)

        for addr, fcs in write_map.items():
            if len(fcs) > 1:
                self.issues.append(Issue(
                    severity='警告',
                    category='跨FC写入冲突',
                    fc_name='全局',
                    line_no=0,
                    message=f'变量 {addr} 被 {len(fcs)} 个FC写入: {sorted(fcs)}',
                    detail='同一变量被多个FC写入可能导致时序冲突,需确认调用顺序与互斥性'
                ))

    # ---- 检查4: 未使用变量 ----
    def _check_unused_vars(self):
        """变量表定义但STL未引用的变量"""
        referenced_addrs = set()
        for ref in self.all_refs:
            if ref.var_type in ('VB', 'VW', 'VD'):
                referenced_addrs.add((ref.var_type, ref.address))
            elif ref.var_type == 'Vbit':
                referenced_addrs.add(('Vbit', ref.address, ref.bit_offset))

        for key, defn in self.var_defs.items():
            if defn.var_type in ('VB', 'VW', 'VD'):
                if (defn.var_type, defn.byte_addr) not in referenced_addrs:
                    # 检查是否被位访问覆盖(如VW2被V2.0访问)
                    covered = False
                    for ref in self.all_refs:
                        if ref.var_type == 'Vbit' and ref.address == defn.byte_addr:
                            covered = True
                            break
                    if not covered:
                        self.issues.append(Issue(
                            severity='提示',
                            category='未使用变量',
                            fc_name='全局',
                            line_no=0,
                            message=f'变量 {key}({defn.symbol}) 定义但未在STL中引用',
                            detail=f'来源: {defn.source}'
                        ))

    # ---- 检查5: 未定义变量 ----
    def _check_undefined_vars(self):
        """STL引用但变量表未定义的变量"""
        defined_addrs = set()
        for key, defn in self.var_defs.items():
            if defn.var_type in ('VB', 'VW', 'VD'):
                defined_addrs.add((defn.var_type, defn.byte_addr))

        seen_undefined = set()
        for ref in self.all_refs:
            if ref.var_type in ('VB', 'VW', 'VD'):
                if (ref.var_type, ref.address) not in defined_addrs:
                    issue_key = (ref.var_type, ref.address)
                    if issue_key not in seen_undefined:
                        seen_undefined.add(issue_key)
                        self.issues.append(Issue(
                            severity='提示',
                            category='未定义变量',
                            fc_name=ref.fc_name,
                            line_no=ref.line_no,
                            message=f'变量 {ref.raw} 在STL中引用但变量表/注释未定义',
                            detail=f'FC: {ref.fc_name}, 行: {ref.line_no}'
                        ))

    # ---- 检查6: 写入HMI参数区(VD10~VD140) ----
    def _check_write_to_param_region(self):
        """HMI参数区(VD10~VD140)不应被FC直接写入(应由HMI设定)"""
        PARAM_REGION = set()
        for addr in range(10, 141, 4):  # VD10, VD14, ... VD140
            PARAM_REGION.add(addr)

        for ref in self.all_refs:
            if ref.var_type == 'VD' and ref.address in PARAM_REGION and ref.access == 'W':
                # 排除已知合法写入(如FC0冷启动清零?不,FC0不清参数区)
                self.issues.append(Issue(
                    severity='警告',
                    category='参数区写入',
                    fc_name=ref.fc_name,
                    line_no=ref.line_no,
                    message=f'FC直接写入HMI参数区 {ref.raw}(VD{ref.address})',
                    detail='VD10~VD140为HMI设定参数区,FC直接写入可能覆盖操作员设定'
                ))


# =============================================================================
# 报告生成
# =============================================================================

class ReportGenerator:
    """生成Markdown分析报告"""

    def __init__(self, analyzer: STLAnalyzer, issues: List[Issue]):
        self.analyzer = analyzer
        self.issues = issues

    def generate_markdown(self, output_path: Path):
        """生成Markdown报告"""
        lines = []
        lines.append('# PLC代码静态分析报告')
        lines.append('')
        lines.append('| 项目 | 内容 |')
        lines.append('|---|---|')
        lines.append(f'| 分析对象 | S7-200 SMART STL代码({len(self.analyzer.fc_refs)}个FC) |')
        lines.append(f'| 分析工具 | stl_static_analyzer.py v1.0 |')
        lines.append(f'| 变量表来源 | HMI-PLC变量地址表v1.0 + STL注释 |')
        lines.append(f'| 分析日期 | 2026-07-18 |')
        lines.append('')

        # 摘要
        lines.append('## 一、分析摘要')
        lines.append('')
        severe = sum(1 for i in self.issues if i.severity == '严重')
        warning = sum(1 for i in self.issues if i.severity == '警告')
        info = sum(1 for i in self.issues if i.severity == '提示')
        lines.append(f'- **问题总数**: {len(self.issues)} 个')
        lines.append(f'- **严重**: {severe} 个')
        lines.append(f'- **警告**: {warning} 个')
        lines.append(f'- **提示**: {info} 个')
        lines.append('')

        # STL文件统计
        lines.append('## 二、STL文件统计')
        lines.append('')
        lines.append('| FC名称 | 引用数 | 写入数 |')
        lines.append('|---|---|---|')
        for fc_name, refs in sorted(self.analyzer.fc_refs.items()):
            write_count = sum(1 for r in refs if r.access == 'W')
            lines.append(f'| {fc_name} | {len(refs)} | {write_count} |')
        total_refs = len(self.analyzer.all_refs)
        total_writes = sum(1 for r in self.analyzer.all_refs if r.access == 'W')
        lines.append(f'| **合计** | **{total_refs}** | **{total_writes}** |')
        lines.append('')

        # 变量定义统计
        lines.append('## 三、变量定义统计')
        lines.append('')
        vb_count = sum(1 for d in self.analyzer.var_defs.values() if d.var_type == 'VB')
        vw_count = sum(1 for d in self.analyzer.var_defs.values() if d.var_type == 'VW')
        vd_count = sum(1 for d in self.analyzer.var_defs.values() if d.var_type == 'VD')
        vbit_count = sum(1 for d in self.analyzer.var_defs.values() if d.var_type == 'Vbit')
        lines.append(f'- VB(字节): {vb_count} 个')
        lines.append(f'- VW(字): {vw_count} 个')
        lines.append(f'- VD(双字): {vd_count} 个')
        lines.append(f'- Vbit(位): {vbit_count} 个')
        lines.append(f'- **合计**: {len(self.analyzer.var_defs)} 个变量定义')
        lines.append('')

        # 问题清单
        lines.append('## 四、问题清单')
        lines.append('')

        if not self.issues:
            lines.append('✅ 未发现问题')
            lines.append('')
        else:
            # 按严重程度分组
            for severity in ['严重', '警告', '提示']:
                sev_issues = [i for i in self.issues if i.severity == severity]
                if not sev_issues:
                    continue
                lines.append(f'### {severity}({len(sev_issues)}个)')
                lines.append('')
                # 按类别分组
                categories = OrderedDict()
                for issue in sev_issues:
                    if issue.category not in categories:
                        categories[issue.category] = []
                    categories[issue.category].append(issue)

                for cat, cat_issues in categories.items():
                    lines.append(f'#### {cat}({len(cat_issues)}个)')
                    lines.append('')
                    for i, issue in enumerate(cat_issues, 1):
                        lines.append(f'{i}. **[{issue.severity}]** {issue.message}')
                        if issue.detail:
                            for line in issue.detail.split('\n'):
                                lines.append(f'   - {line}')
                        if issue.fc_name != '全局':
                            lines.append(f'   - 位置: {issue.fc_name} 第{issue.line_no}行')
                        lines.append('')

        # 跨FC变量访问矩阵
        lines.append('## 五、跨FC变量访问矩阵(写入)')
        lines.append('')
        write_matrix: Dict[str, Set[str]] = defaultdict(set)
        for ref in self.analyzer.all_refs:
            if ref.access == 'W':
                write_matrix[ref.raw].add(ref.fc_name)

        multi_fc_writes = {addr: fcs for addr, fcs in write_matrix.items() if len(fcs) > 1}
        if multi_fc_writes:
            lines.append('以下变量被多个FC写入(需确认调用顺序与互斥性):')
            lines.append('')
            lines.append('| 变量 | 写入FC数 | FC列表 |')
            lines.append('|---|---|---|')
            for addr in sorted(multi_fc_writes.keys(), key=lambda x: (len(x), x)):
                fcs = multi_fc_writes[addr]
                lines.append(f'| {addr} | {len(fcs)} | {", ".join(sorted(fcs))} |')
        else:
            lines.append('✅ 无多FC写入冲突变量')
        lines.append('')

        # V区使用热力图(按字节范围统计引用次数)
        lines.append('## 六、V区使用热力图(引用次数Top20)')
        lines.append('')
        byte_refs: Dict[int, int] = defaultdict(int)
        for ref in self.analyzer.all_refs:
            if ref.var_type in ('VB', 'VW', 'VD'):
                for offset in range(ref.size):
                    byte_refs[ref.address + offset] += 1
            elif ref.var_type == 'Vbit':
                byte_refs[ref.address] += 1

        top20 = sorted(byte_refs.items(), key=lambda x: -x[1])[:20]
        lines.append('| 字节地址 | 引用次数 |')
        lines.append('|---|---|')
        for addr, count in top20:
            lines.append(f'| VB{addr} | {count} |')
        lines.append('')

        # 结论
        lines.append('## 七、结论与建议')
        lines.append('')
        if severe == 0 and warning == 0:
            lines.append('✅ PLC代码静态分析未发现严重/警告问题,代码质量良好。')
        elif severe == 0:
            lines.append(f'⚠️ 未发现严重问题,但存在 {warning} 个警告,建议在下一轮迭代前修复。')
        else:
            lines.append(f'❌ 发现 {severe} 个严重问题,必须立即修复后方可交付。')

        if info > 0:
            lines.append(f'ℹ️ 另有 {info} 个提示项,可择机处理。')
        lines.append('')
        lines.append('---')
        lines.append('')
        lines.append('*本报告由 stl_static_analyzer.py 自动生成,可重复执行以跟踪问题修复进度。*')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


# =============================================================================
# 主入口
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='S7-200 SMART STL静态分析工具')
    parser.add_argument('--stl-dir', default='../plc/stl',
                        help='STL文件目录(默认: ../plc/stl)')
    parser.add_argument('--var-table', default='../docs/HMI-PLC变量地址表_v1.0.md',
                        help='变量表Markdown文件(默认: ../docs/HMI-PLC变量地址表_v1.0.md)')
    parser.add_argument('--report', default='static_analysis_report.md',
                        help='输出报告文件(默认: static_analysis_report.md)')
    parser.add_argument('--json', default=None,
                        help='输出JSON格式结果(可选)')
    args = parser.parse_args()

    stl_dir = Path(args.stl_dir).resolve()
    var_table = Path(args.var_table).resolve()
    report_path = Path(args.report).resolve()

    if not stl_dir.exists():
        print(f'❌ STL目录不存在: {stl_dir}')
        sys.exit(1)

    print(f'🔍 PLC代码静态分析工具 v1.0')
    print(f'   STL目录: {stl_dir}')
    print(f'   变量表: {var_table}')
    print(f'   报告输出: {report_path}')
    print()

    analyzer = STLAnalyzer(stl_dir, var_table)
    issues = analyzer.run()

    # 控制台摘要
    severe = sum(1 for i in issues if i.severity == '严重')
    warning = sum(1 for i in issues if i.severity == '警告')
    info = sum(1 for i in issues if i.severity == '提示')

    print(f'📊 分析完成:')
    print(f'   STL文件: {len(analyzer.fc_refs)} 个')
    print(f'   变量定义: {len(analyzer.var_defs)} 个')
    print(f'   变量引用: {len(analyzer.all_refs)} 个')
    print(f'   问题总数: {len(issues)} 个')
    print(f'     严重: {severe}')
    print(f'     警告: {warning}')
    print(f'     提示: {info}')
    print()

    if issues:
        print('📋 问题清单:')
        for i, issue in enumerate(issues, 1):
            loc = f'{issue.fc_name}:L{issue.line_no}' if issue.fc_name != '全局' else '全局'
            print(f'   {i}. [{issue.severity}] [{issue.category}] {loc}')
            print(f'      {issue.message}')
        print()

    # 生成报告
    report_gen = ReportGenerator(analyzer, issues)
    report_gen.generate_markdown(report_path)
    print(f'✅ 报告已生成: {report_path}')

    # JSON输出
    if args.json:
        json_data = {
            'summary': {
                'stl_files': len(analyzer.fc_refs),
                'var_defs': len(analyzer.var_defs),
                'var_refs': len(analyzer.all_refs),
                'issues_total': len(issues),
                'issues_severe': severe,
                'issues_warning': warning,
                'issues_info': info,
            },
            'issues': [
                {
                    'severity': i.severity,
                    'category': i.category,
                    'fc_name': i.fc_name,
                    'line_no': i.line_no,
                    'message': i.message,
                    'detail': i.detail,
                } for i in issues
            ],
            'fc_stats': {
                fc: {'refs': len(refs), 'writes': sum(1 for r in refs if r.access == 'W')}
                for fc, refs in analyzer.fc_refs.items()
            }
        }
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f'✅ JSON结果已生成: {args.json}')

    # 退出码: 有严重问题返回1
    sys.exit(1 if severe > 0 else 0)


if __name__ == '__main__':
    main()
