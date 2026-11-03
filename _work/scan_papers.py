import pymupdf, glob, os, re, csv

root = r'D:\26年美国大学生数学建模竞赛'
out = os.path.join(root, '_work', '候选表.tsv')
rows = []

def clean(t):
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

for year in ('2022', '2024'):
    for d in sorted(glob.glob(os.path.join(root, year, '*'))):
        if not os.path.isdir(d):
            continue
        folder = os.path.basename(d)
        tcode = folder[0]
        for f in sorted(glob.glob(os.path.join(d, '*.pdf'))):
            name = os.path.basename(f)
            if name.startswith('00_'):
                continue
            try:
                doc = pymupdf.open(f)
            except Exception as e:
                rows.append([year, tcode, folder, name, 'ERR', '', '', '', str(e)])
                continue
            pages = len(doc)
            txt = '\n'.join(p.get_text() for p in doc)
            nfig = len(re.findall(r'Figure\s*\d', txt))
            ntab = len(re.findall(r'Table\s*\d', txt))
            has_code = 'Appendix' in txt or 'Code' in txt
            p1 = clean(doc[0].get_text())
            # 去掉摘要页表头
            p1 = re.sub(r'For office use only.*?T1\s*F1\s*T2\s*F2\s*T3\s*F3\s*T4\s*F4', ' ', p1, flags=re.S|re.I)
            p1 = re.sub(r'Team Control Number.*?Problem Chosen', ' ', p1, flags=re.S|re.I)
            rows.append([year, tcode, folder, name, pages, round(os.path.getsize(f)/1024),
                         nfig, ntab, ('Y' if has_code else 'N'), p1[:200]])

with open(out, 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t')
    w.writerow(['年', '题', '文件夹', '文件', '页数', 'KB', '图', '表', '附录', '摘要开头'])
    for r in rows:
        w.writerow(r)
print('rows', len(rows))
for r in rows:
    print(f'{r[0]} {r[1]} {r[3]:<14} p={r[4]:<3} fig={r[6]:<3} tab={r[7]:<3} code={r[8]} | {r[9][:110]}')
