"""dish.py - a shallow dish as a surface of revolution, and the rings its own mesh derives.

The dish is one authored profile - a shallow elliptical bowl inside, a flat rim band, a curved
outer wall and an underside - revolved once.  Nothing about its shape is a traced coordinate,
and nothing here is drawn.

`derived_rings` finds the dish's real edges again by looking at the mesh: the rim's two corners
are the profile rows where the surface turns sharply, the foot is the lowest ring, the outer
wall's intermediate rings are interpolated between the foot and the rim's outer corner.  The
hand is hung off those rings, so neither module owns a shared constant that could drift.

Profile order matters.  It runs from the underside's axis outward under the dish, up the wall,
inward across the rim's top, then down the bowl's interior to the axis again.  With the
revolution index i running counter-clockwise and the profile index j running in that order, the
outward normal of every quad is `cross(d_i, d_j)` - the convention `geo.Patch` requires.
"""
from __future__ import annotations

import math

import numpy as np

import geo

# The dish's authored size, in px, in its own frame.  Four numbers and one rim thickness.
RIM_OUTER = 310.0
RIM_INNER = 265.0
RIM_Z = 8.0
FOOT_RADIUS = 155.0
FOOT_Z = -95.0
AXIS_UNDER_Z = -80.0
BOWL_DEPTH = 92.0           # rim plane to the bowl's floor

ANGLES = 60
SHARP_DEG = 30.0
UNDER_FRACTIONS = (0.30, 0.55, 0.80)   # rows across the underside, axis -> foot


def _arc(cr, cz, a, b, t0, t1, n, endpoint=True):
    """`n` samples of the arc, spanning [t0, t1] - or [t0, t1) when the next span repeats t1."""
    ts = np.linspace(t0, t1, n if endpoint else n + 1)
    if not endpoint:
        ts = ts[:-1]
    return np.stack([cr + a * np.cos(ts), cz + b * np.sin(ts)], axis=1)


def profile():
    """(radius, height) along the dish, from the underside's axis round to the floor's axis."""
    under = _arc(FOOT_RADIUS, AXIS_UNDER_Z, FOOT_RADIUS, FOOT_Z - AXIS_UNDER_Z,
                 math.pi, math.pi / 2.0, 6, endpoint=False)
    wall = _arc(FOOT_RADIUS, RIM_Z, RIM_OUTER - FOOT_RADIUS, FOOT_Z - RIM_Z,
                math.pi / 2.0, 0.0, 15, endpoint=False)
    rim = np.stack([np.linspace(RIM_OUTER, RIM_INNER, 4)[:-1],
                    np.full(3, RIM_Z)], axis=1)
    bowl = _arc(0.0, RIM_Z, RIM_INNER, -BOWL_DEPTH, 0.0, math.pi / 2.0, 33, endpoint=True)
    return np.vstack([under, wall, rim, bowl])


def build(*, tilt_deg=12.0, offset=(0.0, 0.0, 0.0), lift=0.0):
    """Revolve the profile into a world-space mesh, then tip it towards the viewer."""
    prof = profile()
    theta = np.linspace(0.0, 2.0 * np.pi, ANGLES, endpoint=False)
    r, z = prof[:, 0], prof[:, 1]
    local = np.stack([np.outer(np.cos(theta), r),
                      np.outer(np.sin(theta), r),
                      np.tile(z, (ANGLES, 1))], axis=-1)
    world = geo.apply(local.reshape(-1, 3), geo.rot_x(tilt_deg)).reshape(ANGLES, -1, 3)
    return geo.Patch("dish", world + np.asarray(offset, float) + np.array([0.0, 0.0, lift]),
                     closed_i=True, closed_j=False)


def _axis_xy(patch):
    """The dish's own axis in the xy plane: the centre of any one of its rings, read off the mesh."""
    return patch.v[:, 0, :2].mean(axis=0)


