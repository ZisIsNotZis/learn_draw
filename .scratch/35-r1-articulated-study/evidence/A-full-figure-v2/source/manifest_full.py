#!/usr/bin/env python3
"""Hash every tracked file of this package into manifest.sha256, and verify it.

    .venv/bin/python .../A-full-figure-v1/source/manifest_full.py            # write
    .venv/bin/python .../A-full-figure-v1/source/manifest_full.py --check    # verify

The manifest covers what a reader needs to rebuild the figure, so a revision is a set
of bytes and not a directory that happens to exist today.  It excludes itself.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", "check"}
SKIP_FILES = {"manifest.sha256", "manifest.json"}


def files():
    for path in sorted(PKG.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(PKG).parts):
            continue
        if path.name in SKIP_FILES:
            continue
        yield path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    check = "--check" in sys.argv
    rows = [(digest(p), str(p.relative_to(PKG))) for p in files()]
    text = "".join(f"{h}  {rel}\n" for h, rel in rows)
    manifest = PKG / "manifest.sha256"
    if check:
        if not manifest.exists():
            print("no manifest", file=sys.stderr)
            return 1
        if manifest.read_text(encoding="utf-8") != text:
            print("MANIFEST MISMATCH: the tree differs from manifest.sha256", file=sys.stderr)
            return 1
        print(f"{len(rows)}/{len(rows)} entries OK")
        return 0
    manifest.write_text(text, encoding="utf-8")
    print(f"wrote {len(rows)} entries to manifest.sha256")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
