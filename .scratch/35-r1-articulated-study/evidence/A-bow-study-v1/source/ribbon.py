"""One continuous ribbon strip: spine + width/roll/depth fields + depth-resolved output.

The object is a single strip of cloth.  Everything this module emits is derived from
three things and nothing else:

  * a *route* - an ordered list of generated segments (runs and 180-degree turns), each
    specified by lengths, angles and radii, never by plotted coordinates;
  * three *fields* sampled along the strip's own parameter s - half-width, depth and roll;
  * surface marks authored in the strip's own (u, v).

Visibility is computed, never authored.  Triangles are rasterised into a depth buffer and
every emitted stroke is tested against it, so a rear edge disappears where a nearer part of
the same ribbon covers it.  The fill of a triangle comes from that triangle's own projected
winding: a face turned away from the camera wears the ribbon's back colour.

No reference image is read anywhere in this library; the reference only seeded the
parameters in `parts/bow.py`.
"""
from __future__ import annotations

import math

import numpy as np

TAU = math.tau


# --------------------------------------------------------------------------- fields


class Field:
    """A piecewise-smooth scalar field of the strip parameter u in [0, 1].

    Cosine interpolation between knots: C1-continuous, no overshoot, deterministic.
    """

    def __init__(self, knots):
        self.knots = sorted((float(u), float(v)) for u, v in knots)
        if self.knots[0][0] > 0.0 or self.knots[-1][0] < 1.0:
            raise ValueError("a field must cover the whole strip: knots at u=0 and u=1")

    def __call__(self, u):
        ks = self.knots
        if u <= ks[0][0]:
            return ks[0][1]
        if u >= ks[-1][0]:
            return ks[-1][1]
        for (u0, v0), (u1, v1) in zip(ks, ks[1:]):
            if u0 <= u <= u1:
                f = 0.0 if u1 == u0 else (u - u0) / (u1 - u0)
                w = 0.5 - 0.5 * math.cos(math.pi * f)
                return v0 + (v1 - v0) * w
        return ks[-1][1]


# --------------------------------------------------------------------------- route


class Route:
    """The spine, built by walking segments forward from one starting point.

    A `run` is a cubic curve from the cursor to a target with named exit/entry tangents; a
    `turn` is a 180-degree turn whose exit is displaced `2*b` sideways and whose tangents
    continue the previous direction on both sides.  So a route carries exactly one
    hand-typed position (the first point) and every other point is generated.
    """

    def __init__(self, start):
        self.p = np.array(start, dtype=float)
        self.dir = np.array([1.0, 0.0])
        self.parts = []  # list of (kind, points2d, lengths)

    def _push(self, kind, pts):
        self.parts.append((kind, pts))
        seg = np.diff(pts, axis=0)
        self.dir = seg[-1] / np.linalg.norm(seg[-1])
        self.p = pts[-1].copy()

    def _dir_at(self, deg):
        return np.array([math.cos(math.radians(deg)), math.sin(math.radians(deg))])

    def run(self, length=None, end_deg=0.0, out_deg=None, bend=0.0, end=None):
        """Cubic run.  `end` overrides the generated endpoint (used to exit the frame)."""
        a = self.p.copy()
        d0 = self._dir_at(out_deg) if out_deg is not None else self.dir.copy()
        if end is None:
            b = a + length * self._dir_at(end_deg)
        else:
            b = np.array(end, dtype=float)
        d1 = self._dir_at(end_deg)
        n0 = np.array([-d0[1], d0[0]])
        c1 = a + 0.42 * np.linalg.norm(b - a) * d0 + bend * n0
        c2 = b - 0.42 * np.linalg.norm(b - a) * d1 + bend * n0
        ts = np.linspace(0.0, 1.0, 90)[:, None]
        pts = ((1 - ts) ** 3) * a + 3 * ((1 - ts) ** 2) * ts * c1 + 3 * (1 - ts) * ts**2 * c2 + ts**3 * b
        self._push("run", pts)

    def turn(self, along, across, sign, end=None):
        """180-degree turn: tangential displacement `along`, sideways `2*across*`."""
        d = self.dir
        n = np.array([-d[1], d[0]]) * sign
        a0 = self.p.copy()
        ts = np.linspace(0.0, 1.0, 90)
        phi = math.pi * ts
        pts = a0 + np.outer(np.sin(phi) * along, d) + np.outer((1 - np.cos(phi)) * across, n)
        self._push("turn", pts)

    def polyline(self):
        return np.vstack([p for _, p in self.parts])


