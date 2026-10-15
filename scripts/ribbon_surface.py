#!/usr/bin/env python3
"""Generate a ribbon support with one bounded transverse-camber parameter.

At zero camber the support is a barycentric subdivision of the existing finite ribbon mesh, so its
piecewise-planar geometry is unchanged. Nonzero camber bows those same source triangles along their
locally transported normals; actual triangle winding drives two-sided paint and opaque depth tests.
"""
from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

from ribbon_family import (BACK_STRIPE_COLOR, FRONT_STRIPE_COLOR, Camera, RibbonMesh, RibbonSpec,
                           build_mesh, camera_basis, mesh_triangles_uv, project)
from vector_visibility import visible_regions

STRIPE_HALF_V = 0.18
DEFAULT_V_INTERVALS = 6
DEFAULT_WIDTH = 420
DEFAULT_HEIGHT = 320

Point3 = tuple[float, float, float]
Point2 = tuple[float, float]


@dataclass(frozen=True)
class SupportTriangle:
    """A sampled support face with immutable local-coordinate provenance."""

    source_triangle: int
    points: tuple[Point3, Point3, Point3]
    uv: tuple[Point2, Point2, Point2]


@dataclass(frozen=True)
class SurfaceMesh:
    """Compiler mesh; it is not an authored coordinate interface."""

    base: RibbonMesh
    triangles: tuple[SupportTriangle, ...]
    camber: float
    v_intervals: int
    rows: tuple[tuple[Point3, ...], ...]


def _dot(a: Point3, b: Point3) -> float:
    return sum(x * y for x, y in zip(a, b))


def _cross(a: Point3, b: Point3) -> Point3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _length(a: Point3) -> float:
    return math.sqrt(_dot(a, a))


def _unit(a: Point3) -> Point3:
    length = _length(a)
    if length <= 1e-12 or not math.isfinite(length):
        raise ValueError("transverse support has a singular frame")
    return tuple(value / length for value in a)


def arc_factor(section_camber: float) -> float:
    """Integral of sqrt(1 + 4*c^2*v^2) over v in [-1,1]."""
    if not math.isfinite(section_camber):
        raise ValueError("section camber must be finite")
    if abs(section_camber) < 1e-12:
        return 2.0
    magnitude = abs(section_camber)
    return math.sqrt(1.0 + 4.0 * magnitude * magnitude) + math.asinh(
        2.0 * magnitude) / (2.0 * magnitude)


def transverse_scale(spec: RibbonSpec, u: float, camber: float) -> float:
    """Ideal continuous-section scale k; finite off-station sections use arc calibration below."""
    if not 0.0 <= u <= 1.0:
        raise ValueError("u must be in [0,1]")
    _validate_camber(camber)
    width = spec.width * (1.0 + (spec.tip_ratio - 1.0) * u)
    local_camber = camber * math.sin(math.pi * u) ** 2
    return width / arc_factor(local_camber)


def _validate_camber(camber: float) -> None:
    if not math.isfinite(camber) or not 0.0 <= camber <= 0.5:
        raise ValueError("camber must be finite and in [0, 0.5]")


def _mix(a: Point3, b: Point3, amount: float) -> Point3:
    return tuple(x + amount * (y - x) for x, y in zip(a, b))


def _frame_at(base: RibbonMesh, u: float) -> tuple[Point3, Point3]:
    """Interpolate the legacy transported frame only to orient the normal displacement."""
    count = len(base.stations) - 1
    scaled = min(count, max(0.0, u * count))
    index = min(count - 1, int(scaled))
    amount = scaled - index
    tangent = _unit(_mix(base.tangents[index], base.tangents[index + 1], amount))
    axis_raw = _mix(base.width_axes[index], base.width_axes[index + 1], amount)
    axis = _unit(tuple(axis_raw[i] - _dot(axis_raw, tangent) * tangent[i]
                       for i in range(3)))
    normal = _unit(_cross(tangent, axis))
    return axis, normal


