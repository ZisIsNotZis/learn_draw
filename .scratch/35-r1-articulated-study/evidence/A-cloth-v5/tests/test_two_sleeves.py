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
        cuff = self.parts["A-left-cuff"]
        authored = outline_area(cuff)
        visible = visible_area(self.faces, cuff.name)
        self.assertGreater(authored, 0.0)
        self.assertGreater(visible, 0.0, msg="the second cuff is not visible at all")
        self.assertLess(visible, authored * 0.75,
                        msg="the second cuff is not occluded: its visible shape was not cut by depth")

    def test_second_cuff_extent_is_a_depth_result(self):
        """Remove the bow and the same cuff geometry must become much more visible."""
        without_bow = tuple(face for face in self.faces if face[2] != "A-bow-ribbon")
        with_bow_area = visible_area(self.faces, "A-left-cuff")
        without_bow_area = visible_area(without_bow, "A-left-cuff")
        self.assertGreater(without_bow_area, with_bow_area,
                           msg="the bow does not occlude the second cuff, so its shape is not depth-derived")
        self.assertGreater(without_bow_area / with_bow_area, 1.5,
                           msg=f"occlusion is negligible ({with_bow_area:.1f} vs {without_bow_area:.1f})")

    def test_no_hand_is_drawn(self):
        """A has no hand claim: no part is a hand and no shape carries fingers."""
        for name, part in self.parts.items():
            self.assertNotIn("hand", name.lower())
            self.assertNotIn("finger", part.intent.lower())


if __name__ == "__main__":
    unittest.main()
