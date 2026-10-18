"""Construction tests for the B-hand-v2 hand: digits, taper, separation, derived contact.

None of these tests judge art. They check that the thing built is the thing claimed:
separate constructed digits with a measured width taper, a palm contact read out of the
dish's own foot, fingertips placed against the dish's own rim band, depth doing the
occlusion, and a control that displaces only the dish.
"""
from __future__ import annotations
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[5]
for entry in (str(REPO), str(ROOT), str(ROOT.parent / "source")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import pytest  # noqa: E402

import scene  # noqa: E402
from hand_family import perp, unit  # noqa: E402
from scripts.articulated_construction import Point  # noqa: E402
from spatial_adapter import sample_closed_curve  # noqa: E402

CASES = ("baseline", "variant", "control")
DIGITS = ("index", "middle", "ring", "little")


@pytest.fixture(scope="module")
def cases():
    return {case: scene._b_case(case) for case in CASES}


def _hand(shapes, case="baseline"):
    by_name = {shape.name: shape for shape in shapes}
    return (by_name[f"{case}-palm"],
            [by_name[f"{case}-finger-{name}"] for name in DIGITS],
            by_name[f"{case}-thumb"])


def _anchors(digit):
    return dict(digit.semantic_anchors)


def _segment_distance(point, start, end):
    dx, dy = end.u - start.u, end.v - start.v
    length = dx * dx + dy * dy
    t = 0.0 if length == 0 else max(0.0, min(1.0, ((point.u - start.u) * dx + (point.v - start.v) * dy) / length))
    return math.hypot(point.u - (start.u + t * dx), point.v - (start.v + t * dy))


def _polygon_gap(a, b):
    """Minimum boundary distance between two closed polygons (0 when they cross or touch)."""
    edges_a = list(zip(a, a[1:] + a[:1]))
    edges_b = list(zip(b, b[1:] + b[:1]))
    best = float("inf")
    for start, end in edges_a:
        for point in b:
            best = min(best, _segment_distance(point, start, end))
    for start, end in edges_b:
        for point in a:
            best = min(best, _segment_distance(point, start, end))
    return best


def _measure_width(outline, center, chord):
    """Width across a digit measured only from its emitted outline, perpendicular to its chord."""
    tangent = unit(chord)
    normal = perp(tangent)
    along = [p.u * tangent.u + p.v * tangent.v for p in outline]
    across = [p.u * normal.u + p.v * normal.v for p in outline]
    target = center.u * tangent.u + center.v * tangent.v
    near = [value for value, x in zip(across, along) if abs(x - target) <= 0.03]
    assert len(near) >= 2, "no outline samples around the measurement station"
    return max(near) - min(near)


# --- digit count, separation and individual posing ------------------------------------------

def test_hand_is_one_palm_four_fingers_and_one_thumb(cases):
    shapes, _lines, _evidence = cases["baseline"]
    palm, fingers, thumb = _hand(shapes)
    assert len(fingers) == 4
    assert palm.family == "palm_cup"
    assert all(digit.family == "tapered_digit_tube" for digit in (*fingers, thumb))
    assert all(digit.name and digit.intent for digit in (*fingers, thumb))
    assert len({shape.name for shape in shapes}) == len(shapes)


def test_digits_are_separate_shapes_on_their_own_supports(cases):
    shapes, _lines, _evidence = cases["baseline"]
    _palm, fingers, thumb = _hand(shapes)
    digits = [*fingers, thumb]
    # the webbing between neighbouring digits may touch near the knuckles; what must stay
    # separate is the exposed part of each digit, so the gap is measured on the distal halves.
    distal = {}
    for digit in digits:
        anchors = _anchors(digit)
        keep = 0.45 * math.hypot(anchors["tip"].u - anchors["base"].u, anchors["tip"].v - anchors["base"].v)
        distal[digit.name] = tuple(point for point in digit.controls
                                   if math.hypot(point.u - anchors["tip"].u,
                                                 point.v - anchors["tip"].v) <= keep)
    for index, first in enumerate(digits):
        for second in digits[index + 1:]:
            gap = _polygon_gap(distal[first.name], distal[second.name])
            assert gap >= 0.010, f"{first.name} and {second.name} are only {gap:.4f} apart near the tips"
    # every digit carries its own support surface, so depth (not paint order) orders them
    assert len({digit.support.support_id for digit in digits}) == len(digits)
    assert len({digit.support.origin[2] for digit in digits}) == len(digits)


def test_digits_are_individually_posed(cases):
    shapes, _lines, _evidence = cases["baseline"]
    _palm, fingers, thumb = _hand(shapes)
    digits = [*fingers, thumb]
    bases = [_anchors(digit)["base"] for digit in digits]
    tips = [_anchors(digit)["tip"] for digit in digits]
    lengths = [math.hypot(t.u - b.u, t.v - b.v) for b, t in zip(bases, tips)]
    directions = [math.degrees(math.atan2(t.v - b.v, t.u - b.u)) for b, t in zip(bases, tips)]
    assert min(lengths) > 0.15 and max(lengths) < 0.75
    assert max(lengths) - min(lengths) > 0.02, "all digits share one length"
    assert max(directions) - min(directions) > 12.0, "all digits share one direction"
    assert len({b for b in bases}) == len(bases), "two digits start from the same point"
    assert len({tuple((round(p.u, 4), round(p.v, 4)) for p in digit.controls) for digit in digits}) == len(digits)


def test_digit_width_tapers_towards_the_tip(cases):
    shapes, _lines, _evidence = cases["baseline"]
    _palm, fingers, thumb = _hand(shapes)
    for digit in [*fingers, thumb]:
        anchors = _anchors(digit)
        chord = Point(anchors["tip"].u - anchors["base"].u, anchors["tip"].v - anchors["base"].v)
        proximal = _measure_width(digit.controls, anchors["base"], chord)
        distal = _measure_width(digit.controls, anchors["tip"], chord)
        assert proximal > distal, f"{digit.name}: width does not shrink toward the tip"
        assert distal <= 0.80 * proximal, f"{digit.name}: taper too weak ({proximal:.3f}->{distal:.3f})"


# --- derived contact: palm against the dish foot, fingertips against the rim band -----------

def test_palm_contact_edge_is_the_dish_foot_line(cases):
    shapes, _lines, evidence = cases["baseline"]
    palm, _fingers, _thumb = _hand(shapes)
    by_name = {shape.name: shape for shape in shapes}
    dish = by_name["baseline-dish-wall"]
    dish_contour = sample_closed_curve(dish.controls, steps_per_segment=4)
    lowest = min(point.v for point in dish_contour)
    foot = [point for point in dish_contour if point.v <= lowest + 1e-9]
    foot.sort(key=lambda point: point.u)
    contact = tuple(Point(u, v) for u, v in evidence["hand_contact_stations"])
    assert contact, "no contact stations recorded"
    anchored = dict(palm.semantic_anchors)
    assert anchored["contact-left"] == contact[0]
    assert anchored["contact-right"] == contact[-1]
    for point in contact:
        probe = Point(point.u, point.v - scene.CONTACT_INSET)
        on_foot = any(_segment_distance(probe, a, b) <= 1e-9 for a, b in zip(foot, foot[1:]))
        assert on_foot, f"palm contact station {point} is not on the dish's own foot"
        # the palm edge sits CONTACT_INSET under the dish so the contact line is hidden, not drawn
        assert abs(point.v - (lowest + scene.CONTACT_INSET)) <= 1e-9
        assert 0.0 < scene.CONTACT_INSET <= 0.01
    assert any(abs(point.u - point.u) <= 0 for point in contact)  # contact spans a real run
    assert contact[-1].u - contact[0].u >= 0.15, "palm contact covers too little of the dish foot"


def test_palm_supports_the_dish_underside_in_depth(cases):
    shapes, _lines, evidence = cases["baseline"]
    by_name = {shape.name: shape for shape in shapes}
    recorded = [entry for entry in evidence["collision_check"]["declared_contacts"]
                if sorted(("baseline-palm", "baseline-dish-wall")) == entry["parts"]]
    assert len(recorded) == 1
    entry = recorded[0]
    assert entry["max_projected_gap"] <= 0.01
    assert entry["depth_separation"] == pytest.approx(scene.DISH_DEPTH_OFFSET, abs=1e-12)
    assert entry["palm_behind_dish"] is True, "the palm must sit behind the dish wall, not in front"


def test_each_fingertip_is_placed_against_the_dish_rim_band(cases):
    shapes, _lines, evidence = cases["baseline"]
    _palm, fingers, thumb = _hand(shapes)
    band = evidence["rim_band"]
    rim = scene.RimBand(Point(*band["center"]), band["rx"], band["ry"])
    for digit in [*fingers, thumb]:
        tip = _anchors(digit)["tip"]
        margin = evidence["fingertip_reach_margins"][digit.name.split("-")[-1]]
        tip_half = next(spec.tip_half for spec in (*scene.FINGERS, scene.THUMB)
                        if spec.name == digit.name.split("-")[-1])
        distance = rim.boundary_distance(tip)
        assert distance <= tip_half + margin + 0.002, f"{digit.name}: tip is {distance:.3f} from the rim band"
        assert distance >= tip_half + margin - 0.002, f"{digit.name}: tip overlaps the rim band"
        near = rim.near_point(math.degrees(math.acos(max(-1.0, min(1.0, (tip.u - rim.center.u) / rim.rx)))))
        assert near.v - tip.v >= margin - 1e-6, f"{digit.name}: fingertip would hide under the rim"


def test_control_moves_only_the_dish(cases):
    baseline_shapes, _l, baseline_evidence = cases["baseline"]
    control_shapes, _l2, control_evidence = cases["control"]
    base = {shape.name.replace("baseline-", ""): shape for shape in baseline_shapes}
    control = {shape.name.replace("control-", ""): shape for shape in control_shapes}
    assert set(base) == set(control)
    for name, shape in base.items():
        other = control[name]
        same = (shape.controls == other.controls and shape.support.origin == other.support.origin
                and shape.support.u_axis == other.support.u_axis)
        if name.startswith(("palm", "finger", "thumb")):
            assert same, f"control changed the hand: {name}"
        else:
            assert not same or name in {"torso", "shirt-panel", "neck", "head", "hair",
                                        "upper-arm", "forearm"}, f"control changed {name}"
    for name in ("palm", "finger-index", "finger-middle", "finger-ring", "finger-little", "thumb"):
        assert base[name].controls == control[name].controls
    assert control_evidence["collision_check"]["declared_contacts"] == []
    moved = Point(*control_evidence["dish_center"])
    nominal = Point(*baseline_evidence["dish_center"])
    assert moved.u == pytest.approx(nominal.u) and moved.v - nominal.v == pytest.approx(0.34)


def test_variation_builds_the_hand_against_a_broader_lifted_dish(cases):
    baseline_shapes, _l, baseline_evidence = cases["baseline"]
    variant_shapes, _lv, variant_evidence = cases["variant"]
    assert baseline_evidence["dish_width_ratio"] == 1.0
    assert variant_evidence["dish_width_ratio"] == pytest.approx(1.12)
    base = {shape.name.replace("baseline-", ""): shape for shape in baseline_shapes}
    variant = {shape.name.replace("variant-", ""): shape for shape in variant_shapes}
    assert base["palm"].controls != variant["palm"].controls
    variant_contact = variant_evidence["hand_contact_stations"]
    assert max(abs(a[0] - b[0]) for a, b in zip(variant_contact, baseline_evidence["hand_contact_stations"])) > 0.02


def test_depth_engine_actually_cuts_the_dish_outline(cases):
    """The fingers sit in front of the dish, so the dish's own outline must be interrupted."""
    study, _evidence = scene.build_b_study("baseline")
    _specs, components = scene._assembly(study)
    visible = scene.visible_scene(study)
    for name in ("baseline-finger-index", "baseline-finger-middle", "baseline-finger-ring",
                 "baseline-finger-little", "baseline-thumb"):
        fills, spans = visible[name]
        assert fills, f"{name} produced no visible fill"
        assert spans, f"{name} produced no visible outline"
    dish_fills, dish_spans = visible["baseline-dish-wall"]
    dish_outline = components["baseline-dish-wall"].outline
    assert 0 < len(dish_spans) < len(dish_outline), "the dish outline was not cut by the fingers"
    palm_fills, _palm_spans = visible["baseline-palm"]
    assert palm_fills, "palm produced no visible fill"


def test_captions_claim_only_what_the_panels_show():
    for case in CASES:
        study, _evidence = scene.build_b_study(case)
        texts = [text for text, _style, _x, _y in study.labels]
        joined = " ".join(texts)
        assert "thumb braces rim" not in joined
        assert "braces" not in joined
        if case == "control":
            assert any("CONTROL" in text and "near miss" in text for text in texts)
            assert any("dish displaced" in text and "hand remains still" in text for text in texts)
        else:
            assert any(text == "bent arm - open hand supports dish from below" for text in texts)


def test_no_manual_visibility_ranges_in_the_scene_source():
    source = (ROOT.parent / "source" / "scene.py").read_text(encoding="utf-8")
    for forbidden in ("visible_range", "painter_order", "paint_order", "z_order",
                      "front_copy", "behind_copy", "draw_order"):
        assert forbidden not in source, f"manual visibility control appeared in the scene: {forbidden}"