def resample(poly, n):
    """Resample a 2D polyline to n+1 stations equally spaced by arc length."""
    d = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(d)])
    total = cum[-1]
    want = np.linspace(0.0, total, n + 1)
    x = np.interp(want, cum, poly[:, 0])
    y = np.interp(want, cum, poly[:, 1])
    return np.stack([x, y], axis=1)


# --------------------------------------------------------------------------- strip


class Strip:
    """Stations along the spine with a width field, a depth field and a roll field."""

    def __init__(self, spine2d, halfwidth: Field, depth: Field, roll: Field):
        n = len(spine2d) - 1
        s = np.linspace(0.0, 1.0, n + 1)
        tang = np.gradient(spine2d, axis=0)
        self.u = s
        self.p = np.zeros((n + 1, 3))
        self.p[:, :2] = spine2d
        self.p[:, 2] = np.array([depth(u) for u in s])
        self.h = np.array([halfwidth(u) for u in s])
        self.roll = np.radians(np.array([roll(u) for u in s]))
        t2 = tang / np.linalg.norm(tang, axis=1)[:, None]
        self.t = np.zeros((n + 1, 3))
        self.t[:, :2] = t2
        self.t[:, 2] = 0.0
        a0 = np.stack([t2[:, 1], -t2[:, 0], np.zeros_like(t2[:, 0])], axis=1)
        n0 = np.cross(self.t, a0)
        cr, sr = np.cos(self.roll)[:, None], np.sin(self.roll)[:, None]
        self.a = cr * a0 + sr * n0

    # surface map: (u index, v in [-1, 1]) -> world point
    def point(self, i, v):
        return self.p[i] + self.h[i] * v * self.a[i]

    def sample(self, u, v):
        """World point at continuous (u, v) - used for marks authored on the surface."""
        f = min(max(u, 0.0), 1.0) * (len(self.u) - 1)
        i = min(int(f), len(self.u) - 2)
        w = f - i
        pw = (1 - w) * self.point(i, v) + w * self.point(i + 1, v)
        return pw


def triangles(st: Strip):
    """Tessellate the strip into one triangle fan-chain; returns (tris, meta).

    A triangle is (i0v0, i0v1, i1v1) or (i0v0, i1v1, i1v0) in surface parameter space, so
    the emitted geometry carries its own provenance: every triangle knows its (u, v)
    corners as well as its projected coordinates.
    """
    out = []
    for i in range(len(st.u) - 1):
        q = [(i, 1.0), (i, -1.0), (i + 1, -1.0), (i + 1, 1.0)]
        out.append((q[0], q[1], q[2]))
        out.append((q[0], q[2], q[3]))
    return out


def signed_area(p0, p1, p2):
    return 0.5 * ((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1]))


def depth_buffer(st: Strip, tris, width: int, height: int):
    """Rasterise the strip's triangles and keep the nearest depth per pixel.

    Orthographic camera looking down +z; a smaller z is nearer the viewer.
    """
    zbuf = np.full((height, width), np.inf)
    for tri in tris:
        pts = np.array([st.point(i, v) for i, v in tri])
        x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
        x0, x1 = int(max(0, math.floor(x.min()))), int(min(width - 1, math.ceil(x.max())))
        y0, y1 = int(max(0, math.floor(y.min()))), int(min(height - 1, math.ceil(y.max())))
        if x1 < x0 or y1 < y0:
            continue
        det = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(det) < 1e-9:
            continue
        ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        px, py = xs + 0.5, ys + 0.5
        l0 = ((y[1] - y[2]) * (px - x[2]) + (x[2] - x[1]) * (py - y[2])) / det
        l1 = ((y[2] - y[0]) * (px - x[2]) + (x[0] - x[2]) * (py - y[2])) / det
        l2 = 1.0 - l0 - l1
        inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
        zz = l0 * z[0] + l1 * z[1] + l2 * z[2]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        np.minimum(sub, np.where(inside, zz, np.inf), out=sub)
    return zbuf


def visible_runs(points3d, zbuf, eps):
    """Split a 3D polyline into the runs the depth test leaves visible.

    Returns [(i0, i1), ...] index ranges into the input.
    """
    h, w = zbuf.shape
    ok = []
    for p in points3d:
        x, y, z = int(math.floor(p[0])), int(math.floor(p[1])), p[2]
        if 0 <= x < w and 0 <= y < h:
            ok.append(z <= zbuf[y, x] + eps)
        else:
            ok.append(False)
    runs, start = [], None
    for i, v in enumerate(ok):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - 1 > start:
                runs.append((start, i - 1))
            start = None
    if start is not None and len(ok) - 1 > start:
        runs.append((start, len(ok) - 1))
    return runs
