from __future__ import annotations

import inspect
import xml.etree.ElementTree as ET
import unittest
from pathlib import Path

import compile_case as cc


class CompileCaseTests(unittest.TestCase):
    def test_closed_enums_and_exact_compiler_api(self):
        self.assertEqual({item.value for item in cc.CaseId}, set(cc.CASE_ORDER))
        self.assertEqual({item.value for item in cc.ArtPolicy}, {"SIDE_DEPENDENT", "SHARED_FIXED_LOCAL"})
        self.assertEqual(tuple(inspect.signature(cc.compile_case).parameters),
                         ("case_id", "policy", "output_path"))

    def test_all_pinned_inputs_match(self):
        expected = {**cc.PINNED_INPUTS, **cc.PROTECTED_ARTIFACTS,
                    f"external:{next(iter(cc.EXTERNAL_PINS))}": next(iter(cc.EXTERNAL_PINS.values()))}
        self.assertEqual(cc.verify_pinned_inputs(), expected)

    def test_exact_one_variable_local_art_and_kernel_fragments(self):
        for case_id in cc.CaseId:
            with self.subTest(case=case_id.value):
                proof = cc.validate_scene_pair(case_id)
                self.assertEqual(proof["submitted_inputs"],
                                 162 if case_id is cc.CaseId.CARD_DPLUS else 160)
                self.assertEqual(proof["support_triangles"], 64)
                self.assertEqual(proof["local_uv_stripe_triangles"], 96)
                self.assertTrue(proof["input_geometry_identical"])
                self.assertTrue(proof["source_order_uv_camera_depth_identical"])
                self.assertTrue(proof["visible_depth_fragments_identical_excluding_pigment"])

    def test_shared_local_stripe_generation_never_queries_facing_side(self):
        rr, spec, camera = cc._spec_and_camera(cc.CaseId.PRIMARY_DPLUS)
        mesh = rr.build_return_mesh(spec, 16, 2)
        original = cc._facing_side

        def forbidden(*_args):
            raise AssertionError("shared stripe pigment must not consult side/camera")

        cc._facing_side = forbidden
        try:
            stripes = cc._local_stripe_triangles(mesh, camera, cc.ArtPolicy.SHARED_FIXED_LOCAL)
        finally:
            cc._facing_side = original
        self.assertEqual(len(stripes), 96)
        self.assertTrue(all(item.pigment == "#472639" and item.provenance == "local-uv-stripe"
                            for item in stripes))

    def test_rejects_invalid_case_policy_path_and_mutable_config(self):
        with self.assertRaises(TypeError):
            cc.compile_case("primary-dplus", cc.ArtPolicy.SHARED_FIXED_LOCAL, Path("bad.svg"))
        with self.assertRaises(TypeError):
            cc.compile_case(cc.CaseId.PRIMARY_DPLUS, "SHARED_FIXED_LOCAL", Path("bad.svg"))
        with self.assertRaises(TypeError):
            cc.compile_case([cc.CaseId.PRIMARY_DPLUS], cc.ArtPolicy.SHARED_FIXED_LOCAL, Path("bad.svg"))
        with self.assertRaises(ValueError):
            cc.compile_case(cc.CaseId.PRIMARY_DPLUS, cc.ArtPolicy.SHARED_FIXED_LOCAL,
                            cc.ROOT / ".." / "escape.svg")
        with self.assertRaises(TypeError):
            cc.compile_case(cc.CaseId.PRIMARY_DPLUS, cc.ArtPolicy.SHARED_FIXED_LOCAL,
                            cc.PANELS / "primary-dplus--SHARED_FIXED_LOCAL.svg", side="front")
        for control in ("role", "side", "screen", "per_view", "depth_override"):
            with self.subTest(control=control), self.assertRaises(TypeError):
                cc.compile_case(cc.CaseId.PRIMARY_DPLUS, cc.ArtPolicy.SHARED_FIXED_LOCAL,
                                cc.PANELS / "primary-dplus--SHARED_FIXED_LOCAL.svg", **{control: True})

    def test_rejects_changed_pinned_source_hash(self):
        actual_digest = cc.sha256_file

        def fake_digest(path):
            if path == cc.KERNEL_PATH:
                return "0" * 64
            return actual_digest(path)

        cc.sha256_file = fake_digest
        try:
            with self.assertRaisesRegex(RuntimeError, "pinned input hash mismatch"):
                cc.verify_pinned_inputs()
        finally:
            cc.sha256_file = actual_digest

    def test_final_panel_namespace_dimensions_and_no_overwrite(self):
        for case_id in cc.CaseId:
            for policy in cc.ArtPolicy:
                with self.subTest(case=case_id.value, policy=policy.value):
                    path = cc.PANELS / f"{case_id.value}--{policy.value}.svg"
                    self.assertTrue(path.is_file())
                    root = ET.fromstring(path.read_text(encoding="utf-8"))
                    self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                    self.assertEqual(root.attrib["width"], "420")
                    self.assertEqual(root.attrib["height"], "320")
                    raster = cc._audit_png(path.with_suffix(".png"), (420, 320))
                    self.assertTrue(raster["nonblank"])
                    self.assertGreaterEqual(min(raster["pixel_margins"]), 4)
                    with self.assertRaises(FileExistsError):
                        cc.compile_case(case_id, policy, path)

    def test_embedded_panels_have_no_routing_filename(self):
        for path in cc.PANELS.glob("*.svg"):
            self.assertNotIn("comparison-unlabelled", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
