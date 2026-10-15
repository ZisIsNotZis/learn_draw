#!/usr/bin/env python3
"""Exercise25: select only camera-apparent turns from the actual cambered support mesh.

A candidate is a shared edge of two neighboring support facets only when (1) their actual 3D
normals face opposite ways to the camera, (2) the projected facets fold onto the same side of the
edge with positive-area overlap, and (3) their interpolated depth planes separate beyond the
existing renderer's finite tie band. Whole-scene depth removes hidden centerline spans. This is a
faceted approximation of a smooth apparent contour, not an exact smooth-surface differential.
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import ribbon_drawing as footprint
import ribbon_family
import ribbon_surface
import vector_visibility
from ribbon_family import Camera, RibbonSpec, camera_basis, project
from ribbon_surface import SurfaceMesh, SupportTriangle, build_surface
from vector_visibility import EPS, _positive_area_overlap, depth_plane

CASE_PATH = ROOT / ".scratch/25-apparent-contour/work/cases.json"
PLAN_PATH = ROOT / ".scratch/24-clean-support-replay/work/cases-current.json"
PINNED_SHA256 = {
    "scripts/ribbon_family.py": "015ec14ec90da5768dbcdd9486220d3971c55673f0944971ccb3a8a47662bd3e",
    "scripts/ribbon_surface.py": "5c32715a9359e3228a7cd91e2bed020f47badcc6df949f2f54e6c8ae493df2f4",
    "scripts/vector_visibility.py": "fa4c31acf8ffc622352d1feb192e4adddc7931be9cdfc046fda70b1f4d23d3fa",
    "scripts/ribbon_drawing.py": "a3569bf9492ab88a5377a25523acbd93adf32069ac02825f8b370ec45cdba2dc",
    ".scratch/24-clean-support-replay/work/cases-current.json": "793ca4c206e44d3801cb5a1c82783a5fecbffb9d16e5c1539999445ba20b6034",
}
INK_COLOR = "#253746"
INK_WIDTH_PX = 1.2
CAMBER = 0.35
U_INTERVALS = 96
V_INTERVALS = 12
WIDTH = 480
HEIGHT = 320
PROJECTED_EPS = footprint.PROJECTED_EPS
BARYCENTRIC_EPS = footprint.BARYCENTRIC_EPS
CUT_MERGE_EPS = footprint.CUT_MERGE_EPS
UV_SCALE = 10**12


@dataclass(frozen=True)
class ContourCandidate:
    """One actual shared support edge qualified as a projected facing-turn overlap."""

    index: int
    uv0: tuple[float, float]
    uv1: tuple[float, float]
    point0: tuple[float, float, float]
    point1: tuple[float, float, float]
    owners: tuple[int, int]
    facing_cosines: tuple[float, float]
    overlap_depth_delta: float


@dataclass(frozen=True)
class VisibleContourSpan:
    """A not-hidden part of one candidate; separate spans are never bridged."""

    candidate_index: int
    uv0: tuple[float, float]
    uv1: tuple[float, float]
    screen0: tuple[float, float, float]
    screen1: tuple[float, float, float]
    owners: tuple[int, int]
    t0: float
    t1: float


@dataclass(frozen=True)
class InkPatch:
    """Finite-width ink coverage clipped against the actual nearer projected surfaces."""

    candidate_indices: tuple[int, ...]
    source_faces: tuple[int, ...]
    polygon: tuple[tuple[float, float, float], ...]
    role: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins() -> dict[str, str]:
    actual = {}
    for relative, expected in PINNED_SHA256.items():
        path = ROOT / relative
        found = sha256(path)
        if found != expected:
            raise ValueError(f"frozen source hash changed: {relative}: {found}")
        actual[relative] = found
    for module, relative in ((ribbon_family, "scripts/ribbon_family.py"),
                             (ribbon_surface, "scripts/ribbon_surface.py"),
                             (vector_visibility, "scripts/vector_visibility.py"),
                             (footprint, "scripts/ribbon_drawing.py")):
        if Path(module.__file__).resolve() != (ROOT / relative).resolve():
            raise ValueError(f"wrong imported source path for {relative}: {module.__file__}")
    return actual


def load_cases() -> tuple[dict, list[dict]]:
    verify_pins()
    cases = json.loads(CASE_PATH.read_text(encoding="utf-8"))
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    rows = []
    for row in cases["rows"]:
        source = plan["cases"][row["plan_case_index"]]
        if (source["name"] != row["name"]
                or source["source_spec_sha256"] != row["source_spec_sha256"]
                or source["camera_sha256"] != row["camera_sha256"]):
            raise ValueError(f"frozen case identity changed: {row['name']}")
        spec = RibbonSpec.from_mapping(source["ribbon"])
        camera = Camera(**source["camera"])
        camera.validate()
        rows.append({**row, "spec": spec, "camera": camera, "plan_item": source})
    return cases, rows


def _uv_key(uv: tuple[float, float]) -> tuple[int, int]:
    return round(uv[0] * UV_SCALE), round(uv[1] * UV_SCALE)


def _cross2(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _face_normal(face: SupportTriangle) -> tuple[float, float, float]:
    a, b, c = face.points
    ab = tuple(b[i] - a[i] for i in range(3))
    ac = tuple(c[i] - a[i] for i in range(3))
    return (ab[1] * ac[2] - ab[2] * ac[1],
            ab[2] * ac[0] - ab[0] * ac[2],
            ab[0] * ac[1] - ab[1] * ac[0])


def _dot(a, b) -> float:
    return sum(a[i] * b[i] for i in range(3))


def _norm(a) -> float:
    return math.sqrt(_dot(a, a))


def _triangle_edges(mesh: SurfaceMesh):
    """Map exact shared UV edges to full adjacent face/vertex provenance."""
    edges = {}
    for face_id, face in enumerate(mesh.triangles):
        for local_edge in range(3):
            uv_a, uv_b = face.uv[local_edge], face.uv[(local_edge + 1) % 3]
            key_a, key_b = _uv_key(uv_a), _uv_key(uv_b)
            key = tuple(sorted((key_a, key_b)))
            edges.setdefault(key, []).append((face_id, local_edge, key_a, key_b))
    return edges


def _point_for_uv(face: SupportTriangle, key: tuple[int, int]):
    for uv, point in zip(face.uv, face.points):
        if _uv_key(uv) == key:
            return point
    raise ValueError("shared edge UV provenance does not resolve to a face vertex")


def _third_vertex(face: SupportTriangle, edge_key: tuple[tuple[int, int], tuple[int, int]]):
    for uv, point in zip(face.uv, face.points):
        if _uv_key(uv) not in edge_key:
            return uv, point
    raise ValueError("shared edge has no third face vertex")


def _overlap_polygon(a, b):
    """Convex screen-space triangle intersection used only for the depth-separation witness."""
    polygon = list(a)
    area = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(b, b[1:] + b[:1]))
    if abs(area) < EPS:
        return []
    sign = 1.0 if area > 0 else -1.0
    for p, q in zip(b, b[1:] + b[:1]):
        polygon = vector_visibility.line_clip(
            polygon,
            lambda point, p=p, q=q: sign * ((q[0] - p[0]) * (point[1] - p[1])
                                             - (q[1] - p[1]) * (point[0] - p[0])),
            True,
        )
        if len(polygon) < 3:
            return []
    return polygon


def discover_contours(mesh: SurfaceMesh, camera: Camera) -> tuple[ContourCandidate, ...]:
    """Classify real facing-transition folds, not arbitrary normal-sign changes or mesh edges."""
    view = camera_basis(camera)[2]
    projected = tuple(tuple(project(point, camera) for point in face.points)
                      for face in mesh.triangles)
    normals = tuple(_face_normal(face) for face in mesh.triangles)
    facing = tuple(_dot(normal, view) / max(_norm(normal), 1e-30) for normal in normals)
    edge_map = _triangle_edges(mesh)
    candidates = []
    for edge_key, owners in sorted(edge_map.items()):
        if len(owners) != 2:
            continue
        face_a, face_b = owners[0][0], owners[1][0]
        facing_a, facing_b = facing[face_a], facing[face_b]
        if not ((facing_a > 0.0 and facing_b < 0.0)
                or (facing_a < 0.0 and facing_b > 0.0)):
            continue
        pa, pb = (_point_for_uv(mesh.triangles[face_a], edge_key[0]),
                  _point_for_uv(mesh.triangles[face_a], edge_key[1]))
        qa, qb = project(pa, camera), project(pb, camera)
        if math.hypot(qb[0] - qa[0], qb[1] - qa[1]) <= PROJECTED_EPS:
            continue
        third_a_uv, third_a = _third_vertex(mesh.triangles[face_a], edge_key)
        third_b_uv, third_b = _third_vertex(mesh.triangles[face_b], edge_key)
        side_a = _cross2((qb[0] - qa[0], qb[1] - qa[1]),
                         (project(third_a, camera)[0] - qa[0], project(third_a, camera)[1] - qa[1]))
        side_b = _cross2((qb[0] - qa[0], qb[1] - qa[1]),
                         (project(third_b, camera)[0] - qa[0], project(third_b, camera)[1] - qa[1]))
        # Opposite-facing is necessary, not sufficient: a projected fold has both adjacent facets
        # on the same side of their shared edge and actual positive-area projected overlap.
        if side_a * side_b <= 0.0:
            continue
        tri_a, tri_b = projected[face_a], projected[face_b]
        if not _positive_area_overlap(tri_a, tri_b):
            continue
        overlap = _overlap_polygon(tri_a, tri_b)
        if len(overlap) < 3:
            continue
        centroid = (sum(p[0] for p in overlap) / len(overlap),
                    sum(p[1] for p in overlap) / len(overlap), 0.0)
        plane_a, plane_b = depth_plane(tri_a), depth_plane(tri_b)
        if plane_a is None or plane_b is None:
            continue
        delta = footprint._plane_at(plane_a, centroid) - footprint._plane_at(plane_b, centroid)
        # A projected overlap is only an occluding turn if the actual adjacent depth planes
        # separate beyond the renderer's existing EPS + first-declared tie band.
        if abs(delta) <= footprint.TIE_BIAS + EPS:
            continue
        candidates.append(ContourCandidate(
            len(candidates), tuple(float(x) / UV_SCALE for x in edge_key[0]),
            tuple(float(x) / UV_SCALE for x in edge_key[1]), tuple(pa), tuple(pb),
            (face_a, face_b), (facing_a, facing_b), delta,
        ))
    return tuple(candidates)


def _unique_cuts(values: Iterable[float]) -> tuple[float, ...]:
    ordered = sorted(min(1.0, max(0.0, value)) for value in values
                     if math.isfinite(value) and -PROJECTED_EPS <= value <= 1 + PROJECTED_EPS)
    result = []
    for value in ordered:
        if not result or value - result[-1] > CUT_MERGE_EPS:
            result.append(value)
    return tuple(result)


def _interpolate(a, b, t: float):
    return tuple(a[index] + t * (b[index] - a[index]) for index in range(3))


def _screen_bounds(triangle):
    return (min(point[0] for point in triangle), min(point[1] for point in triangle),
            max(point[0] for point in triangle), max(point[1] for point in triangle))


def _bounds_overlap(a, b):
    return (a[0] <= b[2] + EPS and b[0] <= a[2] + EPS
            and a[1] <= b[3] + EPS and b[1] <= a[3] + EPS)


def _edge_visibility_cuts(candidate: ContourCandidate, camera: Camera,
                          projected: tuple[tuple[tuple[float, float, float], ...], ...],
                          planes, bounds, owner_index: int) -> tuple[float, ...]:
    q0, q1 = project(candidate.point0, camera), project(candidate.point1, camera)
    edge_bounds = (min(q0[0], q1[0]), min(q0[1], q1[1]),
                   max(q0[0], q1[0]), max(q0[1], q1[1]))
    cuts = [0.0, 1.0]
    for other_index, triangle in enumerate(projected):
        if (other_index in candidate.owners or planes[other_index] is None
                or not _bounds_overlap(bounds[other_index], edge_bounds)):
            continue
        triangle_cuts = [0.0, 1.0]
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            triangle_cuts.extend(footprint._segment_edge_parameters(q0, q1, a, b))
        triangle_cuts = _unique_cuts(triangle_cuts)
        cuts.extend(triangle_cuts)
        bias = footprint._tie_bias_for(other_index, owner_index)
        threshold = -bias - EPS
        for lo, hi in zip(triangle_cuts, triangle_cuts[1:]):
            if hi - lo <= CUT_MERGE_EPS:
                continue
            middle = _interpolate(q0, q1, (lo + hi) / 2.0)
            weights = footprint._barycentric2(middle, triangle)
            if weights is None or min(weights) < -BARYCENTRIC_EPS:
                continue
            low_point, high_point = _interpolate(q0, q1, lo), _interpolate(q0, q1, hi)
            delta0 = low_point[2] - footprint._plane_at(planes[other_index], low_point)
            delta1 = high_point[2] - footprint._plane_at(planes[other_index], high_point)
            value0, value1 = delta0 - threshold, delta1 - threshold
            if value0 * value1 < 0.0:
                cuts.append(lo + value0 / (value0 - value1) * (hi - lo))
    return _unique_cuts(cuts)


def select_visible_contours(mesh: SurfaceMesh, camera: Camera,
                            external_triangles: tuple[tuple[tuple[float, float, float], ...], ...] = ()
                            ) -> tuple[tuple[ContourCandidate, ...], tuple[VisibleContourSpan, ...],
                                       tuple[tuple[tuple[float, float, float], ...], ...]]:
    """Generate complete geometric candidates, then reject hidden centerline intervals by depth."""
    candidates = discover_contours(mesh, camera)
    surface_triangles = tuple(tuple(face.points) for face in mesh.triangles)
    world_triangles = surface_triangles + tuple(external_triangles)
    projected = tuple(tuple(project(point, camera) for point in triangle)
                      for triangle in world_triangles)
    planes = tuple(depth_plane(triangle) for triangle in projected)
    bounds = tuple(_screen_bounds(triangle) for triangle in projected)
    spans = []
    for candidate in candidates:
        owner_index = min(candidate.owners)
        q0, q1 = project(candidate.point0, camera), project(candidate.point1, camera)
        edge_bounds = (min(q0[0], q1[0]), min(q0[1], q1[1]),
                       max(q0[0], q1[0]), max(q0[1], q1[1]))
        cuts = _edge_visibility_cuts(candidate, camera, projected, planes, bounds, owner_index)
        for t0, t1 in zip(cuts, cuts[1:]):
            if t1 - t0 <= CUT_MERGE_EPS:
                continue
            middle = _interpolate(q0, q1, (t0 + t1) / 2.0)
            hidden = False
            for other_index, triangle in enumerate(projected):
                if (other_index in candidate.owners or planes[other_index] is None
                        or not _bounds_overlap(bounds[other_index], edge_bounds)):
                    continue
                weights = footprint._barycentric2(middle, triangle)
                if weights is None or min(weights) < -BARYCENTRIC_EPS:
                    continue
                other_depth = footprint._plane_at(planes[other_index], middle)
                if footprint._is_front_occluder(other_depth, middle[2], other_index, owner_index):
                    hidden = True
                    break
            if hidden:
                continue
            uv0 = tuple(candidate.uv0[i] + t0 * (candidate.uv1[i] - candidate.uv0[i])
                        for i in range(2))
            uv1 = tuple(candidate.uv0[i] + t1 * (candidate.uv1[i] - candidate.uv0[i])
                        for i in range(2))
            spans.append(VisibleContourSpan(candidate.index, uv0, uv1,
                                            _interpolate(q0, q1, t0),
                                            _interpolate(q0, q1, t1),
                                            candidate.owners, t0, t1))
    return candidates, tuple(spans), projected


def _span_endpoint_key(span: VisibleContourSpan, at_start: bool):
    uv = span.uv0 if at_start else span.uv1
    return round(uv[0] / 1e-8), round(uv[1] / 1e-8)


def visible_face_fragments(mesh: SurfaceMesh, camera: Camera,
                           external_triangles=()):
    """Resolve actual support/card visibility once and retain each source face's ownership."""
    faces = [(tuple(project(point, camera) for point in face.points), "#ffffff", f"face:{index}")
             for index, face in enumerate(mesh.triangles)]
    faces.extend((tuple(project(point, camera) for point in triangle), "#000000",
                  f"external:{index}") for index, triangle in enumerate(external_triangles))
    visible = {}
    for polygon, _color, component in vector_visibility.visible_fragments(faces):
        if component.startswith("face:"):
            visible.setdefault(int(component.split(":", 1)[1]), []).append(tuple(polygon))
    return visible


