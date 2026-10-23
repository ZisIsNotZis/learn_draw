"""Render the full figure: parts -> supports -> scene faces -> visible regions -> SVG.

The renderer is the project's own: `scripts/vector_visibility` decides which triangle
of which part is visible from the depth of each triangle, and every authored mark is
clipped by the same depth test.  Nothing here decides a visible cut.
"""
from __future__ import annotations

import html
import re

from scripts.articulated_construction import component_faces, triangulate_polygon
from scripts.vector_visibility import visible_regions

from ..lines import Occluders, visible_runs_of_mark
from . import figure


def scene_faces(scene):
    planar = []
    for part in scene["parts"].values():
        if not hasattr(part, "component"):
            continue
        component = part.component()
        try:
            triangulate_polygon(component.outline)
        except ValueError as exc:
            raise ValueError(f"{component.name}: {exc}") from exc
        planar.append(component)
    faces = list(component_faces(planar, figure.CAMERA))
    for part in scene["parts"].values():
        if hasattr(part, "faces") and not hasattr(part, "component"):
            faces.extend(part.faces())
    return tuple(faces)


def mark_geometry(scene):
    marks = []
    for part in scene["parts"].values():
        if not hasattr(part, "component"):
            continue
        support = part.frame.support()
        for index, edge in enumerate(part.edges):
            if edge.type not in figure.LINE_POLICY:
                continue
            points = tuple(support.local_to_world(p) for p in edge.points)
            marks.append((f"{part.name}-{edge.type}-{index}", part.name, edge.type,
                          f"{part.name}.edges[{index}] ({edge.intent})", points))
    for name, owner, line_class, points, _ink in scene["sheet_marks"]:
        if line_class not in figure.LINE_POLICY:
            raise ValueError(f"{name}: undeclared line class {line_class}")
        if owner not in scene["parts"]:
            raise ValueError(f"{name}: owner {owner} is not a declared part")
        marks.append((name, owner, line_class, f"{name} sampled on its sheet surface", points))
    return tuple(marks)


def _flip(path):
    """Backend paths are plane coordinates with y up; SVG is y down.  Flip the y once."""
    tokens = re.findall(r"[MLZ]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?", path)
    out, index, expect_y = [], 0, False
    while index < len(tokens):
        token = tokens[index]
        if token in ("M", "L", "Z"):
            out.append(token)
            index += 1
            expect_y = token != "Z"
            continue
        x = float(token)
        y = float(tokens[index + 1]) if index + 1 < len(tokens) else 0.0
        out.append(f"{x:.4f},{figure.HEIGHT - y:.4f}")
        index += 2
    return " ".join(out)


def _dense(points):
    from ..lines import densify
    return densify(points)


def render_svg(scene):
    faces = scene_faces(scene)
    regions = tuple(visible_regions(faces))
    occluders = Occluders(faces)
    parts = scene["parts"]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{figure.WIDTH}" '
        f'height="{figure.HEIGHT}" viewBox="0 0 {figure.WIDTH} {figure.HEIGHT}">',
        '<title>Full figure — the girl seated, built from parts; no image read</title>',
        '<desc>One connected object per part, each traceable to the study that authored it. '
        'Depth decides visibility; no visible cut is authored.</desc>',
        '<!-- A-local-composition-field: flat contextual background, not a generated image -->',
        f'<rect id="A-local-composition-field" x="0" y="0" width="{figure.WIDTH}" '
        f'height="{figure.HEIGHT}" fill="{figure.BACKGROUND_SKY}"/>',
    ]
    for name, points, color in scene.get("field", ()):
        d = "M " + " L ".join(f"{p.u:.2f},{figure.HEIGHT - p.v:.2f}" for p in points) + " Z"
        out.append(f'<!-- {html.escape(name)}: the picture field, painted behind every part -->')
        out.append(f'<path id="{html.escape(name)}" d="{d}" fill="{color}"/>')
    for path, color, name in regions:
        intent = parts[name].intent if name in parts else ""
        out.append(f'<!-- {html.escape(name)}: {html.escape(intent)} -->')
        out.append(f'<path id="fill-{html.escape(name)}" data-part="{html.escape(name)}" '
                   f'd="{_flip(path)}" fill="{color}" fill-rule="nonzero"/>')
    clipped = drawn = 0
    for name, owner, line_class, source, points in mark_geometry(scene):
        runs = visible_runs_of_mark(points, occluders)
        if not runs:
            continue
        color, width = figure.LINE_POLICY[line_class]
        out.append(f'<!-- {html.escape(name)}: class={line_class} owner={html.escape(owner)} '
                   f'source={html.escape(source)} depth-clipped -->')
        dense = _dense(points)
        for run_index, (lo, hi) in enumerate(runs):
            segment = dense[lo:hi + 1]
            if len(segment) < 2:
                continue
            d = "M " + " L ".join(f"{p[0]:.4f},{figure.HEIGHT - p[1]:.4f}" for p in segment)
            out.append(f'<path id="{html.escape(name)}-{run_index}" data-class="{line_class}" '
                       f'd="{d}" fill="none" stroke="{color}" stroke-width="{width:.2f}" '
                       f'stroke-linecap="round" stroke-linejoin="round"/>')
            drawn += 1
        clipped += 1
    out.append('</svg>')
    return "\n".join(out) + "\n", dict(regions=len(regions), marks=clipped, mark_paths=drawn,
                                       faces=len(faces))
