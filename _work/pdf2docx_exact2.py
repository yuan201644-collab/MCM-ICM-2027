# -*- coding: utf-8 -*-
"""2209466.pdf -> 版式还原 docx v2：文字按原始坐标定位；图与公式（矢量）按原位置渲染成图。"""
import io
import pymupdf
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

PDF = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"
OUT = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466_版式还原.docx"

AFTER_FRAME = (
    "w:widowControl", "w:numPr", "w:suppressLineNumbers", "w:pBdr", "w:shd", "w:tabs",
    "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct", "w:topLinePunct",
    "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd", "w:snapToGrid",
    "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap",
    "w:jc", "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
    "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange",
)


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


def framed(doc, x, y, w, h):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    f = OxmlElement("w:framePr")
    f.set(qn("w:w"), str(max(1, int(round(w * 20)))))
    f.set(qn("w:h"), str(max(1, int(round(h * 20)))))
    f.set(qn("w:hRule"), "exact")
    f.set(qn("w:hAnchor"), "page")
    f.set(qn("w:vAnchor"), "page")
    f.set(qn("w:x"), str(int(round(x * 20))))
    f.set(qn("w:y"), str(int(round(y * 20))))
    f.set(qn("w:wrap"), "none")
    pPr.insert_element_before(f, *AFTER_FRAME)
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.first_line_indent = Pt(0)
    return p


src = pymupdf.open(PDF)
out = Document()
sec = out.sections[0]
sec.page_width = Pt(src[0].rect.width)
sec.page_height = Pt(src[0].rect.height)
sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Pt(0)
sec.header_distance = sec.footer_distance = Pt(0)

n = out.styles["Normal"]
n.font.name = "Times New Roman"
n.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
n.font.size = Pt(12)
n.paragraph_format.space_before = Pt(0)
n.paragraph_format.space_after = Pt(0)

n_line = n_fig = n_eq = 0
for pno, page in enumerate(src):
    imgs = [pymupdf.Rect(b["bbox"]) for b in page.get_text("dict")["blocks"] if b["type"] == 1]
    draws = [pymupdf.Rect(d["rect"]) for d in page.get_drawings()
             if d["rect"].width > 0.4 and d["rect"].height > 0.4]
    bigs = [g for g in merge(imgs + draws, 6) if g.width > 110 and g.height > 55]

    left = [d for d in draws if not any(abs((d & g).get_area() - d.get_area()) < 0.5 for g in bigs)]
    smalls = [c for c in merge(left, 1.5)
              if c.width >= 3 and c.height >= 2 and c.width * c.height < 0.25 * page.rect.width * page.rect.height]

    for g in bigs:
        try:
            pix = page.get_pixmap(clip=g, matrix=pymupdf.Matrix(3, 3))
            if pix.width < 20 or pix.height < 12:
                continue
            p = framed(out, g.x0, g.y0, g.width, g.height)
            p.add_run().add_picture(io.BytesIO(pix.tobytes("png")), width=Pt(g.width), height=Pt(g.height))
            n_fig += 1
        except Exception as e:
            print("fig fail", pno + 1, e)

    for c in smalls:
        try:
            clip = pymupdf.Rect(c.x0 - 0.6, c.y0 - 0.6, c.x1 + 0.6, c.y1 + 0.6)
            pix = page.get_pixmap(clip=clip, matrix=pymupdf.Matrix(4, 4))
            if pix.width < 6 or pix.height < 4:
                continue
            p = framed(out, clip.x0, clip.y0, clip.width, clip.height)
            p.add_run().add_picture(io.BytesIO(pix.tobytes("png")), width=Pt(clip.width), height=Pt(clip.height))
            n_eq += 1
        except Exception as e:
            print("eq fail", pno + 1, e)

    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            if not "".join(s["text"] for s in l["spans"]).strip():
                continue
            x0, y0, x1, y1 = l["bbox"]
            if any(x0 >= g.x0 - 1 and x1 <= g.x1 + 1 and y0 >= g.y0 - 1 and y1 <= g.y1 + 1 for g in bigs):
                continue
            size = max(s["size"] for s in l["spans"])
            p = framed(out, x0, y0 - 1.0, (x1 - x0) + 4, (y1 - y0) + 2)
            pf = p.paragraph_format
            pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            pf.line_spacing = Pt(round(size * 1.2, 1))
            for span in l["spans"]:
                t = span["text"]
                if not t:
                    continue
                r = p.add_run(t)
                r.font.name = span["font"].split(",")[0]
                r.font.size = Pt(round(span["size"], 1))
                r.bold = ("bold" in span["font"].lower()) or bool(span["flags"] & 16)
                r.italic = bool(span["flags"] & 2)
                if span["flags"] & 1:
                    r.font.superscript = True
            n_line += 1

    if pno < src.page_count - 1:
        br = out.add_paragraph()
        br.paragraph_format.space_before = Pt(0)
        br.paragraph_format.space_after = Pt(0)
        run = br.add_run()
        run.add_break(WD_BREAK.PAGE)
        run.font.size = Pt(1)

out.save(OUT)
print("saved lines", n_line, "figs", n_fig, "eqs", n_eq)
