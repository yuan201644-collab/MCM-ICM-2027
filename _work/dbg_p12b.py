# -*- coding: utf-8 -*-
import pymupdf
p = pymupdf.open(r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf")
page = p[11]
print("--- text lines y<160 ---")
for b in page.get_text("dict")["blocks"]:
    if b["type"] != 0:
        continue
    for l in b["lines"]:
        t = "".join(s["text"] for s in l["spans"])
        if t.strip() and l["bbox"][1] < 160:
            print("%7.1f %7.1f x%6.1f %s" % (l["bbox"][1], l["bbox"][3], l["bbox"][0], t[:70]))
print("--- drawings y<160 (small) ---")
for d in page.get_drawings():
    r = d["rect"]
    if r.y0 < 160 and r.width < 40:
        print("x=%6.1f y=%6.1f w=%5.1f h=%5.1f items=%d" % (r.x0, r.y0, r.width, r.height, len(d["items"])))
