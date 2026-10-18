"""Line ownership: every emitted mark declares a class this build knows, an owner and a source.

`assemble.mark_geometry`'s docstring names this file, and until the v6 closeout the file
did not exist (defect N4).  The mechanism — a semantic class per mark, a `data-class` and
an owning part per path — was already in the code; nothing checked it.

Two negative controls run in memory: a mark with an undeclared class, and a mark whose
owner is not a part of this build.  Both must raise.
"""
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


class LineOwnershipTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene = assemble.build()
        cls.marks = assemble.mark_geometry(cls.scene)
        cls.svg, cls.info = assemble.render_svg(cls.scene)

    def test_every_mark_declares_a_known_class(self):
        self.assertGreater(len(self.marks), 20, msg="no marks were built")
        for name, _owner, line_class, _source, _points in self.marks:
            self.assertIn(line_class, assemble.LINE_POLICY,
                          msg=f"{name} declares class {line_class!r}, which is not in LINE_POLICY")

    def test_every_mark_has_an_owner_that_is_a_part(self):
        for name, owner, _class, _source, _points in self.marks:
            self.assertIn(owner, self.scene["parts"],
                          msg=f"{name} is owned by {owner!r}, which is not a part of this build")

    def test_every_mark_names_the_geometry_that_produced_it(self):
        for name, owner, _class, source, _points in self.marks:
            self.assertTrue(source.strip(), msg=f"{name} carries no source")
            self.assertTrue(owner in source or "." in source or "sampled" in source,
                            msg=f"{name}'s source {source!r} names no geometry")

    def test_mark_names_are_unique(self):
        names = [mark[0] for mark in self.marks]
        self.assertEqual(len(names), len(set(names)), msg="two marks share a name")

    def test_every_drawn_path_states_what_it_is(self):
        """On the emitted SVG: a path is a fill of a named part or a line of a known
        class, never an anonymous shape."""
        paths = re.findall(r"<path ([^>]*)/>", self.svg)
        self.assertGreater(len(paths), 50)
        fills = drawn = 0
        for attrs in paths:
            if 'data-part=' in attrs:
                part = re.search(r'data-part="([^"]+)"', attrs).group(1)
                self.assertIn(part, self.scene["parts"], msg=f"a fill names unknown part {part}")
                fills += 1
                continue
            match = re.search(r'data-class="([^"]+)"', attrs)
            self.assertIsNotNone(match, msg=f"a path declares neither a part nor a class: {attrs[:80]}")
            self.assertIn(match.group(1), assemble.LINE_POLICY,
                          msg=f"a path declares unknown class {match.group(1)}")
            drawn += 1
        self.assertGreater(fills, 0)
        self.assertEqual(drawn, self.info["mark_paths"],
                         msg="the paths on the canvas are not the marks the build reported")

    def test_an_undeclared_class_is_refused(self):
        scene = dict(self.scene)
        marks = list(scene["sheet_marks"])
        marks.append(("A-hair-unknown", "A-hair-sheet", "suggestion", marks[0][3], marks[0][4]))
        scene["sheet_marks"] = tuple(marks)
        with self.assertRaises(ValueError):
            assemble.mark_geometry(scene)

    def test_an_undeclared_owner_is_refused(self):
        scene = dict(self.scene)
        marks = list(scene["sheet_marks"])
        marks.append(("A-hair-orphan", "A-nowhere", marks[0][2], marks[0][3], marks[0][4]))
        scene["sheet_marks"] = tuple(marks)
        with self.assertRaises(ValueError):
            assemble.mark_geometry(scene)


if __name__ == "__main__":
    unittest.main()
