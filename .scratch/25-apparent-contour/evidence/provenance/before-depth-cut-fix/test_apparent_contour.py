"""Exercise25 geometry tests: select only actual, visible surface-turn contours."""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import sys
import unittest
from pathlib import Path

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[2]
sys.path.insert(0, str(WORK))
sys.path.insert(0, str(ROOT / "scripts"))

import apparent_contour as contour
import ribbon_drawing as footprint
from ribbon_family import camera_basis, project
from ribbon_surface import build_surface
from vector_visibility import EPS, _positive_area_overlap, depth_plane


class ApparentContourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.rows = contour.load_cases()
        cls.primary = cls.rows[0]
        cls.spec = dataclasses.replace(cls.primary["spec"], segments=96)
        cls.camera = cls.primary["camera"]
        cls.mesh = build_surface(cls.spec, 0.35, 96, 12)
        (cls.candidates, cls.spans, cls.projected) = contour.select_visible_contours(
            cls.mesh, cls.camera)
        cls.visible_faces = contour.visible_face_fragments(cls.mesh, cls.camera)
        cls.fit = contour.ribbon_surface._projected_fit(
            (build_surface(cls.spec, 0.0, 96, 12), cls.mesh), cls.camera, 480, 320)

    def _camera_line_frame(self, span):
        dx = span.screen1[0] - span.screen0[0]
        dy = span.screen1[1] - span.screen0[1]
        length = math.hypot(dx, dy)
        tangent = (dx / length, dy / length)
        normal = (-tangent[1], tangent[0])
        candidate = self.candidates[span.candidate_index]
        face = self.mesh.triangles[candidate.owners[0]]
        edge_keys = {contour._uv_key(candidate.uv0), contour._uv_key(candidate.uv1)}
        third = next(point for uv, point in zip(face.uv, face.points)
                     if contour._uv_key(uv) not in edge_keys)
        q0 = project(candidate.point0, self.camera)
        q1 = project(candidate.point1, self.camera)
        q3 = project(third, self.camera)
        side = contour._cross2((q1[0] - q0[0], q1[1] - q0[1]),
                               (q3[0] - q0[0], q3[1] - q0[1]))
        if side < 0:
            normal = (-normal[0], -normal[1])
        center = tuple((span.screen0[i] + span.screen1[i]) / 2 for i in range(3))
        return length, tangent, normal, center

    def _card_area(self, polygon, card_triangles):
        fit = self.fit
        canvas_cards = [contour._canvas_polygon(tuple(project(p, self.camera) for p in tri), fit)
                        for tri in card_triangles]
        return sum(contour._polygon_area(contour._clip_convex_polygon(polygon, card))
                   for card in canvas_cards)

    def test_pins_and_import_paths_are_exact(self):
        self.assertEqual(contour.verify_pins(), contour.PINNED_SHA256)
        self.assertEqual(hashlib.sha256(contour.PLAN_PATH.read_bytes()).hexdigest(),
                         contour.PINNED_SHA256[".scratch/24-clean-support-replay/work/cases-current.json"])

    def test_every_candidate_is_a_shared_depth_separating_projected_fold(self):
        edge_map = contour._triangle_edges(self.mesh)
        projected = tuple(tuple(project(point, self.camera) for point in face.points)
                          for face in self.mesh.triangles)
        self.assertTrue(self.candidates)
        for candidate in self.candidates:
            edge_key = tuple(sorted([contour._uv_key(candidate.uv0),
                                     contour._uv_key(candidate.uv1)]))
            self.assertIn(edge_key, edge_map)
            self.assertEqual(len(candidate.owners), 2)
            a, b = candidate.owners
            self.assertTrue((candidate.facing_cosines[0] > 0 > candidate.facing_cosines[1])
                            or (candidate.facing_cosines[0] < 0 < candidate.facing_cosines[1]))
            p0, p1 = project(candidate.point0, self.camera), project(candidate.point1, self.camera)
            def third(face_id):
                face = self.mesh.triangles[face_id]
                keys = {contour._uv_key(candidate.uv0), contour._uv_key(candidate.uv1)}
                return next(point for uv, point in zip(face.uv, face.points)
                            if contour._uv_key(uv) not in keys)
            q_a, q_b = project(third(a), self.camera), project(third(b), self.camera)
            side_a = contour._cross2((p1[0] - p0[0], p1[1] - p0[1]),
                                     (q_a[0] - p0[0], q_a[1] - p0[1]))
            side_b = contour._cross2((p1[0] - p0[0], p1[1] - p0[1]),
                                     (q_b[0] - p0[0], q_b[1] - p0[1]))
            self.assertGreater(side_a * side_b, 0.0)
            self.assertTrue(_positive_area_overlap(projected[a], projected[b]))
            plane_a, plane_b = depth_plane(projected[a]), depth_plane(projected[b])
            overlap = contour._overlap_polygon(projected[a], projected[b])
            witness = (sum(p[0] for p in overlap) / len(overlap),
                       sum(p[1] for p in overlap) / len(overlap), 0.0)
            delta = footprint._plane_at(plane_a, witness) - footprint._plane_at(plane_b, witness)
            self.assertAlmostEqual(delta, candidate.overlap_depth_delta, places=8)
            self.assertGreater(abs(delta), footprint.TIE_BIAS + EPS)
            self.assertEqual(len(candidate.owners), len(set(candidate.owners)))

    def test_mesh_diagonals_are_not_automatically_lines(self):
        candidates = {frozenset((contour._uv_key(candidate.uv0),
                                 contour._uv_key(candidate.uv1))) for candidate in self.candidates}
        edges = contour._triangle_edges(self.mesh)
        diagonal_edges = 0
        rejected_same_facing_diagonals = 0
        view = camera_basis(self.camera)[2]
        face_facing = []
        for face in self.mesh.triangles:
            normal = contour._face_normal(face)
            face_facing.append(contour._dot(normal, view) / contour._norm(normal))
        for edge, owners in edges.items():
            if len(owners) != 2:
                continue
            du = edge[0][0] - edge[1][0]
            dv = edge[0][1] - edge[1][1]
            if du == 0 or dv == 0:
                continue
            diagonal_edges += 1
            a, b = owners[0][0], owners[1][0]
            if face_facing[a] * face_facing[b] > 0:
                rejected_same_facing_diagonals += 1
                self.assertNotIn(frozenset(edge), candidates)
        self.assertGreater(diagonal_edges, len(candidates))
        self.assertGreater(rejected_same_facing_diagonals, 0)
        self.assertLess(len(candidates), len(edges) / 20,
                        "a material perimeter or all-edge mesh wireframe must not pass")

    def test_untwisted_arch_is_a_true_negative_control(self):
        row = self.rows[4]
        mesh = build_surface(dataclasses.replace(row["spec"], segments=96), 0.35, 96, 12)
        candidates, spans, _projected = contour.select_visible_contours(mesh, row["camera"])
        self.assertEqual(candidates, ())
        self.assertEqual(spans, ())
        self.assertEqual(contour.build_ink_patches(spans, {}, self.fit), ())

    def test_camera_change_recomputes_contour_from_same_support(self):
        camera_front = self.camera
        camera_oblique = self.rows[1]["camera"]
        front = {frozenset((contour._uv_key(c.uv0), contour._uv_key(c.uv1)))
                 for c in contour.discover_contours(self.mesh, camera_front)}
        oblique = {frozenset((contour._uv_key(c.uv0), contour._uv_key(c.uv1)))
                   for c in contour.discover_contours(self.mesh, camera_oblique)}
        self.assertNotEqual(front, oblique)
        self.assertTrue(front and oblique)

    def test_foreground_card_hides_centerline_not_just_a_flag(self):
        self.assertTrue(self.spans)
        span = max(self.spans, key=lambda item: math.dist(item.screen0[:2], item.screen1[:2]))
        length, tangent, normal, center = self._camera_line_frame(span)
        card = contour.camera_line_card(self.camera, center, tangent, normal,
                                        (-length / 2 - 0.02, length / 2 + 0.02),
                                        (-0.08, 0.08), toward_viewer=0.5)
        card_triangles = contour.split_card(card)
        _candidates, obscured_spans, _projected = contour.select_visible_contours(
            self.mesh, self.camera, card_triangles)
        for visible in obscured_spans:
            if visible.candidate_index == span.candidate_index:
                overlap = min(visible.t1, span.t1) - max(visible.t0, span.t0)
                self.assertLessEqual(overlap, contour.CUT_MERGE_EPS,
                                     "foreground card must hide the selected centerline interval")

    def test_foreground_card_clips_finite_width_without_hiding_centerline(self):
        span = max(self.spans, key=lambda item: math.dist(item.screen0[:2], item.screen1[:2]))
        length, tangent, normal, center = self._camera_line_frame(span)
        half_width_world = contour.INK_WIDTH_PX / (2.0 * self.fit[0])
        card = contour.camera_line_card(
            self.camera, center, tangent, normal,
            (-0.25 * length, 0.25 * length),
            (0.15 * half_width_world, 0.95 * half_width_world), toward_viewer=0.5)
        card_triangles = contour.split_card(card)
        _candidates, visible_spans, _projected = contour.select_visible_contours(
            self.mesh, self.camera, card_triangles)
        target_spans = [item for item in visible_spans
                        if item.candidate_index == span.candidate_index
                        and min(item.t1, span.t1) - max(item.t0, span.t0) > contour.CUT_MERGE_EPS]
        self.assertTrue(target_spans, "card geometry must leave the centerline visible")
        card_projected = [tuple(project(point, self.camera) for point in tri)
                          for tri in card_triangles]
        a = (self.fit[1] + self.fit[0] * span.screen0[0],
             self.fit[2] - self.fit[0] * span.screen0[1], span.screen0[2])
        b = (self.fit[1] + self.fit[0] * span.screen1[0],
             self.fit[2] - self.fit[0] * span.screen1[1], span.screen1[2])
        raw = footprint._line_rectangle(a, b, contour.INK_WIDTH_PX)
        self.assertGreater(self._card_area(raw, card_triangles), 1e-5,
                           "negative control must put a real foreground card through finite ink width")
        visible_faces = contour.visible_face_fragments(self.mesh, self.camera, card_triangles)
        patches = contour.build_ink_patches(target_spans, visible_faces, self.fit)
        leakage = sum(self._card_area(patch.polygon, card_triangles) for patch in patches)
        self.assertLess(leakage, 1e-6,
                        "finite-width ink must be clipped to actual depth-visible source faces")

    def test_render_overlay_changes_only_by_deterministic_ink_group(self):
        source = (ROOT / self.rows[0]["control_panel"]).read_text(encoding="utf-8")
        group = contour.serialize_group((), "empty-control")
        self.assertEqual(group, "")
        patches = contour.build_ink_patches(self.spans, self.visible_faces, self.fit)
        one = contour.serialize_group(patches, "repeatable-case")
        two = contour.serialize_group(patches, "repeatable-case")
        self.assertEqual(one, two)
        candidate = contour.overlay_group(source, one)
        self.assertEqual(contour.remove_group(candidate, one), source)
        self.assertIn('data-line-width-px="1.2"', one)


if __name__ == "__main__":
    unittest.main()
