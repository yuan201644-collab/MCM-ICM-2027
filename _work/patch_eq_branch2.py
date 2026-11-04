# -*- coding: utf-8 -*-
q = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
b = open(q, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in b else "\n"
old = ('                _t0 = (it.get("text") or "").strip()' + nl +
       '                if _t0.startswith("Algorithm"):' + nl +
       '                    _pc = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=10, indent=0)' + nl +
       '                    style(_pc.add_run(zh.get(str(idx), _t0)), "微软雅黑", 10,' + nl +
       '                          color=RGBColor(0x40, 0x40, 0x40))')
new = ('                _t0 = (it.get("text") or "").strip()' + nl +
       '                _cz = (zh.get(str(idx), "") or "").strip()' + nl +
       '                if _t0.startswith("Algorithm") and _cz and _cz != _t0:' + nl +
       '                    _pc = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=10, indent=0)' + nl +
       '                    style(_pc.add_run(_cz), "微软雅黑", 10,' + nl +
       '                          color=RGBColor(0x40, 0x40, 0x40))')
assert old in b, "anchor missing"
b = b.replace(old, new, 1)
open(q, "w", encoding="utf-8", newline="").write(b)
print("skip duplicate caption line")
