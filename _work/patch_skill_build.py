# -*- coding: utf-8 -*-
"""把 build.py 里两处论文专属的中文注改成读配置。"""
import io
import os

p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
s = io.open(p, encoding="utf-8").read()

old_fig = '''        if "Figure 11" in cap_txt:
            note = "（图中标签：Type 类型；Sprinter 冲刺手；Time Trial Specialist 个人计时赛选手；Tokyo 东京；Belgium 比利时；Own design 自主设计赛道。）"'''
new_fig = '''        if cap_txt in FIG_NOTE_KEYS:
            note = FIG_NOTE'''
assert old_fig in s, "figure note block not found"
s = s.replace(old_fig, new_fig)

# 在 add_fig_block 之前放一个 key 集合
anchor = "    def add_fig_block(info):"
assert anchor in s
s = s.replace(anchor, "    FIG_NOTE_KEYS = set(CFG.get(\"figure_note_for\", []))\n\n" + anchor, 1)

# 表 1 的中文注也改成配置（原来写死在 build 里）
io.open(p, "w", encoding="utf-8").write(s)
print("patched build.py")
