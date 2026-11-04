# -*- coding: utf-8 -*-
"""图题上方若是一堆短标签（图表被抽成文字），整块裁成一张图。"""
import json, os
import pymupdf

BASE = r"D:\26年美国大学生数学建模竞赛\_work\bil"
SRC = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf"

items = json.load(open(os.path.join(BASE, "items_full.json"), encoding="utf-8"))
doc = pymupdf.open(SRC)
out = {}


def is_label(it):
    if it.get("kind") != "para":
        return False
    t = (it.get("text") or "").strip()
    if not t:
        return False
    if len(t.split()) >= 8 or t.endswith(".") or t.endswith(":"):
        return False
    return True


for i, it in enumerate(items):
    if it.get("kind") != "caption":
        continue
    if not (it.get("text") or "").startswith("Figure"):
        continue
    if i == 0:
        continue
    j = i - 1
    block = []
    while j >= 0 and items[j].get("page") == it["page"] and is_label(items[j]):
        block.append(j)
        j -= 1
    if not block:
        continue
    block.sort()
    y0 = min(items[k]["y0"] for k in block) - 8
    y1 = items[i]["y0"] - 2
    if y1 - y0 < 120:
        continue
    clip = pymupdf.Rect(58, y0, 548, y1)
    pix = doc[it["page"] - 1].get_pixmap(clip=clip, matrix=pymupdf.Matrix(3.0, 3.0))
    fn = os.path.join(BASE, "fig_%02d.png" % i)
    pix.save(fn)
    out[str(i)] = {"img": fn, "w": round(clip.width, 1), "h": round(clip.height, 1),
                   "skip": block, "page": it["page"]}
    print("p%-3s %-44s labels=%d h=%.0f" % (it["page"], it["text"][:44], len(block), y1 - y0))

json.dump(out, open(os.path.join(BASE, "fig_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("figure blocks", len(out))
