"""Contract tests for the bounded continuous center-route return-bend support."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from ribbon_return import (MAX_KERNEL_FACES, OrthographicCamera, ReturnSpec, build_return_mesh,
                           card_triangles, material_width, panel_svg, projected_width,
                           return_art_faces)
from vector_visibility import visible_fragments

POSITIVE = OrthographicCamera("positive-D-plus", (1.0, 0.0, 0.0),
                               (0.0, math.sin(math.radians(10)), -math.cos(math.radians(10))),
                               (0.0, math.cos(math.radians(10)), math.sin(math.radians(10))))
NEGATIVE = OrthographicCamera("negative-D-minus", (1.0, 0.0, 0.0), (0.0, 0.0, -1.0),
                               (0.0, 1.0, 0.0))


def fixture(alpha=math.pi, name="return-fixture", **overrides):
    values = {"length": 3.0, "width": 0.36, "tip_ratio": 1.0}
    values.update(overrides)
    return ReturnSpec(name, (0, 0, 0), (1, 0, 0), (0, 0, 1),
                      values["length"], values["width"], values["tip_ratio"], alpha)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1]))) / 2


def solve3(matrix, rhs):
    """Small pivoted elimination independent of the closed-form barycentric equations."""
    augmented = [list(row) + [value] for row, value in zip(matrix, rhs)]
    for column in range(3):
        pivot = max(range(column, 3), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= 1e-14:
            raise ValueError("singular barycentric system")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(3):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [a - factor * b for a, b in zip(augmented[row], augmented[column])]
    return tuple(augmented[row][3] for row in range(3))


def faulty_old_y_barycentric(point, triangle):
    """Regression reproduction of the superseded y-y0 term; never used by the oracle."""
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = triangle
    denominator = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(denominator) <= 1e-14:
        return None
    x, y = point
    a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / denominator
    b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y0)) / denominator
    return a, b, 1.0 - a - b


def projected_source_faces(mesh, camera):
    rows = {face.source_index: face for face in mesh.faces}
    faces = []
    signs = {}
    root_ids = set()
    for face in mesh.faces:
        normal = cross(sub(face.points[1], face.points[0]), sub(face.points[2], face.points[0]))
        facing = dot(normal, camera.toward_viewer)
        sign = 1 if facing > 1e-12 else (-1 if facing < -1e-12 else 0)
        signs[face.source_index] = sign
        if face.u_cell == 0:
            root_ids.add(face.source_index)
        projected = [(dot(point, camera.right), dot(point, camera.up),
                      dot(point, camera.toward_viewer)) for point in face.points]
        faces.append((projected, f"side:{sign}", face.source_index))
    return faces, signs, root_ids


def barycentric(x, y, tri):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = tri
    denominator = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(denominator) <= 1e-14:
        return None
    a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / denominator
    b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / denominator
    return a, b, 1.0 - a - b


def independent_depth_oracle(faces, signs, root_ids, step=0.0125):
    """Independent barycentric nearest-depth check; does not call the clipping kernel."""
    boxes = [(min(p[0] for p in tri), min(p[1] for p in tri),
              max(p[0] for p in tri), max(p[1] for p in tri), fid, tri)
             for tri, _color, fid in faces]
    xmin, ymin = min(box[0] for box in boxes), min(box[1] for box in boxes)
    xmax, ymax = max(box[2] for box in boxes), max(box[3] for box in boxes)
    nx, ny = math.ceil((xmax - xmin) / step), math.ceil((ymax - ymin) / step)
    winners = {"-1": 0, "1": 0, "0": 0}
    root = mixed = samples = 0
    for iy in range(ny):
        y = ymin + (iy + 0.619) * step
        for ix in range(nx):
            x = xmin + (ix + 0.371) * step
            hits = []
            for bx0, by0, bx1, by1, fid, tri in boxes:
                if x < bx0 or x > bx1 or y < by0 or y > by1:
                    continue
                weights = barycentric(x, y, tri)
                if weights is None or min(weights) < 1e-10:
                    continue
                depth = sum(weights[k] * tri[k][2] for k in range(3))
                hits.append((depth, fid))
            if not hits:
                continue
            samples += 1
            hit_signs = {signs[fid] for _depth, fid in hits}
            depths = [depth for depth, _fid in hits]
            if -1 in hit_signs and 1 in hit_signs and max(depths) - min(depths) > 1e-5:
                mixed += 1
            _depth, fid = max(hits, key=lambda hit: hit[0])
            winners[str(signs[fid])] += 1
            root += fid in root_ids
    return {"winners": winners, "root": root, "mixed": mixed, "samples": samples}


def kernel_area_by_sign(faces, signs, root_ids):
    result = {"-1": 0.0, "1": 0.0, "0": 0.0}
    root_area = 0.0
    for polygon, _color, fid in visible_fragments(faces):
        result[str(signs[fid])] += area(polygon)
        if fid in root_ids:
            root_area += area(polygon)
    return result, root_area


def centerline_self_intersection(mesh):
    root, ex, _w = mesh.spec.validate()
    ed = mesh.bend_direction
    centers = [tuple((row[0][axis] + row[-1][axis]) / 2 for axis in range(3))
               for row in mesh.rows]
    uv = [(dot(sub(point, root), ex), dot(sub(point, root), ed)) for point in centers]
    for first in range(len(uv) - 1):
        for second in range(first + 2, len(uv) - 1):
            a, b = uv[first], uv[first + 1]
            c, d = uv[second], uv[second + 1]
            ab, cd = (b[0] - a[0], b[1] - a[1]), (d[0] - c[0], d[1] - c[1])
            denominator = ab[0] * cd[1] - ab[1] * cd[0]
            if abs(denominator) <= 1e-12:
                continue
            delta = (c[0] - a[0], c[1] - a[1])
            t = (delta[0] * cd[1] - delta[1] * cd[0]) / denominator
            u = (delta[0] * ab[1] - delta[1] * ab[0]) / denominator
            if 1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9:
                return (first, second)
    return None


def segment_hits_triangle(start, end, tri, eps=1e-10):
    edge_a, edge_b = sub(tri[1], tri[0]), sub(tri[2], tri[0])
    direction = sub(end, start)
    pvec = cross(direction, edge_b)
    determinant = dot(edge_a, pvec)
    if abs(determinant) <= eps:
        return False
    inverse = 1 / determinant
    tvec = sub(start, tri[0])
    b1 = dot(tvec, pvec) * inverse
    qvec = cross(tvec, edge_a)
    b2 = dot(direction, qvec) * inverse
    along = dot(edge_b, qvec) * inverse
    return (b1 > eps and b2 > eps and b1 + b2 < 1 - eps
            and eps < along < 1 - eps)


def sampled_mesh_self_intersection(mesh):
    if centerline_self_intersection(mesh) is not None:
        return True
    for first, a in enumerate(mesh.faces):
        for b in mesh.faces[first + 1:]:
            if abs(a.u_cell - b.u_cell) <= 1:
                continue
            for source, target in ((a, b), (b, a)):
                for edge in range(3):
                    if segment_hits_triangle(source.points[edge], source.points[(edge + 1) % 3],
                                             target.points):
                        return True
    return False


class ReturnMeshTests(unittest.TestCase):
    def test_fixture_is_continuous_connected_and_preserves_root_material_width(self):
        spec = fixture()
        mesh = build_return_mesh(spec, 16, 2)
        self.assertEqual(mesh.rows[0][1], spec.root)
        self.assertEqual(mesh.stations, tuple(i / 16 for i in range(17)))
        self.assertEqual(len(mesh.faces), 64)
        self.assertEqual(mesh.faces[0].uv[0], (0.0, -1.0))
        self.assertEqual(mesh.faces[-1].uv[1][0], 1.0)
        self.assertAlmostEqual(math.dist(mesh.rows[0][0], mesh.rows[0][-1]), 0.36)
        self.assertAlmostEqual(math.dist(mesh.rows[-1][0], mesh.rows[-1][-1]), 0.36)
        self.assertAlmostEqual(material_width(spec, 0.0), 0.36)
        self.assertAlmostEqual(material_width(spec, 1.0), 0.36)
        self.assertAlmostEqual(projected_width(spec, POSITIVE, 0.5),
                               0.36 * math.cos(math.radians(10)), places=12)
        self.assertNotEqual(material_width(spec, 0.5), projected_width(spec, POSITIVE, 0.5))
        for first, second in zip(mesh.rows, mesh.rows[1:]):
            self.assertTrue(all(math.isfinite(value) for point in first + second for value in point))
            self.assertTrue(all(math.dist(a, b) > 0 for a, b in zip(first, second)))
        edges = {}
        for face in mesh.faces:
            for a, b in ((face.points[0], face.points[1]), (face.points[1], face.points[2]),
                         (face.points[2], face.points[0])):
                edges.setdefault(tuple(sorted((a, b))), []).append(face.source_index)
        neighbors = {face.source_index: set() for face in mesh.faces}
        for owners in edges.values():
            for owner in owners:
                neighbors[owner].update(owners)
        reached, pending = set(), [0]
        while pending:
            current = pending.pop()
            if current in reached:
                continue
            reached.add(current)
            pending.extend(neighbors[current] - reached)
        self.assertEqual(len(reached), len(mesh.faces))

    def test_analytic_jacobian_is_bounded_and_primary_midpoint_is_edge_on(self):
        minimum = ReturnSpec("minimum-domain", (0, 0, 0), (1, 0, 0), (0, 0, 1),
                             1.0, 0.1, 0.5, math.pi)
        self.assertAlmostEqual(1.0 * material_width(minimum, 1.0) / 2.0, 0.025)
        spec = fixture()
        tangent_mid = (math.cos(math.pi / 2), math.sin(math.pi / 2), 0.0)
        normal_mid = cross(tangent_mid, (0.0, 0.0, 1.0))
        self.assertAlmostEqual(dot(normal_mid, POSITIVE.toward_viewer), 0.0, delta=1e-12)
        self.assertAlmostEqual(math.sqrt(sum(value * value for value in normal_mid)), 1.0)
        self.assertGreater(spec.length * material_width(spec, 1.0) / 2.0, 0.025)

    def test_frozen_return_variations_have_no_sampled_surface_self_intersection(self):
        for alpha in (math.pi, 2 * math.pi / 3, 0.0):
            mesh = build_return_mesh(fixture(alpha=alpha), 16, 2)
            self.assertFalse(sampled_mesh_self_intersection(mesh), f"alpha={alpha}")

    def test_constructor_normalizes_and_checks_frame_domain_sampling_and_finite_bounds(self):
        spec = ReturnSpec("scaled-frame", (1, -2, 3), (2, 0, 0), (0, 0, 4), 1, 0.1, 0.5, 0)
        mesh = build_return_mesh(spec, 16, 2)
        self.assertEqual(mesh.rows[0][1], (1.0, -2.0, 3.0))
        cases = [
            (ReturnSpec("bad", (0, 0, 0), (1, 0, 0), (1, 0, 1), 3, .36, 1, math.pi), 16, 2),
            (fixture(), 15, 2), (fixture(), 16, 1), (fixture(), 33, 2),
            (fixture(), 32, 5), (fixture(length=3.01), 16, 2),
            (fixture(width=0), 16, 2), (fixture(alpha=math.pi + 1e-8), 16, 2),
            (ReturnSpec("bad", (11, 0, 0), (1, 0, 0), (0, 0, 1), 3, .36, 1, 0), 16, 2),
            (ReturnSpec("bad", (0, 0, 0), (0, 0, 0), (0, 0, 1), 3, .36, 1, 0), 16, 2),
        ]
        for bad_spec, u_count, v_count in cases:
            with self.subTest(spec=bad_spec, u=u_count, v=v_count), self.assertRaises(ValueError):
                build_return_mesh(bad_spec, u_count, v_count)
        with self.assertRaises(ValueError):
            build_return_mesh(fixture(), True, 2)
        self.assertEqual(len(build_return_mesh(fixture(), 32, 4).faces), MAX_KERNEL_FACES)

    def test_positive_fixture_has_two_actual_depth_visible_sides_before_render(self):
        mesh = build_return_mesh(fixture(), 16, 2)
        faces, signs, roots = projected_source_faces(mesh, POSITIVE)
        clipped, root_area = kernel_area_by_sign(faces, signs, roots)
        oracle = independent_depth_oracle(faces, signs, roots)
        self.assertGreater(clipped["-1"], 0.0)
        self.assertGreater(clipped["1"], 0.0)
        self.assertGreater(oracle["winners"]["-1"], 0)
        self.assertGreater(oracle["winners"]["1"], 0)
        self.assertGreater(oracle["mixed"], 0)
        self.assertGreater(root_area, 0.0)
        self.assertGreater(oracle["root"], 0)

    def test_exact_symmetric_negative_keeps_hidden_side_and_kernel_residual_separate(self):
        mesh = build_return_mesh(fixture(), 16, 2)
        faces, signs, roots = projected_source_faces(mesh, NEGATIVE)
        clipped, _root_area = kernel_area_by_sign(faces, signs, roots)
        oracle = independent_depth_oracle(faces, signs, roots)
        hidden_sign = min(oracle["winners"], key=oracle["winners"].get)
        self.assertEqual(oracle["winners"][hidden_sign], 0)
        self.assertEqual(oracle["winners"]["1"], 2581)
        self.assertGreaterEqual(clipped[hidden_sign], 0.0)
        self.assertLess(clipped[hidden_sign], 1e-5)

    def test_old_y_term_false_exclusion_regression_against_linear_solve_and_actual_depth(self):
        mesh = build_return_mesh(fixture(), 16, 2)
        by_id = {face.source_index: face for face in mesh.faces}
        screen_point = (0.1921375, -0.1722625)
        hidden_face, near_face = by_id[7], by_id[58]
        hit_depths = {}
        for face in (hidden_face, near_face):
            tri = [tuple((sum(p[i] * axis[i] for i in range(3))
                          for axis in (NEGATIVE.right, NEGATIVE.up, NEGATIVE.toward_viewer)))
                   for p in face.points]
            xy = tuple((point[0], point[1], 0.0) for point in tri)
            closed_form = barycentric(screen_point[0], screen_point[1], xy)
            linear = solve3([[tri[0][0], tri[1][0], tri[2][0]],
                             [tri[0][1], tri[1][1], tri[2][1]], [1.0, 1.0, 1.0]],
                            [screen_point[0], screen_point[1], 1.0])
            for actual, independent in zip(closed_form, linear):
                self.assertAlmostEqual(actual, independent, places=12)
            self.assertGreaterEqual(min(closed_form), 1e-10)
            hit_depths[face.source_index] = sum(closed_form[i] * tri[i][2] for i in range(3))
            if face.source_index == near_face.source_index:
                old = faulty_old_y_barycentric(screen_point, xy)
                self.assertIsNotNone(old)
                self.assertLess(min(old), -1e-10,
                                "the old y-y0 term must wrongly reject this true interior near-side hit")
        self.assertGreater(hit_depths[near_face.source_index],
                           hit_depths[hidden_face.source_index] + 1e-5)

    def test_card_is_a_root_attached_opaque_depth_occluder_and_stays_under_total_face_cap(self):
        spec = fixture()
        mesh = build_return_mesh(spec, 16, 2)
        art = return_art_faces(mesh, POSITIVE, with_card=True)
        self.assertLessEqual(len(art), MAX_KERNEL_FACES)
        self.assertEqual(len(card_triangles(spec)), 2)
        self.assertEqual(len(art), 162)
        self.assertTrue(all("root-attached-card" in component for _tri, _color, component in art
                            if component == "root-attached-card"))
        support = return_art_faces(mesh, POSITIVE, with_card=False)
        self.assertEqual(len(support), 160)
        self.assertLess(len(support), MAX_KERNEL_FACES)
        for camera in (POSITIVE, NEGATIVE):
            camera.validate()
        # A real card projection overlaps return geometry and wins a source-depth test in D+.
        card_world = card_triangles(spec)
        candidates = []
        tags = {}
        for index, face in enumerate(mesh.faces):
            normal = cross(sub(face.points[1], face.points[0]), sub(face.points[2], face.points[0]))
            sign = 1 if dot(normal, POSITIVE.toward_viewer) > 1e-12 else -1
            tri = [(dot(p, POSITIVE.right), dot(p, POSITIVE.up), dot(p, POSITIVE.toward_viewer))
                   for p in face.points]
            candidates.append((tri, f"ribbon:{sign}", index))
            tags[index] = "ribbon"
        for index, tri3 in enumerate(card_world):
            fid = len(mesh.faces) + index
            tri = [(dot(p, POSITIVE.right), dot(p, POSITIVE.up), dot(p, POSITIVE.toward_viewer))
                   for p in tri3]
            candidates.append((tri, "card", fid))
            tags[fid] = "card"
        oracle = independent_tagged_oracle(candidates, tags)
        self.assertGreater(oracle["overlap_samples"], 0)
        self.assertGreater(oracle["card_winners"], 0)

    def test_alpha_zero_is_a_straight_single_facing_negative_control(self):
        mesh = build_return_mesh(fixture(alpha=0), 16, 2)
        faces, signs, roots = projected_source_faces(mesh, POSITIVE)
        _clipped, _root_area = kernel_area_by_sign(faces, signs, roots)
        oracle = independent_depth_oracle(faces, signs, roots)
        self.assertEqual(oracle["winners"]["1"], 0)
        self.assertGreater(oracle["winners"]["-1"], 0)

    def test_svg_namespace_center_margin_nonblank_crop_and_two_process_determinism(self):
        spec = fixture()
        camera = POSITIVE
        svg = panel_svg(build_return_mesh(spec, 16, 2), camera)
        root = ET.fromstring(svg)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
        self.assertEqual(len(ids), len(set(ids)))
        path_values = [element.attrib["d"] for element in root.iter()
                       if element.tag.endswith("path")]
        point_values = [float(value) for path in path_values
                        for value in re.findall(r"(?<![A-Za-z])[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", path)]
        self.assertTrue(point_values)
        self.assertGreaterEqual(min(point_values), 20.0)
        self.assertLessEqual(max(point_values), 400.0)
        x_values, y_values = point_values[0::2], point_values[1::2]
        self.assertLess(abs((min(x_values) + max(x_values)) / 2 - 210.0), 30.0)
        self.assertLess(abs((min(y_values) + max(y_values)) / 2 - 160.0), 30.0)
        code = ("import hashlib,math; from ribbon_return import ReturnSpec,OrthographicCamera,build_return_mesh,panel_svg; "
                "s=ReturnSpec('return-fixture',(0,0,0),(1,0,0),(0,0,1),3,.36,1,math.pi); "
                "c=OrthographicCamera('positive-D-plus',(1,0,0),(0,math.sin(math.radians(10)),-math.cos(math.radians(10))),"
                "(0,math.cos(math.radians(10)),math.sin(math.radians(10)))); "
                "print(hashlib.sha256(panel_svg(build_return_mesh(s,16,2),c).encode()).hexdigest())")
        env = dict(__import__("os").environ)
        env["PYTHONPATH"] = str(SCRIPTS)
        hashes = [subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                                 check=True, capture_output=True, text=True, timeout=30).stdout.strip()
                  for _ in range(2)]
        self.assertEqual(hashes[0], hashes[1])
        with tempfile.TemporaryDirectory() as temp:
            svg_path, png_path = Path(temp) / "panel.svg", Path(temp) / "panel.png"
            svg_path.write_text(svg, encoding="utf-8")
            from draw import render
            render(str(svg_path), str(png_path))
            import cv2
            image = cv2.imread(str(png_path), cv2.IMREAD_COLOR)
            self.assertEqual(image.shape[:2], (320, 420))
            background = image[0, 0].astype(int)
            changed = __import__("numpy").any(image.astype(int) != background, axis=2)
            self.assertGreater(int(changed.sum()), 500)
            self.assertFalse(changed[0].any())
            self.assertFalse(changed[-1].any())
            self.assertFalse(changed[:, 0].any())
            self.assertFalse(changed[:, -1].any())

    def test_board_builder_unpacks_pair_side_and_panel_metadata_separately(self):
        build_path = ROOT / ".scratch/27-return-bend/work/build.py"
        plan_path = ROOT / ".scratch/27-return-bend/work/cases.json"
        if not build_path.exists() or not plan_path.exists():
            self.skipTest("the bounded board producer is not present")
        module_spec = importlib.util.spec_from_file_location("return_bend_build_test", build_path)
        producer = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(producer)
        cases = json.loads(plan_path.read_text(encoding="utf-8"))
        original_root = producer.ROOT
        with tempfile.TemporaryDirectory() as temp:
            producer.ROOT = Path(temp)
            panels = {}
            for pair in cases["pairs"]:
                for side in ("before", "after"):
                    token = pair[side]["panel_token"]
                    filename = f"{token}.png"
                    (Path(temp) / filename).write_bytes(b"frozen-png-payload")
                    panels[token] = {"png": filename}
            try:
                blind = producer.board_svg(cases, panels, labelled=False)
                self.assertEqual(blind, producer.board_svg(cases, panels, labelled=False))
                labelled = producer.board_svg(cases, panels, labelled=True)
            finally:
                producer.ROOT = original_root
        blind_root = ET.fromstring(blind)
        labelled_root = ET.fromstring(labelled)
        ns = "{http://www.w3.org/2000/svg}"
        self.assertEqual(len(blind_root.findall(f".//{ns}image")), 10)
        self.assertEqual(len(labelled_root.findall(f".//{ns}image")), 10)
        self.assertEqual(labelled_root.attrib["viewBox"], "0 0 900 1870")
        self.assertEqual(blind_root.attrib["viewBox"], "0 0 900 1670")
        self.assertEqual(len(blind_root.findall(f".//{ns}text")), 0)
        self.assertGreater(len(labelled_root.findall(f".//{ns}text")), 10)

    def test_blind_report_routes_only_the_anonymous_board_not_raw_pair_order(self):
        build_path = ROOT / ".scratch/27-return-bend/work/build.py"
        plan_path = ROOT / ".scratch/27-return-bend/work/cases.json"
        producer_spec = importlib.util.spec_from_file_location("return_bend_report_test", build_path)
        producer = importlib.util.module_from_spec(producer_spec)
        producer_spec.loader.exec_module(producer)
        cases = json.loads(plan_path.read_text(encoding="utf-8"))
        board_path = ".scratch/27-return-bend/evidence/boards/comparison-unlabelled.png"
        payload = producer.review_report_payload(
            cases, {"unlabelled": {"png": board_path}, "labelled": {"png": "excluded.png"}})
        self.assertEqual(payload, board_path + "\n\n" + cases["blind_board"]["review_question"] + "\n")
        image_lines = [line for line in payload.splitlines() if line.endswith(".png")]
        self.assertEqual(image_lines, [board_path])
        self.assertNotIn("panel-", payload)
        self.assertNotIn("pair-", payload)
        self.assertNotIn("before", payload)
        self.assertNotIn("after", payload)
        self.assertNotIn("expected", payload.lower())

    def test_art_subdivisions_are_local_uv_and_total_opacity_faces_are_capped(self):
        mesh = build_return_mesh(fixture(), 16, 2)
        for camera in (POSITIVE, NEGATIVE):
            faces = return_art_faces(mesh, camera, with_card=True)
            self.assertTrue(faces)
            self.assertLessEqual(len(faces), MAX_KERNEL_FACES)
            self.assertTrue(all(len(triangle) == 3 for triangle, _color, _component in faces))
        with self.assertRaises(ValueError):
            return_art_faces(build_return_mesh(fixture(), 32, 4), POSITIVE, with_card=True)


def independent_tagged_oracle(faces, tags, step=0.0125):
    boxes = [(min(p[0] for p in tri), min(p[1] for p in tri), max(p[0] for p in tri),
              max(p[1] for p in tri), fid, tri) for tri, _color, fid in faces]
    xmin, ymin = min(box[0] for box in boxes), min(box[1] for box in boxes)
    xmax, ymax = max(box[2] for box in boxes), max(box[3] for box in boxes)
    nx, ny = math.ceil((xmax - xmin) / step), math.ceil((ymax - ymin) / step)
    winners = {"card": 0, "ribbon": 0}
    overlaps = 0
    for iy in range(ny):
        y = ymin + (iy + 0.619) * step
        for ix in range(nx):
            x = xmin + (ix + 0.371) * step
            hits = []
            for x0, y0, x1, y1, fid, tri in boxes:
                if x < x0 or x > x1 or y < y0 or y > y1:
                    continue
                weights = barycentric(x, y, tri)
                if weights is None or min(weights) < 1e-10:
                    continue
                hits.append((sum(weights[k] * tri[k][2] for k in range(3)), fid))
            kinds = {tags[fid] for _depth, fid in hits}
            if "card" in kinds and "ribbon" in kinds:
                overlaps += 1
            if hits:
                _depth, fid = max(hits, key=lambda hit: hit[0])
                winners[tags[fid]] += 1
    return {"overlap_samples": overlaps, "card_winners": winners["card"],
            "ribbon_winners": winners["ribbon"]}


if __name__ == "__main__":
    unittest.main()
