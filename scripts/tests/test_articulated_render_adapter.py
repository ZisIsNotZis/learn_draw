"""Regression tests for WP04 compound fills and depth-visible semantic lines."""

import unittest

from scripts.articulated_line_visibility import transform_compound_path, visible_segment_spans
from scripts.vector_visibility import visible_regions


def _subpaths(path_data):
    paths = []
    current = []
    command = None
    tokens = path_data.split()
    for token in tokens:
        if token == "Z":
            paths.append((command, current))
            current = []
            command = None
        elif token.startswith("M ") or token.startswith("L "):
            pass
        elif token in {"M", "L"}:
            command = token
        elif "," in token:
            x, y = token.split(",")
            current.append((float(x), float(y)))
    return paths


def _signed_area(points):
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(points, points[1:] + points[:1])) / 2


class CompoundFillTests(unittest.TestCase):
    def test_backend_fragments_remain_disjoint_after_panel_transform(self):
        faces = (
            (((0, 0, 0), (2, 0, 0), (0, 2, 0)), "#aabbcc", "one-fill"),
            (((4, 0, 0), (6, 0, 0), (4, 2, 0)), "#aabbcc", "one-fill"),
        )
        path_data, _fill, _name = next(visible_regions(faces))
        transformed = transform_compound_path(path_data, lambda x, y: (20 + 3*x, 7 - 2*y))
        self.assertEqual(transformed.count("M "), 2)
        self.assertEqual(transformed.count("Z"), 2)
        paths = _subpaths(transformed)
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0][1][0], (20.0, 7.0))
        self.assertEqual(paths[1][1][0], (32.0, 7.0))
        self.assertEqual([_signed_area(points) for _command, points in paths], [-12.0, -12.0])

    def test_transformed_hole_keeps_separate_boundary_and_winding(self):
        # The clockwise inner ring is a nonzero-fill hole; the third ring is disconnected fill.
        source = ("M 0 0 L 4 0 L 4 4 L 0 4 Z "
                  "M 1 1 L 1 3 L 3 3 L 3 1 Z "
                  "M 6 0 L 7 0 L 7 1 Z")
        transformed = transform_compound_path(source, lambda x, y: (10 + 2*x, -5 + 3*y))
        self.assertEqual(transformed.count("M "), 3)
        self.assertEqual(transformed.count("Z"), 3)
        paths = [points for _command, points in _subpaths(transformed)]
        areas = [_signed_area(points) for points in paths]
        self.assertEqual(areas, [96.0, -24.0, 3.0])


class SemanticLineVisibilityTests(unittest.TestCase):
    def test_nearer_occluder_hides_semantic_line_independent_of_face_order(self):
        owner = (
            ((0, 0, 0), (2, 0, 0), (2, 2, 0)),
            ((0, 0, 0), (2, 2, 0), (0, 2, 0)),
        )
        blocker = (
            ((.75, .5, 1), (1.25, .5, 1), (1.25, 1.5, 1)),
            ((.75, .5, 1), (1.25, 1.5, 1), (.75, 1.5, 1)),
        )
        owner_faces = tuple((triangle, "#888888", "line-owner") for triangle in owner)
        blocker_faces = tuple((triangle, "#555555", "near-blocker") for triangle in blocker)
        for faces in (owner_faces + blocker_faces, blocker_faces + owner_faces):
            with self.subTest(owner_first=faces[0][2] == "line-owner"):
                spans = visible_segment_spans((0, 1, 0), (2, 1, 0), faces, "line-owner")
                self.assertEqual(len(spans), 2)
                self.assertAlmostEqual(spans[0][0], 0.0)
                self.assertAlmostEqual(spans[0][1], .375)
                self.assertAlmostEqual(spans[1][0], .625)
                self.assertAlmostEqual(spans[1][1], 1.0)

    def test_missing_owning_component_is_rejected(self):
        faces = ((((0, 0, 0), (1, 0, 0), (0, 1, 0)), "#888888", "other"),)
        with self.assertRaisesRegex(ValueError, "owner"):
            visible_segment_spans((0, 0, 0), (1, 0, 0), faces, "semantic-line-owner")


if __name__ == "__main__":
    unittest.main()
