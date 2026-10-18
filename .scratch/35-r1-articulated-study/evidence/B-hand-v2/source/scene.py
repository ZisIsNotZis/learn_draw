"""B-hand-v2: the confirmed three-panel supported-dish study with a constructed hand.

Concept, variation and control are unchanged from the reviewed sheet: a bent arm
carries a small fruit dish at chest level (baseline), lifted with a broader dish
(variation), and the dish displaced away from a still hand (control). What is new
is the hand: a palm cup whose contact rim is derived from the dish underside, and
four individually posed fingers plus a thumb, each built by the tapered-tube
primitive in ``hand_family``. Depth, not paint order, decides what covers what.

Geometry is derived wherever the drawing has a physical relation to state:
the palm's rim edge is the dish's foot line, each fingertip is placed against the
dish's rim band, the wrist comes from the arm's two-bone reach, and the dish's
width/depth drive all of it. Only proportions and stand-off margins are authored.
"""
from __future__ import annotations
from dataclasses import dataclass
import html
import math
import re
from typing import Iterable

from scripts.articulated_construction import (
    Camera, Component, LimbParameters, Point, SupportFrame, construct_limb,
    polygons_overlap, _overlap_samples, _world_xy_outline, _world_z_at_xy,
)
from spatial_adapter import (
    VisibleSmoothComponent, build_visible_smooth_component, project_visible_semantic_path,
    sample_closed_curve, validate_closed_contour,
)
from hand_family import PalmCup, Tube, mix, palm_cup, perp, shifted, tapered_digit, unit


@dataclass(frozen=True)
class ShapeSpec:
    name: str
    intent: str
    support: SupportFrame
    fill: str
    controls: tuple[Point, ...]  # generated family output consumed by the guarded sampler
    authored_anchors: tuple[Point, ...]
    attachments: tuple[tuple[str, str, str], ...] = ()
    semantic_anchors: tuple[tuple[str, Point], ...] = ()
    family: str = "relation-generated"


@dataclass(frozen=True)
class LineSpec:
    name: str
    intent: str
    owner: str
    points: tuple[Point, ...]
    authored_anchors: tuple[Point, ...]
    color: str = "#253443"
    width: float = 2.0


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
    panel_width: int = 0


@dataclass(frozen=True)
class RimBand:
    """The dish's glazed rim ellipse, in the dish-front plane's coordinates."""
    center: Point
    rx: float
    ry: float

    def near_point(self, degrees: float) -> Point:
        """Point on the lower (near) rim arc at an ellipse parameter angle."""
        phi = math.radians(degrees)
        return Point(self.center.u + self.rx * math.cos(phi),
                     self.center.v - self.ry * math.sin(phi))

    def inward_normal(self, degrees: float) -> Point:
        """Unit normal pointing from the near arc back into the rim band."""
        phi = math.radians(degrees)
        return unit(Point(-math.cos(phi) / self.rx, math.sin(phi) / self.ry))

    def boundary_distance(self, point: Point, samples: int = 720) -> float:
        """Nearest distance from a point to the rim band boundary (independent of the generator)."""
        best = float("inf")
        for index in range(samples):
            phi = math.pi * index / samples
            candidate = self.near_point(math.degrees(phi))
            best = min(best, math.hypot(point.u - candidate.u, point.v - candidate.v))
        return best


@dataclass(frozen=True)
class DigitSpec:
    """Authored proportions and stations for one digit; its positions are derived elsewhere."""
    name: str
    intent: str
    knuckle_fraction: float      # where along the palm's own knuckle edge this digit sits
    rim_angle_degrees: float     # which station of the dish's rim band its tip reaches
    reach_margin: float          # authored stand-off between fingertip edge and dish silhouette
    base_half: float
    tip_half: float
    joint_dip: float
    bow: float
    depth_offset: float


@dataclass(frozen=True)
class DeclaredContact:
    """A contact the scene asserts, with the measured quantities the validator re-checks."""
    owner_a: str
    owner_b: str
    points_a: tuple[Point, ...]
    points_b: tuple[Point, ...]
    max_projected_gap: float
    depth_separation: float
    claim: str


# --- proportion table: authored design values, not measurements of anything -----
HAND_DEPTH_SLOPE = 0.03        # hand surface tilts toward the viewer, as in the reviewed sheet
CONTACT_INSET = 0.006          # palm rim edge tucks this far under the dish foot (hidden)
DISH_DEPTH_OFFSET = 0.012      # dish surface sits this far in front of the palm plane
KNUCKLE_DROP = 0.34            # length of the palm's knuckle edge, down from the dish's foot line
PALM_WRIST_HALF = 0.100        # palm width at the wrist (the forearm's wrist half-width is 0.09)
KNUCKLE_SETBACK = 0.030        # finger bases sit this far inside the palm's knuckle edge
CONTACT_FRACTION = 0.50        # the palm's cup holds the dish foot out to this fraction of its span
FINGERS = (
    DigitSpec("index", "index finger climbs the dish wall to the near rim and reaches it first",
              0.08, 74.0, 0.010, 0.037, 0.025, 0.10, -0.14, 0.0140),
    DigitSpec("middle", "middle finger is the longest digit and meets the rim band",
              0.37, 88.0, 0.008, 0.039, 0.027, 0.10, -0.04, 0.0152),
    DigitSpec("ring", "ring finger meets the rim band beside the middle finger",
              0.66, 103.0, 0.010, 0.037, 0.026, 0.10, 0.06, 0.0164),
    DigitSpec("little", "little finger stops short of the rim band",
              0.93, 118.0, 0.026, 0.033, 0.022, 0.10, 0.14, 0.0176),
)
THUMB = DigitSpec("thumb", "thumb rises on the palm's thenar side to the dish's left rim band",
                  0.62, 146.0, 0.020, 0.058, 0.036, 0.08, -0.22, 0.0200)

