"""Compile editable parts through existing depth visibility; emit inspection bundles."""
from __future__ import annotations

import html
from pathlib import Path

from scripts.articulated_construction import Point, triangulate_polygon
from scripts.vector_visibility import visible_regions

from .geometry import bounds, lock_rows, mix, outline, resolve_root
from .model import engine_fingerprint, fingerprint, node_by_id, validate, write


PALETTE = dict(fill="#517f9b", shade="#426781", light="#729eaf", ink="#2e475a")


def path(points, closed=True):
    return "M " + " L ".join(f"{x:.4f},{y:.4f}" for x, y in points) + (" Z" if closed else "")


def faces_for(scene):
    faces = []
    canvas = scene.get("canvas", [640, 640])
    for node in scene["nodes"]:
        poly = outline(lock_rows(node, canvas))
        root_y = lock_rows(node, canvas)[0].left[1]
        scale = node.get("length", .68) * min(canvas)
        for triangle in triangulate_polygon(tuple(Point(*p) for p in poly)):
            tri = tuple((p.u, p.v, node.get("depth", 0) + node.get("depth_slope", 0) * (p.v - root_y) / scale) for p in triangle)
            faces.append((tri, PALETTE["fill"], node["id"]))
    return faces


def tone_region(rows, start, end, a, b):
    selected = [r for r in rows if start <= r.t <= end]
    # Both ends of the highlight taper inside the lock, not square-ended stripes.
    left, right = [], []
    import math
    for r in selected:
        t = (r.t - start) / (end - start)
        envelope = max(0, math.sin(math.pi * t)) ** .6
        middle, half = (a + b) / 2, (b - a) / 2 * envelope
        left.append(mix(r.left, r.right, middle - half))
        right.append(mix(r.left, r.right, middle + half))
    return left + list(reversed(right))


def drawing(scene, selection=None, previous=None, viewbox=None):
    validate(scene)
    width, height = scene.get("canvas", [640, 640])
    vb = viewbox or [0, 0, width, height]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{" ".join(map(str, vb))}">',
           '<title>Editable hair lock study</title>',
           '<desc>Authored gesture and local edits; visibility from support depth. Selection aids are separate from artwork.</desc>',
           f'<rect id="paper" x="0" y="0" width="{width}" height="{height}" fill="{scene.get("background", "#f5eee4")}"/>']
    regions = list(visible_regions(faces_for(scene)))
    for node in scene["nodes"]:
        sid = node["id"]
        visible = " ".join(p for p, _color, name in regions if name == sid)
        out.append(f'<defs><clipPath id="visible-{sid}" clipPathUnits="userSpaceOnUse"><path d="{visible}"/></clipPath></defs>')
        colors = PALETTE | node.get("palette", {})
        rows = lock_rows(node, [width, height])
        poly = outline(rows)
        out += [f'<!-- {sid}: {html.escape(node["intent"])} -->',
                f'<g id="{sid}" clip-path="url(#visible-{sid})">',
                f'<path id="{sid}-silhouette" d="{path(poly)}" fill="{colors["fill"]}"/>',
                f'<!-- {sid}-shade: cel shadow following the edited inner side -->',
                f'<path id="{sid}-shade" d="{path(tone_region(rows, 0, 1, .77, 1))}" fill="{colors["shade"]}"/>',
                f'<!-- {sid}-light: broad restrained sheen following the lock gesture -->',
                f'<path id="{sid}-light" d="{path(tone_region(rows, .20, .76, .23, .38))}" fill="{colors["light"]}"/>',
                f'<!-- {sid}-contour: two flowing sides; the root joins the host without a sealed ink cap -->',
                f'<path id="{sid}-contour" d="{path([r.left for r in rows], False)} {path([r.right for r in rows], False)}" fill="none" stroke="{colors["ink"]}" stroke-width="3.0" stroke-linejoin="round"/>']
        for k, (share, start, end) in enumerate(((.52, .09, .88), (.73, .27, .96))):
            points = [mix(r.left, r.right, share) for r in rows if start <= r.t <= end]
            out += [f'<!-- {sid}-strand-{k}: a sparse directional strand following the edited mass -->',
                    f'<path id="{sid}-strand-{k}" d="{path(points, False)}" fill="none" stroke="{colors["ink"]}" opacity=".55" stroke-width=".9"/>']
        out.append('</g>')
    if selection:
        if selection.get("engine") != engine_fingerprint():
            raise ValueError("stale selection: implementation changed; inspect again")
        node = node_by_id(scene, selection["object"])
        rows = lock_rows(node, [width, height])
        pts = [getattr(r, selection["side"]) for r in rows if abs(r.t - selection["at"]) <= selection["radius"]]
        if previous:
            old = lock_rows(node_by_id(previous, node["id"]), [width, height])
            old_pts = [getattr(r, selection["side"]) for r in old if abs(r.t - selection["at"]) <= selection["radius"]]
            out += ['<!-- edit-before: dashed alignment guide, never part of artwork -->',
                    f'<path id="edit-before" d="{path(old_pts, False)}" fill="none" stroke="#ba6884" stroke-width="2" stroke-dasharray="5 4"/>']
        out += ['<!-- selected-edge: author alignment aid, never a decorative art line -->',
                f'<path id="selected-edge" d="{path(pts, False)}" fill="none" stroke="#e27d39" stroke-width="3"/>']
        target = min(rows, key=lambda r: abs(r.t - selection["at"]))
        x, y = getattr(target, selection["side"])
        out.append(f'<circle id="edit-focus" cx="{x}" cy="{y}" r="5" fill="#fffaf0" stroke="#bc5128" stroke-width="2"/>')
        for name, p in (("root", resolve_root(node, [width, height])), ("tip", rows[-1].left)):
            out.append(f'<circle id="locked-{name}" cx="{p[0]}" cy="{p[1]}" r="4" fill="#fffaf0" stroke="#506655" stroke-width="2"/>')
    return "\n".join(out + ['</svg>'])


