# -*- coding: utf-8 -*-
"""按表题锚定，把每张表整块裁成一张图；跨页的表上下拼接，不切片。

表题可能在表的上方（多数）或下方（本文件中 Table 1/2/3 都在表下），两种都支持。
"""
import json, os, re
import pymupdf
from PIL import Image

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
BASE = CFG["workdir"]
SRC = CFG["pdf"]

items = json.load(open(os.path.join(BASE, "items_full.json"), encoding="utf-8"))
doc = pymupdf.open(SRC)
out = {}

L, R = 58, 548
M = 3.0
MAXW = 26          # 单元格段落的最大词数
GAPMAX = 26        # 相邻单元格的最大纵向间距


def render(page_no, y0, y1):
    clip = pymupdf.Rect(L, y0, R, y1)
    pix = doc[page_no - 1].get_pixmap(clip=clip, matrix=pymupdf.Matrix(M, M))
    return pix, clip


def is_cell(t):
    t = (t or "").strip()
    return bool(t) and len(t.split()) < MAXW and not t.endswith(".")


def collect_down(i):
    page = items[i]["page"]
    y = items[i]["y1"]
    got = []
    j = i + 1
    while j < len(items):
        n = items[j]
        if n.get("page") != page or n.get("kind") != "para":
            break
        if (n.get("y0") or 0) - y > GAPMAX:
            break
        if not (n.get("text") or "").strip():
            j += 1
            continue
        if not is_cell(n.get("text")):
            break
        got.append(j)
        y = n["y1"]
        j += 1
        if len(got) > 150:
            break
    return got


def collect_up(i):
    page = items[i]["page"]
    y = items[i]["y0"]
    got = []
    j = i - 1
    while j >= 0:
        n = items[j]
        if n.get("page") != page or n.get("kind") != "para":
            break
        if y - (n.get("y1") or 0) > GAPMAX:
            break
        if not (n.get("text") or "").strip():
            j -= 1
            continue
        if not is_cell(n.get("text")):
            break
        got.append(j)
        y = n["y0"]
        j -= 1
        if len(got) > 150:
            break
    return got


for i, it in enumerate(items):
    if it.get("kind") != "caption":
        continue
    text = (it.get("text") or "").strip()
    if not re.match(r"^Table\s*\d", text, re.I):
        continue
    page = it["page"]

    down = collect_down(i)
    up = collect_up(i)
    cells, segs = [], []
    if len(down) >= len(up):
        cells = down
        if cells:
            v, _ = render(page, it["y1"] + 2, items[cells[-1]]["y1"] + 4)
            segs = [(page, it["y1"] + 2, items[cells[-1]]["y1"] + 4)]
    else:
        cells = sorted(up)
        top = None
        for k in range(i - 1, -1, -1):
            prev = items[k]
            if prev.get("page") != page:
                break
            if prev.get("kind") in ("heading", "caption") and it["y0"] - (prev.get("y1") or 0) < 300:
                top = (prev.get("y1") or 0) + 4
                break
        if top is None:
            top = max(40.0, it["y0"] - 240)
        # 若裁切区顶部是引导句（长句且以句号结尾），把顶边压到该句之后
        for k in range(i - 1, -1, -1):
            prev = items[k]
            if prev.get("page") != page:
                break
            if (prev.get("y1") or 0) <= top:
                break
            t = (prev.get("text") or "").strip()
            if len(t.split()) >= 12 and t.endswith("."):
                top = max(top, prev["y1"] + 4)
        segs = [(page, top, it["y0"] - 2)]
    if not cells:
        continue
    for pg, y0, y1 in segs:
        for k, kk in enumerate(items):
            if (kk.get("page") == pg and kk.get("kind") == "para"
                    and (kk.get("y0") or 0) >= y0 - 2 and (kk.get("y1") or 0) <= y1 + 2):
                if k not in cells:
                    cells.append(k)

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
                   "skip": cells, "page": page, "pages": [s[0] for s in segs]}
    print("p%-3s %-40s cells=%-3d dir=%s h=%.0f" %
          (page, text[:40], len(cells), "down" if cells is down else "up", total_h))

json.dump(out, open(os.path.join(BASE, "table_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("tables", len(out))
