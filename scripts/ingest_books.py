#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a lightweight keyword index for Liuyao books and school-specific knowledge files.

Default sources:
- resources/books_corrected/*.txt, *.md
- resources/books_raw_md/*.txt, *.md
- knowledge/**/*.txt, *.md

Dependency-free for Codex/Claude local sandboxes.
"""
from pathlib import Path
import argparse, json, re
from datetime import datetime

DEFAULT_BOOK_DIRS = [
    Path("resources/books_corrected"),
    Path("resources/books_raw_md"),
    Path("knowledge/00_basic_terms"),
    Path("knowledge/01_core_classics"),
    Path("knowledge/02_auxiliary_systems"),
    Path("knowledge/03_modern_cases"),
    Path("knowledge/04_conflict_registry"),
]
INDEX_DIR = Path("resources/index")
INDEX_FILE = INDEX_DIR / "book_chunks.jsonl"
STATS_FILE = INDEX_DIR / "book_stats.json"
CHUNK_SIZE = 900
OVERLAP = 120

ROLE_MAP = {
    "火珠林": ["纳甲源流", "古法", "基础规则", "六亲", "世应"],
    "黄金策": ["分类占断", "断语", "占事专题", "用神"],
    "增删卜易": ["用神", "旺衰", "动爻", "应期", "案例"],
    "卜筮正宗": ["纳甲", "六亲", "世应", "用神", "分类占断"],
    "易隐": ["断法体系", "象意", "分类占断"],
    "断易天机": ["案例", "应期", "取象"],
    "易林补遗": ["分类占断", "取象"],
    "飞伏": ["飞伏神", "伏神", "飞神"],
    "六神": ["六神", "象意"],
    "南山真人": ["现代案例", "象意展开", "反馈案例"],
    "冲突": ["流派冲突", "并列判断"],
}

CORE_NAMES = ["火珠林", "黄金策", "增删卜易", "卜筮正宗"]
MODERN_MARKERS = ["南山", "现代案例", "论坛", "卦例", "案例派"]
MISC_MARKERS = ["秘籍", "合集", "未校", "杂项", "misc", "untrusted"]

def parse_frontmatter(text: str):
    meta = {}
    if text.startswith("---\n") or text.startswith("---\r\n"):
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
        if m:
            block = m.group(1)
            for line in block.splitlines():
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                v = v.strip().strip('"\'')
                if v.lower() == "true": v = True
                elif v.lower() == "false": v = False
                meta[k.strip()] = v
            text = text[m.end():]
    return meta, text

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

def detect_roles(filename: str, meta: dict):
    roles=[]
    if meta.get("roles"):
        roles.extend([x.strip() for x in str(meta["roles"]).strip("[]").split(",") if x.strip()])
    for k,v in ROLE_MAP.items():
        if k in filename:
            roles.extend(v)
    return list(dict.fromkeys(roles or ["六爻文献"]))

def detect_meta(path: Path, explicit: dict):
    name = path.name
    meta = dict(explicit)
    if not meta.get("title"):
        meta["title"] = path.stem
    if not meta.get("school"):
        if "南山" in name:
            meta["school"] = "现代案例派"
        elif "飞伏" in name:
            meta["school"] = "飞伏神取法"
        elif "六神" in name:
            meta["school"] = "六神象意派"
        elif any(x in name for x in CORE_NAMES):
            meta["school"] = "传统纳甲六爻主体系"
        elif "conflict_registry" in path.as_posix() or "冲突" in name:
            meta["school"] = "冲突登记层"
        else:
            meta["school"] = "未标注"
    if not meta.get("source_type"):
        p = path.as_posix()
        if "knowledge/01_core_classics" in p or any(x in name for x in CORE_NAMES):
            meta["source_type"] = "core_classic"
        elif "knowledge/02_auxiliary_systems" in p:
            meta["source_type"] = "auxiliary_system"
        elif "knowledge/03_modern_cases" in p or any(x in name for x in MODERN_MARKERS):
            meta["source_type"] = "modern_case"
        elif "knowledge/04_conflict_registry" in p or "冲突" in name:
            meta["source_type"] = "conflict_registry"
        elif any(x in name for x in MISC_MARKERS):
            meta["source_type"] = "misc_untrusted"
        else:
            meta["source_type"] = "book_text"
    if not meta.get("authority_level"):
        st = meta.get("source_type")
        if st == "core_classic": meta["authority_level"] = "A"
        elif st in ("auxiliary_system", "conflict_registry", "book_text"): meta["authority_level"] = "B"
        elif st == "modern_case": meta["authority_level"] = "C"
        else: meta["authority_level"] = "D"
    if "retrieval_default" not in meta:
        meta["retrieval_default"] = meta.get("source_type") not in ("modern_case", "misc_untrusted")
    if not meta.get("use_mode"):
        st = meta.get("source_type")
        meta["use_mode"] = {
            "core_classic": "rule_source",
            "auxiliary_system": "auxiliary_rule",
            "conflict_registry": "conflict_reference",
            "modern_case": "example_only",
            "misc_untrusted": "manual_reference_only",
        }.get(st, "reference")
    return meta

def collect_files(book_dirs):
    files=[]; seen=set()
    for d in book_dirs:
        if not d.exists(): continue
        for pat in ("*.txt","*.md"):
            for p in sorted(d.rglob(pat)):
                if p.name.upper()=="README.MD": continue
                key=p.resolve()
                if key not in seen:
                    files.append(p); seen.add(key)
    return files

def quality_for(meta: dict, path: Path):
    level = str(meta.get("authority_level", "")).upper()
    if level == "A": return "A_core"
    if level == "B": return "B_auxiliary"
    if level == "C": return "C_modern_case"
    if level == "D": return "D_misc_untrusted"
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
        print("Put books in resources/books_raw_md/, resources/books_corrected/, or knowledge/..., then rerun.")
        return
    stats={"created_at": datetime.now().isoformat(timespec="seconds"), "book_dirs":[d.as_posix() for d in dirs], "books":[]}
    total=0
    with INDEX_FILE.open("w", encoding="utf-8") as f:
        for p in files:
            raw=p.read_text(encoding="utf-8", errors="ignore")
            front, body = parse_frontmatter(raw)
            meta = detect_meta(p, front)
            txt=normalize_text(body)
            chunks=chunk_text(txt,args.chunk_size,args.overlap)
            bid=p.stem; roles=detect_roles(p.name, meta)
            q = quality_for(meta, p)
            for i,(s,e,ch) in enumerate(chunks,1):
                rec={
                    "book_id":bid,
                    "title":meta.get("title") or p.stem,
                    "source_file":p.as_posix(),
                    "chunk_id":f"{bid}_{i:05d}",
                    "chunk_index":i,
                    "char_start":s,
                    "char_end":e,
                    "quality":q,
                    "roles":roles,
                    "school":meta.get("school"),
                    "source_type":meta.get("source_type"),
                    "authority_level":meta.get("authority_level"),
                    "retrieval_default":meta.get("retrieval_default"),
                    "use_mode":meta.get("use_mode"),
                    "text":ch,
                }
                f.write(json.dumps(rec,ensure_ascii=False)+"\n")
            total += len(chunks)
            stats["books"].append({
                "book_id":bid,
                "title":meta.get("title") or p.stem,
                "source_file":p.as_posix(),
                "chars":len(txt),
                "chunks":len(chunks),
                "roles":roles,
                "quality":q,
                "school":meta.get("school"),
                "source_type":meta.get("source_type"),
                "authority_level":meta.get("authority_level"),
                "retrieval_default":meta.get("retrieval_default"),
                "use_mode":meta.get("use_mode"),
            })
    stats["total_books"]=len(files); stats["total_chunks"]=total
    STATS_FILE.write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Indexed books/files: {len(files)}")
    print(f"Total chunks: {total}")
    print(f"Index saved to: {INDEX_FILE}")

if __name__ == "__main__": main()