def _barycentric(uv: Point2, triangle: tuple[Point2, Point2, Point2]) -> tuple[float, float, float]:
    a, b, c = triangle
    determinant = ((b[0] - a[0]) * (c[1] - a[1])
                   - (c[0] - a[0]) * (b[1] - a[1]))
    if abs(determinant) < 1e-14:
        raise ValueError("legacy support triangle has a degenerate UV frame")
    wb = ((uv[0] - a[0]) * (c[1] - a[1])
          - (c[0] - a[0]) * (uv[1] - a[1])) / determinant
    wc = ((b[0] - a[0]) * (uv[1] - a[1])
          - (uv[0] - a[0]) * (b[1] - a[1])) / determinant
    return 1.0 - wb - wc, wb, wc


def _base_point(source_uv: tuple[Point2, Point2, Point2],
                source_points: tuple[Point3, Point3, Point3], uv: Point2) -> Point3:
    weights = _barycentric(uv, source_uv)
    return tuple(sum(weights[j] * source_points[j][axis] for j in range(3))
                 for axis in range(3))


def _section_segments(base: RibbonMesh,
                      source_triangles: list[tuple[tuple[tuple[float, float, float], float, float], ...]],
                      u: float):
    count = len(base.stations) - 1
    scaled = min(count, max(0.0, u * count))
    cell = min(count - 1, int(scaled))
    local_u = scaled - cell
    diagonal_v = 2.0 * local_u - 1.0
    cuts = sorted(set((-1.0, 1.0, min(1.0, max(-1.0, diagonal_v)))))
    segments = []
    for v0, v1 in zip(cuts, cuts[1:]):
        if v1 - v0 <= 1e-14:
            continue
        middle = (u, (v0 + v1) / 2.0)
        source_id = None
        for candidate in (2 * cell, 2 * cell + 1):
            source = source_triangles[candidate]
            source_uv = tuple((vertex[1], vertex[2]) for vertex in source)
            if min(_barycentric(middle, source_uv)) >= -1e-10:
                source_id = candidate
                break
        if source_id is None:
            raise ValueError(f"legacy support has no material section at u={u:g}")
        source = source_triangles[source_id]
        source_uv = tuple((vertex[1], vertex[2]) for vertex in source)
        source_points = tuple(vertex[0] for vertex in source)
        p0 = _base_point(source_uv, source_points, (u, v0))
        p1 = _base_point(source_uv, source_points, (u, v1))
        slope = tuple((p1[i] - p0[i]) / (v1 - v0) for i in range(3))
        segments.append((v0, v1, p0, p1, slope))
    if not segments:
        raise ValueError(f"legacy support has an empty material section at u={u:g}")
    center_source = None
    for candidate in (2 * cell, 2 * cell + 1):
        source = source_triangles[candidate]
        source_uv = tuple((vertex[1], vertex[2]) for vertex in source)
        if min(_barycentric((u, 0.0), source_uv)) >= -1e-10:
            center_source = candidate
            break
    if center_source is None:
        raise ValueError(f"legacy support has no local v=0 point at u={u:g}")
    center = _base_point(tuple((vertex[1], vertex[2]) for vertex in source_triangles[center_source]),
                         tuple(vertex[0] for vertex in source_triangles[center_source]), (u, 0.0))
    return center, tuple(segments)


def _section_length(segments, normal: Point3, bow: float, steps: int = 128) -> float:
    """Bounded composite-Simpson integral of the actual piecewise-barycentric section speed."""
    total = 0.0
    for v0, v1, _p0, _p1, slope in segments:
        count = steps if steps % 2 == 0 else steps + 1
        step = (v1 - v0) / count
        subtotal = 0.0
        for index in range(count + 1):
            v = v0 + index * step
            velocity = tuple(slope[axis] + 2.0 * bow * v * normal[axis]
                             for axis in range(3))
            speed = _length(velocity)
            subtotal += (1 if index in (0, count) else 4 if index % 2 else 2) * speed
        total += subtotal * step / 3.0
    return total


