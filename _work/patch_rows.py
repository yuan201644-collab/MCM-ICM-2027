# -*- coding: utf-8 -*-
"""Refine the rows whose abstract text was truncated, using the PDF summary page."""
import io, sys

ROOT = r"D:\26年美国大学生数学建模竞赛\_work"
sys.stdout.reconfigure(encoding="utf-8")

FIX = {
    "2204883": ("LSTM价格预测+多目标线性规划",
                "先LSTM预测金价与币价，再用多目标线性规划定每日买卖",
                "摘要截断；方法据原文摘要页补全"),
    "2229059": ("瞬时逻辑模型+宏观尺度预测",
                "按当前市场特征即时判定买卖动作，只做宏观尺度预测",
                "摘要截断；方法据原文摘要页补全"),
    "2208928": ("模糊综合评价+EWM-AHP组合赋权",
                "把成熟度拆成人员/技术/流程三面12个KPI，两法打分后融合",
                "摘要截断；方法据原文摘要页补全"),
    "2216618": ("CIF指数+AHP赋权+方案再优化",
                "自建CIF综合指数，把碳汇、经济与生物多样性合成一个分数",
                "摘要截断；原摘要无标题；方法据原文摘要页补全"),
    "2407038": ("ARIMA+岭回归+动力学模型",
                "先用ARIMA与岭回归拟合海流和密度场，再解运动方程推轨迹",
                "摘要截断；方法据原文摘要页补全"),
}

p = ROOT + r"\摘要概览.tsv"
lines = io.open(p, encoding="utf-8").read().rstrip("\n").split("\n")
out = [lines[0]]
n = 0
for r in lines[1:]:
    f = r.split("\t")
    cid = f[2]
    if cid in FIX:
        m, feat, note = FIX[cid]
        assert len(m) <= 20 and len(feat) <= 40, (cid, len(m), len(feat))
        f[4], f[5], f[7] = m, feat, note
        n += 1
    out.append("\t".join(f))
assert n == len(FIX), n
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
print("patched rows:", n, "total lines:", len(out))
