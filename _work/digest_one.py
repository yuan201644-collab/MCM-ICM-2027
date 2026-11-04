# -*- coding: utf-8 -*-
"""Print a digest of one paper's full text: summary, headings, captions."""
import re
import sys

path = r"D:\26年美国大学生数学建模竞赛\_work\全文\2022B_2200084.txt"
raw = open(path, encoding="utf-8").read()
pages = re.split(r"<<<PAGE (\d+)>>>", raw)
# pages = ['', '1', text1, '2', text2, ...]
blocks = [(int(pages[i]), pages[i + 1]) for i in range(1, len(pages) - 1, 2)]

print("PAGES:", len(blocks))
print("=" * 30, "SUMMARY P1")
for pno, txt in blocks[:1]:
    print(txt.strip()[:1800])

print("=" * 30, "HEADINGS")
head_re = re.compile(r"^\s*(\d+(?:\.\d+)*\.?\s+[A-Z][^\n]{2,70})$")
for pno, txt in blocks:
    for line in txt.splitlines():
        m = head_re.match(line.strip())
        if m and len(line.split()) >= 2:
            print(f"p{pno}  {line.strip()[:80]}")

print("=" * 30, "CAPTIONS")
cap_re = re.compile(r"(Table|Figure)\s*\d+\s*[:.]")
for pno, txt in blocks:
    for line in txt.splitlines():
        if cap_re.search(line) and len(line) < 120:
            print(f"p{pno}  {line.strip()[:110]}")

print("=" * 30, "DELIVERABLE / KEYWORDS")
for pno, txt in blocks:
    for kw in ("Memorandum", "Memo", "Letter to", "Dear", "two-page", "Keywords"):
        if kw.lower() in txt.lower():
            print(f"p{pno}  hit: {kw}")

print("=" * 30, "LAST PAGES")
for pno, txt in blocks[-2:]:
    print(f"--- p{pno} ---")
    print(txt.strip()[:900])
