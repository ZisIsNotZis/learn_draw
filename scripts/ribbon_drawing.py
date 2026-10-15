#!/usr/bin/env python3
"""Depth-visible semantic perimeter ink and a side-consistent local ribbon motif.

The drawing rules consume the unchanged ribbon support as compiler input. Support triangles carry
provenance for visibility and clipping; they are never emitted as artistic mesh edges.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ribbon_family import (BACK_STRIPE_COLOR, FRONT_STRIPE_COLOR, Camera, RibbonMesh, RibbonSpec,
                           RibbonArtworkTriangle, build_mesh, camera_basis, face_side,
                           mesh_triangles, mesh_triangles_uv, project, ribbon_artwork_faces,
                           ribbon_faces)
from vector_visibility import EPS, depth_plane, line_clip, subtract_convex, visible_regions

# Geometric tolerances: projected segment/edge intersections use world-projection units; depth
# comparisons reuse vector_visibility.EPS and its documented 1e-5 first-declared tie bias.
PROJECTED_EPS = 1e-9
BARYCENTRIC_EPS = 1e-8
CUT_MERGE_EPS = 1e-8
UV_MERGE_EPS = 1e-8
TIE_BIAS = 1e-5
STROKE_MASK_EPS = 1e-9

# Artistic weights are fixed canvas pixels, never view- or u-range-authored.
SILHOUETTE_WIDTH_PX = 1.2
OVERLAP_WIDTH_PX = 1.8
INK_COLOR = "#253746"
MOTIF_CORE_COLOR = "#fff1b8"
MOTIF_BORDER_COLOR = "#472639"
MOTIF_CORE_HALF_V = 0.08
MOTIF_OUTER_HALF_V = 0.16
MOTIF_JOIN_SIDES = 16
DEFAULT_SAMPLING = 128


@dataclass(frozen=True)
class PerimeterCandidate:
    """One compiler-sampled edge of the complete local UV-domain boundary."""

    index: int
    boundary: str
    cell: int
    uv0: tuple[float, float]
    uv1: tuple[float, float]
    point0: tuple[float, float, float]
    point1: tuple[float, float, float]
    source_triangle: int


@dataclass(frozen=True)
class VisiblePerimeterSpan:
    """A depth-visible subinterval with its source face and any farther covered surfaces."""

    candidate_index: int
    boundary: str
    cell: int
    source_triangle: int
    scene_owner_index: int
    t0: float
    t1: float
    uv0: tuple[float, float]
    uv1: tuple[float, float]
    screen0: tuple[float, float, float]
    screen1: tuple[float, float, float]
    role: str
    farther_triangles: tuple[int, ...]
    nearest_gap: float | None


@dataclass(frozen=True)
class SceneTriangle:
    """Opaque depth surface with stable scene and local-support provenance."""

    points: tuple[tuple[float, float, float], ...]
    component: str
    kind: str
    cell: int | None
    support_triangle: int | None


@dataclass(frozen=True)
class PerimeterSelection:
    candidates: tuple[PerimeterCandidate, ...]
    spans: tuple[VisiblePerimeterSpan, ...]
    scene_triangles: tuple[SceneTriangle, ...]
    projected_triangles: tuple[tuple[tuple[float, float, float], ...], ...]
    camera: Camera


def perimeter_candidates(mesh: RibbonMesh) -> tuple[PerimeterCandidate, ...]:
    """Enumerate both full lengthwise edges and both full-width end caps exactly once."""
    result = []
    cells = len(mesh.stations) - 1
    for cell in range(cells):
        u0, u1 = mesh.stations[cell:cell + 2]
        low0, high0 = mesh.rows[cell]
        low1, high1 = mesh.rows[cell + 1]
        result.append(PerimeterCandidate(len(result), "v=-1", cell, (u0, -1.0),
                                         (u1, -1.0), low0, low1, 2 * cell))
        result.append(PerimeterCandidate(len(result), "v=+1", cell, (u0, 1.0),
                                         (u1, 1.0), high0, high1, 2 * cell + 1))
    result.append(PerimeterCandidate(len(result), "u=0", 0, (0.0, -1.0), (0.0, 1.0),
                                     mesh.rows[0][0], mesh.rows[0][1], 1))
    last = cells - 1
    # At the final cap, the complete low-to-high edge belongs to the first triangle of the last
    # cell; the second face only shares the high endpoint and must not win an unrelated tie.
    result.append(PerimeterCandidate(len(result), "u=1", last, (1.0, -1.0), (1.0, 1.0),
                                     mesh.rows[-1][0], mesh.rows[-1][1], 2 * last))
    return tuple(result)


def _cross2(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _segment_edge_parameters(q0: tuple[float, float, float],
                             q1: tuple[float, float, float],
                             a: tuple[float, float, float],
                             b: tuple[float, float, float]) -> tuple[float, ...]:
    """Return segment parameters for actual projected intersections with a triangle edge."""
    r = (q1[0] - q0[0], q1[1] - q0[1])
    s = (b[0] - a[0], b[1] - a[1])
    delta = (a[0] - q0[0], a[1] - q0[1])
    denominator = _cross2(r, s)
    if abs(denominator) < PROJECTED_EPS:
        if abs(_cross2(delta, r)) > PROJECTED_EPS:
            return ()
        rr = r[0] * r[0] + r[1] * r[1]
        if rr < PROJECTED_EPS:
            return ()
        return tuple(((point[0] - q0[0]) * r[0] + (point[1] - q0[1]) * r[1]) / rr
                     for point in (a, b))
    t = _cross2(delta, s) / denominator
    edge_t = _cross2(delta, r) / denominator
    if (-PROJECTED_EPS <= t <= 1 + PROJECTED_EPS
            and -PROJECTED_EPS <= edge_t <= 1 + PROJECTED_EPS):
        return (min(1.0, max(0.0, t)),)
    return ()


def _barycentric2(point: tuple[float, float, float],
                  triangle: tuple[tuple[float, float, float], ...]
                  ) -> tuple[float, float, float] | None:
    a, b, c = triangle
    ab, ac = (b[0] - a[0], b[1] - a[1]), (c[0] - a[0], c[1] - a[1])
    ap = (point[0] - a[0], point[1] - a[1])
    determinant = _cross2(ab, ac)
    if abs(determinant) < PROJECTED_EPS:
        return None
    wb = _cross2(ap, ac) / determinant
    wc = _cross2(ab, ap) / determinant
    return 1.0 - wb - wc, wb, wc


def _plane_at(plane: tuple[float, float, float], point: tuple[float, float, float]) -> float:
    return plane[0] * point[0] + plane[1] * point[1] + plane[2]


def _interpolate3(a: tuple[float, float, float], b: tuple[float, float, float], t: float
                  ) -> tuple[float, float, float]:
    return tuple(a[k] + t * (b[k] - a[k]) for k in range(3))


def _split_parameters(candidate: PerimeterCandidate, camera: Camera,
                      projected: tuple[tuple[tuple[float, float, float], ...], ...],
                      planes: tuple[tuple[float, float, float] | None, ...],
                      scene_owner_index: int) -> tuple[float, ...]:
    q0, q1 = project(candidate.point0, camera), project(candidate.point1, camera)
    cuts = [0.0, 1.0]
    for index, triangle in enumerate(projected):
        if index == scene_owner_index or planes[index] is None:
            continue
        triangle_cuts = [0.0, 1.0]
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            triangle_cuts.extend(_segment_edge_parameters(q0, q1, a, b))
        triangle_cuts = sorted(triangle_cuts)
        cuts.extend(triangle_cuts)
        # A plane root is relevant only on the segment interval that lies inside this triangle;
        # do not split against an extrapolated depth plane outside its actual support.
        for lo, hi in zip(triangle_cuts, triangle_cuts[1:]):
            if hi - lo <= CUT_MERGE_EPS:
                continue
            middle = _interpolate3(q0, q1, (lo + hi) / 2.0)
            weights = _barycentric2(middle, triangle)
            if weights is None or min(weights) < -BARYCENTRIC_EPS:
                continue
            depth0 = _interpolate3(q0, q1, lo)
            depth1 = _interpolate3(q0, q1, hi)
            delta0 = depth0[2] - _plane_at(planes[index], depth0)
            delta1 = depth1[2] - _plane_at(planes[index], depth1)
            for target in (0.0, _tie_bias_for(index, scene_owner_index) + EPS):
                value0, value1 = delta0 - target, delta1 - target
                if abs(value0) <= EPS:
                    cuts.append(lo)
                if abs(value1) <= EPS:
                    cuts.append(hi)
                if value0 * value1 < 0.0:
                    root = lo + value0 / (value0 - value1) * (hi - lo)
                    cuts.append(root)
    ordered = sorted(min(1.0, max(0.0, value)) for value in cuts
                     if math.isfinite(value) and -PROJECTED_EPS <= value <= 1 + PROJECTED_EPS)
    unique = []
    for value in ordered:
        if not unique or value - unique[-1] > CUT_MERGE_EPS:
            unique.append(value)
    return tuple(unique)


def _tie_bias_for(other_index: int, source_index: int) -> float:
    """Match vector_visibility's declaration-order bias for this triangle pair."""
    return TIE_BIAS if other_index < source_index else -TIE_BIAS


