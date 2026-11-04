# -*- coding: utf-8 -*-
p = r"D:\26年美国大学生数学建模竞赛\.dsh\skills\mcm-bilingual\scripts\build.py"
s = open(p, encoding="utf-8").read()
nl = "\r\n" if "\r\n" in s else "\n"
old_line = [l for l in s.split(nl) if l.startswith("CODE = re.compile")][0]
new_line = ("CODE = re.compile("
            "r'^(?:\\d+\\s+)?(?:while|for|if|else|end|return|repeat|until|Algorithm|"
            "Update|Set|Compute|Initialize|Initialization)\\b|←')")
s = s.replace(old_line, new_line, 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("CODE ->", new_line)
