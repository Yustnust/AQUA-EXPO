# 药液配置加注控制系统 — PLC程序版本管理规范 v1.0

**项目**: AQUA-EXPO 药液配置与加注控制系统
**适用范围**: 8台S7-200 SMART CPU ST20(STL代码20个FC文件,8台程序完全相同,仅IP地址不同)
**托管平台**: GitHub(私有仓库)
**版本**: v1.0
**日期**: 2026-07-18
**配套文档**: PLC代码完整性校验报告v1.0、PLC代码静态分析报告v1.0、HMI-PLC变量地址表v1.0、项目交付文档总索引v1.0

---

## 第1章 版本号规则

### 1.1 语义化版本(SemVer)

PLC程序版本采用语义化版本号 `vX.Y.Z`:

| 位 | 含义 | 触发场景 | 示例 |
|---|---|---|---|
| X(主版本) | 重大重构/不兼容变更 | 状态机重设/编址区整体迁移/8台PLC拓扑变化/通讯协议切换(S7↔Modbus TCP) | v1.0.0 → v2.0.0 |
| Y(次版本) | 功能新增(向前兼容) | 新增FC/新增报警位/新增HMI画面变量/新增手动命令位 | v1.0.0 → v1.1.0 |
| Z(修订版本) | 缺陷修复(向前兼容) | 校验报告缺陷修复/静态分析警告修复/编址冲突修复/注释订正 | v1.0.0 → v1.0.1 |

**版本递进规则**:
- Y位递增时,Z位归零(如 v1.1.3 → v1.2.0)
- X位递增时,Y位与Z位均归零(如 v1.5.2 → v2.0.0)
- 预发布版本加后缀 `-rc.N`(如 v1.1.0-rc.1),正式发布不带后缀

### 1.2 8台PLC版本一致性要求

**核心原则**: 8台PLC必须运行相同版本的程序,版本号在8台PLC之间必须严格一致。

| 项 | 要求 |
|---|---|
| 代码差异 | 8台PLC程序完全相同(变量地址表v1.0第1.1节已规定),仅IP地址不同(192.168.2.101~108) |
| 下装同步 | 8台PLC必须在同一发布窗口内同步下装,禁止单台单独升级后再升级其他台 |
| 版本号一致性 | 8台PLC版本号字段(VW0,见1.3节)必须完全相同 |
| HMI侧显示 | HMI总览页应能显示8台PLC各自版本号,任何一台不一致应在HMI侧黄色高亮告警 |
| 例外情形 | 仅单台调试期(如到货首台调试)允许版本临时不一致,需在变更单中标注并设定期限 |

### 1.3 版本号存储位置

**建议方案**: 将版本号编码为32位WORD存入断电保持V区独立区域 `VW0`。

| 字段 | 地址 | 类型 | 内容 | 说明 |
|---|---|---|---|---|
| 主版本(X) | VB0(高字节高4位) | BCD(0~9) | 主版本号,如 v1.x.x → 0x01 | BCD便于HMI显示 |
| 次版本(Y) | VB0(高字节低4位+低字节高4位) | BCD(0~99) | 次版本号,如 v1.2.x → 0x02 | 支持两位次版本 |
| 修订版本(Z) | VB1(低4位) | BCD(0~9) | 修订版本号,如 v1.0.5 → 0x05 | 单位修订版本 |
| (保留) | VB1(高4位) | 0 | — | 预留 |

**推荐编址方案(实际写入FC0 SysInit,首次扫描赋值)**:

```
// FC0_SysInit NETWORK 0 — 版本号登记(首次扫描)
LD     SM0.1
MOVW   16#0102, VW0    // 版本号 v1.0.2 (示例: 主=01, 次=00, 修订=02)
```

**为何选择 VW0 而非独立断电保持区**:
- VW0 位于系统命令位/状态位区(VB0~VB9),该区已全部配置断电保持(变量表附录A)
- VW0 在 v1.0 变量表中当前未占用(命令位用 V0.0~V0.7 字节位,状态位用 V1.0~V1.7),作为字访问 VW0 不与位访问冲突
- 位于 VB0~VB9 区段内,断电保持已统一配置,无需额外修改系统块
- HMI读取 VW0 即可显示版本号,无需扩展地址区

**注意**:
- VW0 在位编址视角是 V0.0~V1.7,若后续 V0 区或 V1 区扩展位定义,需重新评估 VW0 是否冲突
- 版本号登记必须在 FC0 NETWORK 0(首次扫描 SM0.1),且仅执行一次,严禁在主循环中重复写入
- 版本号字段不可被任何其他FC写入,静态分析器应将 VW0 列入"FC0独占写入"白名单

### 1.4 HMI可读版本号显示

