"""The joint measured on the picture, with the negative control that makes it mean something.

README H1: a joint reads only where exactly one contour breaks and the two orders are mixed.
The package's continuation criterion is `cross_px` >= the floor of rule 2 with
`contour_breaks` 0 across the crossing span - counted on the delivered 1:1 PNG against the
dish's *geometric* projected outline, not its visible one.

The second test is the control: with the wrapped digit put back on the underside route of
`B-hand-study-v1-r1` (same digit, same station, same radii, only the contact surface changed)
the same measurement has to fall below the floor.  Without it a green number would only say
that the audit counts something, not that it counts the crossing.
"""
from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import util  # noqa: E402

import joint_audit  # noqa: E402
import scene  # noqa: E402


class TestCrossing(unittest.TestCase):
    def test_the_crossing_clears_the_floor_and_breaks_one_contour(self):
        m = joint_audit.measure(verbose=False)
        print("  " + joint_audit.line(m))
        self.assertGreaterEqual(m["cross_px"], m["floor"],
                                "the front piece does not reach the crossing floor")
        self.assertEqual(m["contour_breaks"], 0,
                         "the rear piece's contour survives where the front piece covers it: "
                         "a merge, not a joint")
        self.assertGreater(m["contour_points_in_crossing"], 0,
                           "the two pieces do not cross at all")

    def test_the_audit_zeroes_on_the_r1_route(self):
        saved = dict(scene.WRAP)
        try:
            scene.WRAP["name"] = "__none__"      # every digit back on the underside route
            m = joint_audit.measure(verbose=False)
        finally:
            scene.WRAP.clear()
            scene.WRAP.update(saved)
        print(f"  mutation (r1's underside route): cross_px {m['cross_px']} "
              f"< floor {m['floor']}, contour points {m['contour_points_in_crossing']}")
        self.assertLess(m["cross_px"], m["floor"],
                        "the audit stays green without a rim wrap: it does not measure the joint")


if __name__ == "__main__":
    unittest.main(verbosity=2)
