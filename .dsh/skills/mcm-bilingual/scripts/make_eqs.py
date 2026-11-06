# -*- coding: utf-8 -*-
"""把"文字 + 矢量符号"混排的公式块整块裁成图片（以右对齐的 (N) 编号为锚点）。

输出 work/eq_map.json: {"<item_idx>": {"img": path, "w": pt, "h": pt, "skip": [idx...]}}
"""
import json
import os
import re

import pymupdf

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
ROOT = os.path.dirname(os.environ["MCM_CFG"])
WORK = os.path.join(ROOT, "work")
OUT = os.path.join(WORK, "eq_imgs")
os.makedirs(OUT, exist_ok=True)

PDF = os.path.join(ROOT, CFG["pdf"])
EQNUM = re.compile(r"^\((\d+)\)$")
PAGES = CFG["pages"]
EN_ONLY = set(CFG.get("en_only_pages", []))

items = json.load(open(os.path.join(WORK, "items_full.json"), encoding="utf-8"))
doc = pymupdf.open(PDF)

eq_map = {}
total = 0
for pno in PAGES:
    if pno in EN_ONLY or pno >= doc.page_count:
        continue
    page = doc[pno]
    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            t = "".join(s["text"] for s in l["spans"]).strip()
            if not t:
                continue
            lines.append({"t": t, "x0": l["bbox"][0], "y0": l["bbox"][1],
                          "x1": l["bbox"][2], "y1": l["bbox"][3]})
    anchors = [l for l in lines if EQNUM.match(l["t"]) and l["x0"] > 400]
    bands = []
    for a in anchors:
        band = [a]
        changed = True
        while changed:
            changed = False
            y0 = min(x["y0"] for x in band)
            y1 = max(x["y1"] for x in band)
            for l in lines:
                if l in band:
                    continue
                if l["y0"] < y1 + 4 and l["y1"] > y0 - 4 and l["x0"] >= 145:
                    if len(l["t"].split()) <= 26 and not (l["t"].endswith(".") and len(l["t"].split()) >= 6):
                        band.append(l)
                        changed = True
        by0 = min(x["y0"] for x in band) - 4
        by1 = max(x["y1"] for x in band) + 3
        bx0 = min(x["x0"] for x in band) - 6
        merged = False
        for b in bands:
            if by0 < b["y1"] + 4 and by1 > b["y0"] - 4:
                b["y0"] = min(b["y0"], by0)
                b["y1"] = max(b["y1"], by1)
                b["x0"] = min(b["x0"], bx0)
                b["nums"].append(a["t"])
                merged = True
                break
        if not merged:
            bands.append({"y0": by0, "y1": by1, "x0": bx0, "nums": [a["t"]]})
    for bi, b in enumerate(bands):
        y0, y1, x0 = b["y0"], b["y1"], b["x0"]
        if y1 - y0 < 10:
            continue
        clip = pymupdf.Rect(66, y0 - 1.2, 546, y1 + 1.2)
        name = "eq_p%02d_%02d.png" % (pno + 1, bi + 1)
        path = os.path.join(OUT, name)
        page.get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=clip).save(path)
        idxs = [i for i, it in enumerate(items)
                if it.get("page") == pno + 1 and it.get("y0") is not None
                and it["y0"] < y1 and it["y1"] > y0
                and it["kind"] in ("para", "caption")]
        if not idxs:
            os.remove(path)
            continue
        first = min(idxs)
        eq_map[str(first)] = {"img": path, "w": round(clip.width, 1),
                              "h": round(clip.height, 1), "skip": idxs}
        total += 1
        print("p%-2d %-14s band y=%.0f-%.0f items=%d" % (pno + 1, ",".join(b["nums"]), y0, y1, len(idxs)))

json.dump(eq_map, open(os.path.join(WORK, "eq_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
print("equations", total)
