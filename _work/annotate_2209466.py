# -*- coding: utf-8 -*-
"""在可编辑版基础上生成"精读批注版"：术语表 + 首次出现中文括注 + 文末长难句拆解。"""
import copy
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_BREAK, WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

SRC = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466_可编辑.docx"
DST = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466_批注版.docx"

BLUE = RGBColor(0x1F, 0x4E, 0x79)

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

SENTENCES = [
    ("Firstly, we established a Fatigue Physiological Model",
     "Firstly, we established a Fatigue Physiological Model to characterize riders' power curve, which describes a "
     "rider's average power output as a function of sustained output time.",
     "主句：we established a Model。to characterize... 是目的状语；which... 是定语从句。",
     "首先，我们建立了疲劳生理模型来刻画骑手的功率曲线，该曲线把骑手的平均输出功率描述为持续输出时间的函数。",
     "which 指 model 还是 curve？语法上更近的先行词是 curve，但语义上\"描述功率曲线\"的是 model。译文按语义取 model，"
     "并在中文里用\"该曲线\"接住，避免歧义。机翻常直接译成\"它描述了……\"，读者不知道\"它\"是谁。"),
    ("From the perspective of aerobic respiration",
     "From the perspective of aerobic respiration and anaerobic respiration, we fully consider the limitation of "
     "energy and the process of energy recovery, and establish Aerobic and Anaerobic Energy Fatigue Model.",
     "主句：we consider ... and establish ...（一个主语带两个谓语）。",
     "我们从有氧呼吸与无氧呼吸的角度，充分考虑能量的限制与能量恢复过程，建立了有氧与无氧能量疲劳模型。",
     "\"the limitation of energy and the process of energy recovery\" 是两个名词短语并列，不是\"能量的限制与恢复的过程\""
     "这种层层套娃。中文要拆成\"能量受限\"与\"能量恢复\"两个动作。"),
    ("did not increase by 10% until",
     "Completion time did not increase by 10% until the average deviation change reached 5%.",
     "主句：Completion time did not increase。until 引导时间状语从句。",
     "直到平均偏差变化达到 5%，完赛时间才增加 10%。",
     "not ... until 是\"直到……才\"，不是\"没有增加，直到……\"。语序一颠倒，结论就从\"影响很小\"变成\"一直没影响\"。"
     "这是机翻最高频的错误之一。"),
    ("insensitive to rider deviation",
     "Therefore, we believe that the model results are insensitive to rider deviation from target power.",
     "主句：we believe that ...；宾语从句的主干是 results are insensitive to deviation。",
     "因此我们认为，模型结果对骑手偏离目标功率这一情况并不敏感。",
     "insensitive to 是\"对……不敏感\"，不是\"不敏感地对待\"。deviation from target power 是\"偏离目标功率\"，"
     "不是\"目标功率的偏差\"。"),
    ("Considering that practical problems always contain",
     "Considering that practical problems always contain many complex factors, first of all, we need to make "
     "reasonable assumptions to simplify the model, and each hypothesis is closely followed by its corresponding "
     "explanation:",
     "主句：we need to make assumptions。Considering that... 是分词状语；and 连接后半句 each hypothesis is followed by ...。",
     "考虑到实际问题总包含许多复杂因素，首先我们需要作出合理假设以简化模型，而每个假设后面都紧跟对应的说明：",
     "同一句里 assumptions 与 hypothesis 混用，指的是同一件事。中文统一译\"假设\"，否则读者以为有两类东西。"
     "这是原文写作不严谨，译者要在术语表里说明，不要跟着混。"),
]


def add_page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)
    return p


def style_run(r, size=10.5, color=None, bold=False):
    r.font.size = Pt(size)
    r.bold = bold
    if color is not None:
        r.font.color.rgb = color
    r.font.name = "Times New Roman"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


doc = Document(SRC)
first = doc.paragraphs[0]
front = []


def front_par(text="", size=10.5, bold=False, color=None, align=None, space_after=4):
    p = doc.add_paragraph()
    if text:
        style_run(p.add_run(text), size=size, bold=bold, color=color)
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    front.append(p._p)
    return p


