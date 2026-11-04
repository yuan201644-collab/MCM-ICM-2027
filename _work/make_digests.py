# -*- coding: utf-8 -*-
"""Compact digest for a list of papers: summary, section flow, captions, tool hits, weakness lines."""
import os
import re

SRC = r"D:\26年美国大学生数学建模竞赛\_work\全文"
OUT = r"D:\26年美国大学生数学建模竞赛\_work\digests"
os.makedirs(OUT, exist_ok=True)

TARGETS = [
    "2022C_2203120", "2022D_2215444", "2022E_2223495", "2022F_2224021",
    "2024A_2400996", "2024B_2419984", "2024C_2401298", "2024D_2429211",
    "2024E_2413552", "2024F_2409949",
]

TOOLS = ["linear programming", "integer programming", "dynamic programming",
         "regression", "ARIMA", "LSTM", "neural network", "random forest",
         "XGBoost", "Markov", "Monte Carlo", "simulation", "differential equation",
         "ODE", "PDE", "game theory", "auction", "network flow", "graph",
         "clustering", "PCA", "AHP", "entropy weight", "TOPSIS", "fuzzy",
         "hypothesis test", "t-test", "Bayesian", "sensitivity analysis",
         "genetic algorithm", "simulated annealing", "particle swarm",
         "multi-objective", "Pareto", "queueing", "cellular automata",
         "system dynamics", "logistic", "SIR", "kriging", "GWR", "spatial"]

WEAK = ["limitation", "due to time", "future work", "shortcoming", "not consider",
        "we did not", "cannot", "further research", "weakness"]


def digest(name):
    raw = open(os.path.join(SRC, name + ".txt"), encoding="utf-8").read()
    parts = re.split(r"<<<PAGE (\d+)>>>", raw)
    blocks = [(int(parts[i]), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    out = []
    out.append(f"### {name}  pages={len(blocks)}")
    first = blocks[0][1]
    lines = [l.strip() for l in first.splitlines() if l.strip()]
    out.append("TITLE: " + " / ".join(lines[:8])[:200])
    idx = next((i for i, l in enumerate(lines) if l.lower() in ("summary", "abstract")), 3)
    out.append("SUMMARY: " + " ".join(lines[idx + 1: idx + 14])[:900])
    out.append("FLOW:")
    for pno, txt in blocks:
        ls = [l.strip() for l in txt.splitlines() if l.strip()]
        if ls:
            out.append(f"  p{pno}: " + " | ".join(ls[:4])[:150])
    caps = []
    for pno, txt in blocks:
        for line in txt.splitlines():
            if re.search(r"(Table|Figure)\s*\d+\s*[:.]", line) and len(line) < 110:
                caps.append(f"  p{pno} {line.strip()[:90]}")
    out.append("CAPTIONS:")
    out.extend(caps[:20])
    low = raw.lower()
    hits = [t for t in TOOLS if t.lower() in low]
    out.append("TOOLS: " + ", ".join(hits))
    out.append("WEAK LINES:")
    n = 0
    for pno, txt in blocks:
        for line in txt.splitlines():
            s = line.strip()
            if any(w in s.lower() for w in WEAK) and 40 < len(s) < 220:
                out.append(f"  p{pno}: {s[:200]}")
                n += 1
                if n >= 6:
                    break
        if n >= 6:
            break
    text = "\n".join(out)
    open(os.path.join(OUT, name + ".txt"), "w", encoding="utf-8").write(text)
    return len(text)


for t in TARGETS:
    try:
        print(t, digest(t), "chars")
    except Exception as e:
        print(t, "ERR", e)
