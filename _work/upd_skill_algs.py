# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\SKILL.md"
s = open(p, encoding="utf-8").read()
add = """
- **伪代码块（Algorithm N）也会被拆成碎片**：行号、`←`、上下标各成一行，正文里出现
  `2 > h_lowestdo` / `2t1 ← t · Δt` / `Update: V (t+1)` 这种残片，且中英文各重复一遍。
  `scripts/make_algs.py` 以 `Algorithm N:` 为锚点整块裁图（裁切时**把英文题注一起裁进去**），
  `work/alg_map.json` 与 `eq_map.json` 同构，`build.py` 已一并读取并在图片下方补中文题注。
  裁剪边界经验：`x0 < 86` 视为正文行、行间距 `> 40pt` 断开、末尾再剪掉"首字母大写 + ≥7 词"的散文行。
"""
s = s.rstrip() + "\n" + add
open(p, "w", encoding="utf-8").write(s)
print("skill updated with make_algs")
