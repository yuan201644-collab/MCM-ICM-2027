# -*- coding: utf-8 -*-
"""Build the 分工 folder: three role folders, each with 精读(3 papers), 通读(9 cards), 交付."""
import os
import re
import shutil

BASE = r"D:\26年美国大学生数学建模竞赛"
SRC = os.path.join(BASE, "研读材料", "12篇研读")
OUT = os.path.join(BASE, "分工")

ROLES = {
    "建模手": ["2022B_2200084", "2022D_2215444", "2024A_2400996", "2024D_2429211"],
    "编程手": ["2022C_2203120", "2022E_2223495", "2024B_2419984", "2024C_2401298"],
    "论文手": ["2022A_2209466", "2022F_2224021", "2024E_2413552", "2024F_2409949"],
}

ROLE_EXTRA = {
    "建模手": [
        ("三个关键决策", "这篇论文在方法上做了哪三个\"要么这样、要么那样\"的选择？（例如：连续 vs 离散、有数据 vs 无数据、单目标 vs 多目标）每个选择写出\"它选了哪个\"和\"为什么\"。"),
        ("一条可迁移套路", "如果换个题，这一套还能用的动作是什么？用一句话写清\"输入什么→做什么→得到什么\"。"),
        ("换题怎么变", "把这篇的方法搬到另一个题号（例如从 B 搬到 D），哪一步必须改？改成什么？"),
    ],
    "编程手": [
        ("数据来源", "数据从哪来、什么粒度、有没有缺失/异常、你怎么拿到（URL 或表号）。"),
        ("求解实现", "用什么算法/工具求解（含关键参数），伪代码或代码入口在哪一页。"),
        ("验证方式", "作者怎么证明结果可信？（对拍/误差/交叉验证/灵敏度）具体指标是多少。"),
        ("踩过的坑", "实现时最容易翻车的一步是什么？（初值、边界、量纲、收敛）作者有没有明说。"),
    ],
    "论文手": [
        ("八节骨架", "按\"引言/假设/符号/模型/求解/灵敏度/评价/结论\"列出每节的页跨度与一句话主旨。"),
        ("摘要结构", "摘要按什么顺序展开？找出它的\"方法句\"与\"结果句\"各一句，抄下来。"),
        ("交付物嵌入", "交付物（备忘录/信/指导/文章）放在第几节、如何与正文呼应、有没有独立成页。"),
        ("可迁移写法", "哪一句写法可以直接搬到我们的论文里？抄原句，并注明适用条件。"),
    ],
}

SECTIONS = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧"]


def read_card(folder):
    p = os.path.join(SRC, folder, "精炼版.md")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def split_card(text):
    """Return dict ①..⑧ -> body text."""
    out = {}
    cur = None
    buf = []
    for line in text.splitlines():
        m = re.match(r"^\*\*([①②③④⑤⑥⑦⑧])", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf).strip()
            cur = m.group(1)
            buf = [line]
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf).strip()
    return out


def build_card(folder, role):
    parts = split_card(read_card(folder))
    year = folder.split("_")[0]
    no = folder.split("_")[1]
    title = folder.split("_", 2)[2]
    lines = []
    lines.append(f"# {year} {no} 角色卡片（{role}）\n")
    lines.append(f"> 论文目录：`{folder}`　填卡人：____　完成日期：____\n")
    lines.append("## 一、公共脊柱（已从精炼版预填，核对后可直接用）\n")
    for k in ["①", "②", "③", "⑤"]:
        body = parts.get(k, "（缺）")
        lines.append(body + "\n")
    lines.append("## 二、" + role + "专属（必须自己写，不许抄摘要）\n")
    for i, (name, prompt) in enumerate(ROLE_EXTRA[role], 1):
        lines.append(f"### {role}专属 {i}：{name}\n")
        lines.append(f"*要回答的问题*：{prompt}\n")
        lines.append("**作答**：（在这里写，每条都要带 [p.X]）\n")
    lines.append("## 三、自检\n")
    lines.append("- [ ] 每条都有页码 `[p.X]`")
    lines.append("- [ ] 专属格没有一句是抄摘要的")
    lines.append("- [ ] 至少有一处\"我不同意作者\"或\"我会怎么做\"")
    lines.append("- [ ] 全文没有超过两页\n")
    return "\n".join(lines)


