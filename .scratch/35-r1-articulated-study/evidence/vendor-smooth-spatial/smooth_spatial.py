"""Bounded spatial transfer of vendor R.smooth's Catmull-Rom-to-cubic rule.

Only four sparse semantic cloth landmarks are authored. Their same semantic input is rendered as a
raw polygon and as a generated closed cubic contour; both pass through the existing support/world,
camera, triangulation, depth-fill and semantic-line-visibility interfaces. This is not R1 artwork.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path

from scripts.articulated_construction import Camera, Component, Point, SupportFrame, component_faces
from scripts.articulated_line_visibility import transform_compound_path, visible_segment_spans
from scripts.vector_visibility import visible_fragments, visible_regions

# Four semantic local landmarks only; these are original design inputs, not sampled reference points.
SEMANTIC_CONTROLS = (
    ("neckline", Point(0.0, 0.0)),
    ("shoulder", Point(3.0, 0.35)),
    ("hem", Point(2.15, 3.65)),
    ("side", Point(-0.72, 2.75)),
)

# This foreground sheet is a separate named component, also specified by four authored corners.
OCCLUDER_CORNERS = (
    Point(-1.15, 0.95), Point(1.45, 0.95),
    Point(1.45, 2.95), Point(-1.15, 2.95),
)


@dataclass(frozen=True)
class CubicSegment:
    start: Point
    control1: Point
    control2: Point
    end: Point


def _finite_point(point: Point) -> bool:
    return math.isfinite(point.u) and math.isfinite(point.v)


def cubic_segments(points: tuple[Point, ...], k: float = 0.5) -> tuple[CubicSegment, ...]:
    """Closed Catmull-Rom-to-cubic rule from R.smooth; wrapping closes the seam."""
    if len(points) < 3 or not math.isfinite(k):
        raise ValueError("closed curve needs at least three points and finite tension")
    if any(not _finite_point(point) for point in points):
        raise ValueError("curve controls must be finite")
    count = len(points)
    segments = []
    for index, p1 in enumerate(points):
        p0, p2, p3 = (points[(index - 1) % count], points[(index + 1) % count],
                      points[(index + 2) % count])
        c1 = Point(p1.u + (p2.u - p0.u) * k / 3,
                   p1.v + (p2.v - p0.v) * k / 3)
        c2 = Point(p2.u - (p3.u - p1.u) * k / 3,
                   p2.v - (p3.v - p1.v) * k / 3)
        segments.append(CubicSegment(p1, c1, c2, p2))
    return tuple(segments)


def evaluate(segment: CubicSegment, t: float) -> Point:
    """Evaluate one cubic Bezier segment at t in [0,1]."""
    s = 1 - t
    return Point(s**3 * segment.start.u + 3*s*s*t * segment.control1.u
                 + 3*s*t*t * segment.control2.u + t**3 * segment.end.u,
                 s**3 * segment.start.v + 3*s*s*t * segment.control1.v
                 + 3*s*t*t * segment.control2.v + t**3 * segment.end.v)


def _orient(a: Point, b: Point, c: Point) -> float:
    return (b.u - a.u) * (c.v - a.v) - (b.v - a.v) * (c.u - a.u)


def _on_segment(a: Point, b: Point, p: Point, eps: float = 1e-9) -> bool:
    return (min(a.u, b.u) - eps <= p.u <= max(a.u, b.u) + eps
            and min(a.v, b.v) - eps <= p.v <= max(a.v, b.v) + eps
            and abs(_orient(a, b, p)) <= eps)


def _segments_touch(a: Point, b: Point, c: Point, d: Point) -> bool:
    """True for proper crossings, endpoint touches and collinear overlap."""
    o1, o2, o3, o4 = _orient(a, b, c), _orient(a, b, d), _orient(c, d, a), _orient(c, d, b)
    if ((o1 > 1e-9 and o2 < -1e-9 or o1 < -1e-9 and o2 > 1e-9)
            and (o3 > 1e-9 and o4 < -1e-9 or o3 < -1e-9 and o4 > 1e-9)):
        return True
    return ((abs(o1) <= 1e-9 and _on_segment(a, b, c))
            or (abs(o2) <= 1e-9 and _on_segment(a, b, d))
            or (abs(o3) <= 1e-9 and _on_segment(c, d, a))
            or (abs(o4) <= 1e-9 and _on_segment(c, d, b)))


def validate_closed_contour(points: tuple[Point, ...]) -> None:
    """Reject sampled degeneracy and any nonadjacent edge crossing/touching before triangulation."""
    if len(points) < 3 or any(not _finite_point(point) for point in points):
        raise ValueError("sampled closed contour must contain at least three finite points")
    count = len(points)
    for index in range(count):
        a, b = points[index], points[(index + 1) % count]
        if math.hypot(b.u - a.u, b.v - a.v) <= 1e-10:
            raise ValueError("sampled closed contour has a zero-length edge")
    twice_area = sum(a.u * b.v - b.u * a.v
                     for a, b in zip(points, points[1:] + points[:1]))
    if not math.isfinite(twice_area) or abs(twice_area) <= 1e-10:
        raise ValueError("sampled closed contour has degenerate area")
    for first in range(count):
        a, b = points[first], points[(first + 1) % count]
        for second in range(first + 1, count):
            # Neighbor edges share their intended knot; every other touch is invalid.
            if second == first + 1 or (first == 0 and second == count - 1):
                continue
            c, d = points[second], points[(second + 1) % count]
            if _segments_touch(a, b, c, d):
                raise ValueError("sampled closed contour self-intersects or touches itself")


def sample_closed_curve(points: tuple[Point, ...], steps_per_segment: int = 24,
                        k: float = 0.5) -> tuple[Point, ...]:
    """Flatten cubic segments for depth-engine triangles, validating the actual closed sample."""
    if steps_per_segment < 2:
        raise ValueError("curve sampling needs at least two steps per segment")
    segments = cubic_segments(points, k)
    sampled = tuple(evaluate(segment, step / steps_per_segment)
                    for segment in segments for step in range(steps_per_segment))
    validate_closed_contour(sampled)
    return sampled


def _support(component_name: str, z: float) -> SupportFrame:
    # Tilted affine surfaces make the local-to-world depth mapping observable in generated triangles.
    return SupportFrame(component_name, component_name + "-depth", origin=(0.0, 0.0, z),
                        u_axis=(1.0, 0.0, 0.055), v_axis=(0.0, 1.0, -0.025))


CLOTH_SUPPORT = _support("cloth-support", 0.0)
OCCLUDER_SUPPORT = _support("foreground-support", 1.1)
CAMERA = Camera()


def build_components(mode: str, include_occluder: bool = True) -> tuple[Component, ...]:
    """Create one cloth component with raw/smoothed same controls and optional depth occluder."""
    if mode not in {"polygon", "smooth"}:
        raise ValueError("mode must be polygon or smooth")
    controls = tuple(point for _name, point in SEMANTIC_CONTROLS)
    contour = controls if mode == "polygon" else sample_closed_curve(controls)
    cloth = Component("cloth", "one draped cloth silhouette; semantic outer boundary",
                      CLOTH_SUPPORT, contour, "#7896ad")
    if not include_occluder:
        return (cloth,)
    foreground = Component("foreground", "near sheet occludes cloth by support depth",
                           OCCLUDER_SUPPORT, OCCLUDER_CORNERS, "#bd825e")
    return cloth, foreground


def _project(point: Point, support: SupportFrame) -> tuple[float, float, float]:
    return CAMERA.project(support.local_to_world(point))


def visible_boundary_spans(mode: str, include_occluder: bool = True):
    """Return authored-contour visible pieces; every cut comes from current face depth."""
    components = build_components(mode, include_occluder)
    owner = components[0]
    faces = component_faces(components, CAMERA)
    controls = tuple(point for _name, point in SEMANTIC_CONTROLS)
    outline = controls if mode == "polygon" else sample_closed_curve(controls)
    projected = tuple(_project(point, owner.support) for point in outline)
    result = []
    for start, end in zip(projected, projected[1:] + projected[:1]):
        spans = visible_segment_spans(start, end, faces, owner.name)
        for lo, hi in spans:
            p0 = tuple(start[i] + (end[i] - start[i]) * lo for i in range(3))
            p1 = tuple(start[i] + (end[i] - start[i]) * hi for i in range(3))
            result.append((p0, p1))
    return tuple(result)


def _fill_paths(mode: str):
    components = build_components(mode)
    faces = component_faces(components, CAMERA)
    return tuple(visible_regions(faces))


def _screen(point: tuple[float, float, float], x_offset: float) -> tuple[float, float]:
    scale = 72.0
    return x_offset + 178.0 + scale * point[0], 56.0 + scale * (3.95 - point[1])


def _svg_path(points: tuple[tuple[float, float, float], tuple[float, float, float]],
              x_offset: float) -> str:
    start, end = (_screen(point, x_offset) for point in points)
    return f"M {start[0]:.4f},{start[1]:.4f} L {end[0]:.4f},{end[1]:.4f}"


def build_svg() -> str:
    """Render polygon and curve using identical anchors, support and depth occluder."""
    width, height = 860, 390
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="#f7f4ed"/>']
    for mode, x_offset, title in (("polygon", 0.0, "same four semantic controls: raw polygon"),
                                  ("smooth", 430.0, "same four semantic controls: R.smooth curve")):
        for path_data, fill, name in _fill_paths(mode):
            # Backend fill paths are actual visible fragments from SupportFrame-mapped triangles.
            transformed = transform_compound_path(
                path_data, lambda x, y: (x_offset + 178.0 + 72.0*x, 56.0 + 72.0*(3.95-y)))
            parts.append(f'<path id="{mode}-{name}-visible-fill" d="{transformed}" '
                         f'fill="{fill}" stroke="none"/>')
        # Only the authored semantic contour is inked; no triangulation/mesh edges are stroked.
        for index, span in enumerate(visible_boundary_spans(mode)):
            d = _svg_path(span, x_offset)
            parts.append(f'<path id="{mode}-cloth-boundary-{index}" d="{d}" fill="none" '
                         'stroke="#27394b" stroke-width="2.1" stroke-linecap="round"/>')
        parts.append(f'<text x="{x_offset + 10:.0f}" y="25" font-family="sans-serif" '
                     f'font-size="14" fill="#243241">{title}</text>')
    parts.append('<text x="10" y="378" font-family="sans-serif" font-size="11" fill="#38444c">'
                 'Foreground sheet overlaps each cloth support; depth visibility supplies the hidden spans.</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    output = Path(__file__).with_name("spatial-study.svg")
    output.write_text(build_svg(), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