def _clip_convex_polygon(subject, clip):
    """Intersect two convex screen-space polygons with the shared renderer halfspace clip."""
    if len(subject) < 3 or len(clip) < 3:
        return []
    area = sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(clip, clip[1:] + clip[:1]))
    if abs(area) < EPS:
        return []
    orientation = 1.0 if area > 0 else -1.0
    result = list(subject)
    for a, b in zip(clip, clip[1:] + clip[:1]):
        result = vector_visibility.line_clip(
            result, lambda p, a=a, b=b: orientation * (
                (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])), True)
        if len(result) < 3:
            return []
    return result


def _polygon_area(points) -> float:
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(points, points[1:] + points[:1]))) / 2.0


def _canvas_polygon(polygon, fit):
    scale, offset_x, offset_y = fit
    return tuple((offset_x + scale * point[0], offset_y - scale * point[1], point[2])
                 for point in polygon)


def build_ink_patches(spans: tuple[VisibleContourSpan, ...], visible_faces,
                      fit: tuple[float, float, float], width_px: float = INK_WIDTH_PX
                      ) -> tuple[InkPatch, ...]:
    """Clip the fixed-pixel ink footprint to incident faces' actual depth-visible coverage.

    The visible face fragments come directly from the pinned kernel and include every support/card
    depth test. Ink stays on the unexpanded visible support; it cannot spill through an occluder or
    outside a source face. The only line-weight choice is 1.2 canvas pixels. Hidden intervals remain
    separate; round joins require visible spans from both sides of the same original UV vertex.
    """
    patches = []

    def clip_to_visible_faces(shape, owners, candidate_ids, role):
        for owner in owners:
            for source_polygon in visible_faces.get(owner, ()):
                clipped = _clip_convex_polygon(shape, _canvas_polygon(source_polygon, fit))
                if len(clipped) < 3 or _polygon_area(clipped) <= 1e-8:
                    continue
                patches.append(InkPatch(tuple(candidate_ids), tuple(owners),
                                        tuple(tuple(point) for point in clipped), role))

    for span in spans:
        a = (fit[1] + fit[0] * span.screen0[0],
             fit[2] - fit[0] * span.screen0[1], span.screen0[2])
        b = (fit[1] + fit[0] * span.screen1[0],
             fit[2] - fit[0] * span.screen1[1], span.screen1[2])
        footprint_polygon = footprint._line_rectangle(a, b, width_px)
        if footprint_polygon:
            clip_to_visible_faces(footprint_polygon, span.owners, (span.candidate_index,),
                                  "surface-turn apparent contour")

    # A join is added only at a shared UV endpoint where both adjacent spans are visible all the
    # way to that original vertex. A hidden split has no endpoint match and can never be bridged.
    endpoints = {}
    for span in spans:
        if span.t0 <= CUT_MERGE_EPS:
            endpoints.setdefault(_span_endpoint_key(span, True), []).append((span, True))
        if span.t1 >= 1.0 - CUT_MERGE_EPS:
            endpoints.setdefault(_span_endpoint_key(span, False), []).append((span, False))
    joined = set()
    for key, meeting in endpoints.items():
        if len(meeting) < 2 or key in joined:
            continue
        joined.add(key)
        span, at_start = meeting[0]
        center3 = span.screen0 if at_start else span.screen1
        center = (fit[1] + fit[0] * center3[0], fit[2] - fit[0] * center3[1], center3[2])
        disc = footprint._join_disc(center, width_px)
        owners = tuple(sorted({face for item, _ in meeting for face in item.owners}))
        candidate_ids = tuple(sorted({item.candidate_index for item, _ in meeting}))
        clip_to_visible_faces(disc, owners, candidate_ids, "surface-turn apparent contour join")
    return tuple(patches)


