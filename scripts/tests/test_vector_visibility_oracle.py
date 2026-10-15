"""Runnable scratch form of the proposed raw-triangle coverage/source-partition gate."""
import ast
import hashlib
import inspect
import json
import math
import sys
import unittest

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPTS))

from scripts.tests.test_vector_visibility import ring_and_occluder
from vector_visibility import EPS, subtract_convex, visible_fragments

EDGE_DISTANCE = 1e-12
BARY_EDGE = 1e-10
ORACLE_TIE = 1e-10
AREA_FLOOR = 1e-18


def _source_declaration_bias():
    """Read the declaration-order bias from the resolver used by this proposed test."""
    tree = ast.parse(inspect.getsource(visible_fragments))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not any(
                isinstance(target, ast.Name) and target.id == "bias" for target in node.targets):
            continue
        value = node.value
        branches = (value.body, value.orelse) if isinstance(value, ast.IfExp) else (value,)
        numbers = []
        for branch in branches:
            if isinstance(branch, ast.Constant) and isinstance(branch.value, (float, int)):
                numbers.append(float(branch.value))
            elif (isinstance(branch, ast.UnaryOp) and isinstance(branch.op, ast.USub)
                  and isinstance(branch.operand, ast.Constant)
                  and isinstance(branch.operand.value, (float, int))):
                numbers.append(-float(branch.operand.value))
        if numbers:
            return max(abs(number) for number in numbers)
    raise AssertionError("resolver declaration bias could not be read from source")


DECLARATION_BIAS = _source_declaration_bias()
NEAR_POLICY_BAND = DECLARATION_BIAS + EPS


def _area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1])) / 2)


def _point_segment_boundary(poly, xx, yy):
    boundary = np.zeros(xx.shape, dtype=bool)
    tol2 = EDGE_DISTANCE * EDGE_DISTANCE
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ax, ay = a[:2]
        bx, by = b[:2]
        dx, dy = bx - ax, by - ay
        length2 = dx * dx + dy * dy
        if length2 == 0:
            continue
        t = ((xx - ax) * dx + (yy - ay) * dy) / length2
        # Endpoint selection is only for Euclidean distance-to-segment membership.
        qx = np.where(t <= 0, ax, np.where(t >= 1, bx, ax + t * dx))
        qy = np.where(t <= 0, ay, np.where(t >= 1, by, ay + t * dy))
        boundary |= (xx - qx) ** 2 + (yy - qy) ** 2 <= tol2
    return boundary


def _point_in_polygon(poly, xx, yy):
    inside = np.zeros(xx.shape, dtype=bool)
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ax, ay = a[:2]
        bx, by = b[:2]
        if ay != by:
            crosses = (ay > yy) != (by > yy)
            inside ^= crosses & (xx < ax + (yy - ay) * (bx - ax) / (by - ay))
    return inside


def _barycentric(tri, x, y):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = tri
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    wb = ((x - x0) * (y2 - y0) - (y - y0) * (x2 - x0)) / det
    wc = ((x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)) / det
    return 1 - wb - wc, wb, wc


