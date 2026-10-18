"""The bow, studied on its own (round R1a, repair r2).  One continuous ribbon, no figure.

Every number here is either a *measured target* carrying the reference's value scaled into
the canvas, or an *author choice* that composes the drawing.  The reference crop seeded
these scalars once, at authoring time; nothing at build time reads the reference.

Measured targets (reference crop 400x480, registered to image.jpg 500,320,900,800; the bow
occupies crop bbox (33,134)-(271,285), 239 x 152, scaled 3.3x into this canvas):
  bow bbox            239 x 152 crop   -> aspect 1.57 (this drawing: 790 x 500 = 1.58)
  knot waist          59 crop tall at x=201 -> 0.39 of the bow's height; the knot sits at
                      0.70 of the bow's width
  lobes               81 px / 63 px crop (1.29 : 1)
  tails               left tail leaves the left edge; lower tail 78 crop px wide at y=278
                      = 0.33 of the bow's width, i.e. broad and barely tapered
  fill / fold shadow  #ce4e7e / #67233d (measured at (140,175) and (140,205) of the crop)
  background          #77c8c0 (mint field, measured at (30,260) of the crop)
Author choices: cloth thickness (16 px), the fold radii, the crease table, the roll field,
and the tails' routes.

Repair r2 changed the *turn generation* rather than the object: a fold now turns with a
radius the gathered ribbon can actually wrap (half-width <= turn radius), so the two rails
never cross at the fold and the fold's free edge is a rounded cap; and the limbs of each loop
come back over each other, so a lobe is filled cloth instead of a closed outline with a hole.
"""
from __future__ import annotations

import math

import numpy as np

from ribbon import Field, Route, Strip, triangles

CANVAS = (800, 560)

PALETTE = {
    "bg": "#77c8c0",      # measured: mint background field
    "front": "#ce4e7e",   # measured: bow fill - the lit, exposed face of the cloth
    "back": "#67233d",    # measured: fold shadow - a face lying under another pass
    "rail": "#8a2350",    # author choice: ribbon edge, between fill and shadow
    "crease": "#67233d",  # measured fold-shadow value, used for the fold marks
}

THICKNESS = 16.0          # one cloth thickness, in canvas px - the minimum depth break
HALF_WIDTH = 150.0        # half-width of the ribbon at its fullest (the lobes' cloth)
NOMINAL_HALF = HALF_WIDTH  # the single name the fields scale against

STATIONS = 620

# ---- the knot's measured station -------------------------------------------------------
# The knot sits at 0.70 of the bow's width and its waist is 0.39 of the bow's height.  The
# bow's in-canvas bbox is 790 x 500 px, so the knot's centre belongs at x = 553 and the
# narrowest column there must be about 0.39 * 392 = 153 px tall (the lobes are 392 tall).
KNOT_X = 553.0
KNOT_Y = 272.0
LOBE_HALF_HEIGHT = 196.0   # half of the lobes' 392 px vertical extent
KNOT_HALF = 76.0           # half-width of the cloth at the knot station = 0.39 x 196

# fold radii: a gathered ribbon can only wrap a turn whose radius is at least its own
# half-width, so the width field contracts to H_FOLD through every turn.
R_FOLD = 46.0
R_WRAP = 62.0
H_FOLD = 38.0

# where the loops' two limbs lie: the outbound limb's centre line and the return limb's,
# one cloth-and-a-turn apart (2 * R_FOLD), close enough that the two overlap and the lobe
# is filled cloth.
Y_LOBES = 210.0            # outbound limb centre line, both lobes
Y_RETURN = Y_LOBES + 2 * R_FOLD   # 302

LEFT_FOLD_X = 281.0 + R_FOLD + H_FOLD   # outer edge of the left lobe at x = 281
RIGHT_FOLD_X = 787.0 - R_FOLD - H_FOLD  # outer edge of the right lobe at x = 787


