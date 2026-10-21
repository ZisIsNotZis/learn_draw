"""scene.py - the authored pose: where each digit meets the dish's underside, and how big it is.

This module holds every hand-typed number in the drawing, and nothing else.  Each entry is a
pose hypothesis - a station around the dish, how far in toward the axis a pad reaches on the
underside, a digit's radii, the palm's length - not a coordinate of a contour.  `contact.py`
turns them into geometry by reading the dish's own derived rings, so the hand is *made out of*
the dish.

The hand is under the plate.  Every contact surface this file names is on the dish's underside,
which is the face that carries the weight; the plate's near rim is therefore the nearest thing
in the drawing and the digits that reach past it are behind it.
"""
from __future__ import annotations

import numpy as np

import contact
import dish
import geo

# The dish's pose in the world frame: tipped 12 degrees towards the viewer so the interior is
# readable.  The framing offset is computed from the dish's own projected extent, not typed.
DISH_POSE = dict(tilt_deg=12.0, offset=(400.0, 40.0, 0.0))

# (name, root offset across the palm's knuckle line as a fraction of the palm's end radius,
#  ring station in degrees around the dish, how far in toward the axis the pad lands on the
#  underside (0 = the axis, 1 = the foot ring), the digit's (knuckle, proximal, middle, tip)
#  radii).  The stations are deliberately uneven and the reaches differ by more than a digit's
#  width: five digits of one radius law on an even fan is the study's "rake tines" failure.
FINGERS = (
    ("index", -0.92, 228.0, 0.86, (33.0, 30.0, 27.0, 17.0)),
    ("middle", -0.30, 254.0, 0.98, (35.0, 32.0, 29.0, 19.0)),
    ("ring", 0.34, 286.0, 0.94, (30.0, 27.0, 24.0, 15.0)),
    ("little", 0.96, 316.0, 0.88, (25.0, 22.0, 19.0, 12.0)),
)
FINGER_GEOMETRY = dict(clearance=1.5, thin=0.88, samples=24)

# The thumb opposes on the near flank: its root is placed on the side of the palm's mid mass
# that faces the camera, its station is 26 degrees past the little finger, and it is short and
# thick, so its pad lands near the foot ring instead of reaching in toward the axis.
THUMB = dict(station=338.0, radii=(40.0, 38.0, 32.0, 26.0), reach=0.88,
             clearance=1.5, thin=0.95, base=0.86)

# (wrist, heel, mid, end) radii: the heel ring is the widest, a fifth of the way up the mass.
PALM = dict(wrist=(392.0, -150.0, -520.0), mid=(430.0, -70.0, -300.0),
            radii=(58.0, 92.0, 82.0, 66.0), thin=0.58, clearance=1.5, reach=0.30)


def parts(lift=0.0):
    """The drawing's parts.  The dish is built first because the hand is derived from it.

    `lift` raises the dish after the hand has been built from it, which is what makes the
    optional second image a proof that the pose is parameterised rather than a redraw.
    """
    dish_patch = dish.build(**DISH_POSE)
    rings = dish.derived_rings(dish_patch)
    dish_patch.mat = dish.material_split(dish_patch, rings)

    palm_patch, palm_frame = contact.palm("palm", rings, wrist=PALM["wrist"], mid=PALM["mid"],
                                          radii=PALM["radii"], thin=PALM["thin"],
                                          clearance=PALM["clearance"], reach=PALM["reach"])
    # the thumb roots in the palm's mid mass, on the flank that faces the camera: the sign is
    # chosen by measurement, not typed - of the two flanks, the nearer one wins
    across = palm_frame["lateral"] * (PALM["radii"][2] * THUMB["base"])
    flank = [np.asarray(PALM["mid"], float) + across,
             np.asarray(PALM["mid"], float) - across]
    thumb_base = min(flank, key=lambda p: float(geo.project(p)[2]))

    out = [("palm", palm_patch)]
    for name, root_off, station, reach, radii in FINGERS:
        root = (palm_frame["station"]
                + palm_frame["lateral"] * (root_off * palm_frame["radius"])
                + palm_frame["normal"] * (palm_frame["radius"] * 0.10))
        out.append((name, contact.finger(name, rings, root=root, station=station, reach=reach,
                                         radii=radii, **FINGER_GEOMETRY)))
    out.append(("thumb", contact.finger("thumb", rings, root=thumb_base,
                                        station=THUMB["station"], reach=THUMB["reach"],
                                        radii=THUMB["radii"], clearance=THUMB["clearance"],
                                        thin=THUMB["thin"], samples=22)))
    if lift:
        dish_patch.v = dish_patch.v + np.array([0.0, 0.0, float(lift)])
    out.append(("dish", dish_patch))
    return out, rings
