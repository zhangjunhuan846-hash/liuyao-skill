# 六爻迭代解卦 Skill（合并流派冲突版）

这是一个面向 Codex / Claude Code / OpenClaw 的六爻解卦 skill。新版已把原来的“六爻迭代解卦 skill”和“流派冲突并列分析 skill”合并到同一个项目里。

核心目标：

1. **fresh 模式独立解卦**：新卦默认不读取旧案例，避免历史案例污染。
2. **古籍 RAG 与案例记忆分离**：古籍可以作为规则证据；真实案例默认只用于事后复盘。
3. **流派矛盾并列输出**：遇到用神、旺衰、飞伏神、六神象意、应期等冲突时，不强行合并，而是列出所有可辨识结果，并标注流派、来源、证据链、冲突点和置信度。
4. **现代案例降权**：南山真人、论坛卦例、课程讲义等默认不检索；只有用户明确要求时才作为现代案例派参考。

> 注意：本 skill 不把六爻结论当成确定事实，也不建议用于医疗、法律、金融等高风险决策。

---

## 1. 安装到 Codex

Codex skill 通常放在：

```powershell
$env:USERPROFILE\.agents\skills
```

Windows PowerShell：

```powershell
$SkillRoot = "$env:USERPROFILE\.agents\skills"
New-Item -ItemType Directory -Force $SkillRoot
Expand-Archive ".\liuyao-iterative-divination-merged-school-conflict.zip" -DestinationPath $SkillRoot -Force
```

最终结构应为：

```text
C:\Users\你的用户名\.agents\skills\liuyao-iterative-divination\SKILL.md
```

在 Codex 里输入：

```text
/skills
```

应能看到：

```text
liuyao-iterative-divination
```

显式调用：

```text
$liuyao-iterative-divination
按 fresh 模式分析这个六爻卦，不参考历史案例。如果有流派矛盾，把所有结果都列出来并标注流派。
```

---

## 2. 目录结构

```text
liuyao-iterative-divination/
├─ SKILL.md
├─ README.md
├─ README.zh-CN.md
├─ CODEX_TEST_PROMPTS.md
├─ config/
│  ├─ school_registry.yml            # 流派注册表
│  ├─ rule_priority.yml              # 规则优先级和置信度规则
│  └─ retrieval_policy.yml           # 检索开关和冲突触发条件
├─ knowledge/
│  ├─ 00_basic_terms/                # 基础术语
│  ├─ 01_core_classics/              # 核心古籍
│  ├─ 02_auxiliary_systems/          # 辅助流派
│  ├─ 03_modern_cases/               # 现代案例，默认不检索
│  └─ 04_conflict_registry/          # 冲突登记表
├─ scripts/
│  ├─ ingest_books.py                # 建立古籍/知识库 chunk 索引
│  ├─ retrieve_passages.py           # 单次关键词检索
│  ├─ retrieve_for_divination.py     # 按六爻主题组合检索
│  ├─ liuyao_basic_chart.py          # 基础六爻记录/本变卦辅助脚本
│  ├─ add_case.py                    # 事后写入案例
│  ├─ update_feedback.py             # 追加反馈
│  ├─ summarize_learning.py          # 汇总反馈，不自动改规则
│  └─ reset_runtime_memory.py        # 清空/备份运行记忆
├─ resources/
│  ├─ books_raw_md/                  # 原始 OCR/MinerU Markdown
│  ├─ books_corrected/               # 清洗校对后的 md/txt
│  ├─ books_metadata/book_manifest.yaml
│  ├─ index/                         # 自动生成索引
│  ├─ templates/                     # 输入、输出、学习协议模板
│  └─ schemas/                       # 案例和反馈 JSON schema
├─ memory/
│  ├─ casebook.jsonl                 # 本地私有案例，fresh 默认不读
│  ├─ feedback_log.jsonl             # 本地反馈，fresh 默认不读
│  └─ incoming_cases/
├─ raw_pdfs/                         # 原始 PDF，只归档，不直接检索
├─ templates/                        # 流派冲突版模板
└─ examples/
```

---

## 3. 古籍和案例应该放哪里

### 3.1 原始 PDF

放在：

```text
raw_pdfs/
```

PDF 太大或 OCR 未校对时，不建议直接给 skill 检索。

### 3.2 原始 OCR / MinerU Markdown

放在：

```text
resources/books_raw_md/
```

### 3.3 清洗校对后的古籍文本

放在：

```text
resources/books_corrected/
```

也可以按流派分层放入 `knowledge/`：

```text
knowledge/01_core_classics/      火珠林、黄金策、增删卜易、卜筮正宗
knowledge/02_auxiliary_systems/  易隐、断易天机、飞伏神、六神象意、神煞、纳音等
knowledge/03_modern_cases/       南山真人卦例、现代案例、论坛卦例
knowledge/04_conflict_registry/  用神、旺衰、飞伏神、六神象意、应期冲突表
```

### 3.4 推荐古籍优先级

第一批建议先放：

```text
火珠林
黄金策
增删卜易
卜筮正宗
```

第二批再放：

```text
易隐
断易天机
卜筮全书
海底眼
易林补遗
筮学指要
```

南山真人材料建议放：

```text
knowledge/03_modern_cases/南山真人卦例_modern_case.md
```

并加元数据：

