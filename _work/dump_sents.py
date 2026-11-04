# -*- coding: utf-8 -*-
import json

p = r"D:\26年美国大学生数学建模竞赛\_work\bil\items.json"
items = json.load(open(p, encoding="utf-8"))
out = []
for i, it in enumerate(items):
    if it["kind"] == "img":
        out.append("%d\t[IMG]" % i)
        continue
    if it["kind"] in ("heading", "caption"):
        out.append("%d\t[%s] %s" % (i, it["kind"], it["text"]))
        continue
    for j, s in enumerate(it["sents"]):
        out.append("%d.%d\t%s" % (i, j, s))
open(r"D:\26年美国大学生数学建模竞赛\_work\bil\ensents.txt", "w", encoding="utf-8").write("\n".join(out))
print("lines", len(out))