def serialize_group(patches: tuple[InkPatch, ...], prefix: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]", "-", prefix)
    elements = []
    for index, patch in enumerate(patches):
        path = footprint._polygon_path(patch.polygon)
        if not path:
            continue
        candidates = ",".join(str(value) for value in patch.candidate_indices)
        faces = ",".join(str(value) for value in patch.source_faces)
        role = escape(patch.role)
        elements.append(
            f'<!-- Surface-turn apparent contour, not contact line or tessellation wireframe; '
            f'source faces {faces}, candidates {candidates}. -->'
            f'<path id="{safe}-contour-{index}" d="{path}" fill="{INK_COLOR}" '
            f'data-role="{role}" data-source-faces="{faces}" '
            f'data-candidate-edges="{candidates}"/>')
    if not elements:
        return ""
    return (f'<g id="{safe}-apparent-contour" data-line-width-px="{INK_WIDTH_PX:.1f}" '
            f'data-line-role="surface-turn apparent contour">{"".join(elements)}</g>')


def overlay_group(source_svg: str, group: str) -> str:
    if not source_svg.endswith("</svg>"):
        raise ValueError("cached control panel is not a complete SVG document")
    return source_svg[:-6] + group + "</svg>"


def remove_group(candidate_svg: str, group: str) -> str:
    suffix = group + "</svg>"
    if not group or not candidate_svg.endswith(suffix):
        raise ValueError("candidate SVG does not end with the exact appended contour group")
    return candidate_svg[:-len(suffix)] + "</svg>"