| 显示位置 | 内容 | 实现方式 |
|---|---|---|
| HMI画面1总览页 8单元卡片 | 每张卡片底部显示版本号"v1.0.2" | HMI读取对应PLC连接的 VW0,按BCD解析后字符串显示 |
| HMI画面8系统设置页 | 8台PLC版本号集中列表+一致性状态 | 列表对比8台 VW0,任何不一致时红色高亮 |
| HMI报警日志 | 升级事件记录"PLC#1~8 升级至 v1.0.2 (变更单 AQEX-CHG-XXX)" | HMI侧记录,不依赖PLC |
| 程序内部署文件 | `.mwp`/`.sdfp` 文件名包含版本号,如 `AQUA-EXPO_PLC_v1.0.2.mwp` | Git LFS存储(见第8章) |

**HMI版本号解析脚本示例(MCGS)**:
```
' VW0 字读取,BCD解析
Dim verWord As Integer
verWord = ReadVW(0, "PLC_01")
Dim majorVer, minorVer, patchVer As Integer
majorVer = (verWord And &HF000) / 4096
minorVer = (verWord And &H0FF0) / 16
patchVer = (verWord And &H000F)
版本显示字符串 = "v" + Str(majorVer) + "." + Str(minorVer) + "." + Str(patchVer)
```

---

## 第2章 分支策略

### 2.1 分支模型

采用简化版 GitFlow 模型,适配8台PLC"代码完全相同+同步下装"的特点:

| 分支 | 用途 | 生命周期 | 合并规则 |
|---|---|---|---|
| `main` | 稳定发布分支,8台PLC实际下装的版本来源 | 永久 | 仅接收 release-* 合并,禁止直接提交 |
| `develop` | 集成分支,日常开发成果汇总 | 永久 | 接收 feature-*/fix-* 合并,定期向 release-* 分出 |
| `feature-<scope>-<desc>` | 新功能开发(对应Story规格书) | 临时 | 从 develop 拉,完成后PR合回 develop |
| `fix-<scope>-<desc>` | 缺陷修复(对应校验报告/静态分析问题) | 临时 | 从 develop 拉,完成后PR合回 develop |
| `hotfix-<scope>-<desc>` | 现场紧急缺陷修复(对应紧急变更单) | 临时 | 从 main 拉,完成后PR同时合回 main 和 develop |
| `release-x.y` | 发布准备(版本号填充/CHANGELOG/最终回归) | 临时 | 从 develop 拉,完成后合回 main 并打 tag `vx.y.0` |

### 2.2 分支命名规范

| 命名 | 规则 | 示例 |
|---|---|---|
| 主干分支 | `main` / `develop`(全小写,固定) | main, develop |
| 功能分支 | `feature-<scope>-<story-id>-<short-desc>` | `feature-plc-story1.8-datapersist` |
| 缺陷分支 | `fix-<scope>-<issue-id>-<short-desc>` | `fix-plc-AQEX-101-vw270-conflict` |
| 紧急分支 | `hotfix-<scope>-<issue-id>-<short-desc>` | `hotfix-plc-AQEX-150-estop-latch` |
| 发布分支 | `release-<x.y>`(无前导v) | `release-1.1` |

**scope 取值表**(与第3章提交scope一致):

