# -*- coding: utf-8 -*-
"""把 12 篇研读论文 + 对应赛题原文 + 中文译文，按一一对应整理到 研读材料/12篇研读/"""
import shutil
from pathlib import Path

ROOT = Path(r'D:\26年美国大学生数学建模竞赛')
OUT = ROOT / '研读材料' / '12篇研读'

PICKS = [
    ('2022', 'A', '2209466'),
    ('2022', 'B', '2200084'),
    ('2022', 'C', '2203120'),
    ('2022', 'D', '2215444'),
    ('2022', 'E', '2223495'),
    ('2022', 'F', '2224021'),
    ('2024', 'A', '2400996'),
    ('2024', 'B', '2419984'),
    ('2024', 'C', '2401298'),
    ('2024', 'D', '2429211'),
    ('2024', 'E', '2413552'),
    ('2024', 'F', '2409949'),
]

REASON = {
    '2022A': '疲劳生理模型 + 有氧/无氧双路径能量模型，机理路线最正，带代码附录',
    '2022B': '拍卖机制 + 边际效用定价，全类唯一有机制设计，带附录',
    '2022C': 'ARIMA 预测 → 动态规划 → 回测，标准五步，附备忘录',
    '2022D': '扎根理论筛指标，示范无数据题怎么建体系',
    '2022E': '微分方程 + 多目标 + 演化博弈，差异化最大，带附录',
    '2022F': '自建 HELEN 五维指标体系，体系自洽，带附录',
    '2024A': '分龄种群迭代 + BDS 评估，骨架最干净',
    '2024B': '四阶 RK + 分场景搜索，结构取胜',
    '2024C': '双时间贝叶斯 + 假设检验，先证动量存在再建模',
    '2024D': '多粒度动态坝模型，最像可交付的决策工具',
    '2024E': 'MGWR 刻画空间异质性，方法最新',
    '2024F': '逻辑框架法 LFA + 764 个项目数据，交付物最全',
}

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

lines = ['# 12 篇研读材料（一一对应）', '',
         '每篇一个文件夹：赛题原文 PDF + 中文译文 MD + O 奖论文 PDF。', '']

for year, t, cid in PICKS:
    src_dir = next(p for p in (ROOT / year).iterdir() if p.is_dir() and p.name.startswith(t + '-'))
    title = src_dir.name.split('-', 1)[1].replace('(题)', '')
    dst = OUT / f'{year}{t}_{cid}_{title}'
    dst.mkdir()

    prob_pdf = next(src_dir.glob('00_*.pdf'))
    prob_md = next(src_dir.glob('00_*_中文.md'))
    paper = src_dir / f'{cid}.pdf'
    assert paper.exists(), paper

    shutil.copy2(prob_pdf, dst / prob_pdf.name)
    shutil.copy2(prob_md, dst / prob_md.name)
    shutil.copy2(paper, dst / paper.name)

    lines.append(f'## {year} {t} · {title}')
    lines.append('')
    lines.append(f'- 论文：`{cid}.pdf`（O 奖）')
    lines.append(f'- 赛题：`{prob_pdf.name}`')
    lines.append(f'- 译文：`{prob_md.name}`')
    lines.append(f'- 选它的理由：{REASON[year + t]}')
    lines.append('')
    print('OK', dst.name, [p.name for p in sorted(dst.iterdir())])

(OUT / '清单.md').write_text('\n'.join(lines), encoding='utf-8')
print('total dirs', len(list(OUT.iterdir())) - 1)
