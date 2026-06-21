#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, subprocess, sys, os
if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BOOK_QUERIES = {
    "增删卜易": "{base} 用神 原神 忌神 世爻 应爻 动爻 月建 日辰 应期",
    "卜筮正宗": "{base} 纳甲 六亲 世应 用神 动爻 空亡",
    "易隐": "{base} 象意 世应 用神 六亲 分类占断",
    "黄金策": "{base} 占事 分类 断语 用神 应期",
    "断易天机": "{base} 案例 应期 取象 动爻",
}

def run(book, query, top_k):
    cmd=[sys.executable,"scripts/retrieve_passages.py","--book",book,"--query",query,"--top-k",str(top_k)]
    env=os.environ.copy(); env["PYTHONIOENCODING"]="utf-8"
    print("\n"+"="*100); print(f"BOOK: {book}"); print(f"QUERY: {query}"); print("="*100)
    r=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8",errors="replace",env=env)
    if r.stdout: print(r.stdout,end="")
    if r.stderr: print(r.stderr,end="",file=sys.stderr)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--top-k", type=int, default=5)
    args=ap.parse_args()
    for book,tpl in BOOK_QUERIES.items():
        run(book,tpl.format(base=args.base),args.top_k)
if __name__ == "__main__": main()
