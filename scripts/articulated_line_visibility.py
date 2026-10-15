"""Local adapter utilities for depth-clipped authored semantic lines and compound SVG fills."""

from __future__ import annotations

import math
import re
from collections.abc import Callable

from scripts import ribbon_drawing as _line_probe
from scripts.vector_visibility import EPS, depth_plane


_PATH_TOKEN = re.compile(r"[MLZ]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?")


def transform_compound_path(path_data: str, transform: Callable[[float, float], tuple[float, float]]) -> str:
    """Transform the backend's absolute M/L/Z paths without joining separate subpaths."""
    tokens = _PATH_TOKEN.findall(path_data)
    residue = _PATH_TOKEN.sub("", path_data)
    if residue.strip(" \t\r\n,"):
        raise ValueError("compound path contains unsupported SVG commands or tokens")
    if not tokens:
        raise ValueError("compound path is empty")
    output: list[str] = []
    index = 0
    command: str | None = None
    have_move = False
    while index < len(tokens):
        token = tokens[index]
        if token in {"M", "L", "Z"}:
            command = token
            index += 1
            if command == "Z":
                if not have_move:
                    raise ValueError("close command has no subpath")
                output.append("Z")
            continue
        if command not in {"M", "L"} or index + 1 >= len(tokens):
            raise ValueError("compound path must use absolute M/L pairs and Z")
        x, y = float(tokens[index]), float(tokens[index + 1])
        index += 2
        px, py = transform(x, y)
        if not (math.isfinite(px) and math.isfinite(py)):
            raise ValueError("transformed path coordinate is not finite")
        if command == "L" and not have_move:
            raise ValueError("line command precedes move command")
        output.append(f"{command} {px:.6f},{py:.6f}")
        if command == "M":
            have_move = True
    if output[-1] != "Z":
        raise ValueError("compound path contains an unclosed subpath")
    return " ".join(output)


def _hidden_intervals(q0, q1, triangles, owner_index: int, owner_component: str) -> tuple[tuple[float, float], ...]:
    """Partition a projected semantic segment at shared probe triangle boundaries/depth roots."""
    cuts = [0.0, 1.0]
    prepared = []
    for index, (triangle, component) in enumerate(triangles):
        plane = depth_plane(triangle)
        if plane is None:
            continue
        prepared.append((index, triangle, component, plane))
        if component == owner_component:
            continue
        edge_cuts = [0.0, 1.0]
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            edge_cuts.extend(_line_probe._segment_edge_parameters(q0, q1, a, b))
        edge_cuts = sorted(set(min(1.0, max(0.0, t)) for t in edge_cuts))
        cuts.extend(edge_cuts)
        for lo, hi in zip(edge_cuts, edge_cuts[1:]):
            if hi - lo <= _line_probe.PROJECTED_EPS:
                continue
            midpoint = _line_probe._interpolate3(q0, q1, (lo + hi) / 2)
            weights = _line_probe._barycentric2(midpoint, triangle)
            if weights is None or min(weights) < -_line_probe.BARYCENTRIC_EPS:
                continue
            p0, p1 = _line_probe._interpolate3(q0, q1, lo), _line_probe._interpolate3(q0, q1, hi)
            bias = _line_probe._tie_bias_for(index, owner_index)
            v0 = _line_probe._plane_at(plane, p0) - p0[2] + bias + EPS
            v1 = _line_probe._plane_at(plane, p1) - p1[2] + bias + EPS
            if v0 == 0:
                cuts.append(lo)
            if v1 == 0:
                cuts.append(hi)
            if v0 * v1 < 0:
                cuts.append(lo + v0 / (v0 - v1) * (hi - lo))
    cuts = sorted(min(1.0, max(0.0, t)) for t in cuts)
    unique = []
    for t in cuts:
        if not unique or t - unique[-1] > _line_probe.PROJECTED_EPS:
            unique.append(t)
    hidden = []
    for lo, hi in zip(unique, unique[1:]):
        if hi - lo <= _line_probe.PROJECTED_EPS:
            continue
        midpoint = _line_probe._interpolate3(q0, q1, (lo + hi) / 2)
        if any(component != owner_component and weights is not None
               and min(weights) >= -_line_probe.BARYCENTRIC_EPS
               and _line_probe._is_front_occluder(
                   _line_probe._plane_at(plane, midpoint), midpoint[2], index, owner_index)
               for index, triangle, component, plane in prepared
               for weights in (_line_probe._barycentric2(midpoint, triangle),)):
            hidden.append((lo, hi))
    return tuple(hidden)


def visible_segment_spans(q0: tuple[float, float, float], q1: tuple[float, float, float],
                          faces, owner_component: str) -> tuple[tuple[float, float], ...]:
    """Return visible [t0,t1] intervals for an authored line on its owning support.

    Faces are the same support-mapped projected triangles passed to the fill backend. The owning
    component anchors the source depth and is not treated as its own occluder; every other component
    participates, independent of whether it was declared before or after the authored line. Exact
    segment-edge, barycentric, interpolation and depth-tie probes reuse `ribbon_drawing`'s tested
    semantic-line boundary machinery; the opaque-triangle backend is unchanged.
    """
    owner_indices = [i for i, (_triangle, _fill, name) in enumerate(faces) if name == owner_component]
    if not owner_indices:
        raise ValueError(f"semantic line owner {owner_component!r} has no support-mapped faces")
    owner_index = owner_indices[0]
    triangles = tuple((tuple(triangle), name) for triangle, _fill, name in faces)
    hidden = _hidden_intervals(q0, q1, triangles, owner_index, owner_component)
    visible = []
    cursor = 0.0
    for lo, hi in hidden:
        if lo > cursor + _line_probe.PROJECTED_EPS:
            visible.append((cursor, lo))
        cursor = max(cursor, hi)
    if cursor < 1.0 - _line_probe.PROJECTED_EPS:
        visible.append((cursor, 1.0))
    return tuple(visible)
