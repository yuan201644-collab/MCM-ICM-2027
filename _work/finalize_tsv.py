# -*- coding: utf-8 -*-
"""Fill 是否含交付物 from scan_out.txt keyword hits, validate, write final TSV."""
import io, re, sys

ROOT = r"D:\26年美国大学生数学建模竞赛\_work"
sys.stdout.reconfigure(encoding="utf-8")

hits = set()
for ln in io.open(ROOT + r"\scan_out.txt", encoding="utf-16"):
    m = re.match(r"### (\d{7}) \|", ln)
    if m:
        hits.add(m.group(1))
print("hit cids:", len(hits))

lines = io.open(ROOT + r"\摘要概览.tsv", encoding="utf-8").read().rstrip("\n").split("\n")
head, rows = lines[0], lines[1:]
print("data rows:", len(rows))
assert len(rows) == 79
assert head.split("\t") == ["年", "题", "控制号", "中文标题", "核心方法", "一句话特色", "是否含交付物", "备注"]

out = [head]
yes = no = 0
for r in rows:
    f = r.split("\t")
    assert len(f) == 8, (len(f), r[:40])
    cid = f[2]
    assert re.fullmatch(r"\d{7}", cid), cid
    assert len(f[3]) <= 20, ("标题", cid, len(f[3]))
    assert len(f[4]) <= 20, ("方法", cid, len(f[4]))
    assert len(f[5]) <= 40, ("特色", cid, len(f[5]))
    f[6] = "是" if cid in hits else "否"
    yes += f[6] == "是"
    no += f[6] == "否"
    out.append("\t".join(f))

txt = "\n".join(out) + "\n"
io.open(ROOT + r"\摘要概览.tsv", "w", encoding="utf-8", newline="\n").write(txt)
print("YES:", yes, "NO:", no, "lines:", len(out), "chars:", len(txt))
print("hits not in rows:", sorted(hits - {r.split("\t")[2] for r in rows}))
