#!/usr/bin/env python3
"""Build bounded S1a perimeter-cue and twist-tessellation comparison boards.

This exercise-only probe selects a semantic ribbon perimeter cue from projected geometry and
interpolated depth. It does not alter the support, its visibility, the production renderer, or the
frozen case matrix.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from ribbon_family import (Camera, RibbonMesh, RibbonSpec, _cross, _dot, _unit, build_mesh,
                           camera_basis, centerline, mesh_triangles, project,
                           ribbon_artwork_faces)
from vector_visibility import EPS, depth_plane, visible_regions


CASES_PATH = ROOT / ".scratch/19-ribbon-family/work/cases.json"
DIAGNOSTIC_CUE_COLOR = "#263b4b"
DIAGNOSTIC_CUE_WIDTH = 1.7
PROJECTED_EPS = 1e-9
BARYCENTRIC_EPS = 1e-8


@dataclass(frozen=True)
class PerimeterCandidate:
    """One tessellated segment of an authored local-domain perimeter curve."""

    index: int
    boundary: str
    cell: int
    uv0: tuple[float, float]
    uv1: tuple[float, float]
    point0: tuple[float, float, float]
    point1: tuple[float, float, float]
    source_triangle: int


@dataclass(frozen=True)
class SelectedInterval:
    """Visible portion of a perimeter segment that covers a farther nonadjacent face."""

    candidate_index: int
    boundary: str
    cell: int
    t0: float
    t1: float
    uv0: tuple[float, float]
    uv1: tuple[float, float]
    screen0: tuple[float, float, float]
    screen1: tuple[float, float, float]
    masked_triangles: tuple[int, ...]
    minimum_depth_gap: float


@dataclass(frozen=True)
class CuePath:
    """Connected generated semantic-perimeter stroke and its local source provenance."""

    boundary: str
    uv: tuple[tuple[float, float], ...]
    screen: tuple[tuple[float, float, float], ...]
    source_cells: tuple[int, ...]
    masked_triangles: tuple[int, ...]
    minimum_depth_gap: float


@dataclass(frozen=True)
class CueSelection:
    candidates: tuple[PerimeterCandidate, ...]
    intervals: tuple[SelectedInterval, ...]
    paths: tuple[CuePath, ...]
    support_triangles: tuple[tuple[tuple[float, float, float], ...], ...]
    projected_triangles: tuple[tuple[tuple[float, float, float], ...], ...]
    camera: Camera


def load_frozen_cases() -> tuple[list[dict[str, Any]], list[Camera]]:
    """Use the unchanged six-case file; callers copy specs only for explicit depth/tess controls."""
    from ribbon_family import load_case_file
    return load_case_file(CASES_PATH)


def perimeter_candidates(mesh: RibbonMesh) -> tuple[PerimeterCandidate, ...]:
    """Enumerate both complete lengthwise UV boundaries and both end caps once."""
    candidates = []
    intervals = len(mesh.stations) - 1
    for cell in range(intervals):
        u0, u1 = mesh.stations[cell], mesh.stations[cell + 1]
        low0, high0 = mesh.rows[cell]
        low1, high1 = mesh.rows[cell + 1]
        candidates.append(PerimeterCandidate(
            len(candidates), "v=-1", cell, (u0, -1.0), (u1, -1.0), low0, low1, 2 * cell))
        candidates.append(PerimeterCandidate(
            len(candidates), "v=+1", cell, (u0, 1.0), (u1, 1.0), high0, high1, 2 * cell + 1))
    candidates.append(PerimeterCandidate(
        len(candidates), "u=0", 0, (0.0, -1.0), (0.0, 1.0),
        mesh.rows[0][0], mesh.rows[0][1], 1))
    last = intervals - 1
    candidates.append(PerimeterCandidate(
        len(candidates), "u=1", last, (1.0, -1.0), (1.0, 1.0),
        mesh.rows[-1][0], mesh.rows[-1][1], 2 * last))
    return tuple(candidates)


def _cross2(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _sub2(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return a[0] - b[0], a[1] - b[1]


def _barycentric2(point: tuple[float, float],
                  triangle: tuple[tuple[float, float, float], ...]
                  ) -> tuple[float, float, float] | None:
    a, b, c = triangle
    ab = (b[0] - a[0], b[1] - a[1])
    ac = (c[0] - a[0], c[1] - a[1])
    ap = (point[0] - a[0], point[1] - a[1])
    determinant = _cross2(ab, ac)
    if abs(determinant) < PROJECTED_EPS:
        return None
    wb = _cross2(ap, ac) / determinant
    wc = _cross2(ab, ap) / determinant
    return 1 - wb - wc, wb, wc


def _segment_edge_parameters(q0: tuple[float, float, float],
                             q1: tuple[float, float, float],
                             a: tuple[float, float, float],
                             b: tuple[float, float, float]) -> tuple[float, ...]:
    """Return projected line parameters at an actual triangle-edge crossing."""
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
        return tuple(((p[0] - q0[0]) * r[0] + (p[1] - q0[1]) * r[1]) / rr
                     for p in (a, b))
    t = _cross2(delta, s) / denominator
    edge_t = _cross2(delta, r) / denominator
    if -PROJECTED_EPS <= t <= 1 + PROJECTED_EPS and -PROJECTED_EPS <= edge_t <= 1 + PROJECTED_EPS:
        return (min(1.0, max(0.0, t)),)
    return ()


def _depth_plane_value(plane: tuple[float, float, float],
                       point: tuple[float, float, float]) -> float:
    return plane[0] * point[0] + plane[1] * point[1] + plane[2]


def _split_parameters(candidate: PerimeterCandidate, camera: Camera,
                      projected: tuple[tuple[float, float, float], ...],
                      planes: tuple[tuple[float, float, float] | None, ...],
                      cells: tuple[int, ...]) -> tuple[float, ...]:
    q0, q1 = project(candidate.point0, camera), project(candidate.point1, camera)
    cuts = [0.0, 1.0]
    for index, triangle in enumerate(projected):
        if abs(cells[index] - candidate.cell) <= 1 or planes[index] is None:
            continue
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            cuts.extend(_segment_edge_parameters(q0, q1, a, b))
        d0 = q0[2] - _depth_plane_value(planes[index], q0)
        d1 = q1[2] - _depth_plane_value(planes[index], q1)
        if abs(d0) <= EPS:
            cuts.append(0.0)
        if abs(d1) <= EPS:
            cuts.append(1.0)
        if d0 * d1 < 0:
            cuts.append(d0 / (d0 - d1))
    ordered = sorted(min(1.0, max(0.0, value)) for value in cuts
                     if math.isfinite(value) and -PROJECTED_EPS <= value <= 1 + PROJECTED_EPS)
    unique = []
    for value in ordered:
        if not unique or value - unique[-1] > 1e-8:
            unique.append(value)
    return tuple(unique)


def select_perimeter_cues(spec: RibbonSpec, camera: Camera, mesh: RibbonMesh | None = None
                          ) -> CueSelection:
    """Select only visible perimeter intervals over nonadjacent surfaces at lesser depth.

    Candidate segments cover the full local boundary. They are split at projected triangle-edge
    crossings and at roots of their actual linear depth difference. The mesh-cell exclusion below
    omits the candidate's own cell and its two vertex-sharing neighbours; it is provenance/topology,
    not an authored visibility interval.
    """
    mesh = mesh or build_mesh(spec)
    candidates = perimeter_candidates(mesh)
    support = tuple(mesh_triangles(mesh))
    projected = tuple(tuple(project(point, camera) for point in triangle) for triangle in support)
    planes = tuple(depth_plane(triangle) for triangle in projected)
    cells = tuple(index // 2 for index in range(len(support)))
    spans = []
    for candidate in candidates:
        q0, q1 = project(candidate.point0, camera), project(candidate.point1, camera)
        if math.hypot(q1[0] - q0[0], q1[1] - q0[1]) < PROJECTED_EPS:
            continue
        cuts = _split_parameters(candidate, camera, projected, planes, cells)
        for t0, t1 in zip(cuts, cuts[1:]):
            if t1 - t0 <= 1e-7:
                continue
            t = (t0 + t1) / 2
            screen = tuple(q0[axis] + t * (q1[axis] - q0[axis]) for axis in range(3))
            masked = []
            hidden = False
            for index, triangle in enumerate(projected):
                if abs(cells[index] - candidate.cell) <= 1 or planes[index] is None:
                    continue
                weights = _barycentric2(screen, triangle)
                if weights is None or min(weights) <= BARYCENTRIC_EPS:
                    continue
                other_depth = _depth_plane_value(planes[index], screen)
                if other_depth > screen[2] + EPS:
                    hidden = True
                    break
                if other_depth < screen[2] - EPS:
                    masked.append((index, screen[2] - other_depth))
            if hidden or not masked:
                continue
            uv0 = tuple(candidate.uv0[k] + t0 * (candidate.uv1[k] - candidate.uv0[k])
                        for k in range(2))
            uv1 = tuple(candidate.uv0[k] + t1 * (candidate.uv1[k] - candidate.uv0[k])
                        for k in range(2))
            spans.append(SelectedInterval(
                candidate_index=candidate.index, boundary=candidate.boundary,
                cell=candidate.cell, t0=t0, t1=t1, uv0=uv0, uv1=uv1,
                screen0=tuple(q0[k] + t0 * (q1[k] - q0[k]) for k in range(3)),
                screen1=tuple(q0[k] + t1 * (q1[k] - q0[k]) for k in range(3)),
                masked_triangles=tuple(sorted(index for index, _gap in masked)),
                minimum_depth_gap=min(gap for _index, gap in masked),
            ))
    return CueSelection(candidates, tuple(spans), _merge_spans(spans), support, projected, camera)


def _merge_spans(spans: list[SelectedInterval]) -> tuple[CuePath, ...]:
    chains = []
    for boundary in ("v=-1", "v=+1", "u=0", "u=1"):
        ordered = sorted((span for span in spans if span.boundary == boundary),
                         key=lambda span: (span.candidate_index, span.t0))
        current = None
        for span in ordered:
            can_join = (current is not None
                        and (current["last_cell"] == span.cell
                             or current["last_cell"] + 1 == span.cell)
                        and math.dist(current["screen"][-1][:2], span.screen0[:2]) <= 1e-6
                        and math.dist(current["uv"][-1], span.uv0) <= 1e-8)
            if not can_join:
                if current is not None:
                    chains.append(_cue_path(current))
                current = {"boundary": span.boundary, "screen": [span.screen0, span.screen1],
                           "uv": [span.uv0, span.uv1], "cells": [span.cell],
                           "far": set(span.masked_triangles), "minimum_gap": span.minimum_depth_gap,
                           "last_cell": span.cell}
            else:
                current["screen"].append(span.screen1)
                current["uv"].append(span.uv1)
                if current["cells"][-1] != span.cell:
                    current["cells"].append(span.cell)
                current["far"].update(span.masked_triangles)
                current["minimum_gap"] = min(current["minimum_gap"], span.minimum_depth_gap)
                current["last_cell"] = span.cell
        if current is not None:
            chains.append(_cue_path(current))
    return tuple(chains)


def _cue_path(data: dict[str, Any]) -> CuePath:
    return CuePath(data["boundary"], tuple(data["uv"]), tuple(data["screen"]),
                   tuple(data["cells"]), tuple(sorted(data["far"])), data["minimum_gap"])


def _facing_value(mesh: RibbonMesh, camera: Camera, u: float) -> float:
    index = min(len(mesh.stations) - 2, max(0, int(u * (len(mesh.stations) - 1))))
    amount = u * (len(mesh.stations) - 1) - index
    tangent = _unit(tuple(mesh.tangents[index][axis]
                          + amount * (mesh.tangents[index + 1][axis] - mesh.tangents[index][axis])
                          for axis in range(3)))
    width_axis = tuple(mesh.width_axes[index][axis]
                       + amount * (mesh.width_axes[index + 1][axis] - mesh.width_axes[index][axis])
                       for axis in range(3))
    width_axis = _unit(tuple(width_axis[axis] - _dot(width_axis, tangent) * tangent[axis]
                             for axis in range(3)))
    return _dot(_cross(tangent, width_axis), camera_basis(camera)[2])


def facing_zero(mesh: RibbonMesh, camera: Camera) -> float:
    values = [_facing_value(mesh, camera, u) for u in mesh.stations]
    brackets = [(a, b) for a, b in zip(mesh.stations, mesh.stations[1:])
                if _facing_value(mesh, camera, a) * _facing_value(mesh, camera, b) < 0]
    if not brackets:
        raise ValueError("twist comparison has no sampled facing-sign transition")
    lo, hi = brackets[0]
    sign_lo = _facing_value(mesh, camera, lo)
    for _ in range(48):
        middle = (lo + hi) / 2
        if _facing_value(mesh, camera, middle) * sign_lo > 0:
            lo = middle
        else:
            hi = middle
    return (lo + hi) / 2


def _fit(meshes: tuple[RibbonMesh, ...], camera: Camera, width: int, height: int,
         margin: float) -> tuple[float, float, float]:
    vertices = [project(point, camera) for mesh in meshes for row in mesh.rows for point in row]
    min_x, max_x = min(point[0] for point in vertices), max(point[0] for point in vertices)
    min_y, max_y = min(point[1] for point in vertices), max(point[1] for point in vertices)
    scale = min((width - 2 * margin) / max(max_x - min_x, 1e-9),
                (height - 2 * margin) / max(max_y - min_y, 1e-9))
    return scale, (width - scale * (min_x + max_x)) / 2, (height + scale * (min_y + max_y)) / 2


def _projected_fill(spec: RibbonSpec, camera: Camera, mesh: RibbonMesh,
                    width: int, height: int, prefix: str,
                    fit: tuple[float, float, float]) -> str:
    scale, offset_x, offset_y = fit
    faces = ribbon_artwork_faces(spec, camera, mesh)
    transformed = [([(offset_x + scale * p[0], offset_y - scale * p[1], p[2])
                    for p in triangle], color, component)
                   for triangle, color, component in faces]
    elements = []
    for index, (path, color, component) in enumerate(visible_regions(transformed)):
        elements.append(f'<!-- {escape(component)}: filled local ribbon artwork region -->'
                        f'<path id="{prefix}-fill-{index}" d="{path}" fill="{escape(color)}" '
                        f'fill-rule="nonzero" data-component="{escape(component)}"/>')
    return "\n".join(elements)


def _projected_cues(paths: tuple[CuePath, ...], width: int, height: int,
                    prefix: str, fit: tuple[float, float, float]) -> str:
    scale, offset_x, offset_y = fit
    output = []
    for index, cue in enumerate(paths):
        commands = [f'M {_fmt(offset_x + scale * point[0])} {_fmt(offset_y - scale * point[1])}'
                    for point in cue.screen[:1]]
        commands.extend(f'L {_fmt(offset_x + scale * point[0])} {_fmt(offset_y - scale * point[1])}'
                        for point in cue.screen[1:])
        source_start, source_end = cue.uv[0], cue.uv[-1]
        cells = ",".join(str(cell) for cell in cue.source_cells)
        output.append(f'<!-- {prefix}: diagnostic occlusion contour on semantic perimeter '
                      f'{escape(cue.boundary)}; source u {source_start[0]:.6f}..{source_end[0]:.6f}; '
                      f'masks nonadjacent faces {escape(",".join(map(str, cue.masked_triangles)))} -->'
                      f'<path id="{prefix}-cue-{index}" d="{" ".join(commands)}" fill="none" '
                      f'stroke="{DIAGNOSTIC_CUE_COLOR}" stroke-width="{_fmt(DIAGNOSTIC_CUE_WIDTH)}" '
                      f'stroke-linecap="butt" data-probe-cue="semantic-perimeter" '
                      f'data-boundary="{escape(cue.boundary)}" data-cells="{cells}" '
                      f'data-min-depth-gap="{_fmt(cue.minimum_depth_gap)}"/>')
    return "\n".join(output)


def _cue_summary(paths: tuple[CuePath, ...]) -> str:
    if not paths:
        return "selector: no visible perimeter masks a nonadjacent farther face"
    summaries = []
    for boundary in ("v=-1", "v=+1", "u=0", "u=1"):
        matching = [path for path in paths if path.boundary == boundary]
        if not matching:
            continue
        u_values = [point[0] for path in matching for point in path.uv]
        face_count = len({face for path in matching for face in path.masked_triangles})
        summaries.append(f"{boundary} u={min(u_values):.3f}..{max(u_values):.3f} masks {face_count}")
    return "generated perimeter cue: " + "; ".join(summaries)


def _fmt(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def _panel(spec: RibbonSpec, camera: Camera, width: int, height: int, title: str,
           subtitle: str, mesh: RibbonMesh, cue_paths: tuple[CuePath, ...], prefix: str,
           labels: bool, fit_meshes: tuple[RibbonMesh, ...] | None = None) -> str:
    fit = _fit(fit_meshes or (mesh,), camera, width, height - 36, 18)
    fill = _projected_fill(spec, camera, mesh, width, height - 36, prefix, fit)
    cue = _projected_cues(cue_paths, width, height - 36, prefix, fit)
    content = (fill + "\n" + cue) if cue else fill
    title_line = (f'<text x="12" y="16" font-size="12" font-family="sans-serif" '
                  f'fill="#263b4b">{escape(title)}</text>'
                  f'<text x="12" y="29" font-size="8" font-family="sans-serif" '
                  f'fill="#42596a">{escape(subtitle)}</text>' if labels else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<rect width="{width}" height="{height}" fill="#eef2ec"/>'
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
            f'fill="none" stroke="#c7d1cd" stroke-width="1"/>{title_line}'
            f'<g transform="translate(0 36)">{content}</g></svg>')


def _geometry_hash(mesh: RibbonMesh) -> str:
    canonical = json.dumps(dataclasses.asdict(mesh), sort_keys=True, separators=(",", ":"),
                           allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _board_svg(cases, cameras, labels: bool) -> str:
    case_by_name = {case["name"]: case for case in cases}
    front, oblique = cameras
    crossing_spec = RibbonSpec.from_mapping(case_by_name["awkward-crossing"]["ribbon"])
    teaching_spec = RibbonSpec.from_mapping(case_by_name["teaching-arch"]["ribbon"])
    twist_spec = RibbonSpec.from_mapping(case_by_name["twisted-two-sided"]["ribbon"])
    reversed_spec = dataclasses.replace(crossing_spec, depth=-abs(crossing_spec.depth))

    crossing_mesh = build_mesh(crossing_spec)
    crossing_reversed_mesh = build_mesh(reversed_spec)
    crossing_cues = select_perimeter_cues(crossing_spec, front, crossing_mesh)
    reversed_cues = select_perimeter_cues(reversed_spec, front, crossing_reversed_mesh)
    teaching_mesh = build_mesh(teaching_spec)
    teaching_cues = select_perimeter_cues(teaching_spec, front, teaching_mesh)
    twist40 = build_mesh(dataclasses.replace(twist_spec, segments=40))
    twist128 = build_mesh(dataclasses.replace(twist_spec, segments=128))
    twist_root40 = facing_zero(twist40, oblique)
    twist_root128 = facing_zero(twist128, oblique)

    rows = [
        (("Frozen crossing · fill + stripe", "same frozen support and front camera",
          crossing_spec, front, crossing_mesh, ()),
         ("Frozen crossing · generated perimeter cue", _cue_summary(crossing_cues.paths),
          crossing_spec, front, crossing_mesh, crossing_cues.paths)),
        (("Teaching arch · fill + stripe", "noncrossing negative control",
          teaching_spec, front, teaching_mesh, ()),
         ("Teaching arch · selector returns no cue", _cue_summary(teaching_cues.paths),
          teaching_spec, front, teaching_mesh, teaching_cues.paths)),
        (("Depth-sign reversal · fill + stripe", "additional control, not a frozen case",
          reversed_spec, front, crossing_reversed_mesh, ()),
         ("Depth-sign reversal · recomputed cue", _cue_summary(reversed_cues.paths),
          reversed_spec, front, crossing_reversed_mesh, reversed_cues.paths)),
        ((f"Twist · 40 intervals", f"facing zero at u={twist_root40:.5f}; same oblique camera",
          dataclasses.replace(twist_spec, segments=40), oblique, twist40, ()),
         (f"Twist · 128 intervals", f"facing zero at u={twist_root128:.5f}; same oblique camera",
          dataclasses.replace(twist_spec, segments=128), oblique, twist128, ())),
    ]
    width, margin, gap, panel_w, panel_h = 1200, 20, 14, 573, 250
    height = 44 + 2 * margin + 4 * panel_h + 3 * gap
    title = ('Occlusion probe · generated semantic perimeter only' if labels else '')
    chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
              '<rect width="100%" height="100%" fill="#e8eeea"/>']
    if labels:
        chunks.append(f'<text x="20" y="26" font-family="sans-serif" font-size="16" '
                      f'fill="#263b4b">{escape(title)}</text>')
    cue_manifest = []
    for row_index, row in enumerate(rows):
        for column, panel_data in enumerate(row):
            caption, subtitle, spec, camera, mesh, cues = panel_data
            prefix = f"probe-r{row_index}-c{column}"
            x = margin + column * (panel_w + gap)
            y = 44 + margin + row_index * (panel_h + gap)
            fit_meshes = ((crossing_mesh, crossing_reversed_mesh) if row_index == 2 else
                          (twist40, twist128) if row_index == 3 else None)
            panel = _panel(spec, camera, panel_w, panel_h, caption, subtitle, mesh, cues,
                           prefix, labels, fit_meshes)
            inside = panel[panel.index(">") + 1:panel.rfind("</svg>")]
            chunks.append(f'<g transform="translate({x} {y})">{inside}</g>')
            cue_manifest.append({"panel": prefix, "title": caption, "camera": camera.name,
                                 "segments": spec.segments,
                                 "selected_cues": [asdict(cue) for cue in cues]})
    chunks.append("</svg>")
    source_paths = {
        "ribbon_family.py": SCRIPTS / "ribbon_family.py",
        "vector_visibility.py": SCRIPTS / "vector_visibility.py",
        "cases.json": CASES_PATH,
        "occlusion_probe.py": Path(__file__).resolve(),
        "test_occlusion_probe.py": Path(__file__).with_name("test_occlusion_probe.py"),
    }
    return "\n".join(chunks), cue_manifest, {
        "source_sha256": {name: _file_hash(path) for name, path in source_paths.items()
                          if path.exists()},
        "geometry_sha256": {
            "frozen_crossing_48": _geometry_hash(crossing_mesh),
            "depth_reversed_48": _geometry_hash(crossing_reversed_mesh),
            "teaching_arch_40": _geometry_hash(teaching_mesh),
            "twist_40": _geometry_hash(twist40),
            "twist_128": _geometry_hash(twist128),
        },
        "twist_facing_zero_40": twist_root40,
        "twist_facing_zero_128": twist_root128,
        "crossing_selected_paths": len(crossing_cues.paths),
        "teaching_selected_paths": len(teaching_cues.paths),
        "reversed_selected_paths": len(reversed_cues.paths),
    }


def write_probe(output_dir: Path, render_png: bool = True) -> list[Path]:
    from draw import render
    cases, cameras = load_frozen_cases()
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, labels in (("occlusion-probe-unlabelled", False),
                             ("occlusion-probe-labelled", True)):
        svg, manifest, summary = _board_svg(cases, cameras, labels)
        svg_path = output_dir / f"{filename}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        written.append(svg_path)
        if render_png:
            png_path = output_dir / f"{filename}.png"
            render(str(svg_path), str(png_path), size=(1200, 44 + 40 + 4 * 250 + 3 * 14))
            written.append(png_path)
        manifest_path = output_dir / f"{filename}-manifest.json"
        manifest_path.write_text(json.dumps({"summary": summary, "panels": manifest},
                                            indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(manifest_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / ".scratch/19-ribbon-family/evidence/probe")
    parser.add_argument("--svg-only", action="store_true")
    args = parser.parse_args()
    for path in write_probe(args.out_dir, render_png=not args.svg_only):
        print(path)


if __name__ == "__main__":
    main()
