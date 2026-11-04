# -*- coding: utf-8 -*-
"""2022C 2203120 paper.json 初稿（terms/gloss 后续补）。"""
import json
import os

ROOT = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022C_2203120_交易策略"
cfg = {
    "pdf": os.path.join(ROOT, "2203120.pdf"),
    "workdir": os.path.join(ROOT, "work"),
    "out_docx": os.path.join(ROOT, "2203120_英中对照.docx"),
    "title": "2203120 英中对照版",
    "footer_prefix": "2203120 英中对照版 · 第 ",
    "subtitle": "2022 MCM Problem C · Trading Strategy Model Based on Dynamic Programming",
    "read_note": "读法：黑字为原文，蓝字为译文，一段英文一段中文，上下对应；蓝字里的小字括号是该术语第一次出现时的英文原词。",
    "pages": [0] + list(range(2, 22)) + [23],
    "en_only_pages": [22],
    "batches": 8,
    "terms": [
        ["Trading Strategy", "交易策略", "本文主题：按价格决定每日买卖"],
        ["Dynamic Programming", "动态规划", "本文核心方法"],
        ["ARIMA", "ARIMA 模型", "自回归积分滑动平均"],
        ["Commission", "手续费", "每次交易按比例抽取"],
        ["Portfolio", "投资组合", "现金+黄金+比特币"],
        ["Return", "收益率", "期末净值与初始之比"],
        ["Risk", "风险", "用价格变化方差度量"],
        ["Constraint", "约束条件", "资金与持仓限制"],
        ["Objective Function", "目标函数", "最大化最终收益"],
        ["Sensitivity Analysis", "灵敏度分析", "扰动参数看结果变化"],
        ["Transaction", "交易", "买或卖一次"],
        ["Threshold", "阈值", "触发交易的临界值"],
        ["Volatility", "波动率", "价格波动的剧烈程度"],
        ["Robustness", "稳健性", "参数变动下结论是否稳定"],
        ["Prediction", "预测", "用历史价格推未来"],
        ["Backtesting", "回测", "用历史数据检验策略"],
        ["Trader Type", "交易者类型", "普通型/激进型等"],
        ["Asset", "资产", "可交易的标的物"],
    ],
    "gloss": [
        ["Trading Strategy", "交易策略"],
        ["Dynamic Programming", "动态规划"],
        ["ARIMA", "ARIMA 模型"],
        ["Commission", "手续费"],
        ["Portfolio", "投资组合"],
        ["Return", "收益率"],
        ["Risk", "风险"],
        ["Constraint", "约束条件"],
        ["Objective Function", "目标函数"],
        ["Sensitivity Analysis", "灵敏度分析"],
        ["Transaction", "交易", ],
        ["Threshold", "阈值"],
        ["Volatility", "波动率"],
        ["Robustness", "稳健性"],
        ["Prediction", "预测"],
        ["Backtesting", "回测"],
        ["Trader Type", "交易者类型"],
        ["Asset", "资产"],
    ],
    "fig_texts": {},
    "figure_note_for": [],
    "figure_note": "",
    "table_note": "",
    "end_note": "（全文完。公式与表格在原 PDF 中是矢量图形，未纳入本对照版；可按文中「原文第 N 页」标记翻到 2203120.pdf 对照查看。）",
}
os.makedirs(cfg["workdir"], exist_ok=True)
json.dump(cfg, open(os.path.join(ROOT, "paper.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("paper.json written, pages=", len(cfg["pages"]))
