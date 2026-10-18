"""Each triangle wears its own face's colour, and the drawing is reproducible from source.

Two claims, each falsifiable:
  * every emitted triangle's colour agrees with the sign of its *own* projected winding - a
    triangle whose winding points away from the camera wears the ribbon's back colour;
  * a build is byte-identical when repeated, and the delivered PNG is a fresh build of the
    delivered SVG through the documented render command.
"""
from __future__ import annotations

import os
import re
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

POLY = re.compile(r'<polygon class="face-(\w+)"[^>]*points="([^"]+)"[^>]*fill="([^"]+)"')


def signed_area(P):
    return 0.5 * ((P[1][0] - P[0][0]) * (P[2][1] - P[0][1]) -
                  (P[2][0] - P[0][0]) * (P[1][1] - P[0][1]))


class TestFillFollowsWinding(unittest.TestCase):
    def test_every_triangle_wears_its_own_winding(self):
        text = open(os.path.join(EVIDENCE, "artwork.svg")).read()
        rows = POLY.findall(text)
        self.assertGreater(len(rows), 1000)
        bad = []
        for face, pts, fill in rows:
            P = [tuple(map(float, p.split(","))) for p in pts.split()]
            forward = signed_area(P) < 0          # y grows down
            if forward != (face == "front"):
                bad.append((face, fill, round(signed_area(P), 1)))
            if fill != (bow.PALETTE["front"] if forward else bow.PALETTE["back"]):
                bad.append(("colour", fill))
        print(f"  {len(rows)} triangles checked; {len(bad)} disagree with their winding")
        self.assertEqual(bad[:5], [])

    def test_both_faces_are_actually_decided(self):
        """A rule with one possible answer is not a rule: the drawing must use both faces."""
        text = open(os.path.join(EVIDENCE, "artwork.svg")).read()
        faces = [f for f, _p, _c in POLY.findall(text)]
        n_back = faces.count("back")
        print(f"  front faces {len(faces) - n_back}, back faces {n_back}")
        self.assertGreater(n_back, 0, "no triangle turns its back: the two-sided rule is untested")
        self.assertGreater(len(faces) - n_back, n_back, "the back must stay the minority face")


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

    def test_the_delivered_png_is_a_fresh_build(self):
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
