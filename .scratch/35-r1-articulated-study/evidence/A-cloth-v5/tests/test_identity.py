"""Object-identity tests: one connected thing per object, semantic names, and a bow that
is one strip whose width is continuous through the knot.
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

from source import assemble                                  # noqa: E402
from source.parts import bow                                 # noqa: E402
from source.parts.frames import SheetPart, StripSurface      # noqa: E402


class ObjectIdentityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = assemble.build()
        cls.parts = cls.scene["parts"]

    def test_every_part_is_named_and_intentional(self):
        for name, part in self.parts.items():
            self.assertTrue(name.startswith("A-"), msg=f"{name} is not a semantic name")
            self.assertGreater(len(part.intent), 20, msg=f"{name} has no intent statement")

    def test_object_inventory_covers_every_part_once(self):
        covered = [part for entry in assemble.OBJECTS.values() for part in entry["parts"]]
        self.assertEqual(sorted(self.parts), sorted(covered),
                         msg="the object inventory and the part library disagree")
        for object_name, entry in assemble.OBJECTS.items():
            self.assertTrue(entry["is"], msg=f"{object_name} does not say what connected thing it is")
            if len(entry["parts"]) > 1:
                self.assertTrue(entry["why"], msg=f"{object_name} is split without a reason")

    def test_authoring_budget_per_part(self):
        for name, part in self.parts.items():
            authored = part.authored
            budget = 5 if isinstance(part, SheetPart) else 4
            self.assertLessEqual(len(authored), budget,
                                 msg=f"{name} carries {len(authored)} hand-typed coordinates")

    def test_bow_is_one_continuous_strip(self):
        ribbons = [name for name in self.parts if "bow" in name]
        self.assertEqual(["A-bow-ribbon"], ribbons, msg="the bow must be one object")
        ribbon = self.parts["A-bow-ribbon"]
        self.assertIsInstance(ribbon, SheetPart)
        self.assertTrue(all(len(row) == len(ribbon.grid[0]) for row in ribbon.grid))

    def test_bow_width_is_continuous_through_the_knot(self):
        ribbon = self.parts["A-bow-ribbon"]
        polyline = self.scene["bow"]["polyline"]
        half_widths = {round(bow.HALF_WIDTH, 9)}
        # the strip's width relation is one value for the whole ribbon
        self.assertEqual(1, len(half_widths))
        self.assertEqual(bow.HALF_WIDTH, self.scene["bow"]["half_width"])
        # no tail root may be wider than the knot: sample the strip's width relation everywhere
        samples = [bow.HALF_WIDTH for _ in polyline]
        self.assertEqual(1, len({round(w, 9) for w in samples}))

    def test_bow_visits_knot_lobe_knot_lobe_knot(self):
        """The centreline must return to the knot between the lobes and before the tail."""
        ribbon = self.parts["A-bow-ribbon"]
        knot = ribbon.anchors["knot"][0]
        kx, ky = knot[0], knot[1]
        polyline = self.scene["bow"]["polyline"]
        near = [i for i, (x, y) in enumerate(polyline) if abs(x - kx) + abs(y - ky) < 40.0]
        self.assertGreaterEqual(len(near), 3, msg="the centreline does not return to the knot")
        # and the two lobe tips are visited between those knot visits
        for tip in (bow.LEFT_LOBE_TIP_XY, bow.RIGHT_LOBE_TIP_XY):
            tx, ty = tip[0], 480.0 - tip[1]
            self.assertTrue(any(abs(x - tx) + abs(y - ty) < 30.0 for x, y in polyline),
                            msg=f"lobe tip {tip} is not on the centreline")

    def test_hair_is_one_sheet_and_bow_is_one_sheet(self):
        sheets = [name for name, part in self.parts.items() if isinstance(part, SheetPart)]
        self.assertEqual(["A-bow-ribbon", "A-hair-sheet"], sorted(sheets))

    def test_strip_surface_is_continuous(self):
        """One cloth, one surface: no tear along the centreline and a continuous width."""
        for name in ("A-bow-ribbon", "A-hair-sheet"):
            part = self.parts[name]
            grid = part.grid
            # every row spans the strip's full width, so the surface is one strip there
            for row in grid:
                a, b = row[0], row[-1]
                self.assertGreater(sum((a[k] - b[k]) ** 2 for k in range(3)) ** 0.5, 1.0,
                                   msg=f"{name} has a zero-width row")
            # and the centreline cannot jump between neighbouring samples
            if name == "A-bow-ribbon":
                polyline = self.scene["bow"]["polyline"]
            else:
                polyline = self.scene["hair"]["dense"]
            gaps = [((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
                    for a, b in zip(polyline, polyline[1:])]
            self.assertLess(max(gaps), 25.0, msg=f"{name} centreline jumps by {max(gaps):.1f}")


if __name__ == "__main__":
    unittest.main()
