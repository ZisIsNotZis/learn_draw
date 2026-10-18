"""Compile the bow study into artwork.svg.  Deterministic: no clock, no randomness.

The output is the drawing, not a preview: fills come from each triangle's own projected
winding, and every stroke is tested against a depth buffer computed from the same
triangles, so a rear edge is emitted broken wherever a nearer part of the ribbon covers it.

    python source/build.py                     # -> artwork.svg
    python source/build.py --no-depth-break    # negative control: rear edges run through
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "parts"))

import bow  # noqa: E402
from ribbon import depth_buffer, signed_area, visible_runs  # noqa: E402

RAIL_SAMPLES = 620
CREASE_SAMPLES = 13
INFLATE = 0.8


def _fmt(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def resolve(break_depth=True):
    """Build the drawing: fills in painter order, plus the visible runs of every stroke."""
    art = bow.build()
    st, tris = art["strip"], art["tris"]
    if not break_depth:
        # the mutation the crossing test must catch: remove the depth separation itself, so
        # no crossing has a break and every stroke is emitted unbroken
        st.p[:, 2] = 0.0
    h_px, w_px = bow.CANVAS[1], bow.CANVAS[0]
    zbuf = depth_buffer(st, tris, w_px, h_px)
    eps = art["thickness"] * 0.45
    # A stroke is covered if a nearer surface is within its own half-width: at a crossing the
    # front edge covers the rear one even where the front triangle's interior does not reach
    # the rear stroke's pixel.  Testing against a locally-nearest depth is what breaks the
    # rear edge at the crossing instead of relying on paint order.
    near = zbuf.copy()
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx == 0 and dy == 0:
                continue
            shifted = np.full_like(zbuf, np.inf)
            ys = slice(max(0, dy), zbuf.shape[0] + min(0, dy))
            xs = slice(max(0, dx), zbuf.shape[1] + min(0, dx))
            sys_ = slice(max(0, -dy), zbuf.shape[0] + min(0, -dy))
            sxs = slice(max(0, -dx), zbuf.shape[1] + min(0, -dx))
            shifted[ys, xs] = zbuf[sys_, sxs]
            np.minimum(near, shifted, out=near)

    fills = []
    for tri in tris:
        pts = np.array([st.point(i, v) for i, v in tri])
        area = signed_area(pts[0, :2], pts[1, :2], pts[2, :2])
        if abs(area) < 1e-6:
            continue
        forward = area < 0.0          # y grows downward, so a viewer-facing face sweeps negative
        # Inflate by INFLATE px about the centroid before emitting: adjacent triangles share
        # their vertices exactly, and the renderer's antialiasing otherwise leaves a
        # background-coloured sliver between them (measured: fans of cracks at both folds,
        # where the strip is edge-on and the triangles are long and thin).  The inflation
        # moves each edge by <1 px and cannot change a triangle's winding.
        cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
        grown = []
        for p in pts:
            dx, dy = p[0] - cx, p[1] - cy
            n = math.hypot(dx, dy) or 1.0
            grown.append((p[0] + INFLATE * dx / n, p[1] + INFLATE * dy / n))
        fills.append({
            "points": grown,
            "z": float(pts[:, 2].mean()),
            "face": "front" if forward else "back",
            "u0": st.u[tri[0][0]],
            "u1": st.u[tri[2][0]],
            "area": abs(area),
        })
    fills.sort(key=lambda f: -f["z"])   # far to near

    rails = []
    for label, v in (("L", 1.0), ("R", -1.0)):
        pts3 = np.array([st.point(i, v) for i in range(len(st.u))])
        runs = ([(0, len(pts3) - 1)] if not break_depth
                else visible_runs(pts3, near, eps))
        for i0, i1 in runs:
            rails.append({
                "rail": label,
                "z": float(pts3[i0:i1 + 1][:, 2].mean()),
                "s0": float(st.u[i0]), "s1": float(st.u[i1]),
                "points": [(p[0], p[1]) for p in pts3[i0:i1 + 1]],
            })

    creases = []
    for idx, (u, v0, v1, curve) in enumerate(art["creases"]):
        ts = np.linspace(0.0, 1.0, CREASE_SAMPLES)
        vs = v0 + (v1 - v0) * ts
        pts3 = np.array([st.sample(u + curve * math.sin(math.pi * t), v)
                         for t, v in zip(ts, vs)])
        runs = ([(0, len(pts3) - 1)] if not break_depth
                else visible_runs(pts3, near, eps))
        for i0, i1 in runs:
            creases.append({
                "mark": idx, "u": u,
                "points": [(p[0], p[1]) for p in pts3[i0:i1 + 1]],
            })

    return {"art": art, "fills": fills, "rails": rails, "creases": creases,
            "zbuf": zbuf, "eps": eps}


def svg(res):
    st = res["art"]["strip"]
    n_back = sum(1 for f in res["fills"] if f["face"] == "back")
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d">' % (bow.CANVAS[0], bow.CANVAS[1], bow.CANVAS[0], bow.CANVAS[1]),
        "<!-- A-bow-study-v1: one continuous ribbon, knot -> left loop -> knot -> right "
        "loop -> knot -> two tails. Compiler output of source/build.py; edit the source. -->",
        '<desc>Object study: a ribbon tied in a bow, filling the frame. %d stations, one '
        'width field, depth-resolved crossings (%d back-facing faces).</desc>'
        % (len(st.u), n_back),
        '<rect id="field" x="0" y="0" width="%d" height="%d" fill="%s"/>'
        % (bow.CANVAS[0], bow.CANVAS[1], bow.PALETTE["bg"]),
        '<g id="ribbon" stroke-linejoin="round">',
    ]
    for f in res["fills"]:
        colour = bow.PALETTE["front"] if f["face"] == "front" else bow.PALETTE["back"]
        # stroke the polygon in its own fill: adjacent triangles share coordinates, and
        # without an overlap the renderer's antialiasing draws a hairline seam between them
        # (measured on this drawing: a radial fan of seams across every lobe).
        # Stroke the polygon in its own fill so adjacent triangles cannot show the
        # renderer's antialiasing seam (measured: a radial fan across every lobe).  A
        # sliver narrower than the stroke is left unstroked: its long edges, drawn, are
        # themselves the fan (measured at the two folds before this guard).
        stroke = ' stroke="%s" stroke-width="2.6"' % colour
        out.append('<polygon class="face-%s" data-u0="%.4f" data-u1="%.4f" points="%s" '
                   'fill="%s"%s/>' % (f["face"], f["u0"], f["u1"], _fmt(f["points"]),
                                      colour, stroke))
    out.append("</g>")
    out.append('<g id="rails" fill="none" stroke="%s" stroke-width="3.4" '
               'stroke-linecap="round">' % bow.PALETTE["rail"])
    # far to near: a nearer rail paints over a rear one, so the rear edge is covered by
    # depth even at the stations where its own stroke is not clipped
    for r in sorted(res["rails"], key=lambda r: -r["z"]):
        out.append('<polyline class="rail" data-rail="%s" data-s0="%.4f" data-s1="%.4f" '
                   'points="%s"/>' % (r["rail"], r["s0"], r["s1"], _fmt(r["points"])))
    out.append("</g>")
    out.append('<g id="creases" fill="none" stroke="%s" stroke-width="3.0" '
               'stroke-linecap="round">' % bow.PALETTE["crease"])
    for c in res["creases"]:
        out.append('<polyline class="crease" data-mark="%d" data-u="%.4f" points="%s"/>'
                   % (c["mark"], c["u"], _fmt(c["points"])))
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(HERE), "artwork.svg"))
    ap.add_argument("--no-depth-break", action="store_true",
                    help="negative control: emit every stroke unbroken")
    a = ap.parse_args()
    res = resolve(break_depth=not a.no_depth_break)
    text = svg(res)
    with open(a.out, "w") as fh:
        fh.write(text)
    print(f"wrote {a.out}: {len(res['fills'])} triangles, "
          f"{len(res['rails'])} rail runs, {len(res['creases'])} crease runs")


if __name__ == "__main__":
    main()
