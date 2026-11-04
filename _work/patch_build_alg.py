# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
s = open(p, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in s else "\n"
old = ('    EQD, EQ_SKIP = {}, set()' + nl +
       '    _eqp = os.path.join(BIL, "eq_map.json")' + nl +
       '    if os.path.exists(_eqp):' + nl +
       '        for _k, _v in json.load(open(_eqp, encoding="utf-8")).items():' + nl +
       '            if "skip" in _v:' + nl +
       '                EQD[int(_k)] = _v' + nl +
       '                EQ_SKIP.update(_v["skip"])')
new = ('    EQD, EQ_SKIP = {}, set()' + nl +
       '    for _f in ("eq_map.json", "alg_map.json"):' + nl +
       '        _eqp = os.path.join(BIL, _f)' + nl +
       '        if os.path.exists(_eqp):' + nl +
       '            for _k, _v in json.load(open(_eqp, encoding="utf-8")).items():' + nl +
       '                if "skip" in _v:' + nl +
       '                    EQD[int(_k)] = _v' + nl +
       '                    EQ_SKIP.update(_v["skip"])')
assert old in s, "anchor missing"
s = s.replace(old, new, 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("build reads alg_map too")
