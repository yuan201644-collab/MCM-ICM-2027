import pymupdf, glob, os, re

root = r'D:\26年美国大学生数学建模竞赛'
out = os.path.join(root, '_work', '摘要合集.txt')
buf = []

BAD = re.compile(r'^(Problem Chosen|For office use only|Team Control Number|Summary Sheet|Summary|20\d\d MCM/ICM|T\d|F\d|\d+$|Page \d+ of \d+|Team #|微信号：MATHmodels)', re.I)

for year in ('2022', '2024'):
    for d in sorted(glob.glob(os.path.join(root, year, '*'))):
        if not os.path.isdir(d):
            continue
        for f in sorted(glob.glob(os.path.join(d, '*.pdf'))):
            name = os.path.basename(f)
            if name.startswith('00_'):
                continue
            doc = pymupdf.open(f)
            t = re.sub(r'\s+', ' ', doc[0].get_text()).strip()
            t = re.sub(r'微信号：MATHmodels', '', t)
            t = re.sub(r'(Problem Chosen\s*[A-F]|Team Control Number\s*\d{5,7}|For office use only.*?F4|20\d\d MCM/ICM Summary Sheet|Summary Sheet)', '', t)
            t = re.sub(r'\s+', ' ', t).strip()
            buf.append(f'### {year} {os.path.basename(d)[0]} {name[:-4]} [{len(doc)}p]')
            buf.append(t[:760])
            buf.append('')

open(out, 'w', encoding='utf-8').write('\n'.join(buf))
print('entries', len(buf)//3, 'chars', os.path.getsize(out))
