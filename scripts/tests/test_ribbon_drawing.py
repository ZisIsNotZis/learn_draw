"""Geometry-provenance and drawing-rule regressions for semantic ribbon perimeter ink."""
import dataclasses
import hashlib
import importlib.util
import json
import math
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

import ribbon_drawing as drawing
from ribbon_family import Camera, RibbonSpec, build_mesh, mesh_triangles, mesh_triangles_uv, project, ribbon_faces
from vector_visibility import depth_plane, line_clip

HISTORICAL_WORK_CASES = ROOT / ".scratch/20-ribbon-drawing-rule/work/cases.json"
WORK_CASES = ROOT / ".scratch/23-visibility-integration/work/cases-current.json"
HISTORICAL_RENDERER_SNAPSHOT = (ROOT / ".scratch/23-visibility-integration/provenance/snapshots"
                                / "vector_visibility-pre-integration.py")
EXERCISE20_ARCHIVE = (ROOT / ".scratch/23-visibility-integration/provenance"
                      / "exercise20-archive-manifest.json")
EXERCISE20_ARCHIVE_SHA256 = "1cd95041ececdbd455417dda01a673db0b19f7aaadddae1920d88cd26850d37a"
EXERCISE20_ARCHIVE_FILE_COUNT = 115
EXPORTER_PATH = ROOT / ".scratch/20-ribbon-drawing-rule/work/build_cached.py"
EXPORTER_SPEC = importlib.util.spec_from_file_location("ribbon_build_cached", EXPORTER_PATH)
EXPORTER = importlib.util.module_from_spec(EXPORTER_SPEC)
EXPORTER_SPEC.loader.exec_module(EXPORTER)
SVG = {"svg": "http://www.w3.org/2000/svg"}


def _polygon_area(polygon):
    if len(polygon) < 3:
        return 0.0
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(polygon, polygon[1:] + polygon[:1])) / 2.0)


def _intersection_area(subject, convex_clip):
    if len(subject) < 3 or len(convex_clip) < 3:
        return 0.0
    area = sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(convex_clip, convex_clip[1:] + convex_clip[:1]))
    sign = 1.0 if area >= 0 else -1.0
    result = list(subject)
    for a, b in zip(convex_clip, convex_clip[1:] + convex_clip[:1]):
        result = line_clip(result, lambda p, a=a, b=b: sign * (
            (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])), True)
        if len(result) < 3:
            return 0.0
    return _polygon_area(result)


def _point_in_triangle(point, triangle, eps=1e-8):
    weights = drawing._barycentric2(point, triangle)
    return weights is not None and min(weights) >= -eps


def _support_edge_set(mesh):
    edges = set()
    for triangle in mesh_triangles(mesh):
        for a, b in zip(triangle, triangle[1:] + triangle[:1]):
            edges.add(tuple(sorted((a, b))))
    return edges