def _source_depth_masks(faces, xs, ys):
    shape = (len(ys), len(xs))
    tops = {name: np.full(shape, -np.inf) for name in ("strip", "body")}
    seconds = {name: np.full(shape, -np.inf) for name in ("strip", "body")}
    hits = {name: np.zeros(shape, dtype=np.uint16) for name in ("strip", "body")}
    source_edge = np.zeros(shape, dtype=bool)
    for tri, _color, component in faces:
        p = np.asarray(tri, dtype=float)
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = p
        det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if det == 0:
            continue
        ix0 = int(np.searchsorted(xs, p[:, 0].min(), side="left"))
        ix1 = int(np.searchsorted(xs, p[:, 0].max(), side="right"))
        iy0 = int(np.searchsorted(ys, p[:, 1].min(), side="left"))
        iy1 = int(np.searchsorted(ys, p[:, 1].max(), side="right"))
        if ix0 >= ix1 or iy0 >= iy1:
            continue
        region = np.s_[iy0:iy1, ix0:ix1]
        xx, yy = np.meshgrid(xs[ix0:ix1], ys[iy0:iy1])
        wb = ((xx - x0) * (y2 - y0) - (yy - y0) * (x2 - x0)) / det
        wc = ((x1 - x0) * (yy - y0) - (y1 - y0) * (xx - x0)) / det
        wa = 1 - wb - wc
        inside = (wa >= -1e-12) & (wb >= -1e-12) & (wc >= -1e-12)
        source_edge[region] |= inside & (np.minimum.reduce(
            (np.abs(wa), np.abs(wb), np.abs(wc))) <= BARY_EDGE)
        depth = wa * z0 + wb * z1 + wc * z2
        top, second, layer_hits = tops[component][region], seconds[component][region], hits[component][region]
        old = top.copy()
        new_second = np.maximum(second, np.minimum(old, depth))
        new_top = np.maximum(old, depth)
        top[inside] = new_top[inside]
        second[inside] = new_second[inside]
        layer_hits[inside] += 1
    strip, body = tops["strip"], tops["body"]
    strip_covered, body_covered = np.isfinite(strip), np.isfinite(body)
    both = strip_covered & body_covered
    delta = np.zeros(shape)
    delta[both] = strip[both] - body[both]
    exact_tie = both & (np.abs(delta) <= ORACLE_TIE)
    cross_near = both & (np.abs(delta) <= NEAR_POLICY_BAND)
    strip_near = strip_covered & np.isfinite(seconds["strip"])
    body_near = body_covered & np.isfinite(seconds["body"])
    strip_gap = np.zeros(shape)
    body_gap = np.zeros(shape)
    strip_gap[strip_near] = strip[strip_near] - seconds["strip"][strip_near]
    body_gap[body_near] = body[body_near] - seconds["body"][body_near]
    strip_near &= strip_gap <= NEAR_POLICY_BAND
    body_near &= body_gap <= NEAR_POLICY_BAND
    policy = source_edge | exact_tie | cross_near | strip_near | body_near
    visible = strip_covered & (~body_covered | (strip > body + ORACLE_TIE))
    return {"visible": visible, "policy": policy, "source_edge": source_edge,
            "exact_tie": exact_tie, "cross_near": cross_near,
            "strip_self_near": strip_near, "body_self_near": body_near,
            "strip_hits": hits["strip"], "body_hits": hits["body"]}


def _grid_bounds(faces, n, phase):
    strip = [tri for tri, _color, name in faces if name == "strip"]
    lo_x = min(p[0] for tri in strip for p in tri)
    hi_x = max(p[0] for tri in strip for p in tri)
    lo_y = min(p[1] for tri in strip for p in tri)
    hi_y = max(p[1] for tri in strip for p in tri)
    xs = lo_x + (np.arange(n) + phase) * ((hi_x - lo_x) / n)
    ys = lo_y + (np.arange(n) + phase) * ((hi_y - lo_y) / n)
    return xs, ys


def _fragment_union(faces, xs, ys):
    interior = np.zeros((len(ys), len(xs)), dtype=bool)
    boundary = np.zeros_like(interior)
    tagged = [(tri, color, (component, index))
              for index, (tri, color, component) in enumerate(faces)]
    fragments = list(visible_fragments(tagged))
    for poly, _color, tag in fragments:
        if tag[0] != "strip" or len(poly) < 3 or _area(poly) <= AREA_FLOOR:
            continue
        coords = np.asarray(poly, dtype=float)
        ix0 = int(np.searchsorted(xs, coords[:, 0].min(), side="left"))
        ix1 = int(np.searchsorted(xs, coords[:, 0].max(), side="right"))
        iy0 = int(np.searchsorted(ys, coords[:, 1].min(), side="left"))
        iy1 = int(np.searchsorted(ys, coords[:, 1].max(), side="right"))
        if ix0 >= ix1 or iy0 >= iy1:
            continue
        xx, yy = np.meshgrid(xs[ix0:ix1], ys[iy0:iy1])
        edge = _point_segment_boundary(poly, xx, yy)
        inside = _point_in_polygon(poly, xx, yy)
        interior[iy0:iy1, ix0:ix1] |= inside & ~edge
        boundary[iy0:iy1, ix0:ix1] |= edge
    return interior, boundary, fragments


def _partition_intersection(subject, cutter):
    output = list(subject)
    orientation = 1 if sum(a[0] * b[1] - b[0] * a[1]
                           for a, b in zip(cutter, cutter[1:] + cutter[:1])) > 0 else -1
    for a, b in zip(cutter, cutter[1:] + cutter[:1]):
        if not output:
            return []
        def side(p):
            return orientation * ((b[0] - a[0]) * (p[1] - a[1])
                                  - (b[1] - a[1]) * (p[0] - a[0]))
        clipped = []
        for first, second in zip(output, output[1:] + output[:1]):
            f0, f1 = side(first), side(second)
            if (f0 >= 0) != (f1 >= 0):
                t = f0 / (f0 - f1)
                clipped.append(tuple(first[k] + t * (second[k] - first[k])
                                     for k in range(3)))
            if f1 >= 0:
                clipped.append(second)
        output = clipped
    return output


