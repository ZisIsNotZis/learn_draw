"""A-bodice-upper / A-derived-waist-band / A-bodice-continuation: one body cloth.

Observed: a light blouse field from the collar opening down to a gathered waist,
continuing past the crop.  Artist hypothesis: the upper field, the narrow waist
band and the continuation are one cloth cut by two section relations, so the band
is derived from the same body width field instead of being a drawn stripe.

Local frame: origin at the chest station C0, +u along the body axis toward the
waist station Cw.  The three pieces share this frame and its support, which is why
their shared sections cannot drift apart.
"""
from __future__ import annotations

import math

from . import families as fam
from .frames import Anchor, PartFrame, PlanarPart, Point, crop, to_local_geometry, tp

CHEST_XY = (231.0, 137.0)         # C0: top chest station (crop px)
WAIST_XY = (174.0, 365.0)         # Cw: waist direction station
LEFT_EDGE_XY = (330.0, 175.0)     # Eleft: the exposed side's silhouette station (crop right)
FRAME_Z0 = 0.10
FRAME_GRAD = (0.0, -0.0006)       # chest surface recedes upward, bulges at the gathered waist

BODY = dict(left_waist_width=48.0, right_widths=(100.0, 43.0),
            left_chest_fullness=9.0, right_chest_fullness=4.0,
            waist_start=0.82, waist_end=0.88,
            continuation_end_t=1.82, continuation_flare=28.0,
            palette="#e8e7dc")


def _toward(a: Point, b: Point) -> tuple[float, float]:
    """Unit local tangent from a to b: the seam direction where two cloths are sewn."""
    dx, dy = b.u - a.u, b.v - a.v
    length = math.hypot(dx, dy)
    if length <= 1e-12:
        raise ValueError("seam stations must differ")
    return (dx / length, dy / length)


def _frame() -> PartFrame:
    c0 = crop(*CHEST_XY)
    cw = crop(*WAIST_XY)
    angle = math.degrees(math.atan2(cw.v - c0.v, cw.u - c0.u))
    return PartFrame("A-bodice", c0, angle, FRAME_Z0, FRAME_GRAD)


FRAME = _frame()


def build(opening_plane: Point, left_root_plane: Point, right_root_plane: Point) -> dict:
    # The three pieces are one cloth cut by section relations, so the body field is
    # solved once in the shared plane and each piece's artwork is stored in its frame.
    spec = dict(authored_xy={"C0": tp(crop(*CHEST_XY)), "Cw": tp(crop(*WAIST_XY)),
                             "Eleft": tp(crop(*LEFT_EDGE_XY)), "Q": tp(opening_plane)},
                authored_input_xy={"Cw": tp(crop(*WAIST_XY)), "Eleft": tp(crop(*LEFT_EDGE_XY))},
                **BODY)
    # The generator closes its right0 silhouette chain with `right_root`. The body
    # frame's +v is the wearer's right, which is the crop's left, so the crop-left
    # collar root closes the right0 chain; the crop-right root closes the left0 chain.
    # Passing them the other way round makes the top boundary cross itself.
    opening_local = {"Q": tp(opening_plane),
                     "right_root": tp(left_root_plane),
                     "left_root": tp(right_root_plane)}
    upper = fam.bodice_upper(spec, opening_local)
    band = fam.waist_band(spec)
    continuation = fam.bodice_continuation(spec)
    st = upper.named_stations
    upper_outline, upper_edges = to_local_geometry(upper, FRAME, "A-bodice-upper")
    band_outline, band_edges = to_local_geometry(band, FRAME, "A-derived-waist-band")
    cont_outline, cont_edges = to_local_geometry(continuation, FRAME, "A-bodice-continuation")
    q_local = FRAME.to_local(opening_plane)
    lr_local = FRAME.to_local(left_root_plane)
    rr_local = FRAME.to_local(right_root_plane)
    shoulder_left_local = FRAME.to_local(side_station(0.0, True))
    shoulder_right_local = FRAME.to_local(side_station(0.0, False))
    parts = {}
    parts["A-bodice-upper"] = PlanarPart(
        name="A-bodice-upper",
        intent="chest cloth field bounded above by the shared opening and below by the waist section",
        frame=FRAME, outline=upper_outline, edges=upper_edges, fill=BODY["palette"],
        anchors={"Q": Anchor(q_local, _toward(q_local, lr_local)),
                 "opening_left_root": Anchor(lr_local, _toward(lr_local, q_local)),
                 "opening_right_root": Anchor(rr_local, _toward(rr_local, q_local)),
                 "shoulder_right": Anchor(shoulder_right_local, (0.0, 1.0)),
                 "shoulder_left": Anchor(shoulder_left_local, (0.0, -1.0)),
                 "waist_left": Anchor(FRAME.to_local(Point(*st["waist_left"])), _toward(
                     FRAME.to_local(Point(*st["waist_left"])), FRAME.to_local(Point(*st["waist_right"])))),
                 "waist_right": Anchor(FRAME.to_local(Point(*st["waist_right"])), _toward(
                     FRAME.to_local(Point(*st["waist_right"])), FRAME.to_local(Point(*st["waist_left"])))),
                 "waist_center": Anchor(FRAME.to_local(Point(*st["waist_center"])), (0.0, 1.0)),
                 "left_seat": Anchor(FRAME.to_local(side_station(0.16, False)), (0.0, 1.0))},
        authored=tuple(spec["authored_input_xy"].items()))
    wb = {k: FRAME.to_local(Point(*band.named_stations[k]))
          for k in ("upper_left", "upper_right", "lower_left", "lower_right")}
    parts["A-derived-waist-band"] = PlanarPart(
        name="A-derived-waist-band",
        intent="narrow band derived from the same body width field at the waist section",
        frame=FRAME, outline=band_outline, edges=band_edges, fill="#d9d8ce",
        anchors={"upper_left": Anchor(wb["upper_left"], _toward(wb["upper_left"], wb["upper_right"])),
                 "upper_right": Anchor(wb["upper_right"], _toward(wb["upper_right"], wb["upper_left"])),
                 "lower_left": Anchor(wb["lower_left"], _toward(wb["lower_left"], wb["lower_right"])),
                 "lower_right": Anchor(wb["lower_right"], _toward(wb["lower_right"], wb["lower_left"]))},
        attachments=(("A-bodice-upper", "upper_left", "waist_left"),))
    cb = {k: FRAME.to_local(Point(*continuation.named_stations[k]))
          for k in ("upper_left", "upper_right")}
    parts["A-bodice-continuation"] = PlanarPart(
        name="A-bodice-continuation",
        intent="the same body cloth continues below the waist band, exiting the crop without a hem",
        frame=FRAME, outline=cont_outline, edges=cont_edges, fill=BODY["palette"],
        anchors={"upper_left": Anchor(cb["upper_left"], _toward(cb["upper_left"], cb["upper_right"])),
                 "upper_right": Anchor(cb["upper_right"], _toward(cb["upper_right"], cb["upper_left"]))})
    return parts


def side_station(t: float, left_side: bool) -> Point:
    """A boundary station relation on the body cloth, in plane coordinates.

    Used by the sleeve parts to seat themselves on this same cloth: the sleeve
    does not carry its own copy of the shoulder location.
    """
    spec = dict(authored_xy={"C0": tp(crop(*CHEST_XY)), "Cw": tp(crop(*WAIST_XY)),
                             "Eleft": tp(crop(*LEFT_EDGE_XY))}, **BODY)
    left, right = fam.body_section(spec, t)
    return Point(*(left if left_side else right))
