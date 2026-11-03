import pymupdf, glob, os, re, csv

root = r'D:\26年美国大学生数学建模竞赛'
rows = []

METHODS = {
    'ODE/动力系统': r'differential equation|ODE\b|dynamical system|Lotka|logistic growth|equilibrium|stability analysis',
    '最优控制': r'optimal control|Pontryagin|Hamiltonian|bang-bang|dynamic programming',
    '线性/整数规划': r'linear programming|integer programming|mixed.integer|MILP|LP model|simplex',
    '非线性规划': r'nonlinear programming|non-linear programming|gradient descent|KKT',
    '启发式算法': r'genetic algorithm|particle swarm|simulated annealing|ant colony|NSGA|tabu search|differential evolution',
    '时间序列': r'ARIMA|ARMA|GARCH|LSTM|GRU|time series|autoregressive|Holt|exponential smoothing',
    '机器学习': r'neural network|random forest|XGBoost|SVM|support vector|decision tree|deep learning|CNN|Transformer',
    '统计推断': r'hypothesis test|p-value|chi-square|t-test|ANOVA|bootstrap|confidence interval|significance',
    '回归': r'regression|OLS|least square|panel data|logit|probit',
    '贝叶斯/概率': r'Bayesian|prior|posterior|Markov chain|Monte Carlo|probability distribution|Poisson',
    '网络流/图': r'network flow|max.flow|min.cut|shortest path|graph theory|Dijkstra|spanning tree',
    '评价体系': r'AHP|analytic hierarchy|entropy weight|TOPSIS|fuzzy comprehensive|grey relation|DEA|principal component',
    '多目标': r'multi-objective|Pareto|weighted sum|trade-off analysis',
    '博弈论': r'game theory|Nash|Stackelberg|payoff matrix',
    '系统动力学/ABM': r'system dynamics|causal loop|agent-based|ABM\b',
    '仿真': r'simulation|Monte Carlo simulation|discrete event',
    '敏感性分析': r'sensitivity analysis|robustness check|perturbation',
}

SECTIONS = {
    '目录': r'Table of Contents|Contents\s*\n',
    '假设': r'Assumption',
    '符号': r'Notation|Symbol',
    '敏感性': r'Sensitivity',
    '优缺点': r'Strengths and Weakness|Strengths\s*&\s*Weakness|Advantages and Disadvantages',
    '参考文献': r'References|Bibliography',
    '附录': r'Appendix',
    '备忘录/信': r'Memorandum|Memo\b|Letter to',
}

def clean(t):
    return re.sub(r'\s+', ' ', t).strip()

for year in ('2022', '2024'):
    for d in sorted(glob.glob(os.path.join(root, year, '*'))):
        if not os.path.isdir(d):
            continue
        folder = os.path.basename(d)
        tcode = folder[0]
        for f in sorted(glob.glob(os.path.join(d, '*.pdf'))):
            name = os.path.basename(f)
            if name.startswith('00_'):
                continue
            doc = pymupdf.open(f)
            txt = '\n'.join(p.get_text() for p in doc)
            flat = clean(txt)
            p1 = clean(doc[0].get_text())
            m = re.search(r'Team Control Number\s*\d{5,7}\s*(.{3,200}?)\s*Summary', p1, re.I|re.S)
            title = clean(m.group(1)) if m else ''
            if not title:
                m2 = re.search(r'Problem Chosen\s*[A-F].{0,120}?(?:Sheet)?\s*(.{5,120}?)\s*Summary', p1, re.I)
                title = clean(m2.group(1)) if m2 else p1[:60]
            title = title.replace('2024 MCM/ICM Summary Sheet','').replace('2022 MCM/ICM Summary Sheet','')
            title = re.sub(r'^(Problem Chosen\s*[A-F]|[A-F]\s*)', '', title).strip()
            hits = []
            for k, pat in METHODS.items():
                c = len(re.findall(pat, flat, re.I))
                if c >= 2:
                    hits.append((c, k))
            hits.sort(reverse=True)
            meth = '、'.join(k for c, k in hits[:6])
            secs = [k for k, pat in SECTIONS.items() if re.search(pat, flat, re.I)]
            rows.append([year, tcode, name, len(doc), title[:120], meth, '/'.join(secs),
                         len(hits)])

with open(os.path.join(root, '_work', '方法指纹.tsv'), 'w', encoding='utf-8', newline='') as fh:
    w = csv.writer(fh, delimiter='\t')
    w.writerow(['年', '题', '文件', '页', '标题', '方法(按词频)', '章节', '方法数'])
    w.writerows(rows)

cur = None
for r in rows:
    k = f'{r[0]} {r[1]}'
    if k != cur:
        print('\n' + '='*6, k)
        cur = k
    print(f'  {r[2]} | {r[4][:70]}')
    print(f'       法[{r[3]}p]: {r[5]}  | 节: {r[6]}')
