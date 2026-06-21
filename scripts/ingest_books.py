#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a lightweight keyword index for Liuyao books.

Default sources:
- resources/books_corrected/*.txt, *.md
- resources/books_raw_md/*.txt, *.md

Dependency-free for Codex/Claude local sandboxes.
"""
from pathlib import Path
import argparse, json, re
from datetime import datetime

DEFAULT_BOOK_DIRS = [Path("resources/books_corrected"), Path("resources/books_raw_md")]
INDEX_DIR = Path("resources/index")
INDEX_FILE = INDEX_DIR / "book_chunks.jsonl"
STATS_FILE = INDEX_DIR / "book_stats.json"
CHUNK_SIZE = 900
OVERLAP = 120

ROLE_MAP = {
    "增删卜易": ["用神", "旺衰", "动爻", "应期", "案例"],
    "卜筮正宗": ["纳甲", "六亲", "世应", "用神", "分类占断"],
    "易隐": ["断法体系", "象意", "分类占断"],
    "黄金策": ["分类占断", "断语", "占事专题"],
    "断易天机": ["案例", "应期", "取象"],
    "火珠林": ["纳甲源流", "古法", "基础规则"],
    "易林补遗": ["分类占断", "取象"],
}

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks=[]; start=0; n=len(text)
    while start<n:
        end=min(start+chunk_size,n); chunk=text[start:end]
        if end<n:
            cut=max([chunk.rfind(x) for x in ("。","\n##","\n#","\n","；","，")])
            if cut>chunk_size*0.55:
                end=start+cut+1; chunk=text[start:end]
        chunk=chunk.strip()
        if chunk: chunks.append((start,end,chunk))
        if end>=n: break
        start=max(0,end-overlap)
    return chunks

def detect_roles(filename: str):
    roles=[]
    for k,v in ROLE_MAP.items():
        if k in filename: roles.extend(v)
    return list(dict.fromkeys(roles or ["六爻文献"]))

def collect_files(book_dirs):
    files=[]; seen=set()
    for d in book_dirs:
        if not d.exists(): continue
        for pat in ("*.txt","*.md"):
            for p in sorted(d.glob(pat)):
                if p.name.upper()=="README.MD": continue
                key=p.resolve()
                if key not in seen:
                    files.append(p); seen.add(key)
    return files

def quality_for(path: Path):
    n=path.name
    if any(x in n for x in ["增删卜易","卜筮正宗","易隐","黄金策"]): return "A_or_B_core"
    if "raw" in path.as_posix(): return "raw_unverified"
    return "unknown"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--book-dir", action="append", default=[])
    ap.add_argument("--chunk-size", type=int, default=CHUNK_SIZE)
    ap.add_argument("--overlap", type=int, default=OVERLAP)
    args=ap.parse_args()
    dirs=DEFAULT_BOOK_DIRS + [Path(x) for x in args.book_dir]
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    files=collect_files(dirs)
    if not files:
        print("No .txt or .md files found.")
        print("Put books in resources/books_raw_md/ or resources/books_corrected/, then rerun.")
        return
    stats={"created_at": datetime.now().isoformat(timespec="seconds"), "book_dirs":[d.as_posix() for d in dirs], "books":[]}
    total=0
    with INDEX_FILE.open("w", encoding="utf-8") as f:
        for p in files:
            txt=normalize_text(p.read_text(encoding="utf-8", errors="ignore"))
            chunks=chunk_text(txt,args.chunk_size,args.overlap)
            bid=p.stem; roles=detect_roles(p.name)
            for i,(s,e,ch) in enumerate(chunks,1):
                rec={"book_id":bid,"title":p.stem,"source_file":p.as_posix(),"chunk_id":f"{bid}_{i:05d}","chunk_index":i,"char_start":s,"char_end":e,"quality":quality_for(p),"roles":roles,"text":ch}
                f.write(json.dumps(rec,ensure_ascii=False)+"\n")
            total += len(chunks)
            stats["books"].append({"book_id":bid,"title":p.stem,"source_file":p.as_posix(),"chars":len(txt),"chunks":len(chunks),"roles":roles,"quality":quality_for(p)})
    stats["total_books"]=len(files); stats["total_chunks"]=total
    STATS_FILE.write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Indexed books: {len(files)}")
    print(f"Total chunks: {total}")
    print(f"Index saved to: {INDEX_FILE}")

if __name__ == "__main__": main()
