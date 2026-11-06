# -*- coding: utf-8 -*-
"""按累计词数把待译条目切成 N 批，输出 batchN.json（元素 {id, kind, en}）。

用法： set MCM_CFG=<paper.json>  &&  python batch.py
"""
import json
import os

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
BIL = CFG["workdir"]
N = int(CFG.get("batches", 8))

items = json.load(open(os.path.join(BIL, "items_full.json"), encoding="utf-8"))


def key(idx, it, j=None):
    if it["kind"] == "para":
        return "%d.%d" % (idx, j)
    return str(idx)


rows = []
for idx, it in enumerate(items):
    if it["kind"] == "img" or it.get("nozh"):
        continue
    if it["kind"] == "para":
        for j, s in enumerate(it["sents"]):
            rows.append({"id": key(idx, it, j), "kind": "para", "en": s, "page": it["page"]})
    else:
        rows.append({"id": key(idx, it), "kind": it["kind"], "en": it["text"], "page": it["page"]})

total = sum(len(r["en"].split()) for r in rows)
target = total / N

batches, cur, acc = [], [], 0
for r in rows:
    cur.append(r)
    acc += len(r["en"].split())
    if acc >= target and len(batches) < N - 1:
        batches.append(cur)
        cur, acc = [], 0
if cur:
    batches.append(cur)

for n, b in enumerate(batches, 1):
    out = os.path.join(BIL, "batch%d.json" % n)
    payload = [{"id": r["id"], "kind": r["kind"], "en": r["en"]} for r in b]
    json.dump(payload, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pages = sorted({r["page"] for r in b})
    print("batch%d  entries=%d words=%d pages=%s" %
          (n, len(b), sum(len(r["en"].split()) for r in b), "%d-%d" % (pages[0], pages[-1])))

print("total rows", len(rows), "words", total, "batches", len(batches))
