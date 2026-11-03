# -*- coding: utf-8 -*-
"""2209466.pdf -> 版式还原 docx v3：文字按原始坐标定位；图/公式按"行带"整体渲染成图。"""
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

n_line = n_img = 0
for pno, page in enumerate(src):
    imgs = [pymupdf.Rect(b["bbox"]) for b in page.get_text("dict")["blocks"] if b["type"] == 1]
    draws = [pymupdf.Rect(d["rect"]) for d in page.get_drawings()
             if d["rect"].width > 0.4 and d["rect"].height > 0.4]
    bigs = [g for g in merge(imgs + draws, 6) if g.width > 110 and g.height > 55]

    rest = [d for d in draws if (d.height >= 0.8 or (d.height >= 0.15 and d.width >= 25)) and not any(abs((d & g).get_area() - d.get_area()) < 0.5 for g in bigs)]
    bands = [b for b in rows_of(rest) if b.width >= 4 and b.height >= 0.8 and b.height < 120]
    zones = bigs + [pymupdf.Rect(b.x0 - 1, b.y0 - 2, b.x1 + 1, b.y1 + 2) for b in bands]

    for z in zones:
        try:
            pix = page.get_pixmap(clip=z, matrix=pymupdf.Matrix(3.2, 3.2))
            if pix.width < 8 or pix.height < 5:
                continue
            p = framed(out, z.x0, z.y0, z.width, z.height)
            p.add_run().add_picture(io.BytesIO(pix.tobytes("png")), width=Pt(z.width), height=Pt(z.height))
            n_img += 1
        except Exception as e:
            print("img fail", pno + 1, e)

    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            if not "".join(s["text"] for s in l["spans"]).strip():
                continue
            lb = pymupdf.Rect(l["bbox"])
            if any(abs((lb & z).get_area()) > 0.4 * lb.get_area() for z in zones):
                continue
            size = max(s["size"] for s in l["spans"])
            p = framed(out, lb.x0, lb.y0 - 1.0, lb.width + 4, lb.height + 2)
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
print("saved lines", n_line, "images", n_img)
