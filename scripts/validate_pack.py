#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
liuyao_validate_pack.py
建议放置：scripts/validate_pack.py

用途：检查六爻 skill 是否存在以下问题：
1. resources/index/book_chunks.jsonl 中是否仍有大量“未标注”。
2. fresh 模式是否在 SKILL.md 中明确禁止读取 memory。
3. 现代案例/杂项资料是否被默认检索。
4. knowledge/resources 下的 md 是否缺少 YAML frontmatter。
5. 同一标题是否重复过多，提示做去重。

运行：
    python scripts/validate_pack.py

可选：
    python scripts/validate_pack.py --root . --fail-on-warning
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ALLOWED_SOURCE_TYPES = {
    "core_classic",
    "auxiliary_system",
    "conflict_registry",
    "book_text",
    "modern_case",
    "misc_untrusted",
    "raw_ocr_reference",
}

BLOCKED_BY_DEFAULT = {"modern_case", "misc_untrusted"}
REQUIRED_META_KEYS = {"title", "school", "source_type", "authority_level", "retrieval_default", "use_mode"}
CORE_SKILL_PHRASES = [
    "fresh 模式不得读取",
    "memory/casebook.jsonl",
    "memory/feedback_log.jsonl",
    "本次为 fresh 模式，未调用历史案例",
]


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip().strip('"\'')
        if v.lower() == "true":
            v = True
        elif v.lower() == "false":
            v = False
        meta[k.strip()] = v
    return meta


def warn(msg: str, warnings: list[str]) -> None:
    warnings.append(msg)
    print(f"[WARN] {msg}")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)
    print(f"[ERROR] {msg}")


def check_skill_md(root: Path, errors: list[str], warnings: list[str]) -> None:
    skill = root / "SKILL.md"
    if not skill.exists():
        fail("缺少 SKILL.md", errors)
        return
    text = skill.read_text(encoding="utf-8", errors="ignore")
    missing = [p for p in CORE_SKILL_PHRASES if p not in text]
    if missing:
        fail("SKILL.md 中 fresh 模式硬隔离语句不完整：" + "；".join(missing), errors)
    else:
        ok("SKILL.md 已包含 fresh 模式记忆隔离核心语句")


def check_index(root: Path, errors: list[str], warnings: list[str]) -> None:
    index = root / "resources" / "index" / "book_chunks.jsonl"
    if not index.exists():
        warn("未找到 resources/index/book_chunks.jsonl；如果尚未 ingest，可忽略", warnings)
        return

    total = 0
    source_types = Counter()
    authority = Counter()
    schools = Counter()
    titles = Counter()
    default_blocked = []
    unknown_source = []

    with index.open("r", encoding="utf-8", errors="ignore") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                fail(f"book_chunks.jsonl 第 {line_no} 行不是合法 JSON", errors)
                continue
            total += 1
            st = rec.get("source_type")
            al = rec.get("authority_level")
            sc = rec.get("school") or "未标注"
            title = normalize_title(rec.get("title") or rec.get("book_id") or "unknown")
            source_types[st] += 1
            authority[al] += 1
            schools[sc] += 1
            titles[title] += 1

            if st not in ALLOWED_SOURCE_TYPES:
                unknown_source.append((line_no, st, title))
            if st in BLOCKED_BY_DEFAULT and rec.get("retrieval_default") is True:
                default_blocked.append((line_no, st, title))

    if total == 0:
        fail("book_chunks.jsonl 为空", errors)
        return

    ok(f"索引存在，共 {total} 个 chunk")
    print("[INFO] source_type 分布：", dict(source_types))
    print("[INFO] authority_level 分布：", dict(authority))
    print("[INFO] school 前 10：", schools.most_common(10))

    unmarked_ratio = schools.get("未标注", 0) / max(total, 1)
    if unmarked_ratio > 0.20:
        warn(f"未标注 school 比例过高：{unmarked_ratio:.1%}。建议补 book_manifest 或 frontmatter", warnings)
    else:
        ok(f"未标注 school 比例可接受：{unmarked_ratio:.1%}")

    if unknown_source:
        sample = unknown_source[:5]
        fail(f"存在未知 source_type，示例：{sample}", errors)

    if default_blocked:
        sample = default_blocked[:5]
        fail(f"现代案例/杂项资料被默认检索，示例：{sample}", errors)
    else:
        ok("modern_case / misc_untrusted 未被默认检索")

    repeated = [(t, c) for t, c in titles.most_common(20) if c > 100]
    if repeated:
        warn("部分标题 chunk 数过高，可能存在同书重复 OCR 或未按卷去重：" + str(repeated[:10]), warnings)


def normalize_title(title: str) -> str:
    title = re.sub(r"^MinerU_markdown_", "", title)
    title = re.sub(r"\.pdf.*$", "", title)
    title = re.sub(r"_[0-9a-f]{8,}.*$", "", title, flags=re.I)
    title = title.replace("#U", "U")
    return title.strip()


def check_frontmatter(root: Path, errors: list[str], warnings: list[str]) -> None:
    paths = []
    for base in [root / "knowledge", root / "resources" / "books_corrected"]:
        if base.exists():
            paths.extend(base.rglob("*.md"))
    paths = [p for p in paths if p.name.upper() != "README.MD"]
    if not paths:
        warn("未找到需要检查 frontmatter 的 md 文件", warnings)
        return

    missing_all = []
    missing_keys = defaultdict(list)
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="ignore")
        meta = parse_frontmatter(text)
        if not meta:
            missing_all.append(p)
            continue
        for k in REQUIRED_META_KEYS:
            if k not in meta:
                missing_keys[k].append(p)

    if missing_all:
        warn(f"有 {len(missing_all)} 个 md 没有 YAML frontmatter。示例：" + ", ".join(str(p.relative_to(root)) for p in missing_all[:8]), warnings)
    else:
        ok("knowledge/books_corrected 下 md 均有 frontmatter")

    for k, files in missing_keys.items():
        if files:
            warn(f"有 {len(files)} 个 md 缺少 frontmatter 字段 {k}。示例：" + ", ".join(str(p.relative_to(root)) for p in files[:5]), warnings)


def check_memory_defaults(root: Path, errors: list[str], warnings: list[str]) -> None:
    for rel in ["memory/casebook.jsonl", "memory/feedback_log.jsonl"]:
        p = root / rel
        if not p.exists():
            warn(f"缺少 {rel}；如果不做案例学习可忽略", warnings)
            continue
        if p.stat().st_size > 0:
            warn(f"{rel} 非空。fresh 模式必须确保不读取该文件", warnings)
        else:
            ok(f"{rel} 为空")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="skill 根目录")
    ap.add_argument("--fail-on-warning", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    print(f"[INFO] checking root: {root}")

    errors: list[str] = []
    warnings: list[str] = []

    check_skill_md(root, errors, warnings)
    check_index(root, errors, warnings)
    check_frontmatter(root, errors, warnings)
    check_memory_defaults(root, errors, warnings)

    print("\n========== SUMMARY ==========")
    print(f"errors: {len(errors)}")
    print(f"warnings: {len(warnings)}")

    if errors:
        return 2
    if warnings and args.fail_on_warning:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
