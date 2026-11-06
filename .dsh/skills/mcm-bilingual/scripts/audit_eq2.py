# -*- coding: utf-8 -*-
"""精确公式审计：逐个核对原 PDF 里每个右缘公式编号 (N)。

判定「公式没丢」的条件：该编号所在行对应的 item 被 eq_map / alg_map /
table_map / fig_map 的 skip 覆盖（说明整块被裁成图了）。
未被覆盖 = 公式在成品里只剩文字碎片，属于真丢失。

用法: python audit_eq2.py                    # 扫当前目录下所有 paper.json
      python audit_eq2.py <dir> [<dir>...]
"""
import json
import os
import re
import glob
import sys

import pymupdf

NUM_ONLY = re.compile(r"^\s*\((\d{1,3})\)\s*$")
NUM_TAIL = re.compile(r"\(\s*(\d{1,3})\s*\)\s*$")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def audit(root):
    cfg_p = os.path.join(root, "paper.json")
    if not os.path.exists(cfg_p):
        return None
    cfg = load(cfg_p)
    wd = cfg["workdir"]
    ip = os.path.join(wd, "items_full.json")
    if not os.path.exists(ip):
        return None
    items = load(ip)
    doc = pymupdf.open(cfg["pdf"])

    covered = set()
    n_imgs = 0
    legacy_keys = set()   # 旧格式：整式图直接挂在条目号上（无 skip）
    legacy = False
    for f in ("eq_map.json", "alg_map.json", "table_map.json", "fig_map.json"):
        p = os.path.join(wd, f)
        if not os.path.exists(p):
            continue
        for k, v in load(p).items():
            vs = v if isinstance(v, list) else [v]
            # 旧格式：公式图直接挂在条目号上（add_eqs(idx) 读取），无 skip 字段
            if str(k).isdigit():
                covered.add(int(k))
            for e in vs:
                if not isinstance(e, dict):
                    continue
                n_imgs += 1
                covered.update(e.get("skip", []))
                if e.get("inline") is not None and "skip" not in e:
                    legacy = True
                    if str(k).isdigit() and not e.get("inline"):
                        legacy_keys.add(int(k))
            if isinstance(v, dict) and "skip" in v:
                covered.add(int(k))

    missing = []
    near_hit = 0     # 旧格式里公式图挂在相邻条目（±3），不算丢失
    total = 0
    pages = [x + 1 for x in cfg["pages"]]
    for pno in pages:
        if pno - 1 >= doc.page_count:
            continue
        page = doc[pno - 1]
        for b in page.get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for l in b["lines"]:
                t = "".join(s["text"] for s in l["spans"]).strip()
                m = NUM_ONLY.match(t) or NUM_TAIL.match(t)
                if not m:
                    continue
                if l["bbox"][2] < page.rect.width - 130:
                    continue
                total += 1
                y0, y1 = l["bbox"][1], l["bbox"][3]
                hits = [i for i, it in enumerate(items)
                        if it.get("page") == pno and it.get("y0") is not None
                        and it["y0"] < y1 + 4 and it["y1"] > y0 - 4]
                if not hits:
                    # 行本身没抽成 item（通常是纯矢量公式），不算丢失
                    continue
                # 编号若没抽成独立文字条目（只有重叠的长正文段落），
                # 说明编号连同公式一起在图里，不该把正文段落误判成"漏掉的编号"。
                numtag = "(%d)" % int(m.group(1))
                real = [i for i in hits
                        if NUM_ONLY.match((items[i].get("text") or "").strip())
                        or (len((items[i].get("text") or "").strip()) <= 22
                            and numtag in (items[i].get("text") or ""))]
                if not real:
                    continue
                if any(i in covered for i in hits):
                    continue
                # 旧脚本把整式图挂在相邻条目上（编号与公式相隔 1~3 条），
                # 公式实际已渲染，只是没有 skip 字段，不算丢失。
                if legacy and any(abs(k - i) <= 3 for k in legacy_keys for i in hits):
                    near_hit += 1
                    continue
                missing.append((pno, int(m.group(1)), t[:40]))
    name = os.path.basename(root.rstrip("/\\"))
    print("%-30s 编号 %-3d 公式图 %-3d 真丢失 %-3d 旧格式邻近挂载 %-2d %s" %
          (name[:30], total, n_imgs, len(missing), near_hit,
           missing[:8] if missing else ""))
    return name, total, n_imgs, missing


if __name__ == "__main__":
    roots = sys.argv[1:] or sorted(
        os.path.dirname(p) for p in glob.glob("*/paper.json"))
    tot = mis = 0
    for r in roots:
        out = audit(r)
        if out:
            tot += out[1]
            mis += len(out[3])
    print("\n合计：右缘编号 %d 个，未被公式图覆盖 %d 个" % (tot, mis))
