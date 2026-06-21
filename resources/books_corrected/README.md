# books_corrected

这里放清洗校对后的六爻古籍文本，支持 `.md` 和 `.txt`。

建议优先放核心书：

1. 《增删卜易》
2. 《卜筮正宗》
3. 《易隐》
4. 《黄金策》
5. 《断易天机》
6. 《火珠林》

运行：

```bash
python scripts/ingest_books.py
```

会生成 `resources/index/book_chunks.jsonl` 和 `resources/index/book_stats.json`。