def _route():
    """The whole ribbon, walked once: one hand-typed point, everything else generated."""
    r = Route((-95.0, Y_RETURN + 32.0))
    r.run(end=(KNOT_X - 31.0, Y_RETURN + 32.0), end_deg=2.0)   # 0 left tail, in from off frame
    r.turn(along=R_WRAP, across=R_WRAP, sign=-1)               # 1 knot wrap: half turn, upward
    r.run(end=(LEFT_FOLD_X, Y_LOBES), end_deg=180.0)           # 2 left lobe, outward limb
    r.turn(along=R_FOLD, across=R_FOLD, sign=-1)               # 3 left lobe fold
    r.run(end=(KNOT_X - 40.0, Y_RETURN), end_deg=0.0)          # 4 left lobe, return limb
    r.run(end=(RIGHT_FOLD_X, Y_LOBES), end_deg=0.0, bend=-30.0)  # 5 the band across the knot
    r.turn(along=R_FOLD, across=R_FOLD, sign=1)                # 6 right lobe fold
    r.run(end=(KNOT_X + 34.0, Y_RETURN), end_deg=180.0)        # 7 right lobe, return limb
    r.run(end=(455.0, 680.0), out_deg=180.0, end_deg=104.0)    # 8 lower tail, off the bottom
    return r


def _parts_u(route, spine):
    """Arc-length fraction of the resampled spine where each route part begins."""
    d = np.linalg.norm(np.diff(spine, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(d)])
    cum /= cum[-1]
    bounds = [0.0]
    for _kind, pts in route.parts:
        bounds.append(bounds[-1] + float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum()))
    total = bounds[-1]
    return [b / total for b in bounds[:-1]]


def _knot_at(parts, k, frac=0.0):
    """The strip parameter at fractional position `frac` inside route part k."""
    if k >= len(parts) - 1:
        return 1.0
    return parts[k] + (parts[k + 1] - parts[k]) * frac


# ---- the three fields along the strip -------------------------------------------------

# depth, in canvas px; negative is nearer the viewer.  A ribbon crossing itself must step
# by at least one cloth thickness at every crossing, and the knot's passes are separated.
BACK_TAIL = 2.25 * THICKNESS   # 36   both tails hang behind the loops
MID = 1.0 * THICKNESS          # 16   the folded-back limb of each loop
FRONT = 0.0                    # 0    the outward limb of each loop
WRAP = -1.75 * THICKNESS       # -28  the knot's wrap, passing over both loops


def _fields(parts):
    P = lambda k, f=0.0: _knot_at(parts, k, f)  # noqa: E731
    # One width field, in canvas px.  It pinches to KNOT_HALF at the knot station - 0.39 of
    # the lobes' half-height, the reference's measured waist ratio - and contracts to H_FOLD
    # through every turn so the two rails cannot cross at the fold.
    half = Field([
        (0.0, 46.0), (P(0, 0.62), 56.0),
        (P(1, 0.5), 56.0),
        (P(2, 0.45), HALF_WIDTH), (P(2, 0.68), 120.0), (P(2, 0.93), 54.0),
        (P(3, 0.5), H_FOLD),                                   # the fold: h <= R_FOLD
        (P(4, 0.22), 130.0), (P(4, 0.62), HALF_WIDTH), (P(4, 0.93), 96.0),
        (P(5, 0.32), KNOT_HALF), (P(5, 0.6), 104.0), (P(5, 0.92), 54.0),
        (P(6, 0.5), H_FOLD),
        (P(7, 0.25), 130.0), (P(7, 0.62), HALF_WIDTH), (P(7, 0.92), 126.0),
        (P(8, 0.22), 130.0), (P(8, 0.7), 126.0),
        (1.0, 122.0),                                          # broad, barely tapered
    ])
    depth = Field([
        (0.0, BACK_TAIL), (P(0, 0.88), BACK_TAIL),
        (P(1, 0.45), WRAP),                                   # the wrap climbs over the knot
        (P(2, 0.30), FRONT), (P(2, 0.85), FRONT),
        (P(3, 0.55), MID),
        (P(4, 0.60), MID),
        (P(5, 0.72), FRONT),                                  # the band rises to the right lobe
        (P(6, 0.55), MID),
        (P(7, 0.75), MID),
        (P(8, 0.20), BACK_TAIL + 4.0),
        (1.0, BACK_TAIL + 4.0),
    ])
    # roll: how far the strip is turned about its own axis.  A roll near 90 degrees projects
    # the strip to a line and a line of triangles is a fan of slivers, so the ribbon is kept
    # nearly face-on throughout; the field exists so a tail can be turned a little without a
    # discontinuity, and _roll_guard holds it out of that dead band.
    roll = Field([
        (0.0, 10.0), (P(0, 0.7), 4.0),
        (P(1, 0.6), 2.0),
        (P(2, 0.5), 0.0), (P(3, 0.5), 0.0), (P(4, 0.6), 0.0),
        (P(5, 0.6), -6.0),
        (P(6, 0.6), 0.0), (P(7, 0.6), 0.0),
        (P(8, 0.5), -8.0),
        (1.0, -14.0),
    ])
    return half, depth, roll


