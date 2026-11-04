# -*- coding: utf-8 -*-
import pymupdf
import sys

pdf = sys.argv[1]
d = pymupdf.open(pdf)
print("pages", d.page_count)
for i in range(d.page_count):
    t = d[i].get_text()
    if "(7) where" in t or "fluid density" in t:
        print("page", i)
        d[i].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(
            r"D:\26年美国大学生数学建模竞赛\_work\preview\eqp%02d.png" % (i + 1))
