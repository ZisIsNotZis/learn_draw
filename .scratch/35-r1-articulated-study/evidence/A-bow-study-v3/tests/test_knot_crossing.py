"""B1: the knot wraps and crosses - a later band's edge runs over an earlier band's edge.

Read off the emitted drawing, not the source: the wrap's outline is intersected with the
outlines of both lobes and the left tail, and the wrap must be painted after each of them.
The mutation `--no-occlusion` paints front to back; the same assertion must then FAIL, which
is what makes this a test of the crossing rather than of the file existing.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(EVIDENCE, "source"), os.path.join(EVIDENCE, "source", "parts")]

import bow  # noqa: E402
import build as compiler  # noqa: E402

G = re.compile(r'<g class="band" data-band="([\w-]+)" data-order="(\d+)"[^>]*>\s*'
               r'<polygon points="([^"]+)"/>')


def bands(text):
    out = {}
    for name, order, pts in G.findall(text):
        out[name] = {"order": int(order),
                     "pts": [tuple(map(float, p.split(","))) for p in pts.split()]}
    return out


def crosses(a, b):
    """Number of proper intersections between two closed polygons' edges."""
    def seg(p1, p2, p3, p4):
        d = ((p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0]))
        if abs(d) < 1e-12:
            return False
        t = ((p1[0] - p3[0]) * (p3[1] - p4[1]) - (p1[1] - p3[1]) * (p3[0] - p4[0])) / d
        u = ((p1[0] - p3[0]) * (p1[1] - p2[1]) - (p1[1] - p3[1]) * (p1[0] - p2[0])) / d
        return 0.0 < t < 1.0 and 0.0 < u < 1.0
    n = 0
    for i in range(len(a)):
        p1, p2 = a[i], a[(i + 1) % len(a)]
        for j in range(len(b)):
            if seg(p1, p2, b[j], b[(j + 1) % len(b)]):
                n += 1
    return n


def audit(text, need=2):
    bs = bands(text)
    w = bs["wrap"]
    failures = []
    for under in ("left-lobe", "right-lobe", "left-tail"):
        n = crosses(w["pts"], bs[under]["pts"])
        if n < need:
            failures.append(f"wrap outline crosses {under} {n}x")
        if w["order"] <= bs[under]["order"]:
            failures.append(f"wrap painted before {under}: no edge can pass over it")
    return failures


class TestKnotCrosses(unittest.TestCase):
    def test_the_wrap_runs_over_the_lobes_and_the_tail(self):
        failures = audit(open(os.path.join(EVIDENCE, "artwork.svg")).read())
        for f in failures:
            print("  FAIL " + f)
        self.assertEqual(failures, [])

    def test_the_mutation_without_paint_order_fails_the_same_audit(self):
        text = compiler.svg(bow.build(), occlusion=False)
        self.assertTrue(audit(text), "without paint order the crossing must disappear")
        print("  mutation --no-occlusion: crossing audit fails as required")


if __name__ == "__main__":
    unittest.main(verbosity=2)
