#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime
import argparse, json
FEEDBACK=Path("memory/feedback_log.jsonl")
VALID={"support","partial","reverse","unverified","abnormal"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--outcome", required=True, choices=sorted(VALID))
    ap.add_argument("--note", required=True)
    args=ap.parse_args()
    rec={"case_id":args.case_id,"outcome":args.outcome,"note":args.note,"created_at":datetime.now().isoformat(timespec="seconds")}
    FEEDBACK.parent.mkdir(parents=True, exist_ok=True)
    with FEEDBACK.open("a",encoding="utf-8") as f: f.write(json.dumps(rec,ensure_ascii=False)+"\n")
    print(f"Feedback added for {args.case_id}: {args.outcome}")
if __name__ == "__main__": main()
