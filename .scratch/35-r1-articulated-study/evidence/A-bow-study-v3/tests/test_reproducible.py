"""The drawing is reproducible from this source, and the delivered PNG is a fresh render.

Two claims: two builds are byte-identical and equal to the delivered `artwork.svg`; and the
delivered `artwork.png` is the documented render of the delivered SVG, pixel for pixel.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path[:0] = [os.path.join(EVIDENCE, "source"), os.path.join(EVIDENCE, "source", "parts")]

import bow  # noqa: E402


class TestReproducible(unittest.TestCase):
    def test_two_builds_are_byte_identical_and_match_the_delivered_svg(self):
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
        print(f"  artwork.svg sha256 {__import__('hashlib').sha256(delivered).hexdigest()[:16]}…")

    def test_the_delivered_png_is_a_fresh_render(self):
        d = tempfile.mkdtemp()
        fresh = os.path.join(d, "artwork.png")
        subprocess.run([os.path.join(ROOT, "scripts", "draw"), "render",
                        os.path.join(EVIDENCE, "artwork.svg"), "-o", fresh],
                       check=True, capture_output=True)
        import cv2
        a = cv2.imread(fresh)
        b = cv2.imread(os.path.join(EVIDENCE, "artwork.png"))
        shutil.rmtree(d)
        self.assertIsNotNone(a)
        self.assertEqual(a.shape, (bow.CANVAS[1], bow.CANVAS[0], 3))
        self.assertLess(int(abs(a.astype(int) - b.astype(int)).max()), 1,
                        "the delivered PNG is not the render of the delivered SVG")


if __name__ == "__main__":
    unittest.main(verbosity=2)
