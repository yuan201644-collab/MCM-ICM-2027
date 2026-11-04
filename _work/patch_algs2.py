# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\make_algs.py"
s = open(p, encoding="utf-8").read()
old = """        if not keep:
            continue"""
new = """        def _prose(t):
            if any(c in t for c in "←∑≤≥¶"):
                return False
            if len(t.split()) < 7:
                return False
            if not t[:1].isupper():
                return False
            return not t.startswith(("Update", "if ", "else", "while", "for ", "BREAK"))

        while keep and _prose(keep[-1]["t"]):
            keep.pop()
        if not keep:
            continue"""
assert old in s
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("added prose-trim")
