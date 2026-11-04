# -*- coding: utf-8 -*-
import json
p = r"D:\26年美国大学生数学建模竞赛\_work\bil\items.json"
items = json.load(open(p, encoding="utf-8"))
print("items", len(items))
for it in items[:6]:
    print(it.get("kind"), {k: (v if not isinstance(v, str) or len(v) < 60 else v[:60] + "...") for k, v in it.items() if k != "sents"})
print("---- first 3 sents ----")
n = 0
for it in items:
    for s in it.get("sents", [])[:2]:
        print(repr(s)[:120])
        n += 1
    if n >= 4:
        break
print("total sents", sum(len(i.get("sents", [])) for i in items))
zh = json.load(open(r"D:\26年美国大学生数学建模竞赛\_work\bil\zh.json", encoding="utf-8"))
print("zh keys", len(zh))
missing = []
for it in items:
    for s in it.get("sents", []):
        if s.get("id") not in zh:
            missing.append((s.get("id"), s.get("en", "")[:50]))
print("missing", len(missing), missing[:5])
