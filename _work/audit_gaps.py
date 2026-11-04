# -*- coding: utf-8 -*-
import json, os, re

BASE = r"D:\26年美国大学生数学建模竞赛\_work\bil"
items = json.load(open(os.path.join(BASE, "items_full.json"), encoding="utf-8"))
zh = json.load(open(os.path.join(BASE, "zh_full.json"), encoding="utf-8"))
eq = json.load(open(os.path.join(BASE, "eq_map.json"), encoding="utf-8"))


def zh_of(i):
    it = items[i]
    n = len(it.get("sents", [])) or 1
    parts = [zh.get("%d.%d" % (i, j), "") for j in range(n)]
    return "".join(parts)


print("item53 zh:", repr(zh.get("53.0", ""))[:60])
print("item44 zh:", repr(zh_of(44))[:60])

bad = []
for i, it in enumerate(items):
    if it["kind"] != "para":
        continue
    en = it.get("text", "")
    if not re.search(r"where,\s*is|,\s?is the|\bare the rider|,\s?is a constant", en):
        continue
    z = zh_of(i)
    gaps = len(re.findall(r"(?<=[\uFF0C\uFF1B\u3001])\u4E3A", z))
    inl = len([e for e in eq.get(str(i), []) if e["inline"]])
    bad.append((i, it["page"], gaps, inl, en[:44]))

print("\npage | gaps | inline-img | text")
for b in bad:
    print("%3d | %2d | %2d | %s" % (b[0], b[2], b[3], b[4]))
print("total", len(bad), "unfilled:", sum(1 for b in bad if b[2] != b[3]))
