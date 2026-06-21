# 六爻迭代解卦 Skill（Codex-ready 中文版）

这是一个面向 Codex / Claude Code / OpenClaw 的六爻解卦 skill 模板。设计目标不是“让模型凭感觉断卦”，而是把六爻解卦拆成可检查的流程：**起卦/装卦 → 古籍检索 → 独立判断 → 结果分级 → 事后反馈 → 规则迭代**。

本 skill 参考你之前的大六壬 skill 结构，但针对六爻做了三项关键调整：

1. **默认 fresh 模式**：新卦不读取旧案例，避免“之前案例影响新使用”。
2. **古籍 RAG 与案例记忆分离**：古籍可以作为证据；真实案例默认只做事后复盘。
3. **装卦与断卦分离**：允许你用外部排盘软件/网页排盘，也允许用本 skill 的基础脚本记录六爻结构。

> 注意：本 skill 不把六爻结论当成确定事实，也不建议用于医疗、法律、金融等高风险决策。

---

## 1. 适合什么场景

适合：

- 你已经有本卦、变卦、世应、六亲、六神、动爻等信息，希望 Codex 按固定流程辅助分析。
- 你有《增删卜易》《卜筮正宗》《易隐》《黄金策》《断易天机》等古籍 md/txt，想建立本地检索库。
- 你想长期积累案例，但不想让旧案例污染新卦。
- 你想做“六爻学习—反馈—规则迭代”的个人知识库。

不适合：

- 想让模型在没有卦盘、没有问题背景的情况下直接断具体结果。
- 想把单个案例反馈直接变成硬规则。
- 想把旧案例作为新卦的默认判断依据。

---

## 2. 安装到 Codex

Codex skill 通常放在：

```powershell
$env:USERPROFILE\.agents\skills
```

Windows PowerShell：

```powershell
$SkillRoot = "$env:USERPROFILE\.agents\skills"
New-Item -ItemType Directory -Force $SkillRoot
Expand-Archive ".\liuyao_iterative_skill_codex_ready_cn.zip" -DestinationPath $SkillRoot -Force
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
按 fresh 模式分析这个六爻卦，不参考历史案例。
```

---

## 3. 目录结构

```text
liuyao-iterative-divination/
├─ SKILL.md
├─ README.md
├─ README.zh-CN.md
├─ CODEX_TEST_PROMPTS.md
├─ scripts/
│  ├─ ingest_books.py                 # 建立古籍 chunk 索引
│  ├─ retrieve_passages.py            # 单次关键词检索
│  ├─ retrieve_for_divination.py      # 按六爻主题组合检索
│  ├─ liuyao_basic_chart.py           # 基础六爻记录/本变卦辅助脚本
│  ├─ add_case.py                     # 事后写入案例
│  ├─ update_feedback.py              # 追加反馈
│  ├─ summarize_learning.py           # 汇总反馈，不自动改规则
│  └─ reset_runtime_memory.py         # 清空/备份运行记忆
├─ resources/
│  ├─ books_raw_md/                   # 原始 md 古籍放这里
│  ├─ books_corrected/                # 清洗校对后的 md/txt 放这里
│  ├─ books_metadata/book_manifest.yaml
│  ├─ index/                          # 自动生成索引
│  ├─ templates/                      # 输入、输出、学习协议模板
│  └─ schemas/                        # 案例和反馈 JSON schema
├─ memory/
│  ├─ casebook.jsonl                  # 本地私有案例，默认不读
│  ├─ feedback_log.jsonl              # 本地反馈，默认不读
│  └─ incoming_cases/
└─ examples/
```

---

## 4. 古籍 md 应该放哪里

原始 OCR / MinerU / Markdown 输出，先放：

```text
resources/books_raw_md/
```

例如：

```text
resources/books_raw_md/增删卜易.md
resources/books_raw_md/卜筮正宗.md
resources/books_raw_md/易隐.md
resources/books_raw_md/黄金策.md
resources/books_raw_md/断易天机.md
```

清洗校对后，再放：

```text
resources/books_corrected/
```

例如：

```text
resources/books_corrected/增删卜易.md
resources/books_corrected/卜筮正宗.md
resources/books_corrected/易隐.md
resources/books_corrected/黄金策.md
resources/books_corrected/断易天机.md
```

建议流程：

```text
PDF/OCR 原文 → books_raw_md/ → 清洗校对 → books_corrected/ → ingest_books.py → index/book_chunks.jsonl
```

建索引：

```powershell
python scripts/ingest_books.py
```

检索：

```powershell
python scripts/retrieve_passages.py --query "用神 世爻 应爻 动爻 空亡 月建 日辰" --top-k 8
```

综合检索：

```powershell
python scripts/retrieve_for_divination.py --base "婚姻 官鬼 妻财 世应 六合 冲克" --top-k 5
```

---

## 5. 四种运行模式

### 5.1 fresh：默认新卦模式

用途：新问题、新卦、新判断。

规则：

