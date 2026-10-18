"""Where the ribbon crosses itself, the rear edge is BROKEN by depth - and the check bites.

The assertion is made on geometry, not on a drawing claim: every place two authored rail
segments cross in 2D and come from different visits of the same strip is found from the
strip itself, then two things are required of it - the two surfaces must be at least one
cloth thickness apart, and the rear rail must have no emitted stroke through that station.

`--no-depth-break` in the builder emits every stroke unbroken.  The same test run against
that build must FAIL; `negative_control()` records both counts in
`tests/negative-control-output.txt`.
"""
from __future__ import annotations

import os
import re
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(EVIDENCE, "source"), os.path.join(EVIDENCE, "source", "parts")]

import bow  # noqa: E402
import build as compiler  # noqa: E402

SVG = os.path.join(EVIDENCE, "artwork.svg")
RAIL = re.compile(r'<polyline class="rail" data-rail="(\w)" data-s0="([\d.]+)" '
                  r'data-s1="([\d.]+)" points="([^"]+)"')


def emitted_intervals(road=SVG):
    """{rail id: [(s0, s1), ...]} of the strokes that survived the depth test."""
    out = {}
    for rail, s0, s1, _pts in RAIL.findall(open(road).read()):
        out.setdefault(rail, []).append((float(s0), float(s1)))
    return out


def authored_segments(step=6):
    """Rail segments of the whole strip, subsampled, with each station's depth."""
    art = bow.build()
    st = art["strip"]
    segs = []
    for rail, v in (("L", 1.0), ("R", -1.0)):
        pts = np.array([st.point(i, v) for i in range(len(st.u))])
        for i in range(0, len(st.u) - step, step):
            a, b = pts[i], pts[i + step]
            segs.append({"rail": rail, "s": float((st.u[i] + st.u[i + step]) / 2),
                         "a": a, "b": b, "z": float((a[2] + b[2]) / 2)})
    return segs, art


def crossings(segs, min_visit_gap=0.12):
    """2D intersections between segments of visits far apart along the same strip."""
    found = []
    for i, s1 in enumerate(segs):
        for s2 in segs[i + 1:]:
            if abs(s1["s"] - s2["s"]) < min_visit_gap:
                continue                      # neighbouring stations, not a self-crossing
            x1, y1 = s1["a"][:2], s1["b"][:2]
            x2, y2 = s2["a"][:2], s2["b"][:2]
            d1 = y2 - x2
            d2 = y1 - x1
            den = (y1[0] - x1[0]) * (y2[1] - x2[1]) - (y1[1] - x1[1]) * (y2[0] - x2[0])
            if abs(den) < 1e-9:
                continue
            t = ((x2[0] - x1[0]) * (y2[1] - x2[1]) - (x2[1] - x1[1]) * (y2[0] - x2[0])) / den
            u = ((x2[0] - x1[0]) * (y1[1] - x1[1]) - (x2[1] - x1[1]) * (y1[0] - x1[0])) / den
            if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
                found.append((s1, s2, (x1[0] + t * d2[0], x1[1] + t * d2[1])))
    return found


def audit(road=SVG):
    """Returns (crossings audited, failures)."""
    segs, art = authored_segments()
    gap = art["thickness"]
    intervals = emitted_intervals(road)
    hits = crossings(segs)
    failures = []
    for s1, s2, pt in hits:
        rear, front = (s1, s2) if s1["z"] > s2["z"] else (s2, s1)
        if abs(s1["z"] - s2["z"]) < gap:
            failures.append(f"no depth break at ({pt[0]:.0f},{pt[1]:.0f}): "
                            f"|dz|={abs(s1['z'] - s2['z']):.1f} < {gap}")
        # The rear edge must be absent at the crossing: no emitted stroke of the rear rail
        # may run through the station where the two edges meet.  A stroke ending within two
        # stations of the crossing (about 6 px) has been broken there; one running past it
        # is drawn through.
        two_stations = 2.0 / 620.0
        drawn = any(min(rear["s"] - a, b - rear["s"]) > two_stations
                    for a, b in intervals.get(rear["rail"], [])
                    if a <= rear["s"] <= b)
        if drawn:
            failures.append(f"rear edge drawn through the crossing at "
                            f"({pt[0]:.0f},{pt[1]:.0f}) (rail {rear['rail']}, "
                            f"s={rear['s']:.3f}), with nothing painted over it")
    return hits, failures


class TestCrossingIsBrokenByDepth(unittest.TestCase):
    def test_the_ribbon_does_cross_itself(self):
        hits, _fail = audit()
        print(f"  audited {len(hits)} 2D self-crossings of the ribbon")
        self.assertGreaterEqual(len(hits), 2,
                                "no crossing found: the depth-break test would test nothing")

    def test_every_crossing_has_a_depth_break_and_a_broken_rear_edge(self):
        hits, failures = audit()
        for f in failures:
            print("  FAIL " + f)
        self.assertEqual(failures, [])


def negative_control():
    """The same audit against a build that emits every stroke unbroken."""
    healthy, bad = audit()
    mutated_path = os.path.join(EVIDENCE, "tests", "_negative-control.svg")
    res = compiler.resolve(break_depth=False)
    open(mutated_path, "w").write(compiler.svg(res))
    m_hits, m_bad = audit(mutated_path)
    os.remove(mutated_path)
    lines = [
        "crossing-break negative control (P37): the mechanism must be visible as a failure",
        f"real build   : {len(healthy)} crossings audited, {len(bad)} failures",
        f"mutation     : --no-depth-break, {len(m_hits)} crossings audited, {len(m_bad)} failures",
    ]
    if bad:
        lines.append("  real-build failures: " + "; ".join(bad))
    if m_bad:
        lines.append("  mutation failures (expected, this is the point):")
        lines += ["    " + f for f in m_bad[:6]]
    verdict = ("PASS: the mechanism is what makes the test pass"
               if not bad and m_bad else
               "FAIL: the mutation did not fail the audit")
    lines.append(verdict)
    out = os.path.join(HERE, "negative-control-output.txt")
    open(out, "w").write("\n".join(lines) + "\n")
    return not bad and bool(m_bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
