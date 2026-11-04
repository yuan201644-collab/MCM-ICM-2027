# -*- coding: utf-8 -*-
"""给 extract.py 增加上下标标记；给 build.py 增加上下标渲染。"""
import re

# ---------- extract.py ----------
pe = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\extract.py"
s = open(pe, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in s else "\n"
old = '        txt = "".join(s["text"] for s in spans).strip()'
assert old in s, "extract anchor missing"
new = nl.join([
    '        _base = max(spans, key=lambda z: z["size"])',
    '        _bsz, _by = _base["size"], _base["origin"][1]',
    '',
    '        def _mk(sp):',
    '            t2 = sp["text"]',
    '            if not t2.strip():',
    '                return t2',
    '            if sp["size"] <= _bsz * 0.82:',
    '                dy = sp["origin"][1] - _by',
    '                if dy < -0.6:',
    '                    return "^{" + t2.strip() + "}"',
    '                if dy > 0.6:',
    '                    return "_{" + t2.strip() + "}"',
    '            return t2',
    '',
    '        txt = "".join(_mk(s) for s in spans).strip()',
])
s = s.replace(old, new, 1)
open(pe, "w", encoding="utf-8", newline="").write(s)
print("extract patched")

# ---------- build.py ----------
pb = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
b = open(pb, encoding="utf-8").read()
old2 = '    for seg, is_term in segs:' + nl + '        if not seg:' + nl + '            continue' + nl + \
       '        style(p.add_run(seg), "Times New Roman", size, bold=bold,' + nl + \
       '              color=GLOSS_BLUE if is_term else None)'
assert old2 in b, "build anchor missing"
new2 = nl.join([
    '    for seg, is_term in segs:',
    '        if not seg:',
    '            continue',
    '        _emit(p, seg, size, bold, GLOSS_BLUE if is_term else None)',
])
b = b.replace(old2, new2, 1)

helper = nl.join([
    'SUPSUB = re.compile(r"([\\^_])\\{([^}]*)\\}")',
    '',
    '',
    'def _emit(p, text, size, bold, color):',
    '    pos = 0',
    '    for m in SUPSUB.finditer(text):',
    '        if m.start() > pos:',
    '            style(p.add_run(text[pos:m.start()]), "Times New Roman", size, bold=bold, color=color)',
    '        r = style(p.add_run(m.group(2)), "Times New Roman", size, bold=bold, color=color)',
    '        if m.group(1) == "^":',
    '            r.font.superscript = True',
    '        else:',
    '            r.font.subscript = True',
    '        pos = m.end()',
    '    if pos < len(text):',
    '        style(p.add_run(text[pos:]), "Times New Roman", size, bold=bold, color=color)',
    '',
    '',
])
anchor = 'def add_en(doc, text, size=12.0, bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,'
b = b.replace(anchor, helper + anchor, 1)
open(pb, "w", encoding="utf-8", newline="").write(b)
print("build patched")