def _section_calibration(spec: RibbonSpec, base: RibbonMesh,
                         source_triangles, u: float, camber: float):
    center, segments = _section_segments(base, source_triangles, u)
    baseline_length = sum(_length(tuple(p1[i] - p0[i] for i in range(3)))
                          for _v0, _v1, p0, p1, _slope in segments)
    if camber == 0.0:
        return center, segments, (0.0, 0.0, 0.0), 0.0, 1.0, baseline_length
    _axis, normal = _frame_at(base, u)
    local_camber = camber * math.sin(math.pi * u) ** 2
    width = spec.width * (1.0 + (spec.tip_ratio - 1.0) * u)
    bow = width * local_camber / 2.0
    bowed_length = _section_length(segments, normal, bow)
    if baseline_length <= 1e-12 or bowed_length <= 1e-12 or not math.isfinite(bowed_length):
        raise ValueError(f"degenerate cambered material section at u={u:g}")
    # The original finite support's true arc length is the exact limiting material width. It
    # differs from the continuous requested width only by the old triangle-sampling tolerance.
    normalization = baseline_length / bowed_length
    if not math.isfinite(normalization) or normalization <= 0:
        raise ValueError(f"invalid material-width normalization at u={u:g}")
    return center, segments, normal, bow, normalization, baseline_length


def _map_source_point(spec: RibbonSpec, base: RibbonMesh,
                      source_uv: tuple[Point2, Point2, Point2],
                      source_points: tuple[Point3, Point3, Point3], uv: Point2,
                      camber: float, source_triangles, section_cache) -> Point3:
    baseline = _base_point(source_uv, source_points, uv)
    u, v = uv
    if camber == 0.0 or u == 0.0 or u == 1.0:
        return baseline
    cache_key = round(u * 10**13)
    if cache_key not in section_cache:
        section_cache[cache_key] = _section_calibration(
            spec, base, source_triangles, u, camber)
    center, _segments, normal, bow, normalization, _baseline_length = section_cache[cache_key]
    displacement = tuple(baseline[i] - center[i] + bow * v * v * normal[i]
                         for i in range(3))
    return tuple(center[i] + normalization * displacement[i] for i in range(3))


def _clip_v(polygon: list[Point2], boundary: float, keep_greater: bool) -> list[Point2]:
    if not polygon:
        return []
    output = []
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        fa, fb = a[1] - boundary, b[1] - boundary
        in_a = fa >= -1e-12 if keep_greater else fa <= 1e-12
        in_b = fb >= -1e-12 if keep_greater else fb <= 1e-12
        if in_a != in_b:
            amount = fa / (fa - fb)
            output.append((a[0] + amount * (b[0] - a[0]), boundary))
        if in_b:
            output.append(b)
    return output


def _polygon_area2(polygon: list[Point2]) -> float:
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(polygon, polygon[1:] + polygon[:1]))


def _triangulate_polygon(polygon: list[Point2]) -> Iterable[tuple[Point2, Point2, Point2]]:
    if len(polygon) < 3:
        return
    first = polygon[0]
    for index in range(1, len(polygon) - 1):
        triangle = (first, polygon[index], polygon[index + 1])
        if abs(_polygon_area2(list(triangle))) > 1e-14:
            yield triangle


def _uv_key(uv: Point2) -> tuple[int, int]:
    return round(uv[0] * 10**13), round(uv[1] * 10**13)


