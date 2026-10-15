#!/usr/bin/env python3
"""Build one A-only semantic garment scene from its local compact family parameters.

No reference, crop, landmark, trace or teacher path is accepted or opened here.
"""
from __future__ import annotations

import argparse
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[5]
SMOOTH_DIR = ROOT / ".scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SMOOTH_DIR) not in sys.path:
    sys.path.insert(0, str(SMOOTH_DIR))

from scripts.articulated_construction import Camera, Component, Point, SupportFrame, component_faces
from scripts.articulated_line_visibility import visible_segment_spans
from scripts.vector_visibility import visible_regions
from smooth_spatial import sample_closed_curve, validate_closed_contour

PARAMS_PATH = Path(__file__).with_name("semantic-parameters.json")
CAMERA = Camera()
WIDTH, HEIGHT = 400, 480


@dataclass(frozen=True)
class Built:
    component: Component
    authored_anchor_count: int
    family_name: str


@dataclass(frozen=True)
class Mark:
    name: str
    intent: str
    owner: str
    points: tuple[Point, ...]
    authored_anchor_count: int
    stroke: str
    width: float


def _screen_to_local(x: float, y_down: float) -> Point:
    return Point(float(x), HEIGHT - float(y_down))


def _local_to_screen(point: Point) -> tuple[float, float]:
    return point.u, HEIGHT - point.v


def _polyline(points: Iterable[tuple[float, float]]) -> tuple[Point, ...]:
    return tuple(_screen_to_local(x, y) for x, y in points)


def _support(name: str, spec: dict, contact: Point | None = None,
             contact_depth: float | None = None) -> SupportFrame:
    su = float(spec["u_depth_slope"])
    sv = float(spec["v_depth_slope"])
    if contact is not None:
        if contact_depth is None:
            raise ValueError("contact-aligned support needs a depth")
        z0 = contact_depth - su * contact.u - sv * contact.v
    else:
        z0 = float(spec["z"])
    return SupportFrame(name, f"{name}-support-depth", (0.0, 0.0, z0),
                        (1.0, 0.0, su), (0.0, 1.0, sv))


def _depth_at(support: SupportFrame, point: Point) -> float:
    return support.local_to_world(point)[2]


def _smooth(controls: Iterable[Point], tension: float = 0.42, steps: int = 8) -> tuple[Point, ...]:
    controls = tuple(controls)
    contour = sample_closed_curve(controls, steps_per_segment=steps, k=tension)
    validate_closed_contour(contour)
    return contour


def _ellipse_controls(center_xy: tuple[float, float], width: float, height: float,
                      angle_degrees: float = 0.0, count: int = 8,
                      x_bias: float = 0.0, y_bias: float = 0.0) -> tuple[Point, ...]:
    cx, cy = center_xy
    angle = math.radians(angle_degrees)
    controls = []
    for i in range(count):
        t = 2 * math.pi * i / count
        # A small smooth lobe bias keeps cloth from reading as a perfect geometric oval.
        rx = (width / 2) * math.cos(t) * (1 + x_bias * math.sin(t))
        ry = (height / 2) * math.sin(t) * (1 + y_bias * math.cos(t))
        x = cx + rx * math.cos(angle) - ry * math.sin(angle)
        y = cy + rx * math.sin(angle) + ry * math.cos(angle)
        controls.append(_screen_to_local(x, y))
    return tuple(controls)


def _part(name: str, intent: str, support: SupportFrame, fill: str,
          anchors: Iterable[tuple[str, Point]], controls: Iterable[Point], family: str,
          attachments: tuple[tuple[str, str, str], ...] = (),
          tension: float = 0.42) -> Built:
    anchors, controls = tuple(anchors), tuple(controls)
    if len(anchors) > 4:
        raise ValueError(f"{name}: exceeds four semantic input anchors")
    if not controls:
        raise ValueError(f"{name}: family emitted no controls")
    outline = _smooth(controls, tension=tension)
    component = Component(name, intent, support, outline, fill, attachments,
                          tuple(anchors))
    # Validate the actual triangulation path here, before any rendered candidate is emitted.
    from scripts.articulated_construction import triangulate_polygon
    triangulate_polygon(outline)
    return Built(component, len(anchors), family)


