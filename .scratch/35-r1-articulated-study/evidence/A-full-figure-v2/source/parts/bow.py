"""A-bow-ribbon: one continuous strip tied into a bow.

Observed in the crop: a magenta bow left of centre on the chest — a left lobe, a
right lobe, a knot between them, one tail leaving the left frame edge and one tail
ending on the bodice below the knot.  Artist hypothesis (the tying order): it is a
single ribbon, so the strip visits knot -> left lobe -> knot -> right lobe -> knot
-> down tail, and its other end is the left tail.  There is no separate knot patch
and no separate lobe solid: the lobes are the strip folded back on itself, the
overlap comes from the two limbs' depth, and the crease reading is authored marks
on the strip.

Width is one constant: the strip is a ribbon, so a tail root cannot be wider than
the knot by construction (the defect this milestone removes).

Authored coordinates (four): the knot, the two lobe tips, and the left tail's exit.
Lobe limbs, fold and tail routes come from generators.
"""
from __future__ import annotations

import math

from . import families as fam
from .frames import SheetPart, StripSurface, crop, tp

KNOT_XY = (185.0, 163.0)
LEFT_LOBE_TIP_XY = (122.0, 175.0)
RIGHT_LOBE_TIP_XY = (262.0, 186.0)
LEFT_TAIL_EXIT_XY = (20.0, 216.0)

HALF_WIDTH = 17.0         # constant: one ribbon, one width, continuous through the knot
LIMB_SEPARATION = 30.0    # centre-to-centre distance of a lobe's two limbs (< 2*half: solid)
FOLD_EXTENSION = 6.0      # how far the fold turns past the authored lobe tip
TAIL_SAG = 105.0           # left tail sag toward the cuff it crosses
DOWN_LENGTH = 130.0       # down tail length from the knot
DOWN_DIRECTION_XY = (-0.22, 0.976)   # crop pixels, y down

FRONT_FILL = "#cf4b79"
BACK_FILL = "#a8405f"
INK = "#5d2138"


def _unit(a):
    import math
    d = math.hypot(*a)
    return (a[0] / d, a[1] / d)


def _perp(a):
    return (-a[1], a[0])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _mul(a, s):
    return (a[0] * s, a[1] * s)


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _bridge(start, end, knot, bend):
    """A short piece of the same strip running through the knot between two limbs."""
    middle = _add(_mul(_add(start, end), 0.5), _mul(_unit(_perp(_unit(
        (end[0] - start[0], end[1] - start[1])))), bend))
    return fam._bezier(start, _add(_mul(_add(start, middle), 0.5), (0.0, 0.0)), middle, end, 6)


def _fold_turn(tip, a, n, separation):
    """The turning fold of one lobe: a generated semicircle past the tip.

    A ribbon folded back on itself turns on a free edge of cloth, not on a chord: the
    arc is centred one fold-extension past the lobe tip and has the limb separation for
    its diameter, so the outer boundary the strip sweeps is a broad curve.
    """
    centre = _add(tip, _mul(a, FOLD_EXTENSION))
    radius = separation / 2.0
    out = []
    for index in range(13):
        angle = math.pi * index / 12
        out.append(_add(_add(centre, _mul(n, radius * math.cos(angle))),
                        _mul(a, radius * math.sin(angle))))
    return tuple(out)


def _lobe(knot, tip, separation):
    """Both limbs of one lobe and the fold that joins them, as polyline pieces."""
    a = _unit((tip[0] - knot[0], tip[1] - knot[1]))
    n = _perp(a)
    out_start = _add(knot, _mul(n, separation / 2))
    in_end = _add(knot, _mul(n, -separation / 2))
    turn = _fold_turn(tip, a, n, separation)
    out_end, in_start = turn[0], turn[-1]
    return [
        fam._bezier(out_start, _add(out_start, _mul(a, 18.0)), _sub(out_end, _mul(a, 12.0)), out_end, 10),
        turn,
        fam._bezier(in_start, _sub(in_start, _mul(a, 12.0)), _add(in_end, _mul(a, 18.0)), in_end, 10),
    ]


