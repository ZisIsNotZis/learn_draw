"""The anchor inventory: every anchor a part declares is accounted for, both ways.

Defect B1 of the v6 closeout: 36 anchors were declared, 34 were joint endpoints, and
the two cuff anchors named `sleeve_seat` appeared in neither a `Joint` nor
`NON_JOINTS` — while the README, the repair log and `seam_contract`'s comment claimed a
completeness test existed.  This is that test.

It fails in both directions and refuses a `NON_JOINTS` entry with no reason:
`unaccounted_anchors` never returns an empty dict because it was never asked anything;
`test_an_unaccounted_anchor_is_reported` adds one in memory and shows the accounting
notices it, which is what makes the other tests discriminating rather than decorative.
"""
from __future__ import annotations

import dataclasses
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
ROOT = HERE.parents[4]
for path in (str(ROOT), str(EVIDENCE)):
    if path not in sys.path:
        sys.path.insert(0, path)

from source import assemble, seam_contract                     # noqa: E402
from source.parts.frames import Anchor, Point                  # noqa: E402


class AnchorInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts = assemble.build()["parts"]
        cls.inventory = seam_contract.unaccounted_anchors(cls.parts)

    def test_every_declared_anchor_is_a_joint_or_a_stated_non_joint(self):
        self.assertEqual([], self.inventory["unaccounted"],
                         msg="an anchor that no joint reads and no reason excuses: "
                             + ", ".join(self.inventory["unaccounted"]))

    def test_the_inventory_names_only_anchors_that_exist(self):
        self.assertEqual([], self.inventory["inventory_names_a_missing_anchor"],
                         msg="the joint list or NON_JOINTS names an anchor no part declares: "
                             + ", ".join(self.inventory["inventory_names_a_missing_anchor"]))
        self.assertEqual([], self.inventory["non_joint_without_reason"],
                         msg="a NON_JOINTS entry gives no reason: "
                             + ", ".join(self.inventory["non_joint_without_reason"]))

    def test_the_three_accounts_add_up_to_the_declared_anchors(self):
        """Every declared anchor is counted exactly once: as a joint endpoint or as a
        stated non-joint.  Printed so the arithmetic is visible, not just asserted."""
        inventory = self.inventory
        print(f"\nanchors declared {inventory['declared']} = "
              f"joint endpoints {inventory['joint_endpoints']} + "
              f"non-joints {inventory['non_joints']} + "
              f"unaccounted {len(inventory['unaccounted'])}")
        self.assertEqual(inventory["declared"],
                         inventory["joint_endpoints"] + inventory["non_joints"]
                         + len(inventory["unaccounted"]))
        self.assertGreater(inventory["joint_endpoints"], 0, msg="no joint reads any anchor")
        self.assertGreater(inventory["non_joints"], 0, msg="no anchor is declared a non-joint")

    def test_an_unaccounted_anchor_is_reported(self):
        """The accounting's negative control, in memory: declare one more anchor on a
        part and the inventory must name it as unaccounted."""
        bow = self.parts["A-bow-ribbon"]
        anchors = dict(bow.anchors)
        anchors["left_tail_exit"] = Anchor(Point(20.0, 264.0), (1.0, 0.0))
        mutated = dict(self.parts)
        mutated["A-bow-ribbon"] = dataclasses.replace(bow, anchors=anchors)

        reported = seam_contract.unaccounted_anchors(mutated)
        self.assertEqual(["A-bow-ribbon.left_tail_exit"], reported["unaccounted"],
                         msg="a newly declared anchor was not reported as unaccounted")
        self.assertEqual(self.inventory["declared"] + 1, reported["declared"])
        self.assertEqual([], self.inventory["unaccounted"],
                         msg="the unmodified build must still account for every anchor")

    def test_a_non_joint_without_a_reason_is_reported(self):
        non_joints = dict(seam_contract.NON_JOINTS)
        non_joints[("A-bow-ribbon", "knot")] = "  "
        reported = seam_contract.unaccounted_anchors(self.parts, non_joints=non_joints)
        self.assertEqual(["A-bow-ribbon.knot"], reported["non_joint_without_reason"])


if __name__ == "__main__":
    unittest.main()
