# -*- coding: utf-8 -*-
import json
import sys

p = r"D:\26年美国大学生数学建模竞赛\_work\bil\items.json"
items = json.load(open(p, encoding="utf-8"))
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 200
for i, it in enumerate(items[:limit]):
    if it["kind"] == "img":
        print(i, "IMG", it["page"], it["w"], it["h"])
    else:
        print(i, it["kind"], it["page"], it["size"], "|", it["text"][:110])
