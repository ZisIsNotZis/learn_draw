"""Construction tests for the B-hand-v2-r1 hand: digits, taper, separation, derived contact.

None of these tests judge art. Each one measures the geometry this package actually emits
against an expectation that comes from somewhere else -- the dish's own contour, the rim
ellipse's own equation, or the delivered pixel scale -- never from the same expression that
produced the value. Four of them additionally demonstrate their own failure by mutating the
emitted geometry (digit separation, width taper, palm contact, single-variable control), so a
check that cannot fail cannot pass silently.
"""
from __future__ import annotations
import hashlib
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent
REPO = next(parent for parent in ROOT.parents
            if (parent / "scripts" / "articulated_construction.py").is_file())
for entry in (str(REPO), str(ROOT), str(PACKAGE / "source")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import pytest  # noqa: E402

import hand_family  # noqa: F401  (imported for the caller search in test_hand_family_has_no_unused_public_construction)
import scene  # noqa: E402
from hand_family import perp, unit  # noqa: E402
from scripts.articulated_construction import Point  # noqa: E402
from spatial_adapter import sample_closed_curve  # noqa: E402

FINGERS = ("index", "middle", "ring", "little")
DISH_OBJECT = {"dish-wall", "dish-rim", "fruit", "leaf"}
DISH_LINES = {"rim-light", "fruit-seam"}


# --- fixtures: one build per case, shared by every test -------------------------------------

@pytest.fixture(scope="module")
def baseline():
    return scene.build_b_study("baseline")


@pytest.fixture(scope="module")
def control():
    return scene.build_b_study("control")


@pytest.fixture(scope="module")
def variant_evidence():
    return scene._b_case("variant")[2]


# --- measurement helpers, independent of the builders that produced the geometry ------------

def _segment_distance(point, start, end):
    dx, dy = end.u - start.u, end.v - start.v
    length = dx * dx + dy * dy
    t = 0.0 if length == 0 else max(0.0, min(1.0, ((point.u - start.u) * dx
                                                   + (point.v - start.v) * dy) / length))
    return math.hypot(point.u - (start.u + t * dx), point.v - (start.v + t * dy))


def _polygon_gap(first, second):
    """Minimum boundary distance between two closed polygons (0 when they cross or touch)."""
    best = float("inf")
    for points, other in ((first, second), (second, first)):
        for start, end in zip(points, points[1:] + points[:1]):
            for point in other:
                best = min(best, _segment_distance(point, start, end))
    return best


def _width_across(outline, station, chord):
    """Width of an emitted digit measured perpendicular to its chord at one station."""
    tangent = unit(chord)
    normal = perp(tangent)
    along = [p.u * tangent.u + p.v * tangent.v for p in outline]
    across = [p.u * normal.u + p.v * normal.v for p in outline]
    target = station.u * tangent.u + station.v * tangent.v
    near = [value for value, x in zip(across, along) if abs(x - target) <= 0.03]
    assert len(near) >= 2, "no emitted outline samples around the measurement station"
    return max(near) - min(near)


def _near_rim_arc(band, samples=721, low=0.0, high=180.0):
    """The rim ellipse's near arc, computed here from rx/ry rather than asked of RimBand."""
    arc = []
    for index in range(samples):
        phi = math.radians(low + (high - low) * index / (samples - 1))
        arc.append((band["center"][0] + band["rx"] * math.cos(phi),
                    band["center"][1] - band["ry"] * math.sin(phi)))
    return arc


def _arc_distance(band, point):
    return min(math.hypot(point.u - u, point.v - v) for u, v in _near_rim_arc(band))


def _arc_vertex_at(band, u):
    """Height of the near arc directly above/below the given u (clamped to the arc's span)."""
    span = sorted(_near_rim_arc(band), key=lambda pair: abs(pair[0] - u))
    return span[0][1]


def _digits(shapes, case="baseline"):
    """Every digit component with its authored semantic anchors, by digit name."""
    by_name = {shape.name: shape for shape in shapes}
    found = {}
    for name in FINGERS:
        found[name] = by_name[f"{case}-finger-{name}"]
    found["thumb"] = by_name[f"{case}-thumb"]
    return found


def _distal_half(shape, anchors):
    tip, root = anchors["tip"], anchors["root"]
    keep = 0.5 * math.hypot(tip.u - root.u, tip.v - root.v)
    return [point for point in shape.controls
            if math.hypot(point.u - tip.u, point.v - tip.v) <= keep]


def _expect_failure(check, message):
    """Prove a check can fail: run it against mutated geometry and demand an AssertionError."""
    with pytest.raises(AssertionError):
        check()
    return message


# --- inventory, families and pose ----------------------------------------------------------

def test_hand_is_one_palm_four_fingers_and_one_thumb(baseline):
    study, _evidence = baseline
    digits = _digits(study.shapes)
    assert len(digits) == 5
    palm = {shape.name: shape for shape in study.shapes}["baseline-palm"]
    assert palm.family == "palm_pad"
    assert all(shape.family == "lofted_digit" for shape in digits.values())
    assert all(shape.name and shape.intent for shape in (*digits.values(), palm))
    # every digit is posed on its own depth plane, so depth not paint order orders them
    depths = [shape.support.origin[2] for shape in digits.values()]
    assert len({round(depth, 6) for depth in depths}) == len(digits)
    assert len({shape.support.support_id for shape in digits.values()}) == len(digits)


def test_digits_are_individually_posed(baseline):
    study, _evidence = baseline
    digits = _digits(study.shapes)
    lengths = [math.hypot(shape.semantic_anchors[2][1].u - shape.semantic_anchors[0][1].u,
                          shape.semantic_anchors[2][1].v - shape.semantic_anchors[0][1].v)
               for shape in digits.values()]
    assert min(lengths) > 0.15 and max(lengths) < 0.75
    assert max(lengths) - min(lengths) > 0.02, "all digits share one length"
    roots = {shape.semantic_anchors[0][1] for shape in digits.values()}
    assert len(roots) == len(digits), "two digits start from the same point"
    assert len({tuple(shape.controls) for shape in digits.values()}) == len(digits)


# --- E9: separation at the delivered scale --------------------------------------------------

def test_digits_are_separated_by_a_fraction_of_their_width(baseline):
    """Gaps measured on emitted outlines, in pixels at the delivered scale (E9)."""
    study, _evidence = baseline
    scale = study.scale
    digits = _digits(study.shapes)
    distal, width = {}, {}
    for name, shape in digits.items():
        anchors = dict(shape.semantic_anchors)
        distal[name] = _distal_half(shape, anchors)
        width[name] = _width_across(shape.controls, anchors["tip"],
                                    Point(anchors["tip"].u - anchors["root"].u,
                                          anchors["tip"].v - anchors["root"].v))
    tightest = None
    for index, first in enumerate(sorted(digits)):
        for second in sorted(digits)[index + 1:]:
            gap = _polygon_gap(distal[first], distal[second])
            floor = 0.35 * min(width[first], width[second])
            assert gap >= floor, (f"{first} and {second} are only {gap * scale:.1f}px apart "
                                  f"({gap / min(width[first], width[second]):.2f} of a digit width)")
            if tightest is None or gap < tightest[2]:
                tightest = (first, second, gap, floor)
    # the check is capable of failing: slide the closest pair together until 10% of the floor is left
    first, second, gap, floor = tightest
    centre_first = (sum(p.u for p in distal[first]) / len(distal[first]),
                    sum(p.v for p in distal[first]) / len(distal[first]))
    centre_second = (sum(p.u for p in distal[second]) / len(distal[second]),
                     sum(p.v for p in distal[second]) / len(distal[second]))
    toward = unit(Point(centre_first[0] - centre_second[0], centre_first[1] - centre_second[1]))
    moved = [Point(p.u + toward.u * gap * 0.9, p.v + toward.v * gap * 0.9) for p in distal[second]]
    _expect_failure(lambda: assert_true(_polygon_gap(distal[first], moved) >= floor),
                    f"digit separation {first}/{second}")


# --- taper ---------------------------------------------------------------------------------

def test_digit_width_tapers_toward_the_tip(baseline):
    study, _evidence = baseline
    digits = _digits(study.shapes)
    for name, shape in digits.items():
        anchors = dict(shape.semantic_anchors)
        chord = Point(anchors["tip"].u - anchors["root"].u, anchors["tip"].v - anchors["root"].v)
        base = _width_across(shape.controls, anchors["root"], chord)
        tip = _width_across(shape.controls, anchors["tip"], chord)
        assert base > tip, f"{name}: width does not shrink toward the tip"
        assert tip <= 0.75 * base, f"{name}: taper too weak ({base:.3f}->{tip:.3f})"
        # a taper check that cannot fail is not a check: fatten the tip and re-measure
        centre = anchors["tip"]
        fattened = [Point(centre.u + (p.u - centre.u) * 2.6, centre.v + (p.v - centre.v) * 2.6)
                    if math.hypot(p.u - centre.u, p.v - centre.v) <= 0.12 else p
                    for p in shape.controls]
        def mutated():
            assert _width_across(fattened, anchors["tip"], chord) <= 0.75 * base
        _expect_failure(mutated, name)


# --- E2: derived contact -------------------------------------------------------------------

def test_palm_contact_edge_lies_on_the_dish_foot(baseline):
    """The palm's distal rim is the dish's own foot line, re-derived from the emitted dish."""
    study, evidence = baseline
    by_name = {shape.name: shape for shape in study.shapes}
    dish_contour = sample_closed_curve(by_name["baseline-dish-wall"].controls, steps_per_segment=4)
    lowest = min(point.v for point in dish_contour)
    foot = sorted((point for point in dish_contour if point.v <= lowest + 1e-9),
                  key=lambda point: point.u)
    palm = by_name["baseline-palm"]
    contact = tuple(Point(u, v) for u, v in evidence["hand_contact_stations"])
    assert len(contact) >= 3
    anchors = dict(palm.semantic_anchors)
    assert anchors["contact-left"] == contact[0]
    assert anchors["contact-right"] == contact[-1]
    on_foot = lambda stations: all(
        any(_segment_distance(Point(p.u, p.v - scene.CONTACT_INSET), a, b) <= 1e-9
            for a, b in zip(foot, foot[1:])) for p in stations)
    assert on_foot(contact), "a palm contact station is not on the dish's own foot"
    assert abs(contact[0].v - (lowest + scene.CONTACT_INSET)) <= 1e-9
    # the contact line is hidden under the dish, not drawn as a second line
    assert 0.0 < scene.CONTACT_INSET <= 0.01
    assert contact[-1].u - contact[0].u >= 0.15, "palm contact covers too little of the dish foot"
    shifted_contact = (Point(contact[0].u, contact[0].v + 0.02), *contact[1:])
    _expect_failure(lambda: assert_true(on_foot(shifted_contact)), "palm contact derivation")


def assert_true(value):
    """Assertion wrapper so a boolean result can be handed to _expect_failure."""
    assert value


def test_palm_sits_behind_the_dish_foot_at_a_constant_stand_off(baseline):
    study, evidence = baseline
    by_name = {shape.name: shape for shape in study.shapes}
    palm, dish = by_name["baseline-palm"], by_name["baseline-dish-wall"]
    gaps, depths = [], []
    for point in (Point(u, v) for u, v in evidence["hand_contact_stations"]):
        under = Point(point.u, point.v - scene.CONTACT_INSET)
        world_palm = palm.support.local_to_world(point)
        world_dish = dish.support.local_to_world(under)
        gaps.append(math.hypot(world_palm[0] - world_dish[0], world_palm[1] - world_dish[1]))
        depths.append(world_palm[2] - world_dish[2])
    assert max(gaps) <= scene.CONTACT_INSET + 1e-9
    assert max(abs(-depth - scene.DISH_DEPTH_OFFSET) for depth in depths) <= 1e-9
    assert all(depth < 0 for depth in depths), "the palm must sit behind the dish wall"
    recorded = [entry for entry in evidence["collision_check"]["declared_contacts"]
                if entry["parts"] == sorted(("baseline-palm", "baseline-dish-wall"))]
    assert len(recorded) == 1 and recorded[0]["palm_behind_dish"] is True
    # lift the palm onto the dish plane and the stand-off check must fail
    raised = scene.SupportFrame("raised", "raised-depth",
                                origin=(0, 0, palm.support.origin[2] + 0.02),
                                u_axis=palm.support.u_axis, v_axis=palm.support.v_axis)
    world_palm = raised.local_to_world(_contact_point(evidence))
    world_dish = dish.support.local_to_world(_under_point(evidence))
    _expect_failure(lambda: assert_true(world_palm[2] - world_dish[2] < -1e-6),
                    "palm depth stand-off")


def _contact_point(evidence):
    u, v = evidence["hand_contact_stations"][0]
    return Point(u, v)


def _under_point(evidence):
    u, v = evidence["hand_contact_stations"][0]
    return Point(u, v - scene.CONTACT_INSET)


# --- fingertips against the dish's own rim band / wall -------------------------------------

def test_every_fingertip_edge_stops_short_of_the_rim_band(baseline):
    study, evidence = baseline
    band = evidence["rim_band"]
    digits = _digits(study.shapes)
    for name in FINGERS:
        spec = next(spec for spec in scene.FINGERS if spec.name == name)
        tip = dict(digits[name].semantic_anchors)["tip"]
        distance = _arc_distance(band, tip)
        expected = spec.tip_half + spec.reach
        assert abs(distance - expected) <= 0.004, (
            f"{name}: tip centre is {distance:.4f} from the rim band, expected {expected:.4f}")
        # below the band along its own normal, so the fingertip stays visible on the outer wall
        assert tip.v < _arc_vertex_at(band, tip.u) - 0.02, f"{name}: tip hides behind the rim band"
        raised = Point(tip.u, tip.v + 0.12)
        _expect_failure(lambda: assert_true(raised.v < _arc_vertex_at(band, raised.u) - 0.02), name)


def test_thumb_presses_the_dish_outer_left_wall(baseline):
    study, evidence = baseline
    by_name = {shape.name: shape for shape in study.shapes}
    contour = sample_closed_curve(by_name["baseline-dish-wall"].controls, steps_per_segment=4)
    tip = dict(by_name["baseline-thumb"].semantic_anchors)["tip"]
    centre_u = evidence["dish_center"][0]
    nearest = min(math.hypot(tip.u - p.u, tip.v - p.v) for p in contour)
    expected = scene.THUMB.tip_half + scene.THUMB.reach
    assert abs(nearest - expected) <= 0.005, (
        f"thumb tip stops {nearest:.4f} from the dish contour, expected {expected:.4f}")
    assert tip.u < centre_u, "the thumb sits on the dish's far side, not the near-left wall"
    assert tip.v > evidence["dish_foot_stations"][0][1], "the thumb does not rise above the foot"


def test_variation_builds_the_hand_against_the_wider_dish(baseline, variant_evidence):
    _study, evidence = baseline
    assert evidence["dish_width_ratio"] == 1.0
    assert variant_evidence["dish_width_ratio"] == pytest.approx(1.12)
    base = evidence["hand_contact_stations"]
    variant = variant_evidence["hand_contact_stations"]
    base_span = base[-1][0] - base[0][0]
    variant_span = variant[-1][0] - variant[0][0]
    assert variant_span / base_span == pytest.approx(1.12, abs=0.02)


# --- E5: the control differs in exactly one respect ----------------------------------------

def _component_map(study, prefix):
    return {shape.name[len(prefix):]: shape for shape in study.shapes}


def _line_map(study, prefix):
    return {line.name[len(prefix):]: line for line in study.lines}


def _same_shape(original, moved_shape, delta):
    """True when the second outline is the first one translated by delta and nothing else."""
    if len(original.controls) != len(moved_shape.controls):
        return False
    return all(abs(b.u - (a.u + delta[0])) <= 1e-12 and abs(b.v - (a.v + delta[1])) <= 1e-12
               for a, b in zip(original.controls, moved_shape.controls))


def test_control_differs_only_in_the_dish_displacement(baseline, control):
    base_study, base_evidence = baseline
    control_study, control_evidence = control
    base = _component_map(base_study, "baseline-")
    moved = _component_map(control_study, "control-")
    assert set(base) == set(moved)
    differing = {name for name in base
                 if base[name].controls != moved[name].controls
                 or base[name].support.origin != moved[name].support.origin}
    assert differing == DISH_OBJECT, f"the control changed more than the dish: {sorted(differing)}"
    shift = (0.0, control_evidence["dish_center"][1] - base_evidence["dish_center"][1])
    assert shift[1] == pytest.approx(0.34)
    for name in DISH_OBJECT:
        assert base[name].support.origin == moved[name].support.origin, f"{name} plane moved"
        assert _same_shape(base[name], moved[name], shift), f"{name} was reshaped, not moved"
    base_lines = _line_map(base_study, "baseline-")
    control_lines = _line_map(control_study, "control-")
    assert set(base_lines) == set(control_lines)
    differing_lines = {name for name in base_lines
                       if base_lines[name].points != control_lines[name].points}
    assert differing_lines == DISH_LINES
    assert control_evidence["collision_check"]["declared_contacts"] == []
    # mutate one hand point by a millimetre and the single-variable claim must collapse
    nudged = {name: (shape.controls if name != "palm" else tuple(
        Point(p.u, p.v + 0.001) for p in shape.controls)) for name, shape in moved.items()}
    def differing_under(map_under_test):
        return {name for name in base
                if base[name].controls != map_under_test[name].controls
                or base[name].support.origin != map_under_test[name].support.origin}
    assert differing_under(nudged) == DISH_OBJECT | {"palm"}
    _expect_failure(lambda: assert_true(differing_under(nudged) == DISH_OBJECT),
                    "single-variable control")


# --- depth does the occlusion ---------------------------------------------------------------

def test_depth_engine_cuts_the_dish_outline_and_fills_every_digit(baseline):
    study, _evidence = baseline
    _specs, components = scene._assembly(study)
    visible = scene.visible_scene(study)
    for name in ("baseline-finger-index", "baseline-finger-middle", "baseline-finger-ring",
                 "baseline-finger-little", "baseline-thumb"):
        fills, spans = visible[name]
        assert fills, f"{name} produced no visible fill"
        assert spans, f"{name} produced no visible outline"
    dish_outline = components["baseline-dish-wall"].outline
    perimeter = sum(math.hypot(b.u - a.u, b.v - a.v) for a, b in zip(dish_outline,
                                                                    dish_outline[1:] + dish_outline[:1]))
    _fills, dish_spans = visible["baseline-dish-wall"]
    visible_length = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in dish_spans)
    assert visible_length < 0.95 * perimeter, "the digits did not interrupt the dish's outline"
    assert visible["baseline-palm"][0], "palm produced no visible fill"
    # E2: the dish object is in front of the palm and behind the fingertips, and its glazed
    # rim is in front of them again -- the hand wraps the dish rather than sitting under a decal
    by_name = {shape.name: shape for shape in study.shapes}
    wall_z = by_name["baseline-dish-wall"].support.origin[2]
    rim_z = by_name["baseline-dish-rim"].support.origin[2]
    palm_z = by_name["baseline-palm"].support.origin[2]
    digits = _digits(study.shapes)
    assert palm_z < wall_z, "the palm is not behind the dish"
    for name, shape in digits.items():
        assert shape.support.origin[2] > wall_z, f"{name} is not in front of the dish's wall"
        assert shape.support.origin[2] < rim_z, f"{name} is not behind the dish's glazed rim"


