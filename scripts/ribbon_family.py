#!/usr/bin/env python3
"""Generate one continuous two-sided ribbon on a computed 3D support.

The author controls a small bounded set of shape and attachment parameters. Mesh vertices,
frames, facing colours, projected paths, and depth-visible fragments are compiler output.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape

from vector_visibility import visible_regions


RIBBON_STRIPE_HALF_V = 0.18
FRONT_STRIPE_COLOR = "#472639"
BACK_STRIPE_COLOR = "#fff1b8"
DIAGNOSTIC_SUPPORT_CARD_COLOR = "#526a60"
PANEL_ARTWORK_TOP = 56


@dataclass(frozen=True)
class RibbonSpec:
    """Ribbon dimensions are world units; angles are radians; u/v are unitless."""

    name: str
    length: float
    width: float
    tip_ratio: float = 1.0
    bend: float = 0.0
    depth: float = 0.0
    twist: float = 0.0
    family: str = "arch"
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    heading: float = 0.0
    front: str = "#e68aa4"
    back: str = "#7188bd"
    segments: int = 40

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "RibbonSpec":
        allowed = {"name", "length", "width", "tip_ratio", "bend", "depth", "twist",
                   "family", "origin", "heading", "front", "back", "segments"}
        extra = set(data) - allowed
        missing = {"name", "length", "width"} - set(data)
        if extra or missing:
            raise ValueError(f"spec fields: missing={sorted(missing)}, unknown={sorted(extra)}")
        try:
            origin = tuple(data.get("origin", (0.0, 0.0, 0.0)))
            if len(origin) != 3:
                raise ValueError("origin must contain x, y, z")
            raw_segments = data.get("segments", 40)
            if isinstance(raw_segments, bool) or not isinstance(raw_segments, int):
                raise ValueError("segments must be an integer")
            spec = cls(
                name=data["name"], length=float(data["length"]), width=float(data["width"]),
                tip_ratio=float(data.get("tip_ratio", 1.0)),
                bend=float(data.get("bend", 0.0)), depth=float(data.get("depth", 0.0)),
                twist=float(data.get("twist", 0.0)), family=data.get("family", "arch"),
                origin=tuple(float(value) for value in origin),
                heading=float(data.get("heading", 0.0)), front=data.get("front", "#e68aa4"),
                back=data.get("back", "#7188bd"), segments=raw_segments,
            )
        except (TypeError, KeyError, OverflowError) as exc:
            raise ValueError(f"invalid ribbon fields: {exc}") from exc
        spec.validate()
        return spec

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", self.name):
            raise ValueError("name must be 1-48 letters, digits, '_' or '-'")
        scalars = (self.length, self.width, self.tip_ratio, self.bend, self.depth,
                   self.twist, self.heading, *self.origin)
        if not all(math.isfinite(value) for value in scalars):
            raise ValueError("all numeric parameters must be finite")
        if not 0.25 <= self.length <= 8.0:
            raise ValueError("length must be in [0.25, 8] world units")
        if not 0.03 <= self.width <= 1.5:
            raise ValueError("width must be in [0.03, 1.5] world units")
        if not 0.15 <= self.tip_ratio <= 1.5:
            raise ValueError("tip_ratio must be in [0.15, 1.5]")
        if abs(self.bend) > 1.5 * self.length or abs(self.depth) > 1.5 * self.length:
            raise ValueError("bend and depth magnitude may not exceed 1.5 * length")
        if abs(self.twist) > 4 * math.pi:
            raise ValueError("twist magnitude must not exceed 4*pi radians")
        if abs(self.heading) > 4 * math.pi:
            raise ValueError("heading magnitude must not exceed 4*pi radians")
        if any(abs(value) > 100 for value in self.origin):
            raise ValueError("origin coordinates must be within +/-100 world units")
        if self.family not in {"arch", "s-curve", "crossback"}:
            raise ValueError("family must be 'arch', 's-curve' or 'crossback'")
        if self.family == "crossback":
            if abs(self.bend) < 0.05:
                raise ValueError("crossback requires |bend| >= 0.05 to keep its frame nonsingular")
            if abs(self.depth) < 2 * self.width:
                raise ValueError("crossback requires |depth| >= 2 * width to separate its principal "
                                 "crossing sections")
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", self.front) or not re.fullmatch(
                r"#[0-9a-fA-F]{6}", self.back):
            raise ValueError("front and back must be six-digit hex colours")
        if isinstance(self.segments, bool) or not isinstance(self.segments, int) or not 12 <= self.segments <= 128:
            raise ValueError("segments must be an integer in [12, 128]")


@dataclass(frozen=True)
class Camera:
    """Orthographic camera rotation; yaw/pitch are degrees."""

    name: str
    yaw: float
    pitch: float

    def validate(self) -> None:
        if not isinstance(self.name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", self.name):
            raise ValueError("camera name must be a short filename-safe label")
        if not math.isfinite(self.yaw) or abs(self.yaw) > 180:
            raise ValueError("camera yaw must be in [-180, 180] degrees")
        if not math.isfinite(self.pitch) or abs(self.pitch) > 80:
            raise ValueError("camera pitch must be in [-80, 80] degrees")


def centerline(spec: RibbonSpec, u: float) -> tuple[float, float, float]:
    """Computed support centre at local u in [0,1]; all families share one attached start."""
    if not 0 <= u <= 1:
        raise ValueError("u must lie in [0,1]")
    envelope = math.sin(math.pi * u) ** 2
    if spec.family == "arch":
        along, side = spec.length * u, spec.bend * envelope
    elif spec.family == "s-curve":
        along = spec.length * u
        side = spec.bend * math.sin(2 * math.pi * u) * envelope
    else:
        # The squared side envelope eases the finite-width band through the reverse run, avoiding
        # the local width fold made by the broader arch while retaining its projected crossing.
        along = spec.length * (u + 0.32 * math.sin(2 * math.pi * u))
        side = spec.bend * envelope * envelope
    depth = spec.depth * math.sin(2 * math.pi * u) * envelope
    ch, sh = math.cos(spec.heading), math.sin(spec.heading)
    x, y, z = spec.origin
    return (x + along * ch - side * sh,
            y + along * sh + side * ch,
            z + depth)


def _unit(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(sum(value * value for value in vector))
    if length < 1e-10 or not math.isfinite(length):
        raise ValueError("ribbon centreline has a singular tangent")
    return tuple(value / length for value in vector)


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]
           ) -> tuple[float, float, float]:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _add_scaled(a: tuple[float, float, float], b: tuple[float, float, float], amount: float
                ) -> tuple[float, float, float]:
    return tuple(x + amount * y for x, y in zip(a, b))


def _rotate(vector: tuple[float, float, float], axis: tuple[float, float, float], angle: float
            ) -> tuple[float, float, float]:
    cosine, sine = math.cos(angle), math.sin(angle)
    cross = _cross(axis, vector)
    parallel = _dot(axis, vector) * (1 - cosine)
    return tuple(vector[i] * cosine + cross[i] * sine + axis[i] * parallel for i in range(3))


def _tangent(spec: RibbonSpec, u: float) -> tuple[float, float, float]:
    envelope = math.sin(math.pi * u) ** 2
    envelope_derivative = math.pi * math.sin(2 * math.pi * u)
    if spec.family == "arch":
        along_derivative = spec.length
        side_derivative = spec.bend * envelope_derivative
    elif spec.family == "s-curve":
        along_derivative = spec.length
        side_derivative = spec.bend * (2 * math.pi * math.cos(2 * math.pi * u) * envelope
                                       + math.sin(2 * math.pi * u) * envelope_derivative)
    else:
        along_derivative = spec.length * (1 + 0.64 * math.pi * math.cos(2 * math.pi * u))
        side_derivative = 2 * spec.bend * envelope * envelope_derivative
    depth_derivative = spec.depth * (2 * math.pi * math.cos(2 * math.pi * u) * envelope
                                     + math.sin(2 * math.pi * u) * envelope_derivative)
    ch, sh = math.cos(spec.heading), math.sin(spec.heading)
    return _unit((along_derivative * ch - side_derivative * sh,
                  along_derivative * sh + side_derivative * ch, depth_derivative))


def _transport(side: tuple[float, float, float], old_tangent: tuple[float, float, float],
               new_tangent: tuple[float, float, float]
               ) -> tuple[float, float, float]:
    axis = _cross(old_tangent, new_tangent)
    sine = math.sqrt(_dot(axis, axis))
    cosine = max(-1.0, min(1.0, _dot(old_tangent, new_tangent)))
    if sine < 1e-10:
        moved = _rotate(side, side, math.pi) if cosine < 0 else side
    else:
        moved = _rotate(side, tuple(value / sine for value in axis), math.atan2(sine, cosine))
    # Remove accumulated floating error while preserving the transported orientation.
    projected = tuple(moved[i] - _dot(moved, new_tangent) * new_tangent[i]
                      for i in range(3))
    return _unit(projected)


@dataclass(frozen=True)
class RibbonArtworkTriangle:
    """One exact subtriangle of a support face, with local UV and authored fill provenance."""

    source_triangle: int
    points: tuple[tuple[float, float, float], ...]
    uv: tuple[tuple[float, float], ...]
    side: str
    fill: str


@dataclass(frozen=True)
class RibbonMesh:
    """Generated vertices share boundary tuples; no authored contour is stored."""

    stations: tuple[float, ...]
    centers: tuple[tuple[float, float, float], ...]
    tangents: tuple[tuple[float, float, float], ...]
    width_axes: tuple[tuple[float, float, float], ...]
    rows: tuple[tuple[tuple[float, float, float], tuple[float, float, float]], ...]


def build_mesh(spec: RibbonSpec, segments: int | None = None) -> RibbonMesh:
    spec.validate()
    count = spec.segments if segments is None else segments
    if isinstance(count, bool) or not isinstance(count, int) or not 4 <= count <= 256:
        raise ValueError("mesh segments must be an integer in [4, 256]")
    stations = tuple(i / count for i in range(count + 1))
    centers = tuple(centerline(spec, u) for u in stations)
    tangents = tuple(_tangent(spec, u) for u in stations)
    heading_side = (-math.sin(spec.heading), math.cos(spec.heading), 0.0)
    first = _unit(tuple(heading_side[i] - _dot(heading_side, tangents[0]) * tangents[0][i]
                        for i in range(3)))
    untwisted = [first]
    for index in range(1, len(tangents)):
        untwisted.append(_transport(untwisted[-1], tangents[index - 1], tangents[index]))
    axes = []
    rows = []
    for u, center, tangent, side in zip(stations, centers, tangents, untwisted):
        normal = _unit(_cross(tangent, side))
        angle = spec.twist * u
        width_axis = _unit(tuple(side[i] * math.cos(angle) + normal[i] * math.sin(angle)
                                 for i in range(3)))
        width = 0.5 * spec.width * (1 + (spec.tip_ratio - 1) * u)
        axes.append(width_axis)
        rows.append((
            tuple(center[i] - width * width_axis[i] for i in range(3)),
            tuple(center[i] + width * width_axis[i] for i in range(3)),
        ))
    return RibbonMesh(stations, centers, tangents, tuple(axes), tuple(rows))


def camera_basis(camera: Camera) -> tuple[tuple[float, float, float], ...]:
    camera.validate()
    yaw, pitch = math.radians(camera.yaw), math.radians(camera.pitch)
    right = (math.cos(yaw), 0.0, math.sin(yaw))
    toward_viewer = (-math.sin(yaw) * math.cos(pitch), math.sin(pitch),
                     math.cos(yaw) * math.cos(pitch))
    up = _cross(toward_viewer, right)
    return right, up, toward_viewer


def project(point: tuple[float, float, float], camera: Camera
            ) -> tuple[float, float, float]:
    right, up, toward_viewer = camera_basis(camera)
    return _dot(point, right), _dot(point, up), _dot(point, toward_viewer)


def face_side(triangle: tuple[tuple[float, float, float], ...], camera: Camera) -> str:
    """Choose front/back paint from consistent surface winding and camera-facing normal."""
    normal = _cross(tuple(triangle[1][i] - triangle[0][i] for i in range(3)),
                    tuple(triangle[2][i] - triangle[0][i] for i in range(3)))
    return "front" if _dot(normal, camera_basis(camera)[2]) > 0 else "back"


def mesh_triangles(mesh: RibbonMesh
                   ) -> list[tuple[tuple[float, float, float], ...]]:
    """Two support triangles per interval; adjacent intervals reuse the same boundary vertices."""
    triangles = []
    for index in range(len(mesh.stations) - 1):
        low0, high0 = mesh.rows[index]
        low1, high1 = mesh.rows[index + 1]
        triangles.extend(((low0, low1, high1), (low0, high1, high0)))
    return triangles


def mesh_triangles_uv(mesh: RibbonMesh
                      ) -> list[tuple[tuple[tuple[float, float, float], float, float], ...]]:
    """Support triangles paired with the same continuous local (u,v) coordinates."""
    triangles = []
    for index in range(len(mesh.stations) - 1):
        u0, u1 = mesh.stations[index:index + 2]
        low0, high0 = mesh.rows[index]
        low1, high1 = mesh.rows[index + 1]
        triangles.extend((
            ((low0, u0, -1.0), (low1, u1, -1.0), (high1, u1, 1.0)),
            ((low0, u0, -1.0), (high1, u1, 1.0), (high0, u0, 1.0)),
        ))
    return triangles


def _clip_local_v(polygon, boundary: float, keep_greater: bool):
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
            u = a[1] + amount * (b[1] - a[1])
            output.append((point, u, boundary))
        if inside_b:
            output.append(b)
    return output


def _fan_local_polygon(polygon):
    if len(polygon) < 3:
        return
    first = polygon[0]
    for index in range(1, len(polygon) - 1):
        triangle = (first, polygon[index], polygon[index + 1])
        (u0, v0), (u1, v1), (u2, v2) = ((vertex[1], vertex[2]) for vertex in triangle)
        area2 = (u1 - u0) * (v2 - v0) - (u2 - u0) * (v1 - v0)
        if abs(area2) > 1e-12:
            yield triangle


def ribbon_artwork_triangles(spec: RibbonSpec, camera: Camera,
                             mesh: RibbonMesh | None = None) -> list[RibbonArtworkTriangle]:
    """Split each support face by one full-length local-v stripe; geometry stays on its source face."""
    mesh = mesh or build_mesh(spec)
    artwork = []
    for source, local_triangle in enumerate(mesh_triangles_uv(mesh)):
        support_triangle = tuple(vertex[0] for vertex in local_triangle)
        side = face_side(support_triangle, camera)
        stripe_fill = FRONT_STRIPE_COLOR if side == "front" else BACK_STRIPE_COLOR
        middle = _clip_local_v(list(local_triangle), -RIBBON_STRIPE_HALF_V, True)
        middle = _clip_local_v(middle, RIBBON_STRIPE_HALF_V, False)
        for triangle in _fan_local_polygon(middle):
            artwork.append(RibbonArtworkTriangle(
                source_triangle=source,
                points=tuple(vertex[0] for vertex in triangle),
                uv=tuple((vertex[1], vertex[2]) for vertex in triangle),
                side=side,
                fill=stripe_fill,
            ))
    return artwork


def ribbon_artwork_faces(spec: RibbonSpec, camera: Camera, mesh: RibbonMesh | None = None
                         ) -> list[tuple[list[tuple[float, float, float]], str, str]]:
    mesh = mesh or build_mesh(spec)
    # Stripe triangles are exact UV subdivisions of the original support, declared before its
    # unchanged base faces so the existing coplanar tie rule lets the authored artwork overlay win.
    stripe = [([project(point, camera) for point in face.points], face.fill, spec.name)
              for face in ribbon_artwork_triangles(spec, camera, mesh)]
    return stripe + ribbon_faces(spec, camera, mesh)


def ribbon_faces(spec: RibbonSpec, camera: Camera, mesh: RibbonMesh | None = None
                 ) -> list[tuple[list[tuple[float, float, float]], str, str]]:
    mesh = mesh or build_mesh(spec)
    faces = []
    for triangle in mesh_triangles(mesh):
        side = face_side(triangle, camera)
        color = spec.front if side == "front" else spec.back
        faces.append(([project(point, camera) for point in triangle], color, spec.name))
    return faces


def card_faces(bounds: tuple[float, float, float, float], camera: Camera,
               component: str = "support-card", color: str = "#d8e4da"
               ) -> list[tuple[list[tuple[float, float, float]], str, str]]:
    """Two triangles construct one opaque XY support card at z=0; no edge strokes."""
    left, bottom, right, top = bounds
    if not all(math.isfinite(value) for value in bounds) or left >= right or bottom >= top:
        raise ValueError("support card bounds must be finite left,bottom,right,top")
    corners = ((left, bottom, 0.0), (right, bottom, 0.0),
               (right, top, 0.0), (left, top, 0.0))
    return [([project(point, camera) for point in tri], color, component)
            for tri in ((corners[0], corners[1], corners[2]),
                        (corners[0], corners[2], corners[3]))]


def _format(value: float) -> str:
    return f"{value:.9f}".rstrip("0").rstrip(".") or "0"


def _svg_path_elements(faces: Iterable[tuple[list[tuple[float, float, float]], str, str]],
                       width: int, height: int, margin: float, component_prefix: str,
                       extra_points: Iterable[tuple[float, float, float]] = ()) -> str:
    vertices = [point for triangle, _, _ in faces for point in triangle]
    vertices.extend(extra_points)
    if not vertices:
        return ""
    min_x, max_x = min(p[0] for p in vertices), max(p[0] for p in vertices)
    min_y, max_y = min(p[1] for p in vertices), max(p[1] for p in vertices)
    span_x, span_y = max(max_x - min_x, 1e-6), max(max_y - min_y, 1e-6)
    scale = min((width - 2 * margin) / span_x, (height - 2 * margin) / span_y)
    offset_x = (width - scale * (min_x + max_x)) / 2
    offset_y = (height + scale * (min_y + max_y)) / 2
    transformed = []
    for tri, color, name in faces:
        transformed.append(([(offset_x + p[0] * scale, offset_y - p[1] * scale, p[2])
                             for p in tri], color, name))
    paths = []
    for index, (path, color, name) in enumerate(visible_regions(transformed)):
        # Filled semantic regions only. Triangle boundaries are support tessellation, never ink.
        safe = re.sub(r"[^A-Za-z0-9_-]", "-", name)
        if name == "support-card":
            intent = "opaque support surface fill, hidden by closer depth"
        elif color == FRONT_STRIPE_COLOR:
            intent = "local longitudinal stripe on the front-facing artwork"
        elif color == BACK_STRIPE_COLOR:
            intent = "local longitudinal stripe on the back-facing artwork"
        else:
            intent = "base artwork fill selected by winding-based side facing"
        paths.append(f'<!-- {escape(name)}: {intent}; tessellation is not line art -->'
                     f'<path id="{component_prefix}-{safe}-fill-{index}" d="{path}" '
                     f'fill="{escape(color)}" fill-rule="nonzero" '
                     f'data-component="{escape(name)}"/>')
    return "\n".join(paths)


def _frame_svg(spec: RibbonSpec, camera: Camera, width: int, height: int,
               include_card: bool, card_bounds: tuple[float, float, float, float] | None,
               marker: bool, prefix: str) -> str:
    mesh = build_mesh(spec)
    faces = ribbon_artwork_faces(spec, camera, mesh)
    if include_card and card_bounds is not None:
        faces = card_faces(card_bounds, camera, color=DIAGNOSTIC_SUPPORT_CARD_COLOR) + faces
    card_fit_points = []
    if card_bounds is not None:
        left, bottom, right, top = card_bounds
        card_fit_points = [project(point, camera) for point in
                           ((left, bottom, 0), (right, bottom, 0), (right, top, 0), (left, top, 0))]
    elements = _svg_path_elements(faces, width, height, 18, prefix, card_fit_points)
    if marker:
        # Diagnostic attachment pin: intentionally not part of the ribbon artwork or mesh.
        projected = project(spec.origin, camera)
        all_points = [point for tri, _, _ in faces for point in tri] + card_fit_points
        min_x, max_x = min(p[0] for p in all_points), max(p[0] for p in all_points)
        min_y, max_y = min(p[1] for p in all_points), max(p[1] for p in all_points)
        span_x, span_y = max(max_x - min_x, 1e-6), max(max_y - min_y, 1e-6)
        scale = min((width - 36) / span_x, (height - 36) / span_y)
        px = (width - scale * (min_x + max_x)) / 2 + scale * projected[0]
        py = (height + scale * (min_y + max_y)) / 2 - scale * projected[1]
        elements += (f'<!-- Diagnostic attachment at local (u=0,v=0). -->'
                     f'<circle cx="{_format(px)}" cy="{_format(py)}" r="4.5" '
                     f'fill="#fffdf4" stroke="#284b68" stroke-width="1.5"/>')
    return elements


def _panel_content(spec: RibbonSpec, camera: Camera, width: int, height: int,
                   include_card: bool, card_bounds: tuple[float, float, float, float] | None,
                   marker: bool, prefix: str) -> str:
    return _frame_svg(spec, camera, width, height, include_card, card_bounds, marker, prefix)


def _wrap_caption(text: str, limit: int = 52) -> list[str]:
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > limit:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def make_panel(case: dict[str, Any], camera: Camera, width: int = 380, height: int = 300,
               labels: bool = True) -> str:
    spec = RibbonSpec.from_mapping(case["ribbon"])
    support = case.get("support_card")
    card_bounds = tuple(float(value) for value in support["bounds"]) if support else None
    name = case["name"]
    title = f'{case["number"]}. {name} — {camera.name}'
    safe = re.sub(r"[^A-Za-z0-9_-]", "-", name)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
             '<!-- panel-background: neutral diagnostic ground behind the projected component -->',
             f'<rect id="{safe}-{camera.name}-panel-ground" width="{width}" height="{height}" '
             f'fill="#f4f5ef"/>',
             '<!-- panel-frame: diagnostic separation only, not an artwork contour -->',
             f'<rect id="{safe}-{camera.name}-panel-frame" x="1" y="1" '
             f'width="{width - 2}" height="{height - 2}" rx="8" '
             f'fill="none" stroke="#c7d1cd" stroke-width="1"/>']
    if labels:
        parts.append(f'<text x="12" y="20" font-family="sans-serif" font-size="14" '
                     f'font-weight="600" fill="#263b4b">{escape(title)}</text>')
        caption_lines = _wrap_caption(case["purpose"])
        tspans = "".join(f'<tspan x="12" y="{36 + 11 * index}">{escape(line)}</tspan>'
                         for index, line in enumerate(caption_lines))
        parts.append(f'<text id="{safe}-{camera.name}-purpose" font-family="sans-serif" '
                     f'font-size="10" fill="#42596a">{tspans}</text>')
    area_y = PANEL_ARTWORK_TOP
    area_h = height - area_y - 8
    if support:
        gap = 8
        half = (width - 24 - gap) // 2
        left_x, right_x = 12, 12 + half + gap
        for x, show_card, caption, suffix in (
                (left_x, False, "full strip", "whole"),
                (right_x, True, "with support card", "card")):
            clip_id = f"clip-{safe}-{camera.name}-{suffix}"
            parts.append(f'<clipPath id="{clip_id}"><rect x="0" y="0" '
                         f'width="{half}" height="{area_h}"/></clipPath>')
            content = _panel_content(spec, camera, half, area_h, show_card, card_bounds,
                                     labels, f"{safe}-{camera.name}-{suffix}")
            parts.append(f'<g transform="translate({x} {area_y})" clip-path="url(#{clip_id})">'
                         f'<!-- {safe}-{camera.name}-{suffix}-ground: neutral view field -->'
                         f'<rect id="{safe}-{camera.name}-{suffix}-ground" width="{half}" '
                         f'height="{area_h}" fill="#eef2ec"/>{content}</g>')
            if labels:
                parts.append(f'<text x="{x + half / 2:.1f}" y="{height - 8}" '
                             f'text-anchor="middle" font-family="sans-serif" font-size="10" '
                             f'fill="#42596a">{caption}</text>')
    else:
        clip_id = f"clip-{safe}-{camera.name}"
        parts.append(f'<clipPath id="{clip_id}"><rect x="0" y="0" '
                     f'width="{width}" height="{area_h}"/></clipPath>')
        content = _panel_content(spec, camera, width, area_h, False, None,
                                 labels, f"{safe}-{camera.name}")
        parts.append(f'<g transform="translate(0 {area_y})" clip-path="url(#{clip_id})">'
                     f'<!-- {safe}-{camera.name}-ground: neutral view field -->'
                     f'<rect id="{safe}-{camera.name}-ground" width="{width}" '
                     f'height="{area_h}" fill="#eef2ec"/>{content}</g>')
    parts.append("</svg>")
    return "\n".join(parts)


def make_board(cases: list[dict[str, Any]], cameras: list[Camera], labels: bool) -> str:
    width, margin, gutter = 1200, 20, 10
    columns, rows = 3, len(cases) * len(cameras) // 3
    panel_w = (width - 2 * margin - (columns - 1) * gutter) // columns
    panel_h = 300
    height = 40 + 2 * margin + rows * panel_h + (rows - 1) * gutter
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
             '<!-- board-background: neutral paper for the component-family diagnostic -->',
             f'<rect id="board-background" width="{width}" height="{height}" fill="#e8eeea"/>']
    if labels:
        parts.append('<text x="20" y="25" font-family="sans-serif" font-size="17" '
                     'font-weight="600" fill="#263b4b">Ribbon family · same local component, '
                     'two fixed cameras</text>')
    index = 0
    for camera in cameras:
        for case in cases:
            col, row = index % columns, index // columns
            x, y = margin + col * (panel_w + gutter), 40 + margin + row * (panel_h + gutter)
            panel = make_panel(case, camera, panel_w, panel_h, labels)
            contents = panel[panel.index(">") + 1:panel.rfind("</svg>")]
            parts.append(f'<g transform="translate({x} {y})">{contents}</g>')
            index += 1
    parts.append("</svg>")
    return "\n".join(parts)


def load_case_file(path: Path) -> tuple[list[dict[str, Any]], list[Camera]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema", "cameras", "cases"} or data["schema"] != 1:
        raise ValueError("case file must be an object with schema=1, cameras, and cases only")
    camera_rows = data["cameras"]
    if not isinstance(camera_rows, list) or len(camera_rows) < 2:
        raise ValueError("cameras must be a list with at least two named camera poses")
    cameras = []
    for index, item in enumerate(camera_rows):
        if not isinstance(item, dict) or set(item) != {"name", "yaw", "pitch"}:
            raise ValueError(f"camera {index + 1} must contain name, yaw, and pitch only")
        if not isinstance(item["name"], str):
            raise ValueError(f"camera {index + 1} name must be text")
        try:
            camera = Camera(item["name"], float(item["yaw"]), float(item["pitch"]))
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"camera {index + 1} has invalid numeric angles") from exc
        camera.validate()
        cameras.append(camera)
    if len({camera.name for camera in cameras}) != len(cameras):
        raise ValueError("camera names must be unique to keep output files and SVG IDs distinct")
    cases = data["cases"]
    if not isinstance(cases, list) or len(cases) != 6:
        raise ValueError("preselected case file must contain six cases")
    if any(not isinstance(case, dict) for case in cases):
        raise ValueError("each preselected case must be an object")
    case_names = [case.get("name") for case in cases]
    if any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", name)
           for name in case_names):
        raise ValueError("case names must be 1-48 filename-safe letters, digits, '_' or '-'")
    if len(set(case_names)) != 6:
        raise ValueError("preselected case names must be unique")
    for index, case in enumerate(cases, 1):
        if case.get("number") != index or not case.get("purpose"):
            raise ValueError("cases need fixed 1-6 numbering and a diagnostic purpose")
        RibbonSpec.from_mapping(case["ribbon"])
        support = case.get("support_card")
        if support:
            bounds = tuple(float(value) for value in support["bounds"])
            card_faces(bounds, cameras[0])  # validate box geometry
    if len(cameras) < 2:
        raise ValueError("at least two fixed camera poses are required")
    return cases, cameras


def _write_svg_and_png(svg: str, destination: Path, render_png: bool) -> tuple[Path, Path | None]:
    from draw import render

    svg_path = destination.with_suffix(".svg")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg, encoding="utf-8")
    png_path = destination.with_suffix(".png") if render_png else None
    if png_path is not None:
        # The existing deterministic Chromium renderer is the sole raster backend.
        import re as _re
        match = _re.search(r'<svg[^>]+viewBox="0 0 (\d+) (\d+)"', svg)
        if not match:
            raise ValueError("generated SVG is missing a pixel-sized viewBox")
        render(str(svg_path), str(png_path), size=(int(match.group(1)), int(match.group(2))))
    return svg_path, png_path


def render_single(spec_path: Path, output: Path, camera: Camera, render_png: bool = True
                  ) -> tuple[Path, Path | None]:
    data = json.loads(spec_path.read_text(encoding="utf-8"))
    spec = RibbonSpec.from_mapping(data)
    case = {"number": 1, "name": spec.name, "purpose": "single continuous ribbon",
            "ribbon": data}
    panel = make_panel(case, camera, 720, 540)
    return _write_svg_and_png(panel, output, render_png)


def render_board(case_path: Path, output_dir: Path, render_png: bool = True
                 ) -> list[Path]:
    cases, cameras = load_case_file(case_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for camera in cameras:
        for case in cases:
            prefix = output_dir / "views" / f'{case["name"]}-{camera.name}'
            svg_path, png_path = _write_svg_and_png(make_panel(case, camera), prefix, render_png)
            written.append(svg_path)
            if png_path:
                written.append(png_path)
    for filename, labels in (("learning-board", True), ("learning-board-unlabelled", False)):
        svg_path, png_path = _write_svg_and_png(make_board(cases, cameras, labels),
                                                output_dir / filename, render_png)
        written.append(svg_path)
        if png_path:
            written.append(png_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    single = subparsers.add_parser("render", help="render one compact ribbon spec")
    single.add_argument("spec", type=Path)
    single.add_argument("--name", default="front", help="camera filename label")
    single.add_argument("--yaw", type=float, default=0.0, help="camera yaw in degrees")
    single.add_argument("--pitch", type=float, default=0.0, help="camera pitch in degrees")
    single.add_argument("-o", "--output", required=True, type=Path,
                        help="output basename or .svg path; writes PNG beside SVG")
    board = subparsers.add_parser("board", help="render the frozen six-case/two-camera board")
    board.add_argument("cases", type=Path)
    board.add_argument("--out-dir", required=True, type=Path)
    board.add_argument("--svg-only", action="store_true", help="skip Chromium PNG output")
    args = parser.parse_args()
    if args.command == "render":
        camera = Camera(args.name, args.yaw, args.pitch)
        camera.validate()
        svg_path, png_path = render_single(args.spec, args.output, camera)
        print(svg_path)
        print(png_path)
    else:
        for path in render_board(args.cases, args.out_dir, not args.svg_only):
            print(path)


if __name__ == "__main__":
    main()
