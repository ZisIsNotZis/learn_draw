"""digits.py - one primitive for a hand: a tapered tube swept along a derived centreline.

A digit, a thumb and the palm are the same primitive and differ only in their numbers: a
centreline through a few knots, a radius law along it, and an optional flattening of the
cross-section.  Nothing is traced, and no part carries more than four knots.

The knots are not typed coordinates: `contact.py` obtains them from the dish's own derived
rings, so the hand is *made out of* the dish rather than drawn next to it.

Cross-section convention (which the patch's normal convention requires): with `w` the
transported normal, `q = t x w`, the surface point at angle `phi` is

    C + a*cos(phi)*w - b*sin(phi)*q

so the circumferential direction at phi = 0 is -q and the quad normal cross(d_i, d_j) comes
out along +w, i.e. outward.  `geo.Patch.front_fraction` is the check.
"""
from __future__ import annotations

import numpy as np

import geo


def spline(knots, samples):
    """Centripetal Catmull-Rom through the knots, resampled uniformly by arc length."""
    p = np.asarray(knots, dtype=float)
    if len(p) < 2:
        raise ValueError("a centreline needs at least two knots")
    ext = np.vstack([p[0] + (p[0] - p[1]), p, p[-1] + (p[-1] - p[-2])])
    dense = []
    for k in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[k - 1], ext[k], ext[k + 1], ext[k + 2]
        for t in np.linspace(0.0, 1.0, 24, endpoint=False):
            t2, t3 = t * t, t * t * t
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t
                                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    dense.append(p[-1])
    dense = np.array(dense)
    d = np.linalg.norm(np.diff(dense, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(d)])
    want = np.linspace(0.0, cum[-1], samples)
    return np.stack([np.interp(want, cum, dense[:, k]) for k in range(3)], axis=1)


def law(knots):
    """Radius along the tube as a smoothstep between (t, radius) knots."""
    ks = sorted((float(t), float(r)) for t, r in knots)
    if ks[0][0] > 0.0 or ks[-1][0] < 1.0:
        raise ValueError("a radius law must cover t = 0 .. 1")

    def at(t):
        t = min(max(t, 0.0), 1.0)
        for (t0, r0), (t1, r1) in zip(ks, ks[1:]):
            if t0 <= t <= t1:
                span = t1 - t0
                f = 0.0 if span <= 1e-12 else (t - t0) / span
                return r0 + (r1 - r0) * (f * f * (3.0 - 2.0 * f))
        return ks[-1][1]

    return at


def _frames(centres, up_hint):
    """Tangents and a parallel-transported normal, so the cross-section never spins."""
    t = geo.unit(np.gradient(centres, axis=0))
    w = np.zeros_like(t)
    hint = np.asarray(up_hint, float)
    w[0] = geo.unit(hint - t[0] * float(hint @ t[0]))
    for i in range(1, len(t)):
        a, b = t[i - 1], t[i]
        axis = np.cross(a, b)
        s = np.linalg.norm(axis)
        if s < 1e-9:
            w[i] = w[i - 1] - t[i] * float(w[i - 1] @ t[i])
            continue
        axis = axis / s
        ang = np.arccos(min(1.0, max(-1.0, float(a @ b))))
        v = w[i - 1]
        w[i] = v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * float(axis @ v) * (1 - np.cos(ang))
    return t, geo.unit(w)


CAP_U = (0.0, 0.25, 0.45, 0.62, 0.76, 0.87, 0.95, 1.0)


def tube(name, knots, radius, *, samples=22, angles=20, thin=1.0, up_hint=(0.0, 0.0, 1.0),
         cap_start=True, cap_end=True):
    """Sweep a (optionally flattened) circular cross-section along the knots.

    `radius` is a law function t -> radius.  `thin` scales the depth-half-axis of the
    cross-section along the transported normal, which is what makes the palm a palm and a
    digit a pad rather than a rope.
    """
    centres = spline(knots, samples)
    t, w = _frames(centres, up_hint)
    q = np.cross(t, w)

    stations, radii, tangents, normals, quats = [], [], [], [], []
    t0, r0 = t[0], radius(0.0)
    if cap_start:
        for u in reversed(CAP_U[1:]):
            stations.append(centres[0] - t0 * (r0 * u))
            radii.append(r0 * np.sqrt(max(0.0, 1.0 - u * u)))
            tangents.append(t0)
            normals.append(w[0])
            quats.append(q[0])
    for i in range(len(centres)):
        stations.append(centres[i])
        radii.append(radius(i / (len(centres) - 1)))
        tangents.append(t[i])
        normals.append(w[i])
        quats.append(q[i])
    t1, r1 = t[-1], radius(1.0)
    if cap_end:
        for u in CAP_U[1:]:
            stations.append(centres[-1] + t1 * (r1 * u))
            radii.append(r1 * np.sqrt(max(0.0, 1.0 - u * u)))
            tangents.append(t1)
            normals.append(w[-1])
            quats.append(q[-1])

    stations = np.array(stations)
    radii = np.array(radii)
    phi = np.linspace(0.0, 2.0 * np.pi, angles, endpoint=False)
    cos, sin = np.cos(phi), np.sin(phi)
    verts = (stations[:, None, :]
             + (radii * thin)[:, None, None] * cos[None, :, None] * np.array(normals)[:, None, :]
             - radii[:, None, None] * sin[None, :, None] * np.array(quats)[:, None, :])
    return geo.Patch(name, verts, closed_i=False, closed_j=True)