def _scene_triangles(spec: RibbonSpec, mesh: RibbonMesh, camera: Camera,
                     card_bounds: tuple[float, float, float, float] | None
                     ) -> tuple[SceneTriangle, ...]:
    result = []
    if card_bounds is not None:
        left, bottom, right, top = card_bounds
        corners = ((left, bottom, 0.0), (right, bottom, 0.0),
                   (right, top, 0.0), (left, top, 0.0))
        for triangle in ((corners[0], corners[1], corners[2]),
                         (corners[0], corners[2], corners[3])):
            result.append(SceneTriangle(triangle, "support-card", "external", None, None))
    for index, triangle in enumerate(mesh_triangles(mesh)):
        result.append(SceneTriangle(tuple(triangle), spec.name, "ribbon", index // 2, index))
    return tuple(result)


def _is_front_occluder(other_depth: float, source_depth: float,
                       other_index: int, source_index: int) -> bool:
    # vector_visibility clips with `other - source + bias >= -EPS`.
    return other_depth - source_depth + _tie_bias_for(other_index, source_index) >= -EPS


def select_visible_perimeter(spec: RibbonSpec, camera: Camera, mesh: RibbonMesh | None = None,
                              card_bounds: tuple[float, float, float, float] | None = None
                              ) -> PerimeterSelection:
    """Split whole-domain candidates at projected edges/depth roots and keep visible intervals.

    Provenance exclusion is exactly the candidate's owning support triangle. Other faces, including
    adjacent cells and external cards, participate in depth visibility; no u-range or neighborhood
    heuristic can hide a true fold. The existing first-declared coplanar tie policy is preserved.
    """
    mesh = mesh or build_mesh(spec)
    candidates = perimeter_candidates(mesh)
    scene = _scene_triangles(spec, mesh, camera, card_bounds)
    projected = tuple(tuple(project(point, camera) for point in triangle.points)
                      for triangle in scene)
    planes = tuple(depth_plane(triangle) for triangle in projected)
    card_count = 2 if card_bounds is not None else 0
    spans = []
    for candidate in candidates:
        owner_index = card_count + candidate.source_triangle
        q0, q1 = project(candidate.point0, camera), project(candidate.point1, camera)
        if math.hypot(q1[0] - q0[0], q1[1] - q0[1]) < PROJECTED_EPS:
            continue
        cuts = _split_parameters(candidate, camera, projected, planes, owner_index)
        owner_plane = planes[owner_index]
        if owner_plane is None:
            continue
        for t0, t1 in zip(cuts, cuts[1:]):
            if t1 - t0 <= CUT_MERGE_EPS:
                continue
            midpoint = _interpolate3(q0, q1, (t0 + t1) / 2.0)
            hidden = False
            farther = []
            gaps = []
            for index, triangle in enumerate(projected):
                if index == owner_index or planes[index] is None:
                    continue
                weights = _barycentric2(midpoint, triangle)
                if weights is None or min(weights) < -BARYCENTRIC_EPS:
                    continue
                other_depth = _plane_at(planes[index], midpoint)
                source_depth = _plane_at(owner_plane, midpoint)
                if _is_front_occluder(other_depth, source_depth, index, owner_index):
                    hidden = True
                    break
                gap = source_depth - other_depth
                if gap > TIE_BIAS + EPS:
                    farther.append(index)
                    gaps.append(gap)
            if hidden:
                continue
            # Distinct provenance, not projected proximity, determines a semantic overlap cue.
            nonadjacent_far = []
            for index in farther:
                source = scene[index]
                if source.kind == "external" or (source.kind == "ribbon"
                                                   and source.cell is not None
                                                   and abs(source.cell - candidate.cell) > 1):
                    nonadjacent_far.append(index)
            role = "overlap" if nonadjacent_far else "silhouette"
            uv0 = tuple(candidate.uv0[k] + t0 * (candidate.uv1[k] - candidate.uv0[k])
                        for k in range(2))
            uv1 = tuple(candidate.uv0[k] + t1 * (candidate.uv1[k] - candidate.uv0[k])
                        for k in range(2))
            spans.append(VisiblePerimeterSpan(
                candidate.index, candidate.boundary, candidate.cell,
                candidate.source_triangle, owner_index, t0, t1, uv0, uv1,
                _interpolate3(q0, q1, t0), _interpolate3(q0, q1, t1), role,
                tuple(nonadjacent_far), min(gaps) if gaps else None))
    return PerimeterSelection(candidates, tuple(spans), scene, projected, camera)


def _clip_polygon_depth(triangle: tuple[tuple[float, float, float], ...],
                        other_plane: tuple[float, float, float],
                        source_plane: tuple[float, float, float],
                        other_index: int, source_index: int) -> list[tuple[float, float, float]]:
    bias = _tie_bias_for(other_index, source_index)
    return line_clip(list(triangle), lambda point: (
        _plane_at(other_plane, point) - _plane_at(source_plane, point) + bias + EPS), True)


def _line_rectangle(a: tuple[float, float, float], b: tuple[float, float, float],
                    width: float) -> list[tuple[float, float, float]]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length <= PROJECTED_EPS:
        return []
    nx, ny = -dy * width / (2.0 * length), dx * width / (2.0 * length)
    return [(a[0] + nx, a[1] + ny, a[2]), (b[0] + nx, b[1] + ny, b[2]),
            (b[0] - nx, b[1] - ny, b[2]), (a[0] - nx, a[1] - ny, a[2])]


def _join_disc(center: tuple[float, float, float], width: float) -> list[tuple[float, float, float]]:
    radius = width / 2.0
    return [(center[0] + radius * math.cos(2 * math.pi * index / MOTIF_JOIN_SIDES),
             center[1] + radius * math.sin(2 * math.pi * index / MOTIF_JOIN_SIDES), center[2])
            for index in range(MOTIF_JOIN_SIDES)]


def _subtract_occluders(subject: list[tuple[float, float, float]],
                        selection: PerimeterSelection, source_owner_index: int,
                        owner_plane: tuple[float, float, float] | None,
                        panel_transform: tuple[float, float, float]) -> list[list[tuple[float, float, float]]]:
    """Clip finite-width screen ink against every depth-nearer support, including cards.

    Ink depth is extended across its finite screen-space footprint using its owning support
    triangle's projected depth plane. This is an explicit line-art convention, not a geometry edit.
    """
    if owner_plane is None or len(subject) < 3:
        return []
    scale, offset_x, offset_y = panel_transform
    output = [subject]
    for index, triangle in enumerate(selection.projected_triangles):
        if index == source_owner_index:
            continue
        other_plane = depth_plane(triangle)
        if other_plane is None:
            continue
        cover = _clip_polygon_depth(triangle, other_plane, owner_plane, index,
                                    source_owner_index)
        if len(cover) < 3:
            continue
        # Affine canvas fit preserves convexity and the interpolated depth plane.
        cover = [(offset_x + scale * point[0], offset_y - scale * point[1], point[2])
                 for point in cover]
        next_output = []
        for polygon in output:
            if len(polygon) < 3:
                continue
            next_output.extend(subtract_convex(polygon, cover))
        output = next_output
        if not output:
            break
    return [polygon for polygon in output if len(polygon) >= 3]


def _uv_key(uv: tuple[float, float]) -> tuple[int, int]:
    return round(uv[0] / UV_MERGE_EPS), round(uv[1] / UV_MERGE_EPS)


def _stroke_shapes(selection: PerimeterSelection, fit: tuple[float, float, float]
                   ) -> list[tuple[str, float, list[tuple[float, float, float]],
                                   tuple[int, ...], int, str]]:
    """Build fixed-pixel stroke coverage polygons and clip their finite width in depth."""
    scale, offset_x, offset_y = fit

    def to_canvas(point):
        return offset_x + scale * point[0], offset_y - scale * point[1], point[2]

    endpoint_counts: dict[tuple[str, tuple[int, int]], list[VisiblePerimeterSpan]] = {}
    for span in selection.spans:
        endpoint_counts.setdefault((span.role, _uv_key(span.uv0)), []).append(span)
        endpoint_counts.setdefault((span.role, _uv_key(span.uv1)), []).append(span)
    shapes = []
    for span in selection.spans:
        width = OVERLAP_WIDTH_PX if span.role == "overlap" else SILHOUETTE_WIDTH_PX
        a, b = to_canvas(span.screen0), to_canvas(span.screen1)
        candidate_poly = _line_rectangle(a, b, width)
        if not candidate_poly:
            continue
        plane = depth_plane(selection.projected_triangles[span.scene_owner_index])
        clipped = _subtract_occluders(candidate_poly, selection, span.scene_owner_index, plane, fit)
        for piece in clipped:
            shapes.append((span.role, width, piece, (span.candidate_index,), span.source_triangle,
                           span.boundary))
    # Round joins are emitted only where two visible spans genuinely meet in local UV; hidden gaps
    # have a single endpoint and therefore cannot acquire a bridge cap.
    joined = set()
    for span in selection.spans:
        width = OVERLAP_WIDTH_PX if span.role == "overlap" else SILHOUETTE_WIDTH_PX
        for uv, point in ((span.uv0, span.screen0), (span.uv1, span.screen1)):
            key = (span.role, _uv_key(uv))
            if key in joined or len(endpoint_counts[key]) < 2:
                continue
            joined.add(key)
            center = to_canvas(point)
            disc = _join_disc(center, width)
            # The two incident support faces share this exact 3D perimeter point; use the current
            # source plane for the subpixel join coverage and clip all other closer geometry.
            plane = depth_plane(selection.projected_triangles[span.scene_owner_index])
            clipped = _subtract_occluders(disc, selection, span.scene_owner_index, plane, fit)
            for piece in clipped:
                shapes.append((span.role, width, piece, (span.candidate_index,), span.source_triangle,
                               span.boundary))
    return shapes


def _format(value: float) -> str:
    return f"{value:.8f}".rstrip("0").rstrip(".") or "0"


def _polygon_path(polygon: Iterable[tuple[float, float, float]]) -> str:
    points = list(polygon)
    if len(points) < 3:
        return ""
    return (f"M {_format(points[0][0])} {_format(points[0][1])} "
            + " ".join(f"L {_format(point[0])} {_format(point[1])}" for point in points[1:])
            + " Z")


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "-", value)


def _clip_uv(polygon, boundary: float, keep_greater: bool):
    """Clip (world point, u, v) vertices to an exact local-v boundary."""
    if not polygon:
        return []
    output = []
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        fa, fb = a[2] - boundary, b[2] - boundary
        inside_a = fa >= -1e-12 if keep_greater else fa <= 1e-12
        inside_b = fb >= -1e-12 if keep_greater else fb <= 1e-12
        if inside_a != inside_b:
            amount = fa / (fa - fb)
            point = tuple(a[0][axis] + amount * (b[0][axis] - a[0][axis])
                          for axis in range(3))
            output.append((point, a[1] + amount * (b[1] - a[1]), boundary))
        if inside_b:
            output.append(b)
    return output


def motif_triangles(spec: RibbonSpec, camera: Camera, mesh: RibbonMesh | None = None
                    ) -> tuple[RibbonArtworkTriangle, ...]:
    """Clip a three-band motif over full local u on unchanged support triangles."""
    mesh = mesh or build_mesh(spec)
    result = []
    for source, original in enumerate(mesh_triangles_uv(mesh)):
        points = tuple(vertex[0] for vertex in original)
        side = face_side(points, camera)
        bands = ((-MOTIF_OUTER_HALF_V, -MOTIF_CORE_HALF_V, MOTIF_BORDER_COLOR),
                 (-MOTIF_CORE_HALF_V, MOTIF_CORE_HALF_V, MOTIF_CORE_COLOR),
                 (MOTIF_CORE_HALF_V, MOTIF_OUTER_HALF_V, MOTIF_BORDER_COLOR))
        for low, high, fill in bands:
            clipped = _clip_uv(list(original), low, True)
            clipped = _clip_uv(clipped, high, False)
            if len(clipped) < 3:
                continue
            for index in range(1, len(clipped) - 1):
                vertices = (clipped[0], clipped[index], clipped[index + 1])
                uv = tuple((vertex[1], vertex[2]) for vertex in vertices)
                result.append(RibbonArtworkTriangle(source, tuple(vertex[0] for vertex in vertices),
                                                    uv, side, fill))
    return tuple(result)


def _faces_for_rule(spec: RibbonSpec, camera: Camera, mesh: RibbonMesh,
                    rule: str, card_bounds: tuple[float, float, float, float] | None,
                    fit: tuple[float, float, float], component: str
                    ) -> tuple[list[tuple[list[tuple[float, float, float]], str, str]],
                               list[dict[str, Any]]]:
    scale, offset_x, offset_y = fit
    source_faces = []
    motif_metadata = []
    if card_bounds is not None:
        left, bottom, right, top = card_bounds
        corners = ((left, bottom, 0.0), (right, bottom, 0.0),
                   (right, top, 0.0), (left, top, 0.0))
        for triangle in ((corners[0], corners[1], corners[2]),
                         (corners[0], corners[2], corners[3])):
            source_faces.append(([project(point, camera) for point in triangle],
                                 "#526a60", "support-card"))
    if rule in {"control", "A"}:
        source_faces.extend(ribbon_artwork_faces(spec, camera, mesh))
    elif rule == "B":
        for face in motif_triangles(spec, camera, mesh):
            source_faces.append(([project(point, camera) for point in face.points], face.fill,
                                 component))
            motif_metadata.append({"source_triangle": face.source_triangle, "side": face.side,
                                   "fill": face.fill, "uv": face.uv})
        source_faces.extend(ribbon_faces(spec, camera, mesh))
    else:
        raise ValueError("rule must be 'control', 'A', or 'B'")
    transformed = [([(offset_x + scale * point[0], offset_y - scale * point[1], point[2])
                     for point in triangle], color, name)
                   for triangle, color, name in source_faces]
    return transformed, motif_metadata


def _fit_points(mesh: RibbonMesh, camera: Camera,
                card_bounds: tuple[float, float, float, float] | None,
                width: int, height: int, margin: float
                ) -> tuple[float, float, float]:
    vertices = [project(point, camera) for row in mesh.rows for point in row]
    if card_bounds is not None:
        left, bottom, right, top = card_bounds
        vertices.extend(project(point, camera) for point in ((left, bottom, 0.0),
                         (right, bottom, 0.0), (right, top, 0.0), (left, top, 0.0)))
    min_x, max_x = min(p[0] for p in vertices), max(p[0] for p in vertices)
    min_y, max_y = min(p[1] for p in vertices), max(p[1] for p in vertices)
    scale = min((width - 2 * margin) / max(max_x - min_x, 1e-9),
                (height - 2 * margin) / max(max_y - min_y, 1e-9))
    return scale, (width - scale * (min_x + max_x)) / 2, (height + scale * (min_y + max_y)) / 2


def render_panel(spec: RibbonSpec, camera: Camera, rule: str, width: int = 420,
                 height: int = 250, prefix: str | None = None, labels: bool = False,
                 card_bounds: tuple[float, float, float, float] | None = None,
                 sampling: int = DEFAULT_SAMPLING, line_only: bool = False
                 ) -> tuple[str, dict[str, Any]]:
    """Compile one drawing with fixed control/A/B selection and generated provenance."""
    if rule not in {"control", "A", "B"}:
        raise ValueError("rule must be 'control', 'A', or 'B'")
    if isinstance(sampling, bool) or not isinstance(sampling, int) or not 12 <= sampling <= 128:
        raise ValueError("sampling must be an integer in [12, 128]")
    render_spec = dataclasses.replace(spec, segments=sampling)
    mesh = build_mesh(render_spec)
    fit = _fit_points(mesh, camera, card_bounds, width, height, 16)
    safe = _safe_name(prefix or spec.name)
    faces, motif = _faces_for_rule(render_spec, camera, mesh, rule, card_bounds, fit, spec.name)
    visible = list(visible_regions(faces))
    fill_elements = []
    for index, (path, color, component) in enumerate(visible):
        fill_elements.append(f"<!-- {escape(component)}: visible local artwork fill; support triangles are not ink -->"
                             f'<path id="{safe}-{_safe_name(component)}-fill-{index}" d="{path}" '
                             f'fill="{escape(color)}" fill-rule="nonzero" '
                             f'data-component="{escape(component)}"/>')
    selection = (select_visible_perimeter(render_spec, camera, mesh, card_bounds)
                 if rule in {"A", "B"} else None)
    stroke_shapes = _stroke_shapes(selection, fit) if selection is not None else []
    line_elements = []
    for index, (role, stroke_width, polygon, candidate_ids, source_triangle,
                boundary) in enumerate(stroke_shapes):
        path = _polygon_path(polygon)
        if not path:
            continue
        candidates = ",".join(map(str, candidate_ids))
        intent = ("foreground semantic perimeter masking a farther nonadjacent surface"
                  if role == "overlap" else "visible external semantic perimeter")
        line_elements.append(f"<!-- {spec.name}: {intent}; source support triangle {source_triangle} -->"
                             f'<path id="{safe}-perimeter-{role}-{index}" d="{path}" '
                             f'fill="{INK_COLOR}" fill-rule="nonzero" '
                             f'data-intent="{role}" data-candidates="{candidates}" '
                             f'data-source-triangle="{source_triangle}" '
                             f'data-boundary="{escape(boundary)}" '
                             f'data-stroke-width-px="{stroke_width:.1f}"/>')
    background = ('#fbfaf6' if not line_only else '#fbfaf6')
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
             f'<!-- {safe}: deterministic ribbon drawing comparison panel -->',
             f'<rect id="{safe}-panel-ground" width="{width}" height="{height}" fill="{background}"/>']
    if labels:
        parts.append(f'<text id="{safe}-panel-label" x="10" y="16" font-family="sans-serif" '
                     f'font-size="11" fill="#263b4b">{escape(spec.name)} · {escape(camera.name)} · '
                     f'{escape(rule)}</text>')
    if line_only:
        # No material fills are drawn; finite-width perimeter polygons carry their own depth masks.
        parts.extend(line_elements)
    else:
        parts.extend(fill_elements)
        parts.extend(line_elements)
    if labels:
        parts.append(f'<text id="{safe}-sampling-label" x="10" y="{height - 7}" '
                     f'font-family="sans-serif" font-size="8" fill="#526a60">'
                     f'{sampling} compiler intervals · geometry input unchanged</text>')
    parts.append('</svg>')
    coverage = {
        "candidate_count": len(selection.candidates) if selection else 2 * sampling + 2,
        "visible_span_count": len(selection.spans) if selection else 0,
        "stroke_polygon_count": len(stroke_shapes),
        "silhouette_span_count": sum(span.role == "silhouette" for span in selection.spans)
        if selection else 0,
        "overlap_span_count": sum(span.role == "overlap" for span in selection.spans)
        if selection else 0,
        "depth_tolerances": {"depth_epsilon": EPS, "tie_bias": TIE_BIAS,
                             "projected_intersection": PROJECTED_EPS,
                             "barycentric_inside": BARYCENTRIC_EPS,
                             "cut_merge_parameter": CUT_MERGE_EPS,
                             "uv_join_parameter": UV_MERGE_EPS},
        "motif_triangle_count": len(motif),
        "motif_sides": sorted({entry["side"] for entry in motif}),
        "fill_regions": len(visible),
        "sampling_override": sampling,
        "support_triangle_count": len(mesh_triangles(mesh)),
        "support_geometry_sha256": _canonical_hash(dataclasses.asdict(mesh)),
        "perimeter_spans": ([{"candidate": span.candidate_index, "boundary": span.boundary,
                               "cell": span.cell, "source_triangle": span.source_triangle,
                               "uv0": span.uv0, "uv1": span.uv1, "role": span.role,
                               "farther_triangles": span.farther_triangles,
                               "nearest_depth_gap": span.nearest_gap}
                              for span in selection.spans] if selection else []),
    }
    return "\n".join(parts), coverage


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(data: Any) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_case_plan(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load frozen source specs by repository-relative reference and verify all source hashes."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError("case plan must have schema=1 and a cases array")
    root = ROOT
    sources = data.get("sources", {})
    for name, record in sources.items():
        source_path = root / record["path"]
        if _sha256(source_path) != record["sha256"]:
            raise ValueError(f"frozen source hash changed: {record['path']}")
    loaded = []
    for item in data["cases"]:
        source = item["source"]
        source_record = sources[source["id"]]
        source_path = root / source_record["path"]
        source_data = json.loads(source_path.read_text(encoding="utf-8"))
        if source["kind"] == "case":
            found = next((case for case in source_data["cases"]
                          if case["name"] == source["case_name"]), None)
            if found is None:
                raise ValueError(f"missing frozen case {source['case_name']}")
            raw_spec = found["ribbon"]
            card = found.get("support_card")
            card_bounds = tuple(float(value) for value in card["bounds"]) if card else None
        elif source["kind"] == "spec":
            raw_spec = source_data
            card_bounds = None
        else:
            raise ValueError(f"unsupported source kind {source['kind']}")
        if _canonical_hash(raw_spec) != item["source_spec_sha256"]:
            raise ValueError(f"frozen spec hash changed for {item['name']}")
        spec = RibbonSpec.from_mapping(raw_spec)
        if item.get("depth_sign") == -1:
            spec = dataclasses.replace(spec, depth=-abs(spec.depth))
        if _canonical_hash(item["camera"]) != item["camera_sha256"]:
            raise ValueError(f"frozen camera hash changed for {item['name']}")
        camera = Camera(**item["camera"])
        camera.validate()
        loaded.append({"name": item["name"], "spec": spec, "camera": camera,
                       "card_bounds": card_bounds, "source_spec_sha256": item["source_spec_sha256"],
                       "source": source, "sampling": int(data["sampling_override"])})
    return loaded, data


def _board_svg(cases: list[dict[str, Any]], labels: bool, line_only: bool = False
               ) -> tuple[str, dict[str, Any]]:
    columns, width, margin, gap = 3, 1380, 18, 8
    panel_width, panel_height = (width - 2 * margin - 2 * gap) // columns, 255
    heading = 38 if labels else 12
    height = heading + margin + len(cases) * panel_height + (len(cases) - 1) * gap + margin
    chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
              '<!-- comparison-board: same support/camera/fit across control and the two frozen rules -->',
              f'<rect id="board-ground" width="{width}" height="{height}" fill="#e9eeea"/>']
    if labels:
        title = "Ribbon drawing rule · control / complete semantic perimeter / perimeter + local motif"
        chunks.append(f'<text x="{margin}" y="23" font-family="sans-serif" font-size="15" '
                      f'font-weight="600" fill="#263b4b">{escape(title)}</text>')
        if line_only:
            chunks.append(f'<text x="{margin}" y="34" font-family="sans-serif" font-size="8" '
                          f'fill="#526a60">Line-only: neutral paper masks preserve depth visibility; '
                          f'no fills or materials shown</text>')
    manifests = []
    column_names = ("control", "rule A · perimeter ink", "rule B · ink + local motif")
    for column, label in enumerate(column_names):
        if labels:
            x = margin + column * (panel_width + gap)
            chunks.append(f'<text x="{x + 7}" y="{heading - 6}" font-family="sans-serif" '
                          f'font-size="9" fill="#42596a">{escape(label)}</text>')
    for row, item in enumerate(cases):
        y = heading + margin + row * (panel_height + gap)
        for column, rule in enumerate(("control", "A", "B")):
            prefix = f"case-{row}-{_safe_name(item['name'])}-col-{column}"
            svg, coverage = render_panel(item["spec"], item["camera"], rule,
                                         panel_width, panel_height, prefix, False,
                                         item["card_bounds"], item["sampling"], line_only)
            inside = svg[svg.index(">") + 1:svg.rfind("</svg>")]
            x = margin + column * (panel_width + gap)
            chunks.append(f'<g id="{prefix}-group" transform="translate({x} {y})">{inside}</g>')
            manifests.append({"name": item["name"], "rule": rule, "camera": item["camera"].name,
                              "source": item["source"], "source_spec_sha256": item["source_spec_sha256"],
                              "coverage": coverage})
        if labels:
            item_label = f"{item['name']} · {item['camera'].name} · {item['sampling']} intervals"
            chunks.append(f'<text x="{margin + 6}" y="{y + 13}" font-family="sans-serif" '
                          f'font-size="9" fill="#263b4b">{escape(item_label)}</text>')
    chunks.append('</svg>')
    return "\n".join(chunks), {"panels": manifests, "line_only": line_only}


