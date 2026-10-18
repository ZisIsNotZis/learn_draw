"""A-hair-sheet: one two-sided curved hair sheet.

Observed in the crop: a blue hair mass on the left of the face, a larger one on the
right, and the frame cutting both.  Artist hypothesis (the mechanism taken from the
project's S1 sketch): the hair is one head-attached sheet whose surface turns over
near the crest — the turn shows the sheet's inside.  So the sheet is authored once
and its two sides are painted by projected face orientation: deep blue outside,
mint inside.  The old flat single-colour band is gone.

Route: the sheet leaves the crop at the lower left, rises along the left side,
turns over at the crest (the turn is where the inside shows), passes above the
frame behind the head — the crop is a window, not the object's boundary — comes
back into the frame on the right of the neck, and falls to the lower right.

Depth: the left fall hangs behind the left sleeve, the right fall hangs in front of
the right sleeve, both behind the bow — a curtain that wraps around the body.  No
occlusion is authored; the engine derives it.

Authored coordinates (five landmarks: the two fall exits, the crest turn, the two
crossing stations); widths, depth and the interpolated spine come from generators.
"""
from __future__ import annotations

from . import families as fam
from .frames import SheetPart, StripSurface, crop, tp

# crop-pixel landmarks (y down)
FALL_LEFT_XY = (2.0, 302.0)
CREST_XY = (132.0, 34.0)
CROSSING_LEFT_XY = (168.0, -72.0)
CROSSING_RIGHT_XY = (252.0, -84.0)
FALL_RIGHT_XY = (298.0, 480.0)

# generated route between the landmarks (artist hypothesis, not a trace)
ROUTE = (
    (FALL_LEFT_XY, 20.0, 0.240),
    ((50.0, 244.0), 24.0, 0.240),
    ((86.0, 176.0), 26.0, 0.250),
    ((114.0, 104.0), 26.0, 0.280),
    (CREST_XY, 20.0, 0.300),          # crest, outbound
    ((150.0, 92.0), 14.0, 0.260),     # return limb: its inside faces the camera
    ((162.0, 22.0), 16.0, 0.300),
    (CROSSING_LEFT_XY, 15.0, 0.320),
    (CROSSING_RIGHT_XY, 16.0, 0.400),
    ((274.0, 18.0), 22.0, 0.500),
    ((302.0, 110.0), 28.0, 0.520),
    ((330.0, 206.0), 30.0, 0.520),
    ((334.0, 306.0), 28.0, 0.520),
    ((318.0, 404.0), 26.0, 0.500),
    (FALL_RIGHT_XY, 22.0, 0.480),
)

OUTSIDE_FILL = "#3c6ba8"
INSIDE_FILL = "#83cbbd"
INK = "#223c63"
STEPS = 6


def _interp(t, values):
    u = t * (len(values) - 1)
    i = min(len(values) - 2, int(u))
    f = u - i
    return values[i] + (values[i + 1] - values[i]) * f


def _plane(xy):
    return tp(crop(*xy))


def build():
    stations = [_plane(xy) for xy, _half, _z in ROUTE]
    halfs = [half for _xy, half, _z in ROUTE]
    depths = [z for _xy, _half, z in ROUTE]
    dense = fam._catmull_open(stations, STEPS)

    def spine(t):
        u = t * (len(dense) - 1)
        i = min(len(dense) - 2, int(u))
        f = u - i
        a, b = dense[i], dense[i + 1]
        return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)

    surface = StripSurface(spine=spine,
                           half_width=lambda t: _interp(t, halfs),
                           depth=lambda t: _interp(t, depths))
    part = SheetPart(
        name="A-hair-sheet",
        intent="one head-attached hair sheet; fill by projected face orientation (blue outside, mint inside)",
        front_fill=OUTSIDE_FILL, back_fill=INSIDE_FILL,
        grid=surface.grid(samples=80, cols=4),
        anchors={"fall_left": ((_plane(FALL_LEFT_XY)[0], _plane(FALL_LEFT_XY)[1], 0.400), (0.0, 1.0)),
                 "fall_right": ((_plane(FALL_RIGHT_XY)[0], _plane(FALL_RIGHT_XY)[1], 0.480), (0.0, 1.0))},
        authored=(("fall_left", FALL_LEFT_XY), ("crest", CREST_XY),
                  ("crossing_left", CROSSING_LEFT_XY), ("crossing_right", CROSSING_RIGHT_XY),
                  ("fall_right", FALL_RIGHT_XY)))
    marks = [("A-hair-sheet-edge-front", surface.edge(0.0, 1.0, 1.0, 110), INK),
             ("A-hair-sheet-edge-back", surface.edge(0.0, 1.0, -1.0, 110), INK)]
    for name, (t0, t1), (v0, v1) in (
            ("A-hair-left-strand", (0.06, 0.24), (-0.2, 0.35)),
            ("A-hair-crest-fold", (0.27, 0.36), (0.55, -0.5)),
            ("A-hair-right-strand", (0.62, 0.88), (-0.35, 0.15))):
        marks.append((name, tuple(surface.point(t0 + (t1 - t0) * i / 10,
                                                v0 + (v1 - v0) * i / 10) for i in range(11)),
                      "#2b4f7d"))
    return {"A-hair-sheet": part}, marks, dict(surface=surface, dense=dense, halfs=halfs, depths=depths)
