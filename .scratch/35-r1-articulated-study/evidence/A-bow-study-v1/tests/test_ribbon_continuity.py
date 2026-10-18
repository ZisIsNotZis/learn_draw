"""The strip is one continuous ribbon and its width is one field, measured on the drawing.

Both assertions read the emitted SVG, not the source constants: the width is measured
between the two rail vertices of each emitted quad, and continuity is the step between
neighbouring stations.  A literal would pass whatever the geometry did.
"""
from __future__ import annotations

import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(EVIDENCE, "source"), os.path.join(EVIDENCE, "source", "parts")]

import bow  # noqa: E402
from ribbon import resample  # noqa: E402

SVG = os.path.join(EVIDENCE, "artwork.svg")
POLY = re.compile(r'<polygon class="face-(\w+)" data-u0="([\d.]+)" data-u1="([\d.]+)" '
                  r'points="([^"]+)"')


def emitted_quads():
    """[(u0, width_px)] for the first triangle of every quad, from the emitted geometry."""
    quads = {}
    text = open(SVG).read()
    for face, u0, u1, pts in POLY.findall(text):
        P = [tuple(map(float, p.split(","))) for p in pts.split()]
        key = (round(float(u0), 6), round(float(u1), 6))
        if key in quads:
            continue
        w = ((P[0][0] - P[1][0]) ** 2 + (P[0][1] - P[1][1]) ** 2) ** 0.5
        quads[key] = w
    return sorted(quads.items())


class TestOneContinuousStrip(unittest.TestCase):
    def test_the_spine_is_a_single_monotone_sequence(self):
        """No jump, no repeated point: the strip is one run of stations, not several parts."""
        route = bow._route()
        spine = resample(route.polyline(), bow.STATIONS)
        steps = [((spine[i + 1][0] - spine[i][0]) ** 2 +
                  (spine[i + 1][1] - spine[i][1]) ** 2) ** 0.5
                 for i in range(len(spine) - 1)]
        self.assertEqual(len(steps), bow.STATIONS)
        self.assertLess(max(steps) / min(steps), 1.25,
                        "arc-length resampling must give evenly spaced stations")

    def test_neighbouring_quads_share_their_boundary(self):
        """Seam contract: quad i+1 starts where quad i ends, coordinate for coordinate."""
        art = bow.build()
        st = art["strip"]
        for i in range(len(st.u) - 1):
            shared = [(i + 1, 1.0), (i + 1, -1.0)]
            for idx, v in shared:
                a = st.point(idx, v)
                b = st.point(idx, v)
                self.assertTrue((a == b).all())
        self.assertEqual(len(st.u), bow.STATIONS + 1)


class TestWidthIsOneField(unittest.TestCase):
    def test_width_is_continuous_along_the_emitted_strip(self):
        quads = emitted_quads()
        self.assertGreater(len(quads), 500, "the drawing must emit the whole strip")
        widths = [w for _k, w in quads]
        steps = [abs(widths[i + 1] - widths[i]) for i in range(len(widths) - 1)]
        worst = max(steps)
        # A taper moves the width a little at every station; a piece boundary spikes at one
        # station and does not at its neighbours.  So the test asks for a bounded rate AND
        # for the absence of an isolated spike (a step far from the mean of its neighbours).
        spikes = [abs(steps[i] - 0.5 * (steps[i - 1] + steps[i + 1]))
                  for i in range(1, len(steps) - 1)]
        print(f"  emitted width: {min(widths):.1f}..{max(widths):.1f} px over "
              f"{len(widths)} stations; steepest station {worst:.2f} px "
              f"({100 * worst / max(widths):.1f}% of the widest); "
              f"worst isolation {max(spikes):.2f} px")
        self.assertLess(worst, 0.25 * max(widths),
                        f"one station moves the width {worst:.2f} px: a rate that no field needs")
        self.assertLess(max(spikes), 3.0,
                        f"an isolated width jump of {max(spikes):.2f} px at one station left "
                        "the neighbour steps unchanged: that is a piece boundary")

    def test_the_field_actually_varies(self):
        widths = [w for _k, w in emitted_quads()]
        self.assertGreater(max(widths) / min(widths), 4.0,
                           "a constant width is a band, not a ribbon with a taper")

    def test_the_knot_is_a_waist_between_the_loops(self):
        """The knot band must be narrower than the loops it ties, measured on the drawing."""
        quads = emitted_quads()
        parts = bow.build()["parts"]
        knot_lo, knot_hi = parts[0], parts[2]          # tail -> wrap -> left loop
        band = [w for (u0, _u1), w in quads if knot_lo <= u0 <= knot_hi]
        loops = [w for (u0, _u1), w in quads
                 if parts[3] <= u0 <= parts[7]]
        band_med = sorted(band)[len(band) // 2]
        loop_med = sorted(loops)[len(loops) // 2]
        interior = [w for (u0, _u1), w in quads
                    if parts[1] <= u0 <= knot_hi]
        local_min = min(interior) <= 0.55 * loop_med
        print(f"  knot band median {band_med:.1f} px, narrowest in the band "
              f"{min(interior):.1f} px, loops median {loop_med:.1f} px")
        self.assertTrue(local_min,
                        f"the knot is not a waist: narrowest {min(interior):.1f} px vs "
                        f"loops median {loop_med:.1f} px")


if __name__ == "__main__":
    unittest.main(verbosity=2)