front_par("2209466 精读批注版", size=16, bold=True, space_after=2)
front_par("2022 年 MCM A 题《Optimal Power Distribution of a Cyclist》· 译者注", size=10.5, space_after=10)
front_par("怎么用这一版", size=12, bold=True, space_after=4)
front_par("一、正文中蓝色小字是译者注，只解决歧义，不是原文的一部分；读正文时可先跳过。", space_after=2)
front_par("二、下面这张术语表按首次出现顺序排列，共 18 条；正文首次出现处已用蓝色括号补中文。", space_after=2)
front_par("三、文末有 5 句长难句，按\"原句—主干—译文—陷阱\"拆开，这 5 句读懂，全文的方法论就读懂了。", space_after=2)
front_par("四、正文里的目录页码是原 PDF（25 页版）的页码，本文件加了批注页，不要按目录页码跳转。", space_after=2)
front_par("五、需要看原始排版（25 页、图与公式原位）请打开同目录的 2209466_版式还原.docx。", space_after=12)

front_par("术语表（按首次出现排序）", size=12, bold=True, space_after=6)

table = doc.add_table(rows=1, cols=4)
table.style = "Table Grid"
table.autofit = False
hdr = table.rows[0].cells
for i, h in enumerate(["#", "英文", "中文", "说明"]):
    hdr[i].text = ""
    style_run(hdr[i].paragraphs[0].add_run(h), size=9, bold=True)
for i, (en, zh, note) in enumerate(TERMS, 1):
    row = table.add_row().cells
    for j, val in enumerate([str(i), en, zh, note]):
        row[j].text = ""
        style_run(row[j].paragraphs[0].add_run(val), size=9)
WIDTHS = [Cm(0.9), Cm(5.6), Cm(4.3), Cm(5.1)]
for w, col in zip(WIDTHS, table.columns):
    col.width = w
    for cell in col.cells:
        cell.width = w
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
front.append(table._tbl)
front_par("", space_after=2)
add_page_break(doc)
front.append(doc.paragraphs[-1]._p)

for el in front:
    first._p.addprevious(el)

# ---- 正文首次出现处括注 ----
paras = [p for p in doc.paragraphs if p.text.strip() and "....." not in p.text]
hits = {}
for en, zh, _ in TERMS:
    for idx, p in enumerate(paras):
        pos = p.text.lower().find(en.lower())
        if pos >= 0:
            hits.setdefault(idx, []).append((pos, pos + len(en), zh))
            break

glossed = 0
for idx, items in hits.items():
    p = paras[idx]
    for start, end, zh in sorted(items, key=lambda t: -t[0]):
        runs = p.runs
        pos = 0
        target = None
        for r in runs:
            if pos < end <= pos + len(r.text):
                target = (r, end - pos)
                break
            pos += len(r.text)
        if target is None:
            continue
        r, cut = target
        gr = p.add_run("（" + zh + "）")
        style_run(gr, size=9, color=BLUE)
        if cut < len(r.text):
            tail = p.add_run(r.text[cut:])
            tail._element.insert(0, copy.deepcopy(r._element.rPr)) if r._element.rPr is not None else None
            r.text = r.text[:cut]
            r._element.addnext(tail._element)
            r._element.addnext(gr._element)
        else:
            r._element.addnext(gr._element)
        glossed += 1

# ---- 文末长难句 ----
add_page_break(doc)
h = doc.add_paragraph()
style_run(h.add_run("长难句拆解（5 句）"), size=14, bold=True)
h.paragraph_format.space_after = Pt(8)

for i, (anchor, sent, trunk, zh, trap) in enumerate(SENTENCES, 1):
    t = doc.add_paragraph()
    style_run(t.add_run("第 %d 句" % i), size=11, bold=True)
    t.paragraph_format.space_before = Pt(10)
    t.paragraph_format.space_after = Pt(3)

    for label, body in (("原句", sent), ("主干", trunk), ("译文", zh), ("陷阱", trap)):
        p = doc.add_paragraph()
        r1 = p.add_run(label + "：")
        style_run(r1, size=10, bold=True, color=BLUE)
        r2 = p.add_run(body)
        style_run(r2, size=10, color=BLUE if label == "陷阱" else None)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Cm(0.6)

doc.save(DST)
print("saved", DST, "| glossed", glossed, "| paras", len(doc.paragraphs))
