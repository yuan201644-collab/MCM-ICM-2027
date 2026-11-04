# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\make_eqs.py"
s = open(p, encoding="utf-8").read()
old = "if len(l[\"t\"].split()) <= 14 and not (l[\"t\"].endswith(\".\") and len(l[\"t\"].split()) >= 4):"
new = "if len(l[\"t\"].split()) <= 26 and not (l[\"t\"].endswith(\".\") and len(l[\"t\"].split()) >= 6):"
assert old in s
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("eq word limit 14 -> 26")
