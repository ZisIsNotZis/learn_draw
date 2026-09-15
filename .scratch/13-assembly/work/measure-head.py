#!/usr/bin/env python3
"""measure-head.py — the M2 head-region instrument: edge_f1 / coverage / color_dist on the head.

M2's gate is region-scoped (roadmap G2b, STATUS D14): the whole-frame alarm applies always, but the
detail floor is measured on the head crop the milestone owns. Those numbers were previously computed
ad-hoc in a scratch shell; this is the reusable instrument. It renders a spec (reference-free — the
whole point of G7), then calls the SAME `metrics()` the tool uses, on the whole frame and on the head
crop. Metrics are signal, never a target (invariant 4): this prints them, it does not optimise them.

Usage:
  .venv/bin/python .scratch/13-assembly/work/measure-head.py <spec.yaml> [--ref image.jpg]
  .venv/bin/python .scratch/13-assembly/work/measure-head.py <render.png> --ref image.jpg
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import draw as dw  # noqa: E402

# the head region M2's gate owns
HX0, HY0, HX1, HY1 = 400, 0, 1020, 420


def render_spec(spec: Path, out: Path) -> None:
    run = subprocess.run([sys.executable, str(ROOT / "scripts" / "relate.py"), str(spec),
                          "-o", str(out)], capture_output=True, text=True)
    if run.returncode != 0:
        sys.exit(f"relate failed:\n{run.stdout}\n{run.stderr}")
    if "TEACHER" in run.stdout or "ERROR" in run.stdout:
        print(run.stdout, file=sys.stderr)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("art", help="spec.yaml or a render .png")
    ap.add_argument("--ref", default=str(ROOT / "image.jpg"))
    ap.add_argument("--label", default=None)
    a = ap.parse_args(argv)
    ref = dw.imread(a.ref)
    art = Path(a.art).resolve()
    if art.suffix in (".yaml", ".yml"):
        tmp = Path(tempfile.mkdtemp()) / "render.png"
        render_spec(art, tmp)
        draft = dw.imread(str(tmp))
    else:
        draft = dw.imread(str(art))
    ref = dw.imread(a.ref, (draft.shape[1], draft.shape[0]))
    whole = dw.metrics(ref, draft)
    rc = ref[HY0:HY1, HX0:HX1]
    dc = draft[HY0:HY1, HX0:HX1]
    head = dw.metrics(rc, dc)
    label = a.label or art.name
    print(f"{label}")
    print(f"  whole-frame : edge_f1 {whole['edge_f1']:.3f}  coverage {whole['coverage']:.3f}  "
          f"color_dist {whole['color_dist']:.1f}  precision {whole['precision']:.3f}  "
          f"recall {whole['recall']:.3f}")
    print(f"  head region : edge_f1 {head['edge_f1']:.3f}  coverage {head['coverage']:.3f}  "
          f"color_dist {head['color_dist']:.1f}  precision {head['precision']:.3f}  "
          f"recall {head['recall']:.3f}")
    print(f"  bars        : head edge_f1 >= 0.412, coverage >= 0.692")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