def role_task_md(role):
    mine = ROLES[role]
    others = [d for d in folders if d.split("_")[1] not in " ".join(mine)]
    deep = "\n".join(f"- `{m}`" for m in mine)
    read = "\n".join(f"- `{o}`" for o in others[:4])
    skim = "\n".join(f"- `{o}`" for o in others[4:])
    extra = "\n".join(f"{i}. **{n}**：{p}" for i, (n, p) in enumerate(ROLE_EXTRA[role], 1))
    return f"""# {role}·第一阶段任务清单

> 目标：两周内把 12 篇 O 奖论文"过一遍、深读四篇"，产出一套可复用的判断力。
> 时间预算：精读 4×90 分钟 + 通读 4×30 分钟 + 快读 4×10 分钟 ≈ 8 小时 40 分（不含写卡片）。

## 一、你要精读的四篇（90 分钟/篇）

{deep}

精读方法（照做，别跳）：
1. 先读摘要 + 结论，10 分钟，判断它解决什么问题。
2. 翻到"假设"与"符号表"，看它把现实简化成了什么，10 分钟。
3. 顺着模型链读推导，遇到公式先看它想表达什么关系，别纠结符号，40 分钟。
4. 读灵敏度与评价两节，这是 O 奖和 M 奖的分界线，20 分钟。
5. 最后写卡片，10 分钟。

## 二、你要通读的四篇（30 分钟/篇，用 `通读/` 里的精炼版当索引）

{read}

通读标准：能回答"这篇用什么方法、解决什么问题、交付物是什么"三句话即可，不要求懂推导。

## 三、你要快读的四篇（10 分钟/篇）

{skim}

快读标准：只看精炼版的 ①②⑤ 三格，记住"它属于哪类套路"就够。

## 四、你的产出（缺一不可）

1. 四张 `角色卡片.md`（在各自精读文件夹里，已预填公共脊柱，你补{role}专属部分）
2. 一张汇总表 `交付/汇总表.md`：12 篇 × (方法/工具/交付物/一句话)
3. 一次 30 分钟汇报：讲清"这四篇里哪一篇最值得学、为什么"

{role}专属要回答的格：
{extra}

## 五、验收（队长按这四条查）

- 每张卡片两页内、每条带页码；
- 专属格不能出现"本文建立了…模型"这种抄摘要的句子；
- 四篇里至少有一篇你能指出作者的弱点，并且说清"如果是我们会怎么改"；
- 汇报时能不看稿讲 5 分钟。

## 六、目录说明

- `精读/`：三篇的 原题 PDF、题目中文翻译、原论文 PDF、精炼版、角色卡片（待填）
- `通读/`：另外九篇的精炼版（只有一页，够你判断要不要深看）
- `交付/`：你写好的卡片副本与汇总表放这里，方便队长统一收
"""


folders = [d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d))]
folders.sort()

for _r in ROLES:
    _d = os.path.join(OUT, _r)
    if os.path.exists(_d):
        shutil.rmtree(_d)

for role, mine in ROLES.items():
    rd = os.path.join(OUT, role)
    os.makedirs(os.path.join(rd, "精读"))
    os.makedirs(os.path.join(rd, "通读"))
    os.makedirs(os.path.join(rd, "交付"))
    open(os.path.join(rd, "00_任务清单.md"), "w", encoding="utf-8").write(role_task_md(role))
    open(os.path.join(rd, "交付", "README.md"), "w", encoding="utf-8").write(
        "# 交付说明\n\n把写好的 `角色卡片.md` 复制到这里，命名：`{年}{题}_{控制号}_{角色}.md`。\n"
        "队长会统一抽查页码与格式。\n")

    for f in folders:
        if any(f.startswith(m) for m in mine):
            dst = os.path.join(rd, "精读", f)
            os.makedirs(dst)
            for fn in os.listdir(os.path.join(SRC, f)):
                src = os.path.join(SRC, f, fn)
                if os.path.isfile(src) and (fn.endswith(".pdf") or fn.endswith(".md")):
                    shutil.copy2(src, os.path.join(dst, fn))
            open(os.path.join(dst, "角色卡片.md"), "w", encoding="utf-8").write(build_card(f, role))
        else:
            src = os.path.join(SRC, f, "精炼版.md")
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(rd, "通读", f + "_精炼版.md"))

print("done", OUT)