def build_case(spec: RibbonSpec, camera: Camera):
    """The only support inputs are frozen .35 camber and 96x12 sampling."""
    locked_spec = dataclasses.replace(spec, segments=U_INTERVALS)
    flat = build_surface(locked_spec, 0.0, U_INTERVALS, V_INTERVALS)
    curved = build_surface(locked_spec, CAMBER, U_INTERVALS, V_INTERVALS)
    fit = ribbon_surface._projected_fit((flat, curved), camera, WIDTH, HEIGHT)
    candidates, spans, _projected = select_visible_contours(curved, camera)
    visible_faces = visible_face_fragments(curved, camera) if spans else {}
    patches = build_ink_patches(spans, visible_faces, fit)
    return flat, curved, fit, candidates, spans, patches


def card_in_camera_plane(camera: Camera, center: tuple[float, float, float],
                         half_width: float, half_height: float, depth: float
                         ) -> tuple[tuple[float, float, float], ...]:
    """Make one real temporary camera-facing quad, triangulated without pixel-space flags."""
    right, up, view = camera_basis(camera)
    result = []
    for dx, dy in ((-half_width, -half_height), (half_width, -half_height),
                   (half_width, half_height), (-half_width, half_height)):
        result.append(tuple(center[axis] + dx * right[axis] + dy * up[axis]
                            + depth * view[axis] for axis in range(3)))
    return tuple(result)


