"""Bounded geometry, width, topology, winding, and sampling checks for ribbon_surface."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from ribbon_family import (BACK_STRIPE_COLOR, FRONT_STRIPE_COLOR, Camera, RibbonSpec,
                           build_mesh, centerline, mesh_triangles, mesh_triangles_uv,
                           project)
import ribbon_surface as ribbon_surface_module
from ribbon_surface import (arc_factor, build_surface, render_pair, surface_faces,
                            surface_point, surface_points, transverse_scale)
from vector_visibility import visible_fragments

CASES_PATH = ROOT / ".scratch/21-ribbon-cross-section/work/cases.json"
FAMILY_CASES_PATH = ROOT / ".scratch/19-ribbon-family/work/cases.json"
LEARNER_PATH = ROOT / ".scratch/19-ribbon-family/learner/gentle-s-ribbon.json"
BUILD_PATH = ROOT / ".scratch/21-ribbon-cross-section/work/build.py"
FINE_CASES_PATH = ROOT / ".scratch/21-ribbon-cross-section/work/cases-fine.json"
EVIDENCE_PATH = ROOT / ".scratch/21-ribbon-cross-section/evidence"
FINE_EVIDENCE_PATH = EVIDENCE_PATH / "fine"
HISTORICAL_VISIBILITY_SHA256 = "6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada"
HISTORICAL_VISIBILITY_SNAPSHOT = (ROOT / ".scratch/23-visibility-integration/provenance/snapshots"
                                  / "vector_visibility-pre-integration.py")


def length(vector):
    return math.sqrt(sum(value * value for value in vector))


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def barycentric(uv, triangle):
    a, b, c = triangle
    determinant = ((b[0] - a[0]) * (c[1] - a[1])
                   - (c[0] - a[0]) * (b[1] - a[1]))
    wb = ((uv[0] - a[0]) * (c[1] - a[1])
          - (c[0] - a[0]) * (uv[1] - a[1])) / determinant
    wc = ((b[0] - a[0]) * (uv[1] - a[1])
          - (uv[0] - a[0]) * (b[1] - a[1])) / determinant
    return 1.0 - wb - wc, wb, wc


def numeric_arc_factor(c, intervals=20000):
    step = 2.0 / intervals
    return sum(math.sqrt(1 + 4 * c * c * (-1 + (i + 0.5) * step) ** 2)
               for i in range(intervals)) * step


def uv_area2(triangle):
    a, b, c = triangle
    return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])


def canonical_edge(a, b):
    return tuple(sorted((tuple(a), tuple(b))))


def polygon_intersection(subject, clipper):
    output = list(subject)
    area = sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(clipper, clipper[1:] + clipper[:1]))
    orientation = 1 if area > 0 else -1
    for a, b in zip(clipper, clipper[1:] + clipper[:1]):
        incoming, output = output, []
        if not incoming:
            break
        def side(point):
            return orientation * ((b[0] - a[0]) * (point[1] - a[1])
                                  - (b[1] - a[1]) * (point[0] - a[0]))
        for p, q in zip(incoming, incoming[1:] + incoming[:1]):
            fp, fq = side(p), side(q)
            in_p, in_q = fp >= -1e-10, fq >= -1e-10
            if in_p != in_q:
                amount = fp / (fp - fq)
                output.append(tuple(p[k] + amount * (q[k] - p[k]) for k in range(3)))
            if in_q:
                output.append(q)
    return output


def polygon_area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1]))) / 2


def polygon_contains(poly, x, y):
    inside = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                inside = not inside
    return inside


def raster_row_length(row):
    return sum(length(subtract(a, b)) for a, b in zip(row, row[1:]))


def mesh_section_points(mesh, u):
    """Intersect the actual triangulated mesh with one u station, independent of smooth evaluators."""
    hits = {}
    def add(v, point):
        key = round(v * 10**12)
        if key in hits:
            if length(subtract(hits[key][1], point)) > 1e-8:
                raise AssertionError(f"mesh section is discontinuous at u={u:g}, v={v:g}")
        else:
            hits[key] = (v, point)

    for face in mesh.triangles:
        for index in range(3):
            a_uv, b_uv = face.uv[index], face.uv[(index + 1) % 3]
            a_xyz, b_xyz = face.points[index], face.points[(index + 1) % 3]
            delta_u = b_uv[0] - a_uv[0]
            if abs(delta_u) < 1e-13:
                if abs(u - a_uv[0]) < 1e-12:
                    add(a_uv[1], a_xyz)
                    add(b_uv[1], b_xyz)
            elif (u - a_uv[0]) * (u - b_uv[0]) <= 1e-14:
                amount = (u - a_uv[0]) / delta_u
                if -1e-10 <= amount <= 1 + 1e-10:
                    v = a_uv[1] + amount * (b_uv[1] - a_uv[1])
                    point = tuple(a_xyz[k] + amount * (b_xyz[k] - a_xyz[k])
                                  for k in range(3))
                    add(v, point)
    points = [point for _v, point in sorted(hits.values())]
    if len(points) < 2:
        raise AssertionError(f"no full-width section found at u={u:g}")
    return tuple(points)


def mesh_section_chord_length(mesh, u):
    return raster_row_length(mesh_section_points(mesh, u))


class RibbonSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        cls.case_rows = cls.plan["cases"]
        cls.family_cases = json.loads(FAMILY_CASES_PATH.read_text(encoding="utf-8"))
        cls.family_by_name = {row["name"]: row for row in cls.family_cases["cases"]}

    def spec(self, **overrides):
        data = {"name": "surface-test", "length": 3.0, "width": 0.36,
                "tip_ratio": 0.55, "bend": 0.42, "depth": 0.12,
                "twist": 0.0, "family": "arch", "origin": [-1.5, 0.0, 0.0],
                "heading": 0.0, "front": "#e68aa4", "back": "#7188bd",
                "segments": 40}
        data.update(overrides)
        return RibbonSpec.from_mapping(data)

    def test_cases_freeze_old_specs_cameras_and_one_camber_before_rendering(self):
        self.assertEqual(self.plan["frozen_camber"], 0.35)
        self.assertEqual([case["name"] for case in self.case_rows], [
            "positive-half-twist-front", "positive-half-twist-oblique",
            "failed-learner-negative-half-twist-front-regression-only",
            "failed-learner-negative-half-twist-oblique-regression-only",
            "untwisted-teaching-arch-front-control"])
        self.assertEqual(self.plan["sources"]["family_cases"]["sha256"], hashlib.sha256(
            FAMILY_CASES_PATH.read_bytes()).hexdigest())
        self.assertEqual(self.plan["sources"]["failed_learner"]["sha256"], hashlib.sha256(
            LEARNER_PATH.read_bytes()).hexdigest())
        self.assertEqual(self.plan["sources"]["old_ribbon_generator"]["sha256"], hashlib.sha256(
            (SCRIPTS / "ribbon_family.py").read_bytes()).hexdigest())
        # Exercise21 remains bound to its archived historical producer, not today's kernel.
        self.assertEqual(self.plan["sources"]["visibility_resolver"]["sha256"],
                         HISTORICAL_VISIBILITY_SHA256)
        self.assertEqual(hashlib.sha256(HISTORICAL_VISIBILITY_SNAPSHOT.read_bytes()).hexdigest(),
                         self.plan["sources"]["visibility_resolver"]["sha256"])
        for case in self.case_rows:
            self.assertEqual(case["camera_sha256"], hashlib.sha256(json.dumps(
                case["camera"], sort_keys=True, separators=(",", ":")).encode()).hexdigest())
            source_name = case["source"].get("case_name")
            source_spec = (json.loads(LEARNER_PATH.read_text(encoding="utf-8"))
                           if source_name is None else self.family_by_name[source_name]["ribbon"])
            self.assertEqual(case["source_spec_sha256"], hashlib.sha256(json.dumps(
                source_spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
            self.assertEqual(case["ribbon"], source_spec)
        plus = self.case_rows[0]["ribbon"]["twist"]
        minus = self.case_rows[2]["ribbon"]["twist"]
        self.assertAlmostEqual(plus, math.pi)
        self.assertAlmostEqual(minus, -math.pi)
        self.assertEqual(self.case_rows[2]["condition"], "untouched-failed-learner-regression-only")

    def test_saved_panel_cache_keys_bind_builder_raster_code_and_chromium(self):
        manifest = json.loads((EVIDENCE_PATH / "build-manifest.json").read_text(encoding="utf-8"))
        provenance = manifest["renderer_provenance"]
        self.assertEqual(provenance["builder_sha256"], hashlib.sha256(
            BUILD_PATH.read_bytes()).hexdigest())
        self.assertEqual(provenance["draw_py_sha256"], hashlib.sha256(
            (SCRIPTS / "draw.py").read_bytes()).hexdigest())
        self.assertTrue(provenance["chromium"]["path"].endswith("chrome-headless-shell"))
        self.assertIn("Google Chrome for Testing", provenance["chromium"]["version"])
        spec = importlib.util.spec_from_file_location("exercise21_build", BUILD_PATH)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        builder.plan = self.plan
        builder.provenance = provenance
        for index, case in enumerate(self.case_rows):
            for condition, camber in (("flat", 0.0), ("camber-035", 0.35)):
                stem = f"case-{index:02d}-{case['name']}-{condition}"
                metadata = json.loads((EVIDENCE_PATH / "cache" / f"{stem}.json").read_text())
                self.assertEqual(metadata["builder_sha256"], provenance["builder_sha256"])
                self.assertEqual(metadata["draw_py_sha256"], provenance["draw_py_sha256"])
                self.assertEqual(metadata["chromium"], provenance["chromium"])
                self.assertEqual(metadata["cache_key"], builder._cache_key(
                    index, case, condition, manifest["renderer_sha256"],
                    manifest["case_plan_sha256"]))
        self.assertTrue(all(board["renderer_provenance"] == provenance
                            for board in manifest["boards"]))

    def test_analytic_arc_factor_and_taper_are_independently_integrated(self):
        for c in (0.0, 0.12, 0.35, 0.5):
            self.assertAlmostEqual(arc_factor(c), numeric_arc_factor(c), delta=2e-9)
        spec = self.spec(width=0.48, tip_ratio=0.25)
        for u in (0.0, 0.25, 0.5, 1.0):
            requested = spec.width * (1 + (spec.tip_ratio - 1) * u)
            scale = transverse_scale(spec, u, 0.35)
            local = 0.35 * math.sin(math.pi * u) ** 2
            self.assertAlmostEqual(scale * arc_factor(local), requested, places=12)
            # The tempting fixed half-width would inflate material length for a bowed section.
            if u == 0.5:
                wrong_width = (requested / 2) * arc_factor(local)
                self.assertGreater(wrong_width, requested * 1.05)
        self.assertEqual(arc_factor(0), 2.0)
        with self.assertRaisesRegex(ValueError, "camber"):
            build_surface(spec, -0.01, 24, 6)
        with self.assertRaisesRegex(ValueError, "camber"):
            build_surface(spec, 0.51, 24, 6)

    def test_root_tip_and_sampled_centerline_remain_attached_for_both_conditions(self):
        spec = self.spec()
        curved = build_surface(spec, 0.35, 48, 8)
        flat = build_surface(spec, 0.0, 48, 8)
        self.assertEqual(curved.rows[0], flat.rows[0])
        self.assertEqual(curved.rows[-1], flat.rows[-1])
        for mesh in (flat, curved):
            self.assertEqual(mesh.base.centers[0], spec.origin)
            for index, row in enumerate(mesh.rows):
                center_vertex = row[len(row) // 2]
                self.assertLess(length(subtract(center_vertex, mesh.base.centers[index])), 1e-12)
                for v_index, point in enumerate(row):
                    v = -1 + 2 * v_index / mesh.v_intervals
                    if index in (0, len(mesh.rows) - 1):
                        expected = tuple(mesh.base.centers[index][axis]
                                         + v * (mesh.base.rows[index][1][axis]
                                                - mesh.base.rows[index][0][axis]) / 2
                                         for axis in range(3))
                        self.assertLess(length(subtract(point, expected)), 1e-12)
        self.assertEqual(centerline(spec, 0.0), spec.origin)

    def test_zero_camber_subdivides_each_legacy_triangle_without_replacing_its_surface(self):
        spec = self.spec(twist=math.pi, depth=0.3)
        old_mesh = build_mesh(spec, 24)
        flat = build_surface(spec, 0.0, 24, 6)
        old_uv = mesh_triangles_uv(old_mesh)
        old_world = mesh_triangles(old_mesh)
        area_by_source = [0.0] * len(old_uv)
        old_normals = []
        for tri in old_world:
            old_normals.append(cross(subtract(tri[1], tri[0]), subtract(tri[2], tri[0])))
        for face in flat.triangles:
            source_uv = tuple((vertex[1], vertex[2]) for vertex in old_uv[face.source_triangle])
            source_world = old_world[face.source_triangle]
            weights_area = abs(uv_area2(face.uv))
            area_by_source[face.source_triangle] += weights_area
            for uv, point in zip(face.uv, face.points):
                weights = barycentric(uv, source_uv)
                expected = tuple(sum(weights[j] * source_world[j][axis] for j in range(3))
                                 for axis in range(3))
                self.assertLess(length(subtract(point, expected)), 2e-12)
            actual_normal = cross(subtract(face.points[1], face.points[0]),
                                  subtract(face.points[2], face.points[0]))
            self.assertGreater(sum(x * y for x, y in zip(actual_normal,
                                                         old_normals[face.source_triangle])), 0)
        for index, triangle in enumerate(old_uv):
            self.assertAlmostEqual(area_by_source[index], abs(uv_area2(
                tuple((vertex[1], vertex[2]) for vertex in triangle))), places=11)

    def test_shared_uv_vertices_form_one_connected_surface_without_sampling_cracks(self):
        mesh = build_surface(self.spec(twist=math.pi), 0.35, 24, 8)
        incidence = {}
        for triangle in mesh.triangles:
            for a, b in zip(triangle.points, triangle.points[1:] + triangle.points[:1]):
                key = canonical_edge(a, b)
                incidence[key] = incidence.get(key, 0) + 1
        self.assertTrue(incidence)
        self.assertTrue(all(count in (1, 2) for count in incidence.values()))
        self.assertGreater(sum(count == 1 for count in incidence.values()), 0)
        self.assertGreater(sum(count == 2 for count in incidence.values()), 0)
        sampled_vertex_ids = {id(point) for triangle in mesh.triangles for point in triangle.points}
        for row in mesh.rows:
            self.assertEqual(len(row), mesh.v_intervals + 1)
            self.assertTrue(all(id(point) in sampled_vertex_ids for point in row))
        self.assertEqual(mesh.rows[0][0], mesh.base.rows[0][0])
        self.assertEqual(mesh.rows[0][-1], mesh.base.rows[0][1])
        self.assertEqual(mesh.rows[-1][0], mesh.base.rows[-1][0])
        self.assertEqual(mesh.rows[-1][-1], mesh.base.rows[-1][1])
        legacy_faces = mesh_triangles(mesh.base)
        for face in mesh.triangles:
            normal = cross(subtract(face.points[1], face.points[0]),
                           subtract(face.points[2], face.points[0]))
            self.assertTrue(all(math.isfinite(value) for value in normal))
            self.assertGreater(length(normal), 1e-10)
            legacy = legacy_faces[face.source_triangle]
            legacy_normal = cross(subtract(legacy[1], legacy[0]),
                                  subtract(legacy[2], legacy[0]))
            self.assertGreater(sum(a * b for a, b in zip(normal, legacy_normal)), 0)

    def test_sampled_cross_section_arc_length_and_taper_converge_to_requested_width(self):
        spec = self.spec(width=0.48, tip_ratio=0.3)
        measurements = []
        for v_count in (4, 8, 16):
            mesh = build_surface(spec, 0.35, 48, v_count)
            dense = surface_points(spec, mesh, 0.49,
                                   (-1 + 2 * i / 512 for i in range(513)))
            dense_arc = sum(length(subtract(a, b)) for a, b in zip(dense, dense[1:]))
            requested = spec.width * (1 + (spec.tip_ratio - 1) * 0.49)
            measurements.append(abs(raster_row_length(tuple(
                surface_point(spec, mesh, 0.49, -1 + 2 * i / v_count)
                for i in range(v_count + 1))) - dense_arc))
            self.assertLess(abs(dense_arc - requested), 1e-5)
        self.assertLess(measurements[1], measurements[0])
        self.assertLess(measurements[2], measurements[1])
        self.assertLess(measurements[2], 5e-4)
        root_tip = build_surface(spec, 0.35, 48, 12)
        self.assertAlmostEqual(raster_row_length(root_tip.rows[0]), spec.width, places=11)
        self.assertAlmostEqual(raster_row_length(root_tip.rows[-1]), spec.width * spec.tip_ratio,
                               places=11)

    def test_selected_finer_u_v_mesh_converges_without_hiding_off_station_width_error(self):
        spec = RibbonSpec.from_mapping(self.case_rows[0]["ribbon"])
        centerline_errors = []
        chord_errors = []
        for u_count, v_count in ((48, 6), (96, 12)):
            mesh_flat = build_surface(spec, 0.0, u_count, v_count)
            mesh_curve = build_surface(spec, 0.35, u_count, v_count)
            center_error = max(length(subtract(
                centerline(spec, (index + 0.5) / u_count),
                tuple((mesh_flat.base.centers[index][axis]
                       + mesh_flat.base.centers[index + 1][axis]) / 2 for axis in range(3))))
                for index in range(u_count))
            centerline_errors.append(center_error)
            u = 0.49
            sample_values = (-1 + 2 * i / 512 for i in range(513))
            dense_flat = surface_points(spec, mesh_flat, u, sample_values)
            dense_curve = surface_points(spec, mesh_curve, u,
                                         (-1 + 2 * i / 512 for i in range(513)))
            flat_arc = sum(length(subtract(a, b)) for a, b in zip(dense_flat, dense_flat[1:]))
            curve_arc = sum(length(subtract(a, b)) for a, b in zip(dense_curve, dense_curve[1:]))
            requested = spec.width * (1 + (spec.tip_ratio - 1) * u)
            self.assertLess(abs(curve_arc - flat_arc), 3e-6)
            self.assertLess(abs(curve_arc - requested), 1e-5)
            mesh_curve_line = surface_points(
                spec, mesh_curve, u, (-1 + 2 * i / v_count for i in range(v_count + 1)))
            chord_errors.append(abs(sum(length(subtract(a, b))
                                        for a, b in zip(mesh_curve_line, mesh_curve_line[1:]))
                                    - curve_arc))
        self.assertLess(centerline_errors[1], centerline_errors[0])
        self.assertLess(chord_errors[1], chord_errors[0])
        self.assertLess(chord_errors[1], 2e-3)

    def test_dense_off_station_width_preserves_legacy_arc_at_u_taper_and_twist_cases(self):
        rows_by_name = {row["name"]: row for row in self.case_rows}
        cases = [
            ("positive-half-twist-front", (0.19, 0.49, 0.51, 0.81)),
            ("failed-learner-negative-half-twist-front-regression-only", (0.19, 0.49, 0.51, 0.81)),
            ("untwisted-teaching-arch-front-control", (0.19, 0.49, 0.51, 0.81)),
            ("tapered-negative-twist-probe", (0.19, 0.49, 0.51, 0.81)),
        ]
        tapered = self.spec(name="tapered-negative-twist-probe", width=0.48,
                            tip_ratio=0.24, twist=-math.pi, bend=0.7, depth=0.3)
        for name, stations in cases:
            spec = tapered if name == "tapered-negative-twist-probe" else RibbonSpec.from_mapping(
                rows_by_name[name]["ribbon"])
            flat = build_surface(spec, 0.0, 48, 6)
            curved = build_surface(spec, 0.35, 48, 6)
            for u in stations:
                with self.subTest(case=name, u=u):
                    v_samples = [-1 + 2 * index / 512 for index in range(513)]
                    flat_points = surface_points(spec, flat, u, v_samples)
                    curved_points = surface_points(spec, curved, u, v_samples)
                    flat_arc = sum(length(subtract(a, b))
                                   for a, b in zip(flat_points, flat_points[1:]))
                    curved_arc = sum(length(subtract(a, b))
                                     for a, b in zip(curved_points, curved_points[1:]))
                    requested = spec.width * (1 + (spec.tip_ratio - 1) * u)
                    # The finite old mesh defines the zero-camber material section. Its chord
                    # integral must agree with the requested continuous width within 1e-5.
                    self.assertLess(abs(flat_arc - requested), 1e-5)
                    self.assertLess(abs(curved_arc - flat_arc), 3e-6)
                    self.assertLessEqual(curved_arc, flat_arc + 3e-6)
                    # Curvature preserves the old finite material centre, not a smoothed C(u).
                    self.assertLess(length(subtract(surface_point(spec, curved, u, 0),
                                                    surface_point(spec, flat, u, 0))), 1e-12)

    def test_fine_precision_plan_changes_only_sampling_and_bound_evidence(self):
        original = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        fine = json.loads(FINE_CASES_PATH.read_text(encoding="utf-8"))
        provenance = fine.pop("precision_retest")
        self.assertEqual(fine["sampling"]["u_intervals"], 96)
        self.assertEqual(fine["sampling"]["v_intervals"], 12)
        fine["sampling"] = original["sampling"]
        self.assertEqual(fine, original)
        self.assertEqual(provenance["original_case_plan_sha256"], hashlib.sha256(
            CASES_PATH.read_bytes()).hexdigest())
        parent_copy = ROOT / provenance["parent_independent_summary"]["evidence_copy_path"]
        self.assertEqual(provenance["parent_independent_summary"]["source_sha256"], hashlib.sha256(
            parent_copy.read_bytes()).hexdigest())
        grid = provenance["actual_mesh_u_probes"]["values"]
        expected = sorted({(i + 0.37) / 32 for i in range(32)}
                          | {(i + 0.5) / 96 for i in (0, 10, 21, 31, 42, 53, 63, 74, 84, 95)}
                          | {0.49, 0.51})
        self.assertEqual(len(grid), 44)
        self.assertEqual(grid, expected)
        self.assertEqual(provenance["selected_tolerance_world_units"], 0.002)

        flat_cases = {}
        unique = {}
        for case in fine["cases"]:
            unique.setdefault(case["ribbon"]["name"], case["ribbon"])
        for name, raw in unique.items():
            spec = RibbonSpec.from_mapping(raw)
            flat = build_surface(spec, 0.0, 96, 12)
            curved = build_surface(spec, 0.35, 96, 12)
            for u in grid:
                flat_width = mesh_section_chord_length(flat, u)
                curved_width = mesh_section_chord_length(curved, u)
                with self.subTest(case=name, u=u):
                    self.assertLessEqual(abs(flat_width - curved_width), 0.002)
        self.assertEqual(set(unique), {"twisted-two-sided", "gentle-s-ribbon", "teaching-arch"})

    def test_fine_matrix_cache_and_manifest_bind_precision_plan_and_renderer(self):
        fine_plan = json.loads(FINE_CASES_PATH.read_text(encoding="utf-8"))
        manifest = json.loads((FINE_EVIDENCE_PATH / "build-manifest.json").read_text(
            encoding="utf-8"))
        plan_hash = hashlib.sha256(FINE_CASES_PATH.read_bytes()).hexdigest()
        module_hash = hashlib.sha256((SCRIPTS / "ribbon_surface.py").read_bytes()).hexdigest()
        provenance = manifest["renderer_provenance"]
        self.assertEqual(manifest["case_plan_sha256"], plan_hash)
        self.assertEqual(provenance["builder_sha256"], hashlib.sha256(BUILD_PATH.read_bytes()).hexdigest())
        self.assertEqual(provenance["draw_py_sha256"], hashlib.sha256(
            (SCRIPTS / "draw.py").read_bytes()).hexdigest())
        spec = importlib.util.spec_from_file_location("exercise21_fine_build", BUILD_PATH)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        builder.plan = fine_plan
        builder.provenance = provenance
        self.assertEqual(len(manifest["panels"]), 10)
        for index, case in enumerate(fine_plan["cases"]):
            for condition, camber in (("flat", 0.0), ("camber-035", 0.35)):
                stem = f"case-{index:02d}-{case['name']}-{condition}"
                metadata = json.loads((FINE_EVIDENCE_PATH / "cache" / f"{stem}.json").read_text())
                self.assertEqual(metadata["sampling"], {"u_intervals": 96, "v_intervals": 12})
                self.assertEqual(metadata["case_plan_sha256"], plan_hash)
                self.assertEqual(metadata["renderer_sha256"], module_hash)
                self.assertEqual(metadata["builder_sha256"], provenance["builder_sha256"])
                self.assertEqual(metadata["draw_py_sha256"], provenance["draw_py_sha256"])
                self.assertEqual(metadata["chromium"], provenance["chromium"])
                self.assertEqual(metadata["cache_key"], builder._cache_key(
                    index, case, condition, module_hash, plan_hash))

    def test_selected_mesh_chord_width_bound_reports_failure_and_finer_convergence(self):
        # This measures the emitted 48x6 piecewise-triangle section, not the smooth diagnostic
        # evaluator. The declared 0.002 world-unit bound is intentionally not relaxed if it fails.
        samples = (0.0, 0.19, 0.49, 0.5, 0.51, 0.81, 1.0)
        frozen_unique = (
            ("positive-half-twist-front", self.case_rows[0]["ribbon"]),
            ("failed-learner-negative-half-twist-front-regression-only",
             self.case_rows[2]["ribbon"]),
            ("untwisted-teaching-arch-front-control", self.case_rows[4]["ribbon"]),
        )
        bound = 2e-3
        observed_failures = []
        for name, raw in frozen_unique:
            spec = RibbonSpec.from_mapping(raw)
            flat48, curved48 = build_surface(spec, 0.0, 48, 6), build_surface(spec, 0.35, 48, 6)
            for u in samples:
                flat_width = mesh_section_chord_length(flat48, u)
                curved_width = mesh_section_chord_length(curved48, u)
                signed_deficit = flat_width - curved_width
                if abs(signed_deficit) > bound:
                    observed_failures.append((name, u, signed_deficit))
                if u in (0.0, 1.0):
                    self.assertAlmostEqual(signed_deficit, 0.0, places=12)
            flat96, curved96 = build_surface(spec, 0.0, 96, 12), build_surface(spec, 0.35, 96, 12)
            finer_errors = [abs(mesh_section_chord_length(flat96, u)
                                - mesh_section_chord_length(curved96, u)) for u in samples]
            coarser_errors = [abs(mesh_section_chord_length(flat48, u)
                                  - mesh_section_chord_length(curved48, u)) for u in samples]
            self.assertLess(max(finer_errors), max(coarser_errors))
            if name == "positive-half-twist-front":
                self.assertLess(max(finer_errors), bound)
        self.assertTrue(observed_failures, "the diagnostic must expose rather than hide a selected-mesh bound failure")
        self.assertTrue(any(name == "positive-half-twist-front" and u in (0.49, 0.51)
                            and deficit > bound for name, u, deficit in observed_failures))
        self.assertTrue(any(name == "failed-learner-negative-half-twist-front-regression-only"
                            and u in (0.49, 0.51) and deficit < -bound
                            for name, u, deficit in observed_failures))

    def test_actual_normals_drive_across_width_facing_and_local_stripe(self):
        spec = self.spec(width=0.36, tip_ratio=1.0, twist=0.0, bend=0.0, depth=0.0)
        camera = Camera("grazing", 0, 80)
        flat = build_surface(spec, 0.0, 24, 8)
        curved = build_surface(spec, 0.35, 24, 8)
        def side_set(mesh):
            result = set()
            for face in mesh.triangles:
                if abs(sum(uv[0] for uv in face.uv) / 3 - 0.5) < 0.06:
                    v = sum(uv[1] for uv in face.uv) / 3
                    if abs(v) > 0.55:
                        normal = cross(subtract(face.points[1], face.points[0]),
                                       subtract(face.points[2], face.points[0]))
                        view = (0.0, math.sin(math.radians(80)), math.cos(math.radians(80)))
                        result.add("front" if sum(normal[i] * view[i] for i in range(3)) > 0
                                   else "back")
            return result
        self.assertEqual(side_set(flat), {"front"})
        self.assertEqual(side_set(curved), {"front", "back"})
        faces = surface_faces(spec, camera, curved)
        stripe = [face for face in faces if face[1] in {FRONT_STRIPE_COLOR, BACK_STRIPE_COLOR}]
        self.assertGreater(len(stripe), 0)
        self.assertTrue({fill for _points, fill, _name in stripe}
                        <= {FRONT_STRIPE_COLOR, BACK_STRIPE_COLOR})
        base_palette = {fill for _points, fill, _name in faces
                        if fill in {spec.front, spec.back}}
        self.assertEqual(base_palette, {spec.front, spec.back})

    def test_across_width_projection_fold_has_real_depth_order_for_visibility(self):
        spec = self.spec(width=0.36, tip_ratio=1.0, twist=0.0, bend=0.0, depth=0.0)
        mesh = build_surface(spec, 0.35, 24, 12)
        camera = Camera("grazing", 0, 80)
        # At u=.5 the projected section folds: v=0 and v=.5 nearly coincide while the latter
        # has greater camera depth. The 0.0002 tolerance is the analytic root's sample offset.
        row = mesh.rows[12]
        p0, p1 = project(row[6], camera), project(row[9], camera)
        self.assertLess(math.hypot(p0[0] - p1[0], p0[1] - p1[1]), 2e-4)
        self.assertGreater(p1[2] - p0[2], 0.005)
        near_candidates, far_candidates = [], []
        for triangle in mesh.triangles:
            u = sum(point[0] for point in triangle.uv) / 3
            v = sum(point[1] for point in triangle.uv) / 3
            projected = tuple(project(point, camera) for point in triangle.points)
            if abs(u - 0.5) < 0.04 and -0.30 <= v <= -0.10:
                near_candidates.append((triangle, projected))
            if abs(u - 0.5) < 0.04 and 0.60 <= v <= 0.80:
                far_candidates.append((triangle, projected))
        best = None
        for near_triangle, near_projected in near_candidates:
            for far_triangle, far_projected in far_candidates:
                overlap = polygon_intersection(list(near_projected), list(far_projected))
                area = polygon_area(overlap)
                if area > 1e-8 and (best is None or area > best[0]):
                    best = (area, near_triangle, near_projected, far_triangle,
                            far_projected, overlap)
        self.assertIsNotNone(best, "sampled across-width sheets must overlap in this fixed grazing view")
        _area, near_tri, near_poly, far_tri, far_poly, overlap = best
        probe_x = sum(point[0] for point in overlap) / len(overlap)
        probe_y = sum(point[1] for point in overlap) / len(overlap)
        near_name = "near-width-patch"
        far_name = "far-width-patch"
        near_face = (list(near_poly), "#e68aa4", near_name)
        far_face = (list(far_poly), "#7188bd", far_name)
        from vector_visibility import depth_plane
        near_depth = sum(depth_plane(near_poly)[i] * value
                         for i, value in enumerate((probe_x, probe_y, 1.0)))
        far_depth = sum(depth_plane(far_poly)[i] * value
                        for i, value in enumerate((probe_x, probe_y, 1.0)))
        expected = near_name if near_depth > far_depth else far_name
        self.assertGreater(abs(near_depth - far_depth), 1e-4)
        for ordered in ([near_face, far_face], [far_face, near_face]):
            visible = [(polygon, name) for polygon, _color, name in visible_fragments(ordered)
                       if polygon_contains(polygon, probe_x, probe_y)]
            self.assertEqual({name for _polygon, name in visible}, {expected})

    def test_shared_pair_fit_contains_every_flat_and_curved_mesh_vertex_with_margin(self):
        spec = RibbonSpec.from_mapping(self.case_rows[0]["ribbon"])
        camera = Camera("front", 0, 0)
        flat = build_surface(spec, 0.0, 48, 6)
        curved = build_surface(spec, 0.35, 48, 6)
        width, height, margin = 480, 320, 20
        scale, offset_x, offset_y = ribbon_surface_module._projected_fit(
            (flat, curved), camera, width, height, margin)
        for mesh in (flat, curved):
            for triangle in mesh.triangles:
                for point in triangle.points:
                    x, y, _depth = project(point, camera)
                    px, py = offset_x + scale * x, offset_y - scale * y
                    self.assertGreaterEqual(px, margin - 1e-9)
                    self.assertLessEqual(px, width - margin + 1e-9)
                    self.assertGreaterEqual(py, margin - 1e-9)
                    self.assertLessEqual(py, height - margin + 1e-9)

    def test_rendering_uses_named_fill_paths_no_mesh_ink_and_unique_ids(self):
        spec = self.spec(twist=math.pi)
        camera = Camera("front", 0, 0)
        flat_svg, curved_svg, _flat, _curved = render_pair(
            spec, camera, 24, 6, 360, 260, "determinism")
        self.assertEqual(flat_svg, render_pair(spec, camera, 24, 6, 360, 260,
                                                "determinism")[0])
        root = ET.fromstring(curved_svg)
        paths = root.findall(".//{http://www.w3.org/2000/svg}path")
        self.assertGreater(len(paths), 0)
        self.assertTrue(all("stroke" not in path.attrib and "fill" in path.attrib for path in paths))
        self.assertTrue(all("-fill-" in path.attrib["id"] for path in paths))
        ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn("<ns0:", curved_svg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