def write_board(case_plan: Path, output_dir: Path) -> list[Path]:
    """Write fixed labelled/unlabelled artwork and line-only comparisons plus manifests."""
    cases, plan = load_case_plan(case_plan)
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for suffix, labels, line_only in (("comparison-labelled", True, False),
                                      ("comparison-unlabelled", False, False),
                                      ("line-only-labelled", True, True),
                                      ("line-only-unlabelled", False, True)):
        svg, manifest = _board_svg(cases, labels, line_only)
        svg_path = output_dir / f"{suffix}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        written.append(svg_path)
        manifest_path = output_dir / f"{suffix}-manifest.json"
        manifest_path.write_text(json.dumps({"plan_sha256": _sha256(case_plan), **manifest},
                                            indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(manifest_path)
    return written


def _write_png(svg_path: Path) -> Path:
    import re as _re
    from draw import render
    match = _re.search(r'<svg[^>]+viewBox="0 0 (\d+) (\d+)"',
                       svg_path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError("generated SVG needs a pixel-sized viewBox")
    png_path = svg_path.with_suffix(".png")
    render(str(svg_path), str(png_path), size=(int(match.group(1)), int(match.group(2))))
    return png_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    one = subparsers.add_parser("render", help="render one compact ribbon spec")
    one.add_argument("spec", type=Path)
    one.add_argument("--name", default="front")
    one.add_argument("--yaw", type=float, default=0.0)
    one.add_argument("--pitch", type=float, default=0.0)
    one.add_argument("--rule", choices=("control", "A", "B"), default="B")
    one.add_argument("--sampling", type=int, default=DEFAULT_SAMPLING,
                     help="compiler-only intervals; does not edit the input spec")
    one.add_argument("--out", required=True, type=Path, help="SVG output path")
    one.add_argument("--svg-only", action="store_true")
    board = subparsers.add_parser("board", help="render the frozen exercise comparison set")
    board.add_argument("cases", type=Path)
    board.add_argument("--out-dir", required=True, type=Path)
    board.add_argument("--svg-only", action="store_true")
    args = parser.parse_args()
    if args.command == "render":
        raw = json.loads(args.spec.read_text(encoding="utf-8"))
        spec = RibbonSpec.from_mapping(raw)
        camera = Camera(args.name, args.yaw, args.pitch)
        camera.validate()
        svg, _coverage = render_panel(spec, camera, args.rule, sampling=args.sampling,
                                      labels=True, prefix=f"{spec.name}-{args.rule}")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(svg, encoding="utf-8")
        print(args.out)
        if not args.svg_only:
            print(_write_png(args.out))
    else:
        for path in write_board(args.cases, args.out_dir):
            print(path)
        if not args.svg_only:
            for svg_path in sorted(args.out_dir.glob("comparison-*.svg")) + sorted(
                    args.out_dir.glob("line-only-*.svg")):
                print(_write_png(svg_path))


if __name__ == "__main__":
    main()
