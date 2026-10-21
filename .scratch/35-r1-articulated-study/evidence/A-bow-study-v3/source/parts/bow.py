"""The bow, studied on its own (round R1a, repair r3).  A ribbon tied in a knot.

The v2 build walked a numeric ribbon surface (a spine in 3D plus width/depth/roll fields)
and projected it.  Its image review (B1..B6) found that the projection put the failure at
the knot and at the junctions: the knot was a closed pouch with no edge crossing another,
a gather was a triangle fan with a visible pole, and every junction was one silhouette cut
by another's outline.  Those are construction failures, so this revision replaces the
construction instead of tuning it:

  * the object is authored as BANDS - a ribbon pass is a closed silhouette plus its crease
    lines - and paint order is the occlusion model.  A band painted later covers the
    silhouette and the crease ends of the bands under it, so a knot that wraps is drawn by
    painting its wrap after the lobes, and every junction in the picture has a break.
  * the knot is three passes that cross: the wrap (vertical, over both lobes' mouths and
    over the left tail's end), a cross band (near horizontal, over the wrap), and the left
    tail's fold flap (over the cross band).  Each pass's edge crosses the pass under it, so
    ribbon edges pass over ribbon edges - B1.
  * the left tail folds over into the knot: its end is a rounded fold flap, and its width
    (40 px) is narrower than the knot's wrap (66 px) - B2.  The wrap has no fan: there is
    no triangle mesh here at all, so no pole can be visible.
  * the lobes are petals whose free edges are curved and whose creases run from the mouth
    (hidden under the wrap) out to the fold, where they end on the silhouette - B3.
  * the lobes open from the knot: their mouths are under the wrap, not cut by it - B4 -
    and nothing is filled with the dark value, so no solid dark blob can exist.
  * the contour is stroked at 5.0 px and the creases at 2.4 px in one dark value, so the
    silhouette carries more weight than the folds - B5.  One flat cel fill, no texture,
    no shading, no background mark.
  * each junction is an occlusion: the wrap over the lobe mouths, the cross band over the
    wrap, the fold flap over the cross band, the bottom tail over the wrap's lower end - B6.

Measured targets carried from the reference crop (400x480, bow bbox (33,134)-(271,285),
scaled 3.3x): bow aspect 1.57, knot at 0.71 of the bow's width, lobes 81:63, left tail to
the left frame edge, lower tail off the bottom, fill #ce4e7e, shadow #67233d, ground
#77c8c0.  Author choices: every control point, the band widths and the crease routes.
"""
from __future__ import annotations

CANVAS = (800, 560)

PALETTE = {
    "bg": "#77c8c0",
    "front": "#ce4e7e",   # measured reference ribbon fill
    "back": "#67233d",    # measured fold-shadow value, used only as a stroke
    "crease": "#67233d",
}

CONTOUR_STROKE = 5.0      # silhouette weight
CREASE_STROKE = 2.4       # fold weight: strictly less than the contour


def _chaikin(pts, rounds=3, closed=True):
    """Corner-cut a control polygon into a curve.  Deterministic, no randomness."""
    for _ in range(rounds):
        out = []
        n = len(pts)
        last = n if closed else n - 1
        if not closed:
            out.append(pts[0])
        for i in range(last):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            out.append((0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1))
            out.append((0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def _curve(pts, rounds=3):
    return _chaikin(pts, rounds=rounds, closed=False)


def bands():
    """The drawing, back to front.  Each band: {"name", "outline", "creases"}."""
    left_lobe = [
        (566, 236), (500, 196), (400, 152), (300, 146), (232, 168), (196, 220),
        (194, 274), (222, 322), (300, 346), (420, 332), (510, 308), (566, 292),
    ]
    right_lobe = [
        (592, 240), (642, 200), (702, 184), (748, 198), (770, 236), (760, 274),
        (728, 306), (668, 318), (610, 304), (592, 284),
    ]
    left_tail = [
        (-20, 286), (120, 292), (260, 300), (380, 302), (470, 302), (560, 300),
        (560, 330), (470, 334), (380, 336), (240, 330), (120, 322), (-20, 322),
    ]
    wrap = [
        (506, 210), (582, 214), (596, 244), (600, 280), (608, 322), (596, 362),
        (528, 360), (522, 312), (514, 266), (508, 236),
    ]
    cross = [
        (470, 292), (540, 282), (610, 274), (648, 276), (652, 306), (612, 310),
        (540, 314), (472, 322),
    ]
    flap = [
        (424, 312), (486, 300), (536, 292), (540, 322), (486, 328), (426, 338),
    ]
    bottom_tail = [
        (534, 306), (516, 372), (532, 470), (548, 540), (540, 600),
        (628, 600), (604, 540), (596, 470), (606, 380), (596, 306),
    ]

    def band(name, control, creases):
        return {"name": name, "outline": _chaikin(control), "creases": [_curve(c) for c in creases]}

    order = [
        band("left-tail", left_tail, [
            [(-20, 306), (160, 306), (330, 312), (470, 312), (522, 310)],
            [(120, 322), (200, 318)],                           # fold mark on the lower rail
        ]),
        band("left-lobe", left_lobe, [
            [(560, 232), (430, 178), (324, 164), (240, 202)],   # mouth -> fold, upper arm
            [(560, 294), (430, 320), (324, 336), (236, 300)],   # mouth -> fold, lower arm
            [(206, 236), (212, 274), (232, 306)],               # the fold's inside edge
            [(520, 240), (500, 214)],                           # gather, ends under the wrap
            [(516, 292), (498, 316)],
        ]),
        band("right-lobe", right_lobe, [
            [(596, 244), (672, 210), (742, 224)],               # mouth -> fold
            [(596, 280), (668, 300), (740, 280)],
            [(700, 252), (712, 276)],                           # short fold mark, ends on the rail
        ]),
        band("wrap", wrap, [
            [(553, 216), (562, 252), (568, 310), (566, 356)],
            [(524, 250), (540, 258), (552, 262)],               # short crease, ends on the rail
        ]),
        band("cross", cross, [
            [(474, 306), (546, 296), (620, 288), (648, 290)],
        ]),
        band("fold-flap", flap, [
            [(432, 318), (452, 326), (476, 326)],
            [(436, 322), (458, 316)],
        ]),
        band("bottom-tail", bottom_tail, [
            [(540, 340), (592, 338)],                           # gather across the junction
            [(534, 404), (602, 400)],
            [(556, 520), (592, 520)],
        ]),
    ]
    return order


def build():
    """The emitted geometry, resolved once (tests and the compiler read this)."""
    return {"canvas": CANVAS, "palette": PALETTE, "bands": bands(),
            "contour_stroke": CONTOUR_STROKE, "crease_stroke": CREASE_STROKE}
