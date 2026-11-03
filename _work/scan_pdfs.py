# -*- coding: utf-8 -*-
"""Scan O-paper PDFs for deliverable mentions; dump full abstract for a few unclear ones."""
import io, os, re, sys

ROOT = r"D:\26年美国大学生数学建模竞赛"
sys.stdout.reconfigure(encoding="utf-8")

pdfs = {}
for year in ("2022", "2024"):
    for dirpath, _, files in os.walk(os.path.join(ROOT, year)):
        for fn in files:
            if fn.lower().endswith(".pdf") and re.fullmatch(r"\d{7}\.pdf", fn.lower()):
                pdfs[fn[:-4]] = os.path.join(dirpath, fn)

print("indexed pdfs:", len(pdfs))

tsv = io.open(os.path.join(ROOT, "_work", "摘要概览.tsv"), encoding="utf-8").read().strip().split("\n")
cids = [ln.split("\t")[2] for ln in tsv[1:]]
print("rows:", len(cids), "missing pdf:", [c for c in cids if c not in pdfs])

import fitz
PAT = re.compile(r"memorandum|memo\b|one-page|two-page|2-page|1-page|non-?technical|general audience|layperson|press release", re.I)
hits = []
errs = []
for c in cids:
    p = pdfs.get(c)
    if not p:
        continue
    try:
        doc = fitz.open(p)
        txt = "\n".join(doc[i].get_text() for i in range(min(3, doc.page_count)))
        doc.close()
    except Exception as e:
        errs.append((c, str(e)[:80])); continue
    for m in PAT.finditer(txt):
        s = max(0, m.start() - 110); e = min(len(txt), m.end() + 110)
        snip = " ".join(txt[s:e].split())
        hits.append((c, m.group(0), snip))
        break

print("errors:", errs)
print("PDFs with deliverable keyword:", len(hits))
for c, kw, snip in hits:
    print("###", c, "|", kw, "|", snip)

UNCLEAR = ["2204883", "2229059", "2208928", "2216618", "2223269", "2407038"]
print("\n==== full page-1 text of unclear papers ====")
for c in UNCLEAR:
    p = pdfs.get(c)
    if not p:
        continue
    doc = fitz.open(p)
    t = doc[0].get_text()
    doc.close()
    print("\n@@@@", c, "@@@@")
    print(" ".join(t.split())[:1500])
