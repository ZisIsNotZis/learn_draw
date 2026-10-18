"""A-head-face: the face field whose jaw boundary and frame-cut skull make a head read.

Observed in the crop: the upper head is cut by the frame, a small chin and jaw are
visible above the collar, and the face is narrow between two hair masses.  Artist
hypothesis: the skull continues above the crop, so the face field is bounded below by
a generated chin/jaw relation and above by the frame; its temples widen slightly past
the jaw so the head is not a straight-sided column.  There is no facial-feature claim
(no eyes, nose or mouth): this part is a head *boundary*, which is what the review
asked to recover.

The jaw relation is shared with the neck field (`families.jaw_section` is called with
these same three stations), so the chin the face ends on is the chin the neck starts
from.

Authored coordinates (three): the chin and the two jaw corners.
"""
from __future__ import annotations

from . import families as fam
from .frames import Anchor, PartFrame, PlanarPart, Point, crop, plain_geometry, tp

CHIN_XY = (212.0, 122.0)
JAW_LEFT_XY = (198.0, 101.0)
JAW_RIGHT_XY = (241.0, 97.0)

FRAME = PartFrame("A-head", crop(216.0, 60.0), 0.0, 0.30, (0.0, 0.0))
FACE_FILL = "#e6c4bd"

# Generated, not authored: how far the skull continues above the jaw, and how much the
# temples widen beyond the jaw corners before the frame cuts the skull.
FACE_RISE = 210.0
FACE_WIDEN = 7.0


def _toward(a: Point, b: Point) -> tuple[float, float]:
    import math
    dx, dy = b.u - a.u, b.v - a.v
    length = math.hypot(dx, dy)
    return (dx / length, dy / length)


def build() -> dict:
    local = {k: FRAME.to_local(crop(*xy)) for k, xy in
             (("chin", CHIN_XY), ("jaw_left", JAW_LEFT_XY), ("jaw_right", JAW_RIGHT_XY))}
    spec = dict(authored_xy={k: tp(v) for k, v in local.items()},
                authored_input_xy={"chin": tp(local["chin"]),
                                   "jaw_left": tp(local["jaw_left"]),
                                   "jaw_right": tp(local["jaw_right"])},
                face_rise=FACE_RISE, face_widen=FACE_WIDEN)
    geom = fam.head_face(spec)
    outline, edges = plain_geometry(geom, "A-head-face")
    jaw = [Point(*p) for p in fam.jaw_section(tp(local["jaw_left"]), tp(local["chin"]),
                                              tp(local["jaw_right"]))]
    anchors = {"jaw_left": Anchor(local["jaw_left"], _toward(jaw[0], jaw[1])),
               "jaw_right": Anchor(local["jaw_right"], _toward(jaw[-1], jaw[-2])),
               "chin": Anchor(local["chin"], _toward(jaw[len(jaw) // 2 - 1], jaw[len(jaw) // 2]))}
    part = PlanarPart(
        name="A-head-face",
        intent="face field: generated chin/jaw boundary below, frame-cut skull above, no feature claim",
        frame=FRAME, outline=outline, edges=edges, fill=FACE_FILL, anchors=anchors,
        authored=tuple(spec["authored_input_xy"].items()))
    return {"A-head-face": part}