def _bodice_controls(p: dict) -> tuple[Point, ...]:
    a = p["artist_parameterization"]
    left, right, low_right, low_left = (_screen_to_local(*xy)
        for xy in a["four_station_anchors_xy_crop_down"])
    center_x, center_y = a["neck_opening_center_xy_crop_down"]
    half_open = a["neck_opening_width_px"] / 2
    depth = a["neck_opening_depth_px"]
    # Intermediate notch, side-ease and lower-return stations are generated from four anchors.
    neck_l = _screen_to_local(center_x - half_open, center_y - 8)
    neck_mid = _screen_to_local(center_x, center_y + depth)
    neck_r = _screen_to_local(center_x + half_open, center_y - 9)
    lower_mid = Point((low_left.u + low_right.u) / 2,
                      (low_left.v + low_right.v) / 2)
    left_waist = Point(left.u - a["left_side_inward_ease_px"] * 0.48,
                       left.v * 0.54 + low_left.v * 0.46)
    left_bow = Point(left.u - a["left_side_inward_ease_px"],
                     left.v * 0.72 + low_left.v * 0.28)
    right_waist = Point(right.u - 14, right.v * 0.55 + low_right.v * 0.45)
    right_lower = Point(right.u - 28, low_right.v + 2)
    # Ordered as a closed outline with a concave neckline opening, then broad shoulder and taper.
    return (left, neck_l, neck_mid, neck_r, right,
            right_waist, right_lower, low_right, lower_mid, low_left,
            left_waist, left_bow)


def _sleeve_controls(p: dict) -> tuple[Point, ...]:
    a = p["artist_parameterization"]
    start_xy, end_xy = a["shoulder_station_xy_crop_down"], a["cuff_approach_xy_crop_down"]
    dx, dy = end_xy[0] - start_xy[0], end_xy[1] - start_xy[1]
    length = math.hypot(dx, dy)
    if length <= 1e-8:
        raise ValueError("sleeve stations must differ")
    nx, ny = -dy / length, dx / length
    ts = (0.0, .14, .34, .56, .78, 1.0)
    widths = (a["upper_half_width_px"] * .56, a["upper_half_width_px"],
              a["upper_half_width_px"] * .96, a["mid_half_width_px"],
              a["cuff_half_width_px"] * 1.18, a["cuff_half_width_px"])
    side_a, side_b = [], []
    for t, width in zip(ts, widths):
        # The broad upper stations generate one puff mass, smoothly narrowing into the cuff approach.
        bulge = a["cap_bulge_px"] * math.sin(math.pi * t) * (1 - .38 * t)
        cx = start_xy[0] + dx * t + nx * bulge
        cy = start_xy[1] + dy * t + ny * bulge
        side_a.append(_screen_to_local(cx + nx * width, cy + ny * width))
        side_b.append(_screen_to_local(cx - nx * width, cy - ny * width))
    return tuple(side_a + list(reversed(side_b)))


def _ribbon_controls(start_xy: tuple[float, float], end_xy: tuple[float, float],
                     width: float, bend: float, stations: int = 6) -> tuple[Point, ...]:
    dx, dy = end_xy[0] - start_xy[0], end_xy[1] - start_xy[1]
    length = math.hypot(dx, dy)
    if length <= 1e-8:
        raise ValueError("ribbon relation stations must differ")
    nx, ny = -dy / length, dx / length
    side_a, side_b = [], []
    for i in range(stations):
        t = i / (stations - 1)
        bulge = bend * math.sin(math.pi * t)
        cx = start_xy[0] + dx * t + nx * bulge
        cy = start_xy[1] + dy * t + ny * bulge
        # Keep width nearly constant; generated end-cut geometry is hidden/unknown, not a point tip.
        w = width * (1 - .10 * t)
        side_a.append(_screen_to_local(cx + nx * w, cy + ny * w))
        side_b.append(_screen_to_local(cx - nx * w, cy - ny * w))
    return tuple(side_a + list(reversed(side_b)))


def _cuff_controls(p: dict, sleeve_start: tuple[float, float], sleeve_end: tuple[float, float]):
    a = p["artist_parameterization"]
    direction = math.degrees(math.atan2(sleeve_end[1] - sleeve_start[1],
                                        sleeve_end[0] - sleeve_start[0]))
    return _ellipse_controls(a["center_xy_crop_down"], a["band_length_px"],
                             2 * a["half_width_px"], direction + 90, count=8,
                             x_bias=.02)


