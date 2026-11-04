# -*- coding: utf-8 -*-
import re

path = r"D:\26年美国大学生数学建模竞赛\_work\全文\2022B_2200084.txt"
raw = open(path, encoding="utf-8").read()
pages = re.split(r"<<<PAGE (\d+)>>>", raw)
blocks = [(int(pages[i]), pages[i + 1]) for i in range(1, len(pages) - 1, 2)]

for pno, txt in blocks:
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    print(f"--- p{pno} ---")
    print(" | ".join(lines[:6])[:260])

print("=" * 20, "TERM HITS")
terms = ["linear programming", "auction", "marginal utility", "IPV", "sensitivity",
         "Sankey", "Time-varying", "Pareto", "grid", "Monte Carlo", "regression"]
for t in terms:
    hits = [p for p, x in blocks if t.lower() in x.lower()]
    print(f"{t:22s} {hits[:8]}")
