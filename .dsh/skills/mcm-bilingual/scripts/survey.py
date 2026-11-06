# -*- coding: utf-8 -*-
"""诊断：给一篇论文 PDF，打印页数、每页首行、疑似目录页/参考文献页。

用法： python survey.py <pdf>
"""
import sys

import pymupdf

path = sys.argv[1]
doc = pymupdf.open(path)
print("FILE", path)
print("PAGES", doc.page_count)
for i, p in enumerate(doc):
    t = " ".join(p.get_text().split())
    dots = t.count("....")
    flag = []
    if dots > 3:
        flag.append("TOC?")
    if t.strip().startswith("References") or t.count("References") == 1 and "References" in t[:60]:
        flag.append("REF?")
    print("  p%-2d len=%-5d %-6s %s" % (i, len(t), ",".join(flag), t[:90]))
