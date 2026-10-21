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



def pressed_ring(rings, t):
    """The dish's *pressed* surface across the near rim, read off the same mesh.

    `t` in [0, 1] runs across the rim's top band from its outer edge to its inner corner;
    `t` past 1 continues onto the bowl's interior (the surface inside the rim, which is the
    face a digit that wraps the rim presses).  This is not a second dish: every point is a
    blend of rings `dish.derived_rings` found in the emitted mesh.
    """
    if t <= 1.0:
        return blend_rings(rings["rim_outer"], rings["rim_inner"], t)
    keys = sorted(rings["bowl"])
    a = rings["rim_inner"]
    b = rings["bowl"][keys[0]]
    return blend_rings(a, b, min(1.0, t - 1.0))


def wrap_finger(name, rings, *, root, station, radii, clearance, land=(0.80, 1.20),
                over=0.12, samples=26, thin=0.88):
    """One digit that crosses the near rim: over the band, pad down on the interior.

    README H1: a joint reads only where exactly one contour breaks and the orders are mixed.
    This digit is the front piece of the joint - its centreline passes *above* the rim's own
    top band (`over`) and its pad lands on the pressed surface past the rim's inner corner
    (`land` = the two pad stations on `pressed_ring`), so its fill lies inside the dish's
    projected outline while the other four digits stay behind the plate.

    Its contact is the same law as `finger`: each pad knot stands one tip radius plus the
    stated clearance off the surface, along that station's own normal.
    """
    r_knuckle, r_prox, r_mid, r_tip = radii
    law = digits.law(((0.0, r_knuckle * 0.86), (0.12, r_knuckle), (0.45, r_prox),
                      (0.74, r_mid), (0.88, r_tip), (1.0, r_tip)))
    op, on = ring_point(pressed_ring(rings, over), station)
    over_pt = op + on * (r_mid + clearance)
    ap, an = ring_point(pressed_ring(rings, land[0]), station)
    approach = ap + an * (r_tip + clearance)
    tp, tn = ring_point(pressed_ring(rings, land[1]), station)
    tip = tp + tn * (r_tip + clearance)
    pad_axis = geo.unit(tip - approach)
    knots = [np.asarray(root, float), over_pt, approach - pad_axis * (PAD_RUN * r_tip),
             approach, tip]
    return digits.tube(name, knots, law, samples=samples, angles=20, thin=thin,
                       up_hint=(0.0, 0.0, 1.0))


def underside_cloud(rings, steps=25):
    """The dish's underside as points with outward normals: what a clearance is measured to.

    The axis ring is dropped: it collapses to a point and its normals are zero, so it is not a
    surface.  (A zero normal would make every signed distance 0 - a null measurement that reads
    as a perfect contact.)
    """
    import numpy as _np
    pts, nrm = [], []
    for t in _np.linspace(0.0, 1.0, steps):
        if t <= 1e-9:
            continue
        ring = underside_ring(rings, t)
        pts.append(ring["points"])
        nrm.append(ring["normals"])
    return _np.vstack(pts), _np.vstack(nrm)


def nearest_clearance(patch, surface):
    """The signed distance of a patch's nearest vertex to a surface cloud, along the normal."""
    import numpy as _np
    surf, surf_n = surface
    v = _np.asarray(patch.v, float).reshape(-1, 3)
    best = _np.inf
    for chunk in _np.array_split(_np.arange(len(v)), max(1, len(v) // 2000)):
        d = _np.linalg.norm(surf[None, :, :] - v[chunk, None, :], axis=2)
        idx = d.argmin(axis=1)
        best = min(best, float(((v[chunk] - surf[idx]) * surf_n[idx]).sum(axis=1).min()))
    return best


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


def palm(name, rings, *, wrist, mid, radii, thin, clearance, reach, samples=28):
    """The palm: a flattened mass from the wrist off the frame to the dish's own underside.

    The distal station is set back from the underside point at `reach` (0 at the dish's axis, 1
    at its foot ring) by exactly one end radius along the palm's own axis, because the tube's
    rounded end reaches one radius past its last station: the cap's last vertex therefore lands
    on that underside point, one stated clearance below the surface.  That is a distance, and
    `tests/test_hand_construction.py::TestContact::test_the_palm_cap_meets_the_underside`
    measures it.  So the plate rests on the palm, and the palm is *under* it - the plate's own
    near rim is nearer to the camera than anything the palm puts there.

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
    surface = underside_cloud(rings)
    wrist = np.asarray(wrist, float)
    # The cap's tip is one end radius past the last station, but the palm is a mass, not a point:
    # its shoulder reaches the curved underside before the tip does.  The set-back is therefore
    # solved - build, measure the nearest vertex against the dish's own underside, move the
    # station by the error - until the closest vertex sits at the stated clearance.  Nothing
    # here is a typed coordinate, and the loop's result is what the suite re-measures.
    offset = 0.0
    for _ in range(4):
        target = target_p + target_n * (offset + clearance)
        axis = geo.unit(target - wrist)
        end_station = target - axis * r_end
        knots = [wrist, np.asarray(mid, float), end_station]
        patch = digits.tube(name, knots, law, samples=samples, angles=24, thin=thin,
                            up_hint=(0.0, 0.0, 1.0))
        gap = nearest_clearance(patch, surface)
        if abs(gap - clearance) < 0.05:
            break
        offset += clearance - gap
    lateral = geo.unit(np.cross(axis, np.array([0.0, 0.0, 1.0])))
    if lateral[0] < 0.0:                      # +lateral always points to the drawer's right
        lateral = -lateral
    normal = geo.unit(np.cross(lateral, axis))
    return patch, {"station": end_station, "axis": axis, "lateral": lateral,
                   "normal": normal, "radius": r_end, "reach": reach}
