"""Every face carries its own side's colour (defect N1 of the v6 closeout).

The two-sided paint rule says a sheet's fill follows the projected winding of the face
(`frames.py`, `hair.py`).  Until this revision a quad's two triangles were both painted
from the first triangle's winding, so a triangle whose own winding pointed the other way
wore the other side's colour: measured, 7 of 660 hair faces and 41 of 720 bow faces.

Two assertions, in opposite directions: no face disagrees with its own winding, and the
per-quad rule this replaced *does* disagree on this geometry — otherwise the first
assertion would pass on a scene where the rule is untestable.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
ROOT = HERE.parents[4]
for path in (str(ROOT), str(EVIDENCE)):
    if path not in sys.path:
        sys.path.insert(0, path)

from source import assemble                                   # noqa: E402
from source.parts.frames import SheetPart, two_sided_fill      # noqa: E402


class FillWindingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = assemble.build()
        cls.sheets = {name: part for name, part in cls.scene["parts"].items()
                      if isinstance(part, SheetPart)}

    def test_every_face_is_painted_by_its_own_winding(self):
        checked = 0
        disagreements = []
        for name, part in self.sheets.items():
            for triangle, fill, _name in part.faces():
                expected = two_sided_fill(*triangle, part.front_fill, part.back_fill)
                checked += 1
                if fill != expected:
                    disagreements.append(f"{name} face {triangle} has {fill}, its winding says {expected}")
        self.assertGreater(checked, 1000, msg="no faces were checked")
        self.assertEqual([], disagreements, msg="\n".join(disagreements[:8]))

    def test_the_shared_quad_fill_would_disagree_on_this_geometry(self):
        """The negative control for the rule above, on the delivered grid.

        Paint both triangles of every quad from the first triangle's winding, as the
        previous revision did, and count the faces that then disagree with their own
        winding.  A non-zero count is what makes the rule above discriminating.
        """
        wrong = 0
        total = 0
        for part in self.sheets.values():
            grid = part.grid
            for i in range(len(grid) - 1):
                for j in range(len(grid[i]) - 1):
                    p00, p10, p11, p01 = (grid[i][j], grid[i + 1][j],
                                          grid[i + 1][j + 1], grid[i][j + 1])
                    shared = two_sided_fill(p00, p10, p01, part.front_fill, part.back_fill)
                    for triangle in ((p00, p10, p11), (p00, p11, p01)):
                        total += 1
                        if two_sided_fill(*triangle, part.front_fill, part.back_fill) != shared:
                            wrong += 1
        print(f"\nper-quad fill disagrees with the winding on {wrong} of {total} faces")
        self.assertGreater(wrong, 0,
                           msg="the per-quad rule agrees everywhere, so this test cannot "
                               "distinguish the two rules on this geometry")

    def test_the_sheet_parts_are_the_ones_with_two_fills(self):
        self.assertTrue(self.sheets, msg="no sheet parts were found")
        for name, part in self.sheets.items():
            self.assertNotEqual(part.front_fill, part.back_fill,
                                msg=f"{name} has one fill, so its two sides are a declaration")


if __name__ == "__main__":
    unittest.main()
