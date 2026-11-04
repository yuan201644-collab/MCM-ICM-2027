# -*- coding: utf-8 -*-
import json

p = r"D:\26年美国大学生数学建模竞赛\研读材料\12篇研读\2022C_2203120_交易策略\paper.json"
d = json.load(open(p, encoding="utf-8"))

d["fig_texts"] = {
    "img_04_3.png": [
        ["Data preprocessing", "数据预处理"],
        ["ARIMA model", "ARIMA 模型"],
        ["Prediction trend by cycle", "按周期预测走势"],
        ["Price Prediction Model", "价格预测模型"],
        ["Define variable parameters", "设定可变参数"],
        ["Establish strategy model", "建立策略模型"],
        ["Conservative strategy", "保守策略"],
        ["Risk strategy", "风险策略"],
        ["Strategy Model", "策略模型"],
        ["Adjust alpha to explore the impact on insurance-type, common-type, radical-type",
         "调整 α 以考察对保守型/普通型/激进型交易者的影响"],
        ["Impact of transaction costs on strategy", "交易成本对策略的影响"],
        ["Generalization Ability", "泛化能力"],
        ["Robustness", "稳健性"],
        ["Yield", "收益"],
        ["Prove Optimization of the Strategy", "证明策略的优化"],
    ],
    "img_11_9.png": [
        ["X_g(i+1) − Y_gi > 0", "当日价格高于昨日"],
        ["calculate the increase threshold e_g(i+1)", "计算上调阈值 e"],
        ["calculate the decrease threshold f_g(i+1)", "计算下调阈值 f"],
        ["calculate proportion of cash in total assets q_i", "计算现金占总资产的比例 q"],
        ["q_i > q", "现金比例超过阈值 q"],
        ["go to step 4(1)", "转到第 4(1) 步"],
        ["go to step 4(2)", "转到第 4(2) 步"],
        ["i=i+1 back to step2", "令 i=i+1，返回第 2 步"],
        ["|X_gi − Y_gi| > f_g(i+1)", "价差绝对值超过下调阈值"],
    ],
    "img_21_30.png": [
        ["When to trade", "何时交易"],
        ["Trading bitcoin or gold", "交易比特币还是黄金"],
        ["How much is the specific transaction", "具体交易多少"],
    ],
}
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("fig_texts:", list(d["fig_texts"]))
