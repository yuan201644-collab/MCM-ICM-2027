# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
s = open(p, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in s else "\n"
old = ('        elif kind == "caption":' + nl +
       '            txt = sents[0] if sents else it.get("text", "")' + nl +
       '            add_en(doc, txt, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, before=3, after=0)')
new = ('        elif kind == "caption":' + nl +
       '            txt = sents[0] if sents else it.get("text", "")' + nl +
       '            _cp = add_en(doc, txt, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, before=3, after=0)' + nl +
       '            if (idx + 1) in EQD:' + nl +
       '                _cp.paragraph_format.keep_with_next = True')
assert old in s, "caption anchor missing"
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("caption keeps with block image")