def _sharp_rows(patch):
    """Profile rows where the emitted surface turns by more than SHARP_DEG, with their radii."""
    v = patch.v
    axis = _axis_xy(patch)
    rows = []
    for j in range(1, patch.nj - 1):
        a = v[0, j] - v[0, j - 1]
        b = v[0, j + 1] - v[0, j]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na < 1e-9 or nb < 1e-9:
            continue
        deg = math.degrees(math.acos(min(1.0, max(-1.0, float(a @ b) / (na * nb)))))
        if deg > SHARP_DEG:
            rows.append((j, float(np.linalg.norm(v[0, j, :2] - axis)), deg))
    return rows


def derived_rings(patch):
    """The rings the emitted dish actually has, named by geometry rather than by index.

    Sharp rows are grouped into runs of neighbouring rows (one fold may span two quad rows),
    then the two folds nearest the top of the dish are its rim: the wider of them is the rim's
    outer edge, the narrower its inner edge.  The foot is simply the lowest ring.  Nothing here
    is an index into `profile()`, so moving the profile cannot silently move the hand.
    """
    normals = patch.vertex_normals()
    v = patch.v
    axis = _axis_xy(patch)
    sharp = _sharp_rows(patch)
    if len(sharp) < 2:
        raise ValueError(f"the dish's mesh has {len(sharp)} sharp profile rows, expected >= 2")
    groups = []
    for row in sharp:
        if groups and row[0] - groups[-1][-1][0] <= 1:
            groups[-1].append(row)
        else:
            groups.append([row])
    folds = [max(g, key=lambda r: r[2]) for g in groups]        # one representative per fold
    top = [f for f in folds if f[1] > 0.6 * max(r[1] for r in folds)]
    if len(top) < 2:
        raise ValueError(f"the dish's rim produced {len(top)} folds, expected 2")
    rim_outer_row, rim_inner_row = sorted((top[0], top[1]), key=lambda r: -r[1])[0][0], \
        sorted((top[0], top[1]), key=lambda r: -r[1])[1][0]
    foot_row = int(np.argmin(v[0, :rim_outer_row, 2]))    # the lowest ring of the outside
    if not (foot_row < rim_outer_row < rim_inner_row):
        raise ValueError("the dish's derived rings are out of profile order: "
                         f"foot {foot_row}, rim outer {rim_outer_row}, rim inner {rim_inner_row}")

    def ring(j):
        pts = v[:, j]
        return {"row": j,
                "radius": float(np.linalg.norm(pts[0, :2] - axis)),
                "z": float(pts[0, 2]),
                "points": pts,
                "normals": normals[:, j]}

    by_row = {row: deg for row, _radius, deg in sharp}
    out = {
        "rim_outer": dict(ring(rim_outer_row), sharp_deg=by_row[rim_outer_row]),
        "axis": ring(0),
        "under": {frac: ring(int(round(foot_row * frac))) for frac in UNDER_FRACTIONS},
        "rim_inner": dict(ring(rim_inner_row), sharp_deg=by_row[rim_inner_row]),
        "foot": ring(foot_row),
        "wall": {},
        "bowl": {},
        "interior_row": rim_inner_row + 1,
    }
    for frac in (0.35, 0.72):
        row = int(round(foot_row + (rim_outer_row - foot_row) * frac))
        out["wall"][frac] = ring(row)
    # The bowl's interior, from the rim's inner corner down toward the floor.  README H1: a
    # joint is a declared front/rear pair, so the surface a digit presses has to be derivable
    # from the same mesh the underside is: the interior is the face above the rim plane.
    for frac in (0.30, 0.65):
        row = int(round(rim_inner_row + (patch.nj - 1 - rim_inner_row) * frac))
        out["bowl"][frac] = ring(row)
    return out


def material_split(patch, rings):
    """Material index per quad: everything past the rim's inner corner is the dish's interior."""
    inside_from = rings["rim_inner"]["row"]
    mat = np.ones((patch.ni, patch.nj - 1), dtype=int)      # the outside of the vessel
    mat[:, max(0, inside_from):] = 2                        # everything past the rim is inside
    return mat
