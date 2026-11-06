# -*- coding: utf-8 -*-
"""清掉"微信公众号：数学模型 / 微信号：MATHmodels"水印残留（items 与 zh 两侧）。

水印在 PDF 里是压在小字号 span 上的，容易被抽成"^{关注数学模型}"这种上标标记，
所以先删整段标记，再删裸串。用法: MCM_CFG=... python clean_wm.py
"""
import json
import os
import re

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
WD = CFG["workdir"]

WM = (r"(?:微\s*信\s*公\s*众\s*号\s*[：:]?\s*|微\s*信\s*号\s*[：:]?\s*)?"
      r"(?:数\s*学\s*模\s*型|数\s*字\s*模\s*型|MATHmodels?|MATmodels?)"
      r"|获\s*取\s*更\s*多\s*资\s*讯")
MARKED = re.compile(r"[\^_]\{\s*(?:%s)\s*\}" % WM)
BARE = re.compile(WM)
# 水印被切剩的半截：“关注 2”“关注 from player 1”“^{关注}”
HALF_MARKED = re.compile(r"[\^_]\{\s*关\s*注\s*\}")
HALF_BARE = re.compile(r"(?<![\u4e00-\u9fff])关\s*注(?=\s*(?:\d|[A-Za-z]))")


def clean(s):
    if not isinstance(s, str):
        return s
    s = MARKED.sub("", s)
    s = BARE.sub("", s)
    s = HALF_MARKED.sub("", s)
    s = HALF_BARE.sub("", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\s+([，。；：、])", r"\1", s)
    return s.strip()


items_p = os.path.join(WD, "items_full.json")
zh_p = os.path.join(WD, "zh_full.json")
items = json.load(open(items_p, encoding="utf-8"))
zh = json.load(open(zh_p, encoding="utf-8"))

n_i = n_z = n_blank = 0
for it in items:
    t = it.get("text")
    if not t:
        continue
    nt = clean(t)
    if nt != t:
        n_i += 1
        it["text"] = nt
        if "sents" in it and isinstance(it["sents"], list):
            it["sents"] = [x for x in (clean(s) for s in it["sents"]) if x]
        if not nt:
            it.update({"kind": "img", "path": "", "sents": []})
            n_blank += 1

for k, v in list(zh.items()):
    if isinstance(v, str):
        nv = clean(v)
        if nv != v:
            n_z += 1
            if nv:
                zh[k] = nv
            else:
                del zh[k]

json.dump(items, open(items_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(zh, open(zh_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("items cleaned %d (blanked %d), zh cleaned %d" % (n_i, n_blank, n_z))
