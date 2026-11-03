import glob, os, re, csv

root = r'D:\26年美国大学生数学建模竞赛'
files = sorted(glob.glob(os.path.join(root, '_work', '全文', '*.txt')))

PAT = {
    '备忘录': r'memorand|memorandum|\bmemo\b',
    '信': r'letter to|dear (madam|sir|congressm|governor|mayor|citizen|resident|community)|open letter',
    '两页/一页指导': r'two-page|one-page|two page|one page|2-page|1-page',
    '新闻稿': r'newspaper|press release|blog post',
}

rows = []
for f in files:
    txt = open(f, encoding='utf-8').read()
    hits = []
    for k, pat in PAT.items():
        c = len(re.findall(pat, txt, re.I))
        if c:
            hits.append(f'{k}{c}')
    rows.append([os.path.basename(f)[:-4], '、'.join(hits)])

with open(os.path.join(root, '_work', '交付物.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t')
    w.writerow(['文件', '交付物'])
    w.writerows(rows)
print('done', len(rows))
