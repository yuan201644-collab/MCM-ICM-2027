# -*- coding: utf-8 -*-
"""抽取 2209466.pdf 全文（跳过目录页），输出 items_full.json。"""
import json
import os
import re
import statistics

import pymupdf

PDF = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"
OUTDIR = r"D:\26年美国大学生数学建模竞赛\_work\bil"
PAGES = [0] + list(range(2, 23))   # 1, 3..23 页（跳过目录与参考文献之后）
EN_ONLY_PAGES = [23, 24]           # 参考文献、附录：只保留英文
os.makedirs(OUTDIR, exist_ok=True)

HDR = re.compile(r"^\s*Team\s*#?\s*\d+\s*,?\s*Page\s+\d+\s+of\s+25\s*$")
CAPTION = re.compile(r"^\s*(Figure|Fig\.|Table)\s*\d+", re.I)
BULLET = re.compile(r"^[\u25cb\u25cf\u2022\u25aa\uf06c\uf0b7]\s*")
ABBR = re.compile(r"(?:Fig|Figs|Tab|Eq|Eqs|No|vs|etc|al|i\.e|e\.g|Dr|Mr|Ms)\.$", re.I)


def merge_rects(rects, pad=8):
    groups = []
    for r in rects:
        cur = pymupdf.Rect(r)
        merged = True
        while merged:
            merged = False
            for g in groups:
                if (cur + (-pad, -pad, pad, pad)).intersects(g):
                    cur |= g
                    groups.remove(g)
                    merged = True
                    break
        groups.append(cur)
    return groups


def rows_of(rects):
    rs = sorted(rects, key=lambda r: (r.y0, r.x0))
    rows = []
    for r in rs:
        if rows and r.y0 < rows[-1][1]:
            rows[-1] = (rows[-1][0] | r, max(rows[-1][1], r.y1))
        else:
            rows.append((pymupdf.Rect(r), r.y1))
    return [b for b, _ in rows]


def split_sents(text):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"(])", text)
    out = []
    for p in parts:
        if out and ABBR.search(out[-1]):
            out[-1] = out[-1] + " " + p
        else:
            out.append(p)
    merged = []
    for s in out:
        if merged and len(merged[-1].strip()) < 30:
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    return [p.strip() for p in merged if p.strip()]


doc = pymupdf.open(PDF)
items = []
fign = 0
eqmap = {}
EQDIR = os.path.join(OUTDIR, "eq")
os.makedirs(EQDIR, exist_ok=True)