def _loop_controls(p: dict) -> tuple[Point, ...]:
    a = p["artist_parameterization"]
    return _ellipse_controls(a["field_center_seed_xy_crop_down"], a["width_px"],
                             a["height_px"], a["tilt_degrees"], count=10,
                             x_bias=.08, y_bias=.05)


def _curve_points(points: tuple[Point, Point, Point, Point], steps: int = 12) -> tuple[Point, ...]:
    a, b, c, d = points
    result = []
    for i in range(steps + 1):
        t = i / steps
        s = 1 - t
        result.append(Point(s**3 * a.u + 3*s*s*t*b.u + 3*s*t*t*c.u + t**3*d.u,
                            s**3 * a.v + 3*s*s*t*b.v + 3*s*t*t*c.v + t**3*d.v))
    return tuple(result)


def _mark(name: str, intent: str, owner: str, crop_points: Iterable[tuple[float, float]],
          color: str, width: float) -> Mark:
    points = _polyline(crop_points)
    if not 2 <= len(points) <= 4:
        raise ValueError(f"{name}: use two to four semantic relation anchors")
    return Mark(name, intent, owner, points, len(points), color, width)


def build_scene() -> tuple[tuple[Built, ...], tuple[Mark, ...], dict]:
    """Create the local parameterized A garment family; this function never reads a target."""
    p = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    parts, support_params = p["parts"], p["supports"]
    built: list[Built] = []
    body_anchor = _screen_to_local(292, 164)
    body_support = _support("A-bodice-support", support_params["body"])
    bodice_part = parts["bodice"]
    bodice = _part("A-bodice", bodice_part["intent"], body_support,
        bodice_part["artist_parameterization"]["palette"],
        (("sleeve-seat", body_anchor),),
        _bodice_controls(bodice_part), "four-station-neckline-bodice")
    built.append(bodice)

    skin_data = parts["neck_skin"]
    skin_a = skin_data["artist_parameterization"]
    skin_controls = _ellipse_controls(skin_a["center_xy_crop_down"],
        2 * skin_a["ellipse_radii_px"][0], 2 * skin_a["ellipse_radii_px"][1],
        skin_a["tilt_degrees"], count=8)
    skin_support = _support("A-neck-skin-support", support_params["skin"])
    built.append(_part("A-visible-neck-skin", skin_data["intent"], skin_support,
        "#d7a9a7", (("neck-field", _screen_to_local(218, 82)),), skin_controls,
        "local-skin-field-ellipse"))

    for key, name in (("left_collar_leaf", "A-collar-left"),
                      ("right_collar_leaf", "A-collar-right")):
        data = parts[key]
        a = data["artist_parameterization"]
        controls = _ellipse_controls(a["field_center_seed_xy_crop_down"],
            a["width_px"] * a["outer_reach_scale"], a["height_px"],
            a["tilt_degrees"], count=8, x_bias=.11, y_bias=.08)
        support = _support(name + "-support", support_params["collar"])
        built.append(_part(name, data["intent"], support, a["palette"],
            (("field-center", _screen_to_local(*a["field_center_seed_xy_crop_down"])),),
            controls, "independent-asymmetric-collar-leaf"))

    sleeve_data = parts["puff_sleeve"]
    sleeve_a = sleeve_data["artist_parameterization"]
    sleeve_start, sleeve_end = sleeve_a["shoulder_station_xy_crop_down"], sleeve_a["cuff_approach_xy_crop_down"]
    sleeve_support = _support("A-continuous-sleeve-support", support_params["sleeve"],
                              body_anchor, _depth_at(body_support, body_anchor))
    sleeve = _part("A-continuous-puff-sleeve", sleeve_data["intent"], sleeve_support,
        sleeve_a["palette"], (("bodice-seat", body_anchor), ("cuff-seat", _screen_to_local(*sleeve_end))),
        _sleeve_controls(sleeve_data), "single-puff-to-tube-family",
        attachments=(("A-bodice", "bodice-seat", "sleeve-seat"),),
        tension=sleeve_a["curve_tension"])
    built.append(sleeve)

    cuff_data = parts["dark_cuff"]
    cuff_a = cuff_data["artist_parameterization"]
    cuff_center = _screen_to_local(*cuff_a["center_xy_crop_down"])
    sleeve_depth = _depth_at(sleeve_support, cuff_center)
    cuff_support = _support("A-cuff-support", support_params["cuff"], cuff_center, sleeve_depth)
    cuff_controls = _cuff_controls(cuff_data, sleeve_start, sleeve_end)
    built.append(_part("A-dark-cuff-band", cuff_data["intent"], cuff_support,
        cuff_a["palette"], (("tube-contact", cuff_center),), cuff_controls,
        "local-transverse-cuff-band", attachments=(("A-continuous-puff-sleeve", "tube-contact", "cuff-seat"),)))

    knot_data = parts["bow_gather"]
    knot_a = knot_data["artist_parameterization"]
    knot_support = _support("A-bow-gather-support", support_params["bow"])
    knot_controls = _ellipse_controls(knot_a["center_xy_crop_down"], knot_a["width_px"],
        knot_a["height_px"], -12, count=8, x_bias=.06)
    knot = _part("A-bow-gather", knot_data["intent"], knot_support, knot_a["palette"],
        (("gather", _screen_to_local(*knot_a["center_xy_crop_down"])),),
        knot_controls, "compact-gather-ellipse")
    built.append(knot)

    for key, name in (("left_bow_loop", "A-bow-left-loop"),
                      ("right_bow_loop", "A-bow-right-loop")):
        data = parts[key]
        a = data["artist_parameterization"]
        support = _support(name + "-support", support_params["bow"])
        loop_center_xy = a["field_center_seed_xy_crop_down"]
        loop_anchors = [("field-center", _screen_to_local(*loop_center_xy))]
        if key == "left_bow_loop":
            left_attach_offset = parts["leftward_tail_fragment"]["artist_parameterization"]["left_loop_attachment_offset_xy"]
            left_root_xy = (loop_center_xy[0] + left_attach_offset[0],
                            loop_center_xy[1] + left_attach_offset[1])
            loop_anchors.append(("tail-root", _screen_to_local(*left_root_xy)))
        loop = _part(name, data["intent"], support, a["palette"],
            tuple(loop_anchors), _loop_controls(data), "rounded-nontip-folded-lobe")
        built.append(loop)

    # Tails are explicitly authored incomplete bands. The downward one enters the bodice depth
    # and disappears under it; the leftward one runs into an identity-unknown blue neighbor.
    down = parts["down_tail_fragment"]
    down_a = down["artist_parameterization"]
    knot_xy = knot_a["center_xy_crop_down"]
    angle = math.radians(down_a["orientation_degrees_screen"])
    down_end = (knot_xy[0] + math.cos(angle) * down_a["hypothesis_route_length_px"],
                knot_xy[1] + math.sin(angle) * down_a["hypothesis_route_length_px"])
    down_start = (knot_xy[0] + math.cos(angle) * 11, knot_xy[1] + math.sin(angle) * 11)
    down_start_local = _screen_to_local(*down_start)
    down_slope_v = .0082
    down_depth_params = {"u_depth_slope": 0.0, "v_depth_slope": down_slope_v}
    desired_front_depth = _depth_at(knot_support, down_start_local) - .015
    down_support = _support("A-down-tail-support", down_depth_params,
                            down_start_local, desired_front_depth)
    down_controls = _ribbon_controls(down_start, down_end, down_a["width_px"] / 2,
                                     bend=-5.0, stations=6)
    built.append(_part("A-down-tail-visible-fragment", down["intent"], down_support,
        down_a["palette"], (("gather-near", _screen_to_local(*down_start)),),
        down_controls, "partial-down-band-depth-fades-under-cloth"))

    left = parts["leftward_tail_fragment"]
    left_a = left["artist_parameterization"]
    loop_center = parts["left_bow_loop"]["artist_parameterization"]["field_center_seed_xy_crop_down"]
    attach_offset = left_a["left_loop_attachment_offset_xy"]
    left_start = (loop_center[0] + attach_offset[0], loop_center[1] + attach_offset[1])
    # This compact generated relation is an artist hypothesis, not a sampled/verified axis.
    # Its arrival enters the observed contact neighborhood and is occluded by identity-unknown blue.
    left_end = (left_a["contact_neighborhood_xy_crop_down"][0] + 5,
                left_a["contact_neighborhood_xy_crop_down"][1] + 3)
    left_start_local = _screen_to_local(*left_start)
    left_loop_component = next(b.component for b in built if b.component.name == "A-bow-left-loop")
    left_support = _support("A-left-tail-support", support_params["tail"], left_start_local,
                             _depth_at(left_loop_component.support, left_start_local))
    left_controls = _ribbon_controls(left_start, left_end, left_a["width_px"] / 2,
                                     bend=left_a["route_bend_px"], stations=7)
    built.append(_part("A-leftward-tail-local-band", left["intent"], left_support,
        left_a["palette"], (("loop-root", left_start_local),), left_controls,
        "artist-route-occluded-at-unknown-contact",
        attachments=(("A-bow-left-loop", "loop-root", "tail-root"),)))

    blue_data = parts["unknown_blue_neighbor"]
    blue_a = blue_data["artist_parameterization"]
    blue_support = _support("A-unknown-blue-neighbor-support", support_params["blue_neighbor"])
    blue_controls = _ellipse_controls(blue_a["contact_neighborhood_xy_crop_down"],
        blue_a["width_px"], blue_a["height_px"], -28, count=8, x_bias=.12)
    built.append(_part("A-identity-unknown-blue-neighbor", blue_data["intent"], blue_support,
        blue_a["palette"], (("contact-neighborhood", _screen_to_local(*blue_a["contact_neighborhood_xy_crop_down"])),),
        blue_controls, "unknown-identity-local-neighbor"))

    # Named intent marks are few semantic curves. Every segment passes through the same depth engine.
    marks = []
    trim = _curve_points((_screen_to_local(171, 122), _screen_to_local(185, 145),
                          _screen_to_local(224, 146), _screen_to_local(245, 120)))
    marks.append(Mark("A-neckline-dark-trim", "visible curved trim around the authored skin opening",
        "A-bodice", trim, 4, "#293243", 3.2))
    marks.append(_mark("A-bodice-left-fold", "short cloth fold descends toward chest gathering",
        "A-bodice", ((131, 235), (145, 262), (159, 276)), "#b8b7a9", 1.7))
    marks.append(_mark("A-bodice-right-fold", "soft short fold approaches the gathering point",
        "A-bodice", ((257, 245), (238, 261), (215, 272)), "#c4c1b2", 1.6))
    marks.append(_mark("A-sleeve-cap-fold", "brief puff highlight follows upper sleeve volume",
        "A-continuous-puff-sleeve", ((313, 163), (328, 154), (341, 162)), "#c1c6bb", 2.1))
    marks.append(_mark("A-sleeve-tube-fold", "short tapered fold approaches cuff without a cap seam",
        "A-continuous-puff-sleeve", ((340, 229), (349, 246), (351, 265)), "#b6b9ae", 1.8))
    marks.append(_mark("A-left-loop-crease", "one generated fold direction inside left rounded loop",
        "A-bow-left-loop", ((133, 163), (143, 175), (158, 184)), "#ee94aa", 1.9))
    marks.append(_mark("A-right-loop-crease", "one generated fold direction inside broader right loop",
        "A-bow-right-loop", ((226, 169), (242, 185), (256, 199)), "#f29bb2", 2.0))
    marks.append(_mark("A-knot-gathers", "two short gather strokes converge inside the bow knot",
        "A-bow-gather", ((173, 177), (179, 181), (185, 185)), "#f2a4b8", 1.7))
    return tuple(built), tuple(marks), p


