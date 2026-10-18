"""The bow, studied on its own (round R1a).  One continuous ribbon, no figure.

Every number here is either a *measured target* carrying the reference's value scaled into
the canvas, or an *author choice* that composes the drawing.  The reference crop seeded
these scalars once, at authoring time; nothing at build time reads the reference.

Measured targets used (reference crop 400x480, registered to image.jpg 500,320,900,800;
canvas scale 3.28 = 800/244 of the crop's bow width):
  bow bbox            239 x 152 crop   -> ~784 x 500 canvas
  knot waist          59 crop tall     -> ~193 canvas, at 0.70 of the bow's width
  knot cross-sections 0.39 of bow height
  lobes               81 px / 63 px crop (1.29 : 1), so the right lobe is smaller
  fill / fold shadow  #ce4e7e / #67233d  (measured at (140,175) and (140,205))
  background          #77c8c0 (mint field, measured at (30,260))
Author choices: cloth thickness (16 px), the roll field that turns the ribbon over at the
folds and at the lower tail, the crease table, and the two tail routes.
"""
from __future__ import annotations

import math

import numpy as np

from ribbon import Field, Route, Strip, triangles

CANVAS = (800, 560)

PALETTE = {
    "bg": "#77c8c0",      # measured: mint background field
    "front": "#ce4e7e",   # measured: bow fill
    "back": "#67233d",    # measured: fold shadow on the same ribbon
    "rail": "#8a2350",    # author choice: ribbon edge, between fill and shadow
    "crease": "#67233d",  # measured fold-shadow value, used for the fold marks
}

THICKNESS = 16.0          # one cloth thickness, in canvas px - the minimum depth break
HALF_WIDTH = 112.0        # nominal half-width of the ribbon (measured lobe proportion)
NOMINAL_HALF = HALF_WIDTH  # kept as the single name the fields scale against

STATIONS = 620


def _route():
    """The whole ribbon, walked once: one hand-typed point, everything else generated."""
    r = Route((-70.0, 300.0))
    r.run(length=525, end_deg=-3.0, out_deg=-3.0)          # 0 left tail
    r.turn(along=56, across=39, sign=-1)                   # 1 knot wrap (a half turn, over the knot)
    r.run(end=(330.0, 130.0), end_deg=180.0, out_deg=180.0)  # 2 left lobe, outer limb
    r.turn(along=140, across=88, sign=-1)                  # 3 left lobe fold
    r.run(end=(470.0, 258.0), end_deg=0.0, out_deg=0.0)    # 4 left lobe, return limb
    r.run(end=(700.0, 168.0), end_deg=0.0, out_deg=0.0, bend=-34.0)  # 5 over the knot, to the right lobe
    r.turn(along=104, across=70, sign=1)                   # 6 right lobe fold
    r.run(end=(610.0, 292.0), end_deg=180.0, out_deg=180.0)  # 7 right lobe, return limb
    r.run(end=(470.0, 552.0), end_deg=90.0)                # 8 lower tail, out of the frame
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
BACK_TAIL = 2.25 * THICKNESS   # 36   tails hang behind the loops
MID = 1.0 * THICKNESS          # 16   the folded-back limb of each loop
FRONT = 0.0                    # 0    the outward limb of each loop
WRAP = -1.75 * THICKNESS       # -28  the knot band, passing over both loops


