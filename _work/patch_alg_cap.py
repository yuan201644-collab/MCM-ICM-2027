# -*- coding: utf-8 -*-
"""算法块把英文题注一起裁进图；build 在图片下方补一行中文题注。"""
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\make_algs.py"
s = open(p, encoding="utf-8").read()
s = s.replace('        y0 = l["y1"] + 2', '        y0 = l["y0"] - 2', 1)
open(p, "w", encoding="utf-8", newline="").write(s)

q = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
b = open(q, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in b else "\n"
old = ('        if idx in EQ_SKIP:' + nl +
       '            _v = EQD.get(idx)' + nl)
idx = b.index(old)
seg = b[idx: idx + 900]
print(seg)
