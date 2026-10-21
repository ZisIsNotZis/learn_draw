"""geo.py - the camera, grid meshes, shading tones, the depth buffer and the silhouettes.

Nothing here reads an image, and nothing here is a drawn line: every curve the drawing
carries is derived from a mesh.

  * a *silhouette* is the zero set of (vertex normal . view direction), extracted from the
    mesh by marching squares over the grid of vertex samples;
  * a *crease* is a mesh edge whose two faces differ by more than `CREASE_DEG`;
  * visibility is a depth buffer: a stroke is emitted only where its own surface is the
    nearest thing at that pixel, so a rear edge is *absent*, not painted over.

World frame: +x right, +y away from the viewer, +z up; the camera looks along
`VIEW = (0, cos, -sin)` with an orthographic tilt of `TILT` above the horizon.
"""
from __future__ import annotations

import math

import numpy as np

CANVAS = (900, 700)
TILT = math.radians(31.0)
S, C = math.sin(TILT), math.cos(TILT)
OX, OY = 0.0, 0.0          # camera offset in px, applied after projection
VIEW = np.array([0.0, C, -S])   # away from the camera
CREASE_DEG = 55.0      # a fold sharper than this is drawn; a smooth cap is not


def project(pts):
    """World (..., 3) -> screen (..., 3) = (canvas x, canvas y, depth); smaller depth is nearer."""
    p = np.asarray(pts, dtype=float)
    sx = p[..., 0] + OX
    sy = -(p[..., 1] * S + p[..., 2] * C) + OY
    dz = p[..., 1] * C - p[..., 2] * S
    return np.stack([sx, sy, dz], axis=-1)


def unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-12)


