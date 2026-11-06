# -*- coding: utf-8 -*-
"""补裁"正文排版型"公式：有些论文的公式用正文字体排（不是矢量图形），
extract.py 的 drawing 检测抓不到，结果被拆成一堆文字碎片（还会串成
`(10) f_{g}_{(}_{i}_{+1)} = ...` 这种）。

做法：在 PDF 上按行扫描，以右缘的公式编号 (N) 为锚点，把编号所在的
"连续数学行"整组裁成图片，并把落在带内的条目加进 skip。

用法: MCM_CFG=<paper.json> python repair_eqs.py [--dry]
"""
import json
import os
import re
import sys

import pymupdf

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
WD = CFG["workdir"]
OUT = os.path.join(WD, "eq_repair")
os.makedirs(OUT, exist_ok=True)
DRY = "--dry" in sys.argv
UNNUM = "--unnum" in sys.argv

NUM_ONLY = re.compile(r"^\((\d{1,2})\)$")
NUM_TAIL = re.compile(r"\((\d{1,2})\)\s*$")
MATHY = re.compile(r"[=<>≤≥≈∑∏∫±×÷−·√∕/]")
HDR = re.compile(r"^(Team\s*#?\s*\d+|Page\s+\d+\s+of\s+\d+)$", re.I)

items = json.load(open(os.path.join(WD, "items_full.json"), encoding="utf-8"))
doc = pymupdf.open(CFG["pdf"])

eqp = os.path.join(WD, "eq_map.json")
eq = json.load(open(eqp, encoding="utf-8")) if os.path.exists(eqp) else {}
algp = os.path.join(WD, "alg_map.json")
alg = json.load(open(algp, encoding="utf-8")) if os.path.exists(algp) else {}

covered = set()
for src in (eq, alg):
    for k, v in src.items():
        vs = v if isinstance(v, list) else [v]
        for e in vs:
            covered.update(e.get("skip", []))
        if isinstance(v, dict) and "skip" in v:
            covered.add(int(k))

by_page = {}
for i, it in enumerate(items):
    if it.get("page") and it.get("y0") is not None:
        by_page.setdefault(it["page"], []).append(i)


def lines_of(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            t = re.sub(r"\s+", " ", "".join(s["text"] for s in l["spans"])).strip()
            if not t or HDR.match(t):
                continue
            out.append({"t": t, "x0": l["bbox"][0], "x1": l["bbox"][2],
                        "y0": l["bbox"][1], "y1": l["bbox"][3]})
    out.sort(key=lambda z: (z["y0"], z["x0"]))
    return out


def is_math(l, width):
    t = l["t"]
    if NUM_ONLY.match(t):
        return True
    if t.endswith((",", ";", ":")):
        return False                      # "where," 这种句子片段
    if len(t.split()) >= 12:
        return False
    return bool(MATHY.search(t)) or len(t.split()) <= 6


made = []
for pno in [p + 1 for p in CFG["pages"]]:
    if pno - 1 >= doc.page_count:
        continue
    page = doc[pno - 1]
    width = page.rect.width
    L = lines_of(page)
    used_line = set()
    for pos, l in enumerate(L):
        if pos in used_line:
            continue
        m = NUM_ONLY.match(l["t"]) or NUM_TAIL.match(l["t"])
        if not m:
            if not UNNUM:
                continue
            # 无编号的展示公式：含等号/不等号、很短、且缩进（不在左边距）
            if not re.search(r"[=≤≥≈]", l["t"]):
                continue
            if len(l["t"].split()) > 9 or l["x0"] < 84:
                continue
            if re.search(r"[a-z]{4,}\s+[a-z]{4,}\s+[a-z]{4,}", l["t"]):
                continue
            m = None
        t = l["t"]
        # 有编号时必须靠右缘；无编号的展示公式不受此限
        if m is not None:
            if not (NUM_ONLY.match(t) or l["x1"] > width * 0.85):
                continue
            if NUM_ONLY.match(t) and l["x1"] < width * 0.8:
                continue
        # 收集连续数学行
        grp = [pos]
        k = pos - 1
        while k >= 0 and k not in used_line:
            if L[grp[0]]["y0"] - L[k]["y1"] > 14:
                break
            if not is_math(L[k], width):
                break
            grp.insert(0, k)
            k -= 1
        k = pos + 1
        while k < len(L) and k not in used_line:
            if L[k]["y0"] - L[grp[-1]]["y1"] > 10:
                break
            if not is_math(L[k], width) or NUM_ONLY.match(L[k]["t"]) and False:
                break
            if NUM_ONLY.match(L[k]["t"]) or NUM_TAIL.match(L[k]["t"]):
                break          # 下一个编号属于另一组
            grp.append(k)
            k += 1
        band = (min(L[g]["y0"] for g in grp) - 3, max(L[g]["y1"] for g in grp) + 4)
        idxs = [i for i in by_page.get(pno, [])
                if items[i]["y0"] < band[1] and items[i]["y1"] > band[0]]
        if not idxs:
            used_line.update(grp)
            continue
        if any(i in covered for i in idxs):
            used_line.update(grp)
            continue
        clip = pymupdf.Rect(60, band[0], width - 8, band[1])
        n = int(m.group(1)) if m is not None else 0
        name = "fix_p%02d_%02d.png" % (pno, n)
        path = os.path.join(OUT, name)
        if not DRY:
            page.get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=clip).save(path)
            eq[str(min(idxs))] = {"img": path, "w": round(clip.width, 1),
                                  "h": round(clip.height, 1), "skip": idxs, "page": pno}
        used_line.update(grp)
        made.append((pno, n, len(idxs), round(band[1] - band[0])))

if not DRY:
    json.dump(eq, open(eqp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("repaired", len(made))
for x in made[:50]:
    print("   p%-2d (%d) items=%d h=%d" % x)
