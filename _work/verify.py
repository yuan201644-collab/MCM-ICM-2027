# -*- coding: utf-8 -*-
"""Final consistency check: order vs source file, encoding, cell hygiene."""
import io, re, sys

ROOT = r"D:\26年美国大学生数学建模竞赛\_work"
sys.stdout.reconfigure(encoding="utf-8")

src = io.open(ROOT + r"\摘要合集.txt", encoding="utf-8").read().split("\n")
order = []
for ln in src:
    m = re.match(r"### (\d{4}) ([A-F]) (\d{7}) \[(\d+)p\]", ln.strip())
    if m:
        order.append((m.group(1), m.group(2), m.group(3)))
print("source headers:", len(order))

raw = io.open(ROOT + r"\摘要概览.tsv", "rb").read()
print("BOM:", raw[:3] == b"\xef\xbb\xbf", "bytes:", len(raw), "CRLF:", b"\r\n" in raw)
lines = io.open(ROOT + r"\摘要概览.tsv", encoding="utf-8").read().rstrip("\n").split("\n")
rows = [ln.split("\t") for ln in lines[1:]]
print("rows:", len(rows), "field counts:", sorted({len(r) for r in rows}))

bad = 0
for i, (r, (y, p, cid)) in enumerate(zip(rows, order), 1):
    if (r[0], r[1], r[2]) != (y, p, cid):
        bad += 1
        print("ORDER MISMATCH row", i, (r[0], r[1], r[2]), "expected", (y, p, cid))
    for j, cell in enumerate(r):
        if cell != cell.strip() or "\r" in cell or "  " in cell:
            print("HYGIENE row", i, "col", j, repr(cell))
    if r[6] not in ("是", "否", "?"):
        print("BAD deliverable flag row", i, repr(r[6]))
print("order mismatches:", bad)
print("deliverable counts:", {v: sum(1 for r in rows if r[6] == v) for v in ("是", "否", "?")})
print("rows with 备注:", sum(1 for r in rows if r[7]))
print("rows with 摘要未明示:", [r[2] for r in rows if r[4] == "摘要未明示"])
print("\n-- patched rows --")
for r in rows:
    if r[2] in ("2204883", "2229059", "2208928", "2216618", "2407038"):
        print(" | ".join(r))
print("\n-- max lengths --", max(len(r[3]) for r in rows), max(len(r[4]) for r in rows), max(len(r[5]) for r in rows))
