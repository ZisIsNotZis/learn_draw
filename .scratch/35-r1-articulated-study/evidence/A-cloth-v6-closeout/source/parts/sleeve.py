"""A-left-sleeve / A-right-sleeve and their cuffs: two whole sleeves.

Observed in the crop: the right sleeve is a large light puff ending in a wide dark
navy cuff; a second, smaller sleeve exists on the left with its own dark cuff around
(84,257)-(105,271), partly covered by the pink bow tail, with a white sleeve sliver
above it.  Both sleeves are authored whole here — shoulder cap, sleeve, cuff — each
as its own component on its own support.  The second cuff's surviving shape is
whatever the depth engine leaves visible; nothing is cut, shortened or authored as
a "visible part".

Each sleeve is authored in its own local frame: origin at its shoulder seat, +u
along the sleeve axis to the cuff centre.  The seat is *derived* from the bodice's
own boundary relation (`bodice.side_station`), not copied as a coordinate, so a
sleeve cannot drift off the shoulder it is sewn into.
"""
from __future__ import annotations

import math

from . import families as fam
from .frames import (Anchor, ClothEdge, PartFrame, PlanarPart, Point, align_depths, as_points,
                     crop, plain_geometry)

# shoulder_radius/cuff_radius/fullness/cap_height/skew are cloth-family values (artist
# hypothesis); cuff_centre is the one authored coordinate per sleeve.
RIGHT = dict(cuff_xy=(362.0, 300.0), shoulder_radius=29.0, cuff_radius=20.0, fullness=16.0,
             cap_height=34.0, skew=3.5, palette="#e2e2d7", seat_t=0.0, seat_left_side=True,
             z=0.30, grad=(-0.0003, -0.0004), band_depth=13.0, seat_anchor="shoulder_left")
LEFT = dict(cuff_xy=(95.0, 263.0), shoulder_radius=24.0, cuff_radius=12.0, fullness=11.0,
            cap_height=22.0, skew=2.0, palette="#e2e2d7", seat_t=0.16, seat_left_side=False,
            z=0.30, grad=(0.0001, -0.0003), band_depth=13.0, seat_anchor="left_seat")
CUFF_FILL = "#29354d"


def _pt(xy) -> Point:
    return Point(float(xy[0]), float(xy[1]))


def _shifted(xy, shift: Point) -> Point:
    return Point(float(xy[0]) - shift.u, float(xy[1]) - shift.v)


def _sleeve(prefix: str, spec: dict, seat: Point):
    """Build one sleeve and its cuff from the seat relation and the cuff centre."""
    c = crop(*spec["cuff_xy"])
    axis_angle = math.degrees(math.atan2(c.v - seat.v, c.u - seat.u))
    frame = PartFrame(f"{prefix}-sleeve", seat, axis_angle, spec["z"], spec["grad"])
    length = math.hypot(c.u - seat.u, c.v - seat.v)
    local_spec = dict(authored_xy={"S": (0.0, 0.0), "C": (length, 0.0)},
                      authored_input_xy={"C": (length, 0.0)},
                      shoulder_radius=spec["shoulder_radius"], cuff_radius=spec["cuff_radius"],
                      fullness=spec["fullness"], cap_height=spec["cap_height"],
                      skew=spec["skew"], palette=spec["palette"])
    geom = fam.sleeve_family(local_spec)
    cuff_spec = dict(band_depth=spec["band_depth"], band_ease=0.0,
                     cuff_radius=spec["cuff_radius"])
    cuff_geom = fam.cuff_family(cuff_spec, geom)
    # The cuff is its own part on its own support, in a frame whose origin is the
    # shared terminal section. The two supports are made to agree along that seam.
    cuff_frame_raw = PartFrame(f"{prefix}-cuff", c, axis_angle, spec["z"], spec["grad"])
    seam_point = c
    section = frame.perp          # the shared terminal section runs across the sleeve axis
    sleeve_aligned, cuff_frame = align_depths(frame, cuff_frame_raw, seam_point, section)
    frame = sleeve_aligned
    # Cuff artwork lives in the cuff's own frame: the generated band is expressed in
    # the sleeve's local coordinates, so subtract the sleeve length along +u.
    shift = Point(length, 0.0)
    cuff_outline = tuple(Point(p.u - shift.u, p.v - shift.v) for p in as_points(cuff_geom.outline))
    cuff_edges = tuple(ClothEdge(e.type, tuple(Point(q.u - shift.u, q.v - shift.v)
                                              for q in as_points(e.points)), f"{prefix}-cuff", e.intent)
                       for e in cuff_geom.edges)
    sleeve_outline, sleeve_edges = plain_geometry(geom, f"{prefix}-sleeve")
    sleeve = PlanarPart(
        name=f"{prefix}-sleeve",
        intent="one puff sleeve from its shoulder cap to the shared cuff section",
        frame=frame, outline=sleeve_outline, edges=sleeve_edges, fill=spec["palette"],
        anchors={"seat": Anchor(Point(0.0, 0.0), (0.0, 1.0)),
                 "terminal_left": Anchor(_pt(geom.named_stations["cuff_left"]), (0.0, 1.0)),
                 "terminal_right": Anchor(_pt(geom.named_stations["cuff_right"]), (0.0, -1.0))},
        authored=tuple(local_spec["authored_input_xy"].items()))
    cuff = PlanarPart(
        name=f"{prefix}-cuff",
        intent="whole transverse cuff band; its visible extent is a depth result",
        frame=cuff_frame, outline=cuff_outline, edges=cuff_edges, fill=CUFF_FILL,
        anchors={"contact_left": Anchor(_shifted(cuff_geom.named_stations["upper_left"], shift), (0.0, 1.0)),
                 "contact_right": Anchor(_shifted(cuff_geom.named_stations["upper_right"], shift), (0.0, -1.0))})
    return {sleeve.name: sleeve, cuff.name: cuff}


def build(bodice_module) -> dict:
    """Both sleeves, each seated on the bodice boundary relation."""
    parts = {}
    right_seat = bodice_module.side_station(RIGHT["seat_t"], RIGHT["seat_left_side"])
    left_seat = bodice_module.side_station(LEFT["seat_t"], LEFT["seat_left_side"])
    parts.update(_sleeve("A-right", RIGHT, right_seat))
    parts.update(_sleeve("A-left", LEFT, left_seat))
    return parts
