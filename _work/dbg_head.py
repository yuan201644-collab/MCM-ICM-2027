# -*- coding: utf-8 -*-
import json, re, os
CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
B = CFG["workdir"]
items = json.load(open(os.path.join(B, "items_full.json"), encoding="utf-8"))
zh = json.load(open(os.path.join(B, "zh_full.json"), encoding="utf-8"))
for i, it in enumerate(items):
    t = (it.get("text") or "").strip()
    if it.get("kind") == "heading" and re.match(r"^\d+(\.\d+)*$", t):
        nx = items[i + 1] if i + 1 < len(items) else None
        ok = nx and nx.get("kind") == "heading" and abs((nx.get("y0") or 0) - (it.get("y0") or 0)) < 2
        print(i, repr(t), "next_kind=", nx.get("kind"), "dy=", round((nx.get("y0") or 0) - (it.get("y0") or 0), 2), "merge=", bool(ok),
              "| zh:", repr(zh.get(str(i))), repr(zh.get(str(i + 1))))
