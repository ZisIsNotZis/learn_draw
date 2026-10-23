"""Tests that the hair is ONE two-sided curved sheet, not a flat single-colour band."""
from __future__ import annotations

import re
import sys
from collections import Counter
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
ROOT = HERE.parents[4]
for path in (str(ROOT), str(EVIDENCE)):
    if path not in sys.path:
        sys.path.insert(0, path)

from source import assemble                                  # noqa: E402
from source.parts.frames import face_normal_z                # noqa: E402
from source.parts import hair                                # noqa: E402


class HairSheetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = assemble.build()
        cls.part = cls.scene["parts"]["A-hair-sheet"]

    def test_hair_is_one_sheet_part(self):
        hair_parts = [name for name in self.scene["parts"] if "hair" in name]
        self.assertEqual(["A-hair-sheet"], hair_parts)
        self.assertEqual(1, len([self.part]), msg="one sheet object")
        self.assertGreater(len(self.part.grid), 10, msg="the sheet must be a sampled surface")

    def test_both_sides_are_painted_by_face_orientation(self):
        fills = {fill for (_tri, fill, _name) in self.part.faces()}
        self.assertEqual({hair.OUTSIDE_FILL, hair.INSIDE_FILL}, fills,
                         msg="one colour means the sheet never turns over")
        normals = [face_normal_z(tri[0], tri[1], tri[2]) for tri, _fill, _name in self.part.faces()]
        self.assertTrue(any(n > 0 for n in normals) and any(n < 0 for n in normals),
                        msg="the sheet's faces do not turn over in projection")
        mirrored = [face_normal_z(p00, p10, p01) for (p00, p10, p01) in
                    ((tri[0], tri[2], tri[1]) for tri, _f, _n in self.part.faces())]
        self.assertNotEqual(normals, mirrored)

    def test_both_fills_survive_depth_visibility_in_the_render(self):
        svg = assemble.render_svg(self.scene)[0]
        fills = set(re.findall(r'fill="(#[0-9a-fA-F]{6})"', svg))
        self.assertIn(hair.OUTSIDE_FILL, fills)
        self.assertIn(hair.INSIDE_FILL, fills,
                      msg="the inside of the sheet is not visible anywhere")

    def test_the_twist_is_what_turns_the_sheet_over(self):
        """Remove the twist and the mint must all but vanish: the reverse side is a
        twist result, not the route's hairpin self-overlap seen through a gap."""
        authored = hair.twist
        turned = Counter(fill for _t, fill, _n in self.part.faces())[hair.INSIDE_FILL]
        try:
            hair.twist = lambda t: 0.0
            flat = assemble.build()["parts"]["A-hair-sheet"]
            untwisted = Counter(fill for _t, fill, _n in flat.faces())[hair.INSIDE_FILL]
        finally:
            hair.twist = authored
        self.assertGreater(turned, 0, msg="the authored sheet never shows its reverse side")
        self.assertGreater(turned, 10 * max(untwisted, 1),
                           msg=f"removing the twist barely changes the reverse side "
                               f"({turned} faces turned, {untwisted} with no twist)")

    def test_sheet_is_curved_in_depth(self):
        depths = [point[2] for row in self.part.grid for point in row]
        self.assertGreater(max(depths) - min(depths), 0.05,
                           msg="a flat band would have one depth")


if __name__ == "__main__":
    unittest.main()
