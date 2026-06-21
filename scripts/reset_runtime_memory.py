#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import argparse, shutil
MEMORY=Path("memory")
BACKUPS=Path("memory_backups")
TARGETS=[MEMORY/"casebook.jsonl", MEMORY/"feedback_log.jsonl"]
INCOMING=MEMORY/"incoming_cases"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backup", action="store_true")
    args=ap.parse_args()
    incoming_files=list(INCOMING.glob("*.json")) if INCOMING.exists() else []
    print("Targets:")
    for p in TARGETS+incoming_files:
        print(f"- {p} exists={p.exists()} size={p.stat().st_size if p.exists() else 0}")
    if args.dry_run: return
    if args.backup:
        ts=datetime.now().strftime("%Y%m%d_%H%M%S")
        b=BACKUPS/ts; b.mkdir(parents=True,exist_ok=True)
        for p in TARGETS:
            if p.exists(): shutil.copy2(p,b/p.name)
        if incoming_files:
            (b/"incoming_cases").mkdir(exist_ok=True)
            for p in incoming_files: shutil.copy2(p,b/"incoming_cases"/p.name)
        print(f"Backup saved to: {b}")
    MEMORY.mkdir(exist_ok=True); INCOMING.mkdir(parents=True,exist_ok=True)
    for p in TARGETS: p.write_text("",encoding="utf-8")
    for p in incoming_files: p.unlink()
    print("Runtime memory cleared.")
if __name__ == "__main__": main()
