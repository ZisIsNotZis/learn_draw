"""Compile the bow study into artwork.svg.  Deterministic: no clock, no randomness.

The drawing is the paint order of authored bands.  Each band is one closed silhouette filled
flat in the ribbon's front colour and stroked at the contour weight, followed by its crease
lines at the fold weight.  A band painted later covers the silhouette and the crease ends of
the bands under it, which is the occlusion model: at every junction one ribbon edge runs over
another, and the rear edge is broken where it is covered.

    python source/build.py                 # -> artwork.svg
    python source/build.py --no-occlusion   # negative control: front band painted first
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "parts"))

import bow  # noqa: E402


def _fmt(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def svg(art, occlusion=True):
    pal = art["palette"]
    order = art["bands"] if occlusion else list(reversed(art["bands"]))
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
        % (art["canvas"][0], art["canvas"][1], art["canvas"][0], art["canvas"][1]),
        "<!-- A-bow-study-v3: one ribbon tied in a knot, authored as bands in paint order. "
        "Compiler output of source/build.py; edit the source. -->",
        '<desc>Object study: a ribbon tied in a bow, filling the frame. %d bands, %d of them '
        'crossed by a later band; flat cel fill, contour %.1f px, creases %.1f px.</desc>'
        % (len(art["bands"]), len(art["bands"]) - 1, art["contour_stroke"], art["crease_stroke"]),
        '<rect id="field" x="0" y="0" width="%d" height="%d" fill="%s"/>'
        % (art["canvas"][0], art["canvas"][1], pal["bg"]),
    ]
    for i, b in enumerate(order):
        out.append('<g class="band" data-band="%s" data-order="%d" fill="%s" stroke="%s" '
                   'stroke-width="%.1f" stroke-linejoin="round">'
                   % (b["name"], i, pal["front"], pal["back"], art["contour_stroke"]))
        out.append('<polygon points="%s"/>' % _fmt(b["outline"]))
        out.append("</g>")
        out.append('<g class="creases" data-band="%s" fill="none" stroke="%s" '
                   'stroke-width="%.1f" stroke-linecap="round" stroke-linejoin="round">'
                   % (b["name"], pal["crease"], art["crease_stroke"]))
        for c in b["creases"]:
            out.append('<polyline points="%s"/>' % _fmt(c))
        out.append("</g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(HERE), "artwork.svg"))
    ap.add_argument("--no-occlusion", action="store_true",
                    help="negative control: paint front to back, so no junction is an occlusion")
    a = ap.parse_args()
    text = svg(bow.build(), occlusion=not a.no_occlusion)
    with open(a.out, "w") as fh:
        fh.write(text)
    art = bow.build()
    print(f"wrote {a.out}: {len(art['bands'])} bands, "
          f"{sum(len(b['creases']) for b in art['bands'])} crease lines")


if __name__ == "__main__":
    main()
