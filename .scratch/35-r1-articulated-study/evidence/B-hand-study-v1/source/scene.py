"""scene.py - the authored pose: which part of the dish each digit takes, and how big it is.

This module holds every hand-typed number in the drawing, and nothing else.  Each entry is a
pose hypothesis - a ring station on the dish, a digit's radii, how far over the rim it reaches,
the palm's length - not a coordinate of a contour.  `contact.py` turns them into geometry by
reading the dish's rings.
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
#  ring station in degrees, how far across the rim's top band the tip reaches, the digit's
#  (root, wall, rim, tip) radii)
FINGERS = (
    ("index", -0.54, 246.0, 0.58, (33.0, 30.0, 27.0, 18.0)),
    ("middle", -0.18, 261.0, 0.88, (34.0, 31.0, 28.0, 19.0)),
    ("ring", 0.18, 279.0, 0.40, (32.0, 29.0, 26.0, 17.5)),
    ("little", 0.52, 297.0, 0.74, (27.0, 24.5, 22.0, 14.5)),
)
FINGER_GEOMETRY = dict(clearance=1.5, thin=0.88, samples=24)

THUMB = dict(station=226.0, radii=(44.0, 40.0, 36.0, 26.0), reach=0.16, clearance=1.5, thin=0.95)
THUMB_BASE_FRACTION = 0.86       # how far across the palm's mid cross-section the thumb roots

PALM = dict(wrist=(392.0, -300.0, -452.0), mid=(430.0, -212.0, -300.0),
            radii=(72.0, 110.0, 100.0), thin=0.58, clearance=1.5)


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
                                          clearance=PALM["clearance"])
    # the thumb roots in the palm's own mid mass, on the side away from the fingers
    thumb_base = (np.asarray(PALM["mid"], float)
                  + palm_frame["lateral"] * (-PALM["radii"][1] * THUMB_BASE_FRACTION)
                  + palm_frame["normal"] * (-PALM["radii"][1] * 0.10))

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
