"""Numerical contracts for reference-independent articulated construction."""

from dataclasses import replace
import math
import unittest

from scripts.articulated_construction import (
    LimbParameters,
    Point,
    SupportFrame,
    construct_limb,
    taper_profile,
    triangulate_polygon,
    Component,
    Camera,
    visible_scene,
    component_faces,
    visible_scene_regions,
    build_study_case,
    validate_study_case,
    polygons_overlap,
)


def _inside_test(point, polygon):
    from scripts.articulated_construction import _inside
    return _inside(point,polygon)


class ArticulatedConstructionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.support = SupportFrame("arm-surface", "depth-arm")
        self.parameters = LimbParameters(
            shoulder=Point(0.0, 0.0),
            upper_length=5.0,
            fore_length=4.0,
            hand_target=Point(6.0, 0.0),
            elbow_branch=1,
            upper_width_shoulder=1.2,
            upper_width_elbow=0.8,
            fore_width_elbow=0.75,
            fore_width_wrist=0.45,
            support=self.support,
        )

    def test_reachable_segments_preserve_lengths_and_support_attachment(self) -> None:
        result = construct_limb(self.parameters)
        self.assertAlmostEqual(math.dist((0, 0), (result.elbow.u, result.elbow.v)), 5.0)
        self.assertAlmostEqual(math.dist((result.elbow.u, result.elbow.v), (6, 0)), 4.0)
        self.assertEqual(result.palm.origin, result.wrist)
        self.assertIs(result.palm.support, self.support)
        self.assertIs(result.support, self.support)
        self.assertEqual(result.upper_arm.start, self.parameters.shoulder)
        self.assertEqual(result.forearm.end, self.parameters.hand_target)

    def test_unreachable_and_degenerate_inputs_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "reachable"):
            construct_limb(replace(self.parameters, hand_target=Point(10.0, 0.0)))
        with self.assertRaisesRegex(ValueError, "differ"):
            construct_limb(replace(self.parameters, hand_target=Point(0.0, 0.0)))
        with self.assertRaisesRegex(ValueError, "branch"):
            construct_limb(replace(self.parameters, elbow_branch=0))

    def test_branch_changes_elbow_side(self) -> None:
        positive = construct_limb(self.parameters)
        negative = construct_limb(replace(self.parameters, elbow_branch=-1))
        self.assertAlmostEqual(positive.elbow.v, -negative.elbow.v)
        self.assertNotEqual(positive.elbow, negative.elbow)

    def test_width_ratio_changes_computed_contour(self) -> None:
        baseline = construct_limb(self.parameters)
        wider = construct_limb(replace(self.parameters, upper_width_shoulder=1.8))
        self.assertNotEqual(baseline.upper_arm.outline, wider.upper_arm.outline)
        base_width = math.dist((baseline.upper_arm.outline[0].u, baseline.upper_arm.outline[0].v), (0, 0))
        wide_width = math.dist((wider.upper_arm.outline[0].u, wider.upper_arm.outline[0].v), (0, 0))
        self.assertGreater(wide_width, base_width)

    def test_result_is_deterministic(self) -> None:
        self.assertEqual(construct_limb(self.parameters), construct_limb(self.parameters))

    def test_taper_is_smoothly_sampled_and_capped(self) -> None:
        segment = construct_limb(self.parameters).upper_arm
        self.assertGreater(len(segment.outline), 60)
        # Rounded caps extend by exactly their endpoint radii.
        start = self.parameters.shoulder
        end = construct_limb(self.parameters).elbow
        direction = ((end.u - start.u) / math.hypot(end.u - start.u, end.v - start.v),
                     (end.v - start.v) / math.hypot(end.u - start.u, end.v - start.v))
        projections = [(p.u - start.u) * direction[0] + (p.v - start.v) * direction[1]
                       for p in segment.outline]
        self.assertAlmostEqual(min(projections), -1.2, places=6)
        self.assertAlmostEqual(max(projections), math.hypot(end.u - start.u, end.v - start.v) + 0.8, places=6)
        self.assertLess(math.dist((segment.outline[0].u,segment.outline[0].v),
                                  (segment.outline[-1].u,segment.outline[-1].v)), 1e-12)
        edge_steps = [math.dist((a.u,a.v),(b.u,b.v)) for a,b in zip(segment.outline,segment.outline[1:])]
        self.assertLess(max(edge_steps), 0.6)
        self.assertTrue(all(math.isfinite(p.u) and math.isfinite(p.v) for p in segment.outline))

    def test_support_maps_local_geometry_to_world(self) -> None:
        frame = SupportFrame("torso", "depth", (1, 2, 3), (2, 0, 0), (0, 0, 4))
        self.assertEqual(frame.local_to_world(Point(3, 2)), (7, 2, 11))
        self.assertEqual(len(construct_limb(replace(self.parameters, support=frame)).upper_arm.world_outline(frame)),
                         len(construct_limb(self.parameters).upper_arm.outline))

    def test_smoothstep_width_values_and_endpoint_derivatives(self) -> None:
        self.assertAlmostEqual(taper_profile(0.0, 2.0, 1.0), 2.0)
        self.assertAlmostEqual(taper_profile(0.25, 2.0, 1.0), 1.84375)
        self.assertAlmostEqual(taper_profile(0.5, 2.0, 1.0), 1.5)
        self.assertAlmostEqual(taper_profile(0.75, 2.0, 1.0), 1.15625)
        self.assertAlmostEqual(taper_profile(1.0, 2.0, 1.0), 1.0)
        epsilon = 1e-5
        start_slope = (taper_profile(epsilon, 2.0, 1.0) - 2.0) / epsilon
        end_slope = (1.0 - taper_profile(1.0-epsilon, 2.0, 1.0)) / epsilon
        self.assertLess(abs(start_slope), 1e-4)
        self.assertLess(abs(end_slope), 1e-4)
        self.assertAlmostEqual(taper_profile(0.4, 2, 1), taper_profile(0.6, 1, 2), places=12)

    def test_concave_triangulation_coverage_disjoint_winding_and_invalid_inputs(self) -> None:
        polygon = (Point(0,0), Point(2,0), Point(2,1), Point(1,0.4), Point(0,1))
        for contour in (polygon, tuple(reversed(polygon))):
            triangles=triangulate_polygon(contour)
            area=lambda poly: abs(sum(a.u*b.v-b.u*a.v for a,b in zip(poly,poly[1:]+poly[:1])))/2
            polygon_area=area(contour)
            self.assertEqual(len(triangles),len(contour)-2)
            self.assertAlmostEqual(sum(area(t) for t in triangles),polygon_area,places=12)
            self.assertTrue(all((b.u-a.u)*(c.v-a.v)-(b.v-a.v)*(c.u-a.u) != 0 for a,b,c in triangles))
            for tri in triangles:
                center=Point(sum(p.u for p in tri)/3,sum(p.v for p in tri)/3)
                self.assertTrue(_inside_test(center,contour))
            for i,first in enumerate(triangles):
                for second in triangles[i+1:]:
                    self.assertFalse(polygons_overlap(first,second))
        with self.assertRaisesRegex(ValueError,"self-intersecting"):
            triangulate_polygon((Point(0,0),Point(3,2),Point(0,3),Point(2,0)))
        with self.assertRaisesRegex(ValueError,"zero area"):
            triangulate_polygon((Point(0,0),Point(1,0),Point(2,0)))

    def test_positive_area_overlap_includes_identical_contained_and_collinear_cases(self):
        square=(Point(0,0),Point(2,0),Point(2,2),Point(0,2))
        contained=(Point(0.5,0.5),Point(1,0.5),Point(1,1),Point(0.5,1))
        partial=(Point(1,0),Point(3,0),Point(3,1),Point(1,1))
        edge_only=(Point(2,0),Point(3,0),Point(3,2),Point(2,2))
        self.assertTrue(polygons_overlap(square,square))
        self.assertTrue(polygons_overlap(square,contained))
        self.assertTrue(polygons_overlap(square,partial))
        self.assertFalse(polygons_overlap(square,edge_only))

    def test_depth_adapter_uses_world_depth_and_is_order_independent(self) -> None:
        back = Component("back", "rear test plane", SupportFrame("back", "back", (0,0,0)),
                         (Point(0,0),Point(2,0),Point(2,2),Point(0,2)), "blue")
        front = Component("front", "near test plane", SupportFrame("front", "front", (0,0,1)),
                          (Point(0,0),Point(2,0),Point(2,2),Point(0,2)), "red")
        for components in ((back,front),(front,back)):
            visible = visible_scene(components, Camera())
            area_by_name = {}
            for polygon, _color, name in visible:
                area = abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1])))/2
                area_by_name[name] = area_by_name.get(name,0)+area
            self.assertAlmostEqual(area_by_name.get("back",0), 0, places=7)
            self.assertAlmostEqual(area_by_name.get("front",0), 4, places=7)
        reversed_depth = (
            Component("back", "rear test plane", SupportFrame("back", "back", (0,0,1)),
                      (Point(0,0),Point(2,0),Point(2,2),Point(0,2)), "blue"),
            Component("front", "near test plane", SupportFrame("front", "front", (0,0,0)),
                      (Point(0,0),Point(2,0),Point(2,2),Point(0,2)), "red"),
        )
        reverse_visible = visible_scene(reversed_depth, Camera())
        positive_area_names = set()
        for polygon, _color, name in reverse_visible:
            area = abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1])))/2
            if area > 1e-7:
                positive_area_names.add(name)
        self.assertEqual(positive_area_names, {"back"})
        self.assertEqual(component_faces(reversed_depth, Camera()),
                         component_faces(reversed_depth, Camera()))

    def test_camera_basis_preserves_vertical_horizontal_and_signed_depth(self) -> None:
        camera=Camera()
        self.assertEqual(camera.project((0,0,0)), (0,0,0))
        self.assertEqual(camera.project((0,2,0)), (0,2,0))
        self.assertEqual(camera.project((3,0,0)), (3,0,0))
        self.assertEqual(camera.project((0,0,-4)), (0,0,-4))
        self.assertEqual(camera.project((0,0,5))[2] - camera.project((0,0,-5))[2], 10)
        from scripts.articulated_construction import _ellipse
        torso=Component("torso","upright bbox contract",SupportFrame("body","body"),
                        _ellipse(Point(0,1.2),.9,1.2),"blue")
        points=[camera.project(torso.support.local_to_world(p)) for p in torso.outline]
        width=max(p[0] for p in points)-min(p[0] for p in points)
        height=max(p[1] for p in points)-min(p[1] for p in points)
        self.assertGreater(height/width, 1.2)

    def test_validator_rejects_undeclared_coplanar_solid_intersection(self) -> None:
        study = build_study_case("control")
        upper = next(c for c in study.components if c.name == "upper_arm")
        prop_index = next(i for i,c in enumerate(study.components) if c.name == "prop")
        prop = study.components[prop_index]
        components = list(study.components)
        tall_outline = tuple(Point(study.contact.u+0.24+0.24*math.cos(2*math.pi*i/32),
                                   study.contact.v+2.0*math.sin(2*math.pi*i/32)) for i in range(32))
        components[prop_index] = replace(prop, support=upper.support, outline=tall_outline)
        with self.assertRaisesRegex(ValueError, "3D surface intersection"):
            validate_study_case(replace(study, components=tuple(components)))

    def test_frozen_scene_cases_keep_semantic_contact_and_control_gap(self) -> None:
        baseline = build_study_case("baseline")
        variant = build_study_case("variant")
        control = build_study_case("control")
        for study in (baseline, variant, control):
            self.assertTrue(validate_study_case(study))
            names = {component.name for component in study.components}
            self.assertEqual(names, {"head","neck","torso","upper_arm","forearm","hand","prop"})
            faces = component_faces(study.components, study.camera)
            self.assertGreater(len(faces), 200)
            depths = [point[2] for triangle, _fill, _name in faces for point in triangle]
            self.assertGreater(max(depths)-min(depths), 0.1)
            self.assertTrue(visible_scene(study.components, study.camera))
            self.assertEqual(visible_scene_regions(study.components, study.camera),
                             visible_scene_regions(study.components, study.camera))
        baseline_hand = next(c for c in baseline.components if c.name == "hand")
        variant_hand = next(c for c in variant.components if c.name == "hand")
        self.assertAlmostEqual(max(p.u for p in baseline_hand.outline), baseline.contact.u, places=8)
        self.assertAlmostEqual(max(p.u for p in variant_hand.outline), variant.contact.u, places=8)
        self.assertNotEqual(baseline.contact, variant.contact)
        self.assertTrue(control.control)
        self.assertAlmostEqual((baseline.hand_target.u-control.hand_target.u),
                               0.18*(1.65+1.35), places=8)
        control_hand = next(c for c in control.components if c.name == "hand")
        control_gap = control.contact.u-max(p.u for p in control_hand.outline)
        self.assertAlmostEqual(control_gap, 0.18*(1.65+1.35), places=8)
        self.assertAlmostEqual(baseline.components[0].outline[0].u * 1.08,
                               variant.components[0].outline[0].u, places=6)
        base_torso = next(c for c in baseline.components if c.name == "torso")
        self.assertNotEqual(base_torso.support.local_to_world(Point(0,1))[2],
                            base_torso.support.local_to_world(Point(1,1))[2])
        self.assertEqual(build_study_case("baseline"), build_study_case("baseline"))

    def test_nonfinite_degenerate_support_and_invalid_dimensions_rejected(self) -> None:
        invalids = [
            replace(self.parameters, upper_length=float("nan")),
            replace(self.parameters, upper_length=float("inf")),
            replace(self.parameters, upper_length=0),
            replace(self.parameters, fore_width_wrist=-1),
            replace(self.parameters, support=SupportFrame("x", "d", u_axis=(1, 0, 0), v_axis=(2, 0, 0))),
        ]
        for parameters in invalids:
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                construct_limb(parameters)


if __name__ == "__main__":
    unittest.main()
