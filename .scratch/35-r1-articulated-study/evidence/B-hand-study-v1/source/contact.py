"""contact.py - the hand is built out of the dish, not drawn beside it.

Every point where the hand meets the dish is read off a ring the dish's own mesh derives
(`dish.derived_rings`), then pushed along that ring's *surface normal* by the digit's own
radius plus one stated clearance.  So:

  * a fingertip rests on the rim's top band, and its centre is one tip-radius from the band's
    surface - contact is a distance, and a distance is a test;
  * a finger's knuckle passes over the rim's outer corner and its shaft lies along the dish's
    outer wall, both read from the rings;
  * the thumb presses the outer wall at two derived heights;
  * the palm's far end sits at the dish's own foot ring, so the dish rests on the palm.

What is authored is the pose: which ring station each digit takes, the digit radii, how far
over the rim each tip reaches, the palm's length and where the wrist leaves the frame.  Those
are hypotheses.  Where each digit meets the dish is not.
"""
from __future__ import annotations

import math

import numpy as np

import digits
import geo


def ring_point(ring, station_deg):
    """The ring's point and its outward surface normal at a local dish angle, in degrees."""
    pts, nrm = ring["points"], ring["normals"]
    n = len(pts)
    f = (float(station_deg) % 360.0) / 360.0 * n
    i0 = int(math.floor(f)) % n
    i1 = (i0 + 1) % n
    w = f - math.floor(f)
    p = pts[i0] * (1.0 - w) + pts[i1] * w
    unit_n = geo.unit(nrm[i0] * (1.0 - w) + nrm[i1] * w)
    return p, unit_n


def blend_rings(a, b, t):
    """A ring between two derived rings: the rim's top band, sampled at a fraction across."""
    t = min(max(float(t), 0.0), 1.0)
    p = a["points"] * (1.0 - t) + b["points"] * t
    n = geo.unit(a["normals"] * (1.0 - t) + b["normals"] * t)
    return {"points": p, "normals": n, "row": None,
            "radius": float(np.linalg.norm(p[0, :2])), "z": float(p[0, 2])}


def finger(name, rings, *, root, station, reach, radii, clearance, samples=24, thin=0.88):
    """One finger: root on the palm's knuckle line, over the wall, over the rim's outer corner,
    tip resting on the rim's top band `reach` of the way across it.

    Three of the four knots come from the dish's derived rings; the root comes from the palm's
    own end.  A finger therefore cannot float: it is pinned to the dish at three places and to
    the hand at one.
    """
    r_root, r_wall, r_rim, r_tip = radii
    law = digits.law(((0.0, r_root), (0.42, r_wall), (0.66, r_rim), (1.0, r_tip)))
    wall_p, wall_n = ring_point(rings["wall"][0.35], station)
    out_p, out_n = ring_point(rings["rim_outer"], station)
    band = blend_rings(rings["rim_outer"], rings["rim_inner"], reach)
    tip_p, tip_n = ring_point(band, station)
    knots = [np.asarray(root, float),
             wall_p + wall_n * (r_wall + clearance),
             out_p + out_n * (r_rim + clearance),
             tip_p + tip_n * (r_tip + clearance)]
    return digits.tube(name, knots, law, samples=samples, angles=20, thin=thin,
                       up_hint=(0.0, 0.0, 1.0))


def thumb(name, rings, base, *, station, radii, clearance, reach=0.45, samples=22, thin=0.95):
    """The thumb: from the palm's own flank, out along the near wall, pressing it twice.

    Its last knot sits on the rim's outer band at the same station, so the thumb visibly runs
    up the wall and its pad meets the rim - the opposition the grip needs.
    """
    r_base, r_low, r_high = radii
    law = digits.law(((0.0, r_base), (0.55, r_low), (1.0, r_high)))
    low_p, low_n = ring_point(rings["wall"][0.35], station)
    high = blend_rings(rings["rim_outer"], rings["rim_inner"], reach)
    high_p, high_n = ring_point(high, station)
    knots = [np.asarray(base, float),
             low_p + low_n * (r_low + clearance),
             high_p + high_n * (r_high + clearance)]
    return digits.tube(name, knots, law, samples=samples, angles=20, thin=thin,
                       up_hint=(0.0, 0.0, 1.0))


def palm(name, rings, *, wrist, mid, radii, thin, clearance, samples=28):
    """The palm: a flattened mass from the wrist to the dish's own foot.

    The distal station is set back by one cap radius along the axis, because the tube's rounded
    end reaches one radius past its last station; the cap therefore lands on the foot ring's
    normal at `clearance`.  Returns the patch, the distal station and the palm's own frame
    (axis, lateral, normal), which is where the digits are rooted.
    """
    r_wrist, r_mid, r_end = radii
    law = digits.law(((0.0, r_wrist), (0.45, r_mid), (1.0, r_end)))
    foot_p, foot_n = ring_point(rings["foot"], 270.0)
    target = foot_p + foot_n * (r_end * thin + clearance)
    wrist = np.asarray(wrist, float)
    axis = geo.unit(target - wrist)
    end_station = target - axis * (r_end * 0.92)
    knots = [wrist, np.asarray(mid, float), end_station]
    patch = digits.tube(name, knots, law, samples=samples, angles=24, thin=thin,
                        up_hint=(0.0, 0.0, 1.0))
    lateral = geo.unit(np.cross(axis, np.array([0.0, 0.0, 1.0])))
    if lateral[0] < 0.0:                      # +lateral always points to the drawer's right
        lateral = -lateral
    normal = geo.unit(np.cross(lateral, axis))
    return patch, {"station": end_station, "axis": axis, "lateral": lateral,
                   "normal": normal, "radius": r_end}
