import csv, os
p = r'D:\26年美国大学生数学建模竞赛\_work\候选表.tsv'
rows = list(csv.reader(open(p, encoding='utf-8'), delimiter='\t'))[1:]
cur = None
for r in rows:
    key = f'{r[0]} {r[1]}'
    if key != cur:
        print('\n' + '='*8, key, r[2])
        cur = key
    print(f'  {r[3]:<13} p{r[4]:<3} 图{r[6]:<2} 表{r[7]:<2} 附{r[8]} | {r[9][:95]}')
