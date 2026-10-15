from __future__ import annotations

import builtins
import hashlib
import inspect
from pathlib import Path
import sys
import tempfile

import pytest

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import spatial_adapter as adapter
import smooth_spatial
import r1_scene
from r1_scene import build_a_study, build_b_study, build_svg, emit_study_svg
from scripts.articulated_construction import Camera, Point, SupportFrame, build_study_case, validate_study_case
from run_r1 import write_svgs


def _rectangle(support, name, fill, x0, y0, x1, y1):
    controls = (Point(x0, y0), Point(x1, y0), Point(x1, y1), Point(x0, y1))
    return adapter.build_visible_smooth_component(controls, name, support, Camera(), (), fill=fill)


def test_guard_fill_and_line_outputs_share_exact_sampled_contour(monkeypatch):
    guarded = []
    original_guard = smooth_spatial.validate_closed_contour

    def record_guard(points):
        guarded.append(points)
        return original_guard(points)

    monkeypatch.setattr(smooth_spatial, "validate_closed_contour", record_guard)
    monkeypatch.setattr(adapter, "validate_closed_contour", record_guard)
    face_inputs, fill_outputs, line_outputs = [], [], []
    original_faces = adapter.component_faces
    original_regions = adapter.visible_regions
    original_spans = adapter.visible_segment_spans

    def record_faces(components, camera):
        result = original_faces(components, camera)
        face_inputs.append((components, result))
        return result

    def record_regions(faces):
        result = tuple(original_regions(faces))
        fill_outputs.append((faces, result))
        return result

    def record_spans(start, end, faces, owner):
        result = original_spans(start, end, faces, owner)
        line_outputs.append((faces, owner, result))
        return result

    monkeypatch.setattr(adapter, "component_faces", record_faces)
    monkeypatch.setattr(adapter, "visible_regions", record_regions)
    monkeypatch.setattr(adapter, "visible_segment_spans", record_spans)
    support = SupportFrame("guard-fixture", "guard-depth")
    result = adapter.build_visible_smooth_component(
        (Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)),
        "guarded-owner", support, Camera(), (), fill="#789abc")

    assert result.component.outline is result.validated_sampled_contour
    assert sum(points is result.validated_sampled_contour for points in guarded) == 2
    assert face_inputs[-1][0][0] is result.component
    assert face_inputs[-1][0][0].outline is result.validated_sampled_contour
    assert result.projected_faces == face_inputs[-1][1]
    assert fill_outputs[-1][0] == result.projected_faces
    assert result.visible_fill_regions == tuple(
        region for region in fill_outputs[-1][1] if region[2] == result.component.name)
    assert line_outputs and all(owner == "guarded-owner" for _faces, owner, _spans in line_outputs)
    assert all(faces == result.projected_faces for faces, _owner, _spans in line_outputs)
    assert sum(len(spans) for _faces, _owner, spans in line_outputs) == len(result.authored_boundary_spans)


def test_invalid_contours_are_rejected_before_component_faces():
    support = SupportFrame("invalid", "invalid-depth")
    with pytest.raises(ValueError):
        adapter.build_visible_smooth_component(
            (Point(-1, -1), Point(1, 1), Point(-1, 1), Point(1, -1)),
            "bow-tie", support, Camera(), ())
    with pytest.raises(ValueError):
        smooth_spatial.validate_closed_contour((Point(0, 0), Point(1, 1), Point(0, 1), Point(1, 0)))


def test_occluder_changes_consumed_fill_and_boundary_line_visibility():
    owner_support = SupportFrame("subject", "subject-depth")
    front_support = SupportFrame("front-sheet", "front-depth", origin=(0, 0, 1.0))
    owner_controls = (Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1))
    front = _rectangle(front_support, "occluder", "#bb8060", -1.4, -.42, -.45, .42)
    clear = adapter.build_visible_smooth_component(owner_controls, "subject", owner_support, Camera(), ())
    covered = adapter.build_visible_smooth_component(
        owner_controls, "subject", owner_support, Camera(), (front.component,))
    assert clear.visible_fill_regions != covered.visible_fill_regions
    assert clear.authored_boundary_spans != covered.authored_boundary_spans
    clear_length = sum(((b[0]-a[0])**2 + (b[1]-a[1])**2)**.5 for a, b in clear.authored_boundary_spans)
    covered_length = sum(((b[0]-a[0])**2 + (b[1]-a[1])**2)**.5 for a, b in covered.authored_boundary_spans)
    assert covered_length < clear_length


