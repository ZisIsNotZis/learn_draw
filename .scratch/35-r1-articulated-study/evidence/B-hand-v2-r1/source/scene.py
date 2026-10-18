"""B-hand-v2-r1: a constructed hand holding a dish, with one continuous arm.

Concept, variation and control are unchanged from the reviewed sheet: a bent arm
carries a small fruit dish at chest level (baseline), lifted with a broader dish
(variation), and the dish displaced away from a still hand (control).

What this revision changes is the construction of the figure, not the concept.
The hand is a palm pad whose distal rim is the dish's own foot line, four digits
that grow from that rim and climb the dish's near wall to its rim band, and a
thumb that presses the dish's near-left wall. The arm is one continuous limb from
a shoulder cap on the torso, through a bend at the elbow, tapering into the wrist.
The head is a skull-and-jaw mass under a hair mass with an ear and a jaw line; it
makes no face claim.

Geometry is derived wherever the drawing states a physical relation: the palm's
contact rim is the dish's foot line, each fingertip is placed against the dish's
rim band, the thumb against the dish's own side wall, the elbow from the arm's
two-bone reach, and the dish's width and depth drive all of it. Only proportions,
pose angles and stand-off margins are authored.
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
from hand_family import (
    Loft, PalmPad, arm_tube, digit_tube, mix, palm_pad, perp, profile_tube, shifted, unit,
)


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

    def outward_normal(self, degrees: float) -> Point:
        """Unit normal pointing from the rim band outward (away from the bowl's mouth)."""
        phi = math.radians(degrees)
        return unit(Point(-math.cos(phi) / self.rx, math.sin(phi) / self.ry))

    def near_arc(self, samples: int = 360, low: float = 0.0, high: float = 180.0) -> tuple[Point, ...]:
        """Sampled near-rim arc, the independent measurement used to check grip contact."""
        return tuple(self.near_point(low + (high - low) * index / (samples - 1))
                     for index in range(samples))

    def boundary_distance(self, point: Point, samples: int = 720) -> float:
        """Nearest distance from a point to the near rim arc, independent of the generator."""
        return min(math.hypot(point.u - candidate.u, point.v - candidate.v)
                   for candidate in self.near_arc(samples))

    def signed_depth_into_band(self, point: Point) -> float:
        """How far inside the rim band a point sits (positive inside, negative outside)."""
        du = (point.u - self.center.u) / self.rx
        dv = (point.v - self.center.v) / self.ry
        return 1.0 - math.hypot(du, dv)


@dataclass(frozen=True)
class DigitSpec:
    """Authored proportion and pose values for one digit; its positions are derived elsewhere."""
    name: str
    intent: str
    foot_fraction: float         # where along the dish's derived foot line the digit grows
    rim_angle_degrees: float     # which station of the dish's near rim band it reaches
    reach: float                 # signed stand-off: positive stops outside the arc, negative hooks over
    base_half: float
    joint_half: float
    tip_half: float
    bend: float                  # authored bow at the digit's own joint
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
PALM_WRIST_HALF = 0.150        # the palm narrows to this at the wrist
PALM_KNUCKLE_DROP = 0.170      # the palm's knuckle pad continues this far past the rim's far end
PALM_THENAR_BULGE = 0.070      # the thumb-side flank swells out by this much
KNUCKLE_SETBACK = 0.014        # digit roots sit this far inside the palm's contact rim
DISH_FOOT_FRACTION = 0.48      # the dish's flat foot spans this fraction of its radius each way

FINGERS = (
    DigitSpec("index", "index digit climbs the dish's near wall to its rim band",
              0.10, 122.0, 0.012, 0.058, 0.049, 0.032, -0.055, 0.0200),
    DigitSpec("middle", "middle digit is the longest and hooks over the rim band",
              0.37, 100.0, -0.010, 0.060, 0.051, 0.033, -0.020, 0.0215),
    DigitSpec("ring", "ring digit stands beside the middle digit and stops at the rim",
              0.64, 80.0, 0.010, 0.057, 0.048, 0.031, 0.020, 0.0230),
    DigitSpec("little", "little digit hooks the rim band on the far side of the hand",
              0.91, 60.0, -0.008, 0.050, 0.042, 0.028, 0.055, 0.0245),
)
THUMB = DigitSpec("thumb", "thumb presses the dish's near-left wall from outside",
                  0.90, 168.0, 0.006, 0.078, 0.066, 0.050, -0.030, 0.0260)

ARM_DEPTH = 0.048              # the sleeve sits in front of the torso plane and the vest
ARM_SHOULDER_HALF = 0.215      # sleeve width at the shoulder cap
ARM_ELBOW_HALF = 0.118         # sleeve narrows through the bend
ARM_WRIST_HALF = 0.078         # and tapers into the wrist

# --- palette: the held fruit is separated from skin by both value and hue -------
PAPER = "#efe9de"
INK = "#27394a"
SKIN = "#eec2a1"
SKIN_LINE = "#b9806c"
SLEEVE = "#9dbcb1"
SLEEVE_LINE = "#5d8179"
CLOTH = "#31586b"
VEST = "#dbd0ae"
VEST_LINE = "#8d8a6c"
DISH_WALL = "#5f8a8c"
DISH_RIM = "#f1e3c5"
FRUIT = "#b8452c"
LEAF = "#4f6b4f"
HAIR = "#243b54"


def _ellipse_outline(center: Point, rx: float, ry: float, samples: int = 40) -> tuple[Point, ...]:
    """A sampled ellipse: the rim, the fruit and the leaf are worth more than four controls."""
    return tuple(Point(center.u + rx * math.cos(2 * math.pi * index / samples),
                       center.v + ry * math.sin(2 * math.pi * index / samples))
                 for index in range(samples))


def _bezier(a: Point, b: Point, c: Point, d: Point, steps: int = 5) -> tuple[Point, ...]:
    return tuple(Point((1 - t) ** 3 * a.u + 3 * (1 - t) ** 2 * t * b.u + 3 * (1 - t) * t * t * c.u + t ** 3 * d.u,
                       (1 - t) ** 3 * a.v + 3 * (1 - t) ** 2 * t * b.v + 3 * (1 - t) * t * t * c.v + t ** 3 * d.v)
                 for index in range(steps) for t in (index / steps,))


def _closed_spans(spans: Iterable[tuple[Point, Point, Point, Point]], steps: int = 5) -> tuple[Point, ...]:
    result = []
    for span in spans:
        result.extend(_bezier(*span, steps=steps))
    return tuple(result)


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
          generated: Iterable[Point], color: str = INK, width: float = 2.0) -> LineSpec:
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


