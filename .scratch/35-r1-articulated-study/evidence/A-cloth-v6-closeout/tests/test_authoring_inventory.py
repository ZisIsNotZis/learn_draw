"""The declared authoring inventory against the code (defect B3 of the v6 closeout).

`bodice.py` hand-typed three stations (C0, Cw, Eleft) but declared two: C0 was missing
from `authored_input_xy`, so `A-bodice-upper.authored` said 2 while the code had 3.
The previous budget test counted `part.authored` — a list a builder writes about
itself — so no test could have caught it.

These tests read the source text instead:
`test_every_hand_typed_pair_is_accounted_for` compares the AST-scanned pair literals of
each part module with `source/authored.py`'s inventory, and
`test_declared_authored_equals_the_landmarks` compares each built part's `authored` list
with the landmarks the inventory attributes to it.  A new hand-typed station fails the
first; a builder that under-reports fails the second.
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

from source import assemble, authored                            # noqa: E402
from source.parts.frames import Point, crop                       # noqa: E402


def _pair(value):
    """A declared authored station as (x, y); builders store pairs or Points."""
    if isinstance(value, Point):
        return (float(value.u), float(value.v))
    return tuple(float(c) for c in value)


class AuthoringInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts = assemble.build()["parts"]

    def test_every_hand_typed_pair_is_accounted_for(self):
        problems = authored.audit()
        self.assertEqual([], problems, msg="\n".join(problems))
        self.assertGreater(len(authored.MODULES), 5, msg="no part modules were scanned")

    def test_every_part_module_is_scanned(self):
        """A new part module cannot hide its hand-typed stations by being unknown."""
        on_disk = sorted(path.stem for path in authored.PARTS_DIR.glob("*.py")
                         if path.stem != "__init__")
        self.assertEqual(on_disk, sorted(authored.MODULES),
                         msg="the inventory and the part modules disagree")

    def test_declared_authored_equals_the_landmarks(self):
        """Each built part's `authored` list must be exactly its own landmarks.

        Names and count are compared strictly.  A declared point may be written in the
        crop-pixel frame, in plane coordinates or in the part's own local frame (the
        builders do all three), so each declared point must equal one of those three
        representations of its landmark -- not merely be a number of the right size.
        """
        for module, parts in authored.LANDMARKS.items():
            for part_name, entries in parts.items():
                part = self.parts[part_name]
                declared = {name: _pair(value) for name, value in part.authored}
                expected_names = {name for name, _value in entries}
                self.assertEqual(expected_names, set(declared),
                                 msg=f"{part_name} declares {sorted(declared)} but the code "
                                     f"hand-types {sorted(expected_names)} ({module}.py)")
                for name, value in entries:
                    plane = crop(*value)
                    candidates = {tuple(float(c) for c in value),
                                  (float(plane.u), float(plane.v))}
                    if hasattr(part, "frame"):          # a planar part has a local frame;
                        local = part.frame.to_local(plane)   # a sheet part's stations are
                        candidates.add((float(local.u), float(local.v)))  # already plane points
                    got = declared[name]
                    self.assertTrue(any(max(abs(a - b) for a, b in zip(got, candidate)) < 1e-6
                                        for candidate in candidates),
                                    msg=f"{part_name}.{name} declares {got}, which is none of the "
                                        f"representations of the landmark {tuple(value)}: {candidates}")

    def test_parts_without_landmarks_declare_none(self):
        with_landmarks = {name for parts in authored.LANDMARKS.values() for name in parts}
        for name, part in self.parts.items():
            if name in with_landmarks:
                continue
            self.assertEqual((), tuple(part.authored),
                             msg=f"{name} declares authored inputs but no landmark is attributed to it")

    def test_authoring_budget_per_shape(self):
        """No shape carries more hand-typed landmarks than the budget allows, counting the
        one shared relation as a station of each part that uses it."""
        for row in authored.table():
            if row["part"] == "-":
                continue
            budget = 5 if row["part"] in ("A-hair-sheet", "A-bow-ribbon") else 4
            self.assertLessEqual(row["own"] + row["shared"], budget,
                                 msg=f"{row['part']} carries {row['own']} landmarks plus "
                                     f"{row['shared']} shared stations")

    def test_the_table_is_reproducible(self):
        """The per-part table is printed from the source, so the README quotes a result."""
        for row in authored.table():
            self.assertIsInstance(row["own"], int)
            self.assertEqual(row["own"], len(row["landmarks"]))


if __name__ == "__main__":
    unittest.main()