def build_surface(spec: RibbonSpec, camber: float = 0.0, u_intervals: int | None = None,
                  v_intervals: int = DEFAULT_V_INTERVALS) -> SurfaceMesh:
    """Subdivide legacy triangles and normalize each bowed material section by its actual arc.

    Barycentric evaluation is essential: at camber=0 every subface lies on exactly the old finite
    triangle, not a new smooth patch. For camber>0, each finite baseline section is piecewise linear
    across the old diagonal; its bowed arc is integrated on those segments and uniformly normalized
    about the original local-v=0 point. The requested continuous width and finite legacy section
    can differ by the legacy mesh's sampling error; normalization preserves the latter, which is the
    exact zero-camber material limit. Mesh chords approximate that normalized continuous section.
    """
    spec.validate()
    _validate_camber(camber)
    if isinstance(v_intervals, bool) or not isinstance(v_intervals, int) or not 2 <= v_intervals <= 24:
        raise ValueError("v_intervals must be an integer in [2,24]")
    base = build_mesh(spec, u_intervals)
    old_uv_triangles = mesh_triangles_uv(base)
    cache: dict[tuple[int, int], Point3] = {}
    section_cache = {}
    triangles = []
    levels = tuple(-1.0 + 2.0 * i / v_intervals for i in range(v_intervals + 1))
    for source_id, source in enumerate(old_uv_triangles):
        source_uv = tuple((vertex[1], vertex[2]) for vertex in source)
        source_points = tuple(vertex[0] for vertex in source)
        for low, high in zip(levels, levels[1:]):
            polygon = _clip_v(list(source_uv), low, True)
            polygon = _clip_v(polygon, high, False)
            for uv_triangle in _triangulate_polygon(polygon):
                points = []
                for uv in uv_triangle:
                    key = _uv_key(uv)
                    if key not in cache:
                        cache[key] = _map_source_point(spec, base, source_uv, source_points,
                                                       uv, camber, old_uv_triangles,
                                                       section_cache)
                    points.append(cache[key])
                edge_a = tuple(points[1][i] - points[0][i] for i in range(3))
                edge_b = tuple(points[2][i] - points[0][i] for i in range(3))
                if _length(_cross(edge_a, edge_b)) <= 1e-12:
                    raise ValueError(f"degenerate sampled support face at source triangle {source_id}")
                triangles.append(SupportTriangle(source_id, tuple(points), tuple(uv_triangle)))
    rows = []
    for u in base.stations:
        row = []
        for v in levels:
            key = _uv_key((u, v))
            if key not in cache:
                # Endpoint cross-sections are directly on legacy mesh rows and can occur only at a
                # triangle's isolated vertex in the clipping loop; locate that source face once.
                source_id = next(index for index, triangle in enumerate(old_uv_triangles)
                                 if min(vertex[0] for vertex in triangle) - 1e-12 <= u
                                 <= max(vertex[0] for vertex in triangle)
                                 and min(vertex[1] for vertex in triangle) - 1e-12 <= v
                                 <= max(vertex[1] for vertex in triangle))
                source = old_uv_triangles[source_id]
                cache[key] = _map_source_point(
                    spec, base, tuple((vertex[1], vertex[2]) for vertex in source),
                    tuple(vertex[0] for vertex in source), (u, v), camber,
                    old_uv_triangles, section_cache)
            row.append(cache[key])
        rows.append(tuple(row))
    return SurfaceMesh(base, tuple(triangles), camber, v_intervals, tuple(rows))


def surface_points(spec: RibbonSpec, mesh: SurfaceMesh, u: float,
                   v_values: Iterable[float]) -> tuple[Point3, ...]:
    """Evaluate one section with a shared bounded arc calibration for diagnostics/tests."""
    if not math.isfinite(u) or not 0.0 <= u <= 1.0:
        raise ValueError("u must be finite and in [0,1]")
    source_triangles = mesh_triangles_uv(mesh.base)
    count = len(mesh.base.stations) - 1
    cell = min(count - 1, int(min(count, max(0.0, u * count))))
    profiles = {}
    result = []
    for v in v_values:
        if not math.isfinite(v) or not -1.0 <= v <= 1.0:
            raise ValueError("v must be finite and in [-1,1]")
        coordinate = (u, v)
        selected = None
        for source_id in (2 * cell, 2 * cell + 1):
            source = source_triangles[source_id]
            source_uv = tuple((vertex[1], vertex[2]) for vertex in source)
            if min(_barycentric(coordinate, source_uv)) >= -1e-10:
                selected = source
                break
        if selected is None:
            raise ValueError(f"no finite legacy support triangle contains (u={u:g},v={v:g})")
        source_uv = tuple((vertex[1], vertex[2]) for vertex in selected)
        result.append(_map_source_point(spec, mesh.base, source_uv,
                                       tuple(vertex[0] for vertex in selected), coordinate,
                                       mesh.camber, source_triangles, profiles))
    return tuple(result)


