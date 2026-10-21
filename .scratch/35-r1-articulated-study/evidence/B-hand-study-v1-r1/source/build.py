"""build.py - compile the study into artwork.svg.  Deterministic: no clock, no randomness.

The output is the drawing, not a preview.  Fills come from each quad's own surface normal
(quantised Lambert, so the shading is a flat cel tone rather than a gradient); every stroke is
a curve derived from the mesh - a silhouette (zero set of vertex normal . view) or a crease
(an edge whose two faces differ sharply) - and is clipped against a depth buffer computed from
the same quads, so a rear edge is emitted *absent* wherever a nearer part of the drawing covers
it, rather than being painted over.

    python source/build.py                     # -> artwork.svg
    python source/build.py --no-depth-break    # negative control: every stroke runs through
    python source/build.py --lift 30           # optional second image: dish raised 30 px
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
EVIDENCE = os.path.dirname(HERE)

import geo  # noqa: E402
import scene  # noqa: E402

TITLE = "B-hand-study-v1"
INFLATE = 0.45          # px: closes the renderer's antialias seam between adjacent quads
STROKE_EPS = 1.4        # px: a stroke counts as nearest while it is within this of the buffer
SIL_WIDTH = 3.2
CREASE_WIDTH = 2.4
TOP_MARGIN = 36.0

MATERIALS = (
    {"name": "skin", "base": (231, 179, 141), "stroke": (114, 74, 55)},
    {"name": "dish_out", "base": (188, 199, 198), "stroke": (74, 88, 90)},
    {"name": "dish_in", "base": (228, 233, 227), "stroke": (74, 88, 90)},
)
BACKGROUND = (243, 238, 230)


def framing(parts):
    """Place the dish in the frame: centred across, its top edge a fixed margin down.

    Computed from the dish's own projected extent rather than typed, so a change to the pose
    re-frames the drawing instead of leaving it half out of the canvas.  The hand is not used
    for framing on purpose: it is allowed to leave the frame at the bottom.
    """
    geo.OX, geo.OY = 0.0, 0.0
    dish_scr = geo.project([p for n, p in parts if n == "dish"][0].v).reshape(-1, 3)
    geo.OX = geo.CANVAS[0] * 0.5 - float(dish_scr[:, 0].min() + dish_scr[:, 0].max()) * 0.5
    geo.OY = TOP_MARGIN - float(dish_scr[:, 1].min())
    return geo.OX, geo.OY


def _screen_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return abs(a) * 0.5


def fills(parts, break_depth=True):
    """Front-facing quads, toned by their own normal, emitted in painter order."""
    out = []
    for name, patch in parts:
        corners, _I, _J, _I1, _J1 = patch.quads()
        normals, area2 = patch.quad_normals()
        mats = patch.quad_mat()
        scr = geo.project(corners)
        front = (normals @ geo.VIEW) < 0.0
        for k in range(corners.shape[0]):
            if not front[k] or area2[k] < 1e-9:
                continue
            if _screen_area(scr[k][:, :2]) < 2.0:
                continue        # sub-pixel quads near the dish's axis only show their inflation
            n_hat = normals[k] / area2[k]
            shade = geo.AMBIENT + (1.0 - geo.AMBIENT) * max(0.0, float(n_hat @ geo.LIGHT))
            colour = geo.shaded(MATERIALS[mats[k]]["base"], shade)
            pts = scr[k][:, :2]
            # one screen winding for every quad, so subpaths union under the nonzero rule
            area = 0.0
            for a in range(4):
                x0, y0 = pts[a]
                x1, y1 = pts[(a + 1) % 4]
                area += x0 * y1 - x1 * y0
            ordered = pts if area > 0 else pts[::-1]
            cx, cy = ordered[:, 0].mean(), ordered[:, 1].mean()
            grown = []
            for x, y in ordered:
                dx, dy = x - cx, y - cy
                d = np.hypot(dx, dy) or 1.0
                grown.append((x + INFLATE * dx / d, y + INFLATE * dy / d))
            out.append({"part": name, "colour": colour, "pts": grown, "scr": scr[k],
                        "z": float(scr[k][:, 2].mean()), "mat": int(mats[k])})
    out.sort(key=lambda q: -q["z"])
    return out


CONTOUR_RADIUS = 3      # px: a contour point is inked only if the drawing stops this near it


def _borders_the_drawing(pt, covered, r=CONTOUR_RADIUS):
    """True if an uncovered pixel lies within `r` of this point.

    A surface's zero-normal line is not always the drawing's edge: inside a bowl the surface
    turns away from the camera and becomes a horizon *inside* the drawn shape.  Inking that
    would draw a false second rim.  The rule here is the drawing's own: a contour is inked where
    the drawing stops, and a horizon with surface painted on every side is not.
    """
    h, w = covered.shape
    x, y = int(round(pt[0])), int(round(pt[1]))
    if not (0 <= x < w and 0 <= y < h):
        return False
    x0, x1 = max(0, x - r), min(w, x + r + 1)
    y0, y1 = max(0, y - r), min(h, y + r + 1)
    return not bool(covered[y0:y1, x0:x1].all())


def curves(parts):
    """Every stroke the drawing carries, whole: the mesh's own contours, then its own folds."""
    out = []
    for name, patch in parts:
        for i, line in enumerate(patch.silhouette()):
            out.append({"part": name, "id": f"sil{i}", "kind": "silhouette", "pts": line,
                        "z": float(line[:, 2].mean())})
        for i, line in enumerate(patch.creases()):
            out.append({"part": name, "id": f"crease{i}", "kind": "crease", "pts": line,
                        "z": float(line[:, 2].mean())})
    return out


