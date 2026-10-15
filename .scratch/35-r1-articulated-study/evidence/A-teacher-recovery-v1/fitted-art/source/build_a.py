"""Build the A-only garment family from frozen semantic parameters.

No reference, crop, trace, landmark, or teacher-overlay file is opened here.
Local family outlines are generated, support-bound into world space, projected,
then filled and stroked only through the existing triangle/depth adapters.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(REPO))
from scripts.articulated_construction import Camera, Component, Point, SupportFrame, component_faces, triangulate_polygon
from scripts.articulated_line_visibility import transform_compound_path, visible_segment_spans
from scripts.vector_visibility import visible_regions

ROOT = Path(__file__).resolve().parents[1]
PARAMS = ROOT / "source" / "semantic-parameters.json"
OUT = ROOT / "artwork-a.svg"
SAMPLES = 7


def read_params(path: Path = PARAMS) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def camera_from_params(params: dict) -> Camera:
    azimuth = math.radians(params["camera"]["azimuth_degrees"])
    elevation = math.radians(params["camera"]["elevation_degrees"])
    sa, ca = math.sin(azimuth), math.cos(azimuth)
    se, ce = math.sin(elevation), math.cos(elevation)
    return Camera((ca, 0.0, -sa), (-se * sa, ce, -se * ca), (ce * sa, se, ce * ca))


def support_frame(name: str, values: dict, camera: Camera) -> SupportFrame:
    """Inverse-place a true 3D plane so camera projection retains local crop framing."""
    depth = values["depth"]
    origin = tuple(depth * axis for axis in camera.depth)
    # A small continuous depth gradient makes each part a support plane, not a painter tag.
    u_axis = tuple(camera.horizontal[i] + values["slope_u"] * camera.depth[i] for i in range(3))
    v_axis = tuple(camera.vertical[i] + values["slope_v"] * camera.depth[i] for i in range(3))
    return SupportFrame(f"{name}-support", f"{name}-depth", origin, u_axis, v_axis)


def support_values_on_shared_edge(parent: dict, first: Point, second: Point, normal_gradient: float) -> dict:
    """Derive an adjacent support plane equal in world depth all along one shared edge."""
    dx, dy = second.u-first.u, second.v-first.v
    length = math.hypot(dx, dy)
    if length < 1e-9:
        raise ValueError("support contact edge must have nonzero length")
    nx, ny = -dy/length, dx/length
    slope_u = parent["slope_u"] + normal_gradient*nx
    slope_v = parent["slope_v"] + normal_gradient*ny
    edge_depth = parent["depth"] + parent["slope_u"]*first.u + parent["slope_v"]*first.v
    depth = edge_depth - slope_u*first.u - slope_v*first.v
    return {"depth": depth, "slope_u": slope_u, "slope_v": slope_v}


def catmull_path(points: list[Point], closed: bool = False, steps: int = SAMPLES) -> tuple[Point, ...]:
    """Sample a smooth semantic guide curve; all extra coordinates are generated."""
    if len(points) < 2:
        raise ValueError("a generated curve needs at least two anchors")
    result: list[Point] = []
    count = len(points) if closed else len(points) - 1
    for i in range(count):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        p0 = points[(i - 1) % len(points)] if closed or i > 0 else p1
        p3 = points[(i + 2) % len(points)] if closed or i + 2 < len(points) else p2
        for j in range(steps):
            t = j / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2*p1.u) + (-p0.u+p2.u)*t + (2*p0.u-5*p1.u+4*p2.u-p3.u)*t2 + (-p0.u+3*p1.u-3*p2.u+p3.u)*t3)
            y = 0.5 * ((2*p1.v) + (-p0.v+p2.v)*t + (2*p0.v-5*p1.v+4*p2.v-p3.v)*t2 + (-p0.v+3*p1.v-3*p2.v+p3.v)*t3)
            result.append(Point(x, y))
    result.append(points[0] if closed else points[-1])
    return tuple(result)


def point_pair(values) -> Point:
    return Point(float(values[0]), float(values[1]))


def line_points(points) -> tuple[Point, ...]:
    return catmull_path([point_pair(point) for point in points], closed=False, steps=5)


def ellipse(center, radii, count: int = 28) -> tuple[Point, ...]:
    cx, cy = map(float, center)
    rx, ry = map(float, radii)
    return tuple(Point(cx + rx * math.cos(2*math.pi*i/count), cy + ry * math.sin(2*math.pi*i/count)) for i in range(count))


def bow_loop(shape: dict, count: int = 30) -> tuple[Point, ...]:
    """Generate a closed soft loop with a knot-facing pinch and unequal loop parameters."""
    cx, cy = map(float, shape["center"])
    rx, ry = map(float, shape["radii"])
    pinch = float(shape["pinch"])
    direction = float(shape["pinch_direction"])
    points = []
    for i in range(count):
        angle = 2 * math.pi * i / count
        angular_distance = math.atan2(math.sin(angle - direction), math.cos(angle - direction))
        local_pinch = pinch * math.exp(-0.5 * (angular_distance / 0.58) ** 2)
        scale = 1.0 - local_pinch
        points.append(Point(cx + rx * scale * math.cos(angle), cy + ry * math.sin(angle)))
    return tuple(points)


def ribbon_tail(shape: dict, count: int = 12) -> tuple[Point, ...]:
    """Generate a tapered strip around four semantic route anchors, not a traced edge."""
    anchors = [point_pair(p) for p in shape["anchors"]]
    centerline = catmull_path(anchors, closed=False, steps=4)
    left, right = [], []
    total = len(centerline) - 1
    start_width, end_width = float(shape["width_start"]), float(shape["width_end"])
    for i, center in enumerate(centerline):
        before = centerline[max(0, i - 1)]
        after = centerline[min(total, i + 1)]
        dx, dy = after.u - before.u, after.v - before.v
        length = math.hypot(dx, dy)
        if length < 1e-9:
            raise ValueError("tail family has a degenerate tangent")
        t = i / total
        smooth = t*t*(3-2*t)
        width = start_width + (end_width-start_width)*smooth
        nx, ny = -dy / length, dx / length
        left.append(Point(center.u + nx*width/2, center.v + ny*width/2))
        right.append(Point(center.u - nx*width/2, center.v - ny*width/2))
    stride = max(1, len(centerline) // count)
    outline = left[::stride] + list(reversed(right[::stride]))
    return tuple(outline)


def bodice_outline(shape: dict) -> tuple[Point, ...]:
    anchors = shape["anchors"]
    left_shoulder, seam_top, seam_bottom, right_hem = [point_pair(anchors[name]) for name in ("left_shoulder", "sleeve_seam_top", "sleeve_seam_bottom", "right_hem")]
    shoulder_span = seam_top.u - left_shoulder.u
    opening_width = shoulder_span * float(shape["neck_opening_width_fraction"])
    left_neck = Point(left_shoulder.u + 0.23*shoulder_span, left_shoulder.v - 10)
    right_neck = Point(seam_top.u - 0.25*shoulder_span, seam_top.v - 12)
    notch = Point((left_neck.u + right_neck.u)/2, (left_neck.v + right_neck.v)/2 + float(shape["neck_opening_depth"]))
    # The neckline width is a semantic opening relation, not another typed contour.
    mid = (left_neck.u + right_neck.u)/2
    left_neck = Point(mid-opening_width/2, left_neck.v)
    right_neck = Point(mid+opening_width/2, right_neck.v)
    upper = catmull_path([left_shoulder, left_neck, notch, right_neck, seam_top], steps=5)
    shared = tuple(Point(seam_top.u+(seam_bottom.u-seam_top.u)*i/8, seam_top.v+(seam_bottom.v-seam_top.v)*i/8) for i in range(9))
    side_delta = right_hem.v-seam_bottom.v
    right_waist = Point(seam_bottom.u-0.08*shoulder_span, seam_bottom.v+float(shape["side_curve"])*side_delta)
    left_hem = Point(left_shoulder.u+float(shape["left_hem_fraction"])*(right_hem.u-left_shoulder.u), right_hem.v-4)
    left_waist = Point(left_shoulder.u-10, left_shoulder.v+0.47*(right_hem.v-left_shoulder.v))
    lower = catmull_path([seam_bottom, right_waist, right_hem, left_hem, left_waist, left_shoulder], steps=5)
    # Both bodice and sleeve use this exact shared seam path in opposite direction.
    return tuple(upper[:-1]) + shared + tuple(lower[1:-1])


def sleeve_family(shape: dict) -> tuple[tuple[Point, ...], tuple[Point, ...]]:
    """Generate contacting cap/tube surfaces without asserting an inked cloth seam."""
    anchors = shape["anchors"]
    join_top = point_pair(anchors["bodice_seam_top"])
    join_bottom = point_pair(anchors["bodice_seam_bottom"])
    cap = point_pair(anchors["cap_peak"])
    cuff = point_pair(anchors["cuff_center"])
    bulge = Point(cap.u + float(shape["outer_bulge"])*(cuff.u-cap.u), cap.v + float(shape["cap_tube_transition"])*(cuff.v-cap.v))
    half_w, half_h = 0.78*float(shape["cuff_half_height"]), 0.50*float(shape["cuff_half_height"])
    cuff_top = Point(cuff.u-half_w, cuff.v-half_h)
    cuff_bottom = Point(cuff.u+half_w, cuff.v+half_h)
    transition_inner = Point(join_bottom.u+0.53*(bulge.u-join_bottom.u), join_bottom.v+0.53*(bulge.v-join_bottom.v))
    outer_cap = catmull_path([join_top, cap, bulge], steps=6)
    cap_to_tube = tuple(Point(bulge.u+(transition_inner.u-bulge.u)*i/8, bulge.v+(transition_inner.v-bulge.v)*i/8) for i in range(9))
    inner_cap = tuple(Point(transition_inner.u+(join_bottom.u-transition_inner.u)*i/5, transition_inner.v+(join_bottom.v-transition_inner.v)*i/5) for i in range(6))
    body_seam = tuple(Point(join_bottom.u+(join_top.u-join_bottom.u)*i/8, join_bottom.v+(join_top.v-join_bottom.v)*i/8) for i in range(9))
    cap_shape = tuple(outer_cap[:-1]) + cap_to_tube + tuple(inner_cap[1:-1]) + body_seam

    outer_mid = Point(bulge.u+0.34*(cuff_bottom.u-bulge.u), bulge.v+0.42*(cuff_bottom.v-bulge.v))
    outer_tube = catmull_path([bulge, outer_mid, cuff_bottom], steps=5)
    cuff_opening = tuple(Point(cuff_bottom.u+(cuff_top.u-cuff_bottom.u)*i/8, cuff_bottom.v+(cuff_top.v-cuff_bottom.v)*i/8) for i in range(9))
    inner_mid = Point(join_bottom.u+0.38*(cuff_top.u-join_bottom.u), (cuff_top.v+join_bottom.v)/2)
    inner_tube = catmull_path([cuff_top, inner_mid, transition_inner], steps=5)
    cap_tube_seam = tuple(Point(transition_inner.u+(bulge.u-transition_inner.u)*i/8, transition_inner.v+(bulge.v-transition_inner.v)*i/8) for i in range(9))
    tube_shape = tuple(outer_tube[:-1]) + cuff_opening + tuple(inner_tube[1:-1]) + cap_tube_seam
    return cap_shape, tube_shape


def cuff_outline(shape: dict, sleeve: dict) -> tuple[Point, ...]:
    cx, cy = map(float, sleeve["anchors"]["cuff_center"])
    half_w = 0.78*float(sleeve["cuff_half_height"])
    half_h = 0.50*float(sleeve["cuff_half_height"])
    a = Point(cx-half_w, cy-half_h)
    b = Point(cx+half_w, cy+half_h)
    # The sleeve opening a→b is literally the cuff's shared attachment edge.
    extension = float(shape["overlap_into_sleeve"])
    nx, ny = -0.514, 0.857
    outer_a = Point(a.u+nx*extension*4, a.v+ny*extension*4)
    outer_b = Point(b.u+nx*extension*4, b.v+ny*extension*4)
    return a, b, outer_b, outer_a


def make_components(params: dict) -> tuple[tuple[Component, ...], dict[str, tuple[Point, ...]], Camera]:
    camera = camera_from_params(params)
    rel = params["relations"]
    supports = {name: dict(values) for name, values in params["supports"].items()}
    bodice = rel["bodice"]
    sleeve = rel["right_sleeve"]
    cuff = rel["cuff"]
    body_edge_a = point_pair(bodice["anchors"]["sleeve_seam_top"])
    body_edge_b = point_pair(bodice["anchors"]["sleeve_seam_bottom"])
    supports["sleeve"] = support_values_on_shared_edge(supports["bodice"], body_edge_a, body_edge_b, supports["sleeve"]["attachment_normal_depth_gradient"])
    cuff_edge_a, cuff_edge_b = cuff_outline(cuff, sleeve)[:2]
    supports["cuff"] = support_values_on_shared_edge(supports["sleeve"], cuff_edge_a, cuff_edge_b, supports["cuff"]["attachment_normal_depth_gradient"])
    def support(part, key): return support_frame(part, supports[key], camera)
    shapes: dict[str, tuple[Point, ...]] = {}
    components: list[Component] = []
    def add(name, intent, support_id, support_values, outline, fill, attachments=(), anchors=()):
        shape = tuple(outline)
        triangulate_polygon(shape)
        shapes[name] = shape
        components.append(Component(name, intent, support(support_id, support_values), shape, fill, tuple(attachments), tuple(anchors)))

    bodice_shape = bodice_outline(bodice)
    add("bodice", bodice["intent"], "bodice", "bodice", bodice_shape, params["palette"]["bodice"],
        anchors=(("shoulder-left", point_pair(bodice["anchors"]["left_shoulder"])), ("sleeve-seam-top", point_pair(bodice["anchors"]["sleeve_seam_top"])), ("sleeve-seam-bottom", point_pair(bodice["anchors"]["sleeve_seam_bottom"]))))

    skin = rel["neck_skin"]
    add("neck-skin-opening", skin["intent"], "neck_skin", "neck_skin", ellipse(skin["center"], skin["radius"]), params["palette"]["skin"])

    sleeve = rel["right_sleeve"]
    cap_shape, tube_shape = sleeve_family(sleeve)
    seam_anchors = (("seam-top", point_pair(sleeve["anchors"]["bodice_seam_top"])), ("seam-bottom", point_pair(sleeve["anchors"]["bodice_seam_bottom"])))
    add("puff-sleeve-cap", sleeve["intent"] + "; visible outer sleeve stays continuous", "sleeve-cap", "sleeve", cap_shape, params["palette"]["sleeve"],
        attachments=(("bodice", "sleeve-seam-top", "sleeve-seam-top"), ("bodice", "sleeve-seam-bottom", "sleeve-seam-bottom")), anchors=seam_anchors)
    add("right-sleeve-tube", "generated cuff-reaching tube; shares a construction join with the cap but draws no unsupported cap seam", "sleeve-tube", "sleeve", tube_shape, params["palette"]["sleeve"],
        attachments=(("puff-sleeve-cap", "cap-tube-outer", "cap-tube-outer"), ("puff-sleeve-cap", "cap-tube-inner", "cap-tube-inner")))

    cuff = rel["cuff"]
    cuff_shape = cuff_outline(cuff, sleeve)
    add("dark-cuff-band", cuff["intent"], "cuff", "cuff", cuff_shape, params["palette"]["ink"],
        attachments=(("right-sleeve-tube", "cuff-opening-left", "cuff-opening-left"), ("right-sleeve-tube", "cuff-opening-right", "cuff-opening-right")))

    for name in ("collar_left", "collar_right"):
        leaf = rel[name]
        anchors = [point_pair(p) for p in leaf["anchors"]]
        add(name.replace("_", "-"), leaf["intent"], "collar", "collar", catmull_path(anchors, closed=True), params["palette"][name])

    neighbor = rel["unclassified_blue_neighbor"]
    add("unclassified-blue-neighbor-fragment", neighbor["intent"], "neighbor", "neighbor", catmull_path([point_pair(p) for p in neighbor["anchors"]], closed=True), params["palette"]["band_unknown"])

    for name in ("bow_left_loop", "bow_right_loop"):
        loop = rel[name]
        add(name.replace("_", "-"), loop["intent"], "bow", "bow", bow_loop(loop), params["palette"]["bow"],
            attachments=(("bow-knot", "gathered-root", "knot-contact"),))
    knot = rel["bow_knot"]
    add("bow-knot", knot["intent"], "bow", "bow", ellipse(knot["center"], knot["radii"], 20), params["palette"]["bow"])
    for name in ("bow_left_tail", "bow_down_tail"):
        tail = rel[name]
        add(name.replace("_", "-"), tail["intent"], "bow", "bow", ribbon_tail(tail), params["palette"]["bow"],
            attachments=(("bow-knot", "tail-root", "knot-contact"),))
    return tuple(components), shapes, camera


def semantic_lines(params: dict) -> tuple[tuple[str, tuple[Point, ...], str, str, float], ...]:
    rel, ink = params["relations"], params["palette"]["ink"]
    left = rel["collar_left"]["anchors"]
    right = rel["collar_right"]["anchors"]
    # Three semantic marks on each leaf edge and four sparse cloth/fold cues.
    return (
        ("collar-left-front-binding", tuple(line_points([left[3], [182, 137], left[2]])), "collar-left", ink, rel["collar_left"]["trim_width"]),
        ("collar-right-front-binding", tuple(line_points([right[1], [252, 137], right[2]])), "collar-right", ink, rel["collar_right"]["trim_width"]),
        ("bodice-left-fold", line_points([[112, 206], [107, 250], [120, 292]]), "bodice", "#8c9a8b", 1.7),
        ("bodice-right-fold", line_points([[286, 220], [270, 266], [263, 309]]), "bodice", "#8c9a8b", 1.7),
        ("bow-left-fold", line_points([[157, 167], [143, 176], [130, 182]]), "bow-left-loop", "#74364f", 1.8),
        ("bow-right-fold", line_points([[184, 171], [207, 177], [220, 184]]), "bow-right-loop", "#74364f", 1.8),
        ("bow-tail-tension-fold", line_points([[164, 187], [159, 216], [151, 235]]), "bow-down-tail", "#77384f", 1.7),
    )


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def build_svg(params: dict | None = None) -> str:
    params = params or read_params()
    components, _shapes, camera = make_components(params)
    faces = component_faces(components, camera)
    paths = [f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="480" viewBox="0 0 400 480">',
             f'<rect id="crop-field-background" width="400" height="480" fill="{params["palette"]["background"]}"/>',
             '<!-- A only: observed shoulder/upper torso garment; no face, pose, hand or hidden anatomy -->']
    for path, fill, name in visible_regions(faces):
        paths.append(f'<!-- {escape(name)}: generated semantic family fill; support-frame depth-visible -->')
        paths.append(f'<path id="visible-{escape(name)}" d="{transform_compound_path(path, lambda x,y:(x,y))}" fill="{fill}" fill-rule="nonzero"/>')
    for name, local, owner, color, width in semantic_lines(params):
        support_owner = next((component for component in components if component.name == owner), None)
        if support_owner is None:
            raise ValueError(f"line owner {owner!r} has no component surface")
        world = [camera.project(support_owner.support.local_to_world(point)) for point in local]
        for index, (q0, q1) in enumerate(zip(world, world[1:])):
            for span, (t0, t1) in enumerate(visible_segment_spans(q0, q1, faces, owner)):
                a = (q0[0]+t0*(q1[0]-q0[0]), q0[1]+t0*(q1[1]-q0[1]))
                b = (q0[0]+t1*(q1[0]-q0[0]), q0[1]+t1*(q1[1]-q0[1]))
                paths.append(f'<!-- {escape(name)}: authored trim/fold line clipped by component depth -->')
                paths.append(f'<path id="{escape(name)}-{index}-{span}" d="M {_fmt(a[0])},{_fmt(a[1])} L {_fmt(b[0])},{_fmt(b[1])}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    paths.append('<text id="limited-scope-caption" x="200" y="458" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#28353a">A · observed collar, bow, sleeve &amp; upper bodice only</text>')
    paths.append('</svg>')
    return "\n".join(paths) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--params", type=Path, default=PARAMS)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    params = read_params(args.params)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(build_svg(params), encoding="utf-8")
    parts, shapes, camera = make_components(params)
    print(f"wrote {args.out}; {len(parts)} semantic parts; {sum(len(p) for p in shapes.values())} generated outline vertices; camera={camera}")


if __name__ == "__main__":
    main()
