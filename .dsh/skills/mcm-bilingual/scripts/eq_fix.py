# -*- coding: utf-8 -*-
"""重裁公式：在原 make_eqs 的行带基础上，把同一竖带内的矢量图形（分式横线、根号、括号）一并纳入。

make_eqs.py 只按“文字行”取带，遇到上下分式、根式、大括号时会把分子/分母切掉。
本脚本在行带基础上迭代吸收 x0>=145、宽<400 的矢量 drawing，再按同一 y 带重裁。

输出 work/eq_map.json（结构与 make_eqs 一致，供 build.py 使用）。
"""
import json
import os
import re

import pymupdf

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
WORK = CFG["workdir"]
OUT = os.path.join(WORK, "eq_imgs")
os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(CFG["pdf"])
items = json.load(open(os.path.join(WORK, "items_full.json"), encoding="utf-8"))
EQNUM = re.compile(r"^\((\d+)\)$")

eq_map = {}
for pno in CFG["pages"]:
    if pno >= doc.page_count:
        continue
    page = doc[pno]
    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            t = "".join(s["text"] for s in l["spans"]).strip()
            if t:
                lines.append({"t": t, "x0": l["bbox"][0], "y0": l["bbox"][1],
                              "x1": l["bbox"][2], "y1": l["bbox"][3]})
    draws = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.x1 - r.x0 < 1 and r.y1 - r.y0 < 1:
            continue
        if r.x0 < 145 or r.x1 > page.rect.width - 20 or (r.x1 - r.x0) > 400:
            continue
        draws.append({"x0": r.x0, "y0": r.y0, "x1": r.x1, "y1": r.y1, "t": "\x00draw"})

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
        for _ in range(6):
            y0 = min(x["y0"] for x in band) - 15
            y1 = max(x["y1"] for x in band) + 15
            add = [d for d in draws if d not in band and d["y0"] < y1 and d["y1"] > y0]
            if not add:
                break
            band.extend(add)
        by0 = min(x["y0"] for x in band) - 4
        by1 = max(x["y1"] for x in band) + 3
        merged = False
        for b in bands:
            if by0 < b["y1"] + 4 and by1 > b["y0"] - 4:
                b["y0"] = min(b["y0"], by0)
                b["y1"] = max(b["y1"], by1)
                b["nums"].append(a["t"])
                merged = True
                break
        if not merged:
            bands.append({"y0": by0, "y1": by1, "nums": [a["t"]]})

    for bi, b in enumerate(bands):
        y0, y1 = b["y0"], b["y1"]
        if y1 - y0 < 10:
            continue
        clip = pymupdf.Rect(60, y0 - 1.2, page.rect.width - 8, y1 + 1.2)
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
        print("p%-2d %-14s band y=%.0f-%.0f items=%d" % (pno + 1, ",".join(b["nums"]), y0, y1, len(idxs)))

json.dump(eq_map, open(os.path.join(WORK, "eq_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
print("equations", len(eq_map))
