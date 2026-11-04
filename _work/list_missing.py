# -*- coding: utf-8 -*-
import json, os

BASE = r"D:\26年美国大学生数学建模竞赛\_work\bil"
items = json.load(open(os.path.join(BASE, "items_full.json"), encoding="utf-8"))
zh = json.load(open(os.path.join(BASE, "zh_full.json"), encoding="utf-8"))
miss = [i for i in range(len(items))
        if items[i]["kind"] in ("para", "heading", "caption") and not items[i].get("nozh")
        and str(i) not in zh]
print("missing count", len(miss))
for i in miss:
    print(i, items[i]["page"], repr(items[i]["text"][:110]))