# --- captions and construction hygiene ------------------------------------------------------

def test_captions_claim_only_what_the_panels_show():
    for case in ("baseline", "variant", "control"):
        study, _evidence = scene.build_b_study(case)
        texts = [text for text, _style, _x, _y in study.labels]
        joined = " ".join(texts)
        assert "braces" not in joined
        if case == "control":
            assert any("CONTROL" in text and "near miss" in text for text in texts)
            assert any("dish displaced" in text and "hand remains still" in text for text in texts)
        else:
            assert any(text == "bent arm - open hand holds the dish from below" for text in texts)


def test_no_manual_visibility_ranges_in_the_scene_source():
    source = (PACKAGE / "source" / "scene.py").read_text(encoding="utf-8")
    for forbidden in ("visible_range", "painter_order", "paint_order", "z_order",
                      "front_copy", "behind_copy", "draw_order"):
        assert forbidden not in source, f"manual visibility control appeared in the scene: {forbidden}"


def test_hand_family_has_no_unused_public_construction():
    """E8: every public name in the family module is reached from the scene or these tests."""
    family_source = (PACKAGE / "source" / "hand_family.py").read_text(encoding="utf-8")
    scene_source = (PACKAGE / "source" / "scene.py").read_text(encoding="utf-8")
    test_source = Path(__file__).read_text(encoding="utf-8")
    public = []
    for line in family_source.splitlines():
        for keyword in ("def ", "class "):
            if line.startswith(keyword):
                name = line[len(keyword):].split("(")[0].split(":")[0].strip()
                if not name.startswith("_"):
                    public.append(name)
    assert len(public) >= 8, f"caller search found too few public constructions: {public}"
    corpus = family_source + scene_source + test_source
    unused = [name for name in public if corpus.count(name) < 2]
    assert unused == [], f"dead public construction in hand_family: {unused}"


