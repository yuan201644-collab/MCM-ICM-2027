# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\SKILL.md"
s = open(p, encoding="utf-8").read()
add = """
- **上下标会丢**：PDF 里 `v_ij^(t)`、`S_i`、`β_i` 是“小字号 + 基线偏移”的独立 span，直接拼接文本会被拍平成 `v(t)ij`、`Si`。
  `extract.py` 已按“字号 ≤ 行内最大字号×0.82 且基线抬高/下移 >0.6pt”输出 `^{...}` / `_{...}` 标记，
  `build.py` 的 `_emit()` 再把标记渲染成真正的上/下标 run。
  **注意**：改抽取会改变 item 下标，必须用文本匹配把旧 `zh_full.json` 重新映射
  （`_work/remap_zh2.py` 的做法：heading/caption 的 key 是 `str(idx)`，para 的 key 是 `"%d.%d"`，两侧都要按 kind 取对）。
"""
s = s.rstrip() + "\n" + add
open(p, "w", encoding="utf-8").write(s)
print("skill updated")
