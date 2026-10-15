"""Exact-partition and source-depth regressions for isolated candidate v3."""
import importlib.util
import math
import sys
import unittest
from pathlib import Path

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[2]
SCRIPTS = ROOT / "scripts"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


canonical = load("v3_control_canonical", SCRIPTS / "vector_visibility.py")
v1 = load("v3_control_v1", WORK / "vector_visibility_candidate_v1.py")
v2 = load("v3_control_v2", WORK / "vector_visibility_candidate_v2.py")
v3 = load("v3_candidate", WORK / "vector_visibility_candidate.py")


def signed_area(poly):
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(poly, poly[1:] + poly[:1])) / 2


def area(poly):
    return abs(signed_area(poly))


def barycentric(triangle, point):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = triangle
    x, y = point[:2]
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    wb = ((x - x0) * (y2 - y0) - (y - y0) * (x2 - x0)) / det
    wc = ((x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)) / det
    return 1 - wb - wc, wb, wc


def exact_convex_clip(subject, cutter):
    """Independent exact-sign polygon intersection for area expectations in tests."""
    clipper = list(cutter)
    orientation = 1 if signed_area(clipper) > 0 else -1
    output = list(subject)
    for a, b in zip(clipper, clipper[1:] + clipper[:1]):
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


def subset_of_square(poly, scale, tx, ty, tol=1e-11):
    return all(-tol <= (p[0] - tx) / scale <= 2 + tol
               and -tol <= (p[1] - ty) / scale <= 2 + tol for p in poly)


def pairwise_overlap_areas(polygons):
    overlaps = []
    for i, first in enumerate(polygons):
        if area(first) == 0:
            continue
        for j in range(i + 1, len(polygons)):
            if area(polygons[j]) == 0:
                continue
            intersection = exact_convex_clip(first, polygons[j])
            intersection_area = area(intersection) if len(intersection) >= 3 else 0.0
            overlaps.append((i, j, intersection_area))
    return overlaps


def scale_polygon(poly, scale, tx, ty):
    return [(tx + scale * p[0], ty + scale * p[1], p[2]) for p in poly]


def clip_witness(scale, keep_positive, reverse=False, module=v3):
    inside_x, outside_x = ((-.5 / scale, -1.5 / scale) if keep_positive
                           else (.5 / scale, 1.5 / scale))
    source = [(inside_x, 0, 0), (outside_x, 1, 0), (inside_x, 2, 0)]
    if reverse:
        source.reverse()
    fn = lambda p: scale * module.EPS * p[0]
    return source, module.line_clip(source, fn, keep_positive), fn


