# 冲突登记层

这里专门记录流派冲突。

建议建立：

- 用神冲突表.md
- 旺衰权重冲突表.md
- 动变冲突表.md
- 飞伏神冲突表.md
- 六神象意冲突表.md
- 应期冲突表.md
- 现代卦例降权规则.md

每个冲突条目建议使用：

```yaml
conflict_id: yongshen_love_001
topic: 感情占用神
schools:
  - name: 默认纳甲六爻
    result: 男占女以财为主，女占男以官鬼为主，已有对象并看世应。
    confidence: high
  - name: 象意派/现代案例派
    result: 可能更重应爻、动爻、六神和爻位象。
    confidence: low_to_medium
resolution_policy: 并列输出。默认主判以用神与世应结构为先，象意派作补充。
```
