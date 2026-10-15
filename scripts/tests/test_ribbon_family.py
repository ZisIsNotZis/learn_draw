"""Geometric contract tests for the bounded ribbon-family generator."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

import cv2
import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from ribbon_family import (BACK_STRIPE_COLOR, DIAGNOSTIC_SUPPORT_CARD_COLOR,
                           FRONT_STRIPE_COLOR, PANEL_ARTWORK_TOP, RIBBON_STRIPE_HALF_V, Camera,
                           RibbonSpec, build_mesh, card_faces, centerline, face_side,
                           load_case_file, make_board, make_panel, mesh_triangles,
                           mesh_triangles_uv, project, render_board, ribbon_artwork_faces,
                           ribbon_artwork_triangles, ribbon_faces)
from draw import render
from vector_visibility import visible_fragments


CASES_PATH = ROOT / ".scratch/19-ribbon-family/work/cases.json"


def length(v):
    return math.sqrt(sum(value * value for value in v))


def area2_uv(triangle):
    a, b, c = triangle
    return ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2


def barycentric_uv(point, triangle):
    a, b, c = triangle
    determinant = 2 * area2_uv(triangle)
    px, py = point[0] - a[0], point[1] - a[1]
    ux, uy = b[0] - a[0], b[1] - a[1]
    vx, vy = c[0] - a[0], c[1] - a[1]
    weight_b = (px * vy - py * vx) / determinant
    weight_c = (ux * py - uy * px) / determinant
    return 1 - weight_b - weight_c, weight_b, weight_c


def distance2(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def principal_crossing_pair(spec):
    """Solve the nontrivial x(u)=x(1-u) root instead of pinning a sampled station."""
    lo, hi = 0.1, 0.25
    heading = spec.heading
    for _ in range(64):
        u = (lo + hi) / 2
        first, second = centerline(spec, u), centerline(spec, 1 - u)
        difference = ((first[0] - second[0]) * math.cos(heading)
                      + (first[1] - second[1]) * math.sin(heading))
        if difference < 0:
            lo = u
        else:
            hi = u
    near_u = (lo + hi) / 2
    return near_u, 1 - near_u


def segment_triangle_intersection(start, end, triangle, eps=1e-10):
    """Möller–Trumbore segment/triangle probe for this non-coplanar regression mesh."""
    a, b, c = triangle
    edge_a = tuple(b[i] - a[i] for i in range(3))
    edge_b = tuple(c[i] - a[i] for i in range(3))
    direction = tuple(end[i] - start[i] for i in range(3))
    cross_dir = (direction[1] * edge_b[2] - direction[2] * edge_b[1],
                 direction[2] * edge_b[0] - direction[0] * edge_b[2],
                 direction[0] * edge_b[1] - direction[1] * edge_b[0])
    determinant = sum(edge_a[i] * cross_dir[i] for i in range(3))
    if abs(determinant) < eps:
        return None
    inverse = 1 / determinant
    offset = tuple(start[i] - a[i] for i in range(3))
    bary_u = inverse * sum(offset[i] * cross_dir[i] for i in range(3))
    cross_offset = (offset[1] * edge_a[2] - offset[2] * edge_a[1],
                    offset[2] * edge_a[0] - offset[0] * edge_a[2],
                    offset[0] * edge_a[1] - offset[1] * edge_a[0])
    bary_v = inverse * sum(direction[i] * cross_offset[i] for i in range(3))
    along = inverse * sum(edge_b[i] * cross_offset[i] for i in range(3))
    if (bary_u < -eps or bary_v < -eps or bary_u + bary_v > 1 + eps
            or along < -eps or along > 1 + eps):
        return None
    return tuple(start[i] + along * direction[i] for i in range(3))


def first_nonlocal_mesh_intersection(mesh):
    """Return an exact mesh-edge/triangle hit for separated u cells, if one exists."""
    triangles = mesh_triangles(mesh)
    cells = len(mesh.stations) - 1
    for first in range(cells):
        for second in range(first + 2, cells):
            for first_half in (0, 1):
                a = triangles[2 * first + first_half]
                for second_half in (0, 1):
                    b = triangles[2 * second + second_half]
                    for edge, target in ((a, b), (b, a)):
                        for index in range(3):
                            hit = segment_triangle_intersection(edge[index], edge[(index + 1) % 3],
                                                                target)
                            if hit is not None:
                                return first, second, first_half, second_half, hit
    return None


def covers(poly, x, y):
    inside = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                inside = not inside
    return inside


def visible_names(faces, point):
    x, y = point[:2]
    return [name for polygon, _color, name in visible_fragments(faces) if covers(polygon, x, y)]


def visible_colors(fragments, point):
    x, y = point[:2]
    return [color for polygon, color, _name in fragments if covers(polygon, x, y)]


def visible_fragment_names(fragments, point):
    x, y = point[:2]
    return [name for polygon, _color, name in fragments if covers(polygon, x, y)]


def crossing_triangle_faces(spec, camera, mesh, station_index, name):
    triangles = mesh_triangles(mesh)[station_index * 2:station_index * 2 + 2]
    return [([project(point, camera) for point in triangle], spec.front, name)
            for triangle in triangles]


def stripe_patch_faces(spec, camera, mesh, cells, name):
    return [([project(point, camera) for point in face.points], face.fill, name)
            for face in ribbon_artwork_triangles(spec, camera, mesh)
            if face.source_triangle // 2 in cells
            and face.fill in {FRONT_STRIPE_COLOR, BACK_STRIPE_COLOR}]


class RibbonFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.cameras = load_case_file(CASES_PATH)
        cls.case_by_name = {case["name"]: case for case in cls.cases}

    def spec(self, **overrides):
        data = {"name": "test-ribbon", "length": 3.0, "width": 0.36,
                "tip_ratio": 1.0, "bend": 0.42, "depth": 0.12,
                "twist": 0.0, "family": "arch", "origin": [-1.5, 0.0, 0.0],
                "heading": 0.0, "segments": 48}
        data.update(overrides)
        return RibbonSpec.from_mapping(data)

    def test_local_strip_is_connected_and_adjacent_faces_share_exact_boundaries(self):
        mesh = build_mesh(self.spec())
        triangles = mesh_triangles(mesh)
        self.assertEqual(len(triangles), 2 * (len(mesh.stations) - 1))
        for index in range(len(mesh.rows) - 2):
            low, high = mesh.rows[index + 1]
            next_first = triangles[(index + 1) * 2]
            next_second = triangles[(index + 1) * 2 + 1]
            self.assertIs(triangles[index * 2][1], next_first[0])
            self.assertIs(triangles[index * 2][2], next_second[2])
            self.assertIs(triangles[index * 2 + 1][1], next_second[2])
            self.assertIs(mesh.rows[index + 1][0], low)
            self.assertIs(mesh.rows[index + 1][1], high)
        self.assertEqual(mesh.stations[0], 0.0)
        self.assertEqual(mesh.stations[-1], 1.0)
        self.assertTrue(all(a < b for a, b in zip(mesh.stations, mesh.stations[1:])))

    def test_attachment_center_and_tangent_survive_shape_variations(self):
        common = {"origin": (1.2, -0.8, 0.3), "heading": 0.47, "family": "arch"}
        base = self.spec(**common)
        varied = self.spec(**common, bend=2.0, depth=-1.1, twist=math.pi,
                           tip_ratio=0.23, width=0.7)
        first, second = build_mesh(base), build_mesh(varied)
        self.assertEqual(first.centers[0], base.origin)
        self.assertEqual(second.centers[0], varied.origin)
        self.assertAlmostEqual(length(tuple(a - b for a, b in zip(
            first.tangents[0], second.tangents[0]))), 0.0, delta=1e-6)
        self.assertEqual(centerline(base, 0.0), centerline(varied, 0.0))
        self.assertAlmostEqual(first.centers[-1][0], common["origin"][0] +
                               base.length * math.cos(common["heading"]), places=10)

    def test_local_stripe_partitions_each_original_support_triangle_in_uv(self):
        spec = self.spec(twist=math.pi, segments=32)
        camera = Camera("front", 0, 0)
        mesh = build_mesh(spec)
        source_triangles = mesh_triangles_uv(mesh)
        artwork = ribbon_artwork_triangles(spec, camera, mesh)
        by_source = {index: [] for index in range(len(source_triangles))}
        stripe_uv = []
        for face in artwork:
            by_source[face.source_triangle].append(face)
            source = source_triangles[face.source_triangle]
            source_world = tuple(vertex[0] for vertex in source)
            source_uv = tuple((vertex[1], vertex[2]) for vertex in source)
            self.assertEqual(face.side, face_side(source_world, camera))
            for point, uv in zip(face.points, face.uv):
                weights = barycentric_uv(uv, source_uv)
                self.assertGreaterEqual(min(weights), -1e-9)
                reconstructed = tuple(sum(weights[j] * source_world[j][axis] for j in range(3))
                                      for axis in range(3))
                self.assertLess(length(tuple(point[axis] - reconstructed[axis]
                                             for axis in range(3))), 1e-10)
            if face.fill in {FRONT_STRIPE_COLOR, BACK_STRIPE_COLOR}:
                stripe_uv.extend(face.uv)
                self.assertLessEqual(max(abs(uv[1]) for uv in face.uv),
                                     RIBBON_STRIPE_HALF_V + 1e-12)
                expected = FRONT_STRIPE_COLOR if face.side == "front" else BACK_STRIPE_COLOR
                self.assertEqual(face.fill, expected)
            else:
                v_values = [uv[1] for uv in face.uv]
                self.assertTrue(max(v_values) <= -RIBBON_STRIPE_HALF_V + 1e-12
                                or min(v_values) >= RIBBON_STRIPE_HALF_V - 1e-12)

        for index, source in enumerate(source_triangles):
            faces = by_source[index]
            self.assertTrue(faces)
            source_uv = tuple((vertex[1], vertex[2]) for vertex in source)
            expected_band_area = abs(area2_uv(source_uv)) * RIBBON_STRIPE_HALF_V
            self.assertAlmostEqual(sum(abs(area2_uv(face.uv)) for face in faces),
                                   expected_band_area, places=10)
        self.assertAlmostEqual(min(uv[0] for uv in stripe_uv), 0.0, places=10)
        self.assertAlmostEqual(max(uv[0] for uv in stripe_uv), 1.0, places=10)
        original_base_faces = ribbon_faces(spec, camera, mesh)
        combined_artwork = ribbon_artwork_faces(spec, camera, mesh)
        self.assertEqual(combined_artwork[-len(original_base_faces):], original_base_faces)

    def test_width_is_perpendicular_to_centerline_and_tip_ratio_is_measured(self):
        spec = self.spec(width=0.48, tip_ratio=0.22)
        mesh = build_mesh(spec)
        for index in (0, len(mesh.rows) // 2, len(mesh.rows) - 1):
            low, high = mesh.rows[index]
            tangent = mesh.tangents[index]
            width_vector = tuple(high[i] - low[i] for i in range(3))
            u = mesh.stations[index]
            expected = spec.width * (1 + (spec.tip_ratio - 1) * u)
            self.assertAlmostEqual(length(width_vector), expected, places=7)
            self.assertAlmostEqual(sum(width_vector[i] * tangent[i] for i in range(3)),
                                   0.0, delta=1e-7)
        self.assertAlmostEqual(length(tuple(mesh.rows[0][1][i] - mesh.rows[0][0][i]
                                            for i in range(3))), spec.width, places=7)
        self.assertAlmostEqual(length(tuple(mesh.rows[-1][1][i] - mesh.rows[-1][0][i]
                                            for i in range(3))), spec.width * 0.22, places=7)

    def test_facing_comes_from_winding_and_twist_exposes_both_sides(self):
        camera = Camera("front", 0, 0)
        untwisted = build_mesh(self.spec(twist=0.0))
        twisted = build_mesh(self.spec(twist=math.pi))
        first_triangle = mesh_triangles(untwisted)[0]
        reversed_triangle = tuple(reversed(first_triangle))
        self.assertEqual(face_side(first_triangle, camera), "front")
        self.assertEqual(face_side(reversed_triangle, camera), "back")
        plain_sides = {color for _tri, color, _name in ribbon_faces(
            self.spec(twist=0.0), camera, untwisted)}
        twisted_sides = {color for _tri, color, _name in ribbon_faces(
            self.spec(twist=math.pi), camera, twisted)}
        self.assertEqual(plain_sides, {"#e68aa4"})
        self.assertEqual(twisted_sides, {"#e68aa4", "#7188bd"})
        self.assertEqual(face_side(mesh_triangles(twisted)[-1], camera), "back")
        striped = ribbon_artwork_triangles(self.spec(twist=math.pi), camera, twisted)
        stripe_fills = {face.fill for face in striped
                        if face.fill in {FRONT_STRIPE_COLOR, BACK_STRIPE_COLOR}}
        self.assertEqual(stripe_fills, {FRONT_STRIPE_COLOR, BACK_STRIPE_COLOR})
        self.assertTrue(all((face.fill == FRONT_STRIPE_COLOR and face.side == "front")
                            or (face.fill == BACK_STRIPE_COLOR and face.side == "back")
                            or face.fill in {self.spec().front, self.spec().back}
                            for face in striped))

    def test_parallel_transport_frames_and_normals_remain_finite_and_oriented(self):
        camera = Camera("oblique", 38, 22)
        for family in ("arch", "s-curve", "crossback"):
            spec = self.spec(family=family, bend=4.0, depth=3.5, twist=4 * math.pi,
                             segments=96)
            mesh = build_mesh(spec)
            self.assertTrue(all(math.isfinite(v) for row in mesh.rows for point in row for v in point))
            self.assertTrue(all(abs(length(tangent) - 1) < 1e-7 for tangent in mesh.tangents))
            self.assertTrue(all(abs(length(axis) - 1) < 1e-7 for axis in mesh.width_axes))
            for tangent, axis in zip(mesh.tangents, mesh.width_axes):
                self.assertAlmostEqual(sum(a * b for a, b in zip(tangent, axis)), 0.0, delta=1e-7)
            for a, b in zip(mesh.width_axes, mesh.width_axes[1:]):
                self.assertGreater(sum(x * y for x, y in zip(a, b)), 0.0)
            for triangle in mesh_triangles(mesh):
                edge_a = tuple(triangle[1][axis] - triangle[0][axis] for axis in range(3))
                edge_b = tuple(triangle[2][axis] - triangle[0][axis] for axis in range(3))
                normal = (edge_a[1] * edge_b[2] - edge_a[2] * edge_b[1],
                          edge_a[2] * edge_b[0] - edge_a[0] * edge_b[2],
                          edge_a[0] * edge_b[1] - edge_a[1] * edge_b[0])
                self.assertTrue(all(math.isfinite(value) for value in normal))
                self.assertGreater(length(normal), 1e-8)
                self.assertIn(face_side(triangle, camera), {"front", "back"})

    def test_preselected_crossing_has_near_and_far_depth_without_local_surface_intersection(self):
        spec = RibbonSpec.from_mapping(self.case_by_name["awkward-crossing"]["ribbon"])
        camera = Camera("front", 0, 0)
        mesh = build_mesh(spec, 128)
        u_near, u_far = principal_crossing_pair(spec)
        p_near, p_far = centerline(spec, u_near), centerline(spec, u_far)
        projected_near, projected_far = project(p_near, camera), project(p_far, camera)
        self.assertLess(distance2(projected_near, projected_far), 0.004)
        self.assertGreater(projected_near[2], 0.20)
        self.assertLess(projected_far[2], -0.20)
        self.assertGreater(projected_near[2] - projected_far[2], 0.4)

        # Test local full-width patches, not only their centreline points: their depth intervals
        # remain separated, so the projected crossing is not a physical surface intersection.
        near_index, far_index = round(u_near * 128), round(u_far * 128)
        near_depths = [point[2] for row in mesh.rows[near_index - 1:near_index + 2] for point in row]
        far_depths = [point[2] for row in mesh.rows[far_index - 1:far_index + 2] for point in row]
        self.assertGreater(min(near_depths), max(far_depths) + 0.2)

    def test_corrected_crossback_meshes_converge_without_nonlocal_triangle_intersections(self):
        plane = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        hit = segment_triangle_intersection((0.2, 0.2, -1.0), (0.2, 0.2, 1.0), plane)
        self.assertIsNotNone(hit)
        for actual, expected in zip(hit, (0.2, 0.2, 0.0)):
            self.assertAlmostEqual(actual, expected, places=12)
        self.assertIsNone(segment_triangle_intersection((2.0, 2.0, -1.0), (2.0, 2.0, 1.0), plane))
        spec = RibbonSpec.from_mapping(self.case_by_name["awkward-crossing"]["ribbon"])
        previous_error = None
        for segments in (32, 48, 64, 96):
            mesh = build_mesh(spec, segments)
            maximum_error = max(
                length(tuple(centerline(spec, (index + 0.5) / segments)[axis]
                             - (mesh.centers[index][axis] + mesh.centers[index + 1][axis]) / 2
                             for axis in range(3)))
                for index in range(segments))
            if previous_error is not None:
                self.assertLess(maximum_error, previous_error)
            previous_error = maximum_error
            # This exact triangle-edge probe covers separated u cells in the frozen mesh only;
            # it does not certify a continuous surface or arbitrary parameter values.
            self.assertIsNone(first_nonlocal_mesh_intersection(mesh), segments)

        near_u, far_u = principal_crossing_pair(spec)
        near, far = centerline(spec, near_u), centerline(spec, far_u)
        self.assertLess(distance2(near, far), 1e-10)
        self.assertGreater(abs(near[2] - far[2]), 0.4)

    def test_card_depth_probes_and_visibility_do_not_depend_on_declaration_order(self):
        spec = RibbonSpec.from_mapping(self.case_by_name["body-card"]["ribbon"])
        camera = Camera("front", 0, 0)
        mesh = build_mesh(spec, 128)
        card = [
            ([(x, y, z) for x, y, z in triangle], "#d8e4da", "support-card")
            for triangle in (
                [project(point, camera) for point in ((-0.52, -0.50, 0), (0.52, -0.50, 0),
                                                       (0.52, 0.45, 0))],
                [project(point, camera) for point in ((-0.52, -0.50, 0), (0.52, 0.45, 0),
                                                       (-0.52, 0.45, 0))],
            )]
        u_near, u_far = principal_crossing_pair(spec)
        near_index, far_index = round(u_near * 128), round(u_far * 128)
        near_faces = crossing_triangle_faces(spec, camera, mesh, near_index, "near-ribbon-probe")
        far_faces = crossing_triangle_faces(spec, camera, mesh, far_index, "far-ribbon-probe")
        near_point = project(centerline(spec, near_index / 128), camera)
        far_point = project(centerline(spec, far_index / 128), camera)
        self.assertGreater(near_point[2], 0)
        self.assertLess(far_point[2], 0)

        front_order = near_faces + card
        reverse_order = card + near_faces
        self.assertEqual(visible_names(front_order, near_point), ["near-ribbon-probe"])
        self.assertEqual(visible_names(reverse_order, near_point), ["near-ribbon-probe"])
        crossing_order = near_faces + far_faces
        crossing_reverse = far_faces + near_faces
        self.assertEqual(visible_names(crossing_order, near_point), ["near-ribbon-probe"])
        self.assertEqual(visible_names(crossing_reverse, near_point), ["near-ribbon-probe"])

        # The local stripe is the same uncut UV artwork on both visits; only depth selects which
        # source patch remains at their shared projected centreline.
        near_stripe = stripe_patch_faces(spec, camera, mesh, {near_index - 1, near_index},
                                         "near-local-stripe")
        far_stripe = stripe_patch_faces(spec, camera, mesh, {far_index - 1, far_index},
                                        "far-local-stripe")
        self.assertTrue(visible_names(near_stripe, near_point))
        self.assertTrue(visible_names(far_stripe, near_point))
        self.assertEqual(set(visible_names(near_stripe + far_stripe, near_point)),
                         {"near-local-stripe"})
        self.assertEqual(set(visible_names(far_stripe + near_stripe, near_point)),
                         {"near-local-stripe"})
        near_base = crossing_triangle_faces(spec, camera, mesh, near_index, "near-base")
        far_base = crossing_triangle_faces(spec, camera, mesh, far_index, "far-base")
        actual_order = near_stripe + far_stripe + near_base + far_base
        reversed_order = far_stripe + near_stripe + far_base + near_base
        self.assertEqual(set(visible_names(actual_order, near_point)), {"near-local-stripe"})
        self.assertEqual(set(visible_names(reversed_order, near_point)), {"near-local-stripe"})
        self.assertEqual(visible_colors(visible_fragments(actual_order), near_point),
                         [FRONT_STRIPE_COLOR])
        # Remove the separately located near patch: the negative-depth ribbon is hidden by the card.
        self.assertEqual(visible_names(far_faces + card, far_point), ["support-card"])
        self.assertEqual(visible_names(card + far_faces, far_point), ["support-card"])

    def test_default_tessellation_centerline_error_is_bounded_for_supported_extreme_shapes(self):
        # For 48 stations, midpoint chord error stays below 0.04 world units in the tested
        # maximum length/bend/depth envelope; this is not a guarantee for surface shading or lines.
        for family in ("arch", "s-curve", "crossback"):
            spec = self.spec(length=6, bend=9, depth=9, twist=4 * math.pi,
                             family=family, segments=48)
            mesh = build_mesh(spec)
            maximum = 0.0
            for i in range(48):
                exact = centerline(spec, (i + 0.5) / 48)
                chord = tuple((mesh.centers[i][axis] + mesh.centers[i + 1][axis]) / 2
                              for axis in range(3))
                maximum = max(maximum, length(tuple(exact[k] - chord[k] for k in range(3))))
            self.assertLess(maximum, 0.04, family)

    def test_invalid_ranges_unknown_visibility_fields_and_bad_families_are_rejected(self):
        base = {"name": "bad-input", "length": 3, "width": 0.3}
        bad = (
            ({**base, "length": 0}, "length"),
            ({**base, "width": 0}, "width"),
            ({**base, "tip_ratio": 0}, "tip_ratio"),
            ({**base, "twist": 13}, "twist"),
            ({**base, "family": "unknown"}, "family"),
            ({**base, "segments": 12.5}, "segments"),
            ({**base, "visible_ranges": [[0, 0.4]]}, "unknown"),
            ({**base, "family": "crossback", "bend": 0}, "crossback"),
            ({**base, "family": "crossback", "bend": 0.5, "depth": 0}, "2 \\* width"),
            ({**base, "family": "crossback", "bend": 0.5, "depth": 0.5}, "2 \\* width"),
            ({**base, "bend": float("nan")}, "finite"),
            ({**base, "front": "pink"}, "hex"),
        )
        for values, message in bad:
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, message):
                RibbonSpec.from_mapping(values)

    def test_named_svg_paths_are_deterministic_and_mesh_edges_are_not_art_lines(self):
        case = self.case_by_name["body-card"]
        camera = self.cameras[0]
        first = make_panel(case, camera)
        second = make_panel(case, camera)
        self.assertEqual(first, second)
        self.assertIn("body-card-front-card-support-card-fill", first)
        root = ET.fromstring(first)
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        paths = root.findall(".//svg:path", namespace)
        self.assertGreater(len(paths), 0)
        self.assertTrue(all("fill" in path.attrib and "stroke" not in path.attrib
                            for path in paths))
        self.assertTrue(all("-fill-" in path.attrib["id"] for path in paths))
        self.assertEqual(root.findall(".//svg:polygon", namespace), [])
        board = make_board(self.cases, self.cameras, True)
        self.assertEqual(board, make_board(self.cases, self.cameras, True))
        self.assertIn("Ribbon family", board)
        board_root = ET.fromstring(board)
        board_ids = [node.attrib["id"] for node in board_root.iter() if "id" in node.attrib]
        self.assertEqual(len(board_ids), len(set(board_ids)))
        unlabelled = ET.fromstring(make_board(self.cases, self.cameras, False))
        self.assertEqual(unlabelled.findall(".//svg:text", namespace), [])
        self.assertEqual(unlabelled.findall(".//svg:circle", namespace), [])

    def test_case_captions_wrap_without_losing_words(self):
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        for case in self.cases:
            root = ET.fromstring(make_panel(case, self.cameras[0]))
            purpose = root.find(f'.//svg:text[@id="{case["name"]}-front-purpose"]', namespace)
            self.assertIsNotNone(purpose)
            lines = [node.text or "" for node in purpose.findall("svg:tspan", namespace)]
            self.assertGreater(len(lines), 0)
            self.assertTrue(all(len(line) <= 52 for line in lines))
            self.assertEqual(" ".join(" ".join(lines).split()),
                             " ".join(case["purpose"].split()))

    def test_support_clip_panes_render_and_negative_depth_is_covered_by_card(self):
        case = self.case_by_name["body-card"]
        spec = RibbonSpec.from_mapping(case["ribbon"])
        bounds = tuple(case["support_card"]["bounds"])
        front_color = np.array([0xA4, 0x8A, 0xE6], dtype=np.uint8)
        back_color = np.array([0xBD, 0x88, 0x71], dtype=np.uint8)
        card_color = np.array([0x60, 0x6A, 0x52], dtype=np.uint8)

        def panel_transform(camera):
            pane_width, pane_height = 174, 300 - PANEL_ARTWORK_TOP - 8
            mesh = build_mesh(spec)
            faces = ribbon_faces(spec, camera, mesh) + card_faces(bounds, camera)
            points = [point for triangle, _color, _name in faces for point in triangle]
            min_x, max_x = min(point[0] for point in points), max(point[0] for point in points)
            min_y, max_y = min(point[1] for point in points), max(point[1] for point in points)
            scale = min((pane_width - 36) / (max_x - min_x),
                        (pane_height - 36) / (max_y - min_y))
            offset_x = (pane_width - scale * (min_x + max_x)) / 2
            offset_y = (pane_height + scale * (min_y + max_y)) / 2
            return scale, offset_x, offset_y

        def panel_position(camera, point, pane_x, transform):
            scale, offset_x, offset_y = transform
            q = project(point, camera)
            return pane_x + offset_x + scale * q[0], PANEL_ARTWORK_TOP + offset_y - scale * q[1]

        with tempfile.TemporaryDirectory(prefix="ribbon-card-render-") as directory:
            for camera in self.cameras:
                svg_path = Path(directory) / f"{camera.name}.svg"
                png_path = Path(directory) / f"{camera.name}.png"
                svg_path.write_text(make_panel(case, camera), encoding="utf-8")
                render(str(svg_path), str(png_path), size=(380, 300))
                image = cv2.imread(str(png_path), cv2.IMREAD_COLOR)
                self.assertIsNotNone(image)
                self.assertEqual(image.shape[:2], (300, 380))
                left = image[PANEL_ARTWORK_TOP + 4:292, 12:186]
                right = image[PANEL_ARTWORK_TOP + 4:292, 194:368]
                self.assertGreater(np.count_nonzero(np.all(left == front_color, axis=2)
                                                    | np.all(left == back_color, axis=2)), 0)
                self.assertGreater(np.count_nonzero(np.all(right == card_color, axis=2)), 0)
                ribbon_pixels = np.all(right == front_color, axis=2) | np.all(right == back_color, axis=2)
                stripe_bgrs = (np.array([0x39, 0x26, 0x47]), np.array([0xB8, 0xF1, 0xFF]))
                stripe_pixels = np.logical_or.reduce([np.all(right == color, axis=2)
                                                       for color in stripe_bgrs])
                self.assertGreater(np.count_nonzero(ribbon_pixels), 0)
                self.assertGreater(np.count_nonzero(stripe_pixels), 0)
                if camera.name == "front":
                    left, bottom, right_bound, top = bounds
                    inset = 0.05
                    mesh = build_mesh(spec)
                    artwork = ribbon_artwork_triangles(spec, camera, mesh)
                    transform = panel_transform(camera)
                    far_candidates = []
                    for face in artwork:
                        if face.fill not in {FRONT_STRIPE_COLOR, BACK_STRIPE_COLOR}:
                            continue
                        screen_triangle = [panel_position(camera, point, 12, transform)
                                           for point in face.points]
                        xs, ys = zip(*screen_triangle)
                        for pixel_y in range(max(PANEL_ARTWORK_TOP, math.ceil(min(ys) - 0.5)),
                                             min(292, math.floor(max(ys) - 0.5) + 1)):
                            for pixel_x in range(max(12, math.ceil(min(xs) - 0.5)),
                                                 min(186, math.floor(max(xs) - 0.5) + 1)):
                                sample = (pixel_x + 0.5, pixel_y + 0.5)
                                a, b, c = screen_triangle
                                determinant = ((b[0] - a[0]) * (c[1] - a[1])
                                               - (b[1] - a[1]) * (c[0] - a[0]))
                                if abs(determinant) < 1e-8:
                                    continue
                                wb = ((sample[0] - a[0]) * (c[1] - a[1])
                                      - (sample[1] - a[1]) * (c[0] - a[0])) / determinant
                                wc = ((b[0] - a[0]) * (sample[1] - a[1])
                                      - (b[1] - a[1]) * (sample[0] - a[0])) / determinant
                                weights = (1 - wb - wc, wb, wc)
                                if min(weights) < 0.08:
                                    continue
                                point = tuple(sum(weights[i] * face.points[i][axis]
                                                  for i in range(3)) for axis in range(3))
                                if not (point[2] < -0.1 and left + inset < point[0] < right_bound - inset
                                        and bottom + inset < point[1] < top - inset):
                                    continue
                                expected_fill = np.array([int(face.fill[i:i + 2], 16)
                                                          for i in (5, 3, 1)], dtype=np.uint8)
                                full_pixel = image[pixel_y, pixel_x]
                                covered_pixel = image[pixel_y, pixel_x + 182]
                                if (np.array_equal(full_pixel, expected_fill)
                                        and np.array_equal(covered_pixel, card_color)):
                                    far_candidates.append((point, face.uv, expected_fill))
                    self.assertTrue(far_candidates)
                    far_point, far_uv, expected_fill = min(far_candidates,
                                                          key=lambda candidate: candidate[0][2])
                    far_left_xy = panel_position(camera, far_point, 12, transform)
                    far_right_xy = panel_position(camera, far_point, 194, transform)
                    left_pixel = image[math.floor(far_left_xy[1]), math.floor(far_left_xy[0])]
                    right_pixel = image[math.floor(far_right_xy[1]), math.floor(far_right_xy[0])]
                    self.assertEqual(int(far_right_xy[0] - far_left_xy[0]), 182, far_uv)
                    self.assertAlmostEqual(far_right_xy[1], far_left_xy[1], places=9)
                    self.assertTrue(np.array_equal(left_pixel, expected_fill), (far_uv, left_pixel))
                    self.assertTrue(np.array_equal(right_pixel, card_color), (far_uv, right_pixel))

    def test_case_loader_rejects_duplicate_or_malformed_camera_lists(self):
        with CASES_PATH.open(encoding="utf-8") as source:
            data = json.load(source)
        invalid_cases = []
        duplicate = json.loads(json.dumps(data))
        duplicate["cameras"][1]["name"] = duplicate["cameras"][0]["name"]
        invalid_cases.append((duplicate, "camera names must be unique"))
        invalid_cases.append(({**data, "cameras": "front,oblique"}, "cameras must be a list"))
        invalid_cases.append(({**data, "cameras": [None, data["cameras"][1]]},
                              "camera 1 must contain"))
        invalid_cases.append(({**data, "cameras": [{"name": "front"}, data["cameras"][1]]},
                              "camera 1 must contain"))
        invalid_cases.append(({**data, "cameras": [{"name": None, "yaw": 0, "pitch": 0},
                                                       data["cameras"][1]]},
                              "camera 1 name must be text"))
        unsafe_names = json.loads(json.dumps(data))
        unsafe_names["cases"][0]["name"] = "case!"
        unsafe_names["cases"][1]["name"] = "case?"
        invalid_cases.append((unsafe_names, "case names must be 1-48 filename-safe"))
        with tempfile.TemporaryDirectory(prefix="ribbon-invalid-cases-") as directory:
            path = Path(directory) / "cases.json"
            for invalid, message in invalid_cases:
                path.write_text(json.dumps(invalid), encoding="utf-8")
                with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                    load_case_file(path)
            path.write_text(json.dumps(duplicate), encoding="utf-8")
            output_dir = Path(directory) / "should-not-exist"
            with self.assertRaisesRegex(ValueError, "camera names must be unique"):
                render_board(path, output_dir, render_png=False)
            self.assertFalse(output_dir.exists())
            path.write_text(json.dumps(unsafe_names), encoding="utf-8")
            unsafe_output = Path(directory) / "unsafe-case-names"
            with self.assertRaisesRegex(ValueError, "case names must be 1-48 filename-safe"):
                render_board(path, unsafe_output, render_png=False)
            self.assertFalse(unsafe_output.exists())

    def test_single_pane_clip_keeps_tall_art_visible_above_old_double_offset(self):
        camera = self.cameras[0]
        front_color = np.array([0xA4, 0x8A, 0xE6], dtype=np.uint8)
        back_color = np.array([0xBD, 0x88, 0x71], dtype=np.uint8)
        ribbon = {"name": "clip-test", "length": 0.25, "width": 0.03,
                  "bend": 0.375, "depth": 0, "family": "arch", "segments": 48}
        case = {"number": 1, "name": "clip-test", "purpose": "single-pane clip regression",
                "ribbon": ribbon}
        with tempfile.TemporaryDirectory(prefix="ribbon-single-pane-") as directory:
            svg_path = Path(directory) / "single.svg"
            png_path = Path(directory) / "single.png"
            svg_path.write_text(make_panel(case, camera), encoding="utf-8")
            render(str(svg_path), str(png_path), size=(380, 300))
            image = cv2.imread(str(png_path), cv2.IMREAD_COLOR)
        self.assertIsNotNone(image)
        top_of_view = image[PANEL_ARTWORK_TOP + 4:PANEL_ARTWORK_TOP + 36, :, :]
        visible = (np.all(top_of_view == front_color, axis=2)
                   | np.all(top_of_view == back_color, axis=2)
                   | np.all(top_of_view == np.array([0x39, 0x26, 0x47]), axis=2)
                   | np.all(top_of_view == np.array([0xB8, 0xF1, 0xFF]), axis=2))
        self.assertGreater(np.count_nonzero(visible), 0)

    def test_frozen_cases_hold_the_promised_single_parameter_variations_and_cameras(self):
        base = self.case_by_name["teaching-arch"]["ribbon"]
        bend = self.case_by_name["bend-only"]["ribbon"]
        taper = self.case_by_name["tapered-tip"]["ribbon"]
        twist = self.case_by_name["twisted-two-sided"]["ribbon"]
        for key in base:
            if key not in {"name", "bend"}:
                self.assertEqual(base[key], bend[key])
        for key in base:
            if key not in {"name", "tip_ratio"}:
                self.assertEqual(base[key], taper[key])
        for key in base:
            if key not in {"name", "twist"}:
                self.assertEqual(base[key], twist[key])
        self.assertEqual([(camera.name, camera.yaw, camera.pitch) for camera in self.cameras],
                         [("front", 0.0, 0.0), ("oblique", 38.0, 22.0)])
        body_case = self.case_by_name["body-card"]
        self.assertIn("support_card", body_case)
        self.assertEqual(body_case["ribbon"]["name"], "body-card")


if __name__ == "__main__":
    unittest.main()
