# -*- coding: utf-8 -*-
"""组装英中对照版：术语表 + 一句英文一句中文。"""
import json
import re
import sys
import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
HEADER = re.compile(r'^(Team\s*#?\s*\d+(\s*,?\s*Page\s+\d+(\s+of\s+\d+)?)?|Page\s+\d+\s+of\s+\d+)$', re.I)
CODE = re.compile(r'^(?:\d+\s+)?(?:while|for|if|else|end|return|repeat|until|Algorithm|Update|Set|Compute|Initialize|Initialization)\b|←')
MATHY = re.compile(r"[=+−<>≤≥∑∫√∞≈±×÷→←]|[\^_]\{")


def _is_num_heading(t):
    """'3.2.1 Total Biomass' 是标题；'1 −p1p2. If player…' 是公式残片，不能排成标题。"""
    if not re.match(r"^\d+(\.\d+)*\.?\s", t):
        return False
    if len(t) >= 90 or sum(c.isalpha() for c in t) < 3:
        return False
    return not MATHY.search(t)


def clean(s):
    return _CTRL.sub("", s) if isinstance(s, str) else s

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
BIL = CFG["workdir"]
OUT = sys.argv[1] if len(sys.argv) > 1 else CFG["out_docx"]

NAVY = RGBColor(0x1F, 0x4E, 0x79)
GLOSS_BLUE = RGBColor(0x2E, 0x74, 0xB5)

TERMS = []

GLOSS = []


GLOSS_EN = [(en, zh) for zh, en in GLOSS]

FIG_TEXTS = {}


def style(run, name, size, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    rf.set(qn("w:ascii"), name)
    rf.set(qn("w:hAnsi"), name)
    rf.set(qn("w:eastAsia"), name if name == "微软雅黑" else "宋体")


def para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=0, spacing=1.12, indent=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = spacing
    if indent:
        pf.left_indent = Cm(indent)
    return p


SUPSUB = re.compile(r"([\^_])\{([^}]*)\}")
PRE_MARK = re.compile(r"[ \t]+([\^_])\{")


def _emit(p, text, size, bold, color, font="Times New Roman"):
    """渲染 ^{..}/_{..} 为上/下标；marker 前的空格一并吃掉（PDF 里是排版缝隙，不是词间距）。"""
    text = PRE_MARK.sub(r"\1{", text)
    pos = 0
    for m in SUPSUB.finditer(text):
        if m.start() > pos:
            style(p.add_run(text[pos:m.start()]), font, size, bold=bold, color=color)
        r = p.add_run(m.group(2))
        style(r, "Times New Roman", size, bold=bold, color=color)
        if m.group(1) == "^":
            r.font.superscript = True
        else:
            r.font.subscript = True
        pos = m.end()
    if pos < len(text):
        style(p.add_run(text[pos:]), font, size, bold=bold, color=color)

def add_en(doc, text, size=12.0, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
           after=0, before=0, indent_first=0, used_en=None):
    text = clean(text)
    p = para(doc, align=align, before=before, after=after)
    if indent_first:
        p.paragraph_format.first_line_indent = Cm(indent_first)
    segs = [(text, False)]
    if used_en is not None:
        for term, _cn in GLOSS_EN:
            if term in used_en:
                continue
            new, hit = [], False
            for seg, is_term in segs:
                if is_term or term not in seg:
                    new.append((seg, is_term))
                    continue
                i = seg.index(term)
                new.append((seg[:i], False))
                new.append((seg[i: i + len(term)], True))
                new.append((seg[i + len(term):], False))
                hit = True
            if hit:
                used_en.add(term)
                segs = new
    for seg, is_term in segs:
        if not seg:
            continue
        _emit(p, seg, size, bold, GLOSS_BLUE if is_term else None)
    return p


def panel_border(p, fill="F3F7FB", line="9CC0DE"):
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "6")
    left.set(qn("w:color"), line)
    pbdr.append(left)
    pPr.insert_element_before(pbdr, "w:shd", "w:tabs", "w:spacing", "w:ind", "w:jc",
                              "w:rPr", "w:sectPr")
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.insert_element_before(shd, "w:tabs", "w:spacing", "w:ind", "w:jc", "w:rPr", "w:sectPr")


