import glob, os, re, csv

root = r'D:\26年美国大学生数学建模竞赛'
files = sorted(glob.glob(os.path.join(root, '_work', '全文', '*.txt')))
rows = []

NUM = re.compile(r'^\s*(\d{1,2})(\.\d{1,2})*\.?\s+([A-Z].{2,70})$')
ALLC = re.compile(r'^\s*([A-Z][A-Z &\-]{3,60})\s*$')

top = []
for f in files:
    name = os.path.basename(f)[:-4]
    txt = open(f, encoding='utf-8').read()
    heads = []
    for line in txt.split('\n'):
        line = line.strip()
        if not line or len(line) > 80:
            continue
        m = NUM.match(line)
        if m and '.' not in (m.group(2) or ''):
            heads.append(f'{m.group(1)}. {m.group(3).strip()}')
            continue
        m2 = ALLC.match(line)
        if m2 and len(heads) < 3:
            heads.append(m2.group(1).strip())
    rows.append((name, ' > '.join(heads[:14]), len(heads)))

with open(os.path.join(root, '_work', '结构指纹.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t')
    w.writerow(['文件', '一级标题序列', '标题数'])
    w.writerows(rows)

for r in rows:
    print(r[0], '|', r[1][:150])