class VisibilityCandidateV3Tests(unittest.TestCase):
    def test_public_tolerance_clip_remains_source_bounded_and_v1_v2_fail(self):
        for scale in (.5, 1.0, 2.0):
            for keep_positive in (True, False):
                for reverse in (False, True):
                    with self.subTest(scale=scale, keep_positive=keep_positive, reverse=reverse):
                        source, clipped, fn = clip_witness(scale, keep_positive, reverse)
                        self.assertTrue(clipped)
                        v2_clipped = v2.line_clip(source, lambda p, s=scale: s * v2.EPS * p[0],
                                                  keep_positive)
                        self.assertEqual(clipped, v2_clipped)
                        self.assertTrue(all(math.isfinite(value) for p in clipped for value in p))
                        self.assertEqual(signed_area(source) > 0, signed_area(clipped) > 0)
                        for point in clipped:
                            self.assertGreaterEqual(min(barycentric(source, point)), -1e-12)
                            shifted = fn(point) + v3.EPS if keep_positive else fn(point) - v3.EPS
                            self.assertGreaterEqual(shifted, -1e-20) if keep_positive else self.assertLessEqual(shifted, 1e-20)
        source, _unused, _fn = clip_witness(1, True)
        for control in (canonical, v1):
            clipped = control.line_clip(source, lambda p: control.EPS * p[0], True)
            self.assertLess(min(min(barycentric(source, p)) for p in clipped), -1e-12)
        for control in (v2, v3):
            clipped = control.line_clip(source, lambda p: control.EPS * p[0], True)
            self.assertGreaterEqual(min(min(barycentric(source, p)) for p in clipped), -1e-12)

        on_positive = [(-1, 0, 0), (-2, 1, 0), (-1, 2, 0)]
        clipped_positive = v3.line_clip(on_positive, lambda p: v3.EPS * p[0], True)
        self.assertTrue(all(math.isfinite(value) for p in clipped_positive for value in p))
        self.assertGreaterEqual(min(min(barycentric(on_positive, p)) for p in clipped_positive), -1e-12)
        self.assertGreaterEqual(sum(abs(p[0] + 1) <= 1e-14 for p in clipped_positive), 2)
        on_negative = [(1, 0, 0), (2, 1, 0), (1, 2, 0)]
        clipped_negative = v3.line_clip(on_negative, lambda p: v3.EPS * p[0], False)
        self.assertTrue(all(math.isfinite(value) for p in clipped_negative for value in p))
        self.assertGreaterEqual(min(min(barycentric(on_negative, p)) for p in clipped_negative), -1e-12)
        self.assertGreaterEqual(sum(abs(p[0] - 1) <= 1e-14 for p in clipped_negative), 2)

    def test_subtract_convex_partitions_subject_with_transforms_and_winding(self):
        subject0 = [(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0)]
        cutter0 = [(1, 1, 1), (3, 1, 1), (1, 3, 1)]
        transforms = ((.25, 0, 0, False, False),
                      (1, 50, -20, True, False),
                      (2, -12, 35, False, True),
                      (8, 20, 40, True, True))
        for scale, tx, ty, reverse_subject, reverse_cutter in transforms:
            with self.subTest(scale=scale, tx=tx, ty=ty, reverse_subject=reverse_subject,
                              reverse_cutter=reverse_cutter):
                subject = scale_polygon(subject0, scale, tx, ty)
                cutter = scale_polygon(cutter0, scale, tx, ty)
                if reverse_subject:
                    subject.reverse()
                if reverse_cutter:
                    cutter.reverse()
                intersection = exact_convex_clip(subject, cutter)
                expected = area(subject) - area(intersection)
                fragments = v3.subtract_convex(subject, cutter)
                self.assertTrue(fragments)
                self.assertTrue(all(math.isfinite(value) for poly in fragments for p in poly for value in p))
                numeric_error = 1e-10 * max(1.0, area(subject))
                self.assertLessEqual(abs(sum(area(poly) for poly in fragments) - expected), numeric_error)
                self.assertTrue(all(subset_of_square(poly, scale, tx, ty) for poly in fragments))
                self.assertTrue(all(intersection_area <= numeric_error
                                    for _i, _j, intersection_area in pairwise_overlap_areas(fragments)))

    def test_eps_sensitive_subtract_witness_is_partitioned_not_overlapped(self):
        subject = [(0, .0005, 0), (.001, .0015, 0), (0, .0006, 0)]
        cutter = [(0, 0, 1), (.0001, 0, 1), (.00005, .01, 1)]
        expected = area(subject) - area(exact_convex_clip(subject, cutter))
        v2_pieces = v2.subtract_convex(subject, cutter)
        v2_overlap = max(value for _i, _j, value in pairwise_overlap_areas(v2_pieces))
        self.assertGreater(v2_overlap, 1e-9)  # negative control: EPS bands overlap

        pieces = v3.subtract_convex(subject, cutter)
        numeric_error = 1e-12 * max(1.0, area(subject))
        self.assertLessEqual(abs(sum(area(poly) for poly in pieces) - expected), numeric_error)
        self.assertTrue(all(min(barycentric(subject, point)) >= -1e-10
                            for poly in pieces for point in poly))
        self.assertTrue(all(value <= numeric_error
                            for _i, _j, value in pairwise_overlap_areas(pieces)))

    def test_zero_length_and_collinear_cutter_edges_are_vacuous(self):
        subject = [(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0)]
        triangle = [(1, 1, 1), (3, 1, 1), (1, 3, 1)]
        redundant = [(1, 1, 1), (1, 1, 1), (2, 1, 1), (3, 1, 1),
                     (2, 2, 1), (1, 3, 1), (1, 1, 1)]
        self.assertAlmostEqual(area(triangle), area(redundant), delta=1e-12)
        expected = area(subject) - area(exact_convex_clip(subject, triangle))
        v2_pieces = v2.subtract_convex(subject, redundant)
        self.assertTrue(any(value > 1e-10 for _i, _j, value in pairwise_overlap_areas(v2_pieces)))
        pieces = v3.subtract_convex(subject, redundant)
        tolerance = 1e-10
        self.assertLessEqual(abs(sum(area(poly) for poly in pieces) - expected), tolerance)
        self.assertTrue(all(subset_of_square(poly, 1, 0, 0) for poly in pieces))
        self.assertTrue(all(value <= tolerance for _i, _j, value in pairwise_overlap_areas(pieces)))

        # This cutter has a real edge shorter than EPS but nonzero; it must not be dropped.
        thin_subject = [(0, 0, 0), (1e-8, 0, 0), (1e-8, 1, 0), (0, 1, 0)]
        short_cutter = [(0, 0, 1), (1e-8, 0, 1), (5e-9, 200, 1)]
        self.assertGreater(area(short_cutter), v3.EPS)
        self.assertGreater(math.dist(short_cutter[0][:2], short_cutter[1][:2]), 0)
        self.assertLess(math.dist(short_cutter[0][:2], short_cutter[1][:2]), v3.EPS)
        thin_expected = area(thin_subject) - area(exact_convex_clip(thin_subject, short_cutter))
        thin_pieces = v3.subtract_convex(thin_subject, short_cutter)
        self.assertLessEqual(abs(sum(area(poly) for poly in thin_pieces) - thin_expected), 1e-12)
        self.assertTrue(all(-1e-12 <= p[0] <= 1e-8 + 1e-12 and
                            -1e-12 <= p[1] <= 1 + 1e-12
                            for poly in thin_pieces for p in poly))
        self.assertTrue(all(value <= 1e-12 for _i, _j, value in pairwise_overlap_areas(thin_pieces)))

    def test_coincident_touching_and_tiny_positive_depth_overlap(self):
        square = [(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0)]
        coincident = [(x, y, 1) for x, y, _ in square]
        coincident_pieces = v3.subtract_convex(square, coincident)
        self.assertTrue(coincident_pieces)
        self.assertTrue(all(area(poly) == 0 for poly in coincident_pieces))
        self.assertEqual(v3._compound_path(coincident_pieces), "")
        adjacent = [(2, 0, 1), (4, 0, 1), (4, 2, 1), (2, 2, 1)]
        self.assertAlmostEqual(sum(area(p) for p in v3.subtract_convex(square, adjacent)), 4, delta=1e-12)

        far = ([(0, 0, 0), (2, 0, 0), (0, 2, 0)], "#45c982", "far")
        near = ([(1.9995, 0, 1), (2.0005, 0, 1), (2.0005, .001, 1)], "#e16e87", "near")
        self.assertTrue(v3.overlaps(v3.bbox(far[0]), v3.bbox(near[0])))
        self.assertTrue(v3.positive_area_overlap(far[0], near[0]))
        true_overlap = area(exact_convex_clip(far[0], near[0]))
        self.assertGreater(true_overlap, 0)
        visible = list(v3.visible_fragments([far, near]))
        visible_area = sum(area(poly) for poly, _color, _name in visible)
        self.assertAlmostEqual(visible_area, area(far[0]) + area(near[0]) - true_overlap, delta=1e-12)
        names_at_overlap = [name for poly, _color, name in visible
                            if contains(poly, 1.9997, .00005)]
        self.assertEqual(names_at_overlap, ["near"])


def contains(poly, x, y):
    inside = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                inside = not inside
    return inside


if __name__ == "__main__":
    unittest.main(verbosity=2)