def add_zh(doc, text, size=10.5, bold=False, color=NAVY, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
           after=6, before=0, indent=0.45, used_gloss=None, first_line=0, panel=False,
           inlines=None):
    text = clean(text)
    p = para(doc, align=align, before=before, after=after, indent=indent)
    if first_line:
        p.paragraph_format.first_line_indent = Cm(first_line)
    if panel:
        panel_border(p)
    segs = []
    if inlines:
        gaps = [m.start() for m in re.finditer(r"(?<=[\uFF0C\uFF1B\u3001])\u4E3A", text)]
        if len(inlines) != len(gaps):
            inlines = None
    if inlines:
        last = 0
        used = 0
        for gpos in gaps:
            if used >= len(inlines):
                break
            segs.append((text[last:gpos], False))
            segs.append((None, inlines[used]))
            used += 1
            last = gpos
        segs.append((text[last:], False))
        for extra in inlines[used:]:
            segs.append((None, extra))
    else:
        segs.append((text, False))
    if used_gloss is not None:
        for term, en in GLOSS:
            if term in used_gloss:
                continue
            new, hit = [], False
            for seg, is_gloss in segs:
                if is_gloss or seg is None or term not in seg:
                    new.append((seg, is_gloss))
                    continue
                i = seg.index(term)
                new.append((seg[: i + len(term)], False))
                new.append(("（%s）" % en, True))
                new.append((seg[i + len(term):], False))
                hit = True
            if hit:
                used_gloss.add(term)
                segs = new
    for seg, is_gloss in segs:
        if seg is None:
            e = is_gloss
            h = max(7.0, min(float(e.get("h", 10)) * 0.95, 15.0))
            p.add_run().add_picture(e["path"], height=Pt(h))
            continue
        if not seg:
            continue
        if is_gloss:
            style(p.add_run(seg), "Times New Roman", size - 1.5, color=GLOSS_BLUE)
        else:
            _emit(p, seg, size, bold, color, font="微软雅黑")
    return p


def add_fig_legend(doc, pairs):
    p = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, before=6, after=2)
    p.paragraph_format.keep_with_next = True
    style(p.add_run("图中文字对照（英文 → 中文）"), "微软雅黑", 8.5, bold=True,
          color=RGBColor(0x40, 0x40, 0x40))
    table = doc.add_table(rows=0, cols=4)
    table.autofit = False
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom", "left", "right", "insideH", "insideV"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "nil")
        borders.append(el)
    tblPr.append(borders)
    cols = [Cm(5.0), Cm(3.0), Cm(5.0), Cm(3.0)]
    for k in range(0, len(pairs), 2):
        row = table.add_row().cells
        trPr = table.rows[-1]._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        trPr.append(cant)
        chunk = pairs[k:k + 2]
        for n, (en, cn) in enumerate(chunk):
            for c, (val, fname) in enumerate([(en, "Times New Roman"), (cn, "微软雅黑")]):
                cell = row[n * 2 + c]
                cell.width = cols[n * 2 + c]
                pp = cell.paragraphs[0]
                pp.paragraph_format.space_before = Pt(0.5)
                pp.paragraph_format.space_after = Pt(0.5)
                pp.paragraph_format.line_spacing = 1.0
                style(pp.add_run(val), fname, 8, color=RGBColor(0x33, 0x33, 0x33))
    for row in table.rows[:-1]:
        for cell in row.cells:
            for pp in cell.paragraphs:
                pp.paragraph_format.keep_with_next = True
    return table


