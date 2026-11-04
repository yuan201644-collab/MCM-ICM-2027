# -*- coding: utf-8 -*-
"""重新抽取后 item 下标发生位移，把旧 zh_full.json 按文本重新映射到新下标。"""
import json
import re
import sys

W = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022B_2200084_水资源与水电共享\work"
MARK = re.compile(r"[\^_]\{([^}]*)\}")


def norm(t):
    t = MARK.sub(r"\1", t or "")
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


old = json.load(open(W + r"\items_full.bak.json", encoding="utf-8"))
new = json.load(open(W + r"\items_full.json", encoding="utf-8"))
zh = json.load(open(W + r"\zh_full.json", encoding="utf-8"))

bucket = {}
for i, it in enumerate(old):
    bucket.setdefault((it["kind"], norm(it.get("text", ""))), []).append(i)

zh_new, matched, missed = {}, 0, []
for i, it in enumerate(new):
    k = (it["kind"], norm(it.get("text", "")))
    cands = bucket.get(k)
    if not cands:
        missed.append(i)
        for j, s2 in enumerate(it.get("sents", []) or [""]):
            zh_new["%d.%d" % (i, j)] = s2
        continue
    oi = cands.pop(0)
    ocount = len(old[oi].get("sents", []))
    parts = [zh.get("%d.%d" % (oi, j), "") for j in range(ocount)]
    joined = "".join(parts)
    n = max(1, len(it.get("sents", [])))
    for j in range(n):
        zh_new["%d.%d" % (i, j)] = parts[j] if j < ocount else (joined if j == 0 else "")
    matched += 1

json.dump(zh_new, open(W + r"\zh_full.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("items new=%d matched=%d missed=%d keys=%d" % (len(new), matched, len(missed), len(zh_new)))
if missed[:10]:
    for i in missed[:10]:
        print("  miss", i, new[i]["kind"], repr(new[i].get("text", "")[:60]))