def _verify_exercise20_archive(manifest_path):
    """Verify the reviewed immutable manifest fingerprint, exact count, and every listed byte."""
    manifest_bytes = manifest_path.read_bytes()
    actual_manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    if actual_manifest_sha256 != EXERCISE20_ARCHIVE_SHA256:
        raise ValueError("exercise20 archive manifest fingerprint mismatch")
    archive = json.loads(manifest_bytes)
    files = archive["files"]
    if len(files) != EXERCISE20_ARCHIVE_FILE_COUNT:
        raise ValueError(f"exercise20 archive must list exactly {EXERCISE20_ARCHIVE_FILE_COUNT} files")
    paths = [item["path"] for item in files]
    if len(set(paths)) != EXERCISE20_ARCHIVE_FILE_COUNT:
        raise ValueError("exercise20 archive manifest contains duplicate paths")
    for item in files:
        path = ROOT / item["path"]
        if path.stat().st_size != item["bytes"]:
            raise ValueError(f"exercise20 archived size changed: {item['path']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"exercise20 archived bytes changed: {item['path']}")
    return archive


class RibbonDrawingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Current tests use the derived plan whose active resolver hash must match today's kernel.
        cls.items, cls.plan = drawing.load_case_plan(WORK_CASES)
        cls.historical_plan = json.loads(HISTORICAL_WORK_CASES.read_text(encoding="utf-8"))
        cls.by_name = {item["name"]: item for item in cls.items}
        cls.sampling = 24  # Test subdivision only; accepted comparisons use the frozen 128 override.

    def test_current_plan_changes_only_the_renderer_hash_and_binds_old_archive(self):
        migration = self.plan["renderer_migration"]
        current_sha = hashlib.sha256((SCRIPTS / "vector_visibility.py").read_bytes()).hexdigest()
        archived_sha = hashlib.sha256(HISTORICAL_RENDERER_SNAPSHOT.read_bytes()).hexdigest()
        self.assertEqual(migration["historical_renderer_sha256"], archived_sha)
        self.assertEqual(migration["current_renderer_sha256"], current_sha)
        self.assertEqual(self.plan["sources"]["visibility-resolver"]["sha256"], current_sha)
        self.assertEqual(self.plan["cases"], self.historical_plan["cases"])
        normalized = json.loads(json.dumps(self.plan))
        normalized.pop("renderer_migration")
        normalized["sources"]["visibility-resolver"]["sha256"] = archived_sha
        self.assertEqual(normalized, self.historical_plan,
                         "only resolver provenance and the explicit migration record may differ")

    def test_historical_plan_is_rejected_and_wrong_current_hash_is_rejected(self):
        old_sha = self.historical_plan["sources"]["visibility-resolver"]["sha256"]
        self.assertEqual(old_sha, hashlib.sha256(HISTORICAL_RENDERER_SNAPSHOT.read_bytes()).hexdigest())
        with self.assertRaisesRegex(ValueError, "frozen source hash changed: scripts/vector_visibility.py"):
            drawing.load_case_plan(HISTORICAL_WORK_CASES)

        wrong = json.loads(json.dumps(self.plan))
        wrong["sources"]["visibility-resolver"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="ribbon-current-plan-negative-") as directory:
            bad_plan = Path(directory) / "bad-current-plan.json"
            bad_plan.write_text(json.dumps(wrong), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "frozen source hash changed: scripts/vector_visibility.py"):
                drawing.load_case_plan(bad_plan)

    def test_exercise20_builder_default_remains_historical_and_cannot_load_new_renderer(self):
        builder_source = EXPORTER_PATH.read_text(encoding="utf-8")
        self.assertIn('default=ROOT / ".scratch/20-ribbon-drawing-rule/work/cases.json"',
                      builder_source)
        with self.assertRaisesRegex(ValueError, "frozen source hash changed: scripts/vector_visibility.py"):
            drawing.load_case_plan(HISTORICAL_WORK_CASES)

    def test_exercise20_historical_plan_images_and_caches_match_archive_hashes(self):
        archive = _verify_exercise20_archive(EXERCISE20_ARCHIVE)
        self.assertEqual(archive["scope"], "byte inventory of the untouched exercise20 historical plan, source, caches, images, and logs at renderer migration")

        # Negative control: 114 entries is still >100, but must not pass as the reviewed 115-file archive.
        with tempfile.TemporaryDirectory(prefix="exercise20-archive-negative-") as directory:
            dropped_entry = json.loads(json.dumps(archive))
            dropped_entry["files"].pop()
            self.assertGreater(len(dropped_entry["files"]), 100)
            tampered_copy = Path(directory) / "exercise20-archive-manifest.json"
            tampered_copy.write_text(json.dumps(dropped_entry), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exercise20 archive manifest fingerprint mismatch"):
                _verify_exercise20_archive(tampered_copy)
        self.assertEqual(hashlib.sha256(EXERCISE20_ARCHIVE.read_bytes()).hexdigest(),
                         EXERCISE20_ARCHIVE_SHA256)

    def item(self, name):
        return self.by_name[name]

    def compiled(self, name):
        item = self.item(name)
        spec = dataclasses.replace(item["spec"], segments=self.sampling)
        mesh = build_mesh(spec)
        return item, spec, mesh

    def test_complete_candidates_are_only_the_four_named_semantic_perimeter_edges(self):
        item, spec, mesh = self.compiled("frozen-crossback-front")
        candidates = drawing.perimeter_candidates(mesh)
        intervals = len(mesh.stations) - 1
        self.assertEqual(len(candidates), 2 * intervals + 2)
        self.assertEqual(sum(row.boundary == "v=-1" for row in candidates), intervals)
        self.assertEqual(sum(row.boundary == "v=+1" for row in candidates), intervals)
        self.assertEqual([row.boundary for row in candidates[-2:]], ["u=0", "u=1"])
        self.assertEqual(candidates[-1].source_triangle, 2 * intervals - 2)
        self.assertTrue(all(row.boundary in {"v=-1", "v=+1", "u=0", "u=1"}
                            for row in candidates))
        edges = _support_edge_set(mesh)
        for row in candidates:
            self.assertIn(tuple(sorted((row.point0, row.point1))), edges)

    def test_all_mesh_edge_ink_negative_control_contains_nonperimeter_edges(self):
        _item, _spec, mesh = self.compiled("frozen-crossback-front")
        semantic = drawing.perimeter_candidates(mesh)
        all_mesh_edges = _support_edge_set(mesh)
        semantic_edges = {tuple(sorted((row.point0, row.point1))) for row in semantic}
        self.assertTrue(semantic_edges.issubset(all_mesh_edges))
        # Every triangulation contributes diagonals/interior edges that are absent from semantic ink.
        self.assertGreater(len(all_mesh_edges), len(semantic_edges))
        self.assertEqual(len(semantic_edges), len(semantic))

    def test_teaching_arch_keeps_the_complete_visible_perimeter_and_no_mesh_edges(self):
        item, spec, mesh = self.compiled("teaching-arch-front")
        selection = drawing.select_visible_perimeter(spec, item["camera"], mesh)
        self.assertEqual(len(selection.candidates), 2 * self.sampling + 2)
        self.assertEqual({span.candidate_index for span in selection.spans},
                         {candidate.index for candidate in selection.candidates})
        self.assertTrue(all(span.boundary in {"v=-1", "v=+1", "u=0", "u=1"}
                            for span in selection.spans))
        self.assertTrue(all(span.source_triangle == selection.candidates[
            span.candidate_index].source_triangle for span in selection.spans))
        self.assertEqual({span.role for span in selection.spans}, {"silhouette"})

    def test_external_card_rejects_hidden_centerlines_and_clips_finite_ink_width(self):
        item, spec, mesh = self.compiled("external-support-card-front")
        bounds = item["card_bounds"]
        selection = drawing.select_visible_perimeter(spec, item["camera"], mesh, bounds)
        self.assertTrue(any(span.role == "overlap" and any(
            selection.scene_triangles[index].kind == "external"
            for index in span.farther_triangles) for span in selection.spans))
        # Every retained centerline sample is not behind either external card triangle.
        for span in selection.spans:
            middle = tuple((span.screen0[k] + span.screen1[k]) / 2 for k in range(3))
            for index in range(2):
                triangle = selection.projected_triangles[index]
                if _point_in_triangle(middle, triangle):
                    other = drawing._plane_at(depth_plane(triangle), middle)
                    owner = drawing._plane_at(
                        depth_plane(selection.projected_triangles[span.scene_owner_index]), middle)
                    self.assertFalse(drawing._is_front_occluder(
                        other, owner, index, span.scene_owner_index))

        fit = drawing._fit_points(mesh, item["camera"], bounds, 420, 250, 16)
        scale, offset_x, offset_y = fit
        card_planes = [depth_plane(triangle) for triangle in selection.projected_triangles[:2]]
        raw_leakage = 0.0
        clipped_leakage = 0.0
        stroke_shapes = drawing._stroke_shapes(selection, fit)
        for span in selection.spans:
            owner = span.scene_owner_index
            owner_plane = depth_plane(selection.projected_triangles[owner])
            a = (offset_x + scale * span.screen0[0],
                 offset_y - scale * span.screen0[1], span.screen0[2])
            b = (offset_x + scale * span.screen1[0],
                 offset_y - scale * span.screen1[1], span.screen1[2])
            width = drawing.OVERLAP_WIDTH_PX if span.role == "overlap" else drawing.SILHOUETTE_WIDTH_PX
            unmasked = drawing._line_rectangle(a, b, width)
            for card_index, triangle in enumerate(selection.projected_triangles[:2]):
                cover = drawing._clip_polygon_depth(triangle, card_planes[card_index], owner_plane,
                                                    card_index, owner)
                if len(cover) < 3:
                    continue
                cover = [(offset_x + scale * point[0], offset_y - scale * point[1], point[2])
                         for point in cover]
                raw_leakage = max(raw_leakage, _intersection_area(unmasked, cover))
        for role, _width, polygon, _candidate_ids, owner_triangle, _boundary in stroke_shapes:
            owner = (2 + owner_triangle)
            owner_plane = depth_plane(selection.projected_triangles[owner])
            for card_index, triangle in enumerate(selection.projected_triangles[:2]):
                cover = drawing._clip_polygon_depth(triangle, card_planes[card_index], owner_plane,
                                                    card_index, owner)
                if len(cover) < 3:
                    continue
                cover = [(offset_x + scale * point[0], offset_y - scale * point[1], point[2])
                         for point in cover]
                clipped_leakage = max(clipped_leakage, _intersection_area(polygon, cover))
        self.assertGreater(raw_leakage, 1e-4, "negative control must catch finite-width overpaint")
        self.assertLess(clipped_leakage, 1e-7,
                        "all emitted finite-width ink must be clipped where the nearer card covers it")

        # The frozen card hides nonzero intervals: a no-depth outline would paint these candidates.
        planes = tuple(depth_plane(triangle) for triangle in selection.projected_triangles)
        hidden_card_gap = False
        visible_by_candidate = {}
        for span in selection.spans:
            visible_by_candidate.setdefault(span.candidate_index, []).append((span.t0, span.t1))
        for candidate in selection.candidates:
            owner = 2 + candidate.source_triangle
            q0, q1 = (drawing.project(candidate.point0, item["camera"]),
                      drawing.project(candidate.point1, item["camera"]))
            cuts = drawing._split_parameters(candidate, item["camera"],
                                             selection.projected_triangles, planes, owner)
            for lo, hi in zip(cuts, cuts[1:]):
                if hi - lo <= drawing.CUT_MERGE_EPS:
                    continue
                middle = drawing._interpolate3(q0, q1, (lo + hi) / 2)
                card_hidden = any(_point_in_triangle(middle, selection.projected_triangles[index])
                                  and drawing._is_front_occluder(
                                      drawing._plane_at(planes[index], middle),
                                      drawing._plane_at(planes[owner], middle), index, owner)
                                  for index in range(2))
                if card_hidden:
                    self.assertFalse(any(a - drawing.CUT_MERGE_EPS <= lo
                                         and b + drawing.CUT_MERGE_EPS >= hi
                                         for a, b in visible_by_candidate.get(candidate.index, [])))
                    hidden_card_gap = True
        self.assertTrue(hidden_card_gap)

    def test_depth_reversal_recomputes_front_overlap_from_triangle_provenance(self):
        original, original_spec, original_mesh = self.compiled("frozen-crossback-front")
        reversed_item = self.item("crossback-depth-reversed-front")
        reversed_spec = dataclasses.replace(reversed_item["spec"], segments=self.sampling)
        reversed_mesh = build_mesh(reversed_spec)
        original_selection = drawing.select_visible_perimeter(original_spec,
                                                               original["camera"], original_mesh)
        reversed_selection = drawing.select_visible_perimeter(reversed_spec,
                                                               reversed_item["camera"], reversed_mesh)
        self.assertTrue(original_selection.spans)
        self.assertTrue(reversed_selection.spans)

        def overlap_center(selection):
            cells = [span.cell for span in selection.spans if span.role == "overlap"]
            self.assertTrue(cells)
            return sum((selection.candidates[span.candidate_index].uv0[0]
                        + selection.candidates[span.candidate_index].uv1[0]) / 2
                       for span in selection.spans if span.role == "overlap") / len(cells)

        first = overlap_center(original_selection)
        second = overlap_center(reversed_selection)
        self.assertLess((first - 0.5) * (second - 0.5), 0.0)
        self.assertNotEqual(first, second)
        self.assertTrue(all(span.farther_triangles for selection in
                            (original_selection, reversed_selection)
                            for span in selection.spans if span.role == "overlap"))

    def test_side_consistent_motif_covers_both_material_sides_over_full_local_u(self):
        item, spec, mesh = self.compiled("half-twist-oblique")
        motif = drawing.motif_triangles(spec, item["camera"], mesh)
        self.assertTrue(motif)
        self.assertEqual({face.side for face in motif}, {"front", "back"})
        self.assertEqual({face.fill for face in motif},
                         {drawing.MOTIF_CORE_COLOR, drawing.MOTIF_BORDER_COLOR})
        self.assertEqual({face.source_triangle for face in motif},
                         set(range(2 * self.sampling)))
        for face in motif:
            for u, v in face.uv:
                self.assertGreaterEqual(u, -1e-10)
                self.assertLessEqual(u, 1.0 + 1e-10)
                self.assertGreaterEqual(v, -drawing.MOTIF_OUTER_HALF_V - 1e-10)
                self.assertLessEqual(v, drawing.MOTIF_OUTER_HALF_V + 1e-10)
                if face.fill == drawing.MOTIF_CORE_COLOR:
                    self.assertLessEqual(abs(v), drawing.MOTIF_CORE_HALF_V + 1e-10)
        self.assertEqual((min(u for face in motif for u, _v in face.uv),
                          max(u for face in motif for u, _v in face.uv)), (0.0, 1.0))
        # Each clipped UV point interpolates on its original support triangle; no geometry is moved.
        support_uv = mesh_triangles_uv(mesh)
        for face in motif:
            source = support_uv[face.source_triangle]
            for point, uv in zip(face.points, face.uv):
                a, b, c = source
                ab = (b[1] - a[1], b[2] - a[2])
                ac = (c[1] - a[1], c[2] - a[2])
                ap = (uv[0] - a[1], uv[1] - a[2])
                det = ab[0] * ac[1] - ab[1] * ac[0]
                wb = (ap[0] * ac[1] - ap[1] * ac[0]) / det
                wc = (ab[0] * ap[1] - ab[1] * ap[0]) / det
                wa = 1 - wb - wc
                rebuilt = tuple(wa * a[0][axis] + wb * b[0][axis] + wc * c[0][axis]
                                for axis in range(3))
                self.assertLess(math.dist(point, rebuilt), 1e-10)

    def test_rule_a_preserves_control_fill_and_rule_b_preserves_support_triangles(self):
        item, spec, mesh = self.compiled("frozen-crossback-front")
        before = ribbon_faces(spec, item["camera"], mesh)
        control_svg, _ = drawing.render_panel(spec, item["camera"], "control", 360, 220,
                                               "control", sampling=self.sampling)
        rule_a_svg, _ = drawing.render_panel(spec, item["camera"], "A", 360, 220,
                                              "rule-a", sampling=self.sampling)
        rule_b_svg, _ = drawing.render_panel(spec, item["camera"], "B", 360, 220,
                                              "rule-b", sampling=self.sampling)
        self.assertEqual(before, ribbon_faces(spec, item["camera"], mesh))
        control = ET.fromstring(control_svg)
        rule_a = ET.fromstring(rule_a_svg)
        ns = SVG
        control_fills = [(path.attrib["d"], path.attrib["fill"])
                         for path in control.findall('.//svg:path[@data-component]', ns)]
        rule_a_fills = [(path.attrib["d"], path.attrib["fill"])
                        for path in rule_a.findall('.//svg:path[@data-component]', ns)]
        self.assertEqual(control_fills, rule_a_fills)
        lines = rule_a.findall('.//svg:path[@data-intent]', ns)
        self.assertTrue(lines)
        self.assertTrue(all(path.attrib["data-boundary"] in {"v=-1", "v=+1", "u=0", "u=1"}
                            for path in lines))
        self.assertTrue(all(path.attrib["data-source-triangle"].isdigit() for path in lines))
        widths = {path.attrib["data-intent"]: float(path.attrib["data-stroke-width-px"])
                  for path in lines}
        self.assertEqual(widths["silhouette"], drawing.SILHOUETTE_WIDTH_PX)
        if "overlap" in widths:
            self.assertEqual(widths["overlap"], drawing.OVERLAP_WIDTH_PX)
        self.assertTrue(any(path.attrib["fill"] == drawing.MOTIF_CORE_COLOR
                            for path in ET.fromstring(rule_b_svg).findall(
                                './/svg:path[@data-component]', ns)))

    def test_compiler_override_and_render_are_deterministic_with_unique_named_paths(self):
        item = self.item("teaching-arch-front")
        original_data = json.loads(WORK_CASES.read_text())
        spec = item["spec"]
        self.assertEqual(spec.segments, 40)
        first, summary = drawing.render_panel(spec, item["camera"], "B", 360, 220,
                                              "stable", sampling=self.sampling)
        second, second_summary = drawing.render_panel(spec, item["camera"], "B", 360, 220,
                                                     "stable", sampling=self.sampling)
        self.assertEqual(first, second)
        self.assertEqual(summary, second_summary)
        self.assertEqual(json.loads(WORK_CASES.read_text()), original_data)
        root = ET.fromstring(first)
        ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all("fill" in element.attrib for element in root.findall('.//svg:path', SVG)))
        self.assertEqual(build_mesh(dataclasses.replace(spec, segments=self.sampling)).stations[0], 0.0)
        self.assertEqual(build_mesh(dataclasses.replace(spec, segments=self.sampling)).stations[-1], 1.0)

    def test_line_only_panels_contain_only_depth_clipped_ink(self):
        item, spec, mesh = self.compiled("frozen-crossback-front")
        svg, _ = drawing.render_panel(spec, item["camera"], "A", 360, 220,
                                      "line-only", sampling=self.sampling, line_only=True)
        root = ET.fromstring(svg)
        self.assertEqual(root.findall('.//svg:path[@data-component]', SVG), [])
        self.assertTrue(root.findall('.//svg:path[@data-intent]', SVG))
        self.assertTrue(all(element.attrib.get("data-boundary") in
                            {"v=-1", "v=+1", "u=0", "u=1"}
                            for element in root.findall('.//svg:path[@data-intent]', SVG)))

    def test_fit_independently_centres_all_frozen_cases_in_both_cameras(self):
        cases, _plan = drawing.load_case_plan(WORK_CASES)
        cameras = (Camera("front", 0.0, 0.0), Camera("oblique", 38.0, 22.0))
        width, height, margin = 420, 250, 16.0
        for item in cases:
            spec = dataclasses.replace(item["spec"], segments=self.sampling)
            mesh = build_mesh(spec)
            world_points = [point for row in mesh.rows for point in row]
            if item["card_bounds"] is not None:
                left, bottom, right, top = item["card_bounds"]
                world_points.extend(((left, bottom, 0.0), (right, bottom, 0.0),
                                     (right, top, 0.0), (left, top, 0.0)))
            for camera in cameras:
                # Independent projection/bounds oracle: do not derive these values from _fit_points.
                projected = [project(point, camera) for point in world_points]
                min_x, max_x = min(p[0] for p in projected), max(p[0] for p in projected)
                min_y, max_y = min(p[1] for p in projected), max(p[1] for p in projected)
                expected_scale = min((width - 2 * margin) / (max_x - min_x),
                                     (height - 2 * margin) / (max_y - min_y))
                expected_x = (width - expected_scale * (min_x + max_x)) / 2
                expected_y = (height + expected_scale * (min_y + max_y)) / 2
                actual_scale, actual_x, actual_y = drawing._fit_points(
                    mesh, camera, item["card_bounds"], width, height, margin)
                self.assertAlmostEqual(actual_scale, expected_scale, places=10, msg=item["name"])
                self.assertAlmostEqual(actual_x, expected_x, places=10, msg=item["name"])
                self.assertAlmostEqual(actual_y, expected_y, places=10, msg=item["name"])
                canvas_x = (actual_x + actual_scale * min_x,
                            actual_x + actual_scale * max_x)
                canvas_y = (actual_y - actual_scale * max_y,
                            actual_y - actual_scale * min_y)
                self.assertAlmostEqual(sum(canvas_x) / 2, width / 2, places=8)
                self.assertAlmostEqual(sum(canvas_y) / 2, height / 2, places=8)
                self.assertGreaterEqual(canvas_x[0], margin - 1e-8)
                self.assertLessEqual(canvas_x[1], width - margin + 1e-8)
                self.assertGreaterEqual(canvas_y[0], margin - 1e-8)
                self.assertLessEqual(canvas_y[1], height - margin + 1e-8)

    def test_rasterized_teaching_panel_has_content_in_central_viewport(self):
        item = self.item("teaching-arch-front")
        svg, _ = drawing.render_panel(item["spec"], item["camera"], "control", 420, 250,
                                      "centred-teaching-panel", sampling=self.sampling)
        with tempfile.TemporaryDirectory(prefix="ribbon-drawing-centred-fit-") as temp_dir:
            svg_path = Path(temp_dir) / "panel.svg"
            png_path = Path(temp_dir) / "panel.png"
            svg_path.write_text(svg, encoding="utf-8")
            from draw import render
            render(str(svg_path), str(png_path), size=(420, 250))
            image = cv2.imread(str(png_path), cv2.IMREAD_COLOR)
        self.assertIsNotNone(image)
        center = image[62:188, 105:315]
        paper_bgr = np.array((246, 250, 251), dtype=np.uint8)
        painted = np.any(np.abs(center.astype(np.int16) - paper_bgr) > 12, axis=2)
        self.assertGreater(int(np.count_nonzero(painted)), 100)

    def test_cache_key_tracks_effective_derived_depth(self):
        item = next(item for item in self.items if item["spec"].depth != 0)
        changed = {**item, "spec": dataclasses.replace(item["spec"], depth=-item["spec"].depth)}
        self.assertEqual(item["source_spec_sha256"], changed["source_spec_sha256"])
        original_key = EXPORTER._cache_key(item, "B", "renderer-hash")
        self.assertEqual(original_key, EXPORTER._cache_key(dict(item), "B", "renderer-hash"))
        self.assertNotEqual(original_key, EXPORTER._cache_key(changed, "B", "renderer-hash"))

    def test_cached_line_only_export_raster_matches_direct_external_card(self):
        row = next(index for index, item in enumerate(self.items)
                   if item["name"] == "external-support-card-front")
        item = {**self.items[row], "sampling": self.sampling}
        prefix = EXPORTER._panel_prefix(row, item["name"], EXPORTER.RULES.index("B"))
        full_svg, _ = drawing.render_panel(item["spec"], item["camera"], "B",
                                           EXPORTER.PANEL_WIDTH, EXPORTER.PANEL_HEIGHT, prefix,
                                           False, item["card_bounds"], self.sampling, False)
        direct_svg, _ = drawing.render_panel(item["spec"], item["camera"], "B",
                                             EXPORTER.PANEL_WIDTH, EXPORTER.PANEL_HEIGHT, prefix,
                                             False, item["card_bounds"], self.sampling, True)
        exported_svg = EXPORTER._standalone_line_only(
            full_svg, EXPORTER.PANEL_WIDTH, EXPORTER.PANEL_HEIGHT)
        self.assertNotIn("<ns0:", exported_svg)
        self.assertNotIn("<ns0:", direct_svg)
        raster = EXPORTER._raster_equivalence(
            direct_svg, exported_svg, EXPORTER.PANEL_WIDTH, EXPORTER.PANEL_HEIGHT)
        self.assertEqual(raster["mismatched_pixels"], 0)
        self.assertGreater(raster["nonbackground_pixels"], 0)


if __name__ == "__main__":
    unittest.main()
