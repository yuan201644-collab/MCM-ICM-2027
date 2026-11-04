# -*- coding: utf-8 -*-
import json, os
BASE = r"D:\26年美国大学生数学建模竞赛\_work\bil"
m = json.load(open(os.path.join(BASE, "eq_map.json"), encoding="utf-8"))
for k, v in m.items():
    if k.isdigit() and 185 <= int(k) <= 205:
        print(k, [(e["w"], e["h"], e["inline"], os.path.basename(e["path"])) for e in v])
