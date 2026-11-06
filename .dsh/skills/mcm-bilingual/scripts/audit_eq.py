# -*- coding: utf-8 -*-
"""按"公式编号"体检：原文里每个 (N) 是否被裁成了公式图，还是留在正文里成了碎片。

用法: python audit_eq.py <论文目录> [<论文目录> ...]
"""
import json
import os
import re
import sys

import pymupdf

NUM_ONLY = re.compile(r"^\s*\((\d{1,3})\)\s*$")
NUM_TAIL = re.compile(r"\(\s*(\d{1,3})\s*\)\s*$")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def audit(root):
    cfg_p = os.path.join(root, "paper.json")
    if not os.path.exists(cfg_p):
        print("== %s : 无 paper.json，跳过" % os.path.basename(root))
        return None
    cfg = load(cfg_p)
    wd = cfg["workdir"]
    items_p = os.path.join(wd, "items_full.json")
    if not os.path.exists(items_p):
        print("== %s : 无 items_full.json，跳过" % os.path.basename(root))
        return None
    items = load(items_p)
    doc = pymupdf.open(cfg["pdf"])
    eq_by_page = {}
    for f in ("eq_map.json", "alg_map.json"):
        p = os.path.join(wd, f)
        if not os.path.exists(p):
            continue
        for v in load(p).values():
            for e in (v if isinstance(v, list) else [v]):
                pg = e.get("page") or (int(os.path.basename(e.get("img") or e.get("path") or "x_p00").split("_")[1][1:]) if "_p" in os.path.basename(e.get("img") or e.get("path") or "") else None)
                if pg:
                    eq_by_page[pg] = eq_by_page.get(pg, 0) + 1

    pages = [p + 1 for p in cfg["pages"]]
    found = leaked = 0
    per_page_missing = {}
    for pno in pages:
        if pno - 1 >= doc.page_count:
            continue
        page = doc[pno - 1]
        nums = []
        for b in page.get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                t = "".join(s["text"] for s in l["spans"]).strip()
                m = NUM_ONLY.match(t) or NUM_TAIL.match(t)
                if not m:
                    continue
                # 只要右缘靠近版心右界的编号（正文里 "(3)" 这种引用不算）
                if l["bbox"][2] < page.rect.width - 130:
                    continue
                nums.append((int(m.group(1)), l["bbox"][1], l["bbox"][3]))
        if not nums:
            continue
        found += len(nums)
        for n, y0, y1 in nums:
            hit = [it for it in items
                   if it.get("page") == pno and it.get("y0") is not None
                   and it["y0"] < y1 + 4 and it["y1"] > y0 - 4
                   and ("(%d)" % n) in (it.get("text") or "")]
            if hit:
                leaked += 1
                per_page_missing.setdefault(pno, []).append(n)
    name = os.path.basename(root)
    print("== %s  编号 %d 个，编号留在正文里 %d 个" % (name[:34], found, leaked))
    for pg in sorted(per_page_missing):
        print("    p%-2d %s" % (pg, sorted(per_page_missing[pg])[:14]))
    return found, leaked, per_page_missing


if __name__ == "__main__":
    for r in sys.argv[1:]:
        audit(r)
