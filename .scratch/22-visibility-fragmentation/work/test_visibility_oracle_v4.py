"""Dimensional boundary and source-derived near-policy controls for oracle V4."""
import importlib.util
import math
import sys
import unittest
from pathlib import Path

import numpy as np

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


oracle_v3 = load("oracle_boundary_control_v3", WORK / "visibility_oracle_v3.py")
oracle_v4 = load("oracle_boundary_v4", WORK / "visibility_oracle_v4.py")
candidate_v3 = load("oracle_boundary_candidate_v3", WORK / "vector_visibility_candidate.py")


def mask_at(module, polygon, point):
    x, y = point
    inside, boundary = module.point_polygon_membership(
        polygon, np.asarray([[x]], dtype=float), np.asarray([[y]], dtype=float))
    return bool(inside[0, 0]), bool(boundary[0, 0])


def old_cross_dot_boundary(a, b, point):
    ax, ay = a
    bx, by = b
    x, y = point
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    cross = (x - ax) * dy - (y - ay) * dx
    dot = (x - ax) * dx + (y - ay) * dy
    return (abs(cross) <= 1e-12 * max(1.0, length)
            and dot >= -1e-12 and dot <= dx * dx + dy * dy + 1e-12)


class OracleV4BoundaryTests(unittest.TestCase):
    def test_tiny_collinear_edges_do_not_widen_euclidean_boundary(self):
        tolerance = oracle_v4.EDGE_DISTANCE_TOL
        self.assertEqual(tolerance, 1e-12)
        for length in (1e-8, 1e-14):
            with self.subTest(edge_length=length):
                polygon = [(-1, 0, 0), (0, 0, 0), (length, 0, 0),
                           (1, 0, 0), (1, 1, 0), (-1, 1, 0)]
                interior = (length / 2, 1e-6)
                exterior = (length / 2, -1e-6)
                edge_point = (length / 2, 0)
                start = (0, 0)
                end = (length, 0)
                beyond_start = (-1e-6, 1e-6)

                self.assertTrue(mask_at(oracle_v4, polygon, interior)[0])
                self.assertFalse(mask_at(oracle_v4, polygon, interior)[1])
                self.assertFalse(mask_at(oracle_v4, polygon, exterior)[0])
                self.assertFalse(mask_at(oracle_v4, polygon, exterior)[1])
                self.assertTrue(mask_at(oracle_v4, polygon, edge_point)[1])
                self.assertTrue(mask_at(oracle_v4, polygon, start)[1])
                self.assertTrue(mask_at(oracle_v4, polygon, end)[1])
                self.assertFalse(mask_at(oracle_v4, polygon, beyond_start)[1])

                # Negative control reproduces V3's dimensionally widened raw cross/dot predicate.
                for point in (interior, exterior, beyond_start):
                    self.assertTrue(old_cross_dot_boundary(start, end, point))

                duplicate_edge = [(-1, 0, 0), (0, 0, 0), (0, 0, 0),
                                  (length, 0, 0), (1, 0, 0), (1, 1, 0), (-1, 1, 0)]
                self.assertEqual(mask_at(oracle_v4, duplicate_edge, interior),
                                 mask_at(oracle_v4, polygon, interior))
                self.assertTrue(mask_at(oracle_v4, duplicate_edge, edge_point)[1])

    def test_boundary_distance_is_invariant_to_translation_and_winding(self):
        length = 1e-14
        polygon = [(-1, 0, 0), (0, 0, 0), (length, 0, 0),
                   (1, 0, 0), (1, 1, 0), (-1, 1, 0)]
        translated = [(x + 50, y - 20, z) for x, y, z in reversed(polygon)]
        for point in ((length / 2, 1e-6), (length / 2, -1e-6), (length / 2, 0),
                      (0, 0), (-1e-6, 0)):
            original = mask_at(oracle_v4, polygon, point)
            moved = mask_at(oracle_v4, translated, (point[0] + 50, point[1] - 20))
            self.assertEqual(original, moved, (point, original, moved))

    def test_near_policy_band_is_derived_from_source_constants(self):
        bias = oracle_v4.resolver_tie_bias(candidate_v3)
        eps = candidate_v3.EPS
        band = bias + eps
        self.assertEqual(bias, 1e-5)
        self.assertEqual(eps, 1e-7)
        self.assertAlmostEqual(band, 1.01e-5, delta=1e-20)
        self.assertGreater(band, oracle_v4.TIE_EPS)
        self.assertEqual(oracle_v3.TIE_EPS, oracle_v4.TIE_EPS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
