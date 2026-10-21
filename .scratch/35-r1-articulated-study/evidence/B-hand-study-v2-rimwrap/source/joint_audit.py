"""joint_audit.py - the joint measured on the picture, not a plane away from it.

README H1 replaces a joint built as tangency with a *declared* joint: a front piece, a rear
piece, and a crossing region.  The two numbers this module reports are the ones the package's
continuation criterion is written in (README `work/r1a-method-hypothesis.md` rule 2 and 3):

  * ``cross_px`` - front-piece fill inside the rear piece's **projected outline from the rear
    piece's own geometry** (the outline the picture would show if the front piece were absent,
    not the visible outline, which is exactly the pixel set the front piece covers).  Measured
    on the shipped PNG at tile resolution, so the number is a property of the picture.
  * ``contour_breaks`` - rear-piece contour points that are still inked inside the crossing
    span.  A crossing where both contours survive is a *merge*; the joint rule wants exactly
    one contour to break, the front piece's to run unbroken, so this must be 0.

Both are counted with the mesh that emitted the drawing and the PNG that was delivered from it:

    python source/build.py
    python source/joint_audit.py check/draft-fullres.png

The floor is relative to the rear piece (rule 2), never an absolute number: 1 % of the dish's
projected area, and at least 10 x stroke-width squared.
"""
from __future__ import annotations

import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build  # noqa: E402
import geo  # noqa: E402
import scene  # noqa: E402

FLOOR_FRACTION = 0.01
STROKE = build.SIL_WIDTH
INK = re.compile(r'<polyline class="(\w+)" data-part="(\w+)" data-id="(\w+)" '
                 r'data-s0="([\d.]+)" data-s1="([\d.]+)"')


def _fill(polys, w, h):
    """A boolean raster of filled polygons - no image library, so the source stays drawings only."""
    mask = np.zeros((h, w), dtype=bool)
    for pts in polys:
        p = np.asarray(pts, float)
        x0 = max(0, int(np.floor(p[:, 0].min())))
        x1 = min(w - 1, int(np.ceil(p[:, 0].max())))
        y0 = max(0, int(np.floor(p[:, 1].min())))
        y1 = min(h - 1, int(np.ceil(p[:, 1].max())))
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        inside = np.zeros(xs.shape, dtype=bool)
        for a, b in zip(p, np.roll(p, -1, axis=0)):
            cond = (a[1] > ys) != (b[1] > ys)
            with np.errstate(divide="ignore", invalid="ignore"):
                xint = a[0] + (ys - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            inside ^= cond & (xs < xint)
        mask[y0:y1 + 1, x0:x1 + 1] |= inside
    return mask


def _masks(res, w, h):
    """Boolean rasters: the rear piece's projected outline, and the front piece's fill."""
    name = scene.WRAP["name"]
    dish = _fill([q["pts"] for q in res["quads"] if q["part"] == "dish"], w, h)
    front = _fill([q["pts"] for q in res["quads"] if q["part"] == name], w, h)
    return dish, front


def _inked_runs(svg_text):
    out = {}
    for _kind, part, ident, s0, s1 in INK.findall(svg_text):
        out.setdefault((part, ident), []).append((float(s0), float(s1)))
    return out


def measure(png=None, svg=None, verbose=True):
    """The two numbers, plus the floor they are judged against.  Pure function of the files."""
    w, h = geo.CANVAS
    res = build.resolve()
    dish_mask, front_mask = _masks(res, w, h)
    outline_px = int(dish_mask.sum())
    cross = int((dish_mask & front_mask).sum())
    floor = max(FLOOR_FRACTION * outline_px, 10.0 * STROKE * STROKE)

    # rear contour that is still inked where the front piece covers it
    runs = _inked_runs(open(svg).read()) if svg else {}
    breaks = 0
    checked = 0
    name = scene.WRAP["name"]
    for c in res["curves"]:
        if c["part"] != "dish" or c["kind"] != "silhouette":
            continue
        n = len(c["pts"])
        for i, p in enumerate(c["pts"]):
            x, y = int(round(p[0])), int(round(p[1]))
            if not (0 <= x < w and 0 <= y < h) or not front_mask[y, x]:
                continue
            checked += 1
            s = i / max(1, n - 1)
            if any(a - 1e-6 <= s <= b + 1e-6 for a, b in runs.get((c["part"], c["id"]), [])):
                breaks += 1

    out = {"cross_px": cross, "floor": round(floor), "outline_px": outline_px,
           "contour_breaks": breaks, "contour_points_in_crossing": checked,
           "front_piece": name, "stroke_width": STROKE}
    if verbose:
        print(json.dumps(out, sort_keys=True))
    return out


def line(m):
    ok = m["cross_px"] >= m["floor"] and m["contour_breaks"] == 0
    return (f"joint audit: cross_px {m['cross_px']} / floor {m['floor']} "
            f"(dish outline {m['outline_px']} px, {m['cross_px'] / max(1, m['outline_px']) * 100:.2f} %), "
            f"contour_breaks {m['contour_breaks']} of {m['contour_points_in_crossing']} "
            f"contour points in the crossing ({m['front_piece']} in front) -> {'PASS' if ok else 'FAIL'}")


def main(argv):
    png = next((a for a in argv if a.endswith(".png")), "check/draft-fullres.png")
    svg = next((a for a in argv if a.endswith(".svg")), "artwork.svg")
    report = "check/report.txt"
    m = measure(png, svg)
    text = line(m)
    if "--report" in argv and os.path.exists(report):
        lines = open(report).read().splitlines()
        lines.insert(0, text + "   [1:1 image " + os.path.relpath(png) + "]")
        open(report, "w").write("\n".join(lines) + "\n")
        print("report line 1:", text)
    return 0 if m["cross_px"] >= m["floor"] and m["contour_breaks"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