def _bezier(a: Point, b: Point, c: Point, d: Point, steps: int = 5) -> tuple[Point, ...]:
    return tuple(Point((1 - t) ** 3 * a.u + 3 * (1 - t) ** 2 * t * b.u + 3 * (1 - t) * t * t * c.u + t ** 3 * d.u,
                       (1 - t) ** 3 * a.v + 3 * (1 - t) ** 2 * t * b.v + 3 * (1 - t) * t * t * c.v + t ** 3 * d.v)
                 for index in range(steps) for t in (index / steps,))


def _closed_spans(spans: Iterable[tuple[Point, Point, Point, Point]], steps: int = 5) -> tuple[Point, ...]:
    result = []
    for span in spans:
        result.extend(_bezier(*span, steps=steps))
    return tuple(result)


def _ellipse_controls(center: Point, rx: float, ry: float) -> tuple[Point, ...]:
    """Four derived cardinal controls; centre and radii are semantic parameters."""
    return (Point(center.u - rx, center.v), Point(center.u, center.v + ry),
            Point(center.u + rx, center.v), Point(center.u, center.v - ry))


def _shape(name: str, intent: str, support: SupportFrame, fill: str,
           anchors: Iterable[Point], generated: Iterable[Point], *, family: str,
           attachments: tuple[tuple[str, str, str], ...] = (),
           semantic_anchors: tuple[tuple[str, Point], ...] = ()) -> ShapeSpec:
    anchors, generated = tuple(anchors), tuple(generated)
    if not 1 <= len(anchors) <= 4:
        raise ValueError(f"{name}: semantic author input count must be 1..4, got {len(anchors)}")
    if len(generated) < 3:
        raise ValueError(f"{name}: grammar emitted too few curve controls")
    return ShapeSpec(name, intent, support, fill, generated, anchors, attachments,
                     semantic_anchors, family)


def _line(name: str, intent: str, owner: str, source_anchors: Iterable[Point],
          generated: Iterable[Point], color: str = "#253443", width: float = 2.0) -> LineSpec:
    anchors, points = tuple(source_anchors), tuple(generated)
    if len(anchors) > 4:
        raise ValueError(f"{name}: line author inputs exceed four anchors")
    if len(points) < 2:
        raise ValueError(f"{name}: semantic line needs at least two generated points")
    return LineSpec(name, intent, owner, points, anchors, color, width)


def _line_curve(a: Point, b: Point, bend: float, steps: int = 8) -> tuple[Point, ...]:
    direction = Point(b.u - a.u, b.v - a.v)
    normal = perp(unit(direction))
    mid = mix(a, b, 0.5)
    control_a = shifted(mix(a, mid, 0.66), normal, bend)
    control_b = shifted(mix(mid, b, 0.34), normal, bend)
    return _bezier(a, control_a, control_b, b, steps)


