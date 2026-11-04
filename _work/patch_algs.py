# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\make_algs.py"
s = open(p, encoding="utf-8").read()
s = s.replace('if x["x0"] < 90:', 'if x["x0"] < 86:', 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("threshold set to 86")
