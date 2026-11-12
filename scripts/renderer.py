#!/usr/bin/env python3
"""renderer.py — resolve the headless renderer every tool renders through.

The playwright cache stores one directory per downloaded revision, so a pinned
revision path silently breaks after any browser update. Resolution order:
$CHROME_HEADLESS_SHELL, then the newest chromium_headless_shell-* in the cache.
"""
import glob
import os
import sys
from pathlib import Path
import shutil
import subprocess
import tempfile

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
        local = [shutil.which("msedge"), shutil.which("chromium"), shutil.which("google-chrome")]
        if os.name == "nt":
            local += ["C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
                      "C:/Program Files/Microsoft/Edge/Application/msedge.exe"]
        installed = next((p for p in local if p and os.path.isfile(p)), None)
        if installed:
            return installed
        sys.exit(f"renderer not found: no cached or installed Chromium; "
                 f"set CHROME_HEADLESS_SHELL to a chrome-headless-shell binary")
    return os.path.join(max(found, key=_revision), SUFFIX)


def screenshot(source, target, size, browser=None):
    """Isolated CPU browser profile, shared by legacy and studio renderers."""
    output = Path(target).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="learn-draw-cpu-") as profile:
        rendered = Path(profile) / "render.png"
        subprocess.run([browser or chrome_path(), "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--user-data-dir=" + profile, "--screenshot=" + str(rendered),
                        f"--window-size={size[0]},{size[1]}", Path(source).resolve().as_uri()],
                       check=True, capture_output=True, timeout=60)
        if not rendered.exists() or rendered.stat().st_size == 0:
            raise RuntimeError("browser produced no screenshot")
        shutil.copyfile(rendered, output)