- 不读取 `memory/casebook.jsonl`
- 不读取 `memory/feedback_log.jsonl`
- 不检索历史类案
- 只用当前卦盘、六爻通用规则、古籍检索结果
- 输出末尾声明：`本次为 fresh 模式，未调用历史案例。`

推荐 prompt：

```text
$liuyao-iterative-divination
按 fresh 模式解这个六爻卦，不参考历史案例。
问题：……
起卦时间：……
本卦：……
变卦：……
世应：……
动爻：……
六亲六神：……
```

### 5.2 literature_only：只查古籍

用途：学习某个规则，不断具体卦。

```text
只查古籍：用神、原神、忌神、仇神在婚姻占中的取法。
```

### 5.3 analogical_case：类案参考

用途：你明确说“参考历史案例”。

要求：

- 先独立解卦
- 后列类案
- 类案不能覆盖主判断
- 必须说明类案相似点和不相似点

### 5.4 posthoc_learning：反馈学习

用途：事情应验后做复盘。

要求：

- 只记录反馈，不直接改核心规则
- 标注：支持、部分支持、反向、无法验证、样本异常
- 形成待验证假设，而不是立刻写成定论

---

## 6. 推荐学习路线

### 第一阶段：先学装卦结构

目标：看懂一张六爻盘。

需要掌握：

- 本卦、变卦、互卦可先不急
- 世爻、应爻
- 六亲：父母、兄弟、子孙、妻财、官鬼
- 六神：青龙、朱雀、勾陈、螣蛇、白虎、玄武
- 动爻、暗动、伏神、飞神
- 月建、日辰、旬空

### 第二阶段：再学用神体系

不要一开始就背大量断语。先把“占事—用神”固定住：

| 占事 | 常用用神 |
|---|---|
| 感情/婚姻 | 男占妻财，女占官鬼，同时看世应 |
| 求财 | 妻财为用，子孙为财源，兄弟为劫财 |
| 工作/考试/名位 | 官鬼、父母、世爻 |
| 疾病 | 官鬼、世爻、子孙、父母视病因而定 |
| 出行/行人 | 世应、用神、动爻、日月冲合 |

### 第三阶段：学旺衰冲合空破

核心顺序：

```text
占事定位 → 用神 → 世应用神关系 → 日月旺衰 → 动爻生克 → 空破墓绝 → 变爻趋势 → 应期
```

### 第四阶段：做案例复盘

每个案例至少记录：

- 起卦时间
- 起卦方式
- 问题原文
- 卦盘结构
- 当时判断
- 后验结果
- 哪条判断对/错
- 是否有混杂因素

---

## 7. 迭代优化方法

不要让 skill “自动学习一切”。建议采用人工验收的迭代：

1. `fresh` 模式独立解卦。
2. 事后把结果写入 `feedback_log.jsonl`。
3. 每 20–30 个案例做一次 `summarize_learning.py` 汇总。
4. 只把重复出现、方向稳定、反例少的经验写入 `memory/rule_bank.yaml`。
5. 每次改 `SKILL.md` 后，用 `CODEX_TEST_PROMPTS.md` 做污染测试。

不要做：

- 不要把旧案例放进默认上下文。
- 不要把所有古籍 md 一次性塞进 `SKILL.md`。
- 不要让 Codex 每次都读完整古籍。
- 不要把单次应验当成硬规则。

---

## 8. 本地脚本烟测

进入 skill 目录：

```powershell
cd "$env:USERPROFILE\.agents\skills\liuyao-iterative-divination"
```

检查 Python 脚本：

```powershell
python -m py_compile scripts\*.py
```

建索引：

```powershell
python scripts/ingest_books.py
```

没有放入古籍时，脚本会提示没有可索引文件；这是正常的。放入 md/txt 后重新运行即可。

基础卦盘记录示例：

```powershell
python scripts/liuyao_basic_chart.py --lines 7,8,9,7,8,6 --question "测试卦" --date-ganzhi "甲子日" --month-branch "午"
```

---

## 9. GitHub 上传注意事项

可以上传：

- `SKILL.md`
- `README.md`
- `scripts/`
- `resources/templates/`
- `resources/schemas/`
- 空的 `memory/` 结构

不要上传：

- 真实问卦案例
- 反馈记录
- 含个人信息的截图/OCR
- 未确认版权状态的古籍全文
- 本地生成的大索引文件

公开仓库建议只提供目录和模板，古籍文本由用户自己放入本地。

---

## 10. 常见问题

### Q1：为什么默认不参考旧案例？

因为旧案例会产生“类案污染”。模型容易把相似问题的旧结论迁移到新卦，导致没有先完成独立判断。

### Q2：古籍越多越好吗？

不是。六爻书很多，但断法体系有差异。建议先用 3–5 本核心书做稳定索引，再逐步加入汇编类文本。

### Q3：md 和 txt 哪个更好？

校对后的 md 更好，因为标题层级能保留章节结构；如果 OCR 很乱，先转 txt 清洗也可以。

### Q4：能不能接入现成排盘库？

可以。推荐把外部排盘库当“计算层”，本 skill 作为“解释层 + 检索层 + 反馈层”。不要让 LLM 自己凭空装卦。
