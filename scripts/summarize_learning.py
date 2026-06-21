#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
import json, collections
FEEDBACK=Path("memory/feedback_log.jsonl")

def main():
    if not FEEDBACK.exists():
        print("No feedback log."); return
    rows=[]
    with FEEDBACK.open("r",encoding="utf-8") as f:
        for line in f:
            if line.strip(): rows.append(json.loads(line))
    c=collections.Counter(r.get("outcome","unknown") for r in rows)
    print(f"Feedback records: {len(rows)}")
    for k,v in c.items(): print(f"- {k}: {v}")
    print("\nReminder: Do not auto-promote feedback to rules. Review repeated patterns manually before editing memory/rule_bank.yaml.")
if __name__ == "__main__": main()
