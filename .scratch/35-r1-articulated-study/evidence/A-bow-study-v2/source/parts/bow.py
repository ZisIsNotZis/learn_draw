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
# The knot sits at 0.70 of the bow's width.  Measured on the reference crop: the bow spans
# x 33..271 and the waist is at x 201, so (201 - 33) / (271 - 33) = 0.706.  The canvas' bow
# spans x 0..787, so the knot belongs at x = 0.706 * 787 = 556; KNOT_X is 553, the value the
# route was composed around, and the knot - not the mass - is what has to sit there.  Its
# waist ratio (0.39 of the bow's height) is now produced by H_KNOT below, not asserted.
KNOT_X = 553.0
KNOT_Y = 272.0

# ---- radii and the widths they cost ----------------------------------------------------
# A gathered ribbon can only wrap a turn whose radius exceeds its own half-width, and the
# turn's INNER edge has radius R - h.  That inner radius is where the triangles fan out of;
# when R - h shrinks towards the station spacing the fan collapses into sub-pixel wedges and
# the fold is drawn as a hatch rather than as cloth (measured on the r2 build at R - h = 8).
# So each turn keeps R - h above a cloth's worth of px: the fold pinches the ribbon to
# H_FOLD and the knot crushes it to H_KNOT.
R_FOLD = 38.0
R_WRAP = 62.0
H_FOLD = 34.0             # the ribbon through a fold: R_FOLD - H_FOLD = 4 px of inner edge
H_KNOT = 32.0             # the ribbon through the knot: the one place it is crushed

# where the loops' two limbs lie: the outbound limb's centre line and the return limb's,
# one turn apart (2 * R_FOLD), close enough that the two overlap and the lobe is cloth.
Y_LOBES = 210.0            # outbound limb centre line, both lobes
Y_RETURN = Y_LOBES + 2 * R_FOLD   # 286
GATHER = 0.45             # how far the returning limb climbs back towards the knot's centre

LEFT_FOLD_X = 343.0        # where the left lobe's turn begins (author choice: the lobes' span)
RIGHT_FOLD_X = 679.0       # where the right lobe's turn begins


def _route():
    """The whole ribbon, walked once: one hand-typed point, everything else generated."""
    r = Route((-95.0, Y_RETURN + 32.0))
    r.run(end=(KNOT_X - 31.0, Y_RETURN + 32.0), end_deg=2.0)   # 0 left tail, in from off frame
    r.turn(along=R_WRAP, across=R_WRAP, sign=-1)               # 1 knot wrap: half turn, upward
    r.run(end=(LEFT_FOLD_X, Y_LOBES), end_deg=180.0)           # 2 left lobe, outward limb
    r.turn(along=R_FOLD, across=R_FOLD, sign=-1)               # 3 left lobe fold
    r.run(end=(KNOT_X - 40.0, Y_LOBES + GATHER * 2 * R_FOLD), end_deg=0.0)  # 4 left lobe, return
    r.run(end=(RIGHT_FOLD_X, Y_LOBES), end_deg=0.0, bend=-30.0)  # 5 the band across the knot
    r.turn(along=R_FOLD, across=R_FOLD, sign=1)                # 6 right lobe fold
    r.run(end=(KNOT_X + 34.0, Y_LOBES + GATHER * 2 * R_FOLD), end_deg=180.0)  # 7 right lobe, return
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
    """The strip parameter at fractional position `frac` inside route part k.

    `parts[k]` is where part k begins; part k ends where part k+1 begins, and the LAST part
    ends at the strip's end, u = 1.0.  Reading the last part's end off `parts[k + 1]` is what
    used to be missing here: the old guard returned 1.0 for the last part, so every fraction
    inside it collapsed onto the strip's end and the lower tail's three width knots landed on
    the same station.  The part's own span, not its start, is the interval a fraction walks.
    """
    if k >= len(parts):
        return 1.0
    end = parts[k + 1] if k + 1 < len(parts) else 1.0
    return parts[k] + (end - parts[k]) * frac


# ---- the three fields along the strip -------------------------------------------------

