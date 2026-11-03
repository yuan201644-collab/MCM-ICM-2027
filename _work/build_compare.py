import csv, os

root = r'D:\26年美国大学生数学建模竞赛'
W = os.path.join(root, '_work')

cand = list(csv.reader(open(os.path.join(W, '候选表.tsv'), encoding='utf-8'), delimiter='\t'))[1:]
sig = {(r[0], r[1], r[2].replace('.pdf', '')): r for r in
       list(csv.reader(open(os.path.join(W, '方法指纹.tsv'), encoding='utf-8'), delimiter='\t'))[1:]}
summ = list(csv.reader(open(os.path.join(W, '摘要概览.tsv'), encoding='utf-8'), delimiter='\t'))[1:]
dlv = dict((r[0], r[1]) for r in
           list(csv.reader(open(os.path.join(W, '交付物.tsv'), encoding='utf-8'), delimiter='\t'))[1:])
cand_m = {(r[0], r[1], r[3].replace('.pdf', '')): r for r in cand}

STAR = {'2209466', '2200084', '2203120', '2215444', '2223495', '2224021',
        '2400996', '2419984', '2401298', '2429211', '2413552', '2409949'}

FOLDER = {}
for y in ('2022', '2024'):
    for d in os.listdir(os.path.join(root, y)):
        if os.path.isdir(os.path.join(root, y, d)):
            FOLDER[(y, d[0])] = d

def skeleton(s):
    secs = s[6] if s else ''
    n = sum(1 for k in ('假设', '符号', '敏感性', '优缺点') if k in secs)
    return f'{n}/4'

out = ['# 79 篇 O 奖论文候选对比', '',
       '你的三条偏好：**方法代表性 + 交付物齐全（备忘录/信/两页指导）+ 有代码附录**。',
       '- 「附」= 含 Appendix/Code；「物」= 含备忘录/信/两页指导/新闻稿；',
       '- 「架」= 框架完整度（假设/符号/敏感性/优缺点 各 1 分，满分 4）；★ = 我按"方法代表性"推荐。',
       '- 结论：**三条全中的共 15 篇**，全部落在 2022 C（6 篇）、2024 C（5 篇）、2024 D（2 篇）、2024 F（2 篇）；其余 8 个类别（2022 A/B/D/E/F、2024 A/B/E）没有一篇三者兼得，只能在"附录"与"交付物"之间取舍。', '']
triple = []
for y in ('2022', '2024'):
    for t in 'ABCDEF':
        out.append(f'## {y} {t} · {FOLDER.get((y, t), "?")}')
        out.append('')
        out.append('| 控制号 | 页 | 图/表 | 架 | 附 | 物 | 中文标题 | 核心方法 | 一句话特色 |')
        out.append('|:--:|:--:|:--:|:--:|:--:|:--:|---|---|---|')
        for r in summ:
            if r[0] != y or r[1] != t:
                continue
            cid = r[2]
            c = cand_m.get((y, t, cid), [''] * 10)
            code = 'Y' if c[8] == 'Y' else ''
            d = dlv.get(f'{y}{t}_{cid}', '')
            mark = '★' if cid in STAR else ''
            if code == 'Y' and d:
                triple.append(f'{y}{t}_{cid}')
            out.append(f'| {mark}{cid} | {c[4]} | {c[6]}/{c[7]} | {skeleton(sig.get((y, t, cid)))} | {code} | {d} | {r[3]} | {r[4]} | {r[5]} |')
        out.append('')

out += ['## 三条偏好全中的论文', '',
        '、'.join(triple) + f'（共 {len(triple)} 篇）', '']

open(os.path.join(root, '研读材料', '79篇候选对比.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('triple', triple)
