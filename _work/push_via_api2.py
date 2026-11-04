# -*- coding: utf-8 -*-
"""Push the files changed in HEAD to GitHub via REST API (git.exe cannot reach github.com:443)."""
import base64
import json
import subprocess
import urllib.request
from concurrent.futures import ThreadPoolExecutor

OWNER = "yuan201644-collab"
REPO = "MCM-ICM-2027"
BRANCH = "main"
ROOT = r"D:\26年美国大学生数学建模竞赛"
MSG = ("Add bilingual EN-ZH edition of 2209466 (43 pages): full translation, "
       "formulas, tables and composite figures restored as images")

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
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode("utf-8"))


files = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                       cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
print("files to push:", len(files))

head = call("GET", f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}")
head_sha = head["object"]["sha"]
tree_sha = call("GET", f"/repos/{OWNER}/{REPO}/git/commits/{head_sha}")["tree"]["sha"]
print("remote head", head_sha[:8], "tree", tree_sha[:8])


def upload(rel):
    with open(ROOT + "\\" + rel.replace("/", "\\"), "rb") as f:
        blob = f.read()
    res = call("POST", f"/repos/{OWNER}/{REPO}/git/blobs",
               {"content": base64.b64encode(blob).decode(), "encoding": "base64"})
    return {"path": rel, "mode": "100644", "type": "blob", "sha": res["sha"]}


with ThreadPoolExecutor(max_workers=6) as ex:
    entries = list(ex.map(upload, files))
print("blobs uploaded:", len(entries))

tree = call("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"base_tree": tree_sha, "tree": entries})
commit = call("POST", f"/repos/{OWNER}/{REPO}/git/commits",
              {"message": MSG, "tree": tree["sha"], "parents": [head_sha]})
call("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
     {"sha": commit["sha"], "force": False})
print("new commit", commit["sha"])
print("remote tree", tree["sha"])
print("local tree ", subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                    capture_output=True, text=True).stdout.strip())
