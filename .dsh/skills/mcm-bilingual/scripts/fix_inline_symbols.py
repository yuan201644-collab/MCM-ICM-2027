# -*- coding: utf-8 -*-
"""修补 2022A 旧文字层里丢失的行内数学符号（where,is / 式中，为）。

原 PDF 把这些符号画成矢量小图，文字层没有字符，旧抽取脚本又只把小图挂到
中文侧的「，为」空位上；一旦空位数与小图数不等就整批丢弃，于是英中两侧都缺主语。
本脚本按原 PDF 逐字补回符号（用 _{} 让 build.py 渲染成真下标），并从 eq_map
移除这些条目的行内小图，避免符号重复。

用法: MCM_CFG=<paper.json> python fix_inline_symbols.py
"""
import json
import os

CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))
WD = CFG["workdir"]

# item -> [(英文原句, 英文修补后, 中文修补后)]
FIX = {
    92: ("(1) where,is aerobic respiratory energy output power.are both undetermined parameters.",
         "(1) where, P_{o} is aerobic respiratory energy output power. γ, δ are both undetermined parameters.",
         "（1）式中，P_{o} 为有氧呼吸能量输出功率，γ、δ 均为待定参数。"),
    97: ("(3) where,is the ratio of the anaerobic energy consumption rate of the human body to the anaerobic respiration output power.",
         "(3) where, α is the ratio of the anaerobic energy consumption rate of the human body to the anaerobic respiration output power.",
         "（3）式中，α 为人体无氧能量消耗速率与无氧呼吸输出功率之比。"),
    100: ("where,is the coefficient of recovery, which means that when the output power exceeds the limit of the curve, the rider needs roughly twice the time to restore the stored energy in the energy pool.",
          "where, β is the coefficient of recovery, which means that when the output power exceeds the limit of the curve, the rider needs roughly twice the time to restore the stored energy in the energy pool.",
          "式中，β 为恢复系数，其含义是：当输出功率超过曲线的限制时，车手大约需要两倍的时间才能恢复能量池中储存的能量。"),
    149: ("(7) where,is the fluid density, and it is the air density here.is the frontal area of the total projection of the rider and the bicycle, that is, the effective area.is the resistance coefficient.is the speed of the rider relative to the fluid.is the coefficient of rolling friction. is the total mass of the rider and bike.is the gravitational acceleration.",
          "(7) where, ρ is the fluid density, and it is the air density here. A_{p} is the frontal area of the total projection of the rider and the bicycle, that is, the effective area. C_{D} is the resistance coefficient. v_{f} is the speed of the rider relative to the fluid. C_{R} is the coefficient of rolling friction. M is the total mass of the rider and bike. g is the gravitational acceleration.",
          "（7）式中，ρ 为流体密度，此处即为空气密度；A_{p} 为车手与自行车总投影的迎风面积，即有效面积；C_{D} 为阻力系数；v_{f} 为车手相对于流体的速度；C_{R} 为滚动摩擦系数；M 为车手与自行车的总质量；g 为重力加速度。"),
    152: ("(9) where,is a constant, the general value is 1.293Kg/m3.is air pressure.is the temperature in Kelvin.is the local altitude.",
          "(9) where, ρ_{0} is a constant, the general value is 1.293Kg/m3. PB is air pressure. T is the temperature in Kelvin. Alt is the local altitude.",
          "（9）式中，ρ_{0} 为常数，一般取 1.293Kg/m3；PB 为气压；T 为以开尔文计的温度；Alt 为当地海拔。"),
    164: ("Where,is the motivation provided to the rider, which is related to the power provided by",
          "Where, F is the motivation provided to the rider, which is related to the power provided by",
          "式中，F 为提供给车手的动力，其与所提供的功率有关，"),
    179: ("where,is the position of each corner in the track.",
          "where, s_{i} is the position of each corner in the track.",
          "其中，s_{i} 为每个弯道在赛道中的位置。"),
    238: ("(14) where,is the angle between the traveling direction and the wind direction (less than or equal to the flat angle), which is essentially function of, denoted by.is the symbolic function.are the horizontal speed of the rider and the wind speed, respectively.",
          "(14) where, δ is the angle between the traveling direction and the wind direction (less than or equal to the flat angle), which is essentially function of x, denoted by δ = δ(x). sign() is the symbolic function. v_{f}, v_{w} are the horizontal speed of the rider and the wind speed, respectively.",
          "(14) 其中，δ 为行进方向与风向之间的夹角（小于或等于平角），其本质是 x 的函数，记为 δ = δ(x)。sign() 为符号函数。v_{f}、v_{w} 分别为车手的水平速度与风速。"),
    323: ("where,is a constant, related to the total number of riders and the position of the rider in",
          "where, C_{dr} is a constant, related to the total number of riders and the position of the rider in",
          "其中，C_{dr} 是常数，与车手总数以及车手在"),
    347: ("where,is the position that needs to be drafted in the schedule.",
          "where, d_{i} is the position that needs to be drafted in the schedule.",
          "其中，d_{i} 为赛程中需要进行跟骑换位的位置。"),
}

ip = os.path.join(WD, "items_full.json")
zp = os.path.join(WD, "zh_full.json")
ep = os.path.join(WD, "eq_map.json")
items = json.load(open(ip, encoding="utf-8"))
zh = json.load(open(zp, encoding="utf-8"))
eq = json.load(open(ep, encoding="utf-8"))

n_en = n_zh = n_img = 0
for idx, (old, new, znew) in FIX.items():
    it = items[idx]
    text = it.get("text") or ""
    if old in text:
        it["text"] = text.replace(old, new, 1)
        n_en += 1
    sents = it.get("sents") or []
    for j, s in enumerate(sents):
        if old in s or (s.startswith(old[:24]) and "where" in s.lower() and "is" in s[:16]):
            sents[j] = new if old in s else s
            if old in s:
                n_en += 1
    it["sents"] = sents
    key = "%d.0" % idx
    if zh.get(key, "").strip():
        zh[key] = znew
        n_zh += 1
    # 移除该条目的行内小图（符号已用文字补回）
    k = str(idx)
    if k in eq:
        v = eq[k]
        vs = v if isinstance(v, list) else [v]
        kept = [e for e in vs if not (isinstance(e, dict) and e.get("inline"))]
        dropped = len(vs) - len(kept)
        if dropped:
            eq[k] = kept
            n_img += dropped

json.dump(items, open(ip, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(zh, open(zp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(eq, open(ep, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("英文修补 %d 处，中文修补 %d 条，移除行内小图 %d 张" % (n_en, n_zh, n_img))
