# -*- coding: utf-8 -*-
"""按表题锚定，把每张表整块裁成一张图；跨页的表上下拼接，不切片。"""
import json, os, re
import pymupdf
from PIL import Image

BASE = r"D:\26年美国大学生数学建模竞赛\_work\bil"
SRC = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"

items = json.load(open(os.path.join(BASE, "items_full.json"), encoding="utf-8"))
doc = pymupdf.open(SRC)
out = {}

L, R = 58, 548
M = 3.0


def render(page_no, y0, y1):
    clip = pymupdf.Rect(L, y0, R, y1)
    pix = doc[page_no - 1].get_pixmap(clip=clip, matrix=pymupdf.Matrix(M, M))
    return pix, clip


for i, it in enumerate(items):
    if it.get("kind") != "caption":
        continue
    text = (it.get("text") or "").strip()
    if not text.startswith("Table"):
        continue
    page = it["page"]
    y = it["y1"]
    idxs = []
    j = i + 1
    while j < len(items):
        nxt = items[j]
        if nxt.get("page") != page or nxt.get("kind") != "para":
            break
        if nxt["y0"] - y > 24:
            break
        t = (nxt.get("text") or "").strip()
        if not t:
            j += 1
            continue
        if len(t.split()) >= 20:
            break
        idxs.append(j)
        y = nxt["y1"]
        j += 1
        if len(idxs) > 150:
            break
    if not idxs:
        continue

    def cap_bottom(last_i, y1, pg, start):
        lim = 800.0
        for it2 in items:
            if it2.get("page") == pg and it2.get("kind") in ("heading", "caption") and it2.get("y0", 0) > start:
                lim = min(lim, it2["y0"])
        return min(y1, lim - 2)

    segs = [(page, items[i]["y1"] + 2, cap_bottom(idxs[-1], items[idxs[-1]]["y1"] + 3, page, items[i]["y1"]))]
    # 跨页续表
    last_page = page
    while items[idxs[-1]]["y1"] > 745:
        p2 = last_page + 1
        if p2 > doc.page_count:
            break
        y2 = None
        end2 = None
        k = idxs[-1] + 1
        while k < len(items):
            nxt = items[k]
            if nxt.get("page") != p2 or nxt.get("kind") != "para":
                break
            t = (nxt.get("text") or "").strip()
            if not t:
                k += 1
                continue
            if y2 is not None and nxt["y0"] - y2 > 16:
                break
            if len(t.split()) >= 20:
                break
            idxs.append(k)
            end2 = nxt["y1"]
            y2 = end2
            k += 1
        if end2 is None:
            break
        segs.append((p2, 66, cap_bottom(idxs[-1], end2 + 3, p2, 0)))
        last_page = p2

    imgs = []
    for pg, y0, y1 in segs:
        pix, clip = render(pg, y0, y1)
        imgs.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))

    W = max(im.width for im in imgs)
    H = sum(im.height for im in imgs) + 10 * (len(imgs) - 1)
    canvas = Image.new("RGB", (W, H), "white")
    yy = 0
    for im in imgs:
        canvas.paste(im, (0, yy))
        yy += im.height + 10
    fn = os.path.join(BASE, "tbl_%02d.png" % i)
    canvas.save(fn)

    total_h = sum(y1 - y0 for _, y0, y1 in segs) + 5 * (len(segs) - 1)
    out[str(i)] = {"img": fn, "w": round(R - L, 1), "h": round(total_h, 1),
                   "skip": idxs, "page": page, "pages": [s[0] for s in segs]}
    print("p%-3s %-44s cells=%-3d segs=%s h=%.0f" % (page, text[:44], len(idxs),
                                                     [s[0] for s in segs], total_h))

json.dump(out, open(os.path.join(BASE, "table_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("tables", len(out))
