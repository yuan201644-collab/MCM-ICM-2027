# -*- coding: utf-8 -*-
"""抽取 2209466.pdf 的指定页，输出结构化 items.json（段落=句子列表 + 图片），供对照版组装。"""
import io
import json
import os
import re
import statistics
import pymupdf

PDF = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"
OUTDIR = r"D:\26年美国大学生数学建模竞赛\_work\bil"
PAGES = [0, 2, 3, 4, 5]          # 1,3,4,5,6 页（跳过目录页）
os.makedirs(OUTDIR, exist_ok=True)

HDR = re.compile(r"^\s*Team\s*#?\s*\d+\s*,?\s*Page\s+\d+\s+of\s+25\s*$")
CAPTION = re.compile(r"^\s*(Figure|Fig\.|Table)\s*\d+", re.I)
BULLET = re.compile(r"^[\u25cb\u25cf\u2022\u25aa\uf06c\uf0b7]\s*")
ABBR = re.compile(r"(?:Fig|Figs|Tab|Eq|Eqs|No|vs|etc|al|i\.e|e\.g|Dr|Mr|Ms)\.$", re.I)
AFTER_FRAME = (
    "w:widowControl", "w:numPr", "w:suppressLineNumbers", "w:pBdr", "w:shd", "w:tabs",
    "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct", "w:topLinePunct",
    "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd", "w:snapToGrid",
    "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap",
    "w:jc", "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
    "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange",
)


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

for pno in PAGES:
    page = doc[pno]
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
    # 行带（公式/表格细线），与 exact3 相同思路
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
                   "page": pno + 1, "size": round(size, 1), "runs": [], "_last": None}
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
        prev = l

for it in items:
    if it["kind"] in ("para", "heading", "caption"):
        full = "".join(r[0] for r in it["runs"])
        it["text"] = full
        it["sents"] = split_sents(full)
        del it["runs"]
        it.pop("_last", None)

for idx, it in enumerate(items):
    if it.get("text", "").startswith("Table 1"):
        items = items[:idx]
        break

with open(os.path.join(OUTDIR, "items.json"), "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=1)

n_sent = sum(len(i.get("sents", [])) for i in items)
print("items", len(items), "sentences", n_sent)
for i in items:
    if i["kind"] == "img":
        print("IMG", i["page"], i["w"], i["h"])
