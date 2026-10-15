#!/usr/bin/env python3
"""Build and render one bounded center-route return bend on a continuous 2D ribbon strip.

The geometry API accepts only semantic route/frame parameters. Mesh vertices, material-side choice,
UV stripe faces, projection, and opaque depth-visible paths are compiler output.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable
from xml.sax.saxutils import escape

from vector_visibility import visible_regions

Point3 = tuple[float, float, float]
Point2 = tuple[float, float]
Triangle3 = tuple[Point3, Point3, Point3]
UVTriangle = tuple[Point2, Point2, Point2]

MAX_KERNEL_FACES = 256
QUADRATURE_STEPS = 256
STRIPE_HALF_V = 0.18
PANEL_WIDTH = 420
PANEL_HEIGHT = 320
PANEL_SCALE = 90.0
PANEL_MARGIN = 20.0
FRONT_FILL = "#e68aa4"
BACK_FILL = "#7188bd"
FRONT_STRIPE = "#472639"
BACK_STRIPE = "#fff1b8"
CARD_FILL = "#526a60"


@dataclass(frozen=True)
class ReturnSpec:
    """Small semantic support parameters; dimensions are world units and angles radians."""

    name: str
    root: Point3
    root_tangent: Point3
    bend_normal: Point3
    length: float
    width: float
    tip_ratio: float
    alpha: float

    def validate(self) -> tuple[Point3, Point3, Point3]:
        if not isinstance(self.name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", self.name):
            raise ValueError("name must be 1-48 letters, digits, '_' or '-'")
        root = _vector(self.root, "root")
        ex_raw = _vector(self.root_tangent, "root_tangent")
        w_raw = _vector(self.bend_normal, "bend_normal")
        if any(abs(value) > 10.0 for value in root):
            raise ValueError("root coordinates must be in [-10,10]")
        length, width, tip, alpha = self.length, self.width, self.tip_ratio, self.alpha
        if any(isinstance(value, bool) or not isinstance(value, (int, float))
               or not math.isfinite(value) for value in (length, width, tip, alpha)):
            raise ValueError("dimensions and angle must be finite numeric values")
        if not 1.0 <= length <= 3.0:
            raise ValueError("length must be in [1,3] world units")
        if not 0.1 <= width <= 0.6:
            raise ValueError("width must be in [0.1,0.6] world units")
        if not 0.5 <= tip <= 1.0:
            raise ValueError("tip_ratio must be in [0.5,1]")
        if not 0.0 <= alpha <= math.pi:
            raise ValueError("alpha must be in [0,pi] radians")
        ex = _unit(ex_raw, "root_tangent")
        w = _unit(w_raw, "bend_normal")
        if abs(_dot(ex, w)) > 1e-10:
            raise ValueError("root tangent and bend normal must be orthogonal")
        ed = _unit(_cross(w, ex), "derived bend direction")
        if (abs(_dot(ex, ed)) > 1e-10 or abs(_dot(ed, w)) > 1e-10
                or _distance(_cross(ex, ed), w) > 1e-10):
            raise ValueError("derived support frame must be orthonormal and right-handed")
        return root, ex, w

    @classmethod
    def from_mapping(cls, data: dict) -> "ReturnSpec":
        expected = {"name", "root", "root_tangent", "bend_normal", "length", "width",
                    "tip_ratio", "alpha"}
        if not isinstance(data, dict) or set(data) != expected:
            missing = sorted(expected - set(data)) if isinstance(data, dict) else sorted(expected)
            extra = sorted(set(data) - expected) if isinstance(data, dict) else []
            raise ValueError(f"spec fields: missing={missing}, unknown={extra}")
        try:
            if any(isinstance(data[key], bool) for key in ("length", "width", "tip_ratio", "alpha")):
                raise ValueError("boolean dimensions are not valid numeric inputs")
            spec = cls(data["name"], tuple(data["root"]), tuple(data["root_tangent"]),
                       tuple(data["bend_normal"]), float(data["length"]),
                       float(data["width"]), float(data["tip_ratio"]), float(data["alpha"]))
        except (TypeError, OverflowError) as exc:
            raise ValueError(f"invalid return spec: {exc}") from exc
        spec.validate()
        return spec


@dataclass(frozen=True)
class ReturnFace:
    """One nondegenerate support triangle paired with its source-local UV coordinates."""

    source_index: int
    u_cell: int
    v_cell: int
    points: Triangle3
    uv: UVTriangle


@dataclass(frozen=True)
class ReturnMesh:
    """Compiler output for the whole connected local UV strip."""

    spec: ReturnSpec
    stations: tuple[float, ...]
    rows: tuple[tuple[Point3, ...], ...]
    faces: tuple[ReturnFace, ...]
    bend_direction: Point3


@dataclass(frozen=True)
class OrthographicCamera:
    """Explicit right-handed screen basis; D points toward the viewer."""

    name: str
    right: Point3
    up: Point3
    toward_viewer: Point3

    def validate(self) -> None:
        if not isinstance(self.name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", self.name):
            raise ValueError("camera name must be a short filename-safe label")
        r = _unit(_vector(self.right, "camera right"), "camera right")
        u = _unit(_vector(self.up, "camera up"), "camera up")
        d = _unit(_vector(self.toward_viewer, "camera direction"), "camera direction")
        if (abs(_dot(r, u)) > 1e-10 or abs(_dot(r, d)) > 1e-10
                or abs(_dot(u, d)) > 1e-10 or _distance(_cross(r, u), d) > 1e-10):
            raise ValueError("camera basis must be unit, orthogonal and right-handed (R x U = D)")


def build_return_mesh(spec: ReturnSpec, u_samples: int, v_samples: int) -> ReturnMesh:
    """Generate the single connected return strip from a bounded route and fixed width frame."""
    if not isinstance(spec, ReturnSpec):
        raise TypeError("spec must be a ReturnSpec")
    root, ex, w = spec.validate()
    if (isinstance(u_samples, bool) or not isinstance(u_samples, int)
            or not 16 <= u_samples <= 32):
        raise ValueError("u_samples must be an integer in [16,32]")
    if (isinstance(v_samples, bool) or not isinstance(v_samples, int)
            or not 2 <= v_samples <= 4):
        raise ValueError("v_samples must be an integer in [2,4]")
    if 2 * u_samples * v_samples > MAX_KERNEL_FACES:
        raise ValueError("support sampling exceeds the 256-face input cap")
    ed = _unit(_cross(w, ex), "derived bend direction")
    stations = tuple(i / u_samples for i in range(u_samples + 1))
    levels = _v_levels(v_samples)
    centers = tuple(_center(spec, root, ex, ed, u) for u in stations)
    rows = tuple(tuple(_add(center, _scale(w, 0.5 * _width(spec, u) * v))
                       for v in levels)
                 for u, center in zip(stations, centers))
    faces = []
    for i in range(u_samples):
        for j in range(v_samples):
            uv00 = (stations[i], levels[j])
            uv10 = (stations[i + 1], levels[j])
            uv11 = (stations[i + 1], levels[j + 1])
            uv01 = (stations[i], levels[j + 1])
            p00, p10 = rows[i][j], rows[i + 1][j]
            p11, p01 = rows[i + 1][j + 1], rows[i][j + 1]
            for uv, points in (((uv00, uv10, uv11), (p00, p10, p11)),
                               ((uv00, uv11, uv01), (p00, p11, p01))):
                if not all(math.isfinite(value) for point in points for value in point):
                    raise ValueError("generated support contains a non-finite point")
                if _length(_cross(_sub(points[1], points[0]), _sub(points[2], points[0]))) <= 1e-12:
                    raise ValueError("generated support contains a singular face")
                faces.append(ReturnFace(len(faces), i, j, points, uv))
    if len(faces) != 2 * u_samples * v_samples or len(faces) > MAX_KERNEL_FACES:
        raise ValueError("generated support face count violates the bounded contract")
    return ReturnMesh(spec, stations, rows, tuple(faces), ed)


def material_width(spec: ReturnSpec, u: float) -> float:
    spec.validate()
    _check_u(u)
    return _width(spec, u)


def projected_width(spec: ReturnSpec, camera: OrthographicCamera, u: float) -> float:
    """Return orthographic projected width without changing material width."""
    camera.validate()
    root, ex, w = spec.validate()
    del root, ex
    _check_u(u)
    return _width(spec, u) * math.sqrt(max(0.0, 1.0 - _dot(camera.toward_viewer, w) ** 2))


def return_art_faces(mesh: ReturnMesh, camera: OrthographicCamera,
                     with_card: bool = False) -> list[tuple[list[tuple[float, float, float]], str, str]]:
    """Compile one local UV stripe and two-sided fill to opaque projected triangle inputs."""
    camera.validate()
    art = []
    for face in mesh.faces:
        normal = _cross(_sub(face.points[1], face.points[0]),
                        _sub(face.points[2], face.points[0]))
        side = "front" if _dot(normal, camera.toward_viewer) > 0.0 else "back"
        stripe_color = FRONT_STRIPE if side == "front" else BACK_STRIPE
        polygon = [(face.points[i], face.uv[i]) for i in range(3)]
        stripe = _clip_uv_v(_clip_uv_v(polygon, -STRIPE_HALF_V, True),
                            STRIPE_HALF_V, False)
        for triangle in _fan_uv(stripe):
            art.append((_project_triangle(tuple(item[0] for item in triangle), camera),
                        stripe_color, f"return-strip:{side}:stripe"))
    for face in mesh.faces:
        normal = _cross(_sub(face.points[1], face.points[0]),
                        _sub(face.points[2], face.points[0]))
        side = "front" if _dot(normal, camera.toward_viewer) > 0.0 else "back"
        color = FRONT_FILL if side == "front" else BACK_FILL
        art.append((_project_triangle(face.points, camera), color, f"return-strip:{side}:body"))
    if with_card:
        card = _card_triangles(mesh.spec)
        art.extend((_project_triangle(triangle, camera), CARD_FILL, "root-attached-card")
                   for triangle in card)
    if len(art) > MAX_KERNEL_FACES:
        raise ValueError(f"submitted artwork/card faces {len(art)} exceed the 256-face cap")
    return art


def card_triangles(spec: ReturnSpec) -> tuple[Triangle3, Triangle3]:
    """Fixed card rectangle in root-local (e_x,e_d,W), opaque and attached to the strip root."""
    spec.validate()
    return _card_triangles(spec)


def project_point(point: Point3, camera: OrthographicCamera) -> tuple[float, float, float]:
    camera.validate()
    return (_dot(point, camera.right), _dot(point, camera.up),
            _dot(point, camera.toward_viewer))


def panel_svg(mesh: ReturnMesh, camera: OrthographicCamera, with_card: bool = False,
              width: int = PANEL_WIDTH, height: int = PANEL_HEIGHT) -> str:
    """Render depth-visible flat local artwork to a complete deterministic SVG panel."""
    if isinstance(width, bool) or not isinstance(width, int) or width < 100:
        raise ValueError("panel width must be an integer >=100")
    if isinstance(height, bool) or not isinstance(height, int) or height < 100:
        raise ValueError("panel height must be an integer >=100")
    art_faces = return_art_faces(mesh, camera, with_card)
    all_world = [point for face in mesh.faces for point in face.points]
    if with_card:
        all_world.extend(point for triangle in card_triangles(mesh.spec) for point in triangle)
    projected = [project_point(point, camera) for point in all_world]
    low_x, high_x = min(p[0] for p in projected), max(p[0] for p in projected)
    low_y, high_y = min(p[1] for p in projected), max(p[1] for p in projected)
    center_x, center_y = (low_x + high_x) / 2.0, (low_y + high_y) / 2.0
    scale = min(PANEL_SCALE, (width - 2 * PANEL_MARGIN) / max(high_x - low_x, 1e-12),
                (height - 2 * PANEL_MARGIN) / max(high_y - low_y, 1e-12))
    offset_x, offset_y = width / 2.0 - scale * center_x, height / 2.0 + scale * center_y
    transformed = []
    for triangle, color, component in art_faces:
        xy_depth = [(offset_x + scale * point[0], offset_y - scale * point[1], point[2])
                    for point in triangle]
        transformed.append((xy_depth, color, component))
    paths = []
    for index, (path, color, component) in enumerate(visible_regions(transformed)):
        paths.append(f'<!-- {escape(component)}: depth-visible local artwork fill; tessellation is not ink -->'
                     f'<path id="return-{index}" d="{path}" fill="{color}" '
                     'fill-rule="nonzero"/>')
    if not paths:
        raise ValueError("depth renderer produced a blank panel")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
            '<!-- Full-frame return-bend panel; no stroke or painter-order occlusion override. -->'
            '<rect id="panel-background" width="100%" height="100%" fill="#edf1ef"/>'
            '<g id="return-support-and-local-art">' + ''.join(paths) + '</g></svg>')


def _center(spec: ReturnSpec, root: Point3, ex: Point3, ed: Point3, u: float) -> Point3:
    if u == 0.0:
        return root
    n = QUADRATURE_STEPS
    h = u / n
    sums = [0.0, 0.0, 0.0]
    for i in range(n + 1):
        t = i * h
        weight = 1 if i in (0, n) else (4 if i % 2 else 2)
        q = 3.0 * t * t - 2.0 * t * t * t
        theta = spec.alpha * q
        tangent = _add(_scale(ex, math.cos(theta)), _scale(ed, math.sin(theta)))
        for axis in range(3):
            sums[axis] += weight * tangent[axis]
    return _add(root, _scale(tuple(value * h / 3.0 for value in sums), spec.length))


def _card_triangles(spec: ReturnSpec) -> tuple[Triangle3, Triangle3]:
    root, ex, w = spec.validate()
    ed = _unit(_cross(w, ex), "derived bend direction")
    # This fixed root-local transform places an actual opaque support card in front of the near return.
    def corner(along: float, across: float) -> Point3:
        return _add(_add(_add(root, _scale(ex, along)), _scale(ed, 0.9)), _scale(w, across))
    low_root, high_root = corner(0.3, -0.34), corner(1.05, -0.34)
    high_tip, low_tip = corner(1.05, 0.34), corner(0.3, 0.34)
    return ((low_root, high_root, high_tip), (low_root, high_tip, low_tip))


def _clip_uv_v(polygon, boundary: float, keep_greater: bool):
    if not polygon:
        return []
    output = []
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        fa, fb = a[1][1] - boundary, b[1][1] - boundary
        inside_a = fa >= -1e-12 if keep_greater else fa <= 1e-12
        inside_b = fb >= -1e-12 if keep_greater else fb <= 1e-12
        if inside_a != inside_b:
            amount = fa / (fa - fb)
            world = tuple(a[0][axis] + amount * (b[0][axis] - a[0][axis])
                          for axis in range(3))
            uv = (a[1][0] + amount * (b[1][0] - a[1][0]), boundary)
            output.append((world, uv))
        if inside_b:
            output.append(b)
    return output


def _fan_uv(polygon):
    if len(polygon) < 3:
        return
    for i in range(1, len(polygon) - 1):
        tri = (polygon[0], polygon[i], polygon[i + 1])
        normal = _cross(_sub(tri[1][0], tri[0][0]), _sub(tri[2][0], tri[0][0]))
        if _length(normal) > 1e-14:
            yield tri


def _project_triangle(triangle: Iterable[Point3], camera: OrthographicCamera):
    return [project_point(point, camera) for point in triangle]


def _width(spec: ReturnSpec, u: float) -> float:
    return spec.width * (1.0 - (1.0 - spec.tip_ratio) * u)


def _v_levels(count: int) -> tuple[float, ...]:
    return tuple(-1.0 + 2.0 * i / count for i in range(count + 1))


def _check_u(u: float) -> None:
    if isinstance(u, bool) or not isinstance(u, (int, float)) or not math.isfinite(u) or not 0 <= u <= 1:
        raise ValueError("u must be finite and in [0,1]")


def _vector(value, label: str) -> Point3:
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise ValueError(f"{label} must contain three finite coordinates")
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
        raise ValueError(f"{label} must contain three finite numeric coordinates")
    result = tuple(float(item) for item in value)
    if not all(math.isfinite(item) for item in result):
        raise ValueError(f"{label} must contain three finite coordinates")
    return result


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _scale(a, amount):
    return tuple(value * amount for value in a)


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _length(a):
    return math.sqrt(_dot(a, a))


def _unit(a, label):
    length = _length(a)
    if not math.isfinite(length) or length <= 1e-12:
        raise ValueError(f"{label} frame is singular")
    return _scale(a, 1.0 / length)


def _distance(a, b):
    return _length(_sub(a, b))


def _v_levels_for_faces(count: int):
    return _v_levels(count)
