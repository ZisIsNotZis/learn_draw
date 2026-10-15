from __future__ import annotations

import unittest
import math
from dataclasses import replace
import xml.etree.ElementTree as ET

import source
from scripts.articulated_construction import Camera, Point, component_faces


class OriginalDrawingTests(unittest.TestCase):
    def setUp(self):
        self.parts, self.strokes, self.metadata = source.build()
        self.by_name = {part.name: part for part in self.parts}

    def test_svg_is_deterministic_and_has_no_external_raster_input(self):
        first = source.svg_text(self.parts,self.strokes,self.metadata)
        again = source.svg_text(*source.build())
        self.assertEqual(first,again)
        root = ET.fromstring(first)
        self.assertEqual(root.attrib["viewBox"],"0 0 600 760")
        self.assertFalse(any(element.tag.endswith("image") for element in root.iter()))
        self.assertFalse(any("href" in element.attrib for element in root.iter()))
        self.assertIn('data-part="hat_brim"',first)
        self.assertIn('data-line="jacket_lapel"',first)

    def test_named_attachments_and_hand_contact_share_actual_world_points(self):
        source.validate_scene(self.parts,self.strokes,self.metadata)
        hand = self.by_name["steadying_hand"]
        brim = self.by_name["hat_brim"]
        self.assertLess(math.dist(source.point_world(hand,dict(hand.anchors)["hat_touch"]),
                                  source.point_world(brim,dict(brim.anchors)["touch"])),1e-8)
        for part in self.parts:
            for target,own,target_anchor in part.attachments:
                other=self.by_name[target]
                self.assertLess(math.dist(source.point_world(part,dict(part.anchors)[own]),
                                          source.point_world(other,dict(other.anchors)[target_anchor])),1e-8)

    def test_components_reach_distinct_named_supports_and_computed_depth(self):
        support_ids={part.support.support_id for part in self.parts}
        self.assertGreaterEqual(len(support_ids),12)
        depths={round(Camera().project(part.support.local_to_world(part.outline[0]))[2],6)
                for part in self.parts}
        self.assertGreaterEqual(len(depths),6)
        self.assertTrue(all(part.support.depth_ref for part in self.parts))
        faces=component_faces(self.parts,Camera())
        self.assertGreater(len(faces),len(self.parts))
        self.assertTrue(source.visible_scene_regions(self.parts,Camera()))

    def test_authored_points_feed_geometry_and_semantic_line_output(self):
        jacket=self.by_name["jacket"]
        shifted=replace(jacket,outline=tuple(p+Point(0.02,0) for p in jacket.outline))
        self.assertNotEqual(component_faces((jacket,),Camera()),component_faces((shifted,),Camera()))
        moved=tuple(replace(stroke,points=(stroke.points[0]+Point(0.01,0),)+stroke.points[1:])
                    if stroke.name=="eye_left" else stroke for stroke in self.strokes)
        self.assertNotEqual(source.svg_text(self.parts,self.strokes,self.metadata),
                            source.svg_text(self.parts,moved,self.metadata))

    def test_degenerate_outline_and_detached_contact_are_rejected(self):
        jacket=self.by_name["jacket"]
        broken=replace(jacket,outline=(Point(0,0),)*4)
        invalid=tuple(broken if part.name=="jacket" else part for part in self.parts)
        with self.assertRaisesRegex(ValueError,"invalid polygon for jacket"):
            source.validate_scene(invalid,self.strokes,self.metadata)
        hand=self.by_name["steadying_hand"]
        displaced=replace(hand,support=replace(hand.support,origin=(hand.support.origin[0]+0.02,
                                                                    hand.support.origin[1],
                                                                    hand.support.origin[2])))
        invalid=tuple(displaced if part.name=="steadying_hand" else part for part in self.parts)
        with self.assertRaisesRegex(ValueError,"attachment world points do not coincide"):
            source.validate_scene(invalid,self.strokes,self.metadata)


if __name__ == "__main__":
    unittest.main()