# depth, in canvas px; negative is nearer the viewer.  A ribbon crossing itself must step
# by at least one cloth thickness at every crossing, so each VISIT of the strip gets its own
# level and neighbouring visits differ by more than two thicknesses; where two visits cross
# the test measures the difference on the emitted geometry.  The levels are not a stack of
# separate pieces: one continuous strip is what makes the swing from one level to the next
# have to happen somewhere, and the field puts each swing inside a turn, which is the place
# where the ribbon really does turn over.
TAIL_IN = 3.75 * THICKNESS     # +60  the left tail, hanging behind the knot
WRAP = -3.75 * THICKNESS       # -60  the knot's wrap, the one pass over everything else
LOBE_OUT = -2.5 * THICKNESS    # -40  each lobe's outward limb, in front of its return
LOBE_RET = 2.5 * THICKNESS     # +40  each lobe's returning limb, behind its outward limb
BAND = -1.25 * THICKNESS       # -20  the band crossing the knot, over both limbs' returns
TAIL_OUT = -6.25 * THICKNESS   # -100 the lower tail, in front of everything it crosses


def _fields(parts):
    P = lambda k, f=0.0: _knot_at(parts, k, f)  # noqa: E731
    # One width field, in canvas px.  Four things shape it: the knot is the one place the
    # ribbon is crushed (H_KNOT), every turn pinches it to H_FOLD, the lobes are at their
    # fullest through their middle, and the outer ends of the lobes and the tails are
    # between the two.  Because the limbs of a lobe march up and down across the same x
    # interval, a lobe is a lens with a waist at each end of it: that lens, not a constant
    # width, is what leaves the knot narrower than the cloth either side of it.
    half = Field([
        (0.0, 46.0), (P(0, 0.55), 54.0), (P(0, 0.90), 46.0),   # left tail: broad, then crushed
        (P(1, 0.5), H_KNOT),                                   # the wrap, crushed at the knot
        (P(2, 0.0), H_KNOT),
        (P(2, 0.30), 118.0), (P(2, 0.55), HALF_WIDTH), (P(2, 0.82), 88.0),
        (P(3, 0.5), H_FOLD),                                   # the fold: R_FOLD - h = 28 px
        (P(4, 0.30), 118.0), (P(4, 0.58), HALF_WIDTH), (P(4, 0.86), 86.0),
        (P(5, 0.30), H_KNOT),                                  # the band, crushed at the knot
        # The band's belly, and then NO pinch here: the fold's pinch has one home, the fold
        # turn's own middle (P(6, 0.5)), the way the left fold's pinch sits at P(3, 0.5).
        # Stating it a second time at the band's end put the crush and the pinch 15 stations
        # apart, and two cosine ramps that short turn the width series at
        # (pi^2/2)(dh/N^2) = 1.9 + 2.1 half-width px per station^2 at their apex - a turn
        # no cloth makes, which is what the isolation test read as a piece boundary.
        (P(5, 0.62), 128.0),
        (P(6, 0.5), H_FOLD),                                   # the right fold's pinch
        (P(7, 0.02), H_FOLD),
        (P(7, 0.60), 104.0), (P(7, 0.98), 92.0),   # one ramp each way: the part is short
        (P(8, 0.12), H_KNOT), (P(8, 0.45), 96.0), (1.0, 122.0),  # lower tail: crushed, then broad
    ])
    # Each swing between two levels sits inside a turn (the fold on the way out of a lobe,
    # the wrap on the way over the knot, the junction on the way into the lower tail).
    depth = Field([
        (0.0, TAIL_IN), (P(0, 0.90), TAIL_IN),
        (P(1, 0.18), WRAP), (P(1, 0.85), WRAP),                # over the knot
        (P(2, 0.12), LOBE_OUT), (P(2, 0.92), LOBE_OUT),
        (P(3, 0.92), LOBE_RET),                                # the left fold: front -> behind
        (P(4, 0.90), LOBE_RET),
        (P(5, 0.12), BAND), (P(5, 0.90), BAND),                # over both returns
        (P(7, 0.10), LOBE_RET),                                # the right fold: band -> behind
        (P(7, 0.92), LOBE_RET),
        # The tail has no turn, so its swing has no turn to sit in, and it must not sit where
        # the tail is broad: at the junction the corrected width field makes it 182 px wide,
        # so its rails sweep across the knot, over the band's and the wrap's rails.  A swing
        # there put the tail within 0.3 px of the wrap's depth at (547,354) and within 6.0 px
        # of the band's at (543,193).  It therefore sits where the ribbon is crushed to
        # H_KNOT: the tail leaves the knot at the lobe's level, turns over inside its own
        # waist, and is at TAIL_OUT over the whole broad part it hangs in front of.
        (P(8, 0.05), LOBE_RET),
        (P(8, 0.30), TAIL_OUT),                                # the tail, over the right lobe
        (1.0, TAIL_OUT),
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