def visible_runs(curve, zbuf, covered, break_depth):
    """The runs of one stroke that survive visibility, as index ranges into its own points.

    Two criteria, both computed: the stroke's own surface must be the nearest thing at that
    pixel (depth), and - for a contour only - the drawing must stop within a few pixels of it
    (coverage), so a surface horizon inside the shape is left to the shading.  With
    `break_depth` off, neither runs: the negative control emits every stroke whole.
    """
    n = len(curve["pts"])
    if not break_depth:
        return [(0, n - 1)] if n > 1 else []
    h, w = zbuf.shape
    ok = np.zeros(n, dtype=bool)
    for i, p in enumerate(curve["pts"]):
        x, y, z = int(math.floor(p[0])), int(math.floor(p[1])), p[2]
        inside = 0 <= x < w and 0 <= y < h
        ok[i] = inside and z <= zbuf[y, x] + STROKE_EPS
        if ok[i] and curve["kind"] == "silhouette":
            ok[i] = _borders_the_drawing(p, covered)
    runs, start = [], None
    for i, v in enumerate(ok):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - 1 > start:
                runs.append((start, i - 1))
            start = None
    if start is not None and n - 1 > start:
        runs.append((start, n - 1))
    return runs


def resolve(break_depth=True, lift=0.0):
    parts, rings = scene.parts(lift=lift)
    ox, oy = framing(parts)
    quad_list = fills(parts, break_depth)
    zbuf = geo.depth_buffer([q["scr"] for q in quad_list])
    covered = np.isfinite(zbuf)
    curve_list = curves(parts)
    for c in curve_list:
        c["runs"] = visible_runs(c, zbuf, covered, break_depth)
    curve_list.sort(key=lambda c: -c["z"])
    return {"parts": parts, "rings": rings, "quads": quad_list, "curves": curve_list,
            "zbuf": zbuf, "framing": (ox, oy), "lift": float(lift)}


def _pt(p):
    return geo.fmt_pt(p)


def svg(res):
    w, h = geo.CANVAS
    n_strokes = sum(len(c["runs"]) for c in res["curves"])
    n_quads = len(res["quads"])
    n_sil = sum(1 for c in res["curves"] if c["kind"] == "silhouette")
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
        % (w, h, w, h),
        "<!-- %s: one hand supporting one shallow dish. Compiler output of source/build.py; "
        "edit the source. Framing %.2f,%.2f. -->" % (TITLE, res["framing"][0], res["framing"][1]),
        '<desc>Object study: a hand holding a shallow dish from below, filling the frame. '
        '%d front-facing quads, %d stroke curves (%d silhouettes), %d emitted runs, '
        'visibility from a depth buffer.</desc>'
        % (n_quads, len(res["curves"]), n_sil, n_strokes),
        '<rect id="field" x="0" y="0" width="%d" height="%d" fill="%s"/>'
        % (w, h, geo.hexc(BACKGROUND)),
        '<g id="fills" stroke="none">',
    ]
    # runs of equal colour in painter order become one path: subpaths of one path union, so
    # adjacent quads cannot show the renderer's antialias seam between them
    run_colour, run_paths = None, []
    for q in res["quads"]:
        if q["colour"] != run_colour and run_paths:
            out.append('<path fill="%s" d="%s"/>' % (run_colour, " ".join(run_paths)))
            run_paths = []
        run_colour = q["colour"]
        run_paths.append("M %s L %s L %s L %s Z" % tuple(_pt(p) for p in q["pts"]))
    if run_paths:
        out.append('<path fill="%s" d="%s"/>' % (run_colour, " ".join(run_paths)))
    out.append("</g>")
    out.append('<g id="edges" fill="none" stroke-linecap="round" stroke-linejoin="round">')
    for c in res["curves"]:
        colour = geo.hexc(MATERIALS[0]["stroke"] if c["part"] not in ("dish",)
                          else MATERIALS[1]["stroke"])
        width = SIL_WIDTH if c["kind"] == "silhouette" else CREASE_WIDTH
        n = len(c["pts"])
        for i0, i1 in c["runs"]:
            pts = c["pts"][i0:i1 + 1]
            out.append('<polyline class="%s" data-part="%s" data-id="%s" data-s0="%.4f" '
                       'data-s1="%.4f" stroke="%s" stroke-width="%.1f" points="%s"/>'
                       % (c["kind"], c["part"], c["id"], i0 / max(1, n - 1), i1 / max(1, n - 1),
                          colour, width, " ".join(_pt(p) for p in pts)))
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(EVIDENCE, "artwork.svg"))
    ap.add_argument("--no-depth-break", action="store_true",
                    help="negative control: emit every stroke unbroken")
    ap.add_argument("--lift", type=float, default=0.0,
                    help="optional second image: raise the dish this many px after the hand is built")
    a = ap.parse_args()
    res = resolve(break_depth=not a.no_depth_break, lift=a.lift)
    text = svg(res)
    with open(a.out, "w") as fh:
        fh.write(text)
    print(f"wrote {a.out}: {len(res['quads'])} quads, {len(res['curves'])} stroke curves, "
          f"{sum(len(c['runs']) for c in res['curves'])} runs")


if __name__ == "__main__":
    main()
