from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve()
ROOT = HERE.parents[6]
SMOOTH = ROOT / ".scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial"
sys.path[:0] = [str(ROOT), str(SMOOTH)]

SPEC = importlib.util.spec_from_file_location(
    "a_corrected_garment_fit", HERE.parents[1] / "source" / "build_a.py")
FIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = FIT
SPEC.loader.exec_module(FIT)

from scripts.articulated_construction import component_faces, triangulate_polygon
from scripts.articulated_line_visibility import visible_segment_spans
from smooth_spatial import validate_closed_contour


class ACorrectedGarmentFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built, cls.marks, cls.params = FIT.build_scene()
        cls.by_name = {entry.component.name: entry.component for entry in cls.built}
        cls.faces = component_faces(tuple(cls.by_name.values()), FIT.CAMERA)
        cls.svg, cls.metadata = FIT.render_svg()

    def test_part_inventory_covers_observed_clothing_without_full_portrait(self):
        required = {
            "A-visible-neck-skin", "A-bodice", "A-collar-left", "A-collar-right",
            "A-continuous-puff-sleeve", "A-dark-cuff-band", "A-bow-gather",
            "A-bow-left-loop", "A-bow-right-loop", "A-down-tail-visible-fragment",
            "A-leftward-tail-local-band", "A-identity-unknown-blue-neighbor",
        }
        self.assertEqual(set(self.by_name), required)
        self.assertFalse(any(token in name.lower() for name in self.by_name
                             for token in ("hand", "full-head", "portrait")))
        self.assertNotEqual(self.by_name["A-collar-left"].fill,
                            self.by_name["A-collar-right"].fill)
        left = self.params["parts"]["left_bow_loop"]["artist_parameterization"]
        right = self.params["parts"]["right_bow_loop"]["artist_parameterization"]
        self.assertGreater(right["width_px"], left["width_px"])

    def test_each_generated_closed_family_is_guarded_and_bounded_by_compact_inputs(self):
        for entry in self.built:
            with self.subTest(part=entry.component.name):
                self.assertLessEqual(entry.authored_anchor_count, 4)
                self.assertGreater(len(entry.component.outline), entry.authored_anchor_count)
                validate_closed_contour(entry.component.outline)
                self.assertGreater(len(triangulate_polygon(entry.component.outline)), 0)
        self.assertTrue(all(mark.authored_anchor_count <= 4 for mark in self.marks))
        self.assertGreater(sum(len(entry.component.outline) for entry in self.built), 300)
        self.assertGreater(sum(entry.authored_anchor_count for entry in self.built), 0)

    def test_support_camera_mapping_and_declared_local_contacts_are_real(self):
        contact_count = 0
        for child in self.by_name.values():
            child_anchors = dict(child.anchors)
            for target_name, own_name, target_anchor_name in child.attachments:
                target = self.by_name[target_name]
                target_anchors = dict(target.anchors)
                a = child.support.local_to_world(child_anchors[own_name])
                b = target.support.local_to_world(target_anchors[target_anchor_name])
                self.assertLess(max(abs(a[i] - b[i]) for i in range(3)), 1e-8)
                q = FIT.CAMERA.project(a)
                x, y_down = FIT._local_to_screen(child_anchors[own_name])
                self.assertAlmostEqual(q[0], x, places=8)
                self.assertAlmostEqual(q[1], FIT.HEIGHT - y_down, places=8)
                contact_count += 1
        self.assertGreaterEqual(contact_count, 3)
        body = self.by_name["A-bodice"].support
        skin = self.by_name["A-visible-neck-skin"].support
        ns2 = FIT._screen_to_local(218, 82)
        self.assertGreater(FIT._depth_at(skin, ns2), FIT._depth_at(body, ns2))
        self.assertGreater(FIT._depth_at(self.by_name["A-bow-gather"].support,
                                         FIT._screen_to_local(179, 179)),
                           FIT._depth_at(body, FIT._screen_to_local(179, 179)))

    def test_fills_and_lines_use_shared_depth_derived_scene(self):
        self.assertGreater(self.metadata["projected_faces"], len(self.built))
        self.assertEqual(self.metadata["visible_fill_regions"], len(self.built))
        self.assertIn("fill-A-bodice", self.svg)
        self.assertIn("A-neckline-dark-trim", self.svg)
        self.assertIn("A-sleeve-tube-fold", self.svg)
        self.assertIn("A-left-loop-crease", self.svg)
        owner = self.by_name["A-bodice"]
        trim = next(mark for mark in self.marks if mark.name == "A-neckline-dark-trim")
        start = FIT.CAMERA.project(owner.support.local_to_world(trim.points[0]))
        end = FIT.CAMERA.project(owner.support.local_to_world(trim.points[-1]))
        self.assertTrue(visible_segment_spans(start, end, self.faces, owner.name))
        # A point on the lower generated down-tail fragment is behind the bodice surface;
        # its path is cut by computed world depth, not a hand-authored visibility interval.
        tail = self.by_name["A-down-tail-visible-fragment"]
        down = self.params["parts"]["down_tail_fragment"]["artist_parameterization"]
        knot = self.params["parts"]["bow_gather"]["artist_parameterization"]["center_xy_crop_down"]
        import math
        angle = math.radians(down["orientation_degrees_screen"])
        end = (knot[0] + math.cos(angle) * down["hypothesis_route_length_px"],
               knot[1] + math.sin(angle) * down["hypothesis_route_length_px"])
        hidden_start = FIT._screen_to_local(end[0] - 2, end[1] - 2)
        hidden_end = FIT._screen_to_local(end[0] + 2, end[1] + 2)
        q0 = FIT.CAMERA.project(tail.support.local_to_world(hidden_start))
        q1 = FIT.CAMERA.project(tail.support.local_to_world(hidden_end))
        self.assertEqual(visible_segment_spans(q0, q1, self.faces, tail.name), ())

    def test_reference_and_teacher_are_not_runtime_open_inputs(self):
        source = (HERE.parents[1] / "source" / "build_a.py").read_text()
        for forbidden in ("image.jpg", "teacher-only-corrected-v2", "manual-traces.json",
                          "raw-patches", "pristine-fullcrop.png", "--ref", "--target"):
            self.assertNotIn(forbidden, source)
        original = Path.read_text
        allowed = FIT.PARAMS_PATH.resolve()
        opened = []

        def guarded(path, *args, **kwargs):
            resolved = path.resolve()
            opened.append(resolved)
            if resolved != allowed:
                raise AssertionError(f"runtime tried to read non-parameter file: {resolved}")
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", guarded):
            FIT.build_scene()
        self.assertEqual(opened, [allowed])
        first = FIT.build_scene()[0]
        second = FIT.build_scene()[0]
        self.assertEqual([[p for p in entry.component.outline] for entry in first],
                         [[p for p in entry.component.outline] for entry in second])

    def test_projected_bounds_stay_in_crop_and_quality_is_not_metric_tuned(self):
        for entry in self.built:
            projected = [FIT.CAMERA.project(entry.component.support.local_to_world(p))
                         for p in entry.component.outline]
            screen = [(x, FIT.HEIGHT - y) for x, y, _z in projected]
            self.assertGreaterEqual(min(x for x, _y in screen), 0)
            self.assertLessEqual(max(x for x, _y in screen), FIT.WIDTH)
            self.assertGreaterEqual(min(y for _x, y in screen), 0)
            self.assertLessEqual(max(y for _x, y in screen), FIT.HEIGHT)


if __name__ == "__main__":
    unittest.main()
