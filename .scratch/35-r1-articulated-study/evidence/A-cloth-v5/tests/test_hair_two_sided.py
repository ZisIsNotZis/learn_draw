"""Tests that the hair is ONE two-sided curved sheet, not a flat single-colour band."""
from __future__ import annotations

import re
import sys
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

    def test_sheet_is_curved_in_depth(self):
        depths = [point[2] for row in self.part.grid for point in row]
        self.assertGreater(max(depths) - min(depths), 0.05,
                           msg="a flat band would have one depth")


if __name__ == "__main__":
    unittest.main()
