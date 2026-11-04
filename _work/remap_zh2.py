# -*- coding: utf-8 -*-
"""直接从 p1..p8 重建 zh，按文本映射到新 items 下标。"""
import glob
import json
import os
import re

W = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022B_2200084_水资源与水电共享\work"
MARK = re.compile(r"[\^_]\{([^}]*)\}")


def norm(t):
    t = MARK.sub(r"\1", t or "")
    return re.sub(r"\s+", " ", t).strip().lower()


old = json.load(open(W + r"\items_full.bak.json", encoding="utf-8"))
new = json.load(open(W + r"\items_full.json", encoding="utf-8"))

old_zh = {}
for f in sorted(glob.glob(W + r"\p[0-9]*.json")):
    old_zh.update(json.load(open(f, encoding="utf-8")))
print("p*.json keys:", len(old_zh))

bucket = {}
for i, it in enumerate(old):
    bucket.setdefault((it["kind"], norm(it.get("text", ""))), []).append(i)

zh_new, matched, missed = {}, 0, []
for i, it in enumerate(new):
    k = (it["kind"], norm(it.get("text", "")))
    cands = bucket.get(k)
    if not cands:
        missed.append(i)
        if it["kind"] in ("heading", "caption"):
            zh_new[str(i)] = it.get("text", "")
        else:
            for j, s2 in enumerate(it.get("sents", []) or [""]):
                zh_new["%d.%d" % (i, j)] = s2
        continue
    oi = cands.pop(0)
    if old[oi]["kind"] in ("heading", "caption"):
        parts = [old_zh.get(str(oi), "")]
        ocount = 1
    else:
        ocount = len(old[oi].get("sents", []))
        parts = [old_zh.get("%d.%d" % (oi, j), "") for j in range(ocount)]
    joined = "".join(parts)
    if it["kind"] in ("heading", "caption"):
        zh_new[str(i)] = joined
    else:
        n = max(1, len(it.get("sents", [])))
        for j in range(n):
            zh_new["%d.%d" % (i, j)] = parts[j] if j < ocount else (joined if j == 0 else "")
    matched += 1

json.dump(zh_new, open(W + r"\zh_full.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
tot = empty = 0
for i, it in enumerate(new):
    if it["kind"] not in ("para", "heading", "caption"):
        continue
    tot += 1
    if it["kind"] in ("heading", "caption"):
        s = (zh_new.get(str(i), "") or "").strip()
    else:
        s = "".join(zh_new.get("%d.%d" % (i, j), "") for j in range(len(it.get("sents", [])))).strip()
    if not s:
        empty += 1
print("matched=%d missed=%d empty=%d/%d" % (matched, len(missed), empty, tot))