for pno in PAGES + EN_ONLY_PAGES:
    page = doc[pno]
    first_idx = len(items)
    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt or HDR.match(txt):
                continue
            lines.append(l)
    if pno == 0:
        lines = [l for l in lines if l["bbox"][1] >= 90]
    body = [l for l in lines if l["spans"][0]["size"] < 13.3]
    left = min((l["bbox"][0] for l in body), default=72)
    right = max((l["bbox"][2] for l in body), default=540)
    gaps = []
    for a, b2 in zip(body, body[1:]):
        g = b2["bbox"][1] - a["bbox"][3]
        if 0 <= g < 30:
            gaps.append(g)
    med_gap = statistics.median(gaps) if gaps else 4

    rects = [pymupdf.Rect(b["bbox"]) for b in page.get_text("dict")["blocks"] if b["type"] == 1]
    for d in page.get_drawings():
        r = d["rect"]
        if r.width >= 3 and r.height >= 3:
            rects.append(pymupdf.Rect(r))
    graphics = [g for g in merge_rects(rects) if g.width > 110 and g.height > 55]

    drop = set()
    keep_g = []
    for g in graphics:
        inside = [i for i, l in enumerate(body)
                  if l["bbox"][0] > g.x0 and l["bbox"][2] < g.x1 and l["bbox"][1] > g.y0 and l["bbox"][3] < g.y1]
        if len(inside) > 4:
            continue
        drop.update(inside)
        keep_g.append(g)
    rest = [pymupdf.Rect(d["rect"]) for d in page.get_drawings()
            if (pymupdf.Rect(d["rect"]).height >= 0.8 or
                (pymupdf.Rect(d["rect"]).height >= 0.15 and pymupdf.Rect(d["rect"]).width >= 25))]
    bands = [b for b in rows_of(rest) if b.width >= 4 and b.height >= 0.8 and b.height < 120
             and not any(abs((b & g).get_area() - b.get_area()) < 0.6 for g in keep_g)]

    elems = []
    for i, l in enumerate(lines):
        if i in drop:
            continue
        elems.append((l["bbox"][1], l["bbox"][0], "line", l))
    for g in keep_g:
        elems.append((g.y0, g.x0, "img", g))
    elems.sort(key=lambda t: (t[0], t[1]))

    cur = None
    prev = None
    for y, x, kind, payload in elems:
        if kind == "img":
            cur = None
            prev = None
            g = payload
            pix = page.get_pixmap(clip=g, matrix=pymupdf.Matrix(2.2, 2.2))
            if pix.width < 40 or pix.height < 30:
                continue
            fign += 1
            fn = os.path.join(OUTDIR, "img_%02d_%d.png" % (pno + 1, fign))
            pix.save(fn)
            items.append({"kind": "img", "page": pno + 1, "path": fn,
                          "w": round(g.width, 1), "h": round(g.height, 1)})
            continue

        l = payload
        spans = l["spans"]
        txt = "".join(s["text"] for s in spans).strip()
        size = max(s["size"] for s in spans)
        is_cap = bool(CAPTION.match(txt))
        new_par = cur is None
        if not new_par and prev is not None:
            gap = l["bbox"][1] - prev["bbox"][3]
            short_prev = prev["bbox"][2] < right - 20
            cont = bool(re.match(r"^[a-z,.;:)\]]", txt))
            if gap > max(med_gap * 1.6, 9) or (short_prev and not cont) or BULLET.match(txt):
                new_par = True
        if size >= 13.3:
            new_par = True

        if new_par:
            cur = {"kind": "heading" if size >= 13.3 else ("caption" if is_cap else "para"),
                   "page": pno + 1, "size": round(size, 1), "runs": [], "_last": None,
                   "y0": l["bbox"][1], "y1": l["bbox"][3]}
            items.append(cur)
        t = BULLET.sub("", txt)
        if txt and BULLET.match(txt):
            t = "• " + t
        if not new_par and prev is not None and prev["bbox"][2] >= right - 20:
            if cur and cur["runs"] and cur["runs"][-1][0].endswith("-"):
                cur["runs"][-1][0] = cur["runs"][-1][0][:-1]
            elif cur and cur["runs"]:
                cur["runs"].append([" ", False, False, 12.0])
            else:
                t = " " + t
        if cur and cur["runs"]:
            p = cur["runs"][-1]
            if p[0].endswith(" ") and t.startswith(" "):
                t = t.lstrip()
        if t:
            bold = ("bold" in spans[0]["font"].lower()) or bool(spans[0]["flags"] & 16)
            cur["runs"].append([re.sub(r"[ \t]{2,}", " ", t), bold, bool(spans[0]["flags"] & 2), round(spans[0]["size"], 1)])
        cur["_last"] = l["bbox"][3]
        cur["y1"] = l["bbox"][3]
        prev = l

    page_items = [(i, items[i]) for i in range(first_idx, len(items))
                  if items[i].get("y0") is not None]
    textlines = [pymupdf.Rect(l["bbox"]) for l in lines]

    def text_overlap(r):
        best = 0.0
        for tl in textlines:
            inter = r & tl
            if inter.is_empty:
                continue
            a = inter.get_area() / max(r.get_area(), 0.01)
            best = max(best, a)
        return best

    blocks = [b for b in bands if b.width >= 60 and text_overlap(b) < 0.45]

    line_spans = []
    for l in lines:
        sp = [pymupdf.Rect(s["bbox"]) for s in l["spans"] if s["text"].strip()]
        line_spans.append((pymupdf.Rect(l["bbox"]), sp))

    def in_text_gap(r):
        cy = (r.y0 + r.y1) / 2.0
        for lbox, spans in line_spans:
            if lbox.y0 - 1.5 <= cy <= lbox.y1 + 1.5:
                ov = 0.0
                for sp in spans:
                    inter = pymupdf.Rect(r.x0, sp.y0, r.x1, sp.y1) & sp
                    if not inter.is_empty:
                        ov += inter.get_area()
                return (ov / max(r.get_area(), 0.01)) < 0.15
        return False

    smalls = [pymupdf.Rect(d) for d in rest
              if d.height < 22 and d.width < 40 and in_text_gap(pymupdf.Rect(d))]
    clusters = []
    for r in sorted(smalls, key=lambda q: (round(q.y0, 1), q.x0)):
        cur_r = pymupdf.Rect(r)
        merged = True
        while merged:
            merged = False
            for g in clusters:
                if (cur_r + (-3, -2, 3, 2)).intersects(g):
                    cur_r |= g
                    clusters.remove(g)
                    merged = True
                    break
        clusters.append(cur_r)
    clusters = [c for c in clusters
                if not any((c & b).get_area() > 0.5 * c.get_area() for b in blocks)]

    cands = [(b, False) for b in blocks] + [(c, True) for c in clusters]
    for k, (b, is_inline) in enumerate(cands):
        if b.width < 6 or b.height < 2:
            continue
        target = None
        for i, it2 in page_items:
            if it2["y0"] <= b.y0:
                target = i
        pix = page.get_pixmap(clip=b, matrix=pymupdf.Matrix(3.2, 3.2))
        if pix.width < 10 or pix.height < 6:
            continue
        fn = os.path.join(EQDIR, "eq_p%02d_%02d.png" % (pno + 1, k))
        pix.save(fn)
        eqmap.setdefault(str(target), []).append(
            {"page": pno + 1, "path": fn, "w": round(b.width, 1), "h": round(b.height, 1),
             "inline": bool(is_inline)})

with open(os.path.join(OUTDIR, "eq_map.json"), "w", encoding="utf-8") as f:
    json.dump(eqmap, f, ensure_ascii=False, indent=1)

for it in items:
    if it["kind"] in ("para", "heading", "caption"):
        full = "".join(r[0] for r in it["runs"])
        it["text"] = full
        it["sents"] = split_sents(full)
        it["nwords"] = len(full.split())
        del it["runs"]
        it.pop("_last", None)
    it["nozh"] = it.get("page", 0) in [p + 1 for p in EN_ONLY_PAGES]

with open(os.path.join(OUTDIR, "items_full.json"), "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=1)

n_sent = sum(len(i.get("sents", [])) for i in items)
n_words = sum(i.get("nwords", 0) for i in items)
print("items", len(items), "sentences", n_sent, "words", n_words)
print("imgs", sum(1 for i in items if i["kind"] == "img"))
from collections import Counter
print(Counter(i["kind"] for i in items))
print("words by page", sorted({i["page"]: sum(x.get("nwords", 0) for x in items if x["page"] == i["page"]) for i in items}.items()))
