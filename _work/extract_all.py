import pymupdf, glob, os, re

root = r'D:\26年美国大学生数学建模竞赛'
outdir = os.path.join(root, '_work', '全文')
os.makedirs(outdir, exist_ok=True)
n = 0
for year in ('2022', '2024'):
    for d in sorted(glob.glob(os.path.join(root, year, '*'))):
        if not os.path.isdir(d):
            continue
        t = os.path.basename(d)[0]
        for f in sorted(glob.glob(os.path.join(d, '*.pdf'))):
            name = os.path.basename(f)
            if name.startswith('00_'):
                continue
            cid = name[:-4]
            out = os.path.join(outdir, f'{year}{t}_{cid}.txt')
            if os.path.exists(out):
                continue
            doc = pymupdf.open(f)
            parts = []
            for i, p in enumerate(doc, 1):
                txt = p.get_text()
                txt = re.sub(r'Team # \d+\s*Page \d+ of \d+', '', txt)
                parts.append(f'\n<<<PAGE {i}>>>\n' + txt)
            open(out, 'w', encoding='utf-8').write(''.join(parts))
            n += 1
print('extracted', n)
