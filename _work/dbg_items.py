# -*- coding: utf-8 -*-
import json, os

BASE = r"D:\26年美国大学生数学建模竞赛\_work\bil"
items = json.load(open(os.path.join(BASE, "items_full.json"), encoding="utf-8"))
zh = json.load(open(os.path.join(BASE, "zh_full.json"), encoding="utf-8"))
print("zh keys:", len(zh), "sample:", list(zh)[:5])
for j in range(41, 95):
    it = items[j]
    k = str(j)
    print(j, "p%s" % it.get("page"), it.get("kind"), "zh" if k in zh else "--",
          repr(it.get("text", "")[:60]))
