import glob, re, os

root = r'D:\26年美国大学生数学建模竞赛'
for year in ('2022', '2024'):
    for f in sorted(glob.glob(os.path.join(root, year, '*', '*_中文.md'))):
        t = open(f, encoding='utf-8').read()
        print(year, os.path.basename(f), len(re.findall(r'[\u4e00-\u9fff]', t)))
