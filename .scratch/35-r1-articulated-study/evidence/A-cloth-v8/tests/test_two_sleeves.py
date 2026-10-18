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
        """The second cuff keeps its whole authored area and shows a small band of it.

        The v6 version of this test ended on `assertLess(visible, authored * 0.01)`: it
        asserted the cuff was *entirely* hidden, which is what the user rejected.  The
        claim checked here is the requirement instead — the cuff is authored whole and a
        small fraction of the first cuff's area survives in front of it, measured against
        the first cuff because that is the ratio the reference fixes (17 %, `24x21` px
        against the right band's 2036 px).  `test_the_small_cuff_band_rejects_both_failures`
        holds the band's two ends against the two ways of losing it.
        """
        cuff = self.parts["A-left-cuff"]
        authored = outline_area(cuff)
        visible = visible_area(self.faces, cuff.name)
        fraction = visible / outline_area(self.parts["A-right-cuff"])
        print(f"\nsecond cuff: authored {authored:.1f} px2, visible {visible:.2f} px2, "
              f"{fraction * 100:.1f} % of the first cuff's {outline_area(self.parts['A-right-cuff']):.1f} px2")
        self.assertGreater(authored, 100.0,
                           msg=f"the second cuff has almost no authored extent ({authored:.3f} px2)")
        self.assertGreaterEqual(fraction, 0.10,
                                msg=f"the second cuff is too occluded to read: {visible:.2f} px2 "
                                    f"= {fraction * 100:.1f} % of the first cuff (< 10 %)")
        self.assertLessEqual(fraction, 0.25,
                             msg=f"the second cuff is not small and partly covered: "
                                 f"{fraction * 100:.1f} % of the first cuff (> 25 %)")

    def test_the_small_cuff_band_rejects_both_failures(self):
        """Mutation pair for the band above: hidden fails it, exposed fails it too.

        Both mutations move the same numbers the delivered test reads, so the band
        cannot pass on a cuff nothing occludes and cannot pass on a cuff that is not
        there.  Neither mutation touches the authored geometry: the hidden one slides the
        cuff back to the position the v6 revision authored ((95,263), i.e. +14,+8 in the
        plane), where the hair fall and the bow hide it completely; the exposed one drops
        the front cloth, exactly as the wholeness ablation does.
        """
        first_cuff = outline_area(self.parts["A-right-cuff"])
        delivered = visible_area(self.faces, "A-left-cuff") / first_cuff
        hidden_faces = tuple(
            (tuple((x + 14.0, y + 8.0, z) for x, y, z in tri), color, name)
            if name == "A-left-cuff" else (tri, color, name)
            for tri, color, name in self.faces)
        hidden = visible_area(hidden_faces, "A-left-cuff") / first_cuff
        exposed_faces = tuple(face for face in self.faces
                              if face[2] not in ("A-bow-ribbon", "A-hair-sheet"))
        exposed = visible_area(exposed_faces, "A-left-cuff") / first_cuff
        print(f"\nband {0.10:.2f}..{0.25:.2f}: delivered {delivered:.3f}, "
              f"at the v6 coordinate {hidden:.3f}, front cloth lifted {exposed:.3f}")
        self.assertGreaterEqual(delivered, 0.10)
        self.assertLessEqual(delivered, 0.25)
        self.assertLess(hidden, 0.10,
                        msg=f"a cuff under the hair fall and the bow still clears the band ({hidden:.3f})")
        self.assertGreater(exposed, 0.25,
                           msg=f"a cuff nothing occludes stays inside the band ({exposed:.3f})")

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