def _fields(parts):
    P = lambda k, f=0.0: _knot_at(parts, k, f)  # noqa: E731
    half = Field([
        (P(0, 0.0), 15.0), (P(0, 0.55), 30.0), (P(0, 1.0), 40.0),
        (P(1, 0.35), 22.0), (P(1, 1.0), 34.0),
        (P(2, 0.25), HALF_WIDTH * 0.80), (P(2, 1.0), HALF_WIDTH),
        (P(3, 0.5), HALF_WIDTH * 0.30),                 # the fold pinches the ribbon
        (P(3, 1.0), HALF_WIDTH),
        (P(4, 1.0), HALF_WIDTH * 0.86),
        (P(5, 0.5), HALF_WIDTH * 0.78), (P(5, 1.0), HALF_WIDTH * 0.9),
        (P(6, 0.5), HALF_WIDTH * 0.28),                  # right fold, tighter
        (P(6, 1.0), HALF_WIDTH * 0.94),
        (P(7, 1.0), HALF_WIDTH * 0.82),
        (P(8, 0.45), 46.0), (P(8, 1.0), 17.0),
    ])
    depth = Field([
        (P(0, 0.0), BACK_TAIL), (P(1, 0.0), BACK_TAIL),
        (P(1, 0.55), WRAP), (P(1, 1.0), WRAP),           # the wrap climbs over the knot
        (P(2, 1.0), FRONT),
        (P(3, 0.5), (FRONT + MID) * 0.5), (P(3, 1.0), MID),
        (P(4, 1.0), MID),
        (P(5, 1.0), FRONT),
        (P(6, 1.0), MID),
        (P(7, 1.0), MID),
        (P(8, 1.0), BACK_TAIL),
    ])
    # roll: how far the strip is turned about its own axis.  cos(roll) < 0 means the
    # triangle's own winding points away from the camera, so that face wears the back
    # colour.  Rolls stop short of edge-on and skip the 90-degree dead band.
    roll = Field([
        (P(0, 0.0), 10.0), (P(1, 0.0), 16.0),
        (P(1, 1.0), 26.0),
        (P(3, 0.46), 101.0), (P(3, 0.54), 101.0),        # the fold turns the ribbon over
        (P(3, 1.0), 0.0),
        (P(5, 1.0), -18.0),
        (P(6, 0.22), -36.0), (P(6, 0.78), -36.0),
        (P(6, 1.0), 0.0),
        (P(8, 0.55), 20.0), (P(8, 1.0), 152.0),          # the lower tail hangs turned over
    ])
    return half, depth, roll


def _roll_guard(deg):
    """Keep the ribbon off exact edge-on: the projected width would vanish there.

    A roll of +/-90 degrees projects the strip to a line, and a line of triangles is a fan
    of slivers (measured on this drawing before the guard existed).  Rolls inside the
    dead band are held at its edge.
    """
    d = math.fmod(deg, 360.0)
    if abs(d) >= 180.0:
        d -= math.copysign(360.0, d)
    if 83.0 < d < 97.0:
        return 83.0
    if -97.0 < d < -83.0:
        return -83.0
    return d


# ---- surface marks authored in (u, v) -------------------------------------------------

# (part, fraction inside the part, v_start, v_end).  Each mark lies on the strip surface as
# sampled in its own (u, v), runs across the strip along a fold, and is clipped by depth.
CREASES = [
    (1, 0.46, 0.80, -0.80, 0.004),   # 0 knot: where the band closes on itself
    (1, 0.76, 0.55, -0.55, -0.004),  # 1 knot: the second turn of the wrap
    (2, 0.58, 0.80, -0.28, 0.012),   # 2 left loop, outer limb: the fold running out of the turn
    (4, 0.34, 0.86, 0.10, 0.010),    # 3 left loop, folded-back limb, out of the knot
    (5, 0.58, -0.45, 0.60, 0.008),   # 4 the band crossing the knot: a fold along its length
    (7, 0.38, 0.20, -0.80, -0.012), # 5 right loop, folded-back limb
    (8, 0.32, 0.58, -0.22, 0.016),   # 6 lower tail: the fold where it leaves the knot
]


def build():
    route = _route()
    spine = route.polyline()
    densified = _resample_dense(spine, STATIONS)
    parts = _parts_u(route, densified)
    half, depth, roll_raw = _fields(parts)

    def roll(u):
        return _roll_guard(roll_raw(u))

    st = Strip(densified, half, depth, roll)
    tris = triangles(st)
    creases = [(_knot_at(parts, k, f), v0, v1, c) for (k, f, v0, v1, c) in CREASES]
    return {
        "strip": st,
        "tris": tris,
        "parts": parts,
        "creases": creases,
        "thickness": THICKNESS,
    }


def _resample_dense(poly, n):
    from ribbon import resample
    return resample(poly, n)
