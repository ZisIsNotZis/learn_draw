"""Depth-clipped authored marks.

Fill visibility comes from the project engine (`scripts/vector_visibility.py`), which
subtracts triangle against triangle.  An authored line is a curve lying on a
surface, so its own surface's faces are *not* occluders of it, while every surface
in front of it is.  This module therefore samples a mark and hides the samples where
some other triangle covers the point and lies nearer the camera.

Nothing is cut by hand: the marks are authored whole and their painted extent is a
depth result, exactly like the fills.
"""
from __future__ import annotations

import math

import numpy as np

DEPTH_TOLERANCE = 4e-3     # a mark lies on its own surface; only clearly-nearer cloth hides it


class Occluders:
    """Projected triangles of the whole scene, prepared once for repeated queries."""

    def __init__(self, faces):
        triangles = [np.asarray(triangle, dtype=float) for triangle, _fill, _name in faces]
        if not triangles:
            raise ValueError("line visibility needs the scene faces")
        self.a = np.array([t[0] for t in triangles])
        self.b = np.array([t[1] for t in triangles])
        self.c = np.array([t[2] for t in triangles])
        self.names = np.array([name for _triangle, _fill, name in faces])

    def occluded(self, x: float, y: float, z: float) -> bool:
        ax, ay = self.a[:, 0], self.a[:, 1]
        bx, by = self.b[:, 0], self.b[:, 1]
        cx, cy = self.c[:, 0], self.c[:, 1]
        det = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        safe = np.abs(det) > 1e-12
        if not safe.any():
            return False
        det = np.where(safe, det, 1.0)
        l1 = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / det
        l2 = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / det
        l3 = 1.0 - l1 - l2
        inside = safe & (l1 >= -1e-9) & (l2 >= -1e-9) & (l3 >= -1e-9)
        if not inside.any():
            return False
        depth = l1 * self.a[:, 2] + l2 * self.b[:, 2] + l3 * self.c[:, 2]
        return bool((inside & (depth > z + DEPTH_TOLERANCE)).any())


def visible_runs(points, occluders: Occluders):
    """Return runs of visible sample indices for a 3D polyline."""
    flags = [not occluders.occluded(*p) for p in points]
    runs = []
    start = None
    for index, flag in enumerate(flags):
        if flag and start is None:
            start = index
        if not flag and start is not None:
            runs.append((start, index - 1))
            start = None
    if start is not None:
        runs.append((start, len(flags) - 1))
    return tuple(run for run in runs if run[1] > run[0])


def densify(points, step: float = 1.5):
    """Resample a polyline so a visibility run is finer than one cloth crease."""
    out = []
    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        count = max(1, int(length / step))
        for i in range(count):
            f = i / count
            out.append(tuple(a[k] + (b[k] - a[k]) * f for k in range(3)))
    out.append(points[-1])
    return tuple(out)


def visible_runs_of_mark(points, occluders: Occluders):
    return visible_runs(densify(points), occluders)
