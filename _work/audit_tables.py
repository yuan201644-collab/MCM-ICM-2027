# -*- coding: utf-8 -*-
import json, os

BASE = r"D:\26年美国大学生数学建模竞赛\_work\bil"
items = json.load(open(os.path.join(BASE, "items_full.json"), encoding="utf-8"))
eq = json.load(open(os.path.join(BASE, "eq_map.json"), encoding="utf-8"))

for i, it in enumerate(items):
    if it["kind"] != "caption":
        continue
    t = it.get("text", "")
    if not t.startswith("Table"):
        continue
    nxt = [items[j].get("text", "") for j in range(i + 1, min(i + 5, len(items)))]
    has_eq = sum(1 for j in range(i + 1, min(i + 12, len(items))) if str(j) in eq)
    print("p%-3s %-52s eq_imgs=%d" % (it["page"], t[:52], has_eq))
    for n in nxt:
        print("      ", n[:78])
