"""Numeric and integration regressions for the isolated R.smooth spatial study."""
import importlib.util
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

from scripts.articulated_construction import Point, component_faces
from scripts.vector_visibility import visible_fragments

SOURCE = Path(__file__).with_name("smooth_spatial.py")
spec = importlib.util.spec_from_file_location("smooth_spatial_study", SOURCE)
study = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = study
spec.loader.exec_module(study)


def _derivative_start(segment):
    return (3 * (segment.control1.u - segment.start.u),
            3 * (segment.control1.v - segment.start.v))


def _derivative_end(segment):
    return (3 * (segment.end.u - segment.control2.u),
            3 * (segment.end.v - segment.control2.v))


def _polygon_area(polygon):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(polygon, polygon[1:] + polygon[:1]))) / 2


def _visible_area(components, component_name):
    return sum(_polygon_area(polygon) for polygon, _color, name
               in visible_fragments(component_faces(components, study.CAMERA))
               if name == component_name)


def _span_length(spans):
    return sum(((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2) ** 0.5
               for a, b in spans)


class ClosedCatmullCurveTests(unittest.TestCase):
    def test_four_authored_landmarks_generate_closed_c1_seam_and_knots(self):
        controls = tuple(point for _name, point in study.SEMANTIC_CONTROLS)
        self.assertEqual(len(controls), 4)
        segments = study.cubic_segments(controls)
        self.assertEqual(len(segments), len(controls))
        for index, segment in enumerate(segments):
            next_segment = segments[(index + 1) % len(segments)]
            self.assertEqual(segment.end, next_segment.start)
            for left, right in zip(_derivative_end(segment), _derivative_start(next_segment)):
                self.assertAlmostEqual(left, right, places=12)
        sampled = study.sample_closed_curve(controls)
        self.assertEqual(len(sampled), 4 * 24)
        self.assertNotEqual(sampled[-1], sampled[0])  # last segment closes to first without duplicate point
        study.validate_closed_contour(sampled)

    def test_sampled_curve_guard_rejects_self_crossing_and_touching(self):
        crossing = (Point(0, 0), Point(3, 3), Point(0, 2), Point(2, 0))
        touching = (Point(0, 0), Point(2, 0), Point(1, 0), Point(1, 2))
        for controls in (crossing, touching):
            with self.subTest(controls=controls), self.assertRaisesRegex(ValueError, "self-intersects|touches"):
                study.sample_closed_curve(controls)

    def test_sampled_curve_guard_rejects_degenerate_edges_and_area(self):
        with self.assertRaisesRegex(ValueError, "zero-length|degenerate"):
            study.validate_closed_contour((Point(0, 0), Point(1, 0), Point(1, 0), Point(0, 1)))
        with self.assertRaisesRegex(ValueError, "area"):
            study.validate_closed_contour((Point(0, 0), Point(1, 0), Point(2, 0)))

    def test_same_four_inputs_drive_polygon_and_curve(self):
        polygon = study.build_components("polygon")[0]
        smooth = study.build_components("smooth")[0]
        self.assertEqual(polygon.outline, tuple(point for _name, point in study.SEMANTIC_CONTROLS))
        self.assertEqual(len(polygon.outline), 4)
        self.assertEqual(len(smooth.outline), 96)
        self.assertNotEqual(polygon.outline, smooth.outline)
        self.assertEqual(polygon.support, smooth.support)


class SpatialVisibilityIntegrationTests(unittest.TestCase):
    def test_local_support_world_camera_and_triangle_depth_are_real(self):
        components = study.build_components("smooth")
        faces = component_faces(components, study.CAMERA)
        names = {name for _tri, _fill, name in faces}
        depths = [point[2] for triangle, _fill, _name in faces for point in triangle]
        self.assertEqual(names, {"cloth", "foreground"})
        self.assertGreater(len(faces), 20)
        self.assertGreater(max(depths), min(depths) + 1.0)
        local = study.SEMANTIC_CONTROLS[1][1]
        world = components[0].support.local_to_world(local)
        self.assertAlmostEqual(world[2], local.u * 0.055 + local.v * -0.025)
        self.assertEqual(study.CAMERA.project(world), world)

    def test_depth_occluder_reduces_cloth_fill_and_boundary_visibility(self):
        for mode in ("polygon", "smooth"):
            with self.subTest(mode=mode):
                full_components = study.build_components(mode, include_occluder=False)
                occluded_components = study.build_components(mode, include_occluder=True)
                full_area = _visible_area(full_components, "cloth")
                visible_area = _visible_area(occluded_components, "cloth")
                self.assertGreater(full_area, 0.1)
                self.assertGreater(full_area - visible_area, 0.1)
                full_spans = study.visible_boundary_spans(mode, include_occluder=False)
                visible_spans = study.visible_boundary_spans(mode, include_occluder=True)
                self.assertGreater(_span_length(full_spans), _span_length(visible_spans) + 0.1)

    def test_depth_visibility_is_independent_of_face_declaration_order(self):
        components = study.build_components("smooth")
        faces = component_faces(components, study.CAMERA)
        reversed_faces = tuple(reversed(faces))
        area = lambda items: sum(_polygon_area(poly) for poly, _color, name
                                 in visible_fragments(items) if name == "cloth")
        self.assertAlmostEqual(area(faces), area(reversed_faces), places=6)

    def test_actual_spatial_svg_generation_is_finite_and_deterministic(self):
        first = study.build_svg()
        self.assertEqual(first, study.build_svg())
        self.assertTrue(first.endswith("\n"))
        self.assertIn("polygon-cloth-visible-fill", first)
        self.assertIn("smooth-cloth-visible-fill", first)
        self.assertIn("foreground", first)
        self.assertNotIn("image.jpg", first)
        paths = ET.fromstring(first).findall(".//{http://www.w3.org/2000/svg}path")
        stroked = [path.attrib.get("id", "") for path in paths
                   if path.attrib.get("stroke") not in (None, "none")]
        self.assertTrue(stroked)
        self.assertTrue(all("-cloth-boundary-" in path_id for path_id in stroked))


if __name__ == "__main__":
    unittest.main()
