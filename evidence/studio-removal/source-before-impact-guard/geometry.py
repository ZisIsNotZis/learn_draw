"""A small gesture produces a tapered lock; local pushes preserve its terminals.

The legacy hair-mass offsets sparse spine stations and asks for each width. Here a
continuous width field supplies a usable initial silhouette and an editable edge.
Depth clipping is deliberately delegated to the existing vector visibility engine.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import html


def xml_comment(text):
    """Free author text and names remain valid XML comment bodies."""
    return '<!-- '+html.escape(str(text)).replace('--','—')+' -->'


def path(points,closed=True):
    """Serialize compiled coordinates; paths are never the authoring interface."""
    return 'M '+' L '.join(f'{x:.4f},{y:.4f}' for x,y in points)+(' Z' if closed else '')


@dataclass(frozen=True)
class Row:
    t: float
    left: tuple[float, float]
    right: tuple[float, float]
    spine: tuple[float, float]


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def window(t, center, radius):
    """Compact C1 influence: no movement beyond the selected arc interval."""
    d = abs(t - center) / radius
    return 0.5 + 0.5 * math.cos(math.pi * d) if d < 1 else 0.0


def resolve_root(node, canvas):
    # Sparse semantic canvas anchors seed composition; generated contours never
    # become author inputs. Object attachment is not claimed by this first slice.
    anchors = {"upper_center": (.5, .12), "center": (.5, .5),
               "upper_left": (.25, .12), "upper_right": (.75, .12)}
    placement = node.get("at", {})
    a = anchors[placement.get("anchor", "upper_center")]
    offset = placement.get("offset", [0, 0])
    return ((a[0] + offset[0]) * canvas[0], (a[1] + offset[1]) * canvas[1])


def lock_rows(node, canvas, samples=40):
    """Sweep a full-width field along a smooth gesture, in screen coordinates.

    Root width is modest, the upper-middle swells, the tip converges. These are
    style defaults, not measurements copied from a reference. Optional edits move
    boundary points in screen directions; tonal regions interpolate the new edges.
    """
    length = node.get("length", .68) * min(canvas)
    width = node.get("width", .19) * length
    sweep = node.get("sweep", .16)
    angle = math.radians(node.get("angle", -8))
    root = resolve_root(node, canvas)

    def center(t):
        # Gesture sweep is independent of thickness: widening a lock must not
        # silently move its spine or its protected one-sided boundary.
        u = length * sweep * math.sin(math.pi * t)
        v = length * t
        return (root[0] + u * math.cos(angle) + v * math.sin(angle),
                root[1] - u * math.sin(angle) + v * math.cos(angle))

    rows = []
    for i in range(samples + 1):
        t = i / samples
        c = center(t)
        a, b = center(max(0, t - 1e-4)), center(min(1, t + 1e-4))
        dx, dy = b[0] - a[0], b[1] - a[1]
        norm = math.hypot(dx, dy)
        n = (-dy / norm, dx / norm)
        # A head-attached clump emerges at a narrow root, swells, then tapers.
        half = width * .5 * (.34 * (1 - t) ** 2 +
                              1.35 * math.sin(math.pi * t) ** .8 * (1 - t) ** .5)
        edges = {"left": (c[0] + n[0] * half, c[1] + n[1] * half),
                 "right": (c[0] - n[0] * half, c[1] - n[1] * half)}
        if node.get("width_side", "both") == "right":
            edges = {"left": c, "right": (c[0] - n[0] * half * 2, c[1] - n[1] * half * 2)}
        elif node.get("width_side", "both") == "left":
            edges = {"left": (c[0] + n[0] * half * 2, c[1] + n[1] * half * 2), "right": c}
        for edit in node.get("edits", []):
            weight = window(t, edit["at"], edit["radius"])
            p = edges[edit["side"]]
            edges[edit["side"]] = (p[0] + edit["dx"] * width * weight,
                                    p[1] + edit["dy"] * width * weight)
        rows.append(Row(t, edges["left"], edges["right"], c))
    return rows


def outline(rows):
    # One shared tip, plus a curved root cap generated from the first section.
    left, right = rows[0].left, rows[0].right
    c = mix(left, right, .5)
    # One-sided widening moves the section midpoint. That is NOT the gesture
    # tangent: using it rotates the cap when only thickness changes.
    dx = rows[1].spine[0] - rows[0].spine[0]
    dy = rows[1].spine[1] - rows[0].spine[1]
    length = math.hypot(dx, dy)
    radius = math.dist(left, right) / 2
    cap = []
    for i in range(1, 10):
        th = math.pi * i / 10
        p = mix(right, left, (1 - math.cos(th)) / 2)
        cap.append((p[0] - dx / length * radius * math.sin(th) * .65,
                    p[1] - dy / length * radius * math.sin(th) * .65))
    raw = [r.left for r in rows] + [r.right for r in reversed(rows[:-1])] + cap
    clean = [raw[0]]
    for p in raw[1:]:
        if math.dist(p, clean[-1]) > 1e-8:
            clean.append(p)
    if math.dist(clean[0], clean[-1]) <= 1e-8:
        clean.pop()
    return clean


def bounds(points):
    return [min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points)]


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def geometry_issues(rows):
    """Reject crossed sections and nonadjacent contour intersections, not taste."""
    problems = []
    for i, r in enumerate(rows[:-1]):
        a, b = rows[max(0, i - 1)], rows[min(len(rows) - 1, i + 1)]
        tangent = (b.left[0] + b.right[0] - a.left[0] - a.right[0],
                   b.left[1] + b.right[1] - a.left[1] - a.right[1])
        w = (r.right[0] - r.left[0], r.right[1] - r.left[1])
        if tangent[0] * w[1] - tangent[1] * w[0] >= -1e-8:
            problems.append(f"section crossed or collapsed near t={r.t:.3f}")
    poly = outline(rows)
    from shapely import Polygon, is_valid_reason
    ring = Polygon(poly)
    if not ring.is_valid:
        problems.append("contour self-intersection/invalidity: " + is_valid_reason(ring))
    return problems
