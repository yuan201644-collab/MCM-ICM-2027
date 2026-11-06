# -*- coding: utf-8 -*-
"""把 p1.json … pN.json 合并成 zh_full.json，并做完整性自检。

用法： set MCM_CFG=<paper.json>  &&  python merge.py
"""
import glob
import json
import os
import sys

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
BIL = CFG["workdir"]

items = json.load(open(os.path.join(BIL, "items_full.json"), encoding="utf-8"))
zh = {}
dup = []

for path in sorted(glob.glob(os.path.join(BIL, "p*.json")),
                    key=lambda p: int("".join(c for c in os.path.basename(p)[1:-5] if c.isdigit()) or 0)):
    part = json.load(open(path, encoding="utf-8"))
    for k, v in part.items():
        if k in zh and zh[k] != v:
            dup.append(k)
        zh[k] = v
    print(os.path.basename(path), len(part), "keys")

if dup:
    print("WARN duplicate keys (last wins):", len(dup), dup[:5])

need = []
for idx, it in enumerate(items):
    if it["kind"] == "img" or it.get("nozh"):
        continue
    if it["kind"] == "para":
        for j in range(len(it.get("sents", []))):
            need.append("%d.%d" % (idx, j))
    else:
        need.append(str(idx))

missing = [k for k in need if k not in zh or not str(zh[k]).strip()]
print("expected", len(need), "have", len(zh), "missing", len(missing))
if missing:
    print("MISSING", missing[:20])
    sys.exit(1)

json.dump(zh, open(os.path.join(BIL, "zh_full.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote zh_full.json", len(zh), "keys")
