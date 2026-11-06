# -*- coding: utf-8 -*-
"""扫描已交付论文里的符号/数学标记/代码残留问题（只读，不改文件）。

用法: python audit_math.py <workdir> [...]
"""
import json, os, re, sys, collections

# 私有区 / 数学字母数字符号（伪粗体、数学斜体）
PUA = re.compile(r'[\ue000-\uf8ff]')
MATH_ALNUM = re.compile(r'[\U0001D400-\U0001D7FF]')
MARK = re.compile(r'[\^_]\{[^{}]{0,40}\}')
BAD_MARK = re.compile(r'[\^_]\{?$|[\^_]\{\}')      # 空标记 / 悬空标记
CODE = re.compile(r'\b(while|for each|for all|if|else|end if|return|Algorithm|Update|Set|Compute|Initialize|Input|Output|procedure)\b')
ARROW = re.compile(r'[←→⇒⇐⇔]')
DOUBLE = re.compile(r'([A-Za-z\u0370-\u03ff])\1\1')   # 同一字母连三次

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

def audit(wd):
    name = os.path.basename(os.path.dirname(wd.rstrip('/\\')))
    rep = collections.defaultdict(list)
    it_path = os.path.join(wd, 'items_full.json')
    zh_path = os.path.join(wd, 'zh_full.json')
    if not os.path.exists(zh_path):
        print('== %s : 无 zh_full.json' % name); return
    items = load(it_path)
    zh = load(zh_path)

    for k, v in zh.items():
        if not isinstance(v, str) or not v.strip():
            rep['空译文'].append(k); continue
        if 'where, is' in v: rep['where,is 空位'].append(k)
        if PUA.search(v): rep['私用区字符'].append((k, PUA.findall(v)[:3]))
        m = MATH_ALNUM.findall(v)
        if m:
            # 同一数学字母重复（𝑆𝑆）= 伪粗体未合并
            s = ''.join(m)
            if DOUBLE.search(s) or len(m) >= 2 and len(set(m)) < len(m):
                rep['伪粗体重复'].append((k, s[:12]))
            else:
                rep['数学字母(检查)'].append((k, s[:12]))
        if BAD_MARK.search(v): rep['标记悬空'].append((k, v[-25:]))
        if re.search(r'[\^_]\{', v):
            for mm in MARK.findall(v): rep['上下标标记'].append((k, mm))
        if ARROW.search(v): rep['箭头'].append((k, v[:40]))
        # 中文译文里残留的整句英文
        en_run = re.findall(r'[A-Za-z][A-Za-z ,.\'\-]{28,}', v)
        if en_run: rep['英文长串'].append((k, en_run[0][:50]))
        if CODE.search(v) and re.search(r'[\u4e00-\u9fff]', v):
            rep['代码词+中文'].append((k, v[:60]))

    # 英文侧：代码行是否被当成正文
    for i, it in enumerate(items):
        t = it.get('text') or ''
        if PUA.search(t): rep['EN私用区'].append((i, PUA.findall(t)[:3]))
        if it.get('kind') == 'para' and CODE.search(t) and ARROW.search(t):
            rep['EN代码行(疑)'].append((i, t[:70]))

    total = len(zh)
    print('== %s  条目 %d' % (name, total))
    for cat in ('空译文', 'where,is 空位', '私用区字符', 'EN私用区', '伪粗体重复', '数学字母(检查)',
                '标记悬空', '上下标标记', '箭头', '英文长串', '代码词+中文', 'EN代码行(疑)'):
        lst = rep.get(cat) or []
        if cat == '上下标标记' and lst:
            print('   %-12s %d  %s' % (cat, len(lst), lst[:4]))
        elif lst:
            print('   %-12s %d  %s' % (cat, len(lst), lst[:4]))

if __name__ == '__main__':
    for w in sys.argv[1:]:
        if os.path.isdir(w):
            audit(w)
