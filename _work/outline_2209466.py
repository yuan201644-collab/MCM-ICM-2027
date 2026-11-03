# -*- coding: utf-8 -*-
"""抽取 2209466 的各级标题（按字号/加粗/编号模式）。"""
import pymupdf, json, collections

PDF = r'D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022A_2209466_自行车功率曲线\2209466.pdf'
doc = pymupdf.open(PDF)

# 1) 统计正文字号
sizes = collections.Counter()
for page in doc:
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            for s in l['spans']:
                t = s['text'].strip()
                if len(t) > 20:
                    sizes[round(s['size'], 1)] += len(t)
body = sizes.most_common(1)[0][0]
print('body size =', body, ' pages =', doc.page_count)

# 2) 找标题候选：字号 >= body+1 或加粗且短
cands = []
for pno, page in enumerate(doc, 1):
    for b in page.get_text('dict')['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            text = ''.join(s['text'] for s in l['spans']).strip()
            if not text or len(text) > 90:
                continue
            mx = max(s['size'] for s in l['spans'])
            bold = any(s['flags'] & 16 for s in l['spans'])
            if mx >= body + 1.0 or (bold and mx >= body):
                cands.append((pno, round(mx, 1), bold, text))

print('candidates =', len(cands))
for c in cands:
    print(c[0], c[1], 'B' if c[2] else '-', c[3])
