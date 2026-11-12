"""A-collar-left / A-collar-right: the two leaves of the sailor collar.

Observed in the crop: a light collar field with a dark trim band running from each
shoulder toward a V at the sternum.  Artist hypothesis: the two leaves are one
opening relation.  They share the front convergence station Q and one front width,
so the trim meets at a point instead of crossing, and their supports are made to
agree in depth along the seam they share (a shared seam on two unrelated depth
planes is not one collar).

Each leaf is authored in its own local frame: the origin is that leaf's root R and
local +u runs along R -> Q.  Each leaf keeps only R, its shoulder S and its edge E;
Q is one shared relation (see `opening()`), not a second copy.
"""
from __future__ import annotations

import math

from . import families as fam
from .frames import (Anchor, PartFrame, PlanarPart, Point, align_depths, crop, to_local_geometry,
                     tp, unit2)

OPENING_XY = (214.0, 158.0)      # shared sternum convergence station (crop px)
FRONT_WIDTH = 14.0               # finite front width of the shared seam

LEFT = dict(root=(174.0, 92.0), edge=(137.0, 159.0), shoulder=(168.0, 128.0),
            inner_bend=1.5, root_width=8.0, palette="#a8c9d7", trim="#293346",
            z=0.34, grad=(-0.0004, 0.0002))
RIGHT = dict(root=(230.0, 78.0), edge=(279.0, 150.0), shoulder=(255.0, 139.0),
             inner_bend=-2.0, root_width=8.0, palette="#91b9ca", trim="#293346",
             z=0.35, grad=(0.0001, 0.0003))


def opening() -> Point:
    """The one shared opening station, in plane coordinates."""
    return crop(*OPENING_XY)


def _frame(spec: dict, name: str) -> PartFrame:
    root = crop(*spec["root"])
    q = opening()
    angle = math.degrees(math.atan2(q.v - root.v, q.u - root.u))
    return PartFrame(name, root, angle, spec["z"], spec["grad"])


def _local_spec(spec: dict, frame: PartFrame) -> dict:
    """Convert the leaf's authored crop stations into its own local frame."""
    local = {k: frame.to_local(crop(*spec[k])) for k in ("root", "edge", "shoulder")}
    q = frame.to_local(opening())
    return dict(authored_xy={"R": tp(local["root"]), "Q": tp(q), "E": tp(local["edge"]),
                             "S": tp(local["shoulder"])},
                authored_input_xy={"R": local["root"], "E": local["edge"], "S": local["shoulder"]},
                inner_bend=spec["inner_bend"], root_width=spec["root_width"],
                width_floor=1.5, front_width=FRONT_WIDTH, palette=spec["palette"])


def _plane_spec(spec: dict) -> dict:
    """The same authored leaf stations in the shared plane the pair is solved in."""
    return dict(authored_xy={"R": tp(crop(*spec["root"])), "Q": tp(opening()),
                             "E": tp(crop(*spec["edge"])), "S": tp(crop(*spec["shoulder"]))},
                authored_input_xy={"R": tp(crop(*spec["root"])), "E": tp(crop(*spec["edge"])),
                                   "S": tp(crop(*spec["shoulder"]))},
                inner_bend=spec["inner_bend"], root_width=spec["root_width"],
                width_floor=1.5, front_width=FRONT_WIDTH, palette=spec["palette"])


def build():
    """Return (parts by name, shared opening facts)."""
    frames = {"A-collar-left": _frame(LEFT, "A-collar-left"),
              "A-collar-right": _frame(RIGHT, "A-collar-right")}
    specs = {"A-collar-left": _local_spec(LEFT, frames["A-collar-left"]),
             "A-collar-right": _local_spec(RIGHT, frames["A-collar-right"])}
    names = ("A-collar-left", "A-collar-right")
    # The pair is one coupled relation (a shared front seam), so it is solved once in
    # the shared plane; each leaf's artwork is then stored in that leaf's own frame.
    geoms = fam.wrap_strips(tuple(_plane_spec(LEFT if n == names[0] else RIGHT) for n in names), names)
    # The two leaves must lie on supports that agree in depth along Q..Q'.
    q = geoms[0].named_stations["Q"]
    q_prime = geoms[0].named_stations["Q_prime"]
    fa, fb = align_depths(frames[names[0]], frames[names[1]], Point(*q), unit2((q_prime[0] - q[0], q_prime[1] - q[1])))
    aligned = {names[0]: fa, names[1]: fb}

    parts = {}
    for name, geom in zip(names, geoms):
        frame = aligned[name]
        loc = {k: frame.to_local(Point(*v)) for k, v in geom.named_stations.items()
               if isinstance(v, tuple) and len(v) == 2}
        outline, edges = to_local_geometry(geom, frame, name)
        outer = geom.named_stations["outer_tangent"]
        # project the generated outer sweep into the leaf's local frame
        q_prime_tangent = (outer[0] * frame.axis[0] + outer[1] * frame.axis[1],
                           outer[0] * frame.perp[0] + outer[1] * frame.perp[1])
        # Only the stations a joint needs are declared.  The leaf's free-edge stations
        # (E, S) and its copy of the opening station Q are artwork inputs, not joints,
        # so they are not anchors: an anchor that no joint reads is an unchecked claim.
        anchors = {
            "R": Anchor(loc["R"], (1.0, 0.0)),
            "Q_prime": Anchor(loc["Q_prime"], q_prime_tangent),
        }
        parts[name] = PlanarPart(
            name=name,
            intent="finite-width collar leaf on the shared opening relation; trim is its outer boundary",
            frame=frame, outline=outline, edges=edges, fill=specs[name]["palette"],
            anchors=anchors,
            authored=tuple((k, v) for k, v in specs[name]["authored_input_xy"].items()))
    return parts, {"Q_plane": Point(*q), "Q_prime_plane": Point(*q_prime)}