def test_emitter_rejects_direct_svg_or_unvalidated_geometry_bypass():
    study = build_a_study()
    with pytest.raises(TypeError, match="guarded adapter"):
        emit_study_svg(study, {spec.name: '<path d="M 0,0 L 1,1"/>' for spec in study.shapes})
    svg = build_svg(study)
    assert '<path id="fill-' in svg and 'id="outline-' in svg and 'id="line-' in svg
    assert "<!-- bodice: broad pale upper-body garment field anchors the crop -->" in svg
    assert "<!-- collar-fold: visible inner collar fold -->" in svg


def test_every_a_and_b_shape_is_integrated_and_within_four_control_budget(monkeypatch):
    original = r1_scene.build_visible_smooth_component
    for build in (build_a_study, build_b_study):
        study = build()
        assert study.shapes and all(3 <= len(shape.controls) <= 4 for shape in study.shapes)
        observed = []

        def capture(controls, name, support, camera, occluders, **kwargs):
            observed.append((name, tuple(controls)))
            return original(controls, name, support, camera, occluders, **kwargs)

        monkeypatch.setattr(r1_scene, "build_visible_smooth_component", capture)
        svg = build_svg(study)
        monkeypatch.setattr(r1_scene, "build_visible_smooth_component", original)
        expected = {shape.name: shape.controls for shape in study.shapes}
        assert set(name for name, _controls in observed) == set(expected)
        assert all(controls == expected[name] for name, controls in observed)
        assert svg.count('id="fill-') >= len(study.shapes)
        assert svg.count('id="outline-') >= len(study.shapes)


def test_frozen_b_contact_gap_and_collision_ranges():
    for name in ("baseline", "variant", "control"):
        case = build_study_case(name)
        assert validate_study_case(case)
        hand = next(c for c in case.components if c.name == "hand")
        right = max(p.u for p in hand.outline)
        if name == "control":
            assert case.contact.u - right > .1
        else:
            assert abs(case.contact.u - right) < 1e-8
    baseline, variant = build_study_case("baseline"), build_study_case("variant")
    assert baseline.hand_target != variant.hand_target
    assert max(p.u for p in next(c for c in variant.components if c.name == "torso").outline) > max(
        p.u for p in next(c for c in baseline.components if c.name == "torso").outline)


def test_head_and_complete_art_bounds_fit_matching_viewports():
    a, b = build_a_study(), build_b_study()
    for study, panel_width in ((a, 400), (b, 420)):
        for shape in study.shapes:
            contour = adapter.sample_closed_curve(shape.controls, steps_per_segment=6)
            projected = [study.camera.project(shape.support.local_to_world(p)) for p in contour]
            screen = [(study.offset_x + study.scale*p[0], study.offset_y - study.scale*p[1]) for p in projected]
            if study is a:
                assert min(x for x, _ in screen) >= 0 and max(x for x, _ in screen) <= study.width
            else:
                col = (int(shape.name.startswith("variant-")) + 2*int(shape.name.startswith("control-"))) * panel_width
                assert min(x for x, _ in screen) >= col and max(x for x, _ in screen) <= col + panel_width
            assert min(y for _, y in screen) >= 0 and max(y for _, y in screen) <= study.height
        for line in study.lines:
            for point in (line.start, line.end):
                projected = study.camera.project(line.support.local_to_world(point))
                x = study.offset_x + study.scale * projected[0]
                y = study.offset_y - study.scale * projected[1]
                if study is a:
                    assert 0 <= x <= study.width
                else:
                    col = (int(line.name.startswith("variant-")) + 2*int(line.name.startswith("control-"))) * panel_width
                    assert col <= x <= col + panel_width
                assert 0 <= y <= study.height
        for _text, _style, x, y in study.labels:
            assert 0 <= x <= study.width and 0 <= y <= study.height


def test_reference_isolation_and_deterministic_reproduction(monkeypatch):
    import run_r1

    signature = inspect.signature(run_r1.write_svgs)
    assert list(signature.parameters) == ["output_directory"]
    original_open = builtins.open
    original_path_open = Path.open

    def reject_target(path):
        if Path(path).name == "image.jpg":
            raise AssertionError("runtime renderer attempted to read the target")

    def guarded_open(file, *args, **kwargs):
        reject_target(file)
        return original_open(file, *args, **kwargs)

    def guarded_path_open(path, *args, **kwargs):
        reject_target(path)
        return original_path_open(path, *args, **kwargs)

    renderer_source = "\n".join(path.read_text() for path in (ROOT / "run_r1.py", ROOT / "r1_scene.py", ROOT / "spatial_adapter.py"))
    assert "image.jpg" not in renderer_source
    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(Path, "open", guarded_path_open)
    with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
        temporary = Path(temporary)
        first = temporary / "one"
        second = temporary / "two"
        write_svgs(first)
        write_svgs(second)
        hashes = lambda directory: {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(directory.glob("*.svg"))
        }
        assert hashes(first) == hashes(second)
        assert set(hashes(first)) == {"A-observed-garment.svg", "B-original-action.svg"}
