"""Discriminating semantic checks, not an art verdict."""
import importlib.util
import dataclasses

def value(x):
    if dataclasses.is_dataclass(x):
        return {f.name: value(getattr(x, f.name)) for f in dataclasses.fields(x)}
    if isinstance(x, dict): return {k: value(v) for k,v in x.items()}
    if isinstance(x, (tuple, list)): return tuple(value(v) for v in x)
    return x

import pathlib
import sys
import unittest

PACKAGE = pathlib.Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[3]
sys.path.insert(0, str(ROOT))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path / "__init__.py", submodule_search_locations=[str(path)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return importlib.import_module(name + ".full.figure")

class WaistContinuity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = load("baseline_source", PACKAGE / "baseline/source").build()
        cls.new = load("candidate_source", PACKAGE / "source").build()

    def test_all_geometry_depth_and_ownership_unchanged(self):
        self.assertEqual(self.old.keys(), self.new.keys())
        self.assertEqual(self.old["parts"].keys(), self.new["parts"].keys())
        allowed = {"A-bodice-upper", "A-derived-waist-band", "A-bodice-continuation"}
        for name, before in self.old["parts"].items():
            after = self.new["parts"][name]
            if name not in allowed:
                self.assertEqual(value(before), value(after), name)
            else:
                for key in before.__dict__:
                    if key not in ("fill", "edges"):
                        self.assertEqual(value(before.__dict__[key]), value(after.__dict__[key]), (name, key))
        self.assertEqual(value(self.old["sheet_marks"]), value(self.new["sheet_marks"]))
        self.assertEqual(value(self.old["field"]), value(self.new["field"]))

    def test_old_fails_new_same_cloth_section_semantics(self):
        old, new = self.old["parts"], self.new["parts"]
        self.assertNotEqual(old["A-derived-waist-band"].fill, old["A-bodice-upper"].fill)
        self.assertEqual(new["A-derived-waist-band"].fill, new["A-bodice-upper"].fill)
        for owner, kind, count in (("A-derived-waist-band", "fold_edge", 2), ("A-bodice-continuation", "contact", 1)):
            self.assertEqual(sum(e.type == kind for e in old[owner].edges), count)
            self.assertFalse(any(e.type == kind for e in new[owner].edges))
            self.assertEqual(value(new[owner].edges), value(tuple(e for e in old[owner].edges if e.type != kind)))

    def test_frozen_part_library(self):
        files = list((PACKAGE / "baseline/source/parts").glob("*.py"))
        self.assertTrue(files)
        for f in files:
            self.assertEqual(f.read_bytes(), (PACKAGE / "source/parts" / f.name).read_bytes())

if __name__ == "__main__":
    unittest.main()
