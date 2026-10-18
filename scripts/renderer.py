#!/usr/bin/env python3
"""renderer.py — resolve the headless renderer every tool renders through.

The playwright cache stores one directory per downloaded revision, so a pinned
revision path silently breaks after any browser update. Resolution order:
$CHROME_HEADLESS_SHELL, then the newest chromium_headless_shell-* in the cache.
"""
import glob
import os
import sys

CACHE = os.path.expanduser("~/.cache/ms-playwright")
SUFFIX = os.path.join("chrome-headless-shell-linux64", "chrome-headless-shell")


def _revision(path):
    tail = os.path.basename(path).rsplit("-", 1)[-1]
    return int(tail) if tail.isdigit() else -1


def chrome_path():
    override = os.environ.get("CHROME_HEADLESS_SHELL")
    if override:
        return override
    found = [p for p in glob.glob(os.path.join(CACHE, "chromium_headless_shell-*"))
             if os.path.exists(os.path.join(p, SUFFIX))]
    if not found:
        sys.exit(f"renderer not found: no chromium_headless_shell-*/{SUFFIX} under {CACHE}; "
                 f"set CHROME_HEADLESS_SHELL to a chrome-headless-shell binary")
    return os.path.join(max(found, key=_revision), SUFFIX)
