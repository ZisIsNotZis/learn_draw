"""Bounded tests for generated semantic-perimeter depth cues and twist convergence."""
import dataclasses
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK.parent.parent.parent / "scripts"))
sys.path.insert(0, str(WORK))

import occlusion_probe as probe
from ribbon_family import Camera, RibbonSpec, build_mesh, mesh_triangles, ribbon_artwork_faces
from vector_visibility import EPS, depth_plane


CASES_PATH = WORK / "cases.json"


class OcclusionProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.cameras = probe.load_frozen_cases()
        cls.case_by_name = {case["name"]: case for case in cls.cases}

    def spec(self, name):
        return RibbonSpec.from_mapping(self.case_by_name[name]["ribbon"])

    def test_candidates_span_only_full_local_perimeter(self):
        mesh = build_mesh(self.spec("awkward-crossing"))
        candidates = probe.perimeter_candidates(mesh)
        cells = len(mesh.stations) - 1
        self.assertEqual(len(candidates), 2 * cells + 2)
        self.assertEqual(sum(c.boundary == "v=-1" for c in candidates), cells)
        self.assertEqual(sum(c.boundary == "v=+1" for c in candidates), cells)
        self.assertEqual([c.boundary for c in candidates[-2:]], ["u=0", "u=1"])
        for candidate in candidates:
            if candidate.boundary == "v=-1":
                self.assertEqual((candidate.uv0[1], candidate.uv1[1]), (-1.0, -1.0))
            elif candidate.boundary == "v=+1":
                self.assertEqual((candidate.uv0[1], candidate.uv1[1]), (1.0, 1.0))
            else:
                self.assertEqual(candidate.uv0[0], candidate.uv1[0])
                self.assertIn(candidate.uv0[0], (0.0, 1.0))

    def test_crossing_cue_is_visible_perimeter_masking_a_far_nonadjacent_face(self):
        spec = self.spec("awkward-crossing")
        mesh = build_mesh(spec)
        selection = probe.select_perimeter_cues(spec, self.cameras[0], mesh)
        self.assertTrue(selection.paths)
        self.assertTrue(selection.intervals)
        selected_ids = {piece.candidate_index for piece in selection.intervals}
        self.assertGreater(len(selection.intervals), len(selected_ids))
        self.assertLess(len(selected_ids), len(selection.candidates))
        # This is the counterexample to an all-perimeter outline: most generated candidates are not selected.
        self.assertGreater(len(selection.candidates) - len(selected_ids), 0)

        candidates = {candidate.index: candidate for candidate in selection.candidates}
        source_cells = tuple(index // 2 for index in range(len(selection.support_triangles)))
        planes = tuple(depth_plane(triangle) for triangle in selection.projected_triangles)
        for piece in selection.intervals:
            candidate = candidates[piece.candidate_index]
            self.assertEqual(piece.boundary, candidate.boundary)
            self.assertGreater(piece.minimum_depth_gap, EPS)
            self.assertTrue(piece.masked_triangles)
            self.assertTrue(all(abs(source_cells[face] - candidate.cell) > 1
                                for face in piece.masked_triangles))
            if piece.boundary == "v=-1":
                self.assertTrue(all(abs(uv[1] + 1) < 1e-10 for uv in (piece.uv0, piece.uv1)))
            elif piece.boundary == "v=+1":
                self.assertTrue(all(abs(uv[1] - 1) < 1e-10 for uv in (piece.uv0, piece.uv1)))
            else:
                self.assertEqual(piece.uv0[0], piece.uv1[0])
                self.assertIn(piece.uv0[0], (0.0, 1.0))

            # Recheck that no closer nonadjacent triangle covers this whole selected subinterval.
            middle = tuple((piece.screen0[i] + piece.screen1[i]) / 2 for i in range(3))
            far_found = set()
            for face, triangle in enumerate(selection.projected_triangles):
                if abs(source_cells[face] - candidate.cell) <= 1 or planes[face] is None:
                    continue
                weights = probe._barycentric2(middle, triangle)
                if weights is None or min(weights) <= probe.BARYCENTRIC_EPS:
                    continue
                depth = probe._depth_plane_value(planes[face], middle)
                self.assertLessEqual(depth, middle[2] + EPS)
                if depth < middle[2] - EPS:
                    far_found.add(face)
            self.assertTrue(far_found.intersection(piece.masked_triangles))

        # Reversing depth selects a source boundary from the other traversal half, without a stored u range.
        reversed_spec = dataclasses.replace(spec, depth=-abs(spec.depth))
        reversed_selection = probe.select_perimeter_cues(reversed_spec, self.cameras[0])
        self.assertTrue(reversed_selection.paths)

        def average_source_u(result):
            cells_seen = {cell for path in result.paths for cell in path.source_cells}
            return sum((mesh.stations[cell] + mesh.stations[cell + 1]) / 2
                       for cell in cells_seen) / len(cells_seen)

        self.assertLess((average_source_u(selection) - 0.5)
                        * (average_source_u(reversed_selection) - 0.5), 0)

    def test_teaching_case_produces_no_occlusion_cue(self):
        spec = self.spec("teaching-arch")
        selection = probe.select_perimeter_cues(spec, self.cameras[0])
        self.assertEqual(selection.intervals, ())
        self.assertEqual(selection.paths, ())
        self.assertTrue(probe.perimeter_candidates(build_mesh(spec)))

    def test_original_fills_are_unchanged_and_cue_is_a_separate_overlay(self):
        spec = self.spec("awkward-crossing")
        camera = self.cameras[0]
        mesh = build_mesh(spec)
        original = ribbon_artwork_faces(spec, camera, mesh)
        selection = probe.select_perimeter_cues(spec, camera, mesh)
        before = probe._panel(spec, camera, 573, 250, "Fill + stripe", "same support",
                              mesh, (), "before", True)
        after = probe._panel(spec, camera, 573, 250, "Generated cue", "computed from depth",
                             mesh, selection.paths, "after", True)
        self.assertEqual(original, ribbon_artwork_faces(spec, camera, mesh))
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        before_root, after_root = ET.fromstring(before), ET.fromstring(after)
        before_fill = [(path.attrib["d"], path.attrib["fill"])
                       for path in before_root.findall('.//svg:path[@data-component]', namespace)]
        after_fill = [(path.attrib["d"], path.attrib["fill"])
                      for path in after_root.findall('.//svg:path[@data-component]', namespace)]
        self.assertEqual(before_fill, after_fill)
        strokes = after_root.findall('.//svg:path[@data-probe-cue="semantic-perimeter"]', namespace)
        self.assertEqual(len(strokes), len(selection.paths))
        self.assertTrue(all(path.attrib["fill"] == "none" and "stroke" in path.attrib
                            for path in strokes))
        self.assertTrue(all(path.attrib["data-boundary"] in {"v=-1", "v=+1", "u=0", "u=1"}
                            for path in strokes))
        self.assertEqual(before, probe._panel(spec, camera, 573, 250, "Fill + stripe",
                                             "same support", mesh, (), "before", True))

    def test_twist_pinch_remains_while_facing_zero_converges(self):
        spec = self.spec("twisted-two-sided")
        camera = self.cameras[1]
        mesh40 = build_mesh(dataclasses.replace(spec, segments=40), 40)
        mesh128 = build_mesh(dataclasses.replace(spec, segments=128), 128)
        root40, root128 = probe.facing_zero(mesh40, camera), probe.facing_zero(mesh128, camera)
        self.assertLess(abs(root40 - root128), 0.002)
        for mesh, root in ((mesh40, root40), (mesh128, root128)):
            self.assertGreater(probe._facing_value(mesh, camera, root - 0.01), 0)
            self.assertLess(probe._facing_value(mesh, camera, root + 0.01), 0)
            self.assertLess(abs(probe._facing_value(mesh, camera, root)), 1e-3)
        self.assertEqual((mesh40.stations[0], mesh40.stations[-1]), (0.0, 1.0))
        self.assertEqual((mesh128.stations[0], mesh128.stations[-1]), (0.0, 1.0))

    def test_board_generation_is_repeatable_and_unlabelled_has_no_text(self):
        first, manifest, summary = probe._board_svg(self.cases, self.cameras, labels=False)
        second, other_manifest, other_summary = probe._board_svg(self.cases, self.cameras, labels=False)
        self.assertEqual(first, second)
        self.assertEqual(manifest, other_manifest)
        self.assertEqual(summary, other_summary)
        root = ET.fromstring(first)
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        self.assertEqual(root.findall(".//svg:text", namespace), [])
        self.assertTrue(root.findall('.//svg:path[@data-probe-cue="semantic-perimeter"]', namespace))
        self.assertEqual(summary["teaching_selected_paths"], 0)
        self.assertAlmostEqual(summary["twist_facing_zero_40"],
                               summary["twist_facing_zero_128"], delta=0.002)


if __name__ == "__main__":
    unittest.main()
