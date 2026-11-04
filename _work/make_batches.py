# -*- coding: utf-8 -*-
"""把 items_full.json 按页切成 8 个翻译批次，写 batchN.json。"""
import json
import os

BIL = r"D:\26年美国大学生数学建模竞赛\_work\bil"
items = json.load(open(os.path.join(BIL, "items_full.json"), encoding="utf-8"))

RANGES = [(1, 3), (4, 6), (7, 9), (10, 12), (13, 15), (16, 18), (19, 21), (22, 23)]


def key(idx, it, j=None):
    if it["kind"] == "para":
        return "%d.%d" % (idx, j)
    return str(idx)


for n, (lo, hi) in enumerate(RANGES, 1):
    rows = []
    for idx, it in enumerate(items):
        if it["kind"] == "img" or it.get("nozh"):
            continue
        if not (lo <= it["page"] <= hi):
            continue
        if it["kind"] == "para":
            for j, s in enumerate(it["sents"]):
                rows.append({"id": key(idx, it, j), "kind": "para", "en": s})
        else:
            rows.append({"id": key(idx, it), "kind": it["kind"], "en": it["text"]})
    out = os.path.join(BIL, "batch%d.json" % n)
    json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("batch%d pages %d-%d entries %d words %d" % (n, lo, hi, len(rows), sum(len(r["en"].split()) for r in rows)))
