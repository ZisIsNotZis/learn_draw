"""P1 clipping-root and geometry-provenance regressions for isolated candidate v2."""
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


canonical = load("clip_control_canonical", SCRIPTS / "vector_visibility.py")
v1 = load("clip_control_v1", WORK / "vector_visibility_candidate_v1.py")
v2 = load("clip_candidate_v2", WORK / "vector_visibility_candidate.py")


def barycentric(triangle, point):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = triangle
    x, y = point[:2]
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    wb = ((x - x0) * (y2 - y0) - (y - y0) * (x2 - x0)) / det
    wc = ((x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)) / det
    return 1 - wb - wc, wb, wc


def point_segment_parameter(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    t = ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / denom
    closest = (a[0] + t * dx, a[1] + t * dy)
    distance = math.hypot(point[0] - closest[0], point[1] - closest[1])
    return t, distance


def signed_area(poly):
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(poly, poly[1:] + poly[:1])) / 2


def polygon_area(poly):
    return abs(signed_area(poly))


def source_witness(scale, keep_positive, reverse=False):
    if keep_positive:
        inside_x, outside_x = -.5 / scale, -1.5 / scale
    else:
        inside_x, outside_x = .5 / scale, 1.5 / scale
    poly = [(inside_x, 0, 0), (outside_x, 1, 0), (inside_x, 2, 0)]
    return list(reversed(poly)) if reverse else poly


class VisibilityCandidateV2Tests(unittest.TestCase):
    def test_eps_shifted_crossings_stay_in_source_for_sign_scale_and_winding(self):
        # The scales exercise a fixed family of halfspaces; EPS itself is not varied.
        for scale in (.5, 1.0, 2.0):
            for keep_positive in (True, False):
                for reverse in (False, True):
                    with self.subTest(scale=scale, keep_positive=keep_positive, reverse=reverse):
                        source = source_witness(scale, keep_positive, reverse)
                        fn = lambda point, s=scale: s * v2.EPS * point[0]
                        clipped = v2.line_clip(source, fn, keep_positive)
                        self.assertGreaterEqual(len(clipped), 3)
                        self.assertTrue(all(math.isfinite(value) for p in clipped for value in p))
                        self.assertEqual((signed_area(source) > 0), (signed_area(clipped) > 0))
                        for point in clipped:
                            self.assertGreaterEqual(min(barycentric(source, point)), -1e-12)
                            shifted = fn(point) + v2.EPS if keep_positive else fn(point) - v2.EPS
                            if keep_positive:
                                self.assertGreaterEqual(shifted, -1e-20)
                            else:
                                self.assertLessEqual(shifted, 1e-20)
                            if not any(math.dist(point, vertex) <= 1e-14 for vertex in source):
                                parameters = [point_segment_parameter(point, a, b)
                                              for a, b in zip(source, source[1:] + source[:1])]
                                on_source_edge = [(t, distance) for t, distance in parameters
                                                  if distance <= 1e-12]
                                self.assertTrue(on_source_edge, point)
                                self.assertTrue(any(-1e-12 <= t <= 1 + 1e-12
                                                    for t, _distance in on_source_edge), point)

    def test_canonical_and_v1_fail_the_eps_times_x_source_subset_control(self):
        for control in (canonical, v1):
            for scale in (.5, 1.0, 2.0):
                for keep_positive in (True, False):
                    for reverse in (False, True):
                        source = source_witness(scale, keep_positive, reverse)
                        fn = lambda point, s=scale, m=control: s * m.EPS * point[0]
                        clipped = control.line_clip(source, fn, keep_positive)
                        self.assertTrue(all(math.isfinite(value) for point in clipped for value in point))
                        self.assertLess(min(min(barycentric(source, point)) for point in clipped), -1e-12)
                        bad_segments = []
                        for point in clipped:
                            if any(math.dist(point, vertex) <= 1e-14 for vertex in source):
                                continue
                            for a, b in zip(source, source[1:] + source[:1]):
                                t, distance = point_segment_parameter(point, a, b)
                                if distance <= 1e-12 and not (-1e-12 <= t <= 1 + 1e-12):
                                    bad_segments.append(t)
                        self.assertTrue(bad_segments, (scale, keep_positive, reverse, clipped))

    def test_subtract_convex_returns_finite_source_subset_fragments(self):
        # The short cutter edge makes its signed cross-product values straddle EPS; V1's
        # mismatched zero-root interpolation escapes the subject triangle.
        subject = [(0, .0005, 0), (.001, .0015, 0), (0, .0006, 0)]
        cutter = [(0, 0, 1), (.0001, 0, 1), (.00005, .01, 1)]
        v1_fragments = v1.subtract_convex(subject, cutter)
        v1_excursion = min(min(barycentric(subject, p)) for poly in v1_fragments for p in poly)
        self.assertLess(v1_excursion, -1e-3)

        fragments = v2.subtract_convex(subject, cutter)
        self.assertTrue(fragments)
        self.assertTrue(all(math.isfinite(value) for poly in fragments for p in poly for value in p))
        self.assertGreaterEqual(min(min(barycentric(subject, p)) for poly in fragments for p in poly), -1e-10)
        self.assertGreater(sum(polygon_area(poly) for poly in fragments), 0)
        # The durable oracle/audit separately records area-sum and overlap; do not treat their
        # sum as a union or add a new tolerance/merging rule in this candidate slice.


if __name__ == "__main__":
    unittest.main(verbosity=2)