def _dish_body(center: Point, radius: float, depth: float) -> tuple[Point, ...]:
    """Shallow bowl with a short flat foot edge; the hand's contact derives from that foot."""
    left = Point(center.u - radius, center.v)
    right = Point(center.u + radius, center.v)
    foot_r = Point(center.u + radius * DISH_FOOT_FRACTION, center.v - depth)
    foot_l = Point(center.u - radius * DISH_FOOT_FRACTION, center.v - depth)
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


def dish_wall(contour: tuple[Point, ...], dish_center: Point, side: str) -> tuple[tuple[Point, Point], ...]:
    """Read one side wall out of the dish's own contour as (silhouette point, outward normal) pairs.

    "Left" and "right" are the two silhouette runs between the foot and the dish's mid
    height; the outward normal is radial from the dish centre, so the stations are the
    dish's own shape and nothing here is authored.
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
        raise ValueError("wall fraction must lie in [0, 1]")
    span = (len(wall) - 1) * fraction
    index = min(len(wall) - 2, int(span))
    t = span - index
    return (mix(wall[index][0], wall[index + 1][0], t),
            unit(mix(wall[index][1], wall[index + 1][1], t)))


def _hand_support(case: str, label: str, z_origin: float) -> SupportFrame:
    return SupportFrame(f"{case}-{label}", f"{case}-{label}-depth",
                        origin=(0.0, 0.0, z_origin), u_axis=(1.0, 0.0, HAND_DEPTH_SLOPE),
                        v_axis=(0.0, 1.0, 0.0))


@dataclass(frozen=True)
class Digit:
    """One emitted digit: the loft it was built from and the authored spec that posed it."""
    spec: DigitSpec
    loft: Loft


@dataclass(frozen=True)
class HandAssembly:
    palm: ShapeSpec
    fingers: tuple[ShapeSpec, ...]
    thumb: ShapeSpec
    palm_geometry: PalmPad
    digits: tuple[Digit, ...]
    contact_edge: tuple[Point, ...]


def build_hand(case: str, foot: tuple[Point, ...], rim: RimBand, wall: tuple[tuple[Point, Point], ...],
               wrist: Point, hand_z: float, fill: str) -> HandAssembly:
    """Palm pad, four digits and a thumb, all derived from the dish geometry and the wrist.

    Derived (geometric consequence): the palm's distal rim is the dish's own foot line;
    every digit's root is a station on that foot line; every fingertip is placed against
    a station of the dish's own near rim band; the thumb's tip is placed against a
    station of the dish's own left wall. Authored (hypothesis): the stand-off margins,
    the digit widths, and how much each digit bends.
    """
    contact_edge = tuple(Point(point.u, point.v + CONTACT_INSET) for point in foot)
    pad = palm_pad(contact_edge, wrist, wrist_half=PALM_WRIST_HALF,
                   pad_half=0.0, knuckle_drop=PALM_KNUCKLE_DROP,
                   thenar_bulge=PALM_THENAR_BULGE)
    palm = _shape(f"{case}-palm",
                  "palm pad: its distal rim is the dish's foot line, its wrist end meets the forearm",
                  _hand_support(case, "palm", hand_z), fill,
                  (wrist, contact_edge[0], contact_edge[-1]), pad.outline, family="palm_pad",
                  attachments=((f"{case}-arm", "wrist", "wrist"),),
                  semantic_anchors=(("wrist", wrist),
                                    ("contact-left", contact_edge[0]),
                                    ("contact-right", contact_edge[-1]),
                                    ("knuckle-far", pad.knuckle_edge[1])))

    digits: list[Digit] = []
    finger_shapes = []
    for spec in FINGERS:
        root = shifted(mix(contact_edge[0], contact_edge[-1], spec.foot_fraction),
                       pad.axis, -KNUCKLE_SETBACK)
        rim_point = rim.near_point(spec.rim_angle_degrees)
        # the tip centre sits `reach` off the rim arc along the arc's outward normal
        tip = shifted(rim_point, rim.outward_normal(spec.rim_angle_degrees), spec.reach)
        toward = unit(Point(tip.u - root.u, tip.v - root.v))
        joint = shifted(mix(root, tip, 0.52), perp(toward), spec.bend)
        loft = digit_tube(root, joint, tip, base_half=spec.base_half, joint_half=spec.joint_half,
                          tip_half=spec.tip_half)
        digits.append(Digit(spec, loft))
        finger_shapes.append(_shape(
            f"{case}-finger-{spec.name}", spec.intent,
            _hand_support(case, f"finger-{spec.name}", hand_z + spec.depth_offset), fill,
            (root, tip), loft.outline, family="lofted_digit",
            semantic_anchors=(("root", root), ("joint", joint), ("tip", tip))))

    thumb_root = shifted(mix(pad.wrist_edge[0], contact_edge[0], THUMB.foot_fraction),
                         perp(pad.axis), 0.012)
    wall_point, wall_normal = _wall_station(wall, THUMB.rim_angle_degrees / 180.0)
    thumb_tip = shifted(wall_point, wall_normal, THUMB.tip_half + THUMB.reach)
    thumb_toward = unit(Point(thumb_tip.u - thumb_root.u, thumb_tip.v - thumb_root.v))
    thumb_joint = shifted(mix(thumb_root, thumb_tip, 0.55), perp(thumb_toward), THUMB.bend)
    thumb_loft = digit_tube(thumb_root, thumb_joint, thumb_tip, base_half=THUMB.base_half,
                            joint_half=THUMB.joint_half, tip_half=THUMB.tip_half)
    digits.append(Digit(THUMB, thumb_loft))
    thumb = _shape(f"{case}-thumb", THUMB.intent,
                   _hand_support(case, "thumb", hand_z + THUMB.depth_offset), fill,
                   (thumb_root, thumb_tip), thumb_loft.outline, family="lofted_digit",
                   semantic_anchors=(("root", thumb_root), ("joint", thumb_joint),
                                     ("tip", thumb_tip)))
    return HandAssembly(palm, tuple(finger_shapes), thumb, pad, tuple(digits), contact_edge)


def validate_scene(shapes: tuple[ShapeSpec, ...],
                   declared_contacts: tuple[DeclaredContact, ...]) -> dict:
    """Check named joints, declared contacts, and depth separation of every other overlap."""
    components: dict[str, Component] = {}
    for spec in shapes:
        try:
            contour = sample_closed_curve(spec.controls, steps_per_segment=3)
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
        gaps, depths = [], []
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
    support_center = Point(2.50, 2.10 if variant else 1.92)
    dish_center = Point(support_center.u, support_center.v + (0.34 if control else 0.0))
    dish_rx = 0.60 * (1.12 if variant else 1.0)
    dish_depth = 0.62

    # The hand is built against the nominal (own-case) dish, so in the control the dish
    # alone is displaced and the hand is unchanged geometry.
    nominal_contour = sample_closed_curve(_dish_body(support_center, dish_rx, dish_depth),
                                          steps_per_segment=4)
    foot = dish_foot_contact(nominal_contour)
    rim = RimBand(Point(support_center.u, support_center.v - 0.005), dish_rx, 0.115)
    left_wall = dish_wall(nominal_contour, support_center, "left")
    wrist = Point(2.05, 0.80)

    shoulder = Point(0.60, 2.00)
    limb = construct_limb(LimbParameters(
        shoulder, 1.30, 0.95, wrist, -1, ARM_SHOULDER_HALF, ARM_ELBOW_HALF/2, ARM_ELBOW_HALF/2,
        ARM_WRIST_HALF,
        SupportFrame(f"{case}-arm-support", f"{case}-arm-depth",
                     origin=(0, 0, ARM_DEPTH), u_axis=(1, 0, 0), v_axis=(0, 1, 0))))
    arm_support = limb.support
    wrist_world = arm_support.local_to_world(wrist)
    hand_z = wrist_world[2] - HAND_DEPTH_SLOPE * wrist.u

    # --- arm: one continuous limb, shoulder cap, bend at the elbow, taper to the wrist
    arm_loft = arm_tube(shoulder, limb.elbow, wrist, shoulder_half=ARM_SHOULDER_HALF,
                        elbow_half=ARM_ELBOW_HALF, wrist_half=ARM_WRIST_HALF)
    upper_arm = _shape(f"{case}-arm",
                       "one continuous sleeve: shoulder cap, bend at the elbow, taper into the wrist",
                       arm_support, SLEEVE, (shoulder, limb.elbow, wrist), arm_loft.outline,
                       family="lofted_limb",
                       attachments=((f"{case}-palm", "wrist", "wrist"),),
                       semantic_anchors=(("shoulder", shoulder), ("elbow", limb.elbow),
                                         ("wrist", wrist)))

    # --- body: torso mass, vest panel, neck, skull-and-jaw head, hair mass
    body_support = SupportFrame(f"{case}-body-support", f"{case}-body-depth",
                                origin=(0, 0, .025 + .008 * shoulder.u), u_axis=(1, 0, 0), v_axis=(0, 1, 0))
    cloth_support = SupportFrame(f"{case}-shirt-front", f"{case}-shirt-depth", origin=(0, 0, .042),
                                 u_axis=(1, 0, 0), v_axis=(0, 1, 0))
    hair_support = SupportFrame(f"{case}-hair-front", f"{case}-hair-depth", origin=(0, 0, .065),
                               u_axis=(1, 0, 0), v_axis=(0, 1, 0))
    cap_support = SupportFrame(f"{case}-shoulder-cap", f"{case}-shoulder-cap-depth",
                              origin=(0, 0, .060), u_axis=(1, 0, 0), v_axis=(0, 1, 0))

    neck_base = Point(-.06, 2.12)
    head_base = Point(-.10, 2.44)
    torso_anchors = (Point(-.74, 2.10), Point(.56, 2.06), Point(.62, .50), Point(-.64, .50))
    torso_outline = _closed_spans((
        (torso_anchors[0], Point(-.30, 2.36), Point(.30, 2.30), torso_anchors[1]),
        (torso_anchors[1], Point(.80, 1.62), Point(.72, .76), torso_anchors[2]),
        (torso_anchors[2], Point(.26, .34), Point(-.30, .34), torso_anchors[3]),
        (torso_anchors[3], Point(-.82, .92), Point(-.84, 1.66), torso_anchors[0])))
    torso = _shape(f"{case}-torso", "original clothed torso mass: sloped shoulders, waist taper",
                   body_support, CLOTH, torso_anchors, torso_outline, family="fitted_torso",
                   semantic_anchors=(("shoulder", shoulder), ("neck-base", neck_base)))

    vest_anchors = (Point(-.56, 2.02), Point(.44, 1.98), Point(.44, .62), Point(-.50, .62))
    vest_outline = _closed_spans((
        (vest_anchors[0], Point(-.24, 2.22), Point(.20, 2.18), vest_anchors[1]),
        (vest_anchors[1], Point(.54, 1.48), Point(.52, .90), vest_anchors[2]),
        (vest_anchors[2], Point(.22, .52), Point(-.24, .52), vest_anchors[3]),
        (vest_anchors[3], Point(-.60, .92), Point(-.60, 1.52), vest_anchors[0])))
    vest = _shape(f"{case}-vest-panel",
                  "lighter vest panel: a garment edge runs along its neckline and armhole",
                  cloth_support, VEST, vest_anchors, vest_outline, family="tailored_vest_panel")

    neck = profile_tube(neck_base, head_base, knots=((0.0, .165), (0.5, .150), (1.0, .140)), samples=15)
    neck_shape = _shape(f"{case}-neck", "neck joins the collar opening to the jaw", body_support, SKIN,
                        (neck_base, head_base), neck.outline, family="lofted_profile",
                        attachments=((f"{case}-torso", "torso-join", "neck-base"),
                                     (f"{case}-head", "head-join", "head-base")),
                        semantic_anchors=(("torso-join", neck_base), ("head-join", head_base)))

    chin = Point(-.14, 2.46)
    crown = Point(-.06, 3.52)
    skull = profile_tube(chin, crown,
                         knots=((0.0, .13), (0.16, .27), (0.44, .40), (0.70, .37), (1.0, .11)),
                         samples=25, start_flat=True)
    head = _shape(f"{case}-head", "skull and jaw mass turned toward the dish; the head makes no face claim",
                  body_support, SKIN, (chin, crown), skull.outline, family="lofted_profile",
                  semantic_anchors=(("head-base", head_base), ("chin", chin)))
    hair_centers = (Point(-.52, 2.62), Point(-.40, 3.30), Point(-.02, 3.52), Point(.34, 3.06))
    hair = _shape(f"{case}-hair", "hair mass over the back and crown, ending at the fringe",
                  hair_support, HAIR, (hair_centers[0], hair_centers[1], hair_centers[3]),
                  profile_tube(Point(-.52, 2.62), Point(.34, 3.06),
                               knots=((0.0, .11), (0.30, .26), (0.62, .27), (1.0, .10)),
                               samples=25).outline,
                  family="lofted_hair_mass")

    # --- shoulder cap: joins the sleeve to the torso over the joint
    shoulder_cap = _shape(f"{case}-shoulder-cap",
                          "shoulder cap joins the sleeve to the torso over the shoulder joint",
                          cap_support, SLEEVE, (shoulder,),
                          _ellipse_outline(Point(shoulder.u - 0.02, shoulder.v - 0.02), 0.235, 0.215),
                          family="shoulder_cap",
                          semantic_anchors=(("joint", shoulder),))

    # --- hand: palm pad, four digits, thumb
    hand = build_hand(case, foot, rim, left_wall, wrist, hand_z, SKIN)

    # --- dish: wall, glazed rim, fruit, leaf
    dish_support = _hand_support(case, "dish-support", hand_z + DISH_DEPTH_OFFSET)
    dish = _shape(f"{case}-dish-wall", "shallow ceramic fruit dish: its foot line is the palm's contact rim",
                  dish_support, DISH_WALL,
                  (Point(dish_center.u - dish_rx, dish_center.v), Point(dish_center.u + dish_rx, dish_center.v),
                   Point(dish_center.u, dish_center.v - dish_depth)),
                  _dish_body(dish_center, dish_rx, dish_depth), family="shallow_dish",
                  semantic_anchors=(("foot-left", Point(dish_center.u - dish_rx * DISH_FOOT_FRACTION,
                                                        dish_center.v - dish_depth)),
                                    ("foot-centre", Point(dish_center.u, dish_center.v - dish_depth)),
                                    ("foot-right", Point(dish_center.u + dish_rx * DISH_FOOT_FRACTION,
                                                         dish_center.v - dish_depth))))
    rim_support = _hand_support(case, "dish-rim", hand_z + DISH_DEPTH_OFFSET + 0.060)
    rim_center = Point(dish_center.u, dish_center.v - 0.005)
    actual_rim = RimBand(rim_center, dish_rx, 0.115)
    rim_shape = _shape(f"{case}-dish-rim", "glazed rim and mouth of the bowl: an open ellipse above the wall",
                       rim_support, DISH_RIM, (rim_center,),
                       _ellipse_outline(rim_center, actual_rim.rx - 0.012, actual_rim.ry - 0.010),
                       family="dish_rim")
    fruit_support = _hand_support(case, "fruit", hand_z + DISH_DEPTH_OFFSET + 0.080)
    fruit_center = Point(dish_center.u - .10, dish_center.v + .06)
    fruit = _shape(f"{case}-fruit", "single apricot-like fruit makes the carried dish a small still life",
                   fruit_support, FRUIT, (fruit_center,), _ellipse_outline(fruit_center, .165, .195),
                   family="elliptic_fruit")
    leaf_support = _hand_support(case, "leaf", hand_z + DISH_DEPTH_OFFSET + 0.100)
    leaf_center = Point(fruit_center.u + .06, fruit_center.v + .20)
    leaf = _shape(f"{case}-leaf", "small oval leaf accent echoes the carried still life", leaf_support,
                  LEAF, (leaf_center,), _ellipse_outline(leaf_center, .125, .070), family="leaf_ovoid")

    shapes = (torso, vest, neck_shape, head, hair, shoulder_cap, upper_arm,
              hand.palm, *hand.fingers, hand.thumb, dish, rim_shape, fruit, leaf)

    # --- semantic lines: construction cues, each owned by the surface it sits on
    lines: list[LineSpec] = []
    jaw_a = Point(-.34, 2.58)
    jaw_b = Point(-.14, 2.31)
    lines.append(_line(f"{case}-jaw-line", "jaw and cheek boundary where the face turns away",
                       f"{case}-head", (jaw_a, jaw_b), _line_curve(jaw_a, jaw_b, -0.02),
                       SKIN_LINE, 1.7))
    ear_center = Point(-.40, 2.72)
    ear_a = Point(ear_center.u, ear_center.v - .10)
    ear_b = Point(ear_center.u, ear_center.v + .10)
    lines.append(_line(f"{case}-ear-line", "ear outline gives the head a far side",
                       f"{case}-head", (ear_a, ear_b), _line_curve(ear_a, ear_b, 0.05),
                       SKIN_LINE, 1.6))
    fringe_a = Point(-.30, 3.16)
    fringe_b = Point(.30, 3.02)
    lines.append(_line(f"{case}-fringe-edge", "fringe edge separates the hair mass from the brow",
                       f"{case}-hair", (fringe_a, fringe_b), _line_curve(fringe_a, fringe_b, -0.06),
                       INK, 1.5))
    neck_a = Point(-.06, 2.44)
    neck_b = Point(-.17, 2.44)
    lines.append(_line(f"{case}-collar-line", "collar edge where the vest meets the neck",
                       f"{case}-vest-panel", (neck_a, neck_b), _line_curve(neck_a, neck_b, -0.03),
                       VEST_LINE, 1.7))
    armhole_a = Point(.30, 2.22)
    armhole_b = Point(.06, 1.22)
    lines.append(_line(f"{case}-armhole-seam", "vest armhole edge: the garment boundary the sleeve passes",
                       f"{case}-vest-panel", (armhole_a, armhole_b),
                       _line_curve(armhole_a, armhole_b, 0.10), VEST_LINE, 1.8))
    elbow_a = shifted(limb.elbow, perp(unit(Point(limb.elbow.u - shoulder.u, limb.elbow.v - shoulder.v))),
                      -0.11)
    elbow_b = shifted(limb.elbow, perp(unit(Point(limb.elbow.u - shoulder.u, limb.elbow.v - shoulder.v))),
                      0.11)
    lines.append(_line(f"{case}-elbow-crease", "elbow crease marks the bend the two-bone reach produced",
                       f"{case}-arm", (elbow_a, elbow_b), _line_curve(elbow_a, elbow_b, 0.02),
                       SLEEVE_LINE, 1.8))
    cuff_a = shifted(wrist, perp(unit(Point(wrist.u - limb.elbow.u, wrist.v - limb.elbow.v))), -0.085)
    cuff_b = shifted(wrist, perp(unit(Point(wrist.u - limb.elbow.u, wrist.v - limb.elbow.v))), 0.085)
    lines.append(_line(f"{case}-cuff-seam", "cuff edge where the sleeve meets the wrist",
                       f"{case}-arm", (cuff_a, cuff_b), _line_curve(cuff_a, cuff_b, 0.01),
                       SLEEVE_LINE, 1.9))
    palm_crease_a = mix(wrist, mix(hand.contact_edge[0], hand.contact_edge[-1], 0.5), 0.30)
    palm_crease_b = mix(wrist, mix(hand.contact_edge[0], hand.contact_edge[-1], 0.5), 0.78)
    lines.append(_line(f"{case}-palm-crease", "palm crease runs from the wrist toward the knuckles",
                       f"{case}-palm", (palm_crease_a, palm_crease_b),
                       _line_curve(palm_crease_a, palm_crease_b, 0.03), SKIN_LINE, 1.4))
    for digit in hand.digits:
        station = digit.loft.station_at(0.46)
        normal = perp(station.tangent)
        crease_a = shifted(station.center, normal, station.half_left * 0.70)
        crease_b = shifted(station.center, normal, -station.half_right * 0.70)
        lines.append(_line(f"{case}-{digit.spec.name}-joint-crease",
                           f"{digit.spec.name} joint crease follows its own centreline",
                           f"{case}-{'thumb' if digit.spec.name == 'thumb' else 'finger-' + digit.spec.name}",
                           (crease_a, crease_b), _line_curve(crease_a, crease_b, 0.004),
                           SKIN_LINE, 1.3))
    rim_a = Point(rim_center.u - dish_rx * .80, rim_center.v + .030)
    rim_b = Point(rim_center.u + dish_rx * .80, rim_center.v + .030)
    lines.append(_line(f"{case}-rim-light", "bright rim arc makes the bowl's mouth explicit",
                       f"{case}-dish-rim", (rim_a, rim_b), _line_curve(rim_a, rim_b, .030),
                       "#fbf3dd", 2.2))
    fruit_seam_a = Point(fruit_center.u - .05, fruit_center.v - .13)
    fruit_seam_b = Point(fruit_center.u + .02, fruit_center.v + .09)
    lines.append(_line(f"{case}-fruit-seam", "fruit highlight seam is a restrained colour-form cue",
                       f"{case}-fruit", (fruit_seam_a, fruit_seam_b),
                       _line_curve(fruit_seam_a, fruit_seam_b, .02), "#e08a63", 1.7))

    shape_names = {shape.name for shape in shapes}
    if any(line.owner not in shape_names for line in lines):
        raise ValueError("semantic line owner is missing")
    if len({shape.name for shape in shapes}) != len(shapes):
        raise ValueError("duplicate component id in scene")

    contacts = () if control else (DeclaredContact(
        f"{case}-palm", f"{case}-dish-wall", hand.contact_edge,
        tuple(Point(p.u, p.v - CONTACT_INSET) for p in hand.contact_edge), CONTACT_INSET,
        DISH_DEPTH_OFFSET,
        "palm pad rim meets the dish's derived foot line along its whole flat run"),)
    collision = validate_scene(shapes, contacts)
    evidence = {
        "action": "a bent arm presents a dish on an open hand; the palm's distal rim is the "
                  "dish's foot line, four digits grow from that rim and climb the dish's near "
                  "wall to its rim band, and the thumb presses the dish's near-left wall",
        "semantic_case": case,
        "dish_width_ratio": 1.12 if variant else 1.0,
        "dish_depth": dish_depth,
        "dish_center": [dish_center.u, dish_center.v],
        "wrist_target": [wrist.u, wrist.v],
        "elbow": [limb.elbow.u, limb.elbow.v],
        "hand_contact_stations": [[point.u, point.v] for point in hand.contact_edge],
        "dish_foot_stations": [[point.u, point.v] for point in foot],
        "digit_targets": {digit.spec.name: {"root": [digit.spec.foot_fraction],
                                            "tip": [digit.loft.end().u, digit.loft.end().v]}
                          for digit in hand.digits},
        "digit_reach_margins": {spec.name: spec.reach for spec in (*FINGERS, THUMB)},
        "rim_band": {"center": [rim.center.u, rim.center.v], "rx": rim.rx, "ry": rim.ry},
        "thumb_wall_fraction": THUMB.rim_angle_degrees / 180.0,
        "control": ("dish alone moved away from the unchanged hand by authored 0.34 scene units; "
                    "labeled near miss") if control else "",
        "collision_check": collision,
    }
    return shapes, tuple(lines), evidence


def build_b_study(case: str) -> tuple[Study, dict]:
    shapes, lines, evidence = _b_case(case)
    title = {"baseline": "SUPPORT \u00b7 chest level", "variant": "VARIATION \u00b7 lifted + broader dish",
             "control": "CONTROL \u2014 near miss"}[case]
    caption = ("dish displaced; hand remains still" if case == "control"
               else "bent arm - open hand holds the dish from below")
    study = Study(f"B {case} supported fruit dish", 450, 640, shapes, lines,
                  ((title, "panel", 225, 40), (caption, "caption", 225, 612)),
                  Camera(), PAPER, 102.0, 78.0, 578.0)
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

    Every shape is triangulated onto its own support plane and the project's opaque-triangle
    engine returns the fragments that survive depth testing, so which pixels survive is decided
    by geometry only -- there is no authored front/back list anywhere in this module.
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
            parts.append(_line_svg(study, span, INK, 1.65, f"outline-{spec.name}-{index}"))
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
                         f'font-family="sans-serif" font-size="12" fill="#5b6263">'
                         f'{_svg_text(text)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"
