import glob, re, os

root = r'D:\26年美国大学生数学建模竞赛'
txtdir = os.path.join(root, '_work', '题目原文')
num_re = re.compile(r'\d[\d,\.%/\-]*\d|\d')

for year in ('2022', '2024'):
    for txt in sorted(glob.glob(os.path.join(txtdir, f'00_{year}_*.txt'))):
        base = os.path.splitext(os.path.basename(txt))[0]
        md = glob.glob(os.path.join(root, year, '*', base + '_中文.md'))
        if not md:
            print('MISSING MD', base); continue
        src = open(txt, encoding='utf-8').read()
        dst = open(md[0], encoding='utf-8').read()
        nums = sorted(set(num_re.findall(src)))
        miss = [n for n in nums if n not in dst]
        print(f'{base}: nums={len(nums)} missing={len(miss)} -> {miss[:12]}')