def rot_x(deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return np.array([[1.0, 0.0, 0.0], [0.0, ca, -sa], [0.0, sa, ca]])


def rot_z(deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return np.array([[ca, -sa, 0.0], [sa, ca, 0.0], [0.0, 0.0, 1.0]])


def apply(pts, mat, offset=(0.0, 0.0, 0.0)):
    return np.asarray(pts, dtype=float) @ np.asarray(mat, dtype=float).T + np.asarray(offset, float)


# --------------------------------------------------------------------------- mesh


class Patch:
    """A grid of world samples: verts[i, j].  One quad per (i, j) cell.

    The quad at (i, j) has corners (i, j), (i+1, j), (i+1, j+1), (i, j+1) with i and j taken
    modulo the grid where the patch wraps.  Its outward normal is cross(d_i, d_j), so a
    builder is responsible for the direction its two parameters run in; `front_fraction()`
    is the check that a closed patch got that right (a closed solid shows half its faces).
    """

    def __init__(self, name, verts, *, closed_i=True, closed_j=False, mat=0):
        self.name = name
        self.v = np.asarray(verts, dtype=float)
        self.ni, self.nj = self.v.shape[:2]
        self.closed_i = closed_i
        self.closed_j = closed_j
        self.mat = mat
        self._quads = None

    # -- topology ---------------------------------------------------------
    def quad_index(self):
        ni, nj = self.ni, self.nj
        ii = np.arange(ni if self.closed_i else ni - 1)
        jj = np.arange(nj if self.closed_j else nj - 1)
        I, J = np.meshgrid(ii, jj, indexing="ij")
        return I, J, (I + 1) % ni, (J + 1) % nj

    def quads(self):
        """(nq, 4, 3) world corners, one row per quad, plus the corner index arrays."""
        if self._quads is None:
            I, J, I1, J1 = self.quad_index()
            corners = np.stack([self.v[I, J], self.v[I1, J],
                                self.v[I1, J1], self.v[I, J1]], axis=2)
            nq = I.size
            self._quads = (corners.reshape(nq, 4, 3), I.reshape(-1), J.reshape(-1),
                           I1.reshape(-1), J1.reshape(-1))
        return self._quads

    def quad_normals(self):
        corners, _I, _J, _I1, _J1 = self.quads()
        di = corners[:, 1] - corners[:, 0]
        dj = corners[:, 3] - corners[:, 0]
        n = np.cross(di, dj)
        area2 = np.linalg.norm(n, axis=1)
        return n, area2

    def quad_mat(self):
        if np.ndim(self.mat) == 0:
            nq = self.quads()[0].shape[0]
            return np.full(nq, int(self.mat), dtype=int)
        return np.asarray(self.mat, dtype=int).reshape(-1)

    # -- shading ----------------------------------------------------------
    def vertex_normals(self):
        """Area-weighted vertex normals, wrapped into the grid."""
        corners, I, J, I1, J1 = self.quads()
        n, _area2 = self.quad_normals()
        acc = np.zeros_like(self.v)
        for k, (ii, jj) in enumerate(((I, J), (I1, J), (I1, J1), (I, J1))):
            np.add.at(acc, (ii, jj), n)
        return unit(acc)

    def front_fraction(self):
        """Fraction of quads whose outward normal faces the camera.  ~0.5 for a closed solid."""
        n, area2 = self.quad_normals()
        ok = area2 > 1e-9
        if not ok.any():
            return 1.0
        front = (n[ok] @ VIEW) < 0.0
        return float(front.mean())

    # -- derived curves ---------------------------------------------------
    def silhouette(self):
        """Zero set of (vertex normal . view), as polylines of screen points + depth.

        Marching squares over the vertex grid of the scalar field s = n_hat . VIEW.  Each
        crossing point is shared by the two cells that meet on that mesh edge, so the
        segments chain exactly instead of being matched by coordinate proximity.
        """
        s = self.vertex_normals() @ VIEW
        scr = project(self.v)
        ni, nj = self.ni, self.nj
        _corners, I, J, I1, J1 = self.quads()
        cache = {}

        def on_edge(kind, a, b):
            """Zero crossing on the mesh edge named canonically by (kind, a, b)."""
            key = (kind, a, b)
            got = cache.get(key)
            if got is not None:
                return got
            if kind == "i":
                va, vb = (a, b), ((a + 1) % ni, b)
            else:
                va, vb = (a, b), (a, (b + 1) % nj)
            sa, sb = s[va], s[vb]
            denom = sa - sb
            t = 0.0 if abs(denom) < 1e-12 else float(sa / denom)
            t = min(max(t, 0.0), 1.0)
            p = scr[va] * (1.0 - t) + scr[vb] * t
            cache[key] = p
            return p

        segs = []
        for i, j, i1, j1 in zip(I.tolist(), J.tolist(), I1.tolist(), J1.tolist()):
            vals = [s[i, j], s[i1, j], s[i1, j1], s[i, j1]]
            inside = [v > 0.0 for v in vals]
            if all(inside) or not any(inside):
                continue
            edges = [("i", i, j), ("j", i1, j), ("i", i, j1), ("j", i, j)]
            pts = []
            for k in range(4):
                if inside[k] != inside[(k + 1) % 4]:
                    pts.append(on_edge(*edges[k]))
            if len(pts) == 2:
                segs.append((pts[0], pts[1]))
            elif len(pts) == 4:
                segs.append((pts[0], pts[1]))
                segs.append((pts[2], pts[3]))
        return _join(segs)

    def creases(self, deg=CREASE_DEG):
        """Mesh edges whose two faces differ by more than `deg`, chained into polylines."""
        n, area2 = self.quad_normals()
        _corners, I, J, _I1, _J1 = self.quads()
        nhat = unit(n)
        lim = math.cos(math.radians(deg))
        scr = project(self.v)
        ni, nj = self.ni, self.nj
        index = {(int(I[k]), int(J[k])): k for k in range(I.shape[0])}
        segs = []
        for k in range(I.shape[0]):
            i, j = int(I[k]), int(J[k])
            if area2[k] < 1.0:      # a sub-pixel quad has no reliable normal: no fold to claim
                continue
            for di, dj in ((1, 0), (0, 1)):
                ni2, nj2 = i + di, j + dj
                if (not self.closed_i and ni2 >= ni) or (not self.closed_j and nj2 >= nj):
                    continue
                k2 = index.get((ni2 % ni, nj2 % nj))
                if k2 is None or area2[k2] < 1.0:
                    continue
                if float(nhat[k] @ nhat[k2]) > lim:
                    continue
                # shared edge, in the same order from both sides
                a = ((i + 1) % ni, j) if di == 1 else (i, (j + 1) % nj)
                b = ((i + 1) % ni, (j + 1) % nj)
                segs.append((scr[a], scr[b]))
        return _join(segs)


def _join(segs):
    """Join 2-point screen segments into polylines, deterministically.

    Endpoints are matched by rounded coordinates: a segment ends where the next begins, and
    a closed ring comes back as one polyline whose ends coincide.
    """
    if not segs:
        return []

    def key(p):
        return (round(float(p[0]), 3), round(float(p[1]), 3))

    at = {}
    for idx, (a, b) in enumerate(segs):
        at.setdefault(key(a), []).append(idx)
        at.setdefault(key(b), []).append(idx)
    used = [False] * len(segs)
    lines = []
    for start in range(len(segs)):
        if used[start]:
            continue
        used[start] = True
        a, b = segs[start]
        line = [np.asarray(a, float), np.asarray(b, float)]
        for forward in (True, False):
            while True:
                tip = key(line[-1] if forward else line[0])
                step = None
                for idx in at.get(tip, ()):
                    if used[idx]:
                        continue
                    pa, pb = segs[idx]
                    if key(pa) == tip:
                        step = (idx, pb)
                    elif key(pb) == tip:
                        step = (idx, pa)
                    if step:
                        break
                if step is None:
                    break
                used[step[0]] = True
                pt = np.asarray(step[1], float)
                if forward:
                    line.append(pt)
                else:
                    line.insert(0, pt)
        lines.append(np.array(line, dtype=float))
    return lines


# --------------------------------------------------------------------------- depth


def depth_buffer(quads_scr, eps_px=0.0):
    """Rasterise front-facing quads into a nearest-depth buffer over the canvas.

    `quads_scr` is a list of (4, 3) arrays of screen points + depth.  Orthographic, so the
    depth is affine across each triangle and interpolates linearly in screen space.
    """
    w, h = CANVAS
    zbuf = np.full((h, w), np.inf)
    for q in quads_scr:
        for tri in ((0, 1, 2), (0, 2, 3)):
            p = q[list(tri)]
            _raster(zbuf, p[:, :2], p[:, 2])
    return zbuf


def _raster(zbuf, p, z):
    h, w = zbuf.shape
    x0 = max(0, int(math.floor(p[:, 0].min())))
    x1 = min(w - 1, int(math.ceil(p[:, 0].max())))
    y0 = max(0, int(math.floor(p[:, 1].min())))
    y1 = min(h - 1, int(math.ceil(p[:, 1].max())))
    if x1 < x0 or y1 < y0:
        return
    det = (p[1, 1] - p[2, 1]) * (p[0, 0] - p[2, 0]) + (p[2, 0] - p[1, 0]) * (p[0, 1] - p[2, 1])
    if abs(det) < 1e-9:
        return
    ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    px, py = xs + 0.5, ys + 0.5
    l0 = ((p[1, 1] - p[2, 1]) * (px - p[2, 0]) + (p[2, 0] - p[1, 0]) * (py - p[2, 1])) / det
    l1 = ((p[2, 1] - p[0, 1]) * (px - p[2, 0]) + (p[0, 0] - p[2, 0]) * (py - p[2, 1])) / det
    l2 = 1.0 - l0 - l1
    inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
    if not inside.any():
        return
    zz = l0 * z[0] + l1 * z[1] + l2 * z[2]
    sub = zbuf[y0:y1 + 1, x0:x1 + 1]
    np.minimum(sub, np.where(inside, zz, np.inf), out=sub)


def visible_runs(points3d_scr, zbuf, eps):
    """Index ranges of a screen polyline whose own surface is the nearest thing there."""
    h, w = zbuf.shape
    ok = []
    for p in points3d_scr:
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


# --------------------------------------------------------------------------- colour

AMBIENT = 0.30
LIGHT = unit(np.array([-0.42, -0.78, 0.55]))
TONES = 0        # 0 = continuous shading; a shade is passed straight through
TONE_SCALE = tuple(0.56 + 0.50 * (k / 27.0) for k in range(28))   # used when TONES > 0


def tone(shade):
    s = min(max(shade, 0.0), 1.0)
    return int(round((TONES - 1) * s))


def shaded(base, shade):
    """The base colour at a shade.  `TONES = 0` keeps the shade continuous; a positive TONES
    quantises it into flat cel steps."""
    s = min(max(shade, 0.0), 1.0)
    k = s if TONES == 0 else TONE_SCALE[tone(s)]
    r, g, b = base
    return "#%02x%02x%02x" % tuple(min(255, int(round(min(255.0, c * k)))) for c in (r, g, b))


def hexc(rgb):
    return "#%02x%02x%02x" % tuple(min(255, int(round(c))) for c in rgb)


def fmt_pt(p):
    def one(v):
        return 0.0 if abs(v) < 0.005 else v
    return f"{one(p[0]):.2f},{one(p[1]):.2f}"
