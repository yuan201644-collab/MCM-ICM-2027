# -*- coding: utf-8 -*-
"""组装英中对照版：术语表 + 一句英文一句中文。"""
import json
import re
import sys
import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BIL = r"D:\26年美国大学生数学建模竞赛\_work\bil"
OUT = sys.argv[1] if len(sys.argv) > 1 else r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466_英中对照.docx"

NAVY = RGBColor(0x1F, 0x4E, 0x79)
GLOSS_BLUE = RGBColor(0x2E, 0x74, 0xB5)

TERMS = [
    ("Fatigue Physiological Model", "疲劳生理模型", "本文两大主模型之一，描述平均输出功率与持续输出时间的关系"),
    ("power curve", "功率曲线", "原文另有 power profile / power-time curve / power output curve 三种写法，均指同一物"),
    ("aerobic respiration", "有氧呼吸", ""),
    ("anaerobic respiration", "无氧呼吸", ""),
    ("Aerobic and Anaerobic Energy Fatigue Model", "有氧与无氧能量疲劳模型", "由上面两个子模型合并而成"),
    ("ordinary least squares", "普通最小二乘法（OLS）", "用数据拟合模型参数的估计方法"),
    ("Single Objective Programming", "单目标规划", "目标函数只有完赛时间一个"),
    ("decision variable", "决策变量", "本文指骑行者在赛道各位置施加的功率"),
    ("constraints", "约束条件", "骑手状态与赛道条件"),
    ("dynamic programming", "动态规划", "求解功率分配最优策略的算法"),
    ("sensitivity analysis", "灵敏度分析", "改变输入看结果变化幅度"),
    ("wind resistance", "风阻", ""),
    ("rolling resistance", "滚动阻力", ""),
    ("FTP", "功能性阈值功率（Functional Threshold Power）", "有氧供能的上限功率"),
    ("time trial", "个人计时赛", "车手单独出发、按时间排名"),
    ("draft strategy", "跟骑策略", "跟在队友身后减少风阻"),
    ("camber", "路拱（赛道横坡）", "赛道左右倾斜的角度"),
    ("insensitive", "不敏感的", "结果对该因素变化不敏感＝该因素影响小"),
]

GLOSS = [
    ("疲劳生理模型", "Fatigue Physiological Model"),
    ("功率曲线", "power curve"),
    ("有氧呼吸", "aerobic respiration"),
    ("无氧呼吸", "anaerobic respiration"),
    ("有氧与无氧能量疲劳模型", "Aerobic and Anaerobic Energy Fatigue Model"),
    ("普通最小二乘法", "ordinary least squares"),
    ("单目标规划", "Single Objective Programming"),
    ("决策变量", "decision variable"),
    ("约束条件", "constraints"),
    ("动态规划", "dynamic programming"),
    ("灵敏度分析", "sensitivity analysis"),
    ("风阻", "wind resistance"),
    ("滚动摩擦", "rolling resistance"),
    ("功能性阈值功率", "FTP"),
    ("个人计时赛", "time trial"),
    ("跟骑", "draft strategy"),
    ("不敏感", "insensitive"),
]


GLOSS_EN = [(en, zh) for zh, en in GLOSS]

FIG_TEXTS = {
    "img_05_2.png": [
        ("Part I: Model Construction", "第一部分：模型构建"),
        ("Cyclist's Physiological Model of Fatigue", "车手疲劳生理模型"),
        ("Aerobic Energy Fatigue Model", "有氧能量疲劳模型"),
        ("Anaerobic Energy Fatigue Model", "无氧能量疲劳模型"),
        ("Fit Models to Power Curve", "用功率曲线拟合模型"),
        ("Define Different Types of Cyclists by Power Curves", "按功率曲线划分车手类型"),
        ("Optimal Individual Power Distribution Model", "最优个人功率分配模型"),
        ("Riding Resistance Model", "骑行阻力模型"),
        ("Wind-Modification of Resistance Model", "阻力模型的风阻修正"),
        ("Abstract Course Model", "赛道抽象模型"),
        ("Gain the Height Profile of Courses", "得到赛道高度剖面"),
        ("Corner Course Model", "弯道模型"),
        ("Gain the Corner Profile of Courses", "得到赛道弯道剖面"),
        ("Dynamic Programming for the Best Power Distribution", "用动态规划求最优功率分配"),
        ("Part II: Model Evaluation", "第二部分：模型评价"),
        ("Sensitivity Analysis", "灵敏度分析"),
        ("Sensitivity to Changes in Wind Direction and Speed", "对风向与风速变化的灵敏度"),
        ("Sensitivity to Deviation from Target Power", "对偏离目标功率的灵敏度"),
        ("Strengths and Weaknesses", "优缺点"),
        ("Part III: Model Extension", "第三部分：模型推广"),
        ("Team Strategy Decision Model", "团队策略决策模型"),
        ("Team Resistance Reduction Model", "团队减阻模型"),
        ("Team Draft Strategy", "团队跟骑策略"),
        ("Team Drop Strategy", "团队掉队策略"),
        ("Best Power Profile and Best Team Strategy", "最优功率曲线与最优团队策略"),
    ],
}


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


def add_en(doc, text, size=12.0, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
           after=0, before=0, indent_first=0, used_en=None):
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
        style(p.add_run(seg), "Times New Roman", size, bold=bold,
              color=GLOSS_BLUE if is_term else None)
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
            style(p.add_run(seg), "微软雅黑", size, bold=bold, color=color)
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


