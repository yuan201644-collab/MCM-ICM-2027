# -*- coding: utf-8 -*-
"""图题上方若是一堆短标签（图表被抽成文字），整块裁成一张图。

三轮，按严格到宽松依次尝试，先成立者为准：
1) 短标签段（<8 词、不以句号/冒号结尾），跨度 > 120pt；
2) 连续碎片（<=12 词），跨度 > 100pt；
3) 放宽碎片（<=16 词，排除“≥8 词且以句号结尾”的整句），跨度 > 100pt。
"""
import json, os, re
import pymupdf

FIGCAP = re.compile(r"^Fig[a-z]*\.?\s*\d+", re.I)

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
BASE = CFG["workdir"]
SRC = CFG["pdf"]

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


def frag12(it):
    if it.get("kind") != "para":
        return False
    t = (it.get("text") or "").strip()
    return bool(t) and len(t.split()) <= 12


def frag16(it):
    if it.get("kind") != "para":
        return False
    t = (it.get("text") or "").strip()
    if not t:
        return False
    if t.endswith(".") and len(t.split()) >= 8:
        return False
    return len(t.split()) <= 16


def collect(cap_idx, pred):
    it = items[cap_idx]
    j = cap_idx - 1
    block = []
    while j >= 0 and items[j].get("page") == it["page"] and pred(items[j]):
        block.append(j)
        j -= 1
    return block


def crop(cap_idx, block, minh):
    it = items[cap_idx]
    if not block:
        return False
    block.sort()
    y0 = min(items[k]["y0"] for k in block) - 8
    y1 = it["y0"] - 2
    if y1 - y0 < minh:
        return False
    clip = pymupdf.Rect(58, y0, 548, y1)
    pix = doc[it["page"] - 1].get_pixmap(clip=clip, matrix=pymupdf.Matrix(3.0, 3.0))
    fn = os.path.join(BASE, "fig_%02d.png" % cap_idx)
    pix.save(fn)
    out[str(cap_idx)] = {"img": fn, "w": round(clip.width, 1), "h": round(clip.height, 1),
                         "skip": block, "page": it["page"]}
    print("p%-3s %-46s labels=%-3d h=%.0f" % (it["page"], (it.get("text") or "")[:46], len(block), y1 - y0))
    return True


for i, it in enumerate(items):
    if it.get("kind") != "caption":
        continue
    if not FIGCAP.match(it.get("text") or ""):
        continue
    if i == 0:
        continue
    if crop(i, collect(i, is_label), 120):
        continue
    if crop(i, collect(i, frag12), 100):
        continue
    crop(i, collect(i, frag16), 100)

json.dump(out, open(os.path.join(BASE, "fig_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("figure blocks", len(out))
