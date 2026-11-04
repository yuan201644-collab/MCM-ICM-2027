# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
s = open(p, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in s else "\n"
i = s.index('            keys = ["%d.%d" % (idx, j) for j in range(len(sents))]')
tail = "            add_eqs(idx)" + nl
j = s.index(tail, i) + len(tail)
new = nl.join([
    '            keys = ["%d.%d" % (idx, j) for j in range(len(sents))]',
    '            zh_text = "".join(zh.get(k, "") for k in keys)',
    '            has_cjk = any("\\u4e00" <= c <= "\\u9fff" for c in zh_text)',
    '            if not has_cjk:',
    '                add_en(doc, en_text, size=10.5, after=0, before=3, indent_first=0)',
    '                add_eqs(idx)',
    '                continue',
    '            add_en(doc, en_text, size=12.0, after=0, before=14,',
    '                   indent_first=0.5 if not bullet else 0, used_en=used_en)',
    '            same = zh_text.strip() == en_text.strip()',
    '            if not same:',
    '                inl = [e for e in eqs.get(str(idx), [])',
    '                       if e.get("inline") and os.path.exists(e["path"])]',
    '                add_zh(doc, zh_text, after=4, used_gloss=used_gloss, panel=True,',
    '                       indent=0.15, first_line=0.6 if not bullet else 0,',
    '                       inlines=inl or None)',
    '            add_eqs(idx)',
    '',
])
s = s[:i] + new + s[j:]
open(p, "w", encoding="utf-8", newline="").write(s)
print("rewritten")
