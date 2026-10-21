"""contact.py - the hand is built out of the dish, not drawn beside it.

Every point where the hand meets the dish is read off a ring the dish's own mesh derives
(`dish.derived_rings`), then pushed along that ring's *surface normal* by the digit's own
radius plus one stated clearance.  So:

  * a fingertip presses the dish's **underside**, and its centre is one tip-radius plus the
    clearance below that surface - contact is a distance, and a distance is a test;
  * the digits reach the underside from below, so the plate's near rim stays the nearest thing
    in the drawing and every digit that reaches past it is *behind* it;
  * the thumb presses the underside on the near flank, opposing the fingers across the palm;
  * the palm's distal end meets the dish's own foot ring, the lowest ring of its underside.

What is authored is the pose: which underside station each digit takes, how far in toward the
axis each pad reaches, the digit radii, the palm's length and where the wrist leaves the frame.
Those are hypotheses.  Where each digit meets the dish is not.
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


def underside_ring(rings, t):
    """A ring across the dish's underside, t = 0 at the axis and t = 1 at the foot ring.

    The underside's own rows are read from the mesh (`derived_rings`), and the seam between
    consecutive rows is interpolated, so any `t` lands on the surface the dish really has
    rather than on a table typed here.
    """
    keys = sorted(rings["under"])
    seq = [(0.0, rings["axis"])] + [(k, rings["under"][k]) for k in keys] + [(1.0, rings["foot"])]
    t = min(max(float(t), 0.0), 1.0)
    for (t0, a), (t1, b) in zip(seq, seq[1:]):
        if t0 <= t <= t1:
            f = 0.0 if t1 - t0 < 1e-12 else (t - t0) / (t1 - t0)
            return blend_rings(a, b, f)
    return seq[-1][1]


# How far back from the pad's approach knot the digit straightens onto the pad's own axis,
# in tip radii.  It has to exceed the tube's own sample spacing (roughly a tenth of a digit's
# arc) or the last cross-section still inherits the shaft's direction, and it has to stay short
# enough that the bend into the pad happens inside the digit's own silhouette - at 1.7 tip radii
# the thumb's bend breaks the palm's rear edge (`tests/test_occlusion_break.py`).
PAD_RUN = 1.6


def pad_contact(rings, t, station, radius, clearance):
    """The point a pad of `radius` has to sit at to touch the underside at (t, station)."""
    ring = underside_ring(rings, t)
    p, n = ring_point(ring, station)
    return p + n * (radius + clearance), p, n


def finger(name, rings, *, root, station, reach, radii, clearance, samples=24, thin=0.88):
    """One finger: from the palm's knuckle line, in under the dish, pad on its underside.

    `reach` is how far toward the axis the pad lands (0 at the axis, 1 at the foot ring); the
    pad, the ring it touches and the direction it presses are all read off the dish's own
    underside rows, and the finger is pinned to the palm at its root.  Its first ring is the
    knuckle, which is wider than the shaft so the palm's distal edge carries a row of knuckles
    instead of a flat seam.

    `radii` = (knuckle, proximal, middle, tip).  Nothing here is a coordinate of a contour.

    The **pad's axis runs parallel to the surface it rests on, and the digit arrives along it**.
    Three things hold that, and each cures a stand-off measured against the underside:

      * both pad knots - the approach and the tip - stand the same one tip-radius plus the
        clearance off the underside, each along its own station's normal, so the chord between
        them is parallel to the surface.  Offsetting the approach knot by the wider middle
        radius tilts the axis into the plate;
      * the radius law reaches the tip radius by the approach station and holds it, so the pad
        is a cylinder over that span rather than a taper that pulls the cross-section off the
        chord;
      * a third knot sits `PAD_RUN` tip radii behind the approach knot, on the pad's own axis.
        The tube's cross-sections are framed from the sampled centreline, so the last one
        inherits the direction between the last two samples - the *shaft's*, not the chord's -
        whenever the pad's chord is shorter than that sample spacing.  The middle digit lands
        at `reach = 0.98`, a chord of 2.2 px against a spacing of 10 px: its pad stood on edge
        to the plate and its nearest vertex was 13.5 px off, however exactly its contact point
        was derived.  With the knot the approach-to-tip span is a straight run along the pad
        axis, longer than the spacing, so the last cross-section is framed by the pad and its
        nearest vertex reaches the clearance.
    """
    r_knuckle, r_prox, r_mid, r_tip = radii
    law = digits.law(((0.0, r_knuckle * 0.86), (0.12, r_knuckle), (0.45, r_prox),
                      (0.74, r_mid), (0.88, r_tip), (1.0, r_tip)))
    approach_t = min(1.0, reach + (1.0 - reach) * 0.55)
    approach, _ap_p, _ap_n = pad_contact(rings, approach_t, station, r_tip, clearance)
    tip, _tip_p, _tip_n = pad_contact(rings, reach, station, r_tip, clearance)
    pad_axis = geo.unit(tip - approach)
    knots = [np.asarray(root, float), approach - pad_axis * (PAD_RUN * r_tip), approach, tip]
    return digits.tube(name, knots, law, samples=samples, angles=20, thin=thin,
                       up_hint=(0.0, 0.0, 1.0))


def thumb(name, rings, base, *, station, radii, clearance, reach=0.45, samples=22, thin=0.95):
    """The thumb: rooted on the palm's near flank, its pad pressing the underside on the near side.

    Same primitive as a finger, and the same rule: the pad's place is the dish's underside ring
    at `reach` plus one tip-radius plus the clearance.  What makes it a thumb is signed in the
    scene - its root is on the near flank of the palm and its direction opposes the fingers -
    and it is short, so it lands near the foot ring rather than reaching in toward the axis.
    """
    r_knuckle, r_prox, r_tip = radii
    law = digits.law(((0.0, r_knuckle * 0.88), (0.20, r_knuckle), (0.62, r_prox), (1.0, r_tip)))
    tip, _p, _n = pad_contact(rings, reach, station, r_tip, clearance)
    approach_t = min(1.0, reach + (1.0 - reach) * 0.45)
    approach, _ap, _an = pad_contact(rings, approach_t, station, r_prox, clearance)
    knots = [np.asarray(base, float), approach, tip]
    return digits.tube(name, knots, law, samples=samples, angles=20, thin=thin,
                       up_hint=(0.0, 0.0, 1.0))


def palm(name, rings, *, wrist, mid, radii, thin, clearance, reach, samples=28):
    """The palm: a flattened mass from the wrist off the frame to the dish's own underside.

    The distal station is set back by one cap radius along the axis, because the tube's rounded
    end reaches one radius past its last station; the cap therefore lands on the underside ring
    at `reach` (0 at the dish's axis, 1 at its foot ring), one cap half-axis plus the clearance
    below that surface.  So the plate rests on the palm, and the palm is *under* it - the plate's
    own near rim is nearer to the camera than anything the palm puts there.

    `radii` = (wrist, heel, mid, end): the heel is the widest ring of the palm and it sits a fifth
    of the way up the mass, which is what makes the bottom block read as the heel of a hand
    rather than as a length of wrist.

    Returns the patch and the palm's own frame (distal station, axis, lateral, normal), which is
    where the digits are rooted.
    """
    r_wrist, r_heel, r_mid, r_end = radii
    law = digits.law(((0.0, r_wrist), (0.18, r_heel), (0.45, r_mid), (1.0, r_end)))
    target_ring = underside_ring(rings, reach)
    target_p, target_n = ring_point(target_ring, 270.0)
    target = target_p + target_n * (r_end * thin + clearance)
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
                   "normal": normal, "radius": r_end, "reach": reach}
