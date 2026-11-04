# -*- coding: utf-8 -*-
import pymupdf, os

SRC = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"
OUT = r"D:\26年美国大学生数学建模竞赛\_work\bil\table1.png"
doc = pymupdf.open(SRC)
page = doc[5]
blocks = page.get_text("dict")["blocks"]
ys = {}
for b in blocks:
    if b["type"] != 0:
        continue
    for l in b["lines"]:
        t = "".join(s["text"] for s in l["spans"]).strip()
        if t == "Symbol":
            ys["top"] = l["bbox"][1]
        if t.startswith("Note:"):
            ys["bot"] = l["bbox"][1]
print(ys)
r = pymupdf.Rect(68, ys["top"] + 1, 545, ys["bot"] - 3)
pix = page.get_pixmap(clip=r, matrix=pymupdf.Matrix(3.0, 3.0))
pix.save(OUT)
print("saved", OUT, pix.width, pix.height, "pt", round(r.width, 1), round(r.height, 1))
