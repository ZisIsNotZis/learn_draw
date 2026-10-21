"""Shared measurements for the B study's tests: everything is measured on emitted geometry.

The point of these helpers is that no test reads back a number the producer wrote.  A digit's
width, the gap between two digits, the rim's band and the direction each digit approaches the
dish are all re-derived here from the mesh that gets emitted, or from the SVG that gets
delivered.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
SOURCE = os.path.join(EVIDENCE, "source")
if SOURCE not in sys.path:
    sys.path.insert(0, SOURCE)

import geo  # noqa: E402
import scene  # noqa: E402

DIGITS = ("index", "middle", "ring", "little", "thumb")


def ring_screen(patch):
    """Every mesh vertex projected: (stations, angles, 3) = (x, y, depth)."""
    return geo.project(patch.v)


def width_at(patch, i):
    """A digit's width at station i, measured on that station's own ring of vertices."""
    ring = ring_screen(patch)[i][:, :2]
    centre = ring.mean(axis=0)
    return 2.0 * float(np.hypot(*(ring - centre).T).max())


def station_gap(pa, ia, pb, ib):
    """Smallest screen distance between two digits' station rings."""
    a = ring_screen(pa)[ia][:, :2]
    b = ring_screen(pb)[ib][:, :2]
    d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    return float(d.min())


def stations(patch, count):
    return [int(round(t * (patch.ni - 1))) for t in count]


def parts():
    out, rings = scene.parts()
    return dict(out), rings


def fold_rows(patch, sharp_deg=55.0):
    """Profile rows where the emitted surface folds, found here rather than by the producer.

    Neighbouring rows are grouped (one fold can span two quad rows) and each group is reduced
    to its sharpest row, so the result is a short list of the dish's real edges with no index
    borrowed from `dish.profile()`.
    """
    v = patch.v
    raw = []
    for j in range(1, patch.nj - 1):
        a = v[0, j] - v[0, j - 1]
        b = v[0, j + 1] - v[0, j]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-9 or nb < 1e-9:
            continue
        deg = float(np.degrees(np.arccos(min(1.0, max(-1.0, float(a @ b) / (na * nb))))))
        if deg > sharp_deg:
            raw.append((j, deg))
    groups = []
    for row in raw:
        if groups and row[0] - groups[-1][-1][0] <= 1:
            groups[-1].append(row)
        else:
            groups.append([row])
    return [max(g, key=lambda r: r[1]) for g in groups]


def rim_band(dish_patch):
    """The rim's top band: its plane, its two radii, and the ring the fingers lean on.

    Derived from the mesh alone - the two folds highest on the dish - so a change to the dish's
    profile moves this measurement with it instead of silently disagreeing.
    """
    folds = fold_rows(dish_patch)
    if len(folds) < 2:
        raise AssertionError(f"the dish shows {len(folds)} folds; its rim needs two")
    axis = dish_patch.v[:, 0, :2].mean(axis=0)
    top = sorted(folds, key=lambda f: -dish_patch.v[0, f[0], 2])[:2]
    rows = sorted((f[0] for f in top))
    radii = [float(np.linalg.norm(dish_patch.v[0, r, :2] - axis)) for r in rows]
    points = np.vstack([dish_patch.v[:, r] for r in rows])
    centre = points.mean(axis=0)
    # plane through the band: the normal that the band's own points vary least along
    _u, _s, vt = np.linalg.svd(points - centre)
    normal = vt[-1]
    if normal[2] < 0:
        normal = -normal
    return {"rows": rows, "radii": sorted(radii), "normal": normal, "centre": centre,
            "points": points}


CAP_STATIONS = 7      # the rounded end of a digit: how many rings `digits.tube` adds


def tip_station(patch):
    """The last cross-section of a digit before its rounded end cap."""
    return patch.ni - 1 - CAP_STATIONS


def signed_heights(vertices, band):
    """Signed distances of vertices from the rim band's own plane."""
    return (np.asarray(vertices, float) - band["centre"]) @ band["normal"]


def tip_heights(patch, band):
    """How far a digit's tip - its last real cross-section - sits from the rim's band plane.

    The minimum is the digit's closest approach, i.e. its contact clearance; a negative minimum
    would be the digit sunk into the rim.  Only the tip ring is measured: the digit's shaft
    legitimately passes below the rim's plane outside the rim's outer edge, and averaging that
    in would hide the contact the drawing claims.
    """
    ring = patch.v[tip_station(patch)]
    return signed_heights(ring, band)
