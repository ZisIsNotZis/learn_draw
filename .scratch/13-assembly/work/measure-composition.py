#!/usr/bin/env python3
"""measure-composition.py — the G3 placement instrument (roadmap).

Two jobs, both measurements, never a verdict:

  reference                      measure the target's own composition: per-colour-mass bbox,
                                 centroid and area% -> the numbers that go into the spec's `vars:`
  compare <render> [<render>...]  compare renders against those masses (the placement check), and
                                 the coarse-grid colour-mass distance (the tie-breaker when two
                                 reviewers disagree — roadmap, "if two reviewers disagree, measure")

Usage:
    .venv/bin/python .scratch/13-assembly/work/measure-composition.py reference
    .venv/bin/python .scratch/13-assembly/work/measure-composition.py compare \\
        .scratch/13-assembly/work/m1-v3.png .scratch/00-tooling/baseline/best.png

Provenance note: the probes below are single colours sampled from image.jpg with the project's
`draw measure --point`, then dilated to the smallest tolerance that recovers the whole element
without bleeding into the background. Colours repeat in this palette, so a few entries are
region-restricted — that restriction is part of the measurement, not a fudge.
"""
import os
import sys

import cv2
import numpy as np

REF = "image.jpg"

# element -> (BGR probe, tolerance, region or None)
PROBES = {
    "head/face skin": ((216, 233, 242), 16, (400, 120, 900, 460)),
    "neck":           ((216, 233, 242), 20, (600, 370, 800, 470)),
    "hat crown navy": ((100, 63, 51), 30, (450, 0, 800, 220)),
    "hat brim teal":  ((175, 158, 87), 32, (0, 0, 1024, 300)),
    "hat brim navy":  ((100, 63, 51), 28, (0, 0, 1024, 300)),
    "hair blue":      ((171, 116, 57), 45, None),
    "blouse pale":    ((221, 235, 221), 14, (600, 420, 950, 700)),
    "skirt pale":     ((216, 226, 210), 18, (520, 600, 1024, 900)),
    "bow magenta":    ((129, 80, 211), 45, (400, 400, 900, 700)),
    "skirt dark":     ((95, 68, 41), 34, (0, 600, 1024, 1024)),
    "mint field":     ((193, 204, 125), 34, None),
    "petal pink":     ((150, 140, 235), 55, (0, 600, 600, 1024)),
    "ribbon blue":    ((165, 120, 70), 55, (0, 150, 470, 750)),
}


def load(path, size=(1024, 1024)):
    im = cv2.imread(path)
    if im is None:
        raise SystemExit(f"measure-composition: cannot read {path}")
    if (im.shape[1], im.shape[0]) != size:
        im = cv2.resize(im, size, interpolation=cv2.INTER_AREA)
    return im.astype(np.int16)


def components(im, probe, tol, region=None, minarea=1200, top=3):
    d = np.linalg.norm(im - np.array(probe, np.int16), axis=2)
    m = (d < tol).astype(np.uint8)
    if region:
        x0, y0, x1, y1 = region
        keep = np.zeros_like(m)
        keep[y0:y1, x0:x1] = 1
        m &= keep
    n, _, stats, centroid = cv2.connectedComponentsWithStats(m, 8)
    found = [(stats[i, 4], stats[i, 0], stats[i, 1], stats[i, 2], stats[i, 3], centroid[i])
             for i in range(1, n)]
    found.sort(reverse=True)
    return [f for f in found if f[0] >= minarea][:top]


def mass(im, probe, tol, region=None):
    """Whole-element centroid + area%, region-restricted if the probe needs it."""
    d = np.linalg.norm(im - np.array(probe, np.int16), axis=2)
    m = d < tol
    if region:
        x0, y0, x1, y1 = region
        keep = np.zeros_like(m)
        keep[y0:y1, x0:x1] = 1
        m &= keep
    if m.sum() < 500:
        return None
    ys, xs = np.nonzero(m)
    return xs.mean() / 1024, ys.mean() / 1024, 100 * m.mean()


def grid_distance(ref, draft, cell):
    """Coarse-grid colour-mass distance: how far apart the mass distributions are."""
    h = w = 1024 // cell
    g_ref = ref[:h * cell, :w * cell].reshape(h, cell, w, cell, 3).mean(axis=(1, 3))
    g_dr = draft[:h * cell, :w * cell].reshape(h, cell, w, cell, 3).mean(axis=(1, 3))
    return float(np.linalg.norm(g_ref - g_dr, axis=2).mean())


def cmd_reference(ref):
    print(f"reference composition — {REF} (bbox is x0,y0-x1,y1 in 1024-space)")
    for name, (probe, tol, region) in PROBES.items():
        found = components(ref, probe, tol, region)
        if not found:
            print(f"  {name:16s} (none)")
            continue
        for j, (a, x, y, w, h, c) in enumerate(found):
            print("  {:16s} area {:6d}  {:4d},{:4d} - {:4d},{:4d}  centre ({:4.0f},{:4.0f})  {}x{}".format(
                name if j == 0 else "", a, x, y, x + w, y + h, c[0], c[1], w, h))


def cmd_compare(ref, paths):
    base = os.path.basename(REF)
    print(f"placement check vs {base} (centroid as frame fraction, then area%)")
    head = "  {:16s}".format("element") + "".join(f"  {os.path.basename(p)[:22]:>24s}" for p in [base] + paths)
    print(head)
    for name, (probe, tol, region) in PROBES.items():
        row = "  {:16s}".format(name)
        for im in [ref] + [load(p) for p in paths]:
            v = mass(im, probe, tol, region)
            row += "  {:>24s}".format("--" if v is None else "({:.3f},{:.3f}) {:4.1f}%".format(*v))
        print(row)
    print("\ncoarse-grid colour-mass distance (lower = closer to the reference)")
    for cell in (64, 128):
        row = "  {:3d}px cells ({:2d}x{:2d}):  ".format(cell, 1024 // cell, 1024 // cell)
        row += "  ".join(f"{os.path.basename(p)[:22]} {grid_distance(ref, load(p), cell):6.1f}"
                         for p in paths)
        print(row)


def main(argv):
    if len(argv) < 2 or argv[1] not in ("reference", "compare"):
        raise SystemExit(__doc__)
    ref = load(REF)
    if argv[1] == "reference":
        cmd_reference(ref)
    else:
        if len(argv) < 3:
            raise SystemExit("compare needs at least one render path")
        cmd_compare(ref, argv[2:])


if __name__ == "__main__":
    main(sys.argv)