def _colorful(path):
    """带底色的图（表格色块）不是公式，判为 True。"""
    try:
        from PIL import Image
    except Exception:
        return False
    if path in _COLOR_CACHE:
        return _COLOR_CACHE[path]
    try:
        im = Image.open(path).convert("RGB")
        im = im.resize((min(im.width, 120), max(1, min(im.height, 60))))
        px = list(im.getdata())
        sat = sum(1 for r, g, b in px if max(r, g, b) - min(r, g, b) > 30)
        res = sat / max(len(px), 1) > 0.18
    except Exception:
        res = False
    _COLOR_CACHE[path] = res
    return res


_COLOR_CACHE = {}


# ---- 由 paper.json 覆盖论文相关常量 ----
TERMS = [tuple(x) for x in CFG["terms"]]
GLOSS = [tuple(x) for x in CFG["gloss"]]
GLOSS_EN = [(en, zh) for zh, en in GLOSS]
FIG_TEXTS = {k: [tuple(y) for y in v] for k, v in CFG.get("fig_texts", {}).items()}
TBL_NOTE = CFG.get("table_note", "")
FIG_NOTE = CFG.get("figure_note", "")


def build():

    items = json.load(open(os.path.join(BIL, "items_full.json"), encoding="utf-8"))
    zh = json.load(open(os.path.join(BIL, "zh_full.json"), encoding="utf-8"))
    eqs = json.load(open(os.path.join(BIL, "eq_map.json"), encoding="utf-8"))
    # make_eqs/eq_fix 写的是 {idx: {...}}，extract 写的是 {idx: [...]}；统一成列表
    for _k, _v in list(eqs.items()):
        if isinstance(_v, dict):
            _v = dict(_v)
            _v["path"] = _v.get("img", _v.get("path"))
            eqs[_k] = [_v]

    def add_eqs(idx):
        for e in eqs.get(str(idx), []):
            if e.get("inline") or not os.path.exists(e["path"]):
                continue
            if _colorful(e["path"]):
                continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            wpt = min(e["w"], 430)
            p.add_run().add_picture(e["path"], width=Pt(wpt))

    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(2.4)
    sec.right_margin = Cm(2.4)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.2)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

    # ---------- 第 1 页：术语表 ----------
    t = add_en(doc, CFG["title"], size=16, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=2)
    add_en(doc, CFG.get("subtitle", ""),
           size=10, align=WD_ALIGN_PARAGRAPH.LEFT, after=10)
    add_zh(doc, CFG.get("read_note",
                        "读法：黑字为原文，蓝字为译文，一段英文一段中文，上下对应；蓝字里的小字括号是该术语第一次出现时的英文原词。"),
           size=9.5, color=RGBColor(0x40, 0x40, 0x40), after=10, indent=0)

    add_zh(doc, "术语表（按首次出现排序，%d 条）" % len(CFG["terms"]), size=11, bold=True, color=RGBColor(0, 0, 0),
           after=4, indent=0)

    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = [Cm(0.9), Cm(5.4), Cm(4.2), Cm(5.7)]

    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "12")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    for edge in ("left", "right", "insideH", "insideV"):
        el = OxmlElement("w:%s" % edge)
        el.set(qn("w:val"), "nil")
        borders.append(el)
    tblPr.append(borders)

    hdr = table.rows[0].cells
    for i, h in enumerate(["#", "英文", "中文", "说明：为什么容易译错"]):
        hdr[i].width = widths[i]
        p0 = hdr[i].paragraphs[0]
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        style(p0.add_run(h), "微软雅黑", 9, bold=True)

    for n, (en, cn, note) in enumerate(TERMS, 1):
        row = table.add_row().cells
        for i, val in enumerate([str(n), en, cn, note]):
            row[i].width = widths[i]
            p0 = row[i].paragraphs[0]
            p0.paragraph_format.space_before = Pt(1.5)
            p0.paragraph_format.space_after = Pt(1.5)
            p0.paragraph_format.line_spacing = 1.0
            style(p0.add_run(val), "Times New Roman" if i in (0, 1) else "微软雅黑", 9)

    # 表头下横线（三线表的中线）
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcB = OxmlElement("w:tcBorders")
        bot = OxmlElement("w:bottom")
        bot.set(qn("w:val"), "single")
        bot.set(qn("w:sz"), "6")
        bot.set(qn("w:space"), "0")
        bot.set(qn("w:color"), "000000")
        tcB.append(bot)
        tcPr.append(tcB)

    doc.add_page_break()

    # ---------- 目录（中英对照，页码为原 PDF 页码） ----------
    def add_toc():
        tp = os.path.join(BIL, "toc.json")
        zp = os.path.join(BIL, "toc_zh.json")
        if not (os.path.exists(tp) and os.path.exists(zp)):
            return
        entries = json.load(open(tp, encoding="utf-8")).get("entries", [])
        tzh = json.load(open(zp, encoding="utf-8"))
        if not entries:
            return
        h = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=2)
        style(h.add_run("目录（Contents）"), "微软雅黑", 14, bold=True,
              color=RGBColor(0x1F, 0x1F, 0x1F))
        note = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=8)
        style(note.add_run("页码为原 PDF 页码，可按正文中的「— 原文第 N 页 —」定位。"),
              "微软雅黑", 8.5, color=RGBColor(0x70, 0x70, 0x70))
        for i, (lvl, num, en, pg) in enumerate(entries):
            zh = (tzh.get(str(i)) or "").strip()
            p = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=0, spacing=1.0)
            p.paragraph_format.left_indent = Cm(0.45 * (min(int(lvl), 3) - 1))
            p.paragraph_format.tab_stops.add_tab_stop(
                Cm(15.7), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            head = (num + "  ") if num else ""
            if head:
                style(p.add_run(head), "Times New Roman", 9.5,
                      bold=(int(lvl) == 1), color=RGBColor(0x1F, 0x1F, 0x1F))
            style(p.add_run(zh or en), "微软雅黑", 9.5, bold=(int(lvl) == 1),
                  color=RGBColor(0x1F, 0x1F, 0x1F))
            if zh:
                style(p.add_run("（%s）" % en), "Times New Roman", 8.5,
                      color=RGBColor(0x6A, 0x6A, 0x6A))
            style(p.add_run("\t%d" % pg), "Times New Roman", 9.5,
                  color=RGBColor(0x1F, 0x1F, 0x1F))
        doc.add_page_break()

    add_toc()

    # ---------- 正文：一句英文一句中文 ----------
    used_gloss = set()
    used_en = set()
    pending_legend = None
    cur_page = None
    num_re = re.compile(r"^[\s0-9+\-.,%/()·]+$")
    num_buf = []

    tables_raw = {}
    tpath = os.path.join(BIL, "table_map.json")
    if os.path.exists(tpath):
        tables_raw = json.load(open(tpath, encoding="utf-8"))
    TBL = {}
    for cap_idx, info in tables_raw.items():
        info = dict(info)
        info["cap"] = int(cap_idx)
        info["first"] = min(info["skip"])
        for si in info["skip"]:
            TBL[int(si)] = info

    figs_raw = {}
    fpath = os.path.join(BIL, "fig_map.json")
    if os.path.exists(fpath):
        figs_raw = json.load(open(fpath, encoding="utf-8"))
    EQD, EQ_SKIP = {}, set()
    for _f in ("eq_map.json", "alg_map.json"):
        _eqp = os.path.join(BIL, _f)
        if os.path.exists(_eqp):
            for _k, _v in json.load(open(_eqp, encoding="utf-8")).items():
                if "skip" in _v:
                    EQD[int(_k)] = _v
                    EQ_SKIP.update(_v["skip"])
    FIG = {}
    for cap_idx, info in figs_raw.items():
        info = dict(info)
        info["cap"] = int(cap_idx)
        info["first"] = min(info["skip"])
        for si in info["skip"]:
            FIG[int(si)] = info

    FIG_NOTE_KEYS = set(CFG.get("figure_note_for", []))

    def add_fig_block(info):
        img = info["img"]
        if not os.path.exists(img):
            return
        w = min(float(info["w"]), 445.0)
        pi = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=8, after=6)
        pi.add_run().add_picture(img, width=Pt(w))
        cap_txt = items[info["cap"]].get("text", "")
        if cap_txt in FIG_NOTE_KEYS:
            note = FIG_NOTE
            pn = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, before=2, after=8, indent=0.2)
            style(pn.add_run(note), "微软雅黑", 9, color=RGBColor(0x1F, 0x4E, 0x79))

    def add_table_img(info):
        img = info["img"]
        if not os.path.exists(img):
            return
        w = min(float(info["w"]), 445.0)
        pi = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=6, after=6)
        pi.add_run().add_picture(img, width=Pt(w))
        cap_txt = items[info["cap"]].get("text", "")
        if TBL_NOTE and "Notations" in cap_txt:
            note = TBL_NOTE
            pn = para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=2, after=8, indent=0.2)
            style(pn.add_run(note), "微软雅黑", 9, color=RGBColor(0x1F, 0x4E, 0x79))

    def flush_nums():
        if not num_buf:
            return
        np_ = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, before=3, after=3, indent=0.4)
        style(np_.add_run("   ".join(num_buf)), "Times New Roman", 9,
              color=RGBColor(0x44, 0x44, 0x44))
        num_buf.clear()

    # 合并被 PDF 拆成两段的标题（'1.3' + 'Overview of our work'）
    # 注意：有的编号是 12pt 的 para（不是 heading），条件不能只认 heading
    _skip_head = set()
    for _i, _it in enumerate(items):
        _t = (_it.get("text") or "").strip()
        if _it.get("kind") in ("heading", "para") and re.match(r"^\d+(\.\d+)*$", _t):
            _nx = items[_i + 1] if _i + 1 < len(items) else None
            if (_nx and _nx.get("kind") in ("heading", "para")
                    and abs((_nx.get("y0") or 0) - (_it.get("y0") or 0)) < 2
                    and re.match(r"^[A-Z]", (_nx.get("text") or "").strip())):
                _nx["text"] = _t + "  " + (_nx.get("text") or "").strip()
                if _nx.get("sents"):
                    _nx["sents"][0] = _t + "  " + _nx["sents"][0]
                _zh_a = zh.get(str(_i), "")
                _zh_b = zh.get(str(_i + 1), "")
                zh[str(_i + 1)] = (_zh_a + " " + _zh_b).strip()
                _skip_head.add(_i)

    # 合并被 PDF 行宽从句子中间劈开的段落（上一段无终止符 + 下一段以小写 / 数学符号开头）。
    # 不合并的话中文块会插进英文句子中间，读起来是断的。
    TERM = re.compile(r"[.!?:;。！？：；][\"”’)\]]?$")
    CONT = re.compile(r"^(?:[a-z(“\[‘]|[\U0001D400-\U0001D7FF]|[\^_]\{|\()")
    MERGED, MERGE_SKIP = {}, set()

    def _zh_all(i):
        return "".join(zh.get("%d.%d" % (i, j), "")
                       for j in range(len(items[i].get("sents", []))))

    _i = 0
    while _i < len(items):
        if items[_i].get("kind") != "para" or _i in EQ_SKIP:
            _i += 1
            continue
        _chain = [_i]
        _absorb = set()
        _j = _i + 1
        while _j < len(items):
            # 跳过中间的空图片条目（二维码/水印被清掉后留下的空壳），它们不该阻断合并
            _k = _j
            while (_k < len(items) and items[_k].get("kind") == "img"
                   and not items[_k].get("path")):
                _k += 1
            if _k >= len(items):
                break
            _a, _b = items[_chain[-1]], items[_k]
            if _b.get("kind") != "para":
                break
            # 允许跨一页合并：段落被页码切开是最常见的一种断法
            if abs((_b.get("page") or 0) - (_a.get("page") or 0)) > 1:
                break
            if _k in EQ_SKIP or _k in TBL or _k in FIG:
                break
            _ta, _tb = (_a.get("text") or "").strip(), (_b.get("text") or "").strip()
            if not _ta or not _tb or _tb.startswith("•"):
                break
            if TERM.search(_ta) or not CONT.match(_tb):
                break
            # 上一段过短时只接受“明显是公式续行”的下一段，避免把表格碎片串成一坨
            if len(_ta.split()) < 6 and not re.match(r"^(?:[\(\[]|[\^_]\{|\d+[).])", _tb):
                break
            _absorb.update(range(_j, _k))
            _chain.append(_k)
            _j = _k + 1
        if len(_chain) > 1:
            MERGED[_i] = {
                "text": " ".join((items[k].get("text") or "").strip() for k in _chain),
                "zh": "".join(_zh_all(k) for k in _chain),
            }
            MERGE_SKIP.update(_chain[1:])
            MERGE_SKIP.update(_absorb)
            _i = _j
        else:
            _i += 1

    for idx, it in enumerate(items):
        if idx in _skip_head:
            add_eqs(idx)
            continue
        if idx in MERGE_SKIP:
            add_eqs(idx)
            continue
        kind = it.get("kind")
        sents = it.get("sents", [])
        page = it.get("page")
        if HEADER.match((it.get("text") or "").strip()):
            continue
        if idx in EQ_SKIP:
            _v = EQD.get(idx)
            if _v:
                flush_nums()
                _pw = min(float(_v["w"]), 445.0)
                _pe = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=6, after=6)
                _pe.add_run().add_picture(_v["img"], width=Pt(_pw))
                _t0 = (it.get("text") or "").strip()
                _cz = (zh.get(str(idx), "") or "").strip()
                if _t0.startswith("Algorithm") and _cz and _cz != _t0:
                    _pc = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=10, indent=0)
                    style(_pc.add_run(_cz), "微软雅黑", 10,
                          color=RGBColor(0x40, 0x40, 0x40))
            continue
        if idx in FIG:
            info = FIG[idx]
            if idx == info["first"]:
                flush_nums()
                add_fig_block(info)
            continue
        if idx in TBL:
            info = TBL[idx]
            if idx == info["first"]:
                flush_nums()
                add_table_img(info)
            continue
        if kind != "para":
            flush_nums()
        if page != cur_page:
            flush_nums()
            if cur_page is not None:
                mp = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=12, after=6)
                style(mp.add_run("— 原文第 %d 页 —" % page), "微软雅黑", 8,
                      color=RGBColor(0x9A, 0x9A, 0x9A))
            cur_page = page
        if kind == "heading":
            size = float(it.get("size", 12.0))
            txt = sents[0] if sents else it.get("text", "")
            add_en(doc, txt, size=size, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT,
                   before=10 if size > 15 else 8, after=1)
            _hz = (zh.get(str(idx)) or "").strip()
            if _hz and _hz != txt.strip() and re.search(r"[\u4e00-\u9fff]", _hz):
                add_zh(doc, _hz, size=max(size - 1.5, 10.5), bold=True,
                       color=RGBColor(0x1F, 0x1F, 0x1F), after=5, indent=0)
            add_eqs(idx)
        elif kind == "caption":
            txt = sents[0] if sents else it.get("text", "")
            _cp = add_en(doc, txt, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, before=3, after=0)
            if (idx + 1) in EQD:
                _cp.paragraph_format.keep_with_next = True
            if str(idx) in zh and re.search(r"[\u4e00-\u9fff]", zh.get(str(idx), "")):
                add_zh(doc, zh[str(idx)], size=10, align=WD_ALIGN_PARAGRAPH.CENTER,
                       after=8, indent=0, color=RGBColor(0x40, 0x40, 0x40))
            if pending_legend:
                add_fig_legend(doc, pending_legend)
                pending_legend = None
            add_eqs(idx)
        elif kind == "img":
            path = it.get("path")
            if path and os.path.exists(path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(0)
                width = Cm(it.get("w", 300) * 2.54 / 72.0)
                if width > Cm(16.2):
                    width = Cm(16.2)
                p.add_run().add_picture(path, width=width)
                key = os.path.basename(path)
                if key in FIG_TEXTS:
                    pending_legend = FIG_TEXTS[key]
            add_eqs(idx)
        else:
            en_text = it.get("text", "")
            _mg = MERGED.get(idx)
            if _mg:
                en_text = _mg["text"]
            if num_re.match(en_text) and len(en_text) < 80:
                num_buf.append(en_text.strip())
                continue
            flush_nums()
            bullet = en_text.strip().startswith("•")
            if CODE.match(en_text.strip()):
                add_en(doc, en_text, size=10.5, after=0, before=4, indent_first=0)
                add_eqs(idx)
                continue
            if it.get("nozh"):
                add_en(doc, en_text, size=10.5, after=0, before=6,
                       indent_first=0 if bullet else 0.5)
                add_eqs(idx)
                continue
            if _is_num_heading(en_text):
                add_en(doc, en_text, size=13, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT,
                       before=10, after=1)
                zh_text0 = (_mg["zh"] if _mg else
                            "".join(zh.get("%d.%d" % (idx, j), "") for j in range(len(sents))))
                if zh_text0.strip() and zh_text0.strip() != en_text.strip() \
                        and re.search(r"[\u4e00-\u9fff]", zh_text0):
                    add_zh(doc, zh_text0, size=11.5, bold=True, color=RGBColor(0x1F, 0x1F, 0x1F),
                           after=5, indent=0, panel=False)
                add_eqs(idx)
                continue
            if _mg:
                zh_text = _mg["zh"]
            else:
                keys = ["%d.%d" % (idx, j) for j in range(len(sents))]
                zh_text = "".join(zh.get(k, "") for k in keys)
            has_cjk = any("\u4e00" <= c <= "\u9fff" for c in zh_text)
            if not has_cjk:
                add_en(doc, en_text, size=10.5, after=0, before=3, indent_first=0)
                add_eqs(idx)
                continue
            add_en(doc, en_text, size=12.0, after=0, before=14,
                   indent_first=0.5 if not bullet else 0, used_en=used_en)
            same = zh_text.strip() == en_text.strip()
            if not same:
                inl = [e for e in eqs.get(str(idx), [])
                       if e.get("inline") and os.path.exists(e["path"])]
                add_zh(doc, zh_text, after=4, used_gloss=used_gloss, panel=True,
                       indent=0.15, first_line=0.6 if not bullet else 0,
                       inlines=inl or None)
            add_eqs(idx)

    flush_nums()
    add_zh(doc, CFG["end_note"],
           size=9, color=RGBColor(0x80, 0x80, 0x80), after=0, indent=0)

    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style(fp.add_run(CFG["footer_prefix"]), "微软雅黑", 8, color=RGBColor(0x70, 0x70, 0x70))
    r = fp.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = "PAGE"
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    r._r.append(f1); r._r.append(it); r._r.append(f2)
    style(r, "Times New Roman", 8, color=RGBColor(0x70, 0x70, 0x70))
    style(fp.add_run(" 页"), "微软雅黑", 8, color=RGBColor(0x70, 0x70, 0x70))

    doc.save(OUT)
    print("saved", OUT)
    print("glossed", len(used_gloss), sorted(used_gloss))


if __name__ == "__main__":
    build()
