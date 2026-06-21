# 古籍与流派检索规则

- 核心规则书优先：《火珠林》《黄金策》《增删卜易》《卜筮正宗》。
- 辅助流派、注本、现代案例必须标注来源和流派。
- OCR 未校对文本降权。
- 现代案例、南山真人卦例、论坛卦例默认不检索；只有用户明确要求时才开启。
- 一条断语只能作为证据之一，不能替代当前卦盘结构。
- 检索词应包含：占事、用神、世应、动爻、日月、空破、冲合、六亲。
- 遇到同一问题有不同取法，必须输出并列表，而不是合并成单一结论。

常用命令：

```bash
python scripts/retrieve_passages.py --query "用神 世爻 应爻 动爻 空亡 月建 日辰" --top-k 8
python scripts/retrieve_passages.py --query "南山真人 感情 六神" --include-modern-cases --top-k 8
python scripts/retrieve_for_divination.py --base "婚姻 官鬼 妻财 世应 六合 冲克" --top-k 5
```