def _cardinal_controls(generated_outline: tuple[Point, ...]) -> tuple[Point, ...]:
    """Compact generative curve handles from a validated method output; never an authored contour."""
    if len(generated_outline) < 12:
        raise ValueError("generated limb outline is too small")
    return tuple(generated_outline[index] for index in
                 (0, len(generated_outline) // 4, len(generated_outline) // 2, 3 * len(generated_outline) // 4))


def _dish_body(center: Point, radius: float, depth: float) -> tuple[Point, ...]:
    """Shallow bowl with a short flat foot edge; the hand's contact derives from that foot."""
    left = Point(center.u - radius, center.v)
    right = Point(center.u + radius, center.v)
    foot_r = Point(center.u + radius * 0.48, center.v - depth)
    foot_l = Point(center.u - radius * 0.48, center.v - depth)
    foot_mid = Point(center.u, center.v - depth)
    return _closed_spans(((left, Point(center.u - radius * 0.55, center.v + depth * 0.10),
                           Point(center.u + radius * 0.55, center.v + depth * 0.10), right),
                          (right, Point(right.u - radius * 0.10, right.v - depth * 0.65),
                           Point(foot_r.u + radius * 0.08, foot_r.v), foot_r),
                          (foot_r, mix(foot_r, foot_mid, 0.34), mix(foot_r, foot_mid, 0.72), foot_mid),
                          (foot_mid, mix(foot_mid, foot_l, 0.28), mix(foot_mid, foot_l, 0.66), foot_l),
                          (foot_l, Point(foot_l.u - radius * 0.08, foot_l.v),
                           Point(left.u + radius * 0.10, left.v - depth * 0.65), left)))


def _point_on_segment(point: Point, a: Point, b: Point, epsilon: float = 1e-9) -> bool:
    cross = (b.u - a.u) * (point.v - a.v) - (b.v - a.v) * (point.u - a.u)
    if abs(cross) > epsilon * max(1.0, math.hypot(b.u - a.u, b.v - a.v)):
        return False
    dot = (point.u - a.u) * (b.u - a.u) + (point.v - a.v) * (b.v - a.v)
    return -epsilon <= dot <= (b.u - a.u) ** 2 + (b.v - a.v) ** 2 + epsilon


def dish_foot_contact(contour: tuple[Point, ...], stations: int = 5) -> tuple[Point, ...]:
    """Read the dish's foot out of its own contour and return evenly spaced contact stations."""
    lowest = min(point.v for point in contour)
    run = sorted((point for point in contour if point.v <= lowest + 1e-9), key=lambda point: point.u)
    if len(run) < 2:
        raise ValueError("dish contour exposes no flat foot to support")
    left, right = run[0], run[-1]
    contact = tuple(Point(left.u + (right.u - left.u) * index / (stations - 1), lowest)
                    for index in range(stations))
    for point in contact:
        if not any(_point_on_segment(point, a, b) for a, b in zip(run, run[1:])):
            raise ValueError("derived dish contact station is not on the dish contour")
    return contact


def _hand_support(case: str, label: str, z_origin: float) -> SupportFrame:
    return SupportFrame(f"{case}-{label}", f"{case}-{label}-depth",
                        origin=(0.0, 0.0, z_origin), u_axis=(1.0, 0.0, HAND_DEPTH_SLOPE),
                        v_axis=(0.0, 1.0, 0.0))


@dataclass(frozen=True)
class HandAssembly:
    palm: ShapeSpec
    fingers: tuple[ShapeSpec, ...]
    thumb: ShapeSpec
    palm_geometry: PalmCup
    digit_tubes: dict[str, Tube]
    contact_edge: tuple[Point, ...]


def dish_side_wall(contour: tuple[Point, ...], dish_center: Point, side: str) -> tuple[tuple[Point, Point], ...]:
    """Read one side wall out of the dish's own contour as (silhouette point, outward normal) pairs.

    "Left" and "right" are the two silhouette runs between the foot and the dish's mid height;
    the outward normal is radial from the dish centre, so the stations are the dish's own shape.
    """
    if side not in {"left", "right"}:
        raise ValueError("dish side must be 'left' or 'right'")
    sign = 1.0 if side == "right" else -1.0
    lowest = min(point.v for point in contour)
    run = [point for point in contour
           if (point.u - dish_center.u) * sign > 0
           and lowest - 1e-9 <= point.v <= dish_center.v + 1e-9]
    if len(run) < 4:
        raise ValueError(f"dish {side} wall could not be read from its contour")
    run.sort(key=lambda point: point.v)
    return tuple((point, unit(Point(point.u - dish_center.u, point.v - dish_center.v)))
                 for point in run)


def _wall_station(wall: tuple[tuple[Point, Point], ...], fraction: float) -> tuple[Point, Point]:
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("digit wall fraction must lie in [0, 1]")
    span = (len(wall) - 1) * fraction
    index = min(len(wall) - 2, int(span))
    t = span - index
    return (mix(wall[index][0], wall[index + 1][0], t),
            unit(mix(wall[index][1], wall[index + 1][1], t)))


def build_hand(case: str, foot: tuple[Point, ...], rim: "RimBand", wrist: Point,
               hand_z: float, fill: str) -> HandAssembly:
    """Palm cup, four fingers and a thumb, all derived from the dish geometry and the wrist.

    Derived (geometric consequence): the palm's contact rim is the dish's own foot line out to
    CONTACT_FRACTION of its span; each fingertip is placed a declared stand-off outside a station
    on the dish's own side-wall silhouette; the thumb likewise on the opposite wall. Authored
    (hypothesis): the stand-off margins, widths, taper and bow, i.e. how the hand holds.
    """
    foot_mid = mix(foot[0], foot[-1], 0.5)
    axis = unit(Point(foot_mid.u - wrist.u, foot_mid.v - wrist.v))
    across = perp(axis)
    contact_count = max(2, int(round(CONTACT_FRACTION * (len(foot) - 1))) + 1)
    contact_edge = tuple(Point(point.u, point.v + CONTACT_INSET) for point in foot[:contact_count])
    knuckle_top = contact_edge[-1]
    knuckle_bottom = shifted(knuckle_top, across, -KNUCKLE_DROP)
    wrist_upper = shifted(wrist, across, PALM_WRIST_HALF)
    wrist_lower = shifted(wrist, across, -PALM_WRIST_HALF)

    def spline(span: tuple[Point, Point, Point, Point], steps: int = 6) -> list[Point]:
        a, c1, c2, b = span
        points = []
        for index in range(steps + 1):
            t = index / steps
            s = 1 - t
            points.append(Point(s ** 3 * a.u + 3 * s * s * t * c1.u + 3 * s * t * t * c2.u + t ** 3 * b.u,
                                s ** 3 * a.v + 3 * s * s * t * c1.v + 3 * s * t * t * c2.v + t ** 3 * b.v))
        return points

    distal = spline((knuckle_top,
                     shifted(mix(knuckle_top, knuckle_bottom, 0.35), axis, 0.030),
                     shifted(mix(knuckle_top, knuckle_bottom, 0.72), axis, 0.022),
                     knuckle_bottom))
    ulnar = spline((knuckle_bottom,
                    shifted(mix(knuckle_bottom, wrist_lower, 0.30), across, -0.055),
                    shifted(mix(knuckle_bottom, wrist_lower, 0.72), across, -0.040),
                    wrist_lower))
    wrist_cap = [shifted(wrist,
                         Point(across.u * math.cos(theta) - axis.u * math.sin(theta),
                               across.v * math.cos(theta) - axis.v * math.sin(theta)),
                         PALM_WRIST_HALF)
                 for theta in (math.pi - math.pi * k / 5 for k in range(6))]
    thenar = spline((wrist_upper,
                     shifted(mix(wrist_upper, contact_edge[0], 0.34), across, 0.060),
                     shifted(mix(wrist_upper, contact_edge[0], 0.74), across, 0.030),
                     contact_edge[0]))

    palm_outline: list[Point] = []
    for point in list(contact_edge) + distal + ulnar + wrist_cap + thenar:
        if not palm_outline or math.hypot(point.u - palm_outline[-1].u,
                                          point.v - palm_outline[-1].v) > 1e-9:
            palm_outline.append(point)
    if math.hypot(palm_outline[0].u - palm_outline[-1].u, palm_outline[0].v - palm_outline[-1].v) <= 1e-9:
        palm_outline.pop()
    palm_geometry = PalmCup(tuple(palm_outline), contact_edge, wrist, axis,
                            math.hypot(foot_mid.u - wrist.u, foot_mid.v - wrist.v))
    palm = _shape(f"{case}-palm",
                  "palm cup: its contact rim is the dish's foot line, its wrist end meets the forearm",
                  _hand_support(case, "palm", hand_z), fill,
                  (wrist, contact_edge[0], contact_edge[-1], knuckle_bottom),
                  palm_geometry.outline, family="palm_cup",
                  attachments=((f"{case}-forearm", "wrist", "wrist"),),
                  semantic_anchors=(("wrist", wrist),
                                    ("contact-left", contact_edge[0]),
                                    ("contact-right", contact_edge[-1]),
                                    ("knuckle-low", knuckle_bottom)))

    digit_tubes: dict[str, Tube] = {}
    fingers = []
    for spec in FINGERS:
        base = shifted(mix(knuckle_top, knuckle_bottom, spec.knuckle_fraction), axis, -KNUCKLE_SETBACK)
        rim_point = rim.near_point(spec.rim_angle_degrees)
        tip = shifted(rim_point, rim.inward_normal(spec.rim_angle_degrees),
                      -(spec.tip_half + spec.reach_margin))
        direction = unit(Point(tip.u - base.u, tip.v - base.v))
        knuckle = shifted(mix(base, tip, 0.55), perp(direction),
                          spec.bow * math.hypot(tip.u - base.u, tip.v - base.v))
        tube = tapered_digit(base, knuckle, tip, base_half=spec.base_half, tip_half=spec.tip_half,
                             joint_dip=spec.joint_dip)
        digit_tubes[spec.name] = tube
        fingers.append(_shape(
            f"{case}-finger-{spec.name}", spec.intent,
            _hand_support(case, f"finger-{spec.name}", hand_z + spec.depth_offset), fill,
            (base, tip), tube.outline, family="tapered_digit_tube",
            semantic_anchors=(("base", base), ("tip", tip))))

    thumb_base = shifted(mix(wrist_upper, contact_edge[0], THUMB.knuckle_fraction), across, 0.010)
    thumb_rim = rim.near_point(THUMB.rim_angle_degrees)
    thumb_tip = shifted(thumb_rim, rim.inward_normal(THUMB.rim_angle_degrees),
                        -(THUMB.tip_half + THUMB.reach_margin))
    thumb_direction = unit(Point(thumb_tip.u - thumb_base.u, thumb_tip.v - thumb_base.v))
    thumb_knuckle = shifted(mix(thumb_base, thumb_tip, 0.52), perp(thumb_direction),
                            THUMB.bow * math.hypot(thumb_tip.u - thumb_base.u,
                                                   thumb_tip.v - thumb_base.v))
    thumb_tube = tapered_digit(thumb_base, thumb_knuckle, thumb_tip, base_half=THUMB.base_half,
                               tip_half=THUMB.tip_half, joint_dip=THUMB.joint_dip)
    digit_tubes["thumb"] = thumb_tube
    thumb = _shape(f"{case}-thumb", THUMB.intent,
                   _hand_support(case, "thumb", hand_z + THUMB.depth_offset), fill,
                   (thumb_base, thumb_tip), thumb_tube.outline, family="tapered_digit_tube",
                   semantic_anchors=(("base", thumb_base), ("tip", thumb_tip)))
    return HandAssembly(palm, tuple(fingers), thumb, palm_geometry, digit_tubes, contact_edge)


def validate_scene(shapes: tuple[ShapeSpec, ...],
                   declared_contacts: tuple[DeclaredContact, ...]) -> dict:
    """Check named joints, declared contacts, and depth separation of every other overlap."""
    components: dict[str, Component] = {}
    for spec in shapes:
        try:
            contour = sample_closed_curve(spec.controls, steps_per_segment=4)
            validate_closed_contour(contour)
        except ValueError as exc:
            raise ValueError(f"{spec.name}: invalid generated support contour: {exc}") from exc
        components[spec.name] = Component(spec.name, spec.intent, spec.support, contour, spec.fill,
                                          spec.attachments, spec.semantic_anchors)

    attachments: dict[frozenset[str], list[Point]] = {}
    for component in components.values():
        own = dict(component.anchors)
        if len(own) != len(component.anchors):
            raise ValueError(f"duplicate semantic anchors: {component.name}")
        for target, own_name, target_name in component.attachments:
            if target not in components or own_name not in own:
                raise ValueError(f"unresolved semantic attachment: {component.name}/{target}/{own_name}")
            other = components[target]
            other_anchors = dict(other.anchors)
            if target_name not in other_anchors:
                raise ValueError(f"unresolved attachment target: {target}/{target_name}")
            world_a = component.support.local_to_world(own[own_name])
            world_b = other.support.local_to_world(other_anchors[target_name])
            if max(abs(world_a[i] - world_b[i]) for i in range(3)) > 1e-8:
                raise ValueError(f"attached world anchors disagree: {component.name}/{target}/{own_name}")
            attachments.setdefault(frozenset((component.name, target)), []).append(Point(world_a[0], world_a[1]))

    contact_pairs: set[frozenset[str]] = set()
    contact_evidence = []
    for contact in declared_contacts:
        if contact.owner_a not in components or contact.owner_b not in components:
            raise ValueError(f"declared contact names an unknown component: {contact.owner_a}/{contact.owner_b}")
        owner_a, owner_b = components[contact.owner_a], components[contact.owner_b]
        gaps = []
        depths = []
        for point_a, point_b in zip(contact.points_a, contact.points_b):
            world_a = owner_a.support.local_to_world(point_a)
            world_b = owner_b.support.local_to_world(point_b)
            gaps.append(math.hypot(world_a[0] - world_b[0], world_a[1] - world_b[1]))
            depths.append(world_a[2] - world_b[2])
        if max(gaps) > contact.max_projected_gap + 1e-9:
            raise ValueError(f"contact leaves a visible gap: {contact.owner_a}/{contact.owner_b} {max(gaps):.4f}")
        if max(abs(abs(depth) - contact.depth_separation) for depth in depths) > 1e-9:
            raise ValueError(f"contact depth separation is not constant: {contact.owner_a}/{contact.owner_b}")
        contact_pairs.add(frozenset((owner_a.name, owner_b.name)))
        contact_evidence.append({
            "parts": sorted((owner_a.name, owner_b.name)),
            "claim": contact.claim,
            "max_projected_gap": max(gaps),
            "depth_separation": abs(depths[0]),
            "palm_behind_dish": depths[0] < 0,
            "stations": len(contact.points_a),
        })

    clearances = []
    joint_overlaps = []
    names = list(components)
    for index, name in enumerate(names):
        a = components[name]
        outline_a = _world_xy_outline(a)
        for other_name in names[index + 1:]:
            b = components[other_name]
            outline_b = _world_xy_outline(b)
            if not polygons_overlap(outline_a, outline_b):
                continue
            pair = frozenset((a.name, b.name))
            if pair in contact_pairs:
                continue
            samples = _overlap_samples(outline_a, outline_b)
            delta = [_world_z_at_xy(a.support, point) - _world_z_at_xy(b.support, point) for point in samples]
            if min(delta) < -1e-9 and max(delta) > 1e-9:
                witnesses = attachments.get(pair, [])
                if not witnesses or any(min(math.hypot(p.u - w.u, p.v - w.v) for w in witnesses) > 0.34
                                        for p in samples):
                    raise ValueError(f"support-depth crossing extends beyond named joint: {sorted(pair)}")
                joint_overlaps.append({"parts": sorted(pair), "bounded_support_transition_radius": 0.34})
                continue
            if all(abs(value) <= 1e-9 for value in delta):
                witnesses = attachments.get(pair, [])
                if not witnesses or any(min(math.hypot(p.u - w.u, p.v - w.v) for w in witnesses) > 0.42
                                        for p in samples):
                    raise ValueError(f"coplanar component overlap outside a named joint: {sorted(pair)}")
                joint_overlaps.append({"parts": sorted(pair), "bounded_to_attachment_radius": 0.42})
            else:
                clearances.append({"parts": sorted(pair),
                                   "minimum_depth_separation": min(abs(value) for value in delta)})
    return {"declared_contacts": contact_evidence,
            "depth-separated_overlaps": clearances,
            "bounded_coplanar_attachment_joints": joint_overlaps,
            "scope": "Actual case component footprints/supports only; not a general volume-physics claim"}


def _b_case(case: str) -> tuple[tuple[ShapeSpec, ...], tuple[LineSpec, ...], dict]:
    if case not in {"baseline", "variant", "control"}:
        raise ValueError(case)
    variant = case == "variant"
    control = case == "control"
    support_center = Point(2.55, 2.03 if variant else 1.74)
    dish_center = Point(support_center.u, support_center.v + (0.34 if control else 0.0))
    dish_rx = 0.53 * (1.12 if variant else 1.0)
    dish_ry = 0.34

    # the hand is built against the nominal dish (its own case before the control displacement),
    # so a displaced dish leaves a still hand.
    nominal_contour = sample_closed_curve(_dish_body(support_center, dish_rx, dish_ry), steps_per_segment=4)
    foot = dish_foot_contact(nominal_contour)
    foot_low = min(point.v for point in nominal_contour)
    wrist = Point(foot[0].u - 0.45, foot_low - 0.25)

    shoulder = Point(.54, 2.12)
    upper_length, fore_length = 1.28, 1.02
    limb = construct_limb(LimbParameters(
        shoulder, upper_length, fore_length, wrist, 1, .18, .12, .12, .09,
        SupportFrame(f"{case}-arm-support", f"{case}-arm-depth", origin=(0, 0, .025),
                     u_axis=(1, 0, .008), v_axis=(0, 1, 0))))
    arm_support = limb.support
    wrist_world = arm_support.local_to_world(wrist)
    hand_z = wrist_world[2] - HAND_DEPTH_SLOPE * wrist.u

    body_support = SupportFrame(f"{case}-body-support", f"{case}-body-depth",
                                origin=(0, 0, .025 + .008 * shoulder.u), u_axis=(1, 0, 0), v_axis=(0, 1, 0))
    cloth_support = SupportFrame(f"{case}-shirt-front", f"{case}-shirt-depth", origin=(0, 0, .06),
                                 u_axis=(1, 0, 0), v_axis=(0, 1, 0))
    hair_support = SupportFrame(f"{case}-hair-front", f"{case}-hair-depth", origin=(0, 0, .08),
                                u_axis=(1, 0, 0), v_axis=(0, 1, 0))

    torso_anchors = (Point(-.72, 2.12), Point(.54, 2.12), Point(.61, .52), Point(-.62, .52))
    torso_outline = _closed_spans((
        (torso_anchors[0], Point(-.26, 2.35), Point(.25, 2.34), torso_anchors[1]),
        (torso_anchors[1], Point(.77, 1.70), Point(.73, .79), torso_anchors[2]),
        (torso_anchors[2], Point(.25, .36), Point(-.28, .36), torso_anchors[3]),
        (torso_anchors[3], Point(-.78, .95), Point(-.80, 1.73), torso_anchors[0])))
    torso = _shape(f"{case}-torso", "original fitted clothed torso mass", body_support, "#31586b",
                   torso_anchors, torso_outline, family="relation_fitted_torso",
                   semantic_anchors=(("shoulder", shoulder), ("neck-base", Point(-.04, 2.12))))
    shirt_anchors = (Point(-.53, 2.08), Point(.40, 2.08), Point(.43, .66), Point(-.49, .66))
    shirt_outline = _closed_spans((
        (shirt_anchors[0], Point(-.22, 2.23), Point(.22, 2.22), shirt_anchors[1]),
        (shirt_anchors[1], Point(.51, 1.55), Point(.51, .92), shirt_anchors[2]),
        (shirt_anchors[2], Point(.2, .56), Point(-.22, .56), shirt_anchors[3]),
        (shirt_anchors[3], Point(-.58, .96), Point(-.56, 1.58), shirt_anchors[0])))
    shirt = _shape(f"{case}-shirt-panel", "tailored lighter vest panel defines the chest and carries art lines",
                   cloth_support, "#d7cba7", shirt_anchors, shirt_outline, family="tailored_vest_panel")
    neck_center = Point(-.04, 2.38)
    neck = _shape(f"{case}-neck", "neck joins the collar opening to the head", body_support, "#e7b08a",
                  (neck_center,), _ellipse_controls(neck_center, .22, .30), family="neck_oval",
                  attachments=((f"{case}-torso", "torso-join", "neck-base"),
                               (f"{case}-head", "head-join", "head-base")),
                  semantic_anchors=(("torso-join", Point(-.04, 2.12)), ("head-join", Point(-.08, 2.36))))
    head_center = Point(-.08, 2.91)
    head = _shape(f"{case}-head", "original head silhouette gives the support action human context",
                  body_support, "#e9b58f", (head_center,), _ellipse_controls(head_center, .47, .55),
                  family="head_mass", semantic_anchors=(("head-base", Point(-.08, 2.36)),))
    hair_anchors = (Point(-.56, 2.91), Point(-.42, 3.48), Point(.32, 3.49), Point(.40, 2.91))
    hair = _shape(f"{case}-hair", "swept dark hair cap frames a simple original face", hair_support, "#243b54",
                  hair_anchors,
                  _closed_spans(((hair_anchors[0], Point(-.53, 3.27), Point(-.34, 3.48), hair_anchors[1]),
                                 (hair_anchors[1], Point(-.17, 3.60), Point(.12, 3.60), hair_anchors[2]),
                                 (hair_anchors[2], Point(.50, 3.31), Point(.45, 3.06), hair_anchors[3]),
                                 (hair_anchors[3], Point(.17, 3.04), Point(-.23, 3.08), hair_anchors[0]))),
                  family="swept_hair_cap")

    arm_anchors = (shoulder, limb.elbow, limb.wrist)
    upper_arm = _shape(f"{case}-upper-arm", "bent sleeve follows two-bone shoulder-to-elbow IK",
                       arm_support, "#83a8a6", arm_anchors, _cardinal_controls(limb.upper_arm.outline),
                       family="IK_taper_upper_sleeve",
                       attachments=((f"{case}-torso", "shoulder", "shoulder"),
                                    (f"{case}-forearm", "elbow", "elbow")),
                       semantic_anchors=(("shoulder", shoulder), ("elbow", limb.elbow)))
    forearm = _shape(f"{case}-forearm", "second tapered sleeve segment turns toward the upturned hand",
                     arm_support, "#9abbb1", arm_anchors, _cardinal_controls(limb.forearm.outline),
                     family="IK_taper_forearm",
                     attachments=((f"{case}-upper-arm", "elbow", "elbow"),
                                  (f"{case}-palm", "wrist", "wrist")),
                     semantic_anchors=(("elbow", limb.elbow), ("wrist", wrist)))

    rim = RimBand(Point(support_center.u, support_center.v - 0.005), dish_rx, 0.078)
    hand = build_hand(case, foot, rim, wrist, hand_z, "#e8ad89")
    foot_mid = mix(foot[0], foot[-1], 0.5)
    dish_support = _hand_support(case, "dish-support", hand_z + DISH_DEPTH_OFFSET)
    dish = _shape(f"{case}-dish-wall", "shallow ceramic fruit dish: its foot line is the palm's contact rim",
                  dish_support, "#628c91",
                  (Point(dish_center.u - dish_rx, dish_center.v), Point(dish_center.u + dish_rx, dish_center.v),
                   Point(dish_center.u, dish_center.v - dish_ry)),
                  _dish_body(dish_center, dish_rx, dish_ry), family="shallow_dish",
                  semantic_anchors=(("foot-left", Point(dish_center.u - dish_rx * 0.48, dish_center.v - dish_ry)),
                                    ("foot-centre", Point(dish_center.u, dish_center.v - dish_ry)),
                                    ("foot-right", Point(dish_center.u + dish_rx * 0.48, dish_center.v - dish_ry))))
    rim_support = _hand_support(case, "dish-rim", hand_z + DISH_DEPTH_OFFSET + 0.060)
    rim_center = Point(dish_center.u, dish_center.v - 0.005)
    actual_rim = RimBand(rim_center, dish_rx, 0.078)
    rim_shape = _shape(f"{case}-dish-rim", "elliptical glazed rim separates fruit from the bowl wall",
                       rim_support, "#e7d4af", (rim_center,),
                       _ellipse_controls(rim_center, actual_rim.rx, actual_rim.ry), family="dish_rim")
    fruit_support = _hand_support(case, "fruit", hand_z + DISH_DEPTH_OFFSET + 0.080)
    fruit_center = Point(dish_center.u - .06, dish_center.v + .09)
    fruit = _shape(f"{case}-fruit", "single apricot-like fruit makes the carried dish a small still life",
                   fruit_support, "#e59158", (fruit_center,), _ellipse_controls(fruit_center, .17, .20),
                   family="elliptic_fruit")
    leaf_support = _hand_support(case, "leaf", hand_z + DISH_DEPTH_OFFSET + 0.100)
    leaf_center = Point(fruit_center.u + .06, fruit_center.v + .18)
    leaf = _shape(f"{case}-leaf", "small oval leaf accent echoes the carried still life", leaf_support,
                  "#56755b", (leaf_center,), _ellipse_controls(leaf_center, .13, .075), family="leaf_ovoid")

    shapes = (torso, shirt, neck, head, hair, upper_arm, forearm,
              hand.palm, *hand.fingers, hand.thumb, dish, rim_shape, fruit, leaf)

    lines = []
    face_center = head_center
    eye_l = Point(face_center.u - .16, face_center.v + .04)
    eye_r = Point(face_center.u + .12, face_center.v + .04)
    lines.extend((
        _line(f"{case}-eye-left", "small left eye", f"{case}-head", (eye_l,),
              _line_curve(eye_l, Point(eye_l.u + .045, eye_l.v), 0, 4), "#304251", 2.0),
        _line(f"{case}-eye-right", "small right eye", f"{case}-head", (eye_r,),
              _line_curve(eye_r, Point(eye_r.u + .045, eye_r.v), 0, 4), "#304251", 2.0),
    ))
    cuff_a = Point(wrist.u - .11, wrist.v + .09)
    cuff_b = Point(wrist.u + .08, wrist.v - .11)
    lines.append(_line(f"{case}-cuff-seam", "cuff turn follows wrist orientation", f"{case}-forearm",
                       (cuff_a, cuff_b), _line_curve(cuff_a, cuff_b, .01), "#45686d", 2.1))
    palm_crease_a = mix(wrist, foot_mid, 0.34)
    palm_crease_b = mix(wrist, foot_mid, 0.70)
    lines.append(_line(f"{case}-palm-cup-crease", "the palm's cup crease runs from the wrist toward the dish foot",
                       f"{case}-palm", (palm_crease_a, palm_crease_b),
                       _line_curve(palm_crease_a, palm_crease_b, 0.02), "#a86e62", 1.5))
    for spec in (*FINGERS, THUMB):
        tube = hand.digit_tubes[spec.name]
        crease = _crease(hand, spec, tube)
        lines.append(_line(f"{case}-{spec.name}-knuckle-crease",
                           f"{spec.name} knuckle crease follows the digit's own centreline",
                           f"{case}-{'thumb' if spec.name == 'thumb' else 'finger-' + spec.name}",
                           crease, _line_curve(crease[0], crease[1], 0.006), "#a4695f", 1.35))
    rim_a = Point(rim_center.u - dish_rx * .78, rim_center.v + .015)
    rim_b = Point(rim_center.u + dish_rx * .78, rim_center.v + .015)
    lines.append(_line(f"{case}-rim-light", "small bright rim arc makes the bowl opening explicit",
                       f"{case}-dish-rim", (rim_a, rim_b), _line_curve(rim_a, rim_b, .045), "#f4e6c8", 2.3))
    fruit_seam_a = Point(fruit_center.u - .04, fruit_center.v - .12)
    fruit_seam_b = Point(fruit_center.u + .02, fruit_center.v + .08)
    lines.append(_line(f"{case}-fruit-seam", "fruit highlight seam is a restrained colour-form cue",
                       f"{case}-fruit", (fruit_seam_a, fruit_seam_b),
                       _line_curve(fruit_seam_a, fruit_seam_b, .02), "#f4c07e", 1.8))

    shape_names = {shape.name for shape in shapes}
    if any(line.owner not in shape_names for line in lines):
        raise ValueError("semantic line owner is missing")
    if len({shape.name for shape in shapes}) != len(shapes):
        raise ValueError("duplicate component id in scene")

    contacts = () if control else (DeclaredContact(
        f"{case}-palm", f"{case}-dish-wall", hand.contact_edge, foot, CONTACT_INSET,
        DISH_DEPTH_OFFSET,
        "palm cup rim meets the dish's derived foot line along its whole flat run"),)
    collision = validate_scene(shapes, contacts)
    evidence = {
        "action": "a bent arm presents an open hand; the palm cup supports the dish underside "
                  "along the derived foot line and four individually posed fingers plus a thumb "
                  "close on the dish's rim band",
        "semantic_case": case,
        "dish_width_ratio": 1.12 if variant else 1.0,
        "dish_center": [dish_center.u, dish_center.v],
        "wrist_target": [wrist.u, wrist.v],
        "hand_contact_stations": [[point.u, point.v] for point in hand.contact_edge],
        "dish_foot_stations": [[point.u, point.v] for point in foot],
        "fingertip_targets": {spec.name: [hand.digit_tubes[spec.name].tip().u,
                                          hand.digit_tubes[spec.name].tip().v]
                              for spec in (*FINGERS, THUMB)},
        "fingertip_reach_margins": {spec.name: spec.reach_margin for spec in (*FINGERS, THUMB)},
        "rim_band": {"center": [rim.center.u, rim.center.v], "rx": rim.rx, "ry": rim.ry},
        "palm_contact_fraction": CONTACT_FRACTION,
        "control": ("dish alone moved away from the unchanged hand by authored 0.34 scene units; "
                    "labeled near miss") if control else "",
        "collision_check": collision,
    }
    return shapes, tuple(lines), evidence


def _crease(hand: HandAssembly, spec: DigitSpec, tube: Tube) -> tuple[Point, Point]:
    """A knuckle crease across the digit at its own joint station, from the generated tube."""
    station = tube.stations[max(1, int(0.40 * (len(tube.stations) - 1)))]
    normal = perp(station.tangent)
    return (shifted(station.center, normal, station.half_width * 0.72),
            shifted(station.center, normal, -station.half_width * 0.72))


def build_b_study(case: str) -> tuple[Study, dict]:
    shapes, lines, evidence = _b_case(case)
    title = {"baseline": "SUPPORT \u00b7 chest level", "variant": "VARIATION \u00b7 lifted + broader dish",
             "control": "CONTROL \u2014 near miss"}[case]
    caption = ("dish displaced; hand remains still" if case == "control"
               else "bent arm - open hand supports dish from below")
    study = Study(f"B {case} supported fruit dish", 450, 640, shapes, lines,
                  ((title, "panel", 225, 40), (caption, "caption", 225, 612)),
                  Camera(), "#eee8dd", 108.0, 100.0, 570.0)
    return study, evidence


def compose_b_studies(svgs: tuple[str, ...]) -> str:
    """Arrange three pipeline-rendered case vectors as a matched-camera art contact sheet."""
    if len(svgs) != 3:
        raise ValueError("B artwork sheet needs baseline, variation, and control")
    groups = []
    for index, source in enumerate(svgs):
        opening = source.find(">")
        ending = source.rfind("</svg>")
        if opening < 0 or ending < opening:
            raise ValueError("invalid rendered B panel SVG")
        groups.append(f'<g id="case-panel-{index}" transform="translate({index * 450},0)">'
                      + source[opening + 1:ending] + '</g>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1350" height="640" viewBox="0 0 1350 640">\n'
            '<!-- three matched-camera vector studies; each figure part is emitted from the guarded spatial pipeline -->\n'
            + ''.join(groups)
            + '<path id="case-divider-1" d="M 450,0 V 640" stroke="#d0c6b7" stroke-width="1.2"/>'
            + '<path id="case-divider-2" d="M 900,0 V 640" stroke="#d0c6b7" stroke-width="1.2"/>\n</svg>\n')


def _screen(study: Study, point: tuple[float, float, float]) -> tuple[float, float]:
    return study.offset_x + study.scale * point[0], study.offset_y - study.scale * point[1]


def _svg_text(text: str) -> str:
    """Emit non-ASCII glyphs as ASCII numeric references for the local SVG renderer."""
    return "".join(html.escape(char, quote=False) if ord(char) < 128 else f"&#x{ord(char):X};"
                   for char in text)


def _line_svg(study: Study, span, color: str, width: float, name: str) -> str:
    a, b = (_screen(study, point) for point in span)
    return (f'<path id="{html.escape(name)}" d="M {a[0]:.3f},{a[1]:.3f} L {b[0]:.3f},{b[1]:.3f}" '
            f'fill="none" stroke="{html.escape(color)}" stroke-width="{width:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def _assembly(study: Study) -> tuple[dict[str, ShapeSpec], dict[str, Component]]:
    """Build the guarded component for every shape: generated outline, sampled, validated."""
    specs = {spec.name: spec for spec in study.shapes}
    if len(specs) != len(study.shapes):
        raise ValueError("duplicate component ID in scene")
    components = {}
    for spec in study.shapes:
        sampled = sample_closed_curve(spec.controls, steps_per_segment=2)
        validate_closed_contour(sampled)
        components[spec.name] = Component(spec.name, spec.intent, spec.support, sampled, spec.fill,
                                          spec.attachments, spec.semantic_anchors)
    return specs, components


def visible_scene(study: Study) -> dict[str, tuple[tuple[tuple[str, str, str], ...],
                                                    tuple[tuple[tuple[float, float, float],
                                                                tuple[float, float, float]], ...]]]:
    """One depth pass over the whole scene: per-component visible fills and visible boundary spans.

    The reviewed sheet called the composition adapter once per shape, and each of those calls
    rebuilt and depth-tested the same global face set. This single pass consumes the same faces
    and the same engine (opaque-triangle depth fill + segment clipping), so which pixels survive
    is decided by geometry only -- there is no authored front/back list anywhere in this module.
    """
    from scripts.articulated_construction import component_faces
    from scripts.articulated_line_visibility import visible_segment_spans
    from scripts.vector_visibility import visible_regions
    specs, components = _assembly(study)
    faces = component_faces(tuple(components.values()), study.camera)
    regions: dict[str, list[tuple[str, str, str]]] = {}
    for path, color, owner in visible_regions(faces):
        if owner not in specs:
            raise ValueError(f"depth engine emitted an unknown component: {owner}")
        regions.setdefault(owner, []).append((path, color, owner))
    result = {}
    for spec in study.shapes:
        own = tuple(regions.get(spec.name, ()))
        if not own:
            raise ValueError(f"depth engine removed all fill for {spec.name}")
        world = tuple(study.camera.project(spec.support.local_to_world(point)) for point in components[spec.name].outline)
        spans = []
        for start_point, end_point in zip(world, world[1:] + world[:1]):
            for lo, hi in visible_segment_spans(start_point, end_point, faces, spec.name):
                spans.append((tuple(start_point[i] + (end_point[i] - start_point[i]) * lo for i in range(3)),
                              tuple(start_point[i] + (end_point[i] - start_point[i]) * hi for i in range(3))))
        result[spec.name] = (own, tuple(spans))
    return result


def build_svg(study: Study) -> str:
    """Renderer boundary accepts only the semantic scene, never target/raster/crop paths."""
    from scripts.articulated_line_visibility import transform_compound_path
    specs, components = _assembly(study)
    scene = visible_scene(study)
    prefix = re.sub(r"[^A-Za-z0-9_-]+", "-", study.name).strip("-")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{study.width}" height="{study.height}" '
             f'viewBox="0 0 {study.width} {study.height}">',
             '<!-- ground: authored neutral art paper; all semantic objects below come from guarded support/depth adapters -->',
             f'<rect id="study-ground-{prefix}" width="100%" height="100%" fill="{study.background}"/>']
    for spec in study.shapes:
        fills, spans = scene[spec.name]
        for index, (path, color, owner) in enumerate(fills):
            mapped = transform_compound_path(path, lambda x, y: _screen(study, (x, y, 0.0)))
            parts.append(f'<!-- {html.escape(spec.name)}: {html.escape(spec.intent)}; family={html.escape(spec.family)} -->')
            parts.append(f'<path id="fill-{html.escape(owner)}-{index}" d="{mapped}" fill="{color}" stroke="none"/>')
        for index, span in enumerate(spans):
            parts.append(f'<!-- {html.escape(spec.name)}: geometry-visible semantic component boundary -->')
            parts.append(_line_svg(study, span, "#293a49", 1.65, f"outline-{spec.name}-{index}"))
    for line in study.lines:
        owner = components[line.owner]
        for index, span in enumerate(project_visible_semantic_path(line.points, owner, study.camera,
                                                                  tuple(components.values()))):
            parts.append(f'<!-- {html.escape(line.name)}: {html.escape(line.intent)}; owner={html.escape(line.owner)} -->')
            parts.append(_line_svg(study, span, line.color, line.width, f"line-{line.name}-{index}"))
    for index, (text, style, x, y) in enumerate(study.labels):
        parts.append(f'<!-- label {index}: authored scope/action label -->')
        if style == "panel":
            parts.append(f'<text id="study-label-{prefix}-{index}" x="{x}" y="{y}" text-anchor="middle" '
                         f'font-family="sans-serif" font-size="15" font-weight="650" fill="#283d4a">'
                         f'{_svg_text(text)}</text>')
        else:
            parts.append(f'<text id="study-label-{prefix}-{index}" x="{x}" y="{y}" text-anchor="middle" '
                         f'font-family="sans-serif" font-size="12" fill="#5b6263">{_svg_text(text)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"
