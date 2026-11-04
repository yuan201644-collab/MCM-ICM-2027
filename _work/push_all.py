# -*- coding: utf-8 -*-
"""Push every local file missing on GitHub via REST API (git.exe cannot reach github.com)."""
import base64
import json
import os
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

OWNER = "yuan201644-collab"
REPO = "MCM-ICM-2027"
BRANCH = "main"
ROOT = r"D:\26年美国大学生数学建模竞赛"
API = "https://api.github.com"
MSG = "Add 12 paper digests, team division folders, and bilingual versions for 2022B-2024F"

SKIP_DIRS = {".git", ".dsh", ".workbuddy", "_work/preview", "_work/bil", "__pycache__"}
SKIP_SUFFIX = (".pyc", ".tmp")
MAX_BYTES = 45 * 1024 * 1024

TOKEN = subprocess.run(
    [r"C:\Program Files\GitHub CLI\gh.exe", "auth", "token"],
    capture_output=True, text=True, check=True).stdout.strip()


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


def local_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT).replace("\\", "/")
        if rel_dir == ".":
            rel_dir = ""
        if any(rel_dir == s or rel_dir.startswith(s + "/") for s in SKIP_DIRS):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames
                       if not any((rel_dir + "/" + d).lstrip("/") == s or (rel_dir + "/" + d).lstrip("/").startswith(s + "/")
                                  for s in SKIP_DIRS)]
        for fn in filenames:
            if fn.endswith(SKIP_SUFFIX):
                continue
            if "/work/" in ("/" + rel_dir + "/") or rel_dir.endswith("/work"):
                continue
            p = os.path.join(dirpath, fn)
            size = os.path.getsize(p)
            if size > MAX_BYTES:
                print("SKIP big:", p, round(size / 1048576, 1), "MB")
                continue
            rel = (rel_dir + "/" + fn).lstrip("/")
            if "/work/" in rel:
                continue
            out.append((rel, p, size))
    return out


def remote_paths():
    tree = call("GET", "/repos/%s/%s/git/trees/%s?recursive=1" % (OWNER, REPO, BRANCH))
    return {t["path"] for t in tree.get("tree", []) if t["type"] == "blob"}, tree["sha"]


def make_blob(item):
    rel, p, _ = item
    with open(p, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    res = call("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO),
               {"content": content, "encoding": "base64"})
    return rel, res["sha"]


def main():
    dry = "--dry" in sys.argv
    remote, head_sha = remote_paths()
    local = local_files()
    todo = [x for x in local if x[0] not in remote]
    total = sum(x[2] for x in todo)
    print("local=%d remote=%d to_add=%d size=%.1f MB" % (len(local), len(remote), len(todo), total / 1048576))
    from collections import Counter
    c = Counter(x[0].split("/")[0] for x in todo)
    for k, v in c.most_common(12):
        print("  %-12s %d" % (k, v))
    if dry:
        return
    results = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, (rel, sha) in enumerate(ex.map(make_blob, todo), 1):
            results.append({"path": rel, "mode": "100644", "type": "blob", "sha": sha})
            if i % 25 == 0 or i == len(todo):
                print("blobs %d/%d" % (i, len(todo)), flush=True)
    head = call("GET", "/repos/%s/%s/git/commits/%s" % (OWNER, REPO, head_sha))
    new_tree = call("POST", "/repos/%s/%s/git/trees" % (OWNER, REPO),
                    {"base_tree": head["tree"]["sha"], "tree": results})
    commit = call("POST", "/repos/%s/%s/git/commits" % (OWNER, REPO),
                  {"message": MSG, "tree": new_tree["sha"], "parents": [head_sha]})
    call("PATCH", "/repos/%s/%s/git/refs/heads/%s" % (OWNER, REPO, BRANCH),
         {"sha": commit["sha"], "force": False})
    print("pushed commit:", commit["sha"])


if __name__ == "__main__":
    main()