def surface_point(spec: RibbonSpec, mesh: SurfaceMesh, u: float, v: float) -> Point3:
    """Evaluate one UV point on the legacy-barycentric finite support."""
    return surface_points(spec, mesh, u, (v,))[0]


def _normal(triangle: SupportTriangle) -> Point3:
    a, b, c = triangle.points
    edge_a = tuple(b[i] - a[i] for i in range(3))
    edge_b = tuple(c[i] - a[i] for i in range(3))
    return _cross(edge_a, edge_b)


def surface_faces(spec: RibbonSpec, camera: Camera, mesh: SurfaceMesh
                  ) -> list[tuple[list[Point3], str, str]]:
    """Return base and existing stripe fills; the face label comes from its actual normal."""
    stripe_faces = []
    base_faces = []
    for triangle in mesh.triangles:
        side = "front" if sum(_normal(triangle)[i] * camera_basis(camera)[2][i]
                              for i in range(3)) > 0 else "back"
        stripe_color = FRONT_STRIPE_COLOR if side == "front" else BACK_STRIPE_COLOR
        polygon = _clip_v(list(triangle.uv), -STRIPE_HALF_V, True)
        polygon = _clip_v(polygon, STRIPE_HALF_V, False)
        for uv_triangle in _triangulate_polygon(polygon):
            points = [_point_in_triangle(uv, triangle) for uv in uv_triangle]
            stripe_faces.append(([project(point, camera) for point in points], stripe_color,
                                 spec.name))
        base_color = spec.front if side == "front" else spec.back
        base_faces.append(([project(point, camera) for point in triangle.points], base_color,
                           spec.name))
    return stripe_faces + base_faces


def _point_in_triangle(uv: Point2, triangle: SupportTriangle) -> Point3:
    weights = _barycentric(uv, triangle.uv)
    return tuple(sum(weights[j] * triangle.points[j][axis] for j in range(3))
                 for axis in range(3))


def _projected_fit(meshes: Iterable[SurfaceMesh], camera: Camera, width: int, height: int,
                   margin: float = 20.0) -> tuple[float, float, float]:
    points = [project(vertex, camera) for mesh in meshes
              for triangle in mesh.triangles for vertex in triangle.points]
    points.extend(project(vertex, camera) for mesh in meshes for row in mesh.rows for vertex in row)
    if not points:
        raise ValueError("cannot fit an empty support surface")
    min_x, max_x = min(p[0] for p in points), max(p[0] for p in points)
    min_y, max_y = min(p[1] for p in points), max(p[1] for p in points)
    scale = min((width - 2 * margin) / max(max_x - min_x, 1e-9),
                (height - 2 * margin) / max(max_y - min_y, 1e-9))
    offset_x = (width - scale * (min_x + max_x)) / 2.0
    offset_y = (height + scale * (min_y + max_y)) / 2.0
    return scale, offset_x, offset_y


def _render_faces(spec: RibbonSpec, camera: Camera, mesh: SurfaceMesh, width: int, height: int,
                  fit: tuple[float, float, float], prefix: str, labelled: bool) -> str:
    scale, offset_x, offset_y = fit
    transformed = []
    for triangle, color, component in surface_faces(spec, camera, mesh):
        points = [(offset_x + scale * p[0], offset_y - scale * p[1], p[2])
                  for p in triangle]
        transformed.append((points, color, component))
    semantic_paths = []
    safe = re.sub(r"[^A-Za-z0-9_-]", "-", spec.name)
    for index, (path, color, component) in enumerate(visible_regions(transformed)):
        if color in {FRONT_STRIPE_COLOR, BACK_STRIPE_COLOR}:
            intent = "existing local longitudinal stripe; actual support winding selects its side"
        elif color == spec.front:
            intent = "existing front artwork fill; selected by actual support normal"
        elif color == spec.back:
            intent = "existing back artwork fill; selected by actual support normal"
        else:
            intent = "existing artwork fill"
        semantic_paths.append(
            f'<!-- {escape(component)}: {intent}; support triangles are not line art -->'
            f'<path id="{prefix}-{safe}-fill-{index}" d="{path}" fill="{escape(color)}" '
            f'fill-rule="nonzero" data-component="{escape(component)}"/>')
    metadata = "" if not labelled else (
        f'<metadata id="{prefix}-support-info">camber={mesh.camber:.2f}; '
        f'u={len(mesh.base.stations)-1}; v={mesh.v_intervals}</metadata>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<!-- neutral panel ground; diagnostic support/artwork only -->'
            f'<rect id="{prefix}-ground" width="{width}" height="{height}" fill="#f4f5ef"/>'
            f'{metadata}{"".join(semantic_paths)}</svg>')


