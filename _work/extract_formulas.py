# -*- coding: utf-8 -*-
"""把 PDF 里的公式（矢量绘制）按行带裁成图片，并定位到 items_full 的条目上。"""
import io
import json
import os
import re

import pymupdf

PDF = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"
BIL = r"D:\26年美国大学生数学建模竞赛\_work\bil"
PAGES = [0] + list(range(2, 23))          # 1-based 1,3..23 -> 0-based
OUT = os.path.join(BIL, "eq_map.json")
IMGDIR = os.path.join(BIL, "eq")
os.makedirs(IMGDIR, exist_ok=True)


def merge(rects, pad):
    groups = []
    for r in rects:
        cur = pymupdf.Rect(r)
        changed = True
        while changed:
            changed = False
            for g in groups:
                if (cur + (-pad, -pad, pad, pad)).intersects(g):
                    cur |= g
                    groups.remove(g)
                    changed = True
                    break
        groups.append(cur)
    return groups


def rows_of(rects):
    rs = sorted(rects, key=lambda r: (r.y0, r.x0))
    rows = []
    for r in rs:
        if rows and r.y0 < rows[-1][1]:
            b = rows[-1][0] | r
            rows[-1] = (b, max(rows[-1][1], r.y1))
        else:
            rows.append((pymupdf.Rect(r), r.y1))
    return [b for b, _ in rows]


def norm(s):
    s = s.replace("\u00a0", " ").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\ufb01", "fi").replace("\ufb02", "fl").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


items = json.load(open(os.path.join(BIL, "items_full.json"), encoding="utf-8"))
by_page = {}
for idx, it in enumerate(items):
    by_page.setdefault(it["page"], []).append(idx)

doc = pymupdf.open(PDF)
mapping = {}
stats = []

for pno in PAGES:
    page = doc[pno]
    pageno = pno + 1
    imgs = [pymupdf.Rect(b["bbox"]) for b in page.get_text("dict")["blocks"] if b["type"] == 1]
    draws = [pymupdf.Rect(d["rect"]) for d in page.get_drawings()
             if d["rect"].width > 0.4 and d["rect"].height > 0.4]
    bigs = [g for g in merge(imgs + draws, 6) if g.width > 110 and g.height > 55]
    rest = [d for d in draws
            if (d.height >= 0.8 or (d.height >= 0.15 and d.width >= 25))
            and not any(abs((d & g).get_area() - d.get_area()) < 0.5 for g in bigs)]
    bands = [b for b in rows_of(rest) if b.width >= 4 and b.height >= 0.8 and b.height < 120]
    # 去掉页眉/页脚横线与整页宽长线
    bands = [b for b in bands if not (b.width > 460 and b.height < 3)]

    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            t = "".join(s["text"] for s in l["spans"])
            if t.strip():
                lines.append((pymupdf.Rect(l["bbox"]).y0, norm(t)))
    lines.sort()

    idxs = by_page.get(pageno, [])
    pos = 0
    item_y = []
    for idx in idxs:
        it = items[idx]
        head = norm(it.get("text", ""))[:22]
        y = None
        for k in range(pos, len(lines)):
            if head and lines[k][1].startswith(head[:18]):
                y = lines[k][0]
                pos = k + 1
                break
        item_y.append((idx, y))

    known = [(i, y) for i, y in item_y if y is not None]
    for k, b in enumerate(bands):
        if b.width < 6 or b.height < 2:
            continue
        target = None
        for i, y in known:
            if y <= b.y0:
                target = i
            else:
                break
        path = os.path.join(IMGDIR, "eq_p%02d_%02d.png" % (pageno, k))
        try:
            pix = page.get_pixmap(clip=b, matrix=pymupdf.Matrix(3.2, 3.2))
            if pix.width < 10 or pix.height < 6:
                continue
            pix.save(path)
        except Exception as e:
            print("render fail", pageno, k, e)
            continue
        entry = {"page": pageno, "path": path, "w": round(b.width, 1), "h": round(b.height, 1),
                 "item": target, "y": round(b.y0, 1)}
        mapping.setdefault(str(target), []).append(entry)
        stats.append(entry)

json.dump(mapping, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("bands", len(stats), "pages", len(PAGES), "unattached", sum(1 for e in stats if e["item"] is None))
for e in stats[:12]:
    print(e["page"], e["item"], e["w"], e["h"])