```yaml
---
title: 南山真人卦例
school: 现代案例派
source_type: modern_case
authority_level: C
retrieval_default: false
use_mode: example_only
warning: 仅用于参考象意展开，不作为基础规则来源，不得直接套断。
---
```

---

## 4. 每个 md 文件建议加元数据

核心古籍：

```yaml
---
title: 火珠林
school: 传统纳甲六爻
source_type: core_classic
authority_level: A
retrieval_default: true
use_mode: rule_source
notes: 作为默认主体系基础规则来源之一。
---
```

辅助流派：

```yaml
---
title: 飞伏神规则
school: 飞伏神取法
source_type: auxiliary_system
authority_level: B
retrieval_default: conditional
use_mode: auxiliary_rule
notes: 用神不现或伏藏关键时调用。
---
```

现代案例：

```yaml
---
title: 南山真人卦例
school: 现代案例派
source_type: modern_case
authority_level: C
retrieval_default: false
use_mode: example_only
warning: 不得作为基础规则来源。
---
```

杂项合集：

```yaml
---
title: 六爻秘籍合集
school: 杂项未校资料
source_type: misc_untrusted
authority_level: D
retrieval_default: false
use_mode: manual_reference_only
warning: 默认不检索，只能人工核验。
---
```

---

## 5. 建索引与检索

建索引：

```powershell
python scripts/ingest_books.py
```

默认检索核心古籍、辅助规则和冲突表，不检索现代案例：

```powershell
python scripts/retrieve_passages.py --query "用神 世爻 应爻 动爻 空亡 月建 日辰" --top-k 8
```

按书名过滤：

```powershell
python scripts/retrieve_passages.py --book 增删卜易 --query "用神 动爻 月建 日辰" --top-k 5
```

检索现代案例，需要显式开启：

```powershell
python scripts/retrieve_passages.py --query "南山真人 感情 六神 世应" --include-modern-cases --top-k 8
```

检索杂项未校资料，需要显式开启：

```powershell
python scripts/retrieve_passages.py --query "某口诀" --include-misc --top-k 8
```

组合检索：

```powershell
python scripts/retrieve_for_divination.py --base "婚姻 官鬼 妻财 世应 六合 冲克" --top-k 5
```

组合检索并包含现代案例：

```powershell
python scripts/retrieve_for_divination.py --base "婚姻 官鬼 妻财 世应 六合 冲克" --include-modern-cases --top-k 5
```

---

## 6. 四种主要模式

### 6.1 fresh：默认新卦模式

```text
$liuyao-iterative-divination
按 fresh 模式解这个六爻卦，不参考历史案例。如果流派有矛盾，请全部列出来。
问题：……
起卦时间：……
本卦：……
变卦：……
世应：……
动爻：……
六亲六神：……
```

要求：

- 不读取 `memory/casebook.jsonl`
- 不读取 `memory/feedback_log.jsonl`
- 不检索历史类案
- 只用当前卦盘、六爻通用规则、古籍检索结果
- 末尾声明：`本次为 fresh 模式，未调用历史案例。`

### 6.2 literature_only：只查古籍

```text
只查古籍：用神、原神、忌神、仇神在婚姻占中的取法。
```

### 6.3 school_comparison：流派比较

```text
同一卦按默认纳甲、飞伏神、六神象意、南山真人风格分别分析，互相矛盾的地方全部标注。
```

### 6.4 posthoc_learning：反馈学习

```text
把这个案例作为 posthoc_learning 复盘，标注支持/部分支持/反向/无法验证/样本异常，不要直接改规则。
```

---

## 7. 流派冲突输出格式

遇到矛盾时，必须使用类似格式：

| 序号 | 流派/体系 | 主要来源 | 判断结果 | 证据链 | 与其他体系的冲突点 | 置信度 |
|---|---|---|---|---|---|---|
| A | 默认纳甲六爻 | 增删卜易/卜筮正宗 | ... | 用神、月日、动变... | 与象意派不同 | 高/中/低 |
| B | 飞伏神取法 | 飞伏神规则 | ... | 伏神、飞神、月日... | 与明现用神取法不同 | 中 |
| C | 六神象意派 | 六神象意/现代案例 | ... | 青龙/白虎/玄武... | 与主结构方向不同 | 低 |
| D | 现代案例派 | 南山真人卦例 | ... | 象意展开、类案参考... | 不作为主判据 | 低 |

最后可以给“默认采用判断”，但不能删除其他流派结果。

---

## 8. 案例与反馈

添加案例：

```powershell
python scripts/add_case.py --file examples/sample_case.json
```

添加反馈：

```powershell
python scripts/update_feedback.py --case-id CASE_ID --outcome partial --note "实际结果..."
```

汇总反馈：

```powershell
python scripts/summarize_learning.py
```

清空运行记忆：

```powershell
python scripts/reset_runtime_memory.py --backup
```

---

## 9. 重要原则

- 核心古籍规则优先于现代案例。
- 现代案例默认不检索。
- 用户指定流派时，优先列出该流派，但仍要说明默认体系是否同意。
- 六神、神煞、纳音、爻位和象意只作辅助，不能推翻主结构。
- 用神、世应、月日、动变、生克制化是主证据链。
- 遇到流派矛盾，宁可并列展示，也不要假装统一。