def render_condition(spec: RibbonSpec, camera: Camera, mesh: SurfaceMesh,
                     fit_meshes: tuple[SurfaceMesh, SurfaceMesh], width: int = DEFAULT_WIDTH,
                     height: int = DEFAULT_HEIGHT, prefix: str = "ribbon-condition") -> str:
    """Render one pair member using a fit computed from both geometries."""
    fit = _projected_fit(fit_meshes, camera, width, height)
    return _render_faces(spec, camera, mesh, width, height, fit, prefix, True)


def render_pair(spec: RibbonSpec, camera: Camera, u_intervals: int = 48,
                v_intervals: int = DEFAULT_V_INTERVALS, width: int = DEFAULT_WIDTH,
                height: int = DEFAULT_HEIGHT, prefix: str = "ribbon-pair"
                ) -> tuple[str, str, SurfaceMesh, SurfaceMesh]:
    """Render the flat and frozen-curved conditions under one shared geometric fit."""
    flat = build_surface(spec, 0.0, u_intervals, v_intervals)
    curved = build_surface(spec, 0.35, u_intervals, v_intervals)
    fit = _projected_fit((flat, curved), camera, width, height)
    return (_render_faces(spec, camera, flat, width, height, fit, prefix + "-flat", True),
            _render_faces(spec, camera, curved, width, height, fit, prefix + "-camber", True),
            flat, curved)


def render_single(spec: RibbonSpec, camera: Camera, camber: float, output: Path,
                  u_intervals: int | None = None, v_intervals: int = DEFAULT_V_INTERVALS,
                  size: tuple[int, int] = (720, 540)) -> tuple[Path, Path]:
    """Write one runnable SVG/PNG view from an existing compact ribbon spec plus camber."""
    mesh = build_surface(spec, camber, u_intervals, v_intervals)
    fit = _projected_fit((mesh,), camera, *size)
    svg = _render_faces(spec, camera, mesh, *size, fit,
                        re.sub(r"[^A-Za-z0-9_-]", "-", output.stem), True)
    svg_path = output.with_suffix(".svg")
    png_path = output.with_suffix(".png")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg, encoding="utf-8")
    from draw import render
    render(str(svg_path), str(png_path), size=size)
    return svg_path, png_path


def main() -> None:
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path, help="existing ribbon_family JSON spec")
    parser.add_argument("--camber", required=True, type=float,
                        help="dimensionless transverse camber in [0, 0.5]; study value is 0.35")
    parser.add_argument("--yaw", type=float, default=0.0)
    parser.add_argument("--pitch", type=float, default=0.0)
    parser.add_argument("--camera-name", default="front")
    parser.add_argument("--u-intervals", type=int)
    parser.add_argument("--v-intervals", type=int, default=DEFAULT_V_INTERVALS)
    parser.add_argument("-o", "--output", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.spec.read_text(encoding="utf-8"))
    spec = RibbonSpec.from_mapping(data)
    camera = Camera(args.camera_name, args.yaw, args.pitch)
    camera.validate()
    svg, png = render_single(spec, camera, args.camber, args.output,
                             args.u_intervals, args.v_intervals)
    print(svg)
    print(png)


if __name__ == "__main__":
    main()
