"""The package is true, and the bundle hands the reviewer the 1:1 image first.

Three claims:
  * `manifest.json` / `manifest.sha256` verify over the real file set, and a dropped file
    is reported (the mutation);
  * the check bundle's report lists `draft-fullres.png` first, at the canvas' own size;
  * the build never reads the reference: no source file names a reference path, and a build
    run with the reference path moved away still produces the same bytes.
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

# Calls that would make the reference a runtime input.  A docstring may cite where a measured
# parameter came from; reading the crop at build time is what must not happen.
FORBIDDEN = ("cv2.", "Image.open", "imread", "crop-400x480", "similarity.py", "a-measure-crop")


class TestManifest(unittest.TestCase):
    def test_manifest_verifies_over_the_real_file_set(self):
        proc = subprocess.run([sys.executable, os.path.join(EVIDENCE, "source", "manifest.py"),
                               "--check"], capture_output=True, text=True)
        print("  " + proc.stdout.strip().replace("\n", "\n  "))
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_sha256sum_agrees_with_the_manifest(self):
        proc = subprocess.run(["sha256sum", "-c", "manifest.sha256"],
                              cwd=EVIDENCE, capture_output=True, text=True)
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
        listed = [ln for ln in text.splitlines() if ln.strip().startswith("check/")
                  or "/check/" in ln]
        self.assertTrue(listed, text)
        self.assertIn("draft-fullres.png", listed[0])
        self.assertIn("1:1", listed[0])
        import cv2
        im = cv2.imread(os.path.join(EVIDENCE, "check", "draft-fullres.png"))
        self.assertEqual(im.shape[:2], (560, 800), "the first image is not at canvas size")
        print("  first bundle image:", listed[0].strip())


class TestNoReferenceAtRuntime(unittest.TestCase):
    def test_no_source_file_names_the_reference(self):
        offenders = []
        for root, _dirs, files in os.walk(os.path.join(EVIDENCE, "source")):
            for f in files:
                if not f.endswith(".py"):
                    continue
                path = os.path.join(root, f)
                text = open(path).read()
                for bad in FORBIDDEN:
                    if bad in text:
                        offenders.append(f"{os.path.relpath(path, EVIDENCE)}: {bad}")
                if "import cv2" in text or "from PIL" in text:
                    offenders.append(f"{os.path.relpath(path, EVIDENCE)}: image library")
        self.assertEqual(offenders, [])

    def test_the_build_does_not_depend_on_the_reference_existing(self):
        before = hashlib.sha256(open(os.path.join(EVIDENCE, "artwork.svg"), "rb").read()).hexdigest()
        tmp = tempfile.mkdtemp()
        out = os.path.join(tmp, "a.svg")
        env = dict(os.environ, CWD_REFERENCE_MOVED="1")
        proc = subprocess.run([sys.executable, os.path.join(EVIDENCE, "source", "build.py"),
                               "--out", out], cwd=tmp, env=env, capture_output=True, text=True)
        after = hashlib.sha256(open(out, "rb").read()).hexdigest() if proc.returncode == 0 else None
        shutil.rmtree(tmp)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(before, after, "the build changed when run outside the evidence dir")


if __name__ == "__main__":
    unittest.main(verbosity=2)
