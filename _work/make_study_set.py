import os, shutil, csv

root = r'D:\26年美国大学生数学建模竞赛'
dst = os.path.join(root, '研读材料')
os.makedirs(dst, exist_ok=True)

picks = [
    ('2022', 'A', 'A-自行车功率曲线(题)', '2209466',
     'Optimal Power Distribution of a Cyclist', 25, 30, 15, 'Y',
     '最优控制（能量/疲劳模型→单目标规划）', '有目录+代码附录，Pontryagin 思路最标准'),
    ('2022', 'B', 'B-水资源与水电共享(题)', '2200084',
     'A Model for Better Use of Water Resources Based on Marginal Utility and Auction Theory', 24, 17, 3, 'Y',
     '资源分配网络+边际效用+拍卖理论', '把"分水"变成经济学模型，附录有代码'),
    ('2022', 'C', 'C-交易策略(题)', '2203120',
     'Trading Strategy Model Based on Dynamic Programming', 24, 22, 10, 'Y',
     'ARIMA 预测 + 动态规划求最优策略', 'C 题最经典套路：预测+DP+回测'),
    ('2022', 'D', 'D-数据瘫痪？用我们的分析(题)', '2215444',
     'How Can We Realize the Full Potential of Our Data?', 22, 15, 5, 'N',
     '扎根理论筛指标 + 系统动力学仿真', '没数据也能建指标体系的示范'),
    ('2022', 'E', 'E-森林碳汇(题)', '2223495',
     'Letting "Carbon" Stay: Forest Management for Ecological-Economic Balance', 25, 3, 5, 'Y',
     '微分方程碳循环 + 多目标规划 + 演化博弈', 'E 题"生态-经济"双目标的完整链条'),
    ('2022', 'F', 'F-人人为我，太空为我(题)', '2224021',
     'Harvest in Space! Outlook & Equity', 25, 20, 5, 'Y',
     '五维指标 HELEN + 评价模型 + 情景分析', 'F 题标准动作：先定义公平再量化'),
    ('2024', 'A', 'A-资源可得性与性别比例(题)', '2400996',
     'Adaptive Sex of Lamprey: gift or curse?', 24, 20, 3, 'N',
     '种群迭代模型 + 生态系统评估', '把"性别比例可变"写成动力学方程'),
    ('2024', 'B', 'B-寻找潜水器(题)', '2419984',
     'Time is Life: Precise Localization and Faster Search', 25, 16, 2, 'N',
     '概率定位 + 贝叶斯更新 + 搜索策略', 'B 题"不确定性下的搜索"最佳示范'),
    ('2024', 'C', 'C-网球中的势头(题)', '2401298',
     '"Momentum" Exists In Tennis Game As Residual Effect — A Dual-Temporal Bayesian Network Model', 25, 20, 3, 'N',
     '假设检验 + 贝叶斯网络 + AUC 滑窗', '正面回答"势头是不是随机"'),
    ('2024', 'D', 'D-五大湖水资源问题(题)', '2429211',
     'Dynamic Dams Model: A Multigranular, Human-Centered Approach', 25, 19, 4, 'Y',
     '网络流 + 多粒度控制 + 多目标权衡', 'D 题里少见的真·网络流建模'),
    ('2024', 'E', 'E-财产保险的可持续性(题)', '2413552',
     'Sustainability Study of the Property Insurance Industry Under Extreme Weather Conditions', 25, 16, 8, 'N',
     'MGWR 回归 + 承保决策 + 多目标', 'E 题"承保/不承保"决策链完整'),
    ('2024', 'F', 'F-减少非法野生动植物贸易(题)', '2409949',
     'Roaring Silence: Can We Break the Chains of Illegal Wildlife Trade?', 22, 23, 10, 'Y',
     '项目评估 RBM/LFA + 成本效益 + 政策建议', 'F 题"给客户做方案"的范文'),
]

lines = ['# 12 篇 O 奖研读材料清单', '',
         '选取原则：① 结构齐全（摘要页/重述/假设/符号/建模/求解/检验/敏感性/评价/参考）② 方法该题型主流 ③ 便于复现（尽量有代码附录）④ 图表密度适中 ⑤ 12 篇合起来覆盖 6 类 × 2 年且方法不重复。',
         '', '| # | 年题 | 控制号 | 标题 | 页 | 图 | 表 | 附录 | 核心方法 | 为什么选它 |',
         '|---|---|---|---|---|---|---|---|---|---|']

for i, (y, t, folder, cid, title, pg, nf, nt, code, meth, why) in enumerate(picks, 1):
    src = os.path.join(root, y, folder, cid + '.pdf')
    out = os.path.join(dst, f'{y}{t}_{cid}.pdf')
    shutil.copy2(src, out)
    lines.append(f'| {i} | {y} {t} | {cid} | {title} | {pg} | {nf} | {nt} | {code} | {meth} | {why} |')

lines += ['', '## 原文位置', '']
for y, t, folder, cid, *_ in picks:
    lines.append(f'- {y} {t}：`{y}\\{folder}\\{cid}.pdf`')

open(os.path.join(dst, '清单.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('copied', len(picks))
for f in sorted(os.listdir(dst)):
    print(' ', f)
