"""Manifest over the real file set: write it, verify it, and fail when a file is dropped.

    python source/manifest.py --write     # rewrites manifest.json and manifest.sha256
    python source/manifest.py --check     # verifies every listed file by hash and size

Both files list the same set.  `manifest.sha256` is `sha256sum -c` compatible, so the check does
not depend on this script staying correct.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
SELF = {"manifest.json", "manifest.sha256"}
TREES = ("source", "tests", "check")
SINGLES = ("artwork.svg", "artwork.png", "README.md")


def file_set():
    out = []
    for name in SINGLES:
        if os.path.exists(os.path.join(EVIDENCE, name)):
            out.append(name)
    for tree in TREES:
        base = os.path.join(EVIDENCE, tree)
        for root, _dirs, files in os.walk(base):
            for f in sorted(files):
                if f.endswith(".pyc") or f == "__pycache__":
                    continue
                rel = os.path.relpath(os.path.join(root, f), EVIDENCE)
                if rel not in SELF:
                    out.append(rel)
    return sorted(out)


def digest(rel):
    with open(os.path.join(EVIDENCE, rel), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def write():
    rows = [{"path": rel, "sha256": digest(rel),
             "bytes": os.path.getsize(os.path.join(EVIDENCE, rel))} for rel in file_set()]
    with open(os.path.join(EVIDENCE, "manifest.json"), "w") as fh:
        json.dump({"evidence": "B-hand-study-v1", "files": rows}, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(EVIDENCE, "manifest.sha256"), "w") as fh:
        for r in rows:
            fh.write(f"{r['sha256']}  {r['path']}\n")
    return rows


def check():
    with open(os.path.join(EVIDENCE, "manifest.json")) as fh:
        rows = json.load(fh)["files"]
    listed = [r["path"] for r in rows]
    problems = []
    for r in rows:
        p = os.path.join(EVIDENCE, r["path"])
        if not os.path.exists(p):
            problems.append(f"missing: {r['path']}")
            continue
        if digest(r["path"]) != r["sha256"]:
            problems.append(f"hash mismatch: {r['path']}")
        if os.path.getsize(p) != r["bytes"]:
            problems.append(f"size mismatch: {r['path']}")
    for u in sorted(set(file_set()) - set(listed)):
        problems.append(f"not listed: {u}")
    return rows, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.write:
        rows = write()
        print(f"manifest: wrote {len(rows)} entries")
        return 0
    rows, problems = check()
    if problems:
        print("manifest: FAILED")
        for p in problems:
            print("  " + p)
        return 1
    print(f"manifest: {len(rows)}/{len(rows)} entries OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