def _convex_partition_properties(subject, cutter, pieces):
    expected_cut = _area(_partition_intersection(subject, cutter))
    expected = _area(subject) - expected_cut
    positive = [piece for piece in pieces if _area(piece) > 0]
    tolerance = 1e-10 * max(1, _area(subject))
    self_errors = []
    for piece in positive:
        for point in piece:
            if not all(math.isfinite(value) for value in point):
                self_errors.append("nonfinite")
    overlaps = []
    for i, piece in enumerate(positive):
        for other in positive[i + 1:]:
            overlap = _area(_partition_intersection(piece, other))
            if overlap > tolerance:
                overlaps.append(overlap)
    return {"expected_remaining_area": expected,
            "output_area": sum(_area(piece) for piece in positive),
            "declared_area_error": tolerance,
            "area_error": sum(_area(piece) for piece in positive) - expected,
            "positive_piece_overlaps": overlaps,
            "nonfinite": self_errors}


def _old_cross_dot_boundary(a, b, point):
    ax, ay = a
    bx, by = b
    x, y = point
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    cross = (x - ax) * dy - (y - ay) * dx
    dot = (x - ax) * dx + (y - ay) * dy
    return (abs(cross) <= 1e-12 * max(1.0, length)
            and dot >= -1e-12 and dot <= dx * dx + dy * dy + 1e-12)


