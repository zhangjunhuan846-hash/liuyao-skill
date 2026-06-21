#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal Liuyao chart recorder.

This script does NOT replace a professional Najia engine. It records six lines,
marks moving lines, and derives primary/changed yin-yang patterns for downstream
analysis. Use external charting software for verified 世应、六亲、六神、旬空.
"""
import argparse, json
from datetime import datetime

LINE_MAP = {
    6: {"name":"老阴","symbol":"-- x --","yin_yang":"yin","moving":True,"changed":"yang"},
    7: {"name":"少阳","symbol":"─────","yin_yang":"yang","moving":False,"changed":"yang"},
    8: {"name":"少阴","symbol":"--   --","yin_yang":"yin","moving":False,"changed":"yin"},
    9: {"name":"老阳","symbol":"── o ──","yin_yang":"yang","moving":True,"changed":"yin"},
}
# Bits are recorded bottom-to-top. For example, 离 is yang-yin-yang => (1,0,1).
TRIGRAMS = {
    (1,1,1): "乾", (1,1,0): "兑", (1,0,1): "离", (1,0,0): "震",
    (0,1,1): "巽", (0,1,0): "坎", (0,0,1): "艮", (0,0,0): "坤",
}
# keys are lower trigram + upper trigram. Values are common palace-style names; included for convenience.
HEXAGRAM_BY_TRIGRAM = {
    ("乾","乾"):"乾为天", ("坤","坤"):"坤为地", ("震","坎"):"水雷屯", ("坎","艮"):"山水蒙",
    ("乾","坎"):"水天需", ("坎","乾"):"天水讼", ("坎","坤"):"地水师", ("坤","坎"):"水地比",
    ("乾","巽"):"风天小畜", ("兑","乾"):"天泽履", ("乾","坤"):"地天泰", ("坤","乾"):"天地否",
    ("离","乾"):"天火同人", ("乾","离"):"火天大有", ("艮","坤"):"地山谦", ("坤","震"):"雷地豫",
    ("震","兑"):"泽雷随", ("巽","艮"):"山风蛊", ("兑","坤"):"地泽临", ("坤","巽"):"风地观",
    ("震","离"):"火雷噬嗑", ("离","艮"):"山火贲", ("坤","艮"):"山地剥", ("震","坤"):"地雷复",
    ("震","乾"):"天雷无妄", ("乾","艮"):"山天大畜", ("震","艮"):"山雷颐", ("巽","兑"):"泽风大过",
    ("坎","坎"):"坎为水", ("离","离"):"离为火", ("艮","兑"):"泽山咸", ("巽","震"):"雷风恒",
    ("艮","乾"):"天山遯", ("乾","震"):"雷天大壮", ("坤","离"):"火地晋", ("离","坤"):"地火明夷",
    ("离","巽"):"风火家人", ("兑","离"):"火泽睽", ("艮","坎"):"水山蹇", ("坎","震"):"雷水解",
    ("兑","艮"):"山泽损", ("震","巽"):"风雷益", ("乾","兑"):"泽天夬", ("巽","乾"):"天风姤",
    ("坤","兑"):"泽地萃", ("巽","坤"):"地风升", ("坎","兑"):"泽水困", ("巽","坎"):"水风井",
    ("离","兑"):"泽火革", ("巽","离"):"火风鼎", ("震","震"):"震为雷", ("艮","艮"):"艮为山",
    ("艮","巽"):"风山渐", ("兑","震"):"雷泽归妹", ("离","震"):"雷火丰", ("艮","离"):"火山旅",
    ("巽","巽"):"巽为风", ("兑","兑"):"兑为泽", ("坎","巽"):"风水涣", ("兑","坎"):"水泽节",
    ("兑","巽"):"风泽中孚", ("艮","震"):"雷山小过", ("离","坎"):"水火既济", ("坎","离"):"火水未济",
}

def trigram(bits):
    return TRIGRAMS.get(tuple(bits), "未知")

def hexagram_name(bits):
    lower=trigram(bits[:3]); upper=trigram(bits[3:])
    return HEXAGRAM_BY_TRIGRAM.get((lower,upper), f"{upper}上{lower}下")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--lines", required=True, help="六爻数字，自初爻至上爻，如 7,8,9,7,8,6。6老阴、7少阳、8少阴、9老阳。")
    ap.add_argument("--question", default="")
    ap.add_argument("--date-ganzhi", default="")
    ap.add_argument("--month-branch", default="")
    ap.add_argument("--out", default="")
    args=ap.parse_args()
    vals=[int(x.strip()) for x in args.lines.split(',') if x.strip()]
    if len(vals)!=6 or any(v not in LINE_MAP for v in vals):
        raise SystemExit("--lines must contain exactly six values among 6,7,8,9, bottom-to-top.")
    primary_bits=[1 if LINE_MAP[v]["yin_yang"]=="yang" else 0 for v in vals]
    changed_bits=[1 if LINE_MAP[v]["changed"]=="yang" else 0 for v in vals]
    rec={
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "question": args.question,
        "date_ganzhi": args.date_ganzhi,
        "month_branch": args.month_branch,
        "line_order": "bottom_to_top",
        "lines": [{"position":i+1,"value":v,**LINE_MAP[v]} for i,v in enumerate(vals)],
        "moving_lines": [i+1 for i,v in enumerate(vals) if LINE_MAP[v]["moving"]],
        "primary_pattern": primary_bits,
        "changed_pattern": changed_bits,
        "primary_hexagram": hexagram_name(primary_bits),
        "changed_hexagram": hexagram_name(changed_bits),
        "warning": "This is a minimal recorder, not a verified full Najia engine. Provide external chart details for 世应、六亲、六神、旬空."
    }
    text=json.dumps(rec,ensure_ascii=False,indent=2)
    if args.out:
        with open(args.out,'w',encoding='utf-8') as f: f.write(text)
        print(f"Saved: {args.out}")
    else:
        print(text)
if __name__ == "__main__": main()
