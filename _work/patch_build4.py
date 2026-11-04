# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
s = open(p, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in s else "\n"
old = '                _nx["text"] = _t + "  " + (_nx.get("text") or "").strip()'
new = old + nl + '                if _nx.get("sents"):' + nl + '                    _nx["sents"][0] = _t + "  " + _nx["sents"][0]'
assert old in s
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("patched sents prefix")
