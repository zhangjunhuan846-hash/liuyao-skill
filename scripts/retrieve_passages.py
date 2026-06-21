#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import argparse, json, re, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
INDEX_FILE = Path("resources/index/book_chunks.jsonl")
DEFAULT_TERMS = [
    "用神","原神","忌神","仇神","世爻","应爻","动爻","变爻","伏神","飞神",
    "月建","日辰","旬空","空亡","月破","日破","冲","合","刑","害","墓","绝",
    "六亲","父母","兄弟","子孙","妻财","官鬼","六神","青龙","朱雀","勾陈","螣蛇","腾蛇","白虎","玄武",
    "婚姻","求财","考试","官司","疾病","行人","失物","工作","合作","应期",
    "飞伏","南山真人","现代案例","象意","神煞","纳音","冲突","流派"
]
EXCLUDED_DEFAULT_SOURCE_TYPES = {"modern_case", "misc_untrusted"}

def truthy(v):
    if isinstance(v, bool): return v
    return str(v).strip().lower() in {"true","yes","1","y"}

def load_chunks():
    if not INDEX_FILE.exists():
        raise SystemExit(f"Index not found: {INDEX_FILE}. Run python scripts/ingest_books.py first.")
    out=[]
    with INDEX_FILE.open("r",encoding="utf-8") as f:
        for line in f:
            if line.strip(): out.append(json.loads(line))
    return out

def extract_terms(query):
    terms=[]
    for t in DEFAULT_TERMS:
        if t in query: terms.append(t)
    for item in re.split(r"[\s,，。；;、/]+",query):
        item=item.strip()
        if len(item)>=2 and item not in terms: terms.append(item)
    return terms

def include_chunk(ch, args):
    st = ch.get("source_type") or ""
    if args.source_type and args.source_type != st:
        return False
    if args.school and args.school not in str(ch.get("school", "")):
        return False
    if args.book and args.book not in str(ch.get("title", "")) and args.book not in str(ch.get("source_file", "")):
        return False
    if st == "modern_case" and not args.include_modern_cases:
        return False
    if st == "misc_untrusted" and not args.include_misc:
        return False
    if st in EXCLUDED_DEFAULT_SOURCE_TYPES and not truthy(ch.get("retrieval_default")):
        if st == "modern_case" and args.include_modern_cases:
            return True
        if st == "misc_untrusted" and args.include_misc:
            return True
        return False
    return True

def score(ch, query, terms):
    text=ch.get("text",""); s=0
    if query and query in text: s+=20
    for t in terms:
        c=text.count(t)
        if c: s += c*5
    roles=" ".join(ch.get("roles",[]))
    for t in terms:
        if t in roles: s += 3
        if t in str(ch.get("school", "")): s += 2
        if t in str(ch.get("source_type", "")): s += 2
    q = ch.get("quality")
    if q=="A_core": s += 5
    elif q=="B_auxiliary": s += 2
    elif q=="C_modern_case": s -= 2
    elif q=="D_misc_untrusted": s -= 5
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--book", default="", help="按书名或 source_file 过滤")
    ap.add_argument("--school", default="", help="按流派名称关键词过滤")
    ap.add_argument("--source-type", default="", choices=["", "core_classic", "auxiliary_system", "modern_case", "conflict_registry", "misc_untrusted", "book_text"])
    ap.add_argument("--include-modern-cases", action="store_true", help="显式包含南山真人/论坛卦例等现代案例")
    ap.add_argument("--include-misc", action="store_true", help="显式包含秘籍合集/未校OCR等低权重杂项")
    ap.add_argument("--top-k", type=int, default=8)
    args=ap.parse_args()
    terms=extract_terms(args.query); chunks=load_chunks(); scored=[]
    for ch in chunks:
        if not include_chunk(ch, args):
            continue
        s=score(ch,args.query,terms)
        if s>0: scored.append((s,ch))
    scored.sort(key=lambda x:x[0], reverse=True)
    print(f"Query: {args.query}")
    print(f"Terms: {terms}")
    print(f"Book filter: {args.book or 'ALL'}")
    print(f"School filter: {args.school or 'ALL'}")
    print(f"Source type: {args.source_type or 'ALL DEFAULT'}")
    print(f"Include modern cases: {args.include_modern_cases}")
    print(f"Include misc/untrusted: {args.include_misc}")
    print(f"Matches: {len(scored)}")
    print("="*80)
    for rank,(s,ch) in enumerate(scored[:args.top_k],1):
        text=ch["text"].replace("\n"," ")
        if len(text)>500: text=text[:500]+"..."
        print(f"[{rank}] score={s}")
        print(
            f"book={ch.get('title')} chunk={ch.get('chunk_id')} quality={ch.get('quality')} "
            f"authority={ch.get('authority_level')} source_type={ch.get('source_type')} school={ch.get('school')} use_mode={ch.get('use_mode')}"
        )
        print(f"roles={','.join(ch.get('roles',[]))}")
        print(f"source_file={ch.get('source_file')}")
        print(text)
        print("-"*80)
if __name__ == "__main__": main()
