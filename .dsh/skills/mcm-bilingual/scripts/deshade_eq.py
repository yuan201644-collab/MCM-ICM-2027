# -*- coding: utf-8 -*-
"""把公式/伪代码裁图里的粉色水印（微信公众号水印）刷白。

只处理 eq_map.json / alg_map.json 引用的图（纯黑公式，安全）；
表格与插图不动，避免破坏配色。用法: MCM_CFG=... python deshade_eq.py
"""
import json
import os

from PIL import Image

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
WD = CFG["workdir"]

paths = []
for f in ("eq_map.json", "alg_map.json"):
    p = os.path.join(WD, f)
    if not os.path.exists(p):
        continue
    data = json.load(open(p, encoding="utf-8"))
    for v in data.values():
        for e in (v if isinstance(v, list) else [v]):
            q = e.get("path") or e.get("img")
            if q and os.path.exists(q) and q.endswith(".png"):
                paths.append(q)

done = 0
for q in sorted(set(paths)):
    im = Image.open(q).convert("RGB")
    px = im.load()
    hit = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            # 公式是纯黑字 + 灰抗锯齿（r≈g≈b）；只要偏红就是半透明水印（含极淡的 255,242,242）
            if r > 150 and r - g >= 8 and r - b >= 8:
                px[x, y] = (255, 255, 255)
                hit += 1
    if hit:
        im.save(q)
        done += 1
print("imgs", len(set(paths)), "cleaned", done)
