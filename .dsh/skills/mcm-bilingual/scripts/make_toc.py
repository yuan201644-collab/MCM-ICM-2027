# -*- coding: utf-8 -*-
"""抽取论文 Contents 页的目录条目（支持跨页），输出 work/toc.json。

条目格式: [level, "1.2", "Restatement of the Problem", page]
level: 编号里的点数量（1 → 一级，2 → 二级 ...）；无编号条目 level=1、num=""
用法: MCM_CFG=<paper.json> python make_toc.py
"""
import json
import os
import re

import pymupdf

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
WD = CFG["workdir"]
doc = pymupdf.open(CFG["pdf"])

HDR = re.compile(
    r"^(Team\s*#?\s*\d+.*|Page\s+\d+(\s+of\s+\d+)?|"
    r"微\s*信\s*公\s*众\s*号.*|微\s*信\s*号.*|MATHmodels.*|"
    r"关\s*注\s*数\s*[字学]\s*模\s*型.*|获\s*取\s*更\s*多\s*资\s*讯.*|\d{1,2})\s*$", re.I)
LEAD = re.compile(r"(?:\.{3,}|(?:\s\.){4,}|…{2,}|\u2026+)")
NUM = re.compile(r"^(\d{1,2}(?:\.\d{1,2})*)\s+(.*?)\s+(\d{1,3})$")
PLAIN = re.compile(r"^([A-Z][A-Za-z&,\-’' ()\/]{2,70}?)\s+(\d{1,3})$")
# 公众号水印常被 PDF 抽成与目录标题同一行的前缀（"微信号：MATHmodels Ideal Water..."）。
# 只删水印串本身，保留后面真正的英文标题。
WM_INLINE = re.compile(
    r"(?:微\s*信\s*公\s*众\s*号|微\s*信\s*号)\s*[：:]?\s*"
    r"(?:数\s*[字学]\s*模\s*型|MATHmodels?|MATmodels?)?\s*"
    r"|MATHmodels?\b|关\s*注\s*数\s*[字学]\s*模\s*型|获\s*取\s*更\s*多\s*资\s*讯\s*\d*")


def fix(s):
    s = s.replace("Ĳ", "IJ").replace("ﬁ", "fi").replace("ﬂ", "fl")
    return WM_INLINE.sub("", s).strip()


def rows_of(pno):
    page = doc[pno]
    raw = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            t = fix(re.sub(r"\s+", " ", "".join(s["text"] for s in l["spans"])).strip())
            if not t:
                continue
            raw.append((l["bbox"][1], l["bbox"][0], t))
    raw.sort(key=lambda z: (round(z[0], 0), z[1]))
    rows = []
    for y, x, t in raw:
        if rows and abs(rows[-1][0] - y) <= 2.5:
            rows[-1][2].append((x, t))
        else:
            rows.append([y, x, [(x, t)]])
    out = []
    for y, x, cells in rows:
        cells.sort()
        out.append((y, x, " ".join(c[1] for c in cells).strip()))
    return out


def parse_page(pno):
    entries = []
    for y, x, t in rows_of(pno):
        if HDR.match(t):
            continue
        t2 = re.sub(r"\s{2,}", " ", LEAD.sub(" ", t)).strip()
        if re.match(r"^Contents\b", t2, re.I):
            continue
        m = NUM.match(t2)
        if m:
            num, title, pg = m.group(1), m.group(2).strip(" .·"), int(m.group(3))
            if title:
                entries.append([num.count(".") + 1, num, title, pg])
            continue
        m = PLAIN.match(t2)
        if m and " . " not in t and len(m.group(1).split()) <= 8:
            entries.append([1, "", m.group(1).strip(" .·"), int(m.group(2))])
            continue
        if entries and t2 and not re.match(r"^\d", t2) and len(t2.split()) <= 9 \
                and not t2[0].islower():
            entries[-1][2] = (entries[-1][2] + " " + t2).strip()
    return entries


all_entries = []
pno = 1 if doc.page_count > 1 else 0
for k in range(3):
    if pno + k >= doc.page_count:
        break
    got = parse_page(pno + k)
    if len(got) < 2:
        break
    all_entries.extend(got)

json.dump({"entries": all_entries}, open(os.path.join(WD, "toc.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("entries", len(all_entries))
for e in all_entries[:5]:
    print("   ", e)
