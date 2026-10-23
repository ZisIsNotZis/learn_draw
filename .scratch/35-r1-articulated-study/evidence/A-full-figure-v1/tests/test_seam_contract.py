"""The seam contract test, with a deliberate negative control.

Run: .venv/bin/python -m unittest discover -s <this dir> -v
"""
from __future__ import annotations

import dataclasses
import math
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
from source.parts.frames import Anchor, PartFrame, Point        # noqa: E402


class SeamContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = assemble.build()
        cls.parts = cls.scene["parts"]

    def test_every_declared_joint_passes(self):
        findings = seam_contract.check(self.parts)
        failed = seam_contract.failures(findings)
        self.assertEqual([], failed, msg="\n".join(f"{f['name']}: {f['detail']}" for f in failed))

    def test_joint_inventory_is_not_empty_and_covers_both_kinds(self):
        kinds = {joint.kind for joint in seam_contract.JOINTS}
        self.assertEqual({"seam", "attachment"}, kinds)
        self.assertGreaterEqual(len(seam_contract.JOINTS), 16)
        # every cloth piece that is sewn to another cloth piece appears in at least one seam
        sewn = {joint.a[0] for joint in seam_contract.JOINTS if joint.kind == "seam"}
        sewn |= {joint.b[0] for joint in seam_contract.JOINTS if joint.kind == "seam"}
        for name in ("A-collar-left", "A-collar-right", "A-bodice-upper", "A-visible-neck-skin",
                     "A-derived-waist-band", "A-bodice-continuation", "A-left-sleeve", "A-right-sleeve",
                     "A-left-cuff", "A-right-cuff"):
            self.assertIn(name, sewn, msg=f"{name} declares no seam")

    def test_negative_control_breaks_a_joint_then_restores_it(self):
        """A joint displaced by 4 px must fail. The unmodified build must still pass."""
        broken_parts = dict(self.parts)
        leaf = broken_parts["A-collar-right"]
        frame = leaf.frame
        shifted = PartFrame(frame.name, Point(frame.origin.u + 4.0, frame.origin.v),
                            frame.axis_angle_deg, frame.z0, frame.grad)
        broken_parts["A-collar-right"] = dataclasses.replace(leaf, frame=shifted)

        broken_findings = seam_contract.check(broken_parts)
        broken_failures = {f["name"]: f["detail"] for f in seam_contract.failures(broken_findings)}
        self.assertIn("S1-collar-front", broken_failures,
                      msg=f"the broken joint was not detected: {broken_failures}")
        self.assertIn("boundary gap", broken_failures["S1-collar-front"])

        restored = seam_contract.check(self.parts)
        self.assertEqual([], seam_contract.failures(restored),
                         msg="restoring the build did not restore the seam")

    def test_negative_control_detects_an_unrelated_support(self):
        """A piece put on a support far from its partner must fail the depth rule."""
        broken_parts = dict(self.parts)
        cuff = broken_parts["A-left-cuff"]
        frame = cuff.frame
        lifted = PartFrame(frame.name, frame.origin, frame.axis_angle_deg, frame.z0 + 0.5, frame.grad)
        broken_parts["A-left-cuff"] = dataclasses.replace(cuff, frame=lifted)
        names = {f["name"] for f in seam_contract.failures(seam_contract.check(broken_parts))}
        self.assertTrue({"S10-left-cuff", "S10-left-cuff-right"} & names,
                        msg=f"cuff on an unrelated support was not detected: {names}")

    def test_negative_control_rotated_tangent(self):
        """Rotate one leaf's declared seam direction by 30 degrees and move nothing.

        The boundaries stay coincident and the depth relation still holds, so only the
        tangent clause can notice: without this control the clause is unchecked against
        its own failure.  The rotation is applied to the leaf's local tangent; the frame
        map is a rotation, so the plane angle between the two declared directions stays
        30 degrees.
        """
        angle = math.radians(30.0)
        cos, sin = math.cos(angle), math.sin(angle)
        leaf = self.parts["A-collar-right"]
        anchor = leaf.anchors["Q_prime"]
        tx, ty = anchor.tangent
        rotated = (tx * cos - ty * sin, tx * sin + ty * cos)
        anchors = dict(leaf.anchors)
        anchors["Q_prime"] = Anchor(anchor.point, rotated)
        broken_parts = dict(self.parts)
        broken_parts["A-collar-right"] = dataclasses.replace(leaf, anchors=anchors)

        broken = {f["name"]: f["detail"]
                  for f in seam_contract.failures(seam_contract.check(broken_parts))}
        self.assertIn("S1-collar-front", broken, msg=f"the rotated tangent was not detected: {broken}")
        self.assertIn("tangent mismatch", broken["S1-collar-front"])
        self.assertNotIn("boundary gap", broken["S1-collar-front"],
                         msg="only the direction was changed, so no boundary may move")

        restored = seam_contract.check(self.parts)
        self.assertEqual([], seam_contract.failures(restored),
                         msg="restoring the declared tangent did not restore the seam")

    def test_shared_seam_has_coincident_boundaries(self):
        for joint in seam_contract.JOINTS:
            point_a, _za, _ta = self.parts[joint.a[0]].plane_anchor(joint.a[1])
            point_b, _zb, _tb = self.parts[joint.b[0]].plane_anchor(joint.b[1])
            self.assertLess(math.hypot(point_a.u - point_b.u, point_a.v - point_b.v), 1e-6,
                            msg=f"{joint.name} boundaries do not coincide")


if __name__ == "__main__":
    unittest.main()
