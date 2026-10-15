"""Bounded depth, boundary, subdivision, and SVG-fill regressions for opaque triangles."""
import math
import sys
import tempfile
from pathlib import Path
import unittest

import cv2
import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from vector_visibility import visible_fragments, visible_regions
from draw import render


def covers(poly, x, y):
    inside = False
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if (a[1] > y) != (b[1] > y):
            if x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
                inside = not inside
    return inside


def visible_at(faces, x, y):
    return [(color, name) for poly, color, name in visible_fragments(faces)
            if covers(poly, x, y)]


def polygon_area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1])) / 2)


def square_mesh(nx, ny, diagonal_flip=False):
    faces = []
    for j in range(ny):
        for i in range(nx):
            x0, x1 = i / nx * 3, (i + 1) / nx * 3
            y0, y1 = j / ny * 2, (j + 1) / ny * 2
            a, b, c, d = (x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)
            flip = (i + j) % 2 == 1 if diagonal_flip else False
            tris = ((a, b, d), (b, c, d)) if flip else ((a, b, c), (a, c, d))
            faces.extend((list(tri), '#45c982', 'sheet') for tri in tris)
    return faces


def ring_and_occluder(yaw, segments=24):
    """Same local ring strip and body card, projected from two camera yaws."""
    angle = math.radians(yaw)

    def project(p):
        x, y, z = p
        return (200 + x * math.cos(angle) + z * math.sin(angle),
                150 - y, z * math.cos(angle) - x * math.sin(angle))

    faces = []
    for i in range(segments):
        def point(step, v):
            t = 2 * math.pi * step / segments
            return (math.cos(t) + v * .12 * math.cos(t),
                    .12 * math.sin(2 * t),
                    math.sin(t) + v * .12 * math.sin(t))

        for va, vb, color in ((-1, -.3, '#b64e78'), (-.3, .3, '#f0adbd'),
                              (.3, 1, '#b64e78')):
            a, b = point(i, va), point(i + 1, va)
            c, d = point(i + 1, vb), point(i, vb)
            faces.extend((([project(p) for p in tri], color, 'strip')
                          for tri in ((a, b, c), (a, c, d))))
    body = [((-0.7, -0.5, .55), (.7, -0.5, .55), (.7, .5, .55)),
            ((-.7, -.5, .55), (.7, .5, .55), (-.7, .5, .55))]
    faces.extend(([project(p) for p in tri], '#45c982', 'body') for tri in body)
    return faces


def component_area(faces, name):
    return sum(polygon_area(poly) for poly, _color, component in visible_fragments(faces)
               if component == name)


def fractional_grid_with_occluder():
    faces = []
    for j in range(6):
        for i in range(8):
            x0, x1 = 31.25 + i * 31.125, 31.25 + (i + 1) * 31.125
            y0, y1 = 27.375 + j * 31.125, 27.375 + (j + 1) * 31.125
            a, b, c, d = (x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)
            tris = ((a, b, c), (a, c, d)) if (i + j) % 2 == 0 else ((a, b, d), (b, c, d))
            faces.extend((list(tri), '#45c982', 'sheet') for tri in tris)
    faces.append(([(145.25, 75.375, 2), (225.25, 75.375, 2), (185.25, 180.375, 2)],
                  '#e16e87', 'near-occluder'))
    return faces


def raster_svg(faces, compound):
    if compound:
        shapes = [f'<path d="{path}" fill="{color}" fill-rule="nonzero"/>'
                  for path, color, _component in visible_regions(faces)]
    else:
        shapes = []
        for polygon, color, _component in visible_fragments(faces):
            points = ' '.join(f'{x:.12g},{y:.12g}' for x, y, _depth in polygon)
            shapes.append(f'<polygon points="{points}" fill="{color}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 256">'
            '<rect width="320" height="256" fill="#14212b"/>'
            + ''.join(shapes) + '</svg>')


