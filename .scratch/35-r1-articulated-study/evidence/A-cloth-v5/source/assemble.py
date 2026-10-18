"""Assemble the A garment study: parts -> supports -> scene faces -> visible regions.

Nothing here authors geometry.  The assembly calls one builder per object family,
collects their faces into one scene and lets the project's triangle depth engine
compute what is visible.  Marks are authored whole and clipped by depth only.
"""
from __future__ import annotations

import html

from scripts.articulated_construction import Camera, component_faces, triangulate_polygon
from scripts.vector_visibility import visible_regions

from .lines import Occluders, visible_runs_of_mark
from .parts import bodice, bow, collar, hair, skin, sleeve

WIDTH, HEIGHT = 400, 480
CAMERA = Camera()
BACKGROUND = "#78a49b"

# One entry per drawn object. `is` says the single connected physical thing the
# object is; `why` is required whenever the object is built from more than one part,
# so a split can never pass as an unexplained collection of pieces.
OBJECTS = {
    "collar": {
        "parts": ["A-collar-left", "A-collar-right"],
        "is": "one sailor collar lying around the neck opening",
        "why": "the real collar is two leaves sewn at the shared front seam Q..Q'; the seam is "
               "checked geometrically, not by name",
    },
    "neck": {
        "parts": ["A-visible-neck-skin"],
        "is": "one continuous neck-skin field from the opening up past the crop",
        "why": "",
    },
    "bodice": {
        "parts": ["A-bodice-upper", "A-derived-waist-band", "A-bodice-continuation"],
        "is": "one blouse: chest cloth, gathered waist and the same cloth below it",
        "why": "the upper field, band and continuation are three sections of one width field; the "
               "band is a section relation, not a separate garment",
    },
    "left-sleeve": {
        "parts": ["A-left-sleeve", "A-left-cuff"],
        "is": "one sleeve on the wearer's left: shoulder cap, puff, dark cuff",
        "why": "the cuff is one band sewn onto the sleeve's terminal section; the section is shared "
               "exactly and its visible sliver is what depth leaves",
    },
    "right-sleeve": {
        "parts": ["A-right-sleeve", "A-right-cuff"],
        "is": "one sleeve on the wearer's right: shoulder cap, puff, dark cuff",
        "why": "same shared terminal section as the left sleeve",
    },
    "bow": {
        "parts": ["A-bow-ribbon"],
        "is": "one magenta ribbon tied into a bow: knot, two lobes, two tails",
        "why": "",
    },
    "hair": {
        "parts": ["A-hair-sheet"],
        "is": "one head-attached hair sheet, deep blue outside and mint inside",
        "why": "",
    },
}

ART_EDGE_TYPES = {"silhouette", "free_edge", "trim", "fold_edge"}
TRIM_COLOR = "#293346"
INK = "#34424c"
FOLD_WIDTH = 1.6
SILHOUETTE_WIDTH = 1.3
TRIM_WIDTH = 3.2


def build():
    collar_parts, opening = collar.build()
    left_root = collar_parts["A-collar-left"].plane_anchor("R")[0]
    right_root = collar_parts["A-collar-right"].plane_anchor("R")[0]
    bodice_parts = bodice.build(opening["Q_plane"], left_root, right_root)
    skin_parts, _skin_local = skin.build(collar_parts)
    sleeve_parts = sleeve.build(bodice)
    bow_parts, bow_marks, bow_meta = bow.build()
    hair_parts, hair_marks, hair_meta = hair.build()
    parts = {}
    for group in (collar_parts, bodice_parts, skin_parts, sleeve_parts, bow_parts, hair_parts):
        parts.update(group)
    return dict(parts=parts, opening=opening, bow=bow_meta, hair=hair_meta,
                sheet_marks=tuple(bow_marks) + tuple(hair_marks))


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
    faces = list(component_faces(planar, CAMERA))
    for part in scene["parts"].values():
        if hasattr(part, "faces") and not hasattr(part, "component"):
            faces.extend(part.faces())
    return tuple(faces)


def mark_geometry(scene):
    """Every authored mark as (name, owner, 3D polyline, colour, width)."""
    marks = []
    for part in scene["parts"].values():
        if not hasattr(part, "component"):
            continue
        support = part.frame.support()
        for edge in part.edges:
            if edge.type not in ART_EDGE_TYPES:
                continue
            points = tuple(support.local_to_world(p) for p in edge.points)
            trim = edge.type == "trim"
            marks.append((f"{part.name}-{edge.type}-{len(marks)}", part.name, points,
                          TRIM_COLOR if trim else INK,
                          TRIM_WIDTH if trim else (FOLD_WIDTH if edge.type == "fold_edge" else SILHOUETTE_WIDTH)))
    for name, points, color in scene["sheet_marks"]:
        marks.append((name, name.split("-edge")[0], points, color, 1.4))
    return tuple(marks)


def render_svg(scene):
    faces = scene_faces(scene)
    regions = tuple(visible_regions(faces))
    occluders = Occluders(faces)
    parts = scene["parts"]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<title>A garment construction study — observed shoulder and upper-torso clothing only</title>',
        '<desc>One connected object per part: a continuous bow ribbon, one two-sided hair sheet, '
        'two whole sleeves, and cloth pieces joined by checked seams. Depth decides visibility; '
        'no visible cut is authored.</desc>',
        '<!-- A-local-composition-field: flat contextual background, not a generated image -->',
        f'<rect id="A-local-composition-field" x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="{BACKGROUND}"/>',
    ]
    for path, color, name in regions:
        intent = parts[name].intent if name in parts else ""
        out.append(f'<!-- {html.escape(name)}: {html.escape(intent)} -->')
        out.append(f'<path id="fill-{html.escape(name)}" data-part="{html.escape(name)}" '
                   f'd="{_flip(path)}" fill="{color}" fill-rule="nonzero"/>')
    clipped = 0
    drawn = 0
    for name, owner, points, color, width in mark_geometry(scene):
        runs = visible_runs_of_mark(points, occluders)
        if not runs:
            continue
        out.append(f'<!-- {html.escape(name)}: authored cloth mark, owner={html.escape(owner)}, '
                   f'depth-clipped -->')
        dense = _dense(points)
        for run_index, (lo, hi) in enumerate(runs):
            segment = dense[lo:hi + 1]
            if len(segment) < 2:
                continue
            d = "M " + " L ".join(f"{p[0]:.4f},{HEIGHT - p[1]:.4f}" for p in segment)
            out.append(f'<path id="{html.escape(name)}-{run_index}" d="{d}" fill="none" '
                       f'stroke="{color}" stroke-width="{width:.2f}" stroke-linecap="round" '
                       f'stroke-linejoin="round"/>')
            drawn += 1
        clipped += 1
    out.append('</svg>')
    return "\n".join(out) + "\n", dict(regions=len(regions), marks=clipped, mark_paths=drawn,
                                       faces=len(faces))


def _dense(points):
    from .lines import densify
    return densify(points)


def _flip(path):
    """Backend paths use SVG coordinates already (y down) because the projection is
    produced from plane coordinates; flip once here so the artwork reads y-down."""
    import re
    tokens = re.findall(r"[MLZ]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?", path)
    out = []
    index = 0
    command = None
    while index < len(tokens):
        token = tokens[index]
        if token in ("M", "L", "Z"):
            command = token
            out.append(token)
            index += 1
            continue
        x = float(tokens[index])
        y = float(tokens[index + 1])
        index += 2
        out.append(f"{x:.4f},{HEIGHT - y:.4f}")
    return " ".join(out)
