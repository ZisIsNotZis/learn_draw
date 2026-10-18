"""A-hair-sheet: one head-attached two-sided sheet that frames the head and falls.

Observed in the crop: blue hair masses on both sides of the face, the upper head cut
by the frame, and the strands passing the shoulders.  Artist hypothesis (mechanism
kept from the project's S1 sketch, per issue 54): the hair is ONE sheet attached at
the head; its route leaves the crop at the lower left, rises past the left of the
face, passes over the crown behind the head, comes forward over the right shoulder
and falls to the bottom edge.  The sheet turns over as it crosses the crown, so its
reverse side faces the camera on the right fall.  Nothing is painted by declaration:
the fill of each face comes from its own projected winding.

Depth: the crown section sits behind the head (z ~ 0.18 against the head's 0.30), while
both falls hang in front of the shoulders (z ~ 0.45-0.52 against the sleeves' 0.30), so
the head occludes the crown and the falls occlude the sleeve tops.  That is one
continuous sheet passing behind the skull and in front of the shoulders; no occlusion
is authored.

Authored coordinates (five landmarks): the two fall terminals, the left mass bulge, the
crown crossing, and the right shoulder crossing.  The route between them, the width
profile, the depth profile, the quarter-turn twist and the shoulder curl come from
generators, so no part of the strip is a hand-typed station table.
"""
from __future__ import annotations

import math

from . import families as fam
from .frames import SheetPart, StripSurface, crop, tp

# crop-pixel landmarks (y down). Five hand-typed coordinates; everything else is generated.
LEFT_TIP_XY = (126.0, 356.0)        # left fall terminal: tapers to a point above the left cuff
LEFT_BULGE_XY = (84.0, 188.0)       # left mass, the widest part of the left fall
CROWN_XY = (206.0, -22.0)           # crown crossing, above the frame and behind the head
RIGHT_SHOULDER_XY = (322.0, 210.0)  # right fall crossing the right shoulder
RIGHT_TIP_XY = (286.0, 492.0)       # right fall terminal at the bottom edge

OUTSIDE_FILL = "#2f5f9b"     # the sheet's outside, as it faces the camera on the left fall
INSIDE_FILL = "#4b7fb6"      # the reverse side, which faces the camera after the crown turn
INK = "#233c60"

# Generated route shape (not coordinates): one catmull through the landmarks, a
# moderate sample count, one curl pulse centered on the shoulder station.
ROUTE_SAMPLES = 16
CURL_HALF_WINDOW = 0.085     # half width of the curl, as a fraction of the route
CURL_AMPLITUDE = 15.0        # px of lateral excursion at the curl's centre
WIDTH_TIP = 3.0              # a tapered terminal, not a square cut
WIDTH_MAX = 40.0             # the mass beside the face
CROWN_DEPTH = 0.18           # behind the head (head is 0.30)
FALL_DEPTH = 0.52            # in front of the shoulders (sleeves are 0.30)
TWIST_START = 0.48           # the quarter turn happens here, above the frame
TWIST_SPAN = 0.10
STEPS = 6


def _smoothstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def _plane(xy):
    return tp(crop(*xy))


def _base_route():
    """The generated spine: a catmull through the five landmarks, as (x, y) pairs."""
    stations = [_plane(p) for p in (LEFT_TIP_XY, LEFT_BULGE_XY, CROWN_XY,
                                    RIGHT_SHOULDER_XY, RIGHT_TIP_XY)]
    return fam._catmull_open(stations, ROUTE_SAMPLES)


def _curl(t: float, shoulder_t: float) -> float:
    """Lateral excursion of the route at the shoulder: the fall curls past the shoulder."""
    lo, hi = shoulder_t - CURL_HALF_WINDOW, shoulder_t + CURL_HALF_WINDOW
    if not lo < t < hi:
        return 0.0
    return CURL_AMPLITUDE * math.sin(math.pi * (t - lo) / (hi - lo))


def _spine_factory():
    dense = _base_route()
    count = len(dense) - 1
    # the curl is centred on the generated station nearest the shoulder landmark
    shoulder = _plane(RIGHT_SHOULDER_XY)
    nearest = min(range(count + 1),
                  key=lambda i: (dense[i][0] - shoulder[0]) ** 2 + (dense[i][1] - shoulder[1]) ** 2)
    shoulder_t = nearest / count

    def spine(t: float):
        u = t * count
        i = min(count - 1, int(u))
        f = u - i
        a, b = dense[i], dense[i + 1]
        x = a[0] + (b[0] - a[0]) * f
        y = a[1] + (b[1] - a[1]) * f
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length > 1e-12:
            offset = _curl(t, shoulder_t)
            x += (-dy / length) * offset
            y += (dx / length) * offset
        return (x, y)

    return spine, shoulder_t


def half_width(t: float) -> float:
    """A tapered terminal, a maximum beside the face, and variation along the route."""
    return WIDTH_TIP + (WIDTH_MAX - WIDTH_TIP) * math.sin(math.pi * min(1.0, max(0.0, t))) ** 0.6


def depth(t: float) -> float:
    """Behind the head at the crown, in front of the shoulders on both falls."""
    return CROWN_DEPTH + (FALL_DEPTH - CROWN_DEPTH) * abs(2.0 * t - 1.0) ** 0.75


def twist(t: float) -> float:
    """A quarter-turn crossing near the crown: the sheet's reverse side faces the camera
    on the right fall.  The crossing sits above the frame, where the strip is edge-on."""
    return math.pi * _smoothstep((t - TWIST_START) / TWIST_SPAN)


def build():
    spine, shoulder_t = _spine_factory()
    surface = StripSurface(spine=spine, half_width=half_width, depth=depth, twist=twist)
    part = SheetPart(
        name="A-hair-sheet",
        intent="one head-attached hair sheet; the reverse side faces the camera after the crown turn",
        front_fill=OUTSIDE_FILL, back_fill=INSIDE_FILL,
        grid=surface.grid(samples=110, cols=4),
        anchors={},
        authored=(("left_tip", LEFT_TIP_XY), ("left_bulge", LEFT_BULGE_XY),
                  ("crown", CROWN_XY), ("right_shoulder", RIGHT_SHOULDER_XY),
                  ("right_tip", RIGHT_TIP_XY)))
    marks = [("A-hair-sheet-edge-front", "A-hair-sheet", "silhouette", surface.edge(0.0, 1.0, 1.0, 140), INK),
             ("A-hair-sheet-edge-back", "A-hair-sheet", "silhouette", surface.edge(0.0, 1.0, -1.0, 140), INK)]
    # Creases only where the sheet's own route bends: the left mass, the crown turn and
    # the shoulder curl.  Each is a short curve lying on the surface, never a chord.
    for name, centre, half_window in (("A-hair-left-mass-fold", 0.16, 0.030),
                                      ("A-hair-crown-fold", 0.53, 0.035),
                                      ("A-hair-shoulder-curl-fold", shoulder_t + 0.03, 0.028)):
        points = tuple(surface.point(centre - half_window + 2 * half_window * i / 8,
                                     0.75 - 1.55 * i / 8) for i in range(9))
        marks.append((name, "A-hair-sheet", "fold_edge", points, INK))
    return {"A-hair-sheet": part}, marks, dict(surface=surface, dense=_base_route(),
                                               shoulder_t=shoulder_t)
