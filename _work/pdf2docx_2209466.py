# -*- coding: utf-8 -*-
"""2209466.pdf -> 可编辑 docx（v3）：按行重建段落，保留粗体/斜体/上下标，图形区域渲染为图片。"""
import io
import re
import statistics
import pymupdf
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

PDF = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"
OUT = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466_可编辑.docx"

HDR = re.compile(r"^\s*Team\s*#?\s*\d+\s*,?\s*Page\s+\d+\s+of\s+25\s*$")
CAPTION = re.compile(r"^\s*(Figure|Fig\.|Table)\s*\d+", re.I)
TOC = re.compile(r"\.{4,}\s*\d*\s*$")
BULLET = re.compile(r"^[\u25cb\u25cf\u2022\u25aa\uf06c\uf0b7]\s*")


def merge_rects(rects):
    groups = []
    for r in rects:
        cur = pymupdf.Rect(r)
        merged = True
        while merged:
            merged = False
            for g in groups:
                if (cur + (-8, -8, 8, 8)).intersects(g):
                    cur |= g
                    groups.remove(g)
                    merged = True
                    break
        groups.append(cur)
    return groups


def is_bold(span):
    return ("bold" in span["font"].lower()) or bool(span["flags"] & 16)


doc = pymupdf.open(PDF)
out = Document()
normal = out.styles["Normal"]
normal.font.name = "Times New Roman"
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
normal.font.size = Pt(12)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for lvl, size in ((1, 16), (2, 14), (3, 12)):
    st = out.styles[f"Heading {lvl}"]
    st.font.name = "Times New Roman"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.paragraph_format.space_before = Pt(12)

n_img = n_par = 0

for pno, page in enumerate(doc, 1):
    blocks = page.get_text("dict")["blocks"]
    lines = []
    for b in blocks:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if not txt or HDR.match(txt):
                continue
            lines.append(l)

    # 页 1 抬头的表格：重排成两行
    if pno == 1:
        keep = [l for l in lines if l["bbox"][1] >= 90]
        lines = keep

    if not lines:
        body = []
    else:
        body = [l for l in lines if l["spans"][0]["size"] < 13.3]
    left = min((l["bbox"][0] for l in body), default=72)
    right = max((l["bbox"][2] for l in body), default=540)
    gaps = []
    for a, b2 in zip(body, body[1:]):
        g = b2["bbox"][1] - a["bbox"][3]
        if 0 <= g < 30:
            gaps.append(g)
    med_gap = statistics.median(gaps) if gaps else 4

    rects = [pymupdf.Rect(b["bbox"]) for b in blocks if b["type"] == 1]
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
        if len(inside) > 4:      # 文字很多，多半是表格：保留文字，不渲染成图
            continue
        drop.update(inside)
        keep_g.append(g)

    elems = [(l["bbox"][1], l["bbox"][0], "line", l) for i, l in enumerate(lines) if l not in [body[j] for j in drop]]
    for g in keep_g:
        elems.append((g.y0, g.x0, "img", g))
    elems.sort(key=lambda t: (t[0], t[1]))

    cur = None  # 当前段落 (paragraph, last_line)

    def flush():
        global cur
        cur = None

    prev = None
    for y, x, kind, payload in elems:
        if kind == "img":
            flush()
            g = payload
            try:
                pix = page.get_pixmap(clip=g, matrix=pymupdf.Matrix(2.2, 2.2))
                if pix.width < 40 or pix.height < 30:
                    continue
                out.add_picture(io.BytesIO(pix.tobytes("png")), width=Inches(min(g.width / 72.0, 6.3)))
                out.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                n_img += 1
            except Exception as e:
                print("img fail", pno, e)
            continue

        l = payload
        txt = "".join(s["text"] for s in l["spans"]).strip()
        size = max(s["size"] for s in l["spans"])
        is_cap = bool(CAPTION.match(txt))

        new_par = cur is None
        if not new_par and prev is not None:
            gap = l["bbox"][1] - prev["bbox"][3]
            short_prev = prev["bbox"][2] < right - 20
            cont = bool(re.match(r"^[a-z,.;:)\]]", txt))
            if gap > max(med_gap * 1.6, 9) or (short_prev and not cont) or BULLET.match(txt):
                new_par = True

        if size >= 15.5:
            p = out.add_heading(level=1)
            new_par = True
        elif size >= 13.3:
            p = out.add_heading(level=2)
            new_par = True

        if new_par:
            if size >= 15.5 or size >= 13.3:
                pass
            else:
                p = out.add_paragraph()
            cur = p
        else:
            p = cur

        if txt and BULLET.match(txt):
            txt = BULLET.sub("", txt)
            r0 = p.add_run("• ")
            r0.bold = False
        elif not new_par and prev is not None and prev["bbox"][2] >= right - 20:
            if not (p.runs and p.runs[-1].text.endswith("-")):
                p.add_run(" ")
            else:
                last = p.runs[-1]
                last.text = last.text[:-1]

        for span in l["spans"]:
            t = span["text"]
            if not t.strip():
                continue
            t = re.sub(r"[ \t]{2,}", " ", t)
            run = p.add_run(t)
            run.bold = is_bold(span)
            run.italic = bool(span["flags"] & 2)
            if span["flags"] & 1:
                run.font.superscript = True

        if p.style.name.startswith("Heading") and p.runs:
            p.runs[0].text = re.sub(r"^(\d+(?:\.\d+)*)(?=[A-Za-z])", r"\1 ", p.runs[0].text)

        if is_cap:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = False
                r.font.size = Pt(10.5)
        if TOC.search(txt):
            p.style = out.styles["Normal"]
            for r in p.runs:
                r.bold = False
                r.font.size = Pt(10.5)
        n_par += 1
        prev = l

for p in out.paragraphs:
    for i in range(1, len(p.runs)):
        a, b = p.runs[i - 1], p.runs[i]
        if a.text.endswith(" ") and b.text.startswith(" "):
            b.text = b.text.lstrip()
    if p.runs and re.match(r"^\d+(\.\d+)*[A-Za-z]", p.text):
        p.runs[0].text = re.sub(r"^(\d+(?:\.\d+)*)(?=[A-Za-z])", r"\1 ", p.runs[0].text)

out.save(OUT)
print("saved paragraphs", n_par, "images", n_img)