def _glue(pieces):
    """Join sampled pieces into one polyline with no duplicated interior station."""
    out = list(pieces[0])
    spans = [(0, len(pieces[0]) - 1)]
    for piece in pieces[1:]:
        if abs(piece[0][0] - out[-1][0]) > 1e-9 or abs(piece[0][1] - out[-1][1]) > 1e-9:
            out.append(piece[0])
        start = len(out) - 1
        out.extend(piece[1:])
        spans.append((start, len(out) - 1))
    return out, spans


# One cloth thickness: two layers of the same ribbon cannot share a depth, or the front
# layer of the knot would be decided by the visibility tie rule instead of by depth.
CLOTH_THICKNESS = 0.012

# One depth band per piece of the strip, ordered outermost-first: the tie's last pass is
# in front, then the pass between the lobes, then the pass that leaves the left limb.
# Pass 1 is a ramp and passes 2 and 3 are flat, so the three knot passes must miss each
# other by at least one cloth thickness over their whole spans -- a ramp whose midpoint
# reaches pass 2's band puts two knot layers at the same depth at that station.
PIECE_DEPTH = (
    (0.600, 0.600),                              # left tail: on the chest, in front of the cuff it crosses
    (0.600, 0.600 + CLOTH_THICKNESS / 2),        # knot pass 1, in front of the left limb
    (0.600 - CLOTH_THICKNESS, 0.600 - CLOTH_THICKNESS),   # left lobe outbound limb
    (0.600 - CLOTH_THICKNESS, 0.600 - CLOTH_THICKNESS),   # left lobe fold
    (0.600 - 3 * CLOTH_THICKNESS, 0.600 - 3 * CLOTH_THICKNESS),  # left lobe return, behind the outbound one
    (0.600 + 1.5 * CLOTH_THICKNESS, 0.600 + 1.5 * CLOTH_THICKNESS),  # knot pass 2, between the lobes
    (0.600 - 2 * CLOTH_THICKNESS, 0.600 - 2 * CLOTH_THICKNESS),  # right lobe outbound limb
    (0.600 - 2 * CLOTH_THICKNESS, 0.600 - 2 * CLOTH_THICKNESS),  # right lobe fold
    (0.600 - 3 * CLOTH_THICKNESS, 0.600 - 3 * CLOTH_THICKNESS),  # right lobe return
    (0.600 + 3 * CLOTH_THICKNESS, 0.600 + 3 * CLOTH_THICKNESS),  # knot pass 3: the tie wrapped over the lobes
    (0.600 + 3 * CLOTH_THICKNESS, 0.600 - CLOTH_THICKNESS),      # down tail leaves the tie
)


def _plane(xy):
    """Crop pixel station -> plane coordinates, where every surface is authored."""
    return tp(crop(*xy))


