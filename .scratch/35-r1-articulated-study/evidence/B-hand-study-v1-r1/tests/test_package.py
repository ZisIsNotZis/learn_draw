"""The package is true, reference-free, and reproducible from its own source.

Four claims:
  * `manifest.json` / `manifest.sha256` verify over the real file set, and a dropped file is
    reported (the mutation);
  * the check bundle lists the 1:1 canvas image first, and it is the canvas' own size;
  * the build never reads a reference: no source file names one, no image library is imported,
    and a build run from another directory produces the same bytes;
  * two builds are byte-identical, and the delivered PNG is a fresh render of the delivered SVG
    through the documented command.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path[:0] = [os.path.join(EVIDENCE, "source")]

import geo  # noqa: E402

FORBIDDEN = ("cv2.", "Image.open", "imread", "image.jpg", "similarity.py", "a-measure-crop",
             "teacher-observations")


class TestManifest(unittest.TestCase):
    def test_manifest_verifies_over_the_real_file_set(self):
        proc = subprocess.run([sys.executable, os.path.join(EVIDENCE, "source", "manifest.py"),
                               "--check"], capture_output=True, text=True)
        print("  " + proc.stdout.strip().replace("\n", "\n  "))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_sha256sum_agrees_with_the_manifest(self):
        proc = subprocess.run(["sha256sum", "-c", "manifest.sha256"], cwd=EVIDENCE,
                              capture_output=True, text=True)
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        print(f"  sha256sum -c: {sum(1 for ln in lines if ln.endswith('OK'))}/{len(lines)} OK")

    def test_a_dropped_file_is_caught(self):
        """Mutation: remove one listed file in a copy of the package and require a failure."""
        tmp = tempfile.mkdtemp()
        dest = os.path.join(tmp, "pkg")
        shutil.copytree(EVIDENCE, dest)
        victim = os.path.join(dest, "artwork.svg")
        os.replace(victim, victim + ".moved")
        proc = subprocess.run([sys.executable, os.path.join(dest, "source", "manifest.py"),
                               "--check"], capture_output=True, text=True)
        shutil.rmtree(tmp)
        print("  mutation (artwork.svg removed):", proc.stdout.strip().splitlines()[:2])
        self.assertNotEqual(proc.returncode, 0, "a missing file did not fail the manifest")


class TestBundle(unittest.TestCase):
    def test_the_bundle_lists_the_1to1_image_first(self):
        report = os.path.join(EVIDENCE, "check", "report.txt")
        self.assertTrue(os.path.exists(report), "no check bundle")
        text = open(report).read()
        listed = [ln for ln in text.splitlines() if "/check/" in ln]
        self.assertTrue(listed, text)
        self.assertIn("draft-fullres.png", listed[0])
        self.assertIn("1:1", listed[0])
        import cv2
        im = cv2.imread(os.path.join(EVIDENCE, "check", "draft-fullres.png"))
        self.assertEqual(im.shape[:2], (geo.CANVAS[1], geo.CANVAS[0]),
                         "the first image is not at canvas size")
        print("  first bundle image:", listed[0].strip())


class TestNoReferenceAtRuntime(unittest.TestCase):
    def test_no_source_file_names_the_reference(self):
        offenders = []
        for root, _dirs, files in os.walk(os.path.join(EVIDENCE, "source")):
            for f in sorted(files):
                if not f.endswith(".py"):
                    continue
                path = os.path.join(root, f)
                text = open(path).read()
                for bad in FORBIDDEN:
                    if bad in text:
                        offenders.append(f"{os.path.relpath(path, EVIDENCE)}: {bad}")
                if "import cv2" in text or "from PIL" in text:
                    offenders.append(f"{os.path.relpath(path, EVIDENCE)}: image library")
        print(f"  source files scanned, offenders: {offenders}")
        self.assertEqual(offenders, [])

    def test_the_build_does_not_depend_on_where_it_runs(self):
        before = hashlib.sha256(
            open(os.path.join(EVIDENCE, "artwork.svg"), "rb").read()).hexdigest()
        tmp = tempfile.mkdtemp()
        out = os.path.join(tmp, "b.svg")
        proc = subprocess.run([sys.executable, os.path.join(EVIDENCE, "source", "build.py"),
                               "--out", out], cwd=tmp, capture_output=True, text=True)
        after = (hashlib.sha256(open(out, "rb").read()).hexdigest()
                 if proc.returncode == 0 else None)
        shutil.rmtree(tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(before, after, "the build changed when run outside the evidence dir")


class TestReproducible(unittest.TestCase):
    def test_two_builds_are_byte_identical(self):
        outs = []
        for _ in range(2):
            d = tempfile.mkdtemp()
            out = os.path.join(d, "artwork.svg")
            subprocess.run([sys.executable, os.path.join(EVIDENCE, "source", "build.py"),
                            "--out", out], check=True, capture_output=True)
            outs.append(open(out, "rb").read())
            shutil.rmtree(d)
        self.assertEqual(outs[0], outs[1], "the build is not deterministic")
        delivered = open(os.path.join(EVIDENCE, "artwork.svg"), "rb").read()
        self.assertEqual(outs[0], delivered, "the delivered SVG is not a build of this source")
        print(f"  two builds byte-identical, and equal to the delivered svg "
              f"(sha256 {hashlib.sha256(delivered).hexdigest()[:16]})")

    def test_the_delivered_png_is_a_fresh_build_byte_for_byte(self):
        d = tempfile.mkdtemp()
        fresh = os.path.join(d, "artwork.png")
        subprocess.run([os.path.join(ROOT, "scripts", "draw"), "render",
                        os.path.join(EVIDENCE, "artwork.svg"), "-o", fresh],
                       check=True, capture_output=True)
        a = open(fresh, "rb").read()
        b = open(os.path.join(EVIDENCE, "artwork.png"), "rb").read()
        shutil.rmtree(d)
        self.assertEqual(a, b, "the delivered PNG is not byte-for-byte the render of the "
                               "delivered SVG through scripts/draw render")
        import cv2
        im = cv2.imdecode(__import__("numpy").frombuffer(a, __import__("numpy").uint8), 1)
        self.assertEqual(im.shape[:2], (geo.CANVAS[1], geo.CANVAS[0]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
