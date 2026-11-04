# -*- coding: utf-8 -*-
"""EQ 分支：算法块插图后补一行中文题注（英文题注已裁进图里）。"""
q = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
b = open(q, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in b else "\n"
old = ('                _pe = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=6, after=8)' + nl +
       '                _pe.add_run().add_picture(_v["img"], width=Pt(_pw))' + nl +
       '            continue')
new = ('                _pe = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=6, after=6)' + nl +
       '                _pe.add_run().add_picture(_v["img"], width=Pt(_pw))' + nl +
       '                _t0 = (it.get("text") or "").strip()' + nl +
       '                if _t0.startswith("Algorithm"):' + nl +
       '                    _pc = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, after=10, indent=0)' + nl +
       '                    style(_pc.add_run(zh.get(str(idx), _t0)), "微软雅黑", 10,' + nl +
       '                          color=RGBColor(0x40, 0x40, 0x40))' + nl +
       '            continue')
assert old in b, "eq branch anchor missing"
b = b.replace(old, new, 1)
open(q, "w", encoding="utf-8", newline="").write(b)
print("patched eq branch")
