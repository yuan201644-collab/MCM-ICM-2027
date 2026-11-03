import pymupdf, glob, os, sys

root = r'D:\26年美国大学生数学建模竞赛'
year = sys.argv[1] if len(sys.argv) > 1 else '2022'
outdir = os.path.join(root, '_work', '题目原文')
os.makedirs(outdir, exist_ok=True)

files = sorted(glob.glob(os.path.join(root, year, '*', '00_*.pdf')))
for f in files:
    doc = pymupdf.open(f)
    txt = '\n'.join(p.get_text() for p in doc)
    base = os.path.splitext(os.path.basename(f))[0]
    out = os.path.join(outdir, base + '.txt')
    with open(out, 'w', encoding='utf-8') as fh:
        fh.write(txt)
    print('#####', base, 'pages=', len(doc), 'chars=', len(txt))
    print(txt)
    print()