# --- E10: the emitted package is consistent and reproducible --------------------------------

def test_check_bundle_lists_the_one_to_one_image_first():
    report = (PACKAGE / "check" / "report.txt").read_text(encoding="utf-8")
    images = [line.strip() for line in report.splitlines() if line.strip().startswith(".scratch")]
    assert images, "the check bundle lists no image"
    assert "check/draft-fullres.png" in images[0], f"first image is not the 1:1 draft: {images[0]}"
    from PIL import Image
    with Image.open(PACKAGE / "check" / "draft-fullres.png") as draft:
        with Image.open(PACKAGE / "rendered" / "B-original-support.png") as sheet:
            assert draft.size == sheet.size, "the bundle's 1:1 image is not the delivered size"


def test_manifest_verifies_and_covers_every_file():
    lines = [line for line in (PACKAGE / "manifest.sha256").read_text(encoding="utf-8").splitlines()
             if line.strip()]
    recorded = {}
    for line in lines:
        digest, path = line.split("  ", 1)
        recorded[path] = digest
    for path, digest in recorded.items():
        assert hashlib.sha256((PACKAGE / path).read_bytes()).hexdigest() == digest, f"hash mismatch: {path}"
    actually_present = {str(path.relative_to(PACKAGE)) for path in PACKAGE.rglob("*")
                        if path.is_file()
                        and "__pycache__" not in path.parts
                        and path.suffix != ".pyc"
                        and path.name not in {"manifest.json", "manifest.sha256"}}
    assert actually_present - set(recorded) == set(), "manifest misses real files"
    assert set(recorded) - actually_present - {"manifest.json"} == set(), "manifest lists missing files"
