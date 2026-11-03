# -*- coding: utf-8 -*-
"""2209466.pdf -> 版式完全一致的 docx：每行文字按 PDF 原始坐标定位（framePr），图形按原位置嵌图。"""
import io
import re
import pymupdf
from docx import Document
from docx.shared import Pt, Emu
from docx.enum.text import WD_LINE_SPACING, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

PDF = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"
OUT = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466_版式还原.docx"

# CT_PPr 中 framePr 之后的元素顺序（用于合法插入）
AFTER_FRAME = (
    "w:widowControl", "w:numPr", "w:suppressLineNumbers", "w:pBdr", "w:shd", "w:tabs",
    "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct", "w:topLinePunct",
    "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd", "w:snapToGrid",
    "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap",
    "w:jc", "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
    "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange",
)


def merge_rects(rects, pad=4):
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


def framed(doc, x, y, w, h):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    f = OxmlElement("w:framePr")
    f.set(qn("w:w"), str(int(round(w * 20))))
    f.set(qn("w:h"), str(int(round(h * 20))))
    f.set(qn("w:hRule"), "exact")
    f.set(qn("w:hAnchor"), "page")
    f.set(qn("w:vAnchor"), "page")
    f.set(qn("w:x"), str(int(round(x * 20))))
    f.set(qn("w:y"), str(int(round(y * 20))))
    f.set(qn("w:wrap"), "none")
    f.set(qn("w:xAlign"), "left")
    pPr.insert_element_before(f, *AFTER_FRAME)
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.left_indent = Pt(0)
    pf.right_indent = Pt(0)
    pf.first_line_indent = Pt(0)
    return p


doc_in = pymupdf.open(PDF)
out = Document()
sec = out.sections[0]
sec.page_width = Pt(doc_in[0].rect.width)
sec.page_height = Pt(doc_in[0].rect.height)
sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Pt(0)
sec.header_distance = sec.footer_distance = Pt(0)

normal = out.styles["Normal"]
normal.font.name = "Times New Roman"
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
normal.font.size = Pt(12)
normal.paragraph_format.space_before = Pt(0)
normal.paragraph_format.space_after = Pt(0)

n_lines = n_imgs = 0
for pno, page in enumerate(doc_in):
    rects = [pymupdf.Rect(b["bbox"]) for b in page.get_text("dict")["blocks"] if b["type"] == 1]
    for d in page.get_drawings():
        r = d["rect"]
        if r.width >= 5 and r.height >= 5:
            rects.append(pymupdf.Rect(r))
    graphics = [g for g in merge_rects(rects) if g.width > 45 and g.height > 22]

    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            if not "".join(s["text"] for s in l["spans"]).strip():
                continue
            inside = any(l["bbox"][0] >= g.x0 - 1 and l["bbox"][2] <= g.x1 + 1
                         and l["bbox"][1] >= g.y0 - 1 and l["bbox"][3] <= g.y1 + 1 for g in graphics)
            if inside:
                continue
            lines.append(l)

    for g in graphics:
        try:
            pix = page.get_pixmap(clip=g, matrix=pymupdf.Matrix(3, 3))
            if pix.width < 20 or pix.height < 12:
                continue
            p = framed(out, g.x0, g.y0, g.width, g.height)
            run = p.add_run()
            run.add_picture(io.BytesIO(pix.tobytes("png")), width=Pt(g.width), height=Pt(g.height))
            n_imgs += 1
        except Exception as e:
            print("img fail", pno + 1, e)

    for l in lines:
        x0, y0, x1, y1 = l["bbox"]
        size = max(s["size"] for s in l["spans"])
        p = framed(out, x0, y0 - 1.0, (x1 - x0) + 3, (y1 - y0) + 2)
        pf = p.paragraph_format
        pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        pf.line_spacing = Pt(round(size * 1.22, 1))
        for span in l["spans"]:
            t = span["text"]
            if not t:
                continue
            r = p.add_run(t)
            font = span["font"].replace(",Bold", "").replace(",Italic", "").replace(",BoldItalic", "")
            r.font.name = font
            r.font.size = Pt(round(span["size"], 1))
            r.bold = ("bold" in span["font"].lower()) or bool(span["flags"] & 16)
            r.italic = bool(span["flags"] & 2)
            if span["flags"] & 1:
                r.font.superscript = True
            elif span["flags"] & 8:
                r.font.subscript = True
        n_lines += 1

    if pno < doc_in.page_count - 1:
        br = out.add_paragraph()
        br.paragraph_format.space_before = Pt(0)
        br.paragraph_format.space_after = Pt(0)
        run = br.add_run()
        run.add_break(WD_BREAK.PAGE)
        run.font.size = Pt(1)

out.save(OUT)
print("saved", OUT, "lines", n_lines, "images", n_imgs, "pages", doc_in.page_count)
