"""Tests for the isolated candidate, including a renderer-level negative control."""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(WORK))
sys.path.insert(0, str(SCRIPTS))
import vector_visibility_candidate as visibility
from draw import render


def area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1])) / 2)


def covers(poly, x, y):
    inside = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                inside = not inside
    return inside


def grid_faces(nx=4, ny=3):
    faces = []
    for j in range(ny):
        for i in range(nx):
            x0, x1 = 31.25 + i * 31.125, 31.25 + (i + 1) * 31.125
            y0, y1 = 27.375 + j * 31.125, 27.375 + (j + 1) * 31.125
            a, b, c, d = (x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)
            triangles = ((a, b, c), (a, c, d)) if (i + j) % 2 == 0 else ((a, b, d), (b, c, d))
            faces.extend((list(triangle), "#45c982", "sheet") for triangle in triangles)
    return faces


def raster(polygons, path):
    d = visibility._compound_path(polygons)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 256">'
           f'<rect width="320" height="256" fill="#14212b"/>'
           f'<path d="{d}" fill="#45c982" fill-rule="nonzero"/></svg>')
    path.write_text(svg, encoding="utf-8")
    png = path.with_suffix(".png")
    render(str(path), str(png), size=(320, 256))
    return np.asarray(Image.open(png).convert("RGB"))


class VisibilityCandidateTests(unittest.TestCase):
    def test_touching_and_tiny_positive_area_are_distinct(self):
        first = [(0, 0, 0), (2, 0, 0), (2, 2, 0)]
        touching = [(0, 0, 0), (2, 2, 0), (0, 2, 0)]
        self.assertTrue(visibility.overlaps(visibility.bbox(first), visibility.bbox(touching)))
        self.assertFalse(visibility.positive_area_overlap(first, touching))

        almost = [(2 - 1e-4, 0, 1), (4 - 1e-4, 0, 1), (2 - 1e-4, 2, 1)]
        self.assertTrue(visibility.overlaps(visibility.bbox(first), visibility.bbox(almost)))
        self.assertTrue(visibility.positive_area_overlap(first, almost))

        faces = [(first, "#45c982", "far"), (almost, "#e16e87", "near")]
        visible = list(visibility.visible_fragments(faces))
        self.assertEqual([(color, name) for poly, color, name in visible if covers(poly, 1.99995, .00002)],
                         [("#e16e87", "near")])

    def test_generated_mesh_candidate_matches_raw_and_rejects_canonical_raster_control(self):
        faces = grid_faces()
        raw = [triangle for triangle, _color, _name in faces]
        resolved = [poly for poly, _color, _name in visibility.visible_fragments(faces)]
        self.assertEqual(len(raw), 24)
        self.assertEqual(len(resolved), 24)
        self.assertEqual(sum(area(poly) for poly in raw), sum(area(poly) for poly in resolved))
        self.assertEqual(visibility._compound_path(raw), visibility._compound_path(resolved))

        # Load the unmodified historical module as a negative control. Its extra touching cuts
        # cause four one-level partial-coverage pixels in Chromium on this computed mesh.
        import importlib.util
        canonical_path = SCRIPTS / "vector_visibility.py"
        spec = importlib.util.spec_from_file_location("canonical_visibility_control", canonical_path)
        canonical = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(canonical)
        old = [poly for poly, _color, _name in canonical.visible_fragments(faces)]
        self.assertEqual(len(old), 48)
        self.assertEqual(sum(area(poly) == 0 for poly in old), 24)

        with tempfile.TemporaryDirectory(prefix="visibility-candidate-grid-") as temp:
            root = Path(temp)
            source_image = raster(raw, root / "source.svg")
            old_image = raster(old, root / "canonical.svg")
            new_image = raster(resolved, root / "candidate.svg")
        self.assertEqual(np.count_nonzero(np.any(source_image != new_image, axis=2)), 0)
        self.assertEqual(np.count_nonzero(np.any(source_image != old_image, axis=2)), 4)

    def test_changing_depth_crossing_and_declaration_order(self):
        flat = ([(0, 0, 0), (4, 0, 0), (0, 4, 0)], "#e16e87", "base")
        sloped = ([(0, 0, -1), (4, 0, 1), (0, 4, -1)], "#3974ab", "fold")
        def visible_at(faces, x, y):
            return [(color, name) for poly, color, name in visibility.visible_fragments(faces)
                    if covers(poly, x, y)]
        for order in ([flat, sloped], [sloped, flat]):
            self.assertEqual(visible_at(order, .5, .5), [("#e16e87", "base")])
            self.assertEqual(visible_at(order, 2.6, .3), [("#3974ab", "fold")])
        for y in (.17, .61, 1.05, 1.49, 1.93):
            for x in (.21, .63, 1.07, 1.51, 1.95):
                if x + y < 3.9 and abs(x - 2) > 1e-6:
                    self.assertEqual(visible_at([flat, sloped], x, y),
                                     visible_at([sloped, flat], x, y))

    def test_camera_reprojects_real_self_occlusion_without_component_skip(self):
        import importlib.util
        old_binding = sys.modules.get("vector_visibility")
        sys.modules["vector_visibility"] = visibility
        try:
            spec = importlib.util.spec_from_file_location(
                "vector_visibility_camera_fixture", SCRIPTS / "tests/test_vector_visibility.py")
            fixture = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fixture)
            fractions = []
            for yaw in (0, 55):
                faces = fixture.ring_and_occluder(yaw)
                full_area = sum(area(triangle) for triangle, _color, component in faces
                                if component == "strip")
                visible_area = sum(area(poly) for poly, _color, component
                                   in visibility.visible_fragments(faces) if component == "strip")
                fractions.append(visible_area / full_area)
        finally:
            if old_binding is None:
                sys.modules.pop("vector_visibility", None)
            else:
                sys.modules["vector_visibility"] = old_binding
        self.assertGreater(abs(fractions[0] - fractions[1]), .05, fractions)

    def test_same_component_self_occlusion_and_exact_tie_policy(self):
        outline = [(0, 0), (3, 0), (0, 3)]
        near = ([(*point, 1) for point in outline], "#e16e87", "fold")
        far = ([(*point, 0) for point in outline], "#3974ab", "fold")
        for order in ([far, near], [near, far]):
            visible = [(color, name) for poly, color, name in visibility.visible_fragments(order)
                       if covers(poly, .5, .5)]
            self.assertEqual(visible, [("#e16e87", "fold")])
        coplanar = ([(*point, 1) for point in outline], "#3974ab", "later")
        for order in ([near, coplanar], [coplanar, near]):
            visible = [(color, name) for poly, color, name in visibility.visible_fragments(order)
                       if covers(poly, .5, .5)]
            self.assertEqual(visible, [(order[0][1], order[0][2])])


if __name__ == "__main__":
    unittest.main(verbosity=2)
