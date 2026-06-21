#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import argparse, json, uuid
CASEBOOK=Path("memory/casebook.jsonl")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="case json file")
    args=ap.parse_args()
    data=json.loads(Path(args.file).read_text(encoding="utf-8"))
    data.setdefault("case_id", "LY-"+uuid.uuid4().hex[:10])
    data.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
    data.setdefault("privacy_level", "private")
    CASEBOOK.parent.mkdir(parents=True, exist_ok=True)
    with CASEBOOK.open("a",encoding="utf-8") as f:
        f.write(json.dumps(data,ensure_ascii=False)+"\n")
    print(f"Added case: {data['case_id']}")
if __name__ == "__main__": main()