def _roll_guard(deg):
    """Keep the ribbon off exact edge-on: the projected width would vanish there."""
    d = math.fmod(deg, 360.0)
    if abs(d) >= 180.0:
        d -= math.copysign(360.0, d)
    if 78.0 < d < 102.0:
        return 78.0
    if -102.0 < d < -78.0:
        return -78.0
    return d


# ---- surface marks authored in (u, v) -------------------------------------------------

# (part, fraction inside the part, v_start, v_end, curvature).  Each mark runs across the
# whole strip, from one rail to the other, so both of its ends lie on the ribbon's edge; it
# is curved along the route so it follows the fold instead of chording across it, and it is
# clipped by depth like every other stroke.  Seven marks, as the reference carries seven
# interior strokes on a 239x152 object, and all of them on cloth that faces the viewer.
CREASES = [
    (1, 0.52, 1.0, -1.0, 0.006),    # 0 the knot's wrap: the gather where it closes
    (2, 0.42, 1.0, -1.0, 0.010),    # 1 left lobe, outward limb: the fold out of the knot
    (2, 0.62, 1.0, -1.0, 0.010),    # 2 left lobe, outward limb: mid-lobe fold
    (2, 0.80, 1.0, -1.0, 0.008),    # 3 left lobe, outward limb: the fold into the turn
    (5, 0.40, 1.0, -1.0, 0.008),    # 4 the band at the knot
    (5, 0.72, 1.0, -1.0, -0.008),   # 5 the band running out to the right lobe
    (8, 0.22, 1.0, -1.0, 0.012),    # 6 the lower tail where it leaves the knot
]

# Mutation inputs: each names one mechanism the tests must see fail when it is removed.
VARIANTS = {
    # F1/F3: open the loops - the limbs part and the fold's outline self-intersects, so the
    # lobe's interior becomes an enclosed background island and the outline grows a spike.
    "open-fold": {"fold_radius": 2.6},
    # F5: author the marks short of the rails so both ends float inside the cloth.
    "free-creases": {"crease_v": 0.8},
}


def build(variant=None):
    v = VARIANTS.get(variant, {}) if variant else {}
    route = _opened_route(v["fold_radius"]) if "fold_radius" in v else _route()
    spine = route.polyline()
    densified = _resample_dense(spine, STATIONS)
    parts = _parts_u(route, densified)
    half, depth, roll_raw = _fields(parts)

    def roll(u):
        return _roll_guard(roll_raw(u))

    st = Strip(densified, half, depth, roll)
    tris = triangles(st)
    cv = v.get("crease_v", 1.0)
    creases = [(_knot_at(parts, k, f), cv * v0, cv * v1, c) for (k, f, v0, v1, c) in CREASES]
    return {
        "strip": st,
        "tris": tris,
        "parts": parts,
        "creases": creases,
        "thickness": THICKNESS,
    }


def _opened_route(scale):
    """The r1 turn generation, kept as the mutation: a fold whose radius dwarfs the cloth."""
    f = R_FOLD * scale
    r = Route((-95.0, Y_RETURN + 32.0))
    r.run(end=(KNOT_X - 31.0, Y_RETURN + 32.0), end_deg=2.0)
    r.turn(along=56.0, across=39.0, sign=-1)
    r.run(end=(LEFT_FOLD_X, Y_LOBES), end_deg=180.0)
    r.turn(along=140.0, across=f, sign=-1)
    r.run(end=(KNOT_X - 40.0, Y_RETURN + 2 * (f - R_FOLD)), end_deg=0.0)
    r.run(end=(RIGHT_FOLD_X, Y_LOBES), end_deg=0.0, bend=-30.0)
    r.turn(along=104.0, across=f, sign=1)
    r.run(end=(KNOT_X + 34.0, Y_RETURN + 2 * (f - R_FOLD) + 30.0), end_deg=180.0)
    r.run(end=(455.0, 680.0), out_deg=180.0, end_deg=104.0)
    return r


def _resample_dense(poly, n):
    from ribbon import resample
    return resample(poly, n)
