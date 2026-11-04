# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\make_algs.py"
s = open(p, encoding="utf-8").read()
s = s.replace('if keep and x["y0"] - keep[-1]["y1"] > 24:', 'if keep and x["y0"] - keep[-1]["y1"] > 40:', 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("gap threshold 40")
