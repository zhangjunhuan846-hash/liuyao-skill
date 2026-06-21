# Codex 测试 Prompts

## 1. fresh 模式污染测试

```text
$liuyao-iterative-divination
按 fresh 模式解一个测试卦，不参考历史案例。最后说明是否读取了 memory/casebook.jsonl。
问题：测试感情走势。
本卦：水火既济，变卦：泽火革。
动爻：五爻。
世应、六亲、六神未知，请只做不完整分析。
```

预期：必须说明“未调用历史案例”，且不得声称读取旧案。

## 2. 古籍检索测试

```text
$liuyao-iterative-divination
只查古籍，不解具体卦。检索：用神、世爻、应爻、动爻、月建、日辰。
```

## 3. 类案模式测试

```text
$liuyao-iterative-divination
先按 fresh 模式独立解卦，再参考历史类案。类案必须单独列出，不能覆盖主判断。
```

## 4. 反馈复盘测试

```text
$liuyao-iterative-divination
把这个案例作为 posthoc_learning 复盘，标注支持/部分支持/反向/无法验证/样本异常，不要直接改规则。
```
