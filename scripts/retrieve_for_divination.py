#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse, subprocess, sys, os
if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BOOK_QUERIES = {
    "火珠林": "{base} 纳甲 六亲 世应 基础规则 动爻 月建 日辰",
    "黄金策": "{base} 占事 分类 断语 用神 应期",
    "增删卜易": "{base} 用神 原神 忌神 世爻 应爻 动爻 月建 日辰 应期",
    "卜筮正宗": "{base} 纳甲 六亲 世应 用神 动爻 空亡",
    "易隐": "{base} 象意 世应 用神 六亲 分类占断",
    "断易天机": "{base} 案例 应期 取象 动爻",
    "冲突表": "{base} 用神冲突 旺衰权重 飞伏神 六神象意 应期冲突 流派并列",
}

def run(book, query, top_k, include_modern_cases=False, include_misc=False):
    cmd=[sys.executable,"scripts/retrieve_passages.py","--query",query,"--top-k",str(top_k)]
    if book != "冲突表":
        cmd.extend(["--book", book])
    else:
        cmd.extend(["--source-type", "conflict_registry"])
    if include_modern_cases:
        cmd.append("--include-modern-cases")
    if include_misc:
        cmd.append("--include-misc")
    env=os.environ.copy(); env["PYTHONIOENCODING"]="utf-8"
    print("\n"+"="*100); print(f"BOOK/SOURCE: {book}"); print(f"QUERY: {query}"); print("="*100)
    r=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8",errors="replace",env=env)
    if r.stdout: print(r.stdout,end="")
    if r.stderr: print(r.stderr,end="",file=sys.stderr)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--include-modern-cases", action="store_true")
    ap.add_argument("--include-misc", action="store_true")
    args=ap.parse_args()
    for book,tpl in BOOK_QUERIES.items():
        run(book,tpl.format(base=args.base),args.top_k,args.include_modern_cases,args.include_misc)
    if args.include_modern_cases:
        run("南山真人", f"{args.base} 南山真人 现代案例 象意 六神 世应", args.top_k, True, args.include_misc)
if __name__ == "__main__": main()