def _screen_world(support: SupportFrame, point: Point) -> tuple[float, float, float]:
    return CAMERA.project(support.local_to_world(point))


def _line_svg(mark: Mark, owner: Component, faces: tuple) -> list[str]:
    visible = []
    world = tuple(_screen_world(owner.support, p) for p in mark.points)
    for segment_index, (start, end) in enumerate(zip(world, world[1:])):
        spans = visible_segment_spans(start, end, faces, owner.name)
        for span_index, (lo, hi) in enumerate(spans):
            a = tuple(start[i] + (end[i] - start[i]) * lo for i in range(3))
            b = tuple(start[i] + (end[i] - start[i]) * hi for i in range(3))
            visible.append(f'<path id="{html.escape(mark.name)}-{segment_index}-{span_index}" d="M {a[0]:.6f},{HEIGHT-a[1]:.6f} L {b[0]:.6f},{HEIGHT-b[1]:.6f}" fill="none" stroke="{mark.stroke}" stroke-width="{mark.width:.3f}" stroke-linecap="round" stroke-linejoin="round"/>')
    return visible


def render_svg() -> tuple[str, dict]:
    built, marks, params = build_scene()
    components = tuple(entry.component for entry in built)
    by_name = {component.name: component for component in components}
    faces = component_faces(components, CAMERA)
    regions = tuple(visible_regions(faces))
    output = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
              '<title>A garment study — observed shoulder and upper-torso clothing only</title>',
              '<desc>Generated local family fit; closed structures and joins are artist parameterization, not recovered hidden anatomy.</desc>',
              '<!-- A-nearby-context-field: adjacent teal environment behind the bounded garment study -->',
              '<rect id="A-nearby-context-field" x="0" y="0" width="400" height="480" fill="#78a49b"/>']
    for path, color, name in regions:
        component = by_name[name]
        screen_path = _transform_fill_path(path)
        output.append(f'<!-- {html.escape(component.name)}: {html.escape(component.intent)} -->')
        output.append(f'<path id="fill-{html.escape(component.name)}" data-part="{html.escape(component.name)}" d="{screen_path}" fill="{color}" fill-rule="nonzero"/>')
    # Outline strokes and all semantic marks use identical support and depth visibility.
    for entry in built:
        component = entry.component
        world = tuple(_screen_world(component.support, p) for p in component.outline)
        output.append(f'<!-- {html.escape(component.name)} boundary: generated contour, clipped by actual scene depth -->')
        for i, start in enumerate(world):
            end = world[(i + 1) % len(world)]
            for span_index, (lo, hi) in enumerate(visible_segment_spans(start, end, faces, component.name)):
                a = tuple(start[j] + (end[j] - start[j]) * lo for j in range(3))
                b = tuple(start[j] + (end[j] - start[j]) * hi for j in range(3))
                output.append(f'<path id="edge-{html.escape(component.name)}-{i}-{span_index}" d="M {a[0]:.6f},{HEIGHT-a[1]:.6f} L {b[0]:.6f},{HEIGHT-b[1]:.6f}" fill="none" stroke="#34424c" stroke-width="1.35" stroke-linecap="round"/>')
    for mark in marks:
        output.append(f'<!-- {html.escape(mark.name)}: {html.escape(mark.intent)} -->')
        output.extend(_line_svg(mark, by_name[mark.owner], faces))
    output.append('</svg>')
    metadata = {
        "parts": [{"name": b.component.name, "intent": b.component.intent,
                   "family": b.family_name, "author_anchor_count": b.authored_anchor_count,
                   "generated_outline_vertices": len(b.component.outline),
                   "support_id": b.component.support.support_id,
                   "depth_ref": b.component.support.depth_ref,
                   "attachments": list(b.component.attachments)} for b in built],
        "marks": [{"name": m.name, "intent": m.intent, "owner": m.owner,
                   "author_anchor_count": m.authored_anchor_count} for m in marks],
        "projected_faces": len(faces),
        "visible_fill_regions": len(regions),
        "parameters": params,
    }
    return "\n".join(output) + "\n", metadata


def _transform_fill_path(path: str) -> str:
    # Keep compound M/L/Z subpaths intact while mapping projected y-up to crop y-down.
    from scripts.articulated_line_visibility import transform_compound_path
    return transform_compound_path(path, lambda x, y: (x, HEIGHT - y))


def main() -> int:
    parser = argparse.ArgumentParser(description="render the local A garment family; no reference input")
    parser.add_argument("--out", required=True, help="destination SVG path")
    args = parser.parse_args()
    svg, metadata = render_svg()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print(json.dumps({"svg": str(out), "parts": len(metadata["parts"]),
                      "faces": metadata["projected_faces"],
                      "visible_fill_regions": metadata["visible_fill_regions"],
                      "generated_vertices": sum(p["generated_outline_vertices"] for p in metadata["parts"])},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
