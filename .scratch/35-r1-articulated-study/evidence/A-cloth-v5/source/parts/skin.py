"""A-visible-neck-skin: the skin field exposed by the collar opening.

Observed: pale skin between the collar roots, continuing above the crop.  Artist
hypothesis: the field is the neck cut by the same opening relation the collar
leaves use, so its boundary is the collar's inner boundary (no separate outline
that could drift away), and it continues above the frame instead of ending in a
rounded cap.

Local frame: origin at the shared opening station Q, +u to the right; the field's
upper continuation station is its one authored coordinate.
"""
from __future__ import annotations

from . import families as fam
from .frames import Anchor, PartFrame, PlanarPart, Point, crop, plain_geometry, tp
from .collar import opening

UPPER_CONTINUATION_XY = (203.0, -42.0)
FRAME = PartFrame("A-neck-skin", opening(), 0.0, 0.16, (0.0, -0.0002))


def build(collar_parts) -> tuple[dict, dict]:
    q = opening()
    left_root = collar_parts["A-collar-left"].plane_anchor("R")[0]
    right_root = collar_parts["A-collar-right"].plane_anchor("R")[0]
    local = {
        "R_left": FRAME.to_local(left_root),
        "Q": FRAME.to_local(q),
        "R_right": FRAME.to_local(right_root),
        "upper_continuation": FRAME.to_local(crop(*UPPER_CONTINUATION_XY)),
    }
    spec = dict(authored_xy={k: tp(local[k]) for k in ("R_left", "Q", "R_right", "upper_continuation")},
                authored_input_xy={"upper_continuation": tp(local["upper_continuation"])},
                palette="#d7aaa8")
    geom = fam.neck_skin(spec, {})
    outline, edges = plain_geometry(geom, "A-visible-neck-skin")
    def toward(a, b):
        import math
        dx, dy = b.u - a.u, b.v - a.v
        length = math.hypot(dx, dy)
        return (dx / length, dy / length)

    anchors = {"R_left": Anchor(local["R_left"], toward(local["R_left"], local["Q"])),
               "Q": Anchor(local["Q"], toward(local["Q"], local["R_left"])),
               "R_right": Anchor(local["R_right"], toward(local["R_right"], local["Q"])),
               "upper_continuation": Anchor(local["upper_continuation"], (0.0, 1.0))}
    part = PlanarPart(
        name="A-visible-neck-skin",
        intent="skin field exposed by the shared opening; continues above the crop, no rounded cap",
        frame=FRAME, outline=outline, edges=edges, fill=spec["palette"],
        anchors=anchors,
        authored=tuple(spec["authored_input_xy"].items()))
    return {"A-visible-neck-skin": part}, local
