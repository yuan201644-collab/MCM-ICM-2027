import glob, os, re

root = r'D:\26年美国大学生数学建模竞赛'
src = glob.glob(os.path.join(root, '2024', 'A-*', '*_中文.md'))[0]
text = open(src, encoding='utf-8').read()
cut = text.find('## 附录：COMAP')
appendix = text[cut:].rstrip() + '\n'

out = os.path.join(root, '资料', '规则', 'AI使用政策(中文).md')
header = ('> 来源：2024 年美赛（MCM/ICM）赛题 PDF 末尾附录，COMAP 官方政策原文\n'
          '> 原标题：Use of Large Language Models and Generative AI Tools in COMAP Contests\n\n')
body = appendix.replace('## 附录：COMAP 竞赛中大型语言模型与生成式 AI 工具的使用（Use of Large Language Models and Generative AI Tools in COMAP Contests）',
                        '# COMAP 竞赛中大型语言模型与生成式 AI 工具的使用')
open(out, 'w', encoding='utf-8').write(header + body)
print('written', out, len(header + body))

pointer = ('## 附：COMAP 的 AI 使用政策\n\n'
           '> 本题 PDF 末尾附有 COMAP《竞赛中大型语言模型与生成式 AI 工具的使用》政策全文（与题目本身无关）。'
           '为避免 6 篇重复收录，该政策已统一整理到 `资料\\规则\\AI使用政策(中文).md`。\n')

for f in sorted(glob.glob(os.path.join(root, '2024', '*', '*_中文.md'))):
    t = open(f, encoding='utf-8').read()
    i = t.find('## 附录：COMAP')
    if i < 0:
        print('no appendix', f); continue
    new = t[:i].rstrip() + '\n\n' + pointer
    open(f, 'w', encoding='utf-8').write(new)
    print('trimmed', os.path.basename(f), len(t), '->', len(new))