def rasterize(svg, target):
    """CPU Cairo first; isolated GPU-disabled Edge is a platform fallback."""
    try:
        import cairosvg
        cairosvg.svg2png(url=str(Path(svg).resolve()), write_to=str(target))
        return "cairosvg-cpu"
    except (ImportError, OSError):
        pass
    import xml.etree.ElementTree as ET
    from scripts.renderer import screenshot
    root = ET.parse(svg).getroot()
    size = (int(float(root.attrib["width"])), int(float(root.attrib["height"])))
    screenshot(svg, target, size)
    return "chromium-disable-gpu"


def bundle(scene, directory, selection=None, previous=None, png=True):
    """Scene, inspection and image list are bound to one exact canonical revision."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    validate(scene)
    write(directory / "scene.json", scene)
    revision = fingerprint(scene)
    if selection:
        if previous is None and selection["base"] != revision:
            raise ValueError("stale selection: cannot draw alignment against another revision")
        if previous is not None and selection["base"] != fingerprint(previous):
            raise ValueError("preview alignment base mismatch")
        write(directory / "selection.json", selection)
    views = {"artwork": drawing(scene)}
    if selection:
        # Crop around the object, not a guessed image location. Square pixel crop
        # is rendered to the same output dimensions, providing real magnification.
        box = bounds(outline(lock_rows(node_by_id(scene, selection["object"]), scene.get("canvas", [640, 640]))))
        x0, y0, x1, y1 = box
        pad = max(x1 - x0, y1 - y0) * .1
        span = max(x1 - x0, y1 - y0) + 2 * pad
        vb = [(x0 + x1 - span) / 2, (y0 + y1 - span) / 2, span, span]
        views["alignment"] = drawing(scene, selection, previous)
        views["object-closeup"] = drawing(scene, selection, previous, vb)
        # An operation-scale crop shows the selected edge and before/after guides.
        b = selection["bounds"]
        span = max(b[2] - b[0], b[3] - b[1], 40) * 1.8
        views["edit-closeup"] = drawing(scene, selection, previous,
                                       [(b[0] + b[2] - span) / 2, (b[1] + b[3] - span) / 2, span, span])
    backend = None
    images = []
    for name, svg in views.items():
        f = directory / (name + ".svg")
        f.write_text(svg, encoding="utf-8")
        if png:
            backend = rasterize(f, directory / (name + ".png"))
            images.append(str((directory / (name + ".png")).resolve()))
    report = dict(revision=revision, engine=engine_fingerprint(), renderer=backend, images=images,
                  nodes={n["id"]: dict(intent=n["intent"], bounds=bounds(outline(lock_rows(n, scene.get("canvas", [640, 640]))))) for n in scene["nodes"]},
                  scope="editable planar hair locks; no head, attachment, curved support or whole-artwork acceptance claim")
    write(directory / "report.json", report)
    (directory / "report.txt").write_text("\n".join(images) + "\n", encoding="utf-8")
    return report
