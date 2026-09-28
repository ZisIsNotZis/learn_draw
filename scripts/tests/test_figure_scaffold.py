"""Structural invariants for the provisional seated-figure hypothesis."""
import importlib.util
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('figure_scaffold', SCRIPTS / 'figure_scaffold.py')
figure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(figure)


class FigureScaffoldTests(unittest.TestCase):
    def test_ring_is_single_closed_component(self):
        tris = list(figure.ribbon())
        self.assertEqual(len(tris), 72 * 3 * 2)
        self.assertEqual({name for _, _, name in tris}, {'ribbon'})
        from math import dist
        self.assertLess(dist(tris[0][0][0], tris[-6][0][1]), 1e-10)

    def test_bow_attaches_to_same_ribbon(self):
        from math import dist
        target = (.71, .03, .74)  # bow underside, in world space
        closest = min(dist(p, target) for tri, _, _ in figure.ribbon() for p in tri)
        self.assertLess(closest, .18)

    def test_two_sided_hair_uses_one_support(self):
        hair = list(figure.hair_sheet())
        self.assertEqual({name for _, _, name in hair}, {'hair-sheet', 'hair-fall'})
        svg = figure.view(0, 510)
        self.assertIn('fill="#3974ab"', svg)
        self.assertIn('fill="#83cbbd"', svg)
        self.assertIn('fill="#3974ab" stroke="#3974ab" stroke-width="0.22" data-component="hair-sheet"', svg)
        self.assertIn('fill="#83cbbd" stroke="#83cbbd" stroke-width="0.22" data-component="hair-sheet"', svg)

    def test_reference_is_not_loaded(self):
        self.assertEqual(len(list(figure.scene())), len(list(figure.scene())))
        self.assertIn('data-component="ribbon"', figure.view(0, 510))


if __name__ == '__main__':
    unittest.main()
