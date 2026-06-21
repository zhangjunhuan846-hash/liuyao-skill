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
    "六亲","父母","兄弟","子孙","妻财","官鬼","六神","青龙","朱雀","勾陈","螣蛇","白虎","玄武",
    "婚姻","求财","考试","官司","疾病","行人","失物","工作","合作","应期"
]

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

def score(ch, query, terms):
    text=ch.get("text",""); s=0
    if query and query in text: s+=20
    for t in terms:
        c=text.count(t)
        if c: s += c*5
    roles=" ".join(ch.get("roles",[]))
    for t in terms:
        if t in roles: s += 3
    # core books slight boost
    if ch.get("quality")=="A_or_B_core": s += 2
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--book", default="")
    ap.add_argument("--top-k", type=int, default=8)
    args=ap.parse_args()
    terms=extract_terms(args.query); chunks=load_chunks(); scored=[]
    for ch in chunks:
        if args.book and args.book not in ch.get("title",""): continue
        s=score(ch,args.query,terms)
        if s>0: scored.append((s,ch))
    scored.sort(key=lambda x:x[0], reverse=True)
    print(f"Query: {args.query}")
    print(f"Terms: {terms}")
    print(f"Book filter: {args.book or 'ALL'}")
    print(f"Matches: {len(scored)}")
    print("="*80)
    for rank,(s,ch) in enumerate(scored[:args.top_k],1):
        text=ch["text"].replace("\n"," ")
        if len(text)>500: text=text[:500]+"..."
        print(f"[{rank}] score={s}")
        print(f"book={ch['title']} chunk={ch['chunk_id']} quality={ch.get('quality')} roles={','.join(ch.get('roles',[]))}")
        print(text)
        print("-"*80)
if __name__ == "__main__": main()
