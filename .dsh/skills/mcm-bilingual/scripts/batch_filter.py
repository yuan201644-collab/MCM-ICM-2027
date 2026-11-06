# -*- coding: utf-8 -*-
"""把“不会渲染”的条目（表格单元格、图内标签、公式编号等 skip 项）从批次里剔除，
并为它们预写等值译文 p0.json —— merge.py 仍能通过完整性校验，翻译 agent 只处理真正文。

用法： python batch_filter.py
"""
import glob
import json
import os
import re

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
BIL = CFG["workdir"]

items = json.load(open(os.path.join(BIL, "items_full.json"), encoding="utf-8"))


def load(name):
    p = os.path.join(BIL, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


skip = set()
for name in ("table_map.json", "fig_map.json", "eq_map.json", "alg_map.json"):
    for _k, v in load(name).items():
        if isinstance(v, dict):
            skip.update(int(x) for x in v.get("skip", []))
        elif isinstance(v, list):
            for e in v:
                skip.update(int(x) for x in e.get("skip", []))
skip = {i for i in skip if 0 <= i < len(items)}
print("skip items", len(skip))

prefill = {}
removed = 0
for path in sorted(glob.glob(os.path.join(BIL, "batch[0-9]*.json"))):
    rows = json.load(open(path, encoding="utf-8"))
    keep = []
    for r in rows:
        idx = int(str(r["id"]).split(".")[0])
        if idx in skip:
            prefill[str(r["id"])] = r["en"]
            removed += 1
        else:
            keep.append(r)
    json.dump(keep, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(os.path.basename(path), "keep", len(keep), "drop", len(rows) - len(keep))

json.dump(prefill, open(os.path.join(BIL, "p0.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("prefilled", len(prefill), "removed", removed)
