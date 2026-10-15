"""Proof cases for projected vector visibility and the provisional scaffold."""
import importlib.util
from pathlib import Path
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(SCRIPTS))
from vector_visibility import visible_fragments

SPEC = importlib.util.spec_from_file_location('spatial_sketch', SCRIPTS / 'spatial_sketch.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def covers(poly, x, y):
    hit = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                hit = not hit
    return hit


def visible_at(faces, x, y):
    return {name for poly, _, name in visible_fragments(faces) if covers(poly, x, y)}


class VisibilityTests(unittest.TestCase):
    def test_depth_not_declaration_order(self):
        near = ([(0, 0, 2), (3, 0, 2), (0, 3, 2)], '#f00', 'near')
        far = ([(0, 0, 1), (3, 0, 1), (0, 3, 1)], '#00f', 'far')
        for faces in ([near, far], [far, near]):
            self.assertEqual(visible_at(faces, 0.8, 0.8), {'near'})

    def test_depth_changes_within_one_triangle(self):
        # A slanted strip crosses a flat one: left side farther, right side nearer.
        base = ([(0, 0, 0), (4, 0, 0), (0, 4, 0)], '#f00', 'base')
        slanted = ([(0, 0, -1), (4, 0, 1), (0, 4, -1)], '#00f', 'strip')
        faces = [base, slanted]
        self.assertEqual(visible_at(faces, 0.5, 0.5), {'base'})
        self.assertEqual(visible_at(faces, 2.6, 0.3), {'strip'})

    def test_one_complete_local_strip(self):
        tris = list(module.ribbon())
        self.assertEqual(len(tris), 64 * 3 * 2)
        self.assertEqual({name for _, _, name in tris}, {'ribbon'})
        self.assertEqual(tris[0][0][1], tris[6][0][0])

    def test_camera_changes_projection_without_changing_geometry(self):
        p = list(module.ribbon())[0][0][0]
        self.assertNotEqual(module.project(p, 0, 0, 0, 1),
                            module.project(p, 55, 0, 0, 1))

    def test_views_have_both_components(self):
        for angle in (0, 55):
            svg = module.view(angle, 290)
            self.assertIn('data-component="ribbon"', svg)
            self.assertIn('data-component="body"', svg)


if __name__ == '__main__':
    unittest.main()
