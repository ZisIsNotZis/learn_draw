from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

FIT = Path(__file__).resolve().parents[1]
SOURCE = FIT / "source"
sys.path.insert(0, str(Path(__file__).resolve().parents[6]))
spec = importlib.util.spec_from_file_location("fitted_a_build", SOURCE / "build_a.py")
build_a = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(build_a)


class GarmentFamilyTests(unittest.TestCase):
    def setUp(self):
        self.params = build_a.read_params(SOURCE / "semantic-parameters.json")

    def test_semantic_anchor_budget_and_observation_provenance(self):
        relations = self.params["relations"]
        for name, shape in relations.items():
            anchor_groups = []
            if "anchors" in shape:
                anchors = shape["anchors"]
                if isinstance(anchors, dict):
                    anchor_groups.extend(v for v in anchors.values() if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v))
                elif anchors and isinstance(anchors[0], list):
                    anchor_groups = anchors
            self.assertLessEqual(len(anchor_groups), 4, name)
            self.assertTrue(shape.get("teacher_ids"), name)
        self.assertEqual(self.params["teacher"]["crop_source_xyxy"], [500, 320, 900, 800])
        self.assertIn("unknown", " ".join(self.params["teacher"]["uncertainty"]))

    def test_family_outlines_are_generated_simple_and_named(self):
        parts, shapes, camera = build_a.make_components(self.params)
        self.assertEqual(len(parts), 13)
        self.assertEqual(set(shapes), {part.name for part in parts})
        for part in parts:
            self.assertGreaterEqual(len(part.outline), 4)
            self.assertLess(len(part.outline), 100)
            build_a.triangulate_polygon(part.outline)
            self.assertTrue(part.name)
            self.assertTrue(part.intent)
            for point in part.outline:
                # The unknown blue neighbor is deliberately cropped at the frame edge.
                if part.name != "unclassified-blue-neighbor-fragment":
                    self.assertGreaterEqual(point.u, -1e-8, part.name)
                    self.assertLessEqual(point.u, 400+1e-8, part.name)
                    self.assertGreaterEqual(point.v, -1e-8, part.name)
                    self.assertLessEqual(point.v, 480+1e-8, part.name)
                else:
                    self.assertGreaterEqual(point.u, -6, part.name)
                    self.assertLessEqual(point.u, 56, part.name)
                    self.assertGreaterEqual(point.v, 190, part.name)
                    self.assertLessEqual(point.v, 235, part.name)
            projected = camera.project(part.support.local_to_world(part.outline[0]))
            self.assertAlmostEqual(projected[0], part.outline[0].u, places=6)
            self.assertAlmostEqual(projected[1], part.outline[0].v, places=6)
        self.assertEqual(camera, build_a.camera_from_params(self.params))

    def test_bodice_cap_tube_and_cuff_share_generated_contact_seams(self):
        parts, shapes, camera = build_a.make_components(self.params)
        bodice = shapes["bodice"]
        cap = shapes["puff-sleeve-cap"]
        tube = shapes["right-sleeve-tube"]
        top = build_a.point_pair(self.params["relations"]["bodice"]["anchors"]["sleeve_seam_top"])
        bottom = build_a.point_pair(self.params["relations"]["bodice"]["anchors"]["sleeve_seam_bottom"])
        body_seam = tuple(build_a.Point(top.u+(bottom.u-top.u)*i/8, top.v+(bottom.v-top.v)*i/8) for i in range(9))
        self.assertTrue(any(tuple(bodice[i:i+9]) == body_seam for i in range(len(bodice)-8)))
        self.assertTrue(any(tuple(cap[i:i+9]) == tuple(reversed(body_seam)) for i in range(len(cap)-8)))
        right = self.params["relations"]["right_sleeve"]
        bulge = build_a.Point(350+1.18*(374-350), 119+right["cap_tube_transition"]*(302-119))
        inner = build_a.Point(bottom.u+0.53*(bulge.u-bottom.u), bottom.v+0.53*(bulge.v-bottom.v))
        cap_tube_seam = tuple(build_a.Point(bulge.u+(inner.u-bulge.u)*i/8, bulge.v+(inner.v-bulge.v)*i/8) for i in range(9))
        self.assertTrue(any(tuple(cap[i:i+9]) == cap_tube_seam for i in range(len(cap)-8)))
        self.assertTrue(any(tuple(tube[i:i+9]) == tuple(reversed(cap_tube_seam)) for i in range(len(tube)-8)))
        cuff_edge = build_a.cuff_outline(self.params["relations"]["cuff"], right)[:2]
        self.assertIn(cuff_edge[0], tube)
        self.assertIn(cuff_edge[1], tube)
        by_name = {part.name: part for part in parts}
        self.assertEqual({entry[0] for entry in by_name["puff-sleeve-cap"].attachments}, {"bodice"})
        self.assertEqual({entry[0] for entry in by_name["right-sleeve-tube"].attachments}, {"puff-sleeve-cap"})
        self.assertEqual({entry[0] for entry in by_name["dark-cuff-band"].attachments}, {"right-sleeve-tube"})
        projected_top = camera.project(by_name["puff-sleeve-cap"].support.local_to_world(top))
        self.assertAlmostEqual(projected_top[0], top.u, places=7)
        self.assertAlmostEqual(projected_top[1], top.v, places=7)
        for point in body_seam:
            body_world = by_name["bodice"].support.local_to_world(point)
            cap_world = by_name["puff-sleeve-cap"].support.local_to_world(point)
            for body_coordinate, cap_coordinate in zip(body_world, cap_world):
                self.assertAlmostEqual(body_coordinate, cap_coordinate, places=8)
        for point in cap_tube_seam:
            self.assertEqual(by_name["puff-sleeve-cap"].support.local_to_world(point), by_name["right-sleeve-tube"].support.local_to_world(point))
        for point in cuff_edge:
            tube_world = by_name["right-sleeve-tube"].support.local_to_world(point)
            cuff_world = by_name["dark-cuff-band"].support.local_to_world(point)
            for tube_coordinate, cuff_coordinate in zip(tube_world, cuff_world):
                self.assertAlmostEqual(tube_coordinate, cuff_coordinate, places=8)
        self.assertNotEqual(by_name["bodice"].support.depth_ref, by_name["puff-sleeve-cap"].support.depth_ref)
        seam_mid = build_a.Point((top.u+bottom.u)/2, (top.v+bottom.v)/2)
        away = build_a.Point(seam_mid.u+50*(bottom.v-top.v)/math.hypot(bottom.u-top.u, bottom.v-top.v), seam_mid.v-50*(bottom.u-top.u)/math.hypot(bottom.u-top.u, bottom.v-top.v))
        body_depth = camera.project(by_name["bodice"].support.local_to_world(away))[2]
        cap_depth = camera.project(by_name["puff-sleeve-cap"].support.local_to_world(away))[2]
        self.assertGreater(abs(body_depth-cap_depth), 0.005)

    def test_sleeve_and_cuff_share_the_opening_and_bow_has_unequal_parts(self):
        parts, shapes, _camera = build_a.make_components(self.params)
        sleeve = shapes["right-sleeve-tube"]
        cuff = shapes["dark-cuff-band"]
        cuff_anchors = build_a.cuff_outline(self.params["relations"]["cuff"], self.params["relations"]["right_sleeve"])
        self.assertEqual(cuff[:2], cuff_anchors[:2])
        self.assertIn(cuff[0], sleeve)
        self.assertIn(cuff[1], sleeve)
        centerline = self.params["relations"]["right_sleeve"]["anchors"]["cuff_center"]
        self.assertGreater(centerline[0], 350)
        self.assertEqual(len(self.params["relations"]["bow_left_tail"]["anchors"]), 4)
        self.assertNotEqual(self.params["relations"]["bow_left_loop"]["radii"], self.params["relations"]["bow_right_loop"]["radii"])
        self.assertEqual(self.params["relations"]["unclassified_blue_neighbor"]["intent"].split(";")[1].strip(), "not declared bow material or attached component")
        self.assertTrue(any(part.name == "bow-knot" for part in parts))
        self.assertTrue(any(part.name == "bow-down-tail" for part in parts))
        self.assertTrue(any(part.name == "collar-left" for part in parts))
        self.assertTrue(any(part.name == "collar-right" for part in parts))

    def test_named_shape_parameter_has_an_explainable_effect_without_teacher_input(self):
        changed = json.loads(json.dumps(self.params))
        changed["relations"]["bodice"]["neck_opening_depth"] += 4
        _parts_a, shapes_a, _camera_a = build_a.make_components(self.params)
        _parts_b, shapes_b, _camera_b = build_a.make_components(changed)
        self.assertNotEqual(shapes_a["bodice"], shapes_b["bodice"])
        # The runtime builder only accepts parameters; no path to crop/target is passed.
        self.assertEqual(build_a.make_components.__code__.co_argcount, 1)

    def test_visible_pipeline_is_deterministic_and_depth_derived(self):
        parts, _shapes, camera = build_a.make_components(self.params)
        faces = build_a.component_faces(parts, camera)
        self.assertTrue(faces)
        self.assertEqual(faces, build_a.component_faces(parts, camera))
        depths = [vertex[2] for triangle, _fill, _name in faces for vertex in triangle]
        self.assertGreater(max(depths)-min(depths), 0.4)
        # Visibility output is the existing opaque triangle backend, not layer-order SVG.
        visible_names = {name for _path, _fill, name in build_a.visible_regions(faces)}
        self.assertTrue({"bodice", "puff-sleeve-cap", "right-sleeve-tube", "dark-cuff-band", "bow-knot"}.issubset(visible_names))

    def test_renderer_has_no_teacher_path_and_depth_clips_semantic_lines(self):
        source = (SOURCE / "build_a.py").read_text(encoding="utf-8")
        for forbidden in ("image.jpg", "source-crop-registered.png", "teacher-only", "landmarks.csv", "teacher-topology-overlay.png"):
            self.assertNotIn(forbidden, source)
        parts, _shapes, camera = build_a.make_components(self.params)
        faces = build_a.component_faces(parts, camera)
        part_names = {part.name for part in parts}
        self.assertEqual(len(build_a.semantic_lines(self.params)), 7)
        for name, local, owner, _color, width in build_a.semantic_lines(self.params):
            self.assertIn(owner, part_names, name)
            self.assertGreater(width, 0)
            owner_part = next(part for part in parts if part.name == owner)
            points = [camera.project(owner_part.support.local_to_world(point)) for point in local]
            self.assertTrue(any(build_a.visible_segment_spans(a, b, faces, owner) for a, b in zip(points, points[1:])), name)

    def test_shared_contact_boundaries_have_no_unintended_positive_area(self):
        from scripts.articulated_construction import _overlap_samples
        parts, _shapes, _camera = build_a.make_components(self.params)
        by_name = {part.name: part for part in parts}
        self.assertEqual(_overlap_samples(by_name["bodice"].outline, by_name["puff-sleeve-cap"].outline), [])
        self.assertEqual(_overlap_samples(by_name["puff-sleeve-cap"].outline, by_name["right-sleeve-tube"].outline), [])
        self.assertEqual(_overlap_samples(by_name["right-sleeve-tube"].outline, by_name["dark-cuff-band"].outline), [])
        # The bow knot intentionally overlaps both loops and both tails to gather them.
        knot = by_name["bow-knot"].outline
        self.assertTrue(_overlap_samples(knot, by_name["bow-left-loop"].outline))
        self.assertTrue(_overlap_samples(knot, by_name["bow-right-loop"].outline))


if __name__ == "__main__":
    unittest.main()