| scope | 含义 | 涉及文件 |
|---|---|---|
| `plc` | PLC STL代码(FC/OB) | plc/stl/*.stl |
| `hmi` | HMI组态/变量 | docs/hmi_preparation/, *.mcpg |
| `var` | 变量地址表/编址 | docs/HMI-PLC变量地址表*.md |
| `docs` | 文档(规格书/校验报告/SOP) | docs/、plc/spec/ |
| `param` | 参数调整(VD10~VD140默认值) | 变量表参数区 |
| `chore` | 构建脚本/.gitignore/工具 | scripts/、tools/ |

**short-desc 规则**: 全小写,单词以连字符分隔,长度≤30字符,英文优先,避免拼音

### 2.3 分支保护规则

| 分支 | 保护规则 |
|---|---|
| `main` | 禁止直接推送;仅允许通过 PR 合并;PR 至少1人评审通过;CI静态分析必须通过 |
| `develop` | 禁止直接推送;仅允许通过 PR 合并;PR 至少1人评审通过 |
| `release-*` | 仅创建者与项目管理员可推送;合并到 main 后归档(不删除,标记 tag) |
| `hotfix-*` | 允许直接推送(紧急场景),但合并到 main 时必须 PR+评审 |

---

## 第3章 提交规范

### 3.1 提交信息格式(Conventional Commits)

延续项目现有提交风格(参考git log: `feat(plc)`/`fix(plc)`/`docs(交付运维)`/`docs(hmi准备)`/`docs(调试准备)`):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 3.2 type 取值表

| type | 含义 | 触发场景 | 示例 |
|---|---|---|---|
| `feat` | 新增功能 | 新FC/新报警位/新规格书 | `feat(plc): Story 1.8 加药量自学习(规格书+STL代码)` |
| `fix` | 缺陷修复 | 校验报告/静态分析问题/现场缺陷 | `fix(plc): 修复FC32 VW270跨FC写入冲突(校验P2)` |
| `docs` | 文档变更 | 规格书/校验报告/SOP/手册 | `docs(plc): PLC程序版本管理规范v1.0` |
| `refactor` | 重构(不改变功能) | 编址区迁移/代码结构调整 | `refactor(plc): 阀诊断变量区VW250~VW290重新规划` |
| `test` | 测试相关 | 验收用例/调试脚本 | `test(plc): 补充S5断电恢复回归用例` |
| `chore` | 构建/工具 | .gitignore/scripts/工具 | `chore: 配置Git LFS跟踪.mwp文件` |
| `revert` | 回滚提交 | 回滚某次合并 | `revert: 回滚feat(plc) Story1.8 (变更单AQEX-CHG-101撤销)` |

### 3.3 scope 取值表

参考2.2节,补充细化scope建议:

| scope | 用于 | 示例 |
|---|---|---|
| `fc0` | 仅修改FC0 | `fix(fc0): NETWORK6增加VW2==6条件(校验P7)` |
| `fc11` | 仅修改FC11 | `fix(fc11): VD48运算改用VD290中间变量(静态分析P6)` |
| `fc30` | 仅修改FC30 | `refactor(fc30): T50/T51 PT值迁移至VW278/VW280` |
| `fc32` | 仅修改FC32 | `fix(fc32): MOVB写字地址改为MOVW(静态分析P5)` |
| `fc3` | 仅修改FC3(报警) | `feat(fc3): 新增阀C关类报警码60/61` |
| `ob1` | 仅修改OB1 | `refactor(ob1): 调整FC调用顺序` |
| `hmi` | HMI组态/变量 | `feat(hmi): 画面1增加版本号显示` |
| `var` | 变量地址表 | `docs(var): 变量表9.2报警码同步FC3` |
| `plc` | 涉及多个FC | `fix(plc): 校验报告第二轮S2/S3.5计时失效` |
| `docs` | 仅文档 | `docs: 新增PLC程序版本管理规范v1.0` |

### 3.4 提交信息模板

```
<type>(<scope>): <简要描述,50字符内>

<详细说明,每行72字符内>
- 问题描述/背景
- 修改要点
- 涉及变量地址(如有)
- 关联变更单号 AQEX-CHG-<NNN>
- 关联Jira issue AQEX-<NNN>(如有)

关联: AQEX-CHG-123, AQEX-101
回归: 校验报告v1.2 P2/P5, 静态分析#3
```

**实际示例(对照git log风格)**:
```
fix(plc): 第二轮校验修复S2/S3.5计时失效+泵超时+断电恢复保护

校验报告v1.2发现4个问题:
- A1: FC12 VW252从未被写入,S2计时T38失效
- A2: FC14 VW254从未被写入,S3.5计时T39失效
- A3: FC12 T44/T45用固定+100而非VD58/VD62×10
- P7: FC0 NETWORK6缺VW2==6条件

新增变量分配:
- VW252: S2计时T38 PT转换值
- VW254: S3.5计时T39 PT转换值
- VW282/VW284: 潜水泵1/2 T44/T45 PT转换值
- VD292/VD294/VD296: 各FC运算中间变量

关联: 校验报告v1.2 A1/A2/A3/P7
```

### 3.5 禁止事项

| 禁止项 | 说明 |
|---|---|
| 大体积二进制提交 | `.mwp`/`.sdfp`/`.pdf`/`.docx`/`.xlsx` 单文件>1MB 必须用 Git LFS(见第8章) |
| 一次提交多个不相关变更 | 拆分为多个提交,每个提交聚焦单一变更 |
| 提交信息无 type/scope | 必须遵循3.1格式 |
| 提交信息仅写"修改bug"/"update" | subject 必须描述具体修改内容 |
| 提交未关联变更单号 | 凡涉及生产环境的变更,footer必须含 AQEX-CHG-NNN |
| 提交涉密信息 | PLC密码/HMI密码/客户IP段/服务器凭据禁止入库 |
| 强制推送到 main/develop | 仅 hotfix-* 分支允许强制推送(紧急场景) |
| --no-verify 绕过钩子 | CI静态分析/stl_static_analyzer.py必须通过 |

---

## 第4章 标签与发布

### 4.1 标签格式

| 类型 | 格式 | 示例 |
|---|---|---|
| 正式发布 | `vX.Y.Z`(带v前缀) | `v1.0.0`, `v1.0.2`, `v1.1.0` |
| 预发布 | `vX.Y.Z-rc.N` | `v1.1.0-rc.1`, `v1.1.0-rc.2` |
| 关键里程碑(可选) | `milestone-<name>` | `milestone-sat-passed` |

标签必须为**附注标签(annotated tag)**,不允许轻量标签(lightweight tag):
```
git tag -a v1.0.0 -m "发布说明"
```

### 4.2 标签说明内容(必填)

附注标签的 message 必须包含:

```
版本: vX.Y.Z
日期: YYYY-MM-DD
变更单: AQEX-CHG-NNN(主变更单)
Jira: AQEX-NNN(关联issue)

变更摘要:
<2~5句话描述本次发布主要内容>

涉及FC:
- FC0_SysInit.stl (修改: NETWORK6/7)
- FC11_State_S1_Inlet.stl (修改: VD48运算)
- FC32_ValveC_Diag.stl (修改: MOVB→MOVW)

8台PLC部署清单:
- PLC#1 (192.168.2.101): 待下装
- PLC#2 (192.168.2.102): 待下装
- PLC#3 (192.168.2.103): 待下装
- PLC#4 (192.168.2.104): 待下装
- PLC#5 (192.168.2.105): 待下装
- PLC#6 (192.168.2.106): 待下装
- PLC#7 (192.168.2.107): 待下装
- PLC#8 (192.168.2.108): 待下装

回归测试:
- 校验报告: v1.2 已通过
- 静态分析: 0 严重 / 0 警告 / <N> 提示
- SAT/FAT: 101用例全通过

下装工具: STEP 7-Micro/WIN SMART V2.5+
下装步骤: 见 PLC首次下装与上电调试Checklist_v1.0.md

回滚方案:
- 上一稳定版本: v1.0.1
- 回滚操作: 重新下装 v1.0.1 的 .mwp 文件
- 回滚审批: 项目负责人 + L3管理员双签
```

### 4.3 发布检查清单(发布前必填)

发布分支 `release-x.y` 合并到 main 前,逐项确认:

| # | 检查项 | 通过条件 | 实际结果 |
|---|---|---|---|
| 1 | 代码评审 | release-x.y → main 的 PR 至少1人评审通过 | □ |
| 2 | 静态分析 | `python tools/stl_static_analyzer.py` 严重问题=0 | □ |
| 3 | 完整性校验 | 对照校验报告v1.0检查项全部通过,JMP/LBL平衡/V区无冲突 | □ |
| 4 | 变量地址表 | 变量表v1.x已同步本次新增/修改地址 | □ |
| 5 | CHANGELOG.md | 已更新,版本号/日期/变更分类齐全 | □ |
| 6 | 版本号字段 | FC0 NETWORK0 已写入新版本号到 VW0 | □ |
| 7 | 8台PLC部署清单 | 标签说明含8台PLC IP+待下装状态 | □ |
| 8 | 回滚预案 | 已明确上一稳定版本号+回滚步骤+审批人 | □ |
| 9 | 变更单闭环 | 涉及变更单 AQEX-CHG-NNN 状态已为"待发布" | □ |
| 10 | HMI同步 | HMI变量表/组态工程已同步本次变量变更 | □ |
| 11 | 文档同步 | 规格书/校验报告/SOP已更新至对应版本 | □ |
| 12 | 验收用例 | SAT/FAT相关用例已回归通过 | □ |
| 13 | 现场准备 | 现场工程师已收到下装通知+下装窗口 | □ |
| 14 | 备份 | 8台PLC旧版 .mwp 文件已归档至 `achieve/` 目录 | □ |

清单全部通过后,执行:
```
git checkout main
git merge --no-ff release-x.y -m "release: vX.Y.Z 发布"
git tag -a vX.Y.Z -m "<标签说明,见4.2>"
git push origin main --tags
```

---

## 第5章 8台PLC版本一致性管控

### 5.1 同步下装要求

| 项 | 要求 |
|---|---|
| 下装窗口 | 同一变更单的下装必须在24小时内完成8台PLC,超时需重新评估变更 |
| 下装顺序 | 推荐顺序: PLC#1 → PLC#2 → ... → PLC#8(按IP 101→108) |
| 下装间隔 | 相邻PLC下装间隔≤30分钟(避免长时间不一致) |
| 下装工具 | STEP 7-Micro/WIN SMART V2.5+,通过以太网下装 |
| 下装后自检 | 每台下装后必须执行: ①PLC进入S0 ②HMI读取 VW0 比对版本号 ③急停功能测试 |
| 部署记录 | 8台PLC下装完成时间/操作人/版本号记录至《变更单》"实施记录"栏 |

### 5.2 版本不一致检测方法

**方法一:HMI集中读取比对**

HMI画面8系统设置页应实现8台PLC版本号集中显示:
1. HMI通过8个PLC连接(PLC_01~PLC_08)分别读取 VW0
2. 解析BCD版本号字符串
3. 8台版本号字符串比对:
   - 全部一致 → 显示绿色"✓ 版本一致 v1.0.2"
   - 任何不一致 → 显示红色"✗ 版本不一致"并列出各台版本号
   - 任一台通讯中断 → 显示黄色"? 通讯中断,无法验证"

**方法二:定期巡检脚本**

调试工程师每周执行一次版本巡检:
```bash
# scripts/version_check.sh (示例)
for i in 1 2 3 4 5 6 7 8; do
    ip="192.168.2.10$i"
    ver=$(snap7_client read $ip DB1 0 2)  # 读VW0两个字节
    echo "PLC#$i ($ip): $ver"
done
# 8台 ver 字段必须完全相同
```

**方法三:程序内部自检(可选,后续版本)**

FC0 SysInit 中增加版本号自检 NETWORK,8台PLC之间通过Modbus TCP/S7协议两两互查(限于通讯负载,默认关闭,仅在调试态启用)。

### 5.3 不一致时的处置SOP

| 步骤 | 操作 | 责任人 | 时限 |
|---|---|---|---|
| 1 | HMI发现版本不一致,立即停止该单元自动运行,转手动模式 | HMI操作员 | 立即 |
| 2 | 在变更单"实施记录"标注不一致的PLC编号+实际版本号 | 实施人 | 1小时内 |
| 3 | 排查不一致原因: ①某台下装失败 ②下装了错误版本 ③下装后未重启 | 实施人+调试工程师 | 2小时内 |
| 4 | 决策: ①补下装正确版本 ②全部回滚到上一稳定版本 | 项目负责人 | 4小时内 |
| 5 | 执行补下装/回滚,8台重新同步 | 实施人 | 8小时内 |
| 6 | 重新执行5.2版本检测,确认8台一致 | 调试工程师 | 完成后立即 |
| 7 | 变更单"实施记录"补登完整处置过程,归档 | 实施人 | 24小时内 |
| 8 | 若24小时内无法同步,触发"紧急变更流程"(见变更管理流程第4章) | 项目负责人 | — |

### 5.4 单台紧急回滚流程

仅当单台PLC出现严重故障(如无法进入S0/急停无法复位/与HMI通讯中断),且其他7台正常时,允许单台回滚:

| 步骤 | 操作 | 审批 |
|---|---|---|
| 1 | 故障确认: 该台PLC版本号与其他台一致,但运行异常 → 不适用回滚;该台PLC版本号与其他台不一致 → 进入回滚 | L2维护 |
| 2 | 选择回滚目标版本: 上一稳定版本(标签 vX.Y.Z) | L3管理员 |
| 3 | 取得该台PLC的旧版 .mwp 文件(从 achieve/ 目录或Git LFS) | 实施人 |
| 4 | 单台PLC进入STOP模式(通过HMI或现场操作) | 实施人 |
| 5 | STEP 7-Micro/WIN SMART 连接该台PLC(对应IP),下装旧版 .mwp | 实施人 |
| 6 | PLC重启进入S0,HMI读取 VW0 确认版本号回退至目标版本 | 实施人+HMI操作员 |
| 7 | 急停功能测试+手动阀门测试,确认PLC基本功能正常 | 调试工程师 |
| 8 | 该台PLC转手动模式运行,持续观察2小时无异常后恢复自动 | 调试工程师 |
| 9 | 24小时内补登《变更单》"紧急回滚记录",关联Jira缺陷单 | 实施人 |
| 10 | 评估回滚根因,7天内决定: ①补下装最新版 ②保持回滚版本至下个发布 | 项目负责人 |

**注意**: 单台回滚后,8台版本号不再一致,必须在变更单中明确标注,并在HMI侧该单元卡片显示黄色"⚠ 回滚至 vX.Y.Z"提示。

---

## 第6章 回滚方案

### 6.1 回滚决策树

```
现场反馈异常
    │
    ├── 缺陷可重现且影响安全/工艺 → 立即回滚
    │       │
    │       ├── 8台全部异常 → 全量回滚到上一稳定版本(6.2)
    │       └── 单台异常 → 单台紧急回滚(5.4)
    │
    ├── 缺陷偶发或可规避 → 评估后决定
    │       ├── 影响范围小,可手工规避 → 进入缺陷单流程,下个版本修复
    │       └── 影响范围大,无法规避 → 全量回滚(6.2)
    │
    └── 缺陷无法重现 → 进入观察期,数据收集后再决策
            └── 期间允许运行,缺陷单跟踪
```

### 6.2 Git仓库回滚

| 场景 | 命令 | 适用条件 |
|---|---|---|
| 撤销最近一次提交(保留历史) | `git revert <commit>` | 推荐,不改写历史,生成新提交 |
| 回滚到指定标签 | `git revert --no-commit <old_tag>..HEAD` then commit | 推荐,撤销区间内所有变更 |
| 强制回到旧版本(改写历史) | `git reset --hard <tag>` 然后 `git push --force-with-lease` | 仅 main 分支紧急场景,需项目负责人授权 |

**AQUA-EXPO 项目推荐策略**:
- **优先使用 revert**: 保留完整历史,符合"提交规范"要求,变更可追溯
- **仅在以下场景使用 reset**: ①发现提交包含涉密信息需彻底清除 ②误提交大体积二进制文件污染仓库
- **强制推送 main 分支需双签**: 项目负责人 + 操作人签字记录,事后必须全员通知

### 6.3 PLC程序回滚

| 步骤 | 操作 | 工具 |
|---|---|---|
| 1 | 从 Git LFS 取得上一稳定版本 .mwp 文件 | `git lfs checkout v1.0.1 -- plc/bin/AQUA-EXPO_PLC_v1.0.1.mwp` |
| 2 | 8台PLC依次进入STOP | STEP 7-Micro/WIN SMART 或 HMI |
| 3 | 依次下装 .mwp 到 8台PLC(IP 101~108) | STEP 7-Micro/WIN SMART |
| 4 | 8台PLC重启,确认进入S0 | HMI观察 |
| 5 | 读取 8台 PLC 的 VW0,确认版本号回退至目标版本 | HMI画面8 |
| 6 | 急停功能测试(每台) | 现场按钮+HMI观察 |
| 7 | 状态机基本流程测试(S0→S1→S2) | HMI手动操作 |
| 8 | 报警功能测试(模拟急停+消音+确认) | 现场操作 |
| 9 | 8台PLC恢复自动运行 | HMI操作 |

### 6.4 参数回滚

PLC回滚到旧版程序后,V区参数(VD10~VD140)也需同步回滚:

| 参数类型 | 回滚方式 |
|---|---|
| HMI设定参数(VD10~VD66) | 从备份的参数快照(HMI侧导出CSV)重新下发 |
| 实测值(VD70~VD102) | 不需回滚,PLC实测值由现场状态决定 |
| 纠偏变量(VD104~VD140) | 保留当前值(纠偏是基于历史数据,回滚程序不影响纠偏逻辑) |
| 断电保持时间戳(DT10) | 保留当前值(断电恢复逻辑由FC0处理) |

**参数快照备份策略**:
- 每次发布前,HMI画面4参数设置页导出当前参数CSV,存入 `achieve/params/AQUA-EXPO_Params_vX.Y.Z_<date>.csv`
- 8台PLC参数一致(变量表1.1节),导出一份即可,回滚时8台统一下发

### 6.5 回滚验证

回滚完成后必须验证:

| # | 验证项 | 验证方法 | 通过条件 |
|---|---|---|---|
| 1 | 版本号一致 | HMI画面8读取8台 VW0 | 全部一致且等于目标版本 |
| 2 | 急停功能 | 按下急停,观察PLC进S_ERROR + 报警 | 8台均正常 |
| 3 | 状态机流程 | S0→S1→S2→S3→S3.5→S4→S5→S6→S7 | 流程完整无卡死 |
| 4 | 阀门动作 | 手动操作阀A/B/C开关 | 8台均正常 |
| 5 | 报警功能 | 模拟急停+消音+确认 | 报警位正确置位/复位 |
| 6 | Modbus通讯 | 读取VW4泵状态+VD86流量计 | 通讯正常 |
| 7 | HMI通讯 | 8台PLC均能从HMI访问 | 无通讯中断 |
| 8 | 运行2小时观察 | 持续运行无新报警 | 无异常 |

### 6.6 回滚审批

| 回滚类型 | 审批人 | 时限 |
|---|---|---|
| 单台紧急回滚(5.4) | L3管理员(口头/电话) | 立即 |
| 全量回滚(6.2/6.3) | 项目负责人 + L3管理员(双签) | 4小时内 |
| 回滚到非上一稳定版本(跳跃回滚) | 项目负责人 + 公司技术负责人 | 24小时内 |
| 回滚后再次升级 | 项目负责人(基于回滚根因分析) | 7天内 |

回滚操作必须形成《回滚记录》文档,归档至 `docs/achieve/rollback/` 目录,内容含: 回滚时间/原因/操作人/审批人/目标版本/验证结果/根因分析/后续计划。

---

## 第7章 变更记录模板

### 7.1 CHANGELOG.md 格式

仓库根目录维护 `CHANGELOG.md`,采用 [Keep a Changelog](https://keepachangelog.com/) 风格:

```markdown
# 变更记录

本项目所有重要变更均记录于此文件。
版本号遵循语义化版本 vX.Y.Z(见 PLC程序版本管理规范_v1.0.md)。
日期格式: ISO 8601 YYYY-MM-DD。

## [Unreleased]

### Added
- (待发布的新增功能)

### Changed
- (待发布的变更)

### Fixed
- (待发布的修复)

## [1.0.2] - 2026-07-18

### Added
- 新增 PLC程序版本管理规范 v1.0(docs/PLC程序版本管理规范_v1.0.md)
- 新增 代码评审checklist v1.0(docs/代码评审checklist_v1.0.md)
- 新增 变更管理流程 v1.0(docs/变更管理流程_v1.0.md)
- FC0 NETWORK0 增加版本号登记(VW0 写入 BCD 版本号)

### Fixed
- FC32 L138/L159 的 MOVB 1,VW270 改为 MOVW 1,VW270 (校验报告v1.0 P5)
- FC19 L82 注释 "V0.5" 更正为 "V0.7" (校验报告v1.0 P1)
- 变量表9.2 报警码同步 FC3 实际编码 (校验报告v1.0 P4)

### Changed
- FC30 T50/T51 PT 值由 VW270/VW272 迁移至 VW278/VW280,消除跨FC冲突 (校验报告v1.0 P2)

## [1.0.1] - 2026-07-15

### Fixed
- FC12 VW252 从未被写入,S2计时T38失效 (校验报告v1.2 A1)
- FC14 VW254 从未被写入,S3.5计时T39失效 (校验报告v1.2 A2)
- FC12 T44/T45 用固定+100改为 VD58/VD62×10 (校验报告v1.2 A3)
- FC0 NETWORK6 增加 VW2==6 条件保护 (校验报告v1.2 P7)

## [1.0.0] - 2026-07-10

### Added
- Story 1.2 状态机S0-S7骨架(OB1+FC0~FC4+FC10~FC19)
- Story 1.3 阀门A/B/C诊断(FC30~FC32)
- Story 1.4 配液节奏三层纠偏(FC40)
- Story 1.5 急停双通道+安全继电器反馈(FC2/FC19)
- Story 1.6 报警分级与消音消光(FC3)
- Story 1.7 断电保持与恢复逻辑(FC0)
- 完整变量地址表 v1.0(91变量)
- 完整性校验报告 v1.0(2轮校验,10问题全修复)
- SAT/FAT验收用例 v1.0(101用例)
```

### 7.2 变更分类

| 分类 | 含义 | 对应 type |
|---|---|---|
| Added | 新增功能 | feat |
| Changed | 变更现有功能 | refactor/feat |
| Deprecated | 即将移除的功能 | — |
| Removed | 已移除的功能 | refactor |
| Fixed | 缺陷修复 | fix |
| Security | 安全相关修复 | fix(安全类) |

### 7.3 变更条目格式

每条变更条目建议格式:
```
- <简要描述> (<来源/依据>)
```

**示例**:
- `FC32 L138/L159 的 MOVB 1,VW270 改为 MOVW 1,VW270 (校验报告v1.0 P5)`
- `新增 PLC程序版本管理规范 v1.0 (变更单 AQEX-CHG-100)`

### 7.4 更新时机

| 时机 | 操作 |
|---|---|
| feature/fix 分支合并到 develop | 在 [Unreleased] 区追加条目 |
| 创建 release-x.y 分支 | [Unreleased] 改为 [x.y.0] + 日期 |
| release-x.y 合并到 main 并打 tag | CHANGELOG.md 一并提交,版本号确定 |
| hotfix 修复 | 在对应版本号下追加 Fixed 条目,新增 [x.y.z+1] 段 |

---

## 第8章 仓库管理

### 8.1 .gitignore 规则

```gitignore
# === AQUA-EXPO .gitignore ===

# === IDE/编辑器 ===
.vscode/
.idea/
*.swp
*.swo
*~

# === STEP 7-Micro/WIN SMART 临时文件 ===
*.tmp
*.bak
*.~mwp
*.~sdfp

# === 编译/构建产物 ===
build/
dist/
*.log

# === 操作系统 ===
.DS_Store
Thumbs.db
desktop.ini

# === 敏感信息(严禁入库) ===
*.env
*.secret
credentials.txt
passwords.txt
local_ip_config.txt

# === 大体积二进制(走Git LFS,见8.2) ===
# .mwp/.sdfp 由 LFS 跟踪,不在此忽略
# 以下大文件类型若直接提交则忽略:
*.iso
*.vmdk
*.mp4
*.avi

# === 参数快照(本地生成,不入库) ===
achieve/params/*.csv.local

# === 调试日志 ===
logs/
*.log.*
```

### 8.2 Git LFS 跟踪规则

**问题**: PLC项目必然涉及大体积二进制文件:
- `.mwp`: STEP 7-Micro/WIN SMART 项目文件(8台PLC×多版本,单文件可达数MB)
- `.sdfp`: 项目备份文件
- `.pdf`/`.docx`/`.xlsx`: 设备协议手册/规格书

**建议**: 采用 Git LFS 跟踪,而非直接 .gitignore 排除。

**理由**:
- .mwp 文件是PLC程序的"二进制快照",需要与STL源码版本严格对应,必须入库追溯
- 直接入库会快速膨胀仓库(每次发布8台×多版本,LFS避免此问题)
- LFS 仍可按 tag/commit 检出对应版本的 .mwp

**LFS 跟踪配置**:
```bash
git lfs install
git lfs track "*.mwp"
git lfs track "*.sdfp"
git lfs track "*.pdf"
git lfs track "*.docx"
git lfs track "*.xlsx"
git add .gitattributes
git commit -m "chore: 配置Git LFS跟踪.mwp/.sdfp/.pdf/.docx/.xlsx"
```

`.gitattributes` 内容:
```
*.mwp  filter=lfs diff=lfs merge=lfs -text
*.sdfp filter=lfs diff=lfs merge=lfs -text
*.pdf  filter=lfs diff=lfs merge=lfs -text
*.docx filter=lfs diff=lfs merge=lfs -text
*.xlsx filter=lfs diff=lfs merge=lfs -text
```

**LFS 配额提醒**: GitHub 免费账户 LFS 配额 1GB 存储+1GB/月流量,本项目8台PLC×多版本预计<500MB,够用;超出后购买额外包。

### 8.3 敏感信息管理

| 类型 | 处理方式 |
|---|---|
| PLC密码 | 严禁入库,以 `***` 占位,实际密码存现场保密文档 |
| HMI密码 | 严禁入库,同上 |
| 客户IP段 | 变量表1.1节IP示例(192.168.2.101~108)可入库,实际部署IP如不同,现场另行配置 |
| 服务器凭据 | 严禁入库 |
| API Token | 严禁入库,使用 GitHub Secrets |
| 设备序列号 | 可入库(非敏感) |

**Git Secret 扫描**: 仓库启用 GitHub Secret Scanning + Push Protection,防止误推送密钥。

### 8.4 目录结构规范

```
AQUA-EXPO/
├── .gitattributes              # Git LFS 配置
├── .gitignore                  # 忽略规则
├── CHANGELOG.md                # 变更记录(Keep a Changelog 风格)
├── README.md                   # 项目说明
├── docs/                       # 项目文档
│   ├── PLC程序版本管理规范_v1.0.md       # (本文档)
│   ├── 代码评审checklist_v1.0.md          # 
│   ├── 变更管理流程_v1.0.md               # 
│   ├── PLC代码完整性校验报告_v1.0.md       # 
│   ├── PLC代码静态分析报告_v1.0.md         # 
│   ├── HMI-PLC变量地址表_v1.0.md           # 
│   ├── 项目交付文档总索引_v1.0.md           # 
│   ├── 药液配置加注控制系统_PLC设计文档.md  # 
│   ├── HMI画面架构规划文档.md               # 
│   ├── SAT_FAT验收测试用例_v1.0.md          # 
│   ├── hmi_preparation/                    # HMI组态准备材料
│   │   └── ...
│   ├── commissioning/                      # 现场调试准备
│   │   └── ...
│   └── achieve/                            # 历史版本归档(只读)
│       ├── plc_v1.0.0/                     # 旧版STL+二进制
│       ├── params/                         # 参数快照CSV
│       └── rollback/                       # 回滚记录
├── plc/                                     # PLC代码
│   ├── stl/                                 # STL源代码(20个FC)
│   │   ├── OB1_MAIN.stl
│   │   ├── FC0_SysInit.stl
│   │   ├── ... (共20个)
│   │   └── FC40_RhythmCorrection.stl
│   ├── spec/                                # 程序设计规格书
│   │   └── ... (7份)
│   └── bin/                                 # 二进制.mwp/.sdfp(LFS跟踪)
│       └── AQUA-EXPO_PLC_v1.0.2.mwp
├── hmi/                                     # HMI组态工程(待HMI到货)
│   └── ...
├── tools/                                   # 工具脚本
│   ├── stl_static_analyzer.py               # STL静态分析器
│   └── version_check.sh                     # 版本一致性巡检
├── scripts/                                 # 自动化脚本
│   └── ...
├── 注射泵/                                  # 注射泵设备资料
├── 流量计/                                  # 流量计设备资料
└── achieve/                                 # (顶层历史归档,与 docs/achieve/ 同义,择一)
```

**目录约定**:
- `docs/achieve/`: 文档历史版本(只读,只增不改)
- `docs/achieve/rollback/`: 回滚记录
- `docs/achieve/params/`: 参数快照CSV
- `plc/stl/`: STL源代码(可改)
- `plc/bin/`: 二进制 .mwp 文件(LFS跟踪,按版本归档)
- `tools/`: 开发工具(stl_static_analyzer.py 等)
- `achieve/`(顶层): 与 `docs/achieve/` 二选一,本项目约定使用 `docs/achieve/`

### 8.5 仓库维护

| 任务 | 频率 | 责任人 |
|---|---|---|
| 检查 LFS 配额 | 每月 | 配置管理工程师 |
| 清理已合并的临时分支 | 每月 | 配置管理工程师 |
| 验证 .gitignore 有效性 | 每季度 | 配置管理工程师 |
| 备份仓库(GitHub → 本地) | 每月 | 配置管理工程师 |
| 审计提交规范合规性 | 每季度 | 配置管理工程师 |
| 审计涉密信息扫描结果 | 每季度 | 配置管理工程师 + 安全负责人 |

---

**文档版本**: v1.0
**编制日期**: 2026-07-18
**编制人**: 配置管理与质量保证工程师
**下次更新触发**: ①首次正式发布后回顾 ②8台PLC部署实施后反馈 ③Git LFS配置实际落地后调整 ④分支策略实际运行3个月后优化
