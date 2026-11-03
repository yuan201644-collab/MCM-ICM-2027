# -*- coding: utf-8 -*-
import io, re, sys

src = io.open(r"D:\26年美国大学生数学建模竞赛\_work\build_tsv.py", encoding="utf-8").read()
rows = re.search(r'ROWS = """(.*?)"""', src, re.S).group(1).strip().split("\n")
print("rows:", len(rows))
bad_total = 0
for i, ln in enumerate(rows, 1):
    r = ln.split("|")
    if len(r) != 8:
        print(i, "FIELDCOUNT", len(r)); bad_total += 1; continue
    t, m, f = r[3], r[4], r[5]
    bad = []
    if len(t) > 20: bad.append(("title", len(t), t))
    if len(m) > 20: bad.append(("method", len(m), m))
    if len(f) > 40: bad.append(("feat", len(f), f))
    if bad:
        bad_total += len(bad)
        print(i, r[1], r[2], bad)
print("violations:", bad_total)
