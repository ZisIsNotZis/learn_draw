"""The full figure's discipline: it builds, it builds the same way twice, it reads no image,
and every object it claims is a part that exists.

These are the checks that keep the picture honest as it is iterated.  None of them says the
picture is good — that is REVIEW.md's self-review, and ultimately the person's eye.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[3]
for path in (str(ROOT), str(PKG)):
    if path not in sys.path:
        sys.path.insert(0, path)

from source.full import assemble_full, figure  # noqa: E402


class FullFigure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = figure.build()
        cls.svg, cls.info = assemble_full.render_svg(cls.scene)

    def test_every_declared_object_is_a_part(self):
        missing = sorted(name for name, (part, _why) in figure.OBJECTS.items()
                         if part not in self.scene["parts"])
        self.assertEqual(missing, [], f"declared but absent: {missing}")

    def test_every_part_is_declared(self):
        declared = {part for part, _why in figure.OBJECTS.values()}
        undeclared = sorted(set(self.scene["parts"]) - declared)
        self.assertEqual(undeclared, [], f"parts with no object entry: {undeclared}")

    def test_every_object_states_what_it_is(self):
        for name, (part, why) in figure.OBJECTS.items():
            self.assertTrue(why.strip(), f"{name} has no statement of what it is")
            self.assertTrue(self.scene["parts"][part].intent.strip(),
                            f"{part} carries no intent")

    def test_the_build_is_deterministic(self):
        again, info = assemble_full.render_svg(figure.build())
        self.assertEqual(self.svg, again)
        self.assertEqual(self.info["faces"], info["faces"])

    def test_the_build_reads_no_image(self):
        for path in (PKG / "source").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for banned in ("image.jpg", "cv2", "PIL", "Image.open", "numpy"):
                self.assertNotIn(banned, text, f"{path.name} mentions {banned}")

    def test_the_frame_is_the_references_frame(self):
        self.assertEqual((figure.WIDTH, figure.HEIGHT), (1024, 1024))

    def test_fills_are_declared_colours(self):
        palette = {v for k, v in vars(figure).items()
                   if k.isupper() and isinstance(v, str) and v.startswith("#")}
        for part in self.scene["parts"].values():
            for fill in getattr(part, "fill", None), getattr(part, "front_fill", None), \
                    getattr(part, "back_fill", None):
                if fill is None:
                    continue
                self.assertIn(fill, palette, f"{part.name} uses an undeclared colour {fill}")

    def test_no_part_has_a_hand_typed_station_table(self):
        """Invariant 5: no shape carries more than a handful of typed coordinates."""
        for part in self.scene["parts"].values():
            authored = getattr(part, "authored", ())
            self.assertLessEqual(len(authored), 8, f"{part.name} types {len(authored)} coords")


class Report(unittest.TestCase):
    def test_the_committed_report_matches_this_build(self):
        path = PKG / "build-report.json"
        if not path.exists():
            self.skipTest("no committed report yet")
        committed = json.loads(path.read_text(encoding="utf-8"))
        scene = figure.build()
        svg, info = assemble_full.render_svg(scene)
        self.assertEqual(committed["faces"], info["faces"])
        self.assertEqual(committed["visible_fill_regions"], info["regions"])
        self.assertEqual(sorted(committed["parts"]), sorted(scene["parts"]))


if __name__ == "__main__":
    unittest.main()
