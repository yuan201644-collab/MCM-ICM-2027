# -*- coding: utf-8 -*-
import json, os

BASE = r"D:\26年美国大学生数学建模竞赛\_work\bil"
m = json.load(open(os.path.join(BASE, "eq_map.json"), encoding="utf-8"))
items = json.load(open(os.path.join(BASE, "items_full.json"), encoding="utf-8"))

for k in sorted([x for x in m if x.isdigit()], key=lambda x: int(x)):
    it = items[int(k)]
    if it["page"] not in (12, 13):
        continue
    print(k, it["page"], repr(it["text"][:36]))
    for e in m[k]:
        print("    ", os.path.basename(e["path"]), "w=%.1f h=%.1f" % (e["w"], e["h"]),
              "inline" if e["inline"] else "BLOCK")
print("None-key count:", len(m.get("None", [])))
for e in m.get("None", [])[:10]:
    print("   unattached", os.path.basename(e["path"]), e["page"], e["w"], e["h"], e["inline"])
