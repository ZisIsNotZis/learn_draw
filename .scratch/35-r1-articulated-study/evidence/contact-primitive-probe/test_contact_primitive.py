import math
import unittest
from pathlib import Path
from scripts.articulated_construction import Point, PalmAttachment, SupportFrame, Component, Camera, component_faces
from contact_primitive import ContactSpec, build_contact

class ContactPrimitiveTests(unittest.TestCase):
    def setUp(self):
        self.support=SupportFrame("hand","hand-depth",(0,0,0))
        self.spec=ContactSpec(PalmAttachment(Point(-.7,0),Point(.9,.3),self.support),Point(0,0),Point(1,0),Point(0,1),.32,.38,.13)
    def test_finite_and_degenerate_inputs(self):
        self.assertEqual(len(build_contact(self.spec)),3)
        with self.assertRaisesRegex(ValueError,"degenerate"):
            build_contact(ContactSpec(self.spec.palm,self.spec.prop_contact,Point(0,0),self.spec.opening,.3,.3,.1))
        with self.assertRaisesRegex(ValueError,"positive finite"):
            build_contact(ContactSpec(self.spec.palm,self.spec.prop_contact,self.spec.approach,self.spec.opening,.3,math.inf,.1))
    def test_deterministic_and_anchor_reachable(self):
        first=build_contact(self.spec); self.assertEqual(first,build_contact(self.spec))
        for component in first[1:]: self.assertIn(("contact",Point(0,0)),component.anchors)
        self.assertTrue(all(c.support is self.support for c in first))
        faces=component_faces(first,Camera())
        self.assertEqual({f[2] for f in faces},{c.name for c in first})
    def test_generic_palm_and_disabled_opposition_controls(self):
        generic=build_contact(self.spec, prefix="generic", skin="#d99872")[:1]
        disabled=build_contact(ContactSpec(self.spec.palm,self.spec.prop_contact,self.spec.approach,self.spec.opening,.32,.38,.13,False),prefix="gap")
        self.assertEqual(len(generic),1); self.assertEqual(len(disabled),2)
        band=disabled[-1]
        self.assertTrue(all(p.u < 0 for p in band.outline))
        # Matched positive gap control keeps every authored hand boundary away from prop x=0.
        self.assertLess(max(p.u for p in band.outline),0.0)
    def test_same_rule_handles_grip_and_flat_rim_proportions(self):
        grip=build_contact(self.spec,prefix="grip")
        rim_spec=ContactSpec(PalmAttachment(Point(-.9,.1),Point(.8,.5),self.support),Point(0,0),Point(1,0),Point(0,1),.40,.50,.17)
        rim=build_contact(rim_spec,prefix="rim")
        self.assertEqual([c.intent for c in grip],[c.intent for c in rim])
        self.assertNotEqual(tuple(c.outline for c in grip),tuple(c.outline for c in rim))
        self.assertTrue(all(c.support is self.support for c in (*grip,*rim)))
    def test_author_parameters_are_semantic_not_contour_station_table(self):
        self.assertEqual(set(ContactSpec.__dataclass_fields__),{"palm","prop_contact","approach","opening","palm_half_width","thumb_reach","band_thickness","opposition"})
        self.assertLessEqual(len(build_contact(self.spec)),3)

if __name__=="__main__": unittest.main()