def build():
    items = json.load(open(os.path.join(BIL, "items_full.json"), encoding="utf-8"))
    zh = json.load(open(os.path.join(BIL, "zh_full.json"), encoding="utf-8"))
    eqs = json.load(open(os.path.join(BIL, "eq_map.json"), encoding="utf-8"))

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
    t = add_en(doc, "2209466 英中对照版", size=16, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=2)
    add_en(doc, "2022 MCM Problem A · Optimal Power Distribution of a Cyclist",
           size=10, align=WD_ALIGN_PARAGRAPH.LEFT, after=10)
    add_zh(doc, "读法：黑字为原文，蓝字为译文，一句一段、上下对应；蓝字里的小字括号是该术语第一次出现时的英文原词。",
           size=9.5, color=RGBColor(0x40, 0x40, 0x40), after=10, indent=0)

    add_zh(doc, "术语表（按首次出现排序，18 条）", size=11, bold=True, color=RGBColor(0, 0, 0),
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
    FIG = {}
    for cap_idx, info in figs_raw.items():
        info = dict(info)
        info["cap"] = int(cap_idx)
        info["first"] = min(info["skip"])
        for si in info["skip"]:
            FIG[int(si)] = info

    def add_fig_block(info):
        img = info["img"]
        if not os.path.exists(img):
            return
        w = min(float(info["w"]), 445.0)
        pi = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=8, after=6)
        pi.add_run().add_picture(img, width=Pt(w))
        cap_txt = items[info["cap"]].get("text", "")
        if "Figure 11" in cap_txt:
            note = "（图中标签：Type 类型；Sprinter 冲刺手；Time Trial Specialist 个人计时赛选手；Tokyo 东京；Belgium 比利时；Own design 自主设计赛道。）"
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
        if "Notations" in cap_txt:
            note = ("（上表为原文表 1 原样：符号列在原 PDF 中是矢量图形，文字层里只剩说明与单位。"
                    "中文对照依次为：P_o 有氧呼吸能量输出功率；v_o(P_o) 有氧能量池消耗率；"
                    "P_N 无氧呼吸能量输出功率；v_N(P_N) 无氧能量池消耗率；W_N 无氧能量储备；"
                    "t 持续时间；v_R(P_o) 无氧能量池恢复率；P(t) 车手总输出功率；R_T 总阻力；"
                    "v_f 车手相对空气的速度；C_R 滚动摩擦系数；F 车手提供的功率；x 车手在赛道上的位置；"
                    "φ(x) 赛道坡度角；f(x) 海拔；g(x) 弯道；δ(x) 行进方向与风向的夹角；"
                    "v_w 风速；h(x) 跟骑的最优决策函数。）")
            pn = para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=2, after=8, indent=0.2)
            style(pn.add_run(note), "微软雅黑", 9, color=RGBColor(0x1F, 0x4E, 0x79))

    def flush_nums():
        if not num_buf:
            return
        np_ = para(doc, align=WD_ALIGN_PARAGRAPH.LEFT, before=3, after=3, indent=0.4)
        style(np_.add_run("   ".join(num_buf)), "Times New Roman", 9,
              color=RGBColor(0x44, 0x44, 0x44))
        num_buf.clear()

    for idx, it in enumerate(items):
        kind = it.get("kind")
        sents = it.get("sents", [])
        page = it.get("page")
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
            if str(idx) in zh:
                add_zh(doc, zh[str(idx)], size=max(size - 1.5, 10.5), bold=True,
                       color=RGBColor(0x1F, 0x1F, 0x1F), after=5, indent=0)
            add_eqs(idx)
        elif kind == "caption":
            txt = sents[0] if sents else it.get("text", "")
            add_en(doc, txt, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, before=3, after=0)
            if str(idx) in zh:
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
            if num_re.match(en_text) and len(en_text) < 80:
                num_buf.append(en_text.strip())
                continue
            flush_nums()
            bullet = en_text.strip().startswith("•")
            if it.get("nozh"):
                add_en(doc, en_text, size=10.5, after=0, before=6,
                       indent_first=0 if bullet else 0.5)
                add_eqs(idx)
                continue
            if (re.match(r"^\d+(\.\d+)*\.?\s", en_text) and len(en_text) < 90
                    and sum(c.isalpha() for c in en_text) >= 3):
                add_en(doc, en_text, size=13, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT,
                       before=10, after=1)
                zh_text0 = "".join(zh.get("%d.%d" % (idx, j), "") for j in range(len(sents)))
                if zh_text0:
                    add_zh(doc, zh_text0, size=11.5, bold=True, color=RGBColor(0x1F, 0x1F, 0x1F),
                           after=5, indent=0, panel=False)
                add_eqs(idx)
                continue
            keys = ["%d.%d" % (idx, j) for j in range(len(sents))]
            zh_text = "".join(zh.get(k, "") for k in keys)
            add_en(doc, en_text, size=12.0, after=0, before=14,
                   indent_first=0.5 if not bullet else 0, used_en=used_en)
            if zh_text:
                inl = [e for e in eqs.get(str(idx), [])
                       if e.get("inline") and os.path.exists(e["path"])]
                add_zh(doc, zh_text, after=4, used_gloss=used_gloss, panel=True,
                       indent=0.15, first_line=0.6 if not bullet else 0,
                       inlines=inl or None)
            else:
                add_zh(doc, "【缺译文 %s】" % keys[0], size=9, color=RGBColor(0xC0, 0, 0),
                       after=10, indent=0)
            add_eqs(idx)

    flush_nums()
    add_zh(doc, "（全文完。公式与表格在原 PDF 中是矢量图形，未纳入本对照版；可按文中「原文第 N 页」标记翻到 2209466.pdf 或 2209466_版式还原.docx 对照查看。）",
           size=9, color=RGBColor(0x80, 0x80, 0x80), after=0, indent=0)

    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style(fp.add_run("2209466 英中对照版 · 第 "), "微软雅黑", 8, color=RGBColor(0x70, 0x70, 0x70))
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
