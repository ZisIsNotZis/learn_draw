"""Structural checks for the provisional 3D scaffold; not a visibility-engine gate."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location(
    'spatial_sketch', Path(__file__).resolve().parents[1] / 'spatial_sketch.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class SketchTests(unittest.TestCase):
    def test_one_complete_local_strip(self):
        tris = list(module.ribbon())
        self.assertEqual(len(tris), 160 * 3 * 2)
        self.assertEqual({name for _, _, name in tris}, {'ribbon'})
        # Each longitudinal segment begins at the previous one's far edge.
        self.assertEqual(tris[0][0][1], tris[6][0][0])

    def test_camera_changes_projection_without_changing_geometry(self):
        p = list(module.ribbon())[0][0][0]
        self.assertNotEqual(module.project(p, 0, 0, 0, 1),
                            module.project(p, 55, 0, 0, 1))

    def test_two_views_contain_same_surface_counts(self):
        left = module.view(0, 290)
        right = module.view(55, 900)
        self.assertEqual(left.count('data-component="ribbon"'),
                         right.count('data-component="ribbon"'))
        self.assertEqual(left.count('data-component="body"'),
                         right.count('data-component="body"'))
        self.assertNotEqual(left, right)


if __name__ == '__main__':
    unittest.main()
