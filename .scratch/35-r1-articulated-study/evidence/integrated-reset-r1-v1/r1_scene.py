"""Semantic A/B artwork inputs and deterministic spatially integrated SVG composition."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import html

from scripts.articulated_construction import Camera, Component, Point, SupportFrame, build_study_case, validate_study_case
from spatial_adapter import VisibleSmoothComponent, build_visible_smooth_component, project_visible_semantic_segment

ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ShapeSpec:
    name: str
    intent: str
    support: SupportFrame
    fill: str
    controls: tuple[Point, ...]


@dataclass(frozen=True)
class LineSpec:
    name: str
    intent: str
    owner: str
    support: SupportFrame
    start: Point
    end: Point
    color: str = "#253448"
    width: float = 2.2


@dataclass(frozen=True)
class Study:
    name: str
    width: int
    height: int
    shapes: tuple[ShapeSpec, ...]
    lines: tuple[LineSpec, ...]
    labels: tuple[tuple[str, str, float, float], ...]
    camera: Camera
    background: str
    scale: float
    offset_x: float
    offset_y: float


def controls(name: str, intent: str, support: SupportFrame, fill: str,
             pairs: tuple[tuple[float, float], ...]) -> ShapeSpec:
    """One authored closed shape: every literal coordinate pair is an input to the adapter."""
    if len(pairs) > 4:
        raise ValueError(f"{name}: authored shape exceeds four semantic coordinate pairs")
    return ShapeSpec(name, intent, support, fill, tuple(Point(*p) for p in pairs))


_A_BODY = SupportFrame("A-garment-plane", "A-garment-depth")
_A_TRIM = SupportFrame("A-trim-plane", "A-trim-depth", origin=(0, 0, 0.035))
_A_BOW = SupportFrame("A-bow-plane", "A-bow-depth", origin=(0, 0, 0.075))
_A_KNOT = SupportFrame("A-knot-plane", "A-knot-depth", origin=(0, 0, 0.10))
_A_CAMERA = Camera()


def build_a_study() -> Study:
    # Coordinates are sparse garment-shape landmarks in the registered 400x480 crop frame,
    # observed as local design choices. Camera mapping is 1 scene unit to 1 crop pixel.
    shapes = (
        controls("bodice", "broad pale upper-body garment field anchors the crop", _A_BODY, "#f4f1e6",
                 ((74, 355), (354, 360), (365, 50), (96, 45))),
        controls("right-sleeve", "light sleeve mass gives shoulder-to-bodice context", _A_BODY, "#e9e5d9",
                 ((274, 375), (376, 382), (380, 235), (321, 205))),
        controls("collar", "dark-edged folded collar frames the garment opening", _A_TRIM, "#d9e4dd",
                 ((80, 372), (183, 349), (251, 352), (303, 387))),
        controls("collar-inset", "pale inner collar keeps the neckline layered", _A_BODY, "#f5f2e8",
                 ((115, 365), (184, 344), (238, 349), (272, 372))),
        controls("bow-left-loop", "observed broad pink bow loop opens toward the left", _A_BOW, "#cb4f75",
                 ((193, 291), (88, 349), (107, 278), (194, 260))),
        controls("bow-right-loop", "observed broad pink bow loop opens toward the right", _A_BOW, "#d45c7e",
                 ((203, 292), (281, 344), (256, 266), (204, 256))),
        controls("bow-left-tail", "short pointed ribbon tail falls across the bodice", _A_BOW, "#bd4269",
                 ((180, 265), (213, 270), (205, 190), (153, 211))),
        controls("bow-right-tail", "second ribbon tail turns toward the waist", _A_BOW, "#d65b7c",
                 ((214, 266), (241, 271), (235, 199), (202, 190))),
        controls("bow-knot", "small gathered center joins the two ribbon loops", _A_KNOT, "#e2748e",
                 ((181, 297), (216, 304), (224, 275), (188, 267))),
        controls("waist-band", "dark blue waist trim supplies neighboring garment context", _A_TRIM, "#344c69",
                 ((92, 95), (352, 108), (352, 73), (95, 62))),
        controls("waist-highlight", "narrow pale edge separates bodice from dark band", _A_BOW, "#b8c9c5",
                 ((94, 112), (353, 126), (352, 111), (94, 96))),
    )
    lines = (
        LineSpec("collar-fold", "visible inner collar fold", "collar", _A_TRIM, Point(122, 361), Point(184, 344)),
        LineSpec("collar-fold-right", "visible right collar fold", "collar", _A_TRIM, Point(239, 350), Point(280, 375)),
        LineSpec("bow-crease-left", "short crease articulates the left ribbon loop", "bow-left-loop", _A_BOW, Point(120, 314), Point(175, 286), "#7c3150", 1.8),
        LineSpec("bow-crease-right", "short crease articulates the right ribbon loop", "bow-right-loop", _A_BOW, Point(224, 288), Point(263, 318), "#843451", 1.8),
        LineSpec("waist-stitch", "quiet seam echoes the dark waist edge", "bodice", _A_BODY, Point(116, 145), Point(350, 136), "#9caaa5", 1.5),
    )
    return Study("A observed garment crop", 400, 480, shapes, lines,
                 (("A · observed shoulder / upper-garment study", "title", 16, 24),),
                 _A_CAMERA, "#d5e6e5", 1.0, 0.0, 480.0)


def _cardinal_controls(component: Component) -> tuple[Point, ...]:
    # Downsample generated ellipses to four cardinal relation points; no source coordinates added.
    points = component.outline
    if len(points) == 32:
        return tuple(points[index] for index in (0, 8, 16, 24))
    if len(points) <= 4:
        return points
    raise ValueError(f"unexpected generated outline for {component.name}: {len(points)}")


def _b_case_shapes(case_name: str) -> tuple[list[ShapeSpec], list[LineSpec], tuple]:
    case = build_study_case(case_name)
    validate_study_case(case)
    by_name = {component.name: component for component in case.components}
    shapes = []
    colors = {"torso": "#315568", "head": "#d7a27e", "neck": "#d9a47f",
              "upper_arm": "#a9c1c0", "forearm": "#d1d9cf", "hand": "#d9a784", "prop": "#dfad58"}
    for component in case.components:
        if component.name == "upper_arm":
            source = component.outline
            outline = tuple(source[index] for index in (0, 16, 34, 50))
        elif component.name == "forearm":
            source = component.outline
            outline = tuple(source[index] for index in (0, 16, 34, 50))
        else:
            outline = _cardinal_controls(component)
        shapes.append(ShapeSpec(component.name,
            f"{component.intent}; support-bound original {case_name} action component",
            component.support, colors[component.name], outline))
    # Front garment is an authored, four-control vest panel related to the torso's support.
    torso = by_name["torso"]
    vest_support = SupportFrame("vest-front", "vest-depth", origin=(0, 0, .045),
                                u_axis=torso.support.u_axis, v_axis=torso.support.v_axis)
    shapes.append(controls("vest-panel", "tailored front panel gives the torso clothing context",
        vest_support, "#d5d8c9", ((-.68, .42), (.68, .42), (.57, 1.67), (-.57, 1.67))))
    # Four-point hair cap is a fresh semantic frame cue; no vendor identity or image coordinates.
    shapes.append(controls("hair-cap", "original swept cap frames the head", by_name["head"].support,
        "#25384e", ((-.49, 3.27), (-.12, 3.72), (.50, 3.35), (.27, 3.03))))
    lines = [
        LineSpec("vest-edge-left", "tailored lapel line", "vest-panel", vest_support,
                 Point(-.38, 1.54), Point(-.13, 1.04), "#667c7c", 1.8),
        LineSpec("vest-edge-right", "matching lapel line", "vest-panel", vest_support,
                 Point(.38, 1.54), Point(.13, 1.04), "#667c7c", 1.8),
        LineSpec("grip-finger-one", "first articulated finger reaches the prop", "hand",
                 by_name["hand"].support, Point(case.hand_target.u + .20, case.hand_target.v + .07),
                 Point(case.contact.u - .01, case.contact.v + .07), "#754c46", 1.8),
        LineSpec("grip-finger-two", "second articulated finger closes around the prop", "hand",
                 by_name["hand"].support, Point(case.hand_target.u + .23, case.hand_target.v - .02),
                 Point(case.contact.u - .01, case.contact.v - .02), "#754c46", 1.6),
    ]
    return shapes, lines, (case, by_name)


def build_b_study() -> Study:
    width, height = 3 * 420, 620
    shapes: list[ShapeSpec] = []
    lines: list[LineSpec] = []
    labels = []
    cases = ("baseline", "variant", "control")
    for index, case_name in enumerate(cases):
        case_shapes, case_lines, (_case, _by_name) = _b_case_shapes(case_name)
        dx = index * 420
        support_shift = (dx / 90.0, 0.0, 0.0)
        for spec in case_shapes:
            s = spec.support
            moved = SupportFrame(s.support_id + "-" + case_name, s.depth_ref + "-" + case_name,
                (s.origin[0] + support_shift[0], s.origin[1], s.origin[2]), s.u_axis, s.v_axis)
            controls_shifted = tuple(Point(p.u, p.v) for p in spec.controls)
            shapes.append(ShapeSpec(f"{case_name}-{spec.name}", spec.intent, moved, spec.fill, controls_shifted))
        for line in case_lines:
            s = line.support
            moved = SupportFrame(s.support_id + "-" + case_name, s.depth_ref + "-" + case_name,
                (s.origin[0] + support_shift[0], s.origin[1], s.origin[2]), s.u_axis, s.v_axis)
            lines.append(LineSpec(f"{case_name}-{line.name}", line.intent,
                f"{case_name}-{line.owner}", moved, line.start, line.end, line.color, line.width))
        title = {"baseline": "BASELINE · raised grip", "variant": "VARIANT · chest-rest grip · wider shoulders",
                 "control": "CONTROL — near miss"}[case_name]
        labels.append((title, "panel", dx + 210, 46))
        labels.append(("same camera · original construction", "caption", dx + 210, 578))
    return Study("B original articulated action", width, height, tuple(shapes), tuple(lines),
                 tuple(labels), Camera(), "#eee8dc", 90.0, 150.0, 520.0)


def _screen(study: Study, point: tuple[float, float, float]) -> tuple[float, float]:
    return (study.offset_x + study.scale * point[0], study.offset_y - study.scale * point[1])


def _path_line(study: Study, span, color: str, width: float, name: str) -> str:
    a, b = (_screen(study, point) for point in span)
    return (f'<path id="{html.escape(name)}" d="M {a[0]:.3f},{a[1]:.3f} L {b[0]:.3f},{b[1]:.3f}" '
            f'fill="none" stroke="{html.escape(color)}" stroke-width="{width:.2f}" '
            'stroke-linecap="round" stroke-linejoin="round"/>')


def build_svg(study: Study) -> str:
    """Renderer accepts only a frozen study and output-independent geometry; no reference input."""
    components = {}
    for spec in study.shapes:
        adapter_result = build_visible_smooth_component(
            spec.controls, spec.name, spec.support, study.camera, (),
            intent=spec.intent, fill=spec.fill)
        if not isinstance(adapter_result, VisibleSmoothComponent):
            raise TypeError("scene components must come from the guarded spatial adapter")
        if adapter_result.component.outline is not adapter_result.validated_sampled_contour:
            raise ValueError("component contour bypassed its validation guard")
        components[spec.name] = adapter_result.component
    if len(components) != len(study.shapes):
        raise ValueError("duplicate semantic component IDs")
    # Rebuild each adapter against all sibling surfaces; these returned regions/spans are the only ink/fill source.
    visible = {}
    for spec in study.shapes:
        occluders = tuple(component for component in components.values() if component.name != spec.name)
        adapter_result = build_visible_smooth_component(
            spec.controls, spec.name, spec.support, study.camera, occluders,
            intent=spec.intent, fill=spec.fill)
        if not isinstance(adapter_result, VisibleSmoothComponent):
            raise TypeError("emission accepts guarded adapter results only")
        if adapter_result.component.outline is not adapter_result.validated_sampled_contour:
            raise ValueError("emitted contour is not the guarded sample")
        visible[spec.name] = adapter_result
    return emit_study_svg(study, visible)


def emit_study_svg(study: Study, visible: dict[str, VisibleSmoothComponent]) -> str:
    """Reject direct SVG geometry: only exact guarded adapter results may reach fill/stroke emission."""
    expected = {shape.name for shape in study.shapes}
    if set(visible) != expected or any(not isinstance(value, VisibleSmoothComponent) for value in visible.values()):
        raise TypeError("fill/line emission requires a complete mapping of guarded adapter results")
    for name, result in visible.items():
        if result.component.name != name or result.component.outline is not result.validated_sampled_contour:
            raise ValueError("adapter output identity/dataflow mismatch")
    components = {name: result.component for name, result in visible.items()}
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{study.width}" height="{study.height}" '
             f'viewBox="0 0 {study.width} {study.height}">',
             '<!-- named ground: quiet backdrop separates the garment study from the page -->',
             f'<rect id="study-ground" width="100%" height="100%" fill="{study.background}"/>']
    if study.name.startswith("B "):
        for index, x in enumerate((420, 840)):
            parts.append(f'<!-- panel-divider-{index}: separates matched-camera action variants -->')
            parts.append(f'<path id="panel-divider-{index}" d="M {x},0 V {study.height}" stroke="#c9c1b5" stroke-width="1"/>')
    for spec in study.shapes:
        result = visible[spec.name]
        if not result.visible_fill_regions:
            raise ValueError(f"visible fill missing for {spec.name}")
        for index, (path, color, owner) in enumerate(result.visible_fill_regions):
            from scripts.articulated_line_visibility import transform_compound_path
            mapped = transform_compound_path(path, lambda x, y: _screen(study, (x, y, 0.0)))
            parts.append(f'<!-- {html.escape(spec.name)}: {html.escape(spec.intent)} -->')
            parts.append(f'<path id="fill-{html.escape(owner)}-{index}" d="{mapped}" fill="{color}" stroke="none"/>')
        for index, span in enumerate(result.authored_boundary_spans):
            parts.append(f'<!-- {html.escape(spec.name)}: visible semantic outer boundary -->')
            parts.append(_path_line(study, span, "#293b4c", 2.0, f"outline-{spec.name}-{index}"))
    for line in study.lines:
        owner = components[line.owner]
        occluders = tuple(c for c in components.values() if c.name != line.owner)
        spans = project_visible_semantic_segment(line.start, line.end, owner, study.camera, occluders)
        for index, span in enumerate(spans):
            parts.append(f'<!-- {html.escape(line.name)}: {html.escape(line.intent)} -->')
            parts.append(_path_line(study, span, line.color, line.width, f"line-{line.name}-{index}"))
    for index, (text, style, x, y) in enumerate(study.labels):
        parts.append(f'<!-- study-label-{index}: identifies the observed scope or action case -->')
        if style == "title":
            parts.append(f'<text id="study-label-{index}" x="{x}" y="{y}" font-family="sans-serif" font-size="13" fill="#34464e">{html.escape(text)}</text>')
        elif style == "panel":
            parts.append(f'<text id="study-label-{index}" x="{x}" y="{y}" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="600" fill="#26394a">{html.escape(text)}</text>')
        else:
            parts.append(f'<text id="study-label-{index}" x="{x}" y="{y}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#53616a">{html.escape(text)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"