class VectorVisibilityTests(unittest.TestCase):
    def test_adjacent_tessellated_faces_cover_interior_without_geometry_gaps(self):
        faces = square_mesh(3, 2)
        for row in range(21):
            y = (row + .371) * 2 / 21
            for col in range(31):
                x = (col + .271) * 3 / 31
                self.assertEqual(len(visible_at(faces, x, y)), 1, (x, y))
        regions = list(visible_regions(faces))
        self.assertEqual([(color, name) for _path, color, name in regions],
                         [('#45c982', 'sheet')])
        # One nonzero-winding compound path retains all twelve source triangles.
        self.assertEqual(regions[0][0].count('M '), 12)

    def test_chromium_raster_has_no_tessellation_seams_or_boundary_leaks(self):
        faces = fractional_grid_with_occluder()
        with tempfile.TemporaryDirectory(prefix='vector-visibility-raster-') as temp_dir:
            root = Path(temp_dir)
            grouped_svg = root / 'grouped.svg'
            grouped_png = root / 'grouped.png'
            independent_svg = root / 'independent.svg'
            independent_png = root / 'independent.png'
            grouped_svg.write_text(raster_svg(faces, compound=True), encoding='utf-8')
            independent_svg.write_text(raster_svg(faces, compound=False), encoding='utf-8')
            render(str(grouped_svg), str(grouped_png), size=(320, 256))
            render(str(independent_svg), str(independent_png), size=(320, 256))
            grouped = cv2.imread(str(grouped_png), cv2.IMREAD_COLOR)
            independent = cv2.imread(str(independent_png), cv2.IMREAD_COLOR)

        self.assertIsNotNone(grouped)
        self.assertIsNotNone(independent)
        sheet_bgr = (130, 201, 69)  # #45c982
        near_bgr = (135, 110, 225)  # #e16e87
        background_bgr = (43, 33, 20)  # #14212b

        # A wholly interior far-sheet area crosses many internal grid edges.
        # A per-face-polygon negative control proves this raster assertion catches the old seam.
        fixed_far = grouped[28:214, 32:131]
        old_far = independent[28:214, 32:131]
        self.assertEqual(np.count_nonzero(np.any(fixed_far != sheet_bgr, axis=2)), 0)
        self.assertGreater(np.count_nonzero(np.any(old_far != sheet_bgr, axis=2)), 0)

        def pixel(x, y):
            return tuple(int(channel) for channel in grouped[y, x])

        # Exterior silhouette: inside pixels remain filled; outside pixels remain background.
        self.assertEqual(pixel(30, 100), background_bgr)
        self.assertEqual(pixel(32, 100), sheet_bgr)
        self.assertEqual(pixel(279, 100), sheet_bgr)
        self.assertEqual(pixel(281, 100), background_bgr)
        self.assertEqual(pixel(100, 26), background_bgr)
        self.assertEqual(pixel(100, 28), sheet_bgr)
        self.assertEqual(pixel(100, 213), sheet_bgr)
        self.assertEqual(pixel(100, 215), background_bgr)

        # The foreground triangle ends at a real depth boundary; far fill resumes outside it.
        self.assertEqual(pixel(185, 100), near_bgr)
        self.assertEqual(pixel(180, 80), near_bgr)
        self.assertEqual(pixel(153, 100), sheet_bgr)
        self.assertEqual(pixel(230, 100), sheet_bgr)
        self.assertEqual(pixel(15, 15), background_bgr)

    def test_partial_occlusion_preserves_far_edges_and_background(self):
        far = ([(0, 0, 0), (4, 0, 0), (0, 4, 0)], '#45c982', 'back')
        near = ([(.5, .5, 1), (2.5, .5, 1), (.5, 2.5, 1)], '#e16e87', 'front')
        fragments = list(visible_fragments([far, near]))
        far_area = sum(polygon_area(poly) for poly, _color, name in fragments if name == 'back')
        self.assertAlmostEqual(far_area, 6, delta=1e-8)
        self.assertEqual(visible_at([far, near], .8, .8), [('#e16e87', 'front')])
        self.assertEqual(visible_at([far, near], 2.8, .4), [('#45c982', 'back')])
        self.assertEqual(visible_at([far, near], 3, 3), [])

    def test_depth_flip_crosses_inside_overlap(self):
        base = ([(0, 0, 0), (4, 0, 0), (0, 4, 0)], '#e16e87', 'base')
        slanted = ([(0, 0, -1), (4, 0, 1), (0, 4, -1)], '#3974ab', 'strip')
        for faces in ([base, slanted], [slanted, base]):
            self.assertEqual(visible_at(faces, .5, .5)[0][1], 'base')
            self.assertEqual(visible_at(faces, 1.9, .3)[0][1], 'base')
            self.assertEqual(visible_at(faces, 2.1, .3)[0][1], 'strip')
            self.assertEqual(visible_at(faces, 2.6, .3)[0][1], 'strip')

    def test_declaration_order_is_irrelevant_away_from_exact_tie(self):
        flat = ([(0, 0, 0), (4, 0, 0), (0, 4, 0)], '#e16e87', 'flat')
        slope = ([(0, 0, -1), (4, 0, 1), (0, 4, -1)], '#3974ab', 'slope')
        orders = ([flat, slope], [slope, flat])
        for row in range(11):
            y = (row + .211) * 3.6 / 11
            for col in range(11):
                x = (col + .317) * 3.6 / 11
                if x + y >= 3.9 or abs(x - 2) < 1e-6:
                    continue
                self.assertEqual(visible_at(orders[0], x, y), visible_at(orders[1], x, y),
                                 (x, y))

    def test_self_occlusion_keeps_near_paint_of_same_component(self):
        outline = [(0, 0), (3, 0), (0, 3)]
        near = ([(*point, 1) for point in outline], '#e16e87', 'fold')
        far = ([(*point, 0) for point in outline], '#3974ab', 'fold')
        for faces in ([far, near], [near, far]):
            self.assertEqual(visible_at(faces, .5, .5), [('#e16e87', 'fold')])

    def test_edge_tangency_and_coplanar_tie_policy(self):
        left = ([(0, 0, 0), (2, 0, 0), (0, 2, 0)], '#45c982', 'left')
        right = ([(2, 0, 0), (2, 2, 0), (0, 2, 0)], '#3974ab', 'right')
        self.assertEqual(visible_at([left, right], .5, .5), [('#45c982', 'left')])
        self.assertEqual(visible_at([left, right], 1.5, 1.5), [('#3974ab', 'right')])

        coplanar_later = ([(0, 0, 0), (2, 0, 0), (0, 2, 0)], '#3974ab', 'later')
        for order in ([left, coplanar_later], [coplanar_later, left]):
            self.assertEqual(visible_at(order, .5, .5), [(order[0][1], order[0][2])])

    def test_alternate_subdivision_preserves_sampled_strip_coverage(self):
        coarse = square_mesh(1, 1)
        retessellated = square_mesh(6, 4, diagonal_flip=True)
        for row in range(17):
            y = (row + .137) * 2 / 17
            for col in range(23):
                x = (col + .293) * 3 / 23
                self.assertEqual(visible_at(coarse, x, y), visible_at(retessellated, x, y),
                                 (x, y))

    def test_same_whole_strip_updates_visibility_in_two_cameras(self):
        front = ring_and_occluder(0)
        oblique = ring_and_occluder(55)
        full_front = sum(polygon_area(tri) for tri, _color, name in front if name == 'strip')
        full_oblique = sum(polygon_area(tri) for tri, _color, name in oblique if name == 'strip')
        fraction_front = component_area(front, 'strip') / full_front
        fraction_oblique = component_area(oblique, 'strip') / full_oblique
        self.assertGreater(abs(fraction_front - fraction_oblique), .05)
        self.assertAlmostEqual(fraction_front, .8755, delta=.01)
        self.assertAlmostEqual(fraction_oblique, .7968, delta=.01)

    def test_visible_regions_group_only_matching_semantic_fills(self):
        faces = [
            ([(0, 0, 0), (1, 0, 0), (0, 1, 0)], '#45c982', 'sheet'),
            ([(2, 0, 0), (3, 0, 0), (2, 1, 0)], '#45c982', 'sheet'),
            ([(4, 0, 0), (5, 0, 0), (4, 1, 0)], '#3974ab', 'other'),
        ]
        regions = list(visible_regions(faces))
        self.assertEqual([(color, name) for _path, color, name in regions],
                         [('#45c982', 'sheet'), ('#3974ab', 'other')])
        self.assertEqual(regions[0][0].count('M '), 2)
        self.assertEqual(regions[1][0].count('M '), 1)


if __name__ == '__main__':
    unittest.main()
