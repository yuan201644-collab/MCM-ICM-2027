# -*- coding: utf-8 -*-
"""补裁「位图公式」：有些论文把公式存成小位图，文字层只剩右缘的 (N) 编号。

extract.py / make_eqs.py 只处理文字层公式和矢量图形，这类位图公式会整条漏掉，
成品里就只剩一个孤零零的 "(1)"。本脚本按「编号行 + 同一水平带的图片块」定位，
整条裁成 PNG 写进 eq_map.json。

用法: MCM_CFG=<paper.json> python fill_bitmap_eqs.py [--dry]
"""
import json
import os
import re
import sys

import pymupdf

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
WD = CFG["workdir"]
doc = pymupdf.open(CFG["pdf"])
DRY = "--dry" in sys.argv

NUM_ONLY = re.compile(r"^\s*\((\d{1,3})\)\s*$")
NUM_TAIL = re.compile(r"\(\s*(\d{1,3})\s*\)\s*$")
HDR = re.compile(r"^(Team\s*#?\s*\d+|Page\s+\d+(\s+of\s+\d+)?)$", re.I)

OUT = os.path.join(WD, "eq_imgs")
os.makedirs(OUT, exist_ok=True)
EQ_P = os.path.join(WD, "eq_map.json")
eq = json.load(open(EQ_P, encoding="utf-8")) if os.path.exists(EQ_P) else {}
items = json.load(open(os.path.join(WD, "items_full.json"), encoding="utf-8"))

covered = set()
for f in ("eq_map.json", "alg_map.json", "table_map.json", "fig_map.json"):
    p = os.path.join(WD, f)
    if not os.path.exists(p):
        continue
    for k, v in json.load(open(p, encoding="utf-8")).items():
        for e in (v if isinstance(v, list) else [v]):
            if isinstance(e, dict):
                covered.update(e.get("skip", []))
        if isinstance(v, dict) and "skip" in v:
            covered.add(int(k))


def page_lines(pno):
    page = doc[pno - 1]
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            t = re.sub(r"\s+", " ", "".join(s["text"] for s in l["spans"])).strip()
            if not t or HDR.match(t):
                continue
            out.append((l["bbox"], t))
    return out


def page_img_boxes(pno):
    page = doc[pno - 1]
    out = []
    for im in page.get_images(full=True):
        for r in page.get_image_rects(im[0]):
            # 跳过公众号二维码等装饰位图
            if im[2] in (297, 316) and im[3] in (150, 159):
                continue
            if r.width < 40 or r.height < 8:
                continue
            out.append(r)
    return out


made = []
for pno in [x + 1 for x in CFG["pages"]]:
    if pno - 1 >= doc.page_count:
        continue
    page = doc[pno - 1]
    W = page.rect.width
    boxes = page_img_boxes(pno)
    for bbox, t in page_lines(pno):
        m = NUM_ONLY.match(t) or NUM_TAIL.match(t)
        if not m or bbox[2] < W - 130:
            continue
        y0, y1 = bbox[1], bbox[3]
        # 编号所在条目的下标
        idxs = [i for i, it in enumerate(items)
                if it.get("page") == pno and it.get("y0") is not None
                and it["y0"] < y1 + 4 and it["y1"] > y0 - 4
                and NUM_ONLY.match((it.get("text") or "").strip())]
        if not idxs:
            continue
        idx = idxs[0]
        if idx in covered:
            continue
        # 与编号同一水平带（或上下略浮动）的位图
        near = [r for r in boxes
                if r.y0 < y1 + 14 and r.y1 > y0 - 30
                and r.x0 > 55 and r.x1 < W - 6]
        if not near:
            continue
        top = min([y0] + [r.y0 for r in near]) - 3
        bot = max([y1] + [r.y1 for r in near]) + 3
        if bot - top > 120:          # 太高的多半是整页插图，不是公式
            continue
        clip = pymupdf.Rect(60, top, W - 8, bot)
        name = "eq_p%02d_%s.png" % (pno, m.group(1))
        path = os.path.abspath(os.path.join(OUT, name))
        if not DRY:
            page.get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=clip).save(path)
            eq[str(idx)] = {"img": path, "w": round(clip.width, 1),
                            "h": round(clip.height, 1), "skip": [idx], "page": pno}
        made.append((pno, m.group(1), idx, round(bot - top, 1)))
        covered.add(idx)

if not DRY:
    json.dump(eq, open(EQ_P, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(("DRY " if DRY else "") + "补裁 %d 条: %s" % (len(made), made))