def camera_screen_point_to_world(camera: Camera, point: tuple[float, float, float]):
    right, up, view = camera_basis(camera)
    return tuple(point[0] * right[axis] + point[1] * up[axis] + point[2] * view[axis]
                 for axis in range(3))


def camera_line_card(camera: Camera, center: tuple[float, float, float],
                     tangent: tuple[float, float], normal: tuple[float, float],
                     along: tuple[float, float], across: tuple[float, float],
                     toward_viewer: float = 0.5):
    """Test-only foreground quad placed from a selected 3D candidate's camera projection."""
    corners = []
    for a, b in ((along[0], across[0]), (along[1], across[0]),
                 (along[1], across[1]), (along[0], across[1])):
        point = (center[0] + a * tangent[0] + b * normal[0],
                 center[1] + a * tangent[1] + b * normal[1],
                 center[2] + toward_viewer)
        corners.append(camera_screen_point_to_world(camera, point))
    return tuple(corners)


def split_card(card: tuple[tuple[float, float, float], ...]):
    return ((card[0], card[1], card[2]), (card[0], card[2], card[3]))


def jsonable_candidate(candidate: ContourCandidate) -> dict:
    return {
        "candidate_index": candidate.index, "uv": [candidate.uv0, candidate.uv1],
        "points_3d": [candidate.point0, candidate.point1],
        "source_faces": candidate.owners,
        "view_cosines": candidate.facing_cosines,
        "overlap_depth_delta": candidate.overlap_depth_delta,
        "role": "faceted surface-turn apparent contour",
    }


def jsonable_span(span: VisibleContourSpan) -> dict:
    return {
        "candidate_index": span.candidate_index, "uv": [span.uv0, span.uv1],
        "screen_xyz": [span.screen0, span.screen1], "source_faces": span.owners,
        "parameter_interval": [span.t0, span.t1],
        "visibility": "centerline not hidden by any nearer actual scene triangle",
    }