class VisibilityOracleGateTests(unittest.TestCase):
    def test_derived_fine_plan_binds_current_kernel_without_rewriting_history(self):
        plan_path = ROOT / ".scratch/23-visibility-integration/work/cases-fine-current.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        source_path = ROOT / plan["producer"]["path"]
        self.assertEqual(plan["producer"]["sha256"],
                         hashlib.sha256(source_path.read_bytes()).hexdigest())
        self.assertNotEqual(plan["producer"]["sha256"],
                            plan["producer"]["historical_pre_integration_sha256"])
        historical_plan_path = ROOT / plan["derived_from"]["path"]
        historical_plan = json.loads(historical_plan_path.read_text(encoding="utf-8"))
        self.assertEqual(plan["derived_from"]["sha256"],
                         hashlib.sha256(historical_plan_path.read_bytes()).hexdigest())
        historical_case = next(row for row in historical_plan["cases"]
                               if row["name"] == plan["derived_from"]["case_name"])
        frozen = plan["frozen_geometry"]
        self.assertEqual(frozen["ribbon"], historical_case["ribbon"])
        self.assertEqual(frozen["camera"], historical_case["camera"])
        self.assertEqual(frozen["support_camber"], .35)
        self.assertEqual(frozen["sampling"], {"u_intervals": 96, "v_intervals": 12})

    def test_raw_triangle_coverage_is_two_sided_outside_all_source_masks(self):
        for yaw in (0, 55):
            original = ring_and_occluder(yaw)
            faces = [([(x - 200, y - 150, z) for x, y, z in tri], color, name)
                     for tri, color, name in original]
            for n, phase in ((256, .5), (512, .5), (1024, .25), (1024, .75)):
                with self.subTest(yaw=yaw, n=n, phase=phase):
                    xs, ys = _grid_bounds(faces, n, phase)
                    oracle = _source_depth_masks(faces, xs, ys)
                    strict, fragment_edge, tagged = _fragment_union(faces, xs, ys)
                    usable = ~oracle["policy"] & ~fragment_edge
                    false_positive = strict & ~oracle["visible"] & usable
                    false_negative = ~strict & oracle["visible"] & usable
                    self.assertEqual(int(false_positive.sum()), 0)
                    self.assertEqual(int(false_negative.sum()), 0)
                    # Report every excluded category and both error directions on failure.
                    diagnostic = {"source_edges": int(oracle["source_edge"].sum()),
                                  "exact_ties": int(oracle["exact_tie"].sum()),
                                  "cross_near": int(oracle["cross_near"].sum()),
                                  "strip_self_near": int(oracle["strip_self_near"].sum()),
                                  "body_self_near": int(oracle["body_self_near"].sum()),
                                  "fragment_edges": int(fragment_edge.sum()),
                                  "false_positive": int(false_positive.sum()),
                                  "false_negative": int(false_negative.sum())}
                    self.assertFalse(np.any(false_positive | false_negative), diagnostic)

    def test_candidate_source_owners_remain_convex_source_subsets(self):
        for yaw in (0, 55):
            faces = [([(x - 200, y - 150, z) for x, y, z in tri], color, name)
                     for tri, color, name in ring_and_occluder(yaw)]
            tagged = [(tri, color, (name, index))
                      for index, (tri, color, name) in enumerate(faces)]
            for poly, _color, owner in visible_fragments(tagged):
                triangle = faces[owner[1]][0]
                for point in poly:
                    self.assertTrue(all(math.isfinite(value) for value in point))
                    self.assertGreaterEqual(min(_barycentric(triangle, point[0], point[1])), -1e-10)

    def test_tiny_segment_boundary_has_euclidean_negative_controls(self):
        for length in (1e-8, 1e-14):
            with self.subTest(edge_length=length):
                polygon = [(-1, 0, 0), (0, 0, 0), (length, 0, 0),
                           (1, 0, 0), (1, 1, 0), (-1, 1, 0)]
                points = ((length / 2, 1e-6), (length / 2, -1e-6),
                          (length / 2, 0), (0, 0), (length, 0), (-1e-6, 1e-6))
                classifications = []
                for point in points:
                    xx, yy = np.asarray([[point[0]]]), np.asarray([[point[1]]])
                    inside = _point_in_polygon(polygon, xx, yy)
                    boundary = _point_segment_boundary(polygon, xx, yy)
                    classifications.append((bool(inside[0, 0]), bool(boundary[0, 0])))
                self.assertEqual(classifications[0], (True, False))
                self.assertEqual(classifications[1], (False, False))
                self.assertTrue(all(classifications[index][1] for index in (2, 3, 4)))
                self.assertFalse(classifications[5][1])
                for point in points[:2] + points[5:]:
                    self.assertTrue(_old_cross_dot_boundary((0, 0), (length, 0), point))
                duplicate_edge = [(-1, 0, 0), (0, 0, 0), (0, 0, 0),
                                  (length, 0, 0), (1, 0, 0), (1, 1, 0), (-1, 1, 0)]
                np.testing.assert_array_equal(
                    _point_segment_boundary(duplicate_edge, np.asarray([[length / 2]]),
                                            np.asarray([[1e-6]])),
                    _point_segment_boundary(polygon, np.asarray([[length / 2]]),
                                            np.asarray([[1e-6]])))

    def test_boundary_distance_is_translation_and_winding_invariant(self):
        length = 1e-14
        polygon = [(-1, 0, 0), (0, 0, 0), (length, 0, 0),
                   (1, 0, 0), (1, 1, 0), (-1, 1, 0)]
        translated = [(x + 50, y - 20, z) for x, y, z in reversed(polygon)]
        for point in ((length / 2, 1e-6), (length / 2, -1e-6), (length / 2, 0),
                      (0, 0), (-1e-6, 0)):
            xx, yy = np.asarray([[point[0]]]), np.asarray([[point[1]]])
            original = (_point_in_polygon(polygon, xx, yy),
                        _point_segment_boundary(polygon, xx, yy))
            xx, yy = np.asarray([[point[0] + 50]]), np.asarray([[point[1] - 20]])
            moved = (_point_in_polygon(translated, xx, yy),
                     _point_segment_boundary(translated, xx, yy))
            np.testing.assert_array_equal(original[0], moved[0])
            np.testing.assert_array_equal(original[1], moved[1])

    def test_near_policy_band_is_derived_from_current_resolver_source(self):
        self.assertAlmostEqual(DECLARATION_BIAS, 1e-5, delta=1e-20)
        self.assertAlmostEqual(EPS, 1e-7, delta=1e-20)
        self.assertAlmostEqual(NEAR_POLICY_BAND, 1.01e-5, delta=1e-20)
        self.assertGreater(NEAR_POLICY_BAND, ORACLE_TIE)

    def test_convex_subtract_conserves_source_and_disjoint_intersection(self):
        subject = [(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0)]
        cutter = [(1, 1, 1), (3, 1, 1), (1, 3, 1)]
        pieces = [p for p in subtract_convex(subject, cutter) if _area(p) > 0]
        result = _convex_partition_properties(subject, cutter, pieces)
        self.assertLessEqual(abs(result["area_error"]), result["declared_area_error"])
        self.assertFalse(result["positive_piece_overlaps"])
        self.assertFalse(result["nonfinite"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