def build():
    knot = _plane(KNOT_XY)
    tail_exit = _plane(LEFT_TAIL_EXIT_XY)
    left_tip = _plane(LEFT_LOBE_TIP_XY)
    right_tip = _plane(RIGHT_LOBE_TIP_XY)
    down_dir = _unit((DOWN_DIRECTION_XY[0], -DOWN_DIRECTION_XY[1]))
    chord = (knot[0] - tail_exit[0], knot[1] - tail_exit[1])
    sag_dir = _perp(_unit(chord))
    if sag_dir[1] > 0.0:      # the left tail sags downward on the chest
        sag_dir = (-sag_dir[0], -sag_dir[1])
    left_tail = fam._bezier(
        tail_exit,
        _add(_add(tail_exit, _mul(chord, 0.30)), _mul(sag_dir, TAIL_SAG)),
        _add(_add(knot, _mul(chord, -0.30)), _mul(sag_dir, TAIL_SAG * 0.5)),
        knot, 16)
    lobe_l = _lobe(knot, left_tip, LIMB_SEPARATION)
    lobe_r = _lobe(knot, right_tip, LIMB_SEPARATION)
    down_end = _add(knot, _mul(down_dir, DOWN_LENGTH))
    down_tail = fam._bezier(knot, _add(knot, _mul(down_dir, DOWN_LENGTH * 0.35)),
                            _add(down_end, _mul(down_dir, -DOWN_LENGTH * 0.30)), down_end, 12)
    # The strip really passes through the knot between the lobes, so the two limbs
    # are joined by short pieces of the same cloth instead of a jump.
    through_knot_0 = _bridge(knot, lobe_l[0][0], knot, -3.0)
    through_knot_1 = _bridge(lobe_l[-1][-1], lobe_r[0][0], knot, 8.0)
    through_knot_2 = _bridge(lobe_r[-1][-1], knot, knot, 6.0)
    pieces = ([left_tail, through_knot_0] + lobe_l + [through_knot_1] + lobe_r
              + [through_knot_2] + [down_tail])
    polyline, spans = _glue(pieces)
    count = len(polyline) - 1

    def z_at(t):
        u = t * count
        for (lo, hi), (za, zb) in zip(spans, PIECE_DEPTH):
            if u <= hi or (lo, hi) == spans[-1]:
                f = (u - lo) / max(1, hi - lo)
                return za + (zb - za) * min(1.0, max(0.0, f))
        return PIECE_DEPTH[-1][1]

    surface = StripSurface(
        spine=lambda t: _polyline_point(polyline, t),
        half_width=lambda t: HALF_WIDTH,
        depth=z_at)
    part = SheetPart(
        name="A-bow-ribbon",
        intent="one continuous magenta ribbon visiting knot, left lobe, knot, right lobe, knot, both tails",
        front_fill=FRONT_FILL, back_fill=BACK_FILL, grid=surface.grid(samples=120, cols=4),
        anchors={"knot": ((knot[0], knot[1], 0.620), (1.0, 0.0))},
        authored=(("knot", knot), ("left_lobe_tip", LEFT_LOBE_TIP_XY),
                  ("right_lobe_tip", RIGHT_LOBE_TIP_XY), ("left_tail_exit", tail_exit)))
    marks = _marks(surface, spans, count)
    return {"A-bow-ribbon": part}, marks, dict(polyline=polyline, half_width=HALF_WIDTH,
                                               spans=spans, count=count)


def _polyline_point(polyline, t):
    if t <= 0.0:
        return polyline[0]
    if t >= 1.0:
        return polyline[-1]
    u = t * (len(polyline) - 1)
    i = min(len(polyline) - 2, int(u))
    f = u - i
    a, b = polyline[i], polyline[i + 1]
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def _marks(surface, spans, count):
    """Cloth marks on the ribbon: the two cloth edges, and one crease per real fold.

    A crease is short and lies on the fold that produced it: across the turning fold of
    each lobe, and across the tie where the ribbon crosses itself.  There is no mark
    that sweeps a whole limb, because a ribbon has no such line.
    """
    marks = [("A-bow-ribbon-edge-front", "A-bow-ribbon", "silhouette", surface.edge(0.0, 1.0, 1.0, 120), INK),
             ("A-bow-ribbon-edge-back", "A-bow-ribbon", "silhouette", surface.edge(0.0, 1.0, -1.0, 120), INK)]
    for name, piece in (("A-bow-left-fold-crease", 3), ("A-bow-right-fold-crease", 7)):
        lo, hi = spans[piece]
        centre = (lo + hi) / 2 / count
        half = 0.35 * (hi - lo) / count
        marks.append((name, "A-bow-ribbon", "fold_edge",
                      tuple(surface.point(centre - half + 2 * half * i / 7,
                                          -0.8 + 1.6 * i / 7) for i in range(8)), INK))
    lo, hi = spans[9]
    centre = (lo + hi) / 2 / count
    half = 0.35 * (hi - lo) / count
    marks.append(("A-bow-knot-wrap-fold", "A-bow-ribbon", "fold_edge",
                  tuple(surface.point(centre - half + 2 * half * i / 7,
                                      -0.9 + 1.8 * i / 7) for i in range(8)), INK))
    return marks
