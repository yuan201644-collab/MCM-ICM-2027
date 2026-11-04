# -*- coding: utf-8 -*-
"""Push files to GitHub via REST API when git.exe cannot reach github.com:443."""
import base64
import json
import subprocess
import urllib.request

OWNER = "yuan201644-collab"
REPO = "MCM-ICM-2027"
BRANCH = "main"
MSG = "Add 2209466 framework analysis, exact-layout docx, and PDF-to-docx converters"
ROOT = r"D:\26年美国大学生数学建模竞赛"
FILES = [
    "研读材料/12篇研读/2022A_2209466_自行车功率曲线/框架解剖.md",
    "研读材料/12篇研读/2022A_2209466_自行车功率曲线/2209466_版式还原.docx",
    "_work/outline_2209466.py",
    "_work/pdf2docx_2209466.py",
    "_work/pdf2docx_exact.py",
    "_work/pdf2docx_exact2.py",
    "_work/pdf2docx_exact3.py",
]

TOKEN = subprocess.run(
    [r"C:\Program Files\GitHub CLI\gh.exe", "auth", "token"],
    capture_output=True, text=True, check=True).stdout.strip()
API = "https://api.github.com"


def call(method, path, payload=None):
    url = API + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "dsh-agent")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))


print("token ok, len", len(TOKEN))
head = call("GET", f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}")
head_sha = head["object"]["sha"]
tree_sha = call("GET", f"/repos/{OWNER}/{REPO}/git/commits/{head_sha}")["tree"]["sha"]
print("head", head_sha[:8], "tree", tree_sha[:8])

entries = []
for rel in FILES:
    with open(ROOT + "\\" + rel.replace("/", "\\"), "rb") as f:
        blob = f.read()
    res = call("POST", f"/repos/{OWNER}/{REPO}/git/blobs",
               {"content": base64.b64encode(blob).decode(), "encoding": "base64"})
    entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": res["sha"]})
    print("blob", rel.split("/")[-1], len(blob), "bytes ->", res["sha"][:8])

tree = call("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"base_tree": tree_sha, "tree": entries})
commit = call("POST", f"/repos/{OWNER}/{REPO}/git/commits",
              {"message": MSG, "tree": tree["sha"], "parents": [head_sha]})
call("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
     {"sha": commit["sha"], "force": False})
print("new commit", commit["sha"])
