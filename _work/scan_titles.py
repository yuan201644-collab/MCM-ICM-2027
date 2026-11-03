import pymupdf, glob, os, re

root = r'D:\26年美国大学生数学建模竞赛'
BAD = re.compile(r'^(Problem Chosen|For office use only|Team Control Number|Summary Sheet|Summary|20\d\d MCM/ICM|T\d|F\d|\d+$|微信公众号.*|Page \d+ of \d+|Team #)', re.I)

for year in ('2022', '2024'):
    for d in sorted(glob.glob(os.path.join(root, year, '*'))):
        if not os.path.isdir(d):
            continue
        for f in sorted(glob.glob(os.path.join(d, '*.pdf'))):
            name = os.path.basename(f)
            if name.startswith('00_'):
                continue
            doc = pymupdf.open(f)
            lines = [re.sub(r'\s+', ' ', l).strip() for l in doc[0].get_text().split('\n')]
            cand = []
            for l in lines:
                if not l or BAD.match(l) or len(l) < 12:
                    continue
                if re.match(r'^[\d\s,\.]+$', l):
                    continue
                cand.append(l)
                if len(cand) >= 2:
                    break
            print(f'{year} {os.path.basename(d)[0]} {name} :: ' + ' || '.join(cand))
