# -*- coding: utf-8 -*-
import pymupdf
p = pymupdf.open(r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf")
page = p[11]
lines = []
for b in page.get_text("dict")["blocks"]:
    if b["type"] != 0:
        continue
    for l in b["lines"]:
        t = "".join(s["text"] for s in l["spans"]).strip()
        if t:
            lines.append((round(l["bbox"][1], 1), round(l["bbox"][3], 1), t[:40]))
for y0, y1, t in lines:
    if 150 < y0 < 330:
        print("%7.1f %7.1f  %s" % (y0, y1, t))
print("---- drawings in y 150..330 ----")
for d in page.get_drawings():
    r = d["rect"]
    if 150 < r.y0 < 330 and r.width < 40:
        print("x=%6.1f y=%6.1f w=%5.1f h=%5.1f items=%d" % (r.x0, r.y0, r.width, r.height, len(d["items"])))
