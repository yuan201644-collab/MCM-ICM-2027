# -*- coding: utf-8 -*-
"""把 _work 里跑通的四个脚本复制成 skill 版：所有论文相关常量改为读 MCM_CFG 指向的 paper.json。"""
import os
import re
import shutil

SRC = r"D:\26年美国大学生数学建模竞赛\_work"
DST = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts"
os.makedirs(DST, exist_ok=True)

LOAD = ('CFG = json.load(open(os.environ["MCM_CFG"], encoding="utf-8"))\n')

FILES = {
    "extract_full.py": "extract.py",
    "build_bilingual.py": "build.py",
    "make_table_imgs.py": "make_tables.py",
    "make_fig_crops.py": "make_figs.py",
    "make_batches.py": "batch.py",
}

REPL = {
    "extract.py": [
        (r'PDF = r"D:\\26年美国大学生数学建模竞赛\\研读材料\\12篇研读\\2022A_2209466_自行车功率曲线\\2209466\.pdf"',
         LOAD + 'PDF = CFG["pdf"]'),
        (r'OUTDIR = r"D:\\26年美国大学生数学建模竞赛\\_work\\bil"', 'OUTDIR = CFG["workdir"]'),
        (r'PAGES = \[0\] \+ list\(range\(2, 23\)\)', 'PAGES = CFG["pages"]'),
        (r'EN_ONLY_PAGES = \[23, 24\]', 'EN_ONLY_PAGES = CFG["en_only_pages"]'),
    ],
    "build.py": [
        (r'BIL = r"D:\\26年美国大学生数学建模竞赛\\_work\\bil"', LOAD + 'BIL = CFG["workdir"]'),
        (r'OUT = sys\.argv\[1\] if len\(sys\.argv\) > 1 else r"D:[^"]*"',
         'OUT = sys.argv[1] if len(sys.argv) > 1 else CFG["out_docx"]'),
        (r'add_en\(doc, "2209466 英中对照版"', 'add_en(doc, CFG["title"]'),
        (r'add_zh\(doc, "（全文完。公式与表格[^"]*"', 'add_zh(doc, CFG["end_note"]'),
        (r'style\(fp\.add_run\("2209466 英中对照版 · 第 "\)', 'style(fp.add_run(CFG["footer_prefix"])'),
    ],
    "make_tables.py": [
        (r'BASE = r"D:\\26年美国大学生数学建模竞赛\\_work\\bil"', LOAD + 'BASE = CFG["workdir"]'),
        (r'SRC = r"D:[^"]*2209466\.pdf"', 'SRC = CFG["pdf"]'),
    ],
    "make_figs.py": [
        (r'BASE = r"D:\\26年美国大学生数学建模竞赛\\_work\\bil"', LOAD + 'BASE = CFG["workdir"]'),
        (r'SRC = r"D:[^"]*2209466\.pdf"', 'SRC = CFG["pdf"]'),
    ],
}

OVERRIDE = '''
# ---- 由 paper.json 覆盖论文相关常量 ----
TERMS = [tuple(x) for x in CFG["terms"]]
GLOSS = [tuple(x) for x in CFG["gloss"]]
GLOSS_EN = [(en, zh) for zh, en in GLOSS]
FIG_TEXTS = {k: [tuple(y) for y in v] for k, v in CFG.get("fig_texts", {}).items()}
TBL_NOTE = CFG.get("table_note", "")
FIG_NOTE = CFG.get("figure_note", "")


def build():
'''

for src, dst in FILES.items():
    s = open(os.path.join(SRC, src), encoding="utf-8").read()
    if src == "build_bilingual.py":
        # 术语/词汇/图注三块整体替换成 Config 覆盖，避免残留 2209466 数据
        s = re.sub(r"\nTERMS = \[.*?\n\]\n", "\nTERMS = []\n", s, flags=re.S)
        s = re.sub(r"\nGLOSS = \[.*?\n\]\n", "\nGLOSS = []\n", s, flags=re.S)
        s = re.sub(r"\nFIG_TEXTS = \{.*?\n\}\n", "\nFIG_TEXTS = {}\n", s, flags=re.S)
    for pat, rep in REPL.get(dst, []):
        s2, n = re.subn(pat, rep, s)
        if n == 0:
            raise SystemExit("pattern not found in %s: %s" % (src, pat[:60]))
        s = s2
    if dst == "build.py":
        s = s.replace("\n\ndef build():", "\n" + OVERRIDE + "    pass\n", 1)
        s = s.replace("    pass\n" + "\n    # ", "    # ")
        # 去掉占位 pass，保证 build() 函数体仍以原第一行开始
        s = s.replace(OVERRIDE + "    pass\n", OVERRIDE)
    open(os.path.join(DST, dst), "w", encoding="utf-8").write(s)
    print("wrote", dst, len(s), "chars")
