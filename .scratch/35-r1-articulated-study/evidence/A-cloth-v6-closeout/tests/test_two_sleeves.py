"""Tests that both sleeves exist whole and that the second cuff's surviving shape is a
depth result rather than an authored cut.
"""
from __future__ import annotations

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

from scripts.vector_visibility import visible_fragments             # noqa: E402
from source import assemble                                          # noqa: E402


def outline_area(part) -> float:
    points = [part.frame.to_plane(p) for p in part.outline]
    return abs(sum(a.u * b.v - b.u * a.v for a, b in zip(points, points[1:] + points[:1]))) / 2.0


def visible_area(faces, name: str) -> float:
    total = 0.0
    for polygon, _color, component in visible_fragments(faces):
        if component != name:
            continue
        total += abs(sum(a[0] * b[1] - b[0] * a[1]
                         for a, b in zip(polygon, polygon[1:] + polygon[:1]))) / 2.0
    return total


class TwoSleeveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = assemble.build()
        cls.faces = assemble.scene_faces(cls.scene)
        cls.parts = cls.scene["parts"]

    def test_both_sleeves_and_both_cuffs_exist_as_components(self):
        for name in ("A-left-sleeve", "A-right-sleeve", "A-left-cuff", "A-right-cuff"):
            self.assertIn(name, self.parts, msg=f"{name} is missing")
            self.assertIsNotNone(self.parts[name].component())
        supports = {self.parts[name].frame.support().support_id
                    for name in ("A-left-sleeve", "A-right-sleeve", "A-left-cuff", "A-right-cuff")}
        self.assertEqual(4, len(supports), msg="each piece must sit on its own support")

    def test_second_cuff_is_authored_whole(self):
        """The second cuff keeps its whole authored area and shows almost none of it.

        The previous version of this test ended on `assertGreaterEqual(visible, 0.0)`,
        an absolute area against zero, which no geometry can fail (B2 of the v6
        closeout).  The measurements below move in opposite directions on purpose: the
        authored area must exist, and the surviving area must be a small fraction of
        it.  A cuff drawn small, or a cuff nothing occludes, fails this test.
        """
        cuff = self.parts["A-left-cuff"]
        authored = outline_area(cuff)
        visible = visible_area(self.faces, cuff.name)
        self.assertGreater(authored, 100.0,
                           msg=f"the second cuff has almost no authored extent ({authored:.3f} px2)")
        # At this revision the authored cuff lies entirely behind the bow and the hair
        # fall, so its surviving extent is ~0: an occlusion result, not an authored cut,
        # and test_second_cuff_extent_is_a_depth_result proves the whole shape exists.
        self.assertLess(visible, authored * 0.01,
                        msg=f"the second cuff is not occluded: {visible:.3f} px2 of "
                            f"{authored:.1f} authored px2 survive")

    def test_second_cuff_extent_is_a_depth_result(self):
        """Lift every cloth piece in front of the cuff and the same authored geometry

        appears: the cuff is authored whole and only depth decides how much of it
        survives.  The pieces in front are named, so the occlusion has an owner.
        """
        front = ("A-bow-ribbon", "A-hair-sheet")
        with_front_area = visible_area(self.faces, "A-left-cuff")
        lifted = tuple(face for face in self.faces if face[2] not in front)
        without_front_area = visible_area(lifted, "A-left-cuff")
        authored = outline_area(self.parts["A-left-cuff"])
        self.assertGreater(without_front_area, with_front_area,
                           msg="no front cloth occludes the second cuff, so no depth result is shown")
        self.assertGreater(without_front_area / max(with_front_area, 1e-9), 1.5,
                           msg=f"occlusion is negligible ({with_front_area:.6f} vs {without_front_area:.6f})")
        self.assertAlmostEqual(authored, without_front_area, delta=authored * 0.02,
                               msg="the cuff's authored shape is not the shape that reappears")

    def test_no_hand_is_drawn(self):
        """A has no hand claim: no part is a hand and no shape carries fingers."""
        for name, part in self.parts.items():
            self.assertNotIn("hand", name.lower())
            self.assertNotIn("finger", part.intent.lower())


if __name__ == "__main__":
    unittest.main()
