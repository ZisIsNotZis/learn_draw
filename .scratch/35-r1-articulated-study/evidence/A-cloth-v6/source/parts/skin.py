"""A-visible-neck-skin: the neck field between the jaw and the collar opening.

Observed: pale skin between the collar roots, continuing up to a chin and jaw.  Artist
hypothesis: the neck is one field bounded above by the face's own jaw relation and
below by the collar's opening relation, so neither end is a separate outline that could
drift: the head and the collar decide both ends.  It tapers into the opening instead of
running as a straight-sided column to the frame.

Authored coordinates: none.  The frame origin is the shared opening station Q, the
upper boundary is the jaw relation taken from the head part, and the lower boundary is
the collar's opening relation; the two hand-typed stations that seed them belong to the
parts that own them.
"""
from __future__ import annotations

from . import families as fam
from .collar import opening
from .frames import Anchor, PartFrame, PlanarPart, Point, plain_geometry, tp

FRAME = PartFrame("A-neck-skin", opening(), 0.0, 0.30, (0.0, 0.0))
NECK_FILL = "#d9aca9"


def _toward(a: Point, b: Point) -> tuple[float, float]:
    import math
    dx, dy = b.u - a.u, b.v - a.v
    length = math.hypot(dx, dy)
    return (dx / length, dy / length)


def build(collar_parts, head_parts) -> tuple[dict, dict]:
    q = opening()
    left_root = collar_parts["A-collar-left"].plane_anchor("R")[0]
    right_root = collar_parts["A-collar-right"].plane_anchor("R")[0]
    jaw_left = head_parts["A-head-face"].plane_anchor("jaw_left")[0]
    jaw_right = head_parts["A-head-face"].plane_anchor("jaw_right")[0]
    chin = head_parts["A-head-face"].plane_anchor("chin")[0]
    local = {"R_left": FRAME.to_local(left_root), "Q": FRAME.to_local(q),
             "R_right": FRAME.to_local(right_root)}
    jaw = tuple(FRAME.to_local(Point(*p))
                for p in fam.jaw_section(tp(jaw_left), tp(chin), tp(jaw_right)))
    spec = dict(authored_xy={k: tp(v) for k, v in local.items()})
    geom = fam.neck_skin(spec, jaw)
    outline, edges = plain_geometry(geom, "A-visible-neck-skin")
    anchors = {"R_left": Anchor(local["R_left"], _toward(local["R_left"], local["Q"])),
               "Q": Anchor(local["Q"], _toward(local["Q"], local["R_left"])),
               "R_right": Anchor(local["R_right"], _toward(local["R_right"], local["Q"])),
               "jaw_left": Anchor(jaw[0], _toward(jaw[0], jaw[1])),
               "jaw_right": Anchor(jaw[-1], _toward(jaw[-1], jaw[-2]))}
    part = PlanarPart(
        name="A-visible-neck-skin",
        intent="neck field bounded by the face's jaw relation above and the collar opening below",
        frame=FRAME, outline=outline, edges=edges, fill=NECK_FILL,
        anchors=anchors, authored=())
    return {"A-visible-neck-skin": part}, local
