# -*- coding: utf-8 -*-
"""把 Algorithm 伪代码块整块裁成图片（锚点：`Algorithm N` 题注，冒号可有可无）。"""
import json
import os
import re

import pymupdf

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
ROOT = os.path.dirname(os.environ["MCM_CFG"])
WORK = os.path.join(ROOT, "work")
OUT = os.path.join(WORK, "eq_imgs")
os.makedirs(OUT, exist_ok=True)
PDF = os.path.join(ROOT, CFG["pdf"])

# 有的论文写 "Algorithm 1: xxx"，有的写 "Algorithm 1 Lamprey Population Iteration Simulation"
ALG = re.compile(r"^Algorithm\s*\d+\b", re.I)
STOP = re.compile(r"^(?:Figure|Table|Fig\.)\s*\d+\s*[.:]", re.I)
SECT = re.compile(r"^\d+(?:\.\d+)*\s+[A-Z]")

items = json.load(open(os.path.join(WORK, "items_full.json"), encoding="utf-8"))
doc = pymupdf.open(PDF)

alg_map = {}
for pno in CFG["pages"]:
    if pno >= doc.page_count:
        continue
    page = doc[pno]
    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            t = "".join(s["text"] for s in l["spans"]).strip()
            if t:
                lines.append({"t": t, "x0": l["bbox"][0], "y0": l["bbox"][1],
                              "x1": l["bbox"][2], "y1": l["bbox"][3],
                              "size": max(s["size"] for s in l["spans"])})
    for i, l in enumerate(lines):
        if not ALG.match(l["t"]) or l["size"] >= 13.3:
            continue
        below = sorted([x for x in lines if x["y0"] > l["y1"]], key=lambda z: z["y0"])
        keep = []
        for x in below:
            if ALG.match(x["t"]) or STOP.match(x["t"]) or x["size"] >= 13.3 or SECT.match(x["t"]):
                break
            # 回到正文左边距 = 伪代码块结束（用锚点行左缘做参照，不写死 86pt）
            if x["x0"] < l["x0"] - 6:
                break
            if keep and x["y0"] - keep[-1]["y1"] > 40:
                break
            keep.append(x)

        def _prose(t):
            if any(c in t for c in "←∑≤≥"):
                return False
            if re.match(r"^(?:Input|Output|Initialize|Update|for|while|if|else|end)\b", t):
                return False
            if len(t.split()) < 7 or not t[:1].isupper():
                return False
            return True

        while keep and _prose(keep[-1]["t"]):
            keep.pop()
        if not keep:
            continue
        y0 = l["y0"] - 2
        y1 = max(x["y1"] for x in keep) + 3
        right = max(x["x1"] for x in keep) + 6
        clip = pymupdf.Rect(min(l["x0"], 66) - 2, y0, min(max(right, 420), page.rect.width - 12), y1)
        name = "alg_p%02d_%s.png" % (pno + 1, ALG.match(l["t"]).string.split()[1])
        path = os.path.join(OUT, name)
        page.get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=clip).save(path)
        idxs = [k for k, it in enumerate(items)
                if it.get("page") == pno + 1 and it.get("y0") is not None
                and it["y0"] < y1 and it["y1"] > y0
                and it["kind"] in ("para", "caption")]
        if not idxs:
            os.remove(path)
            continue
        first = min(idxs)
        alg_map[str(first)] = {"img": path, "w": round(clip.width, 1),
                               "h": round(clip.height, 1), "skip": idxs}
        print("p%-2d %s  y=%.0f-%.0f  x=%.0f-%.0f  items=%d"
              % (pno + 1, l["t"][:40], y0, y1, clip.x0, clip.x1, len(idxs)))

json.dump(alg_map, open(os.path.join(WORK, "alg_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0)
print("algorithms", len(alg_map))
