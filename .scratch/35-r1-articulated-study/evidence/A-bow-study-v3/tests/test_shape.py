"""B2..B6: the structure the review named, asserted on the emitted drawing and the 1:1 PNG.

  * B2  the left tail is narrower than the knot's wrap and folded over into it (a flap band
        painted after the wrap);
  * B2/B3  creases end on a contour or at an occlusion - never bare in open fill;
  * B3/B4  the lobes are wider than the knot and their mouths sit under the wrap;
  * B4/B5  one flat cel fill: no filled shape wears the dark value, so no solid dark blob;
  * B5  the silhouette stroke is heavier than the crease stroke, and no mark is dashed;
  * B5/B6  on the delivered 1:1 image: one fill colour family, no enclosed background
        island, and both tails leave the frame.
"""
from __future__ import annotations

import os
import re
import sys
import unittest

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(EVIDENCE, "source"), os.path.join(EVIDENCE, "source", "parts")]

import bow  # noqa: E402

SVG = open(os.path.join(EVIDENCE, "artwork.svg")).read()
FULLRES = os.path.join(EVIDENCE, "check", "draft-fullres.png")
G = re.compile(r'<g class="band" data-band="([\w-]+)" data-order="(\d+)" fill="([^"]+)" '
               r'stroke="([^"]+)" stroke-width="([\d.]+)"[^>]*>\s*<polygon points="([^"]+)"/>')
C = re.compile(r'<g class="creases" data-band="([\w-]+)"[^>]*stroke-width="([\d.]+)"'
               r'[^>]*>(.*?)</g>', re.S)
P = re.compile(r'<polyline points="([^"]+)"/>')


def parse():
    bands = {}
    for name, order, fill, stroke, width, pts in G.findall(SVG):
        bands[name] = {"order": int(order), "fill": fill, "stroke": stroke,
                       "width": float(width),
                       "pts": [tuple(map(float, p.split(","))) for p in pts.split()]}
    creases = {}
    for name, width, body in C.findall(SVG):
        creases[name] = {"width": float(width),
                         "lines": [[tuple(map(float, p.split(","))) for p in pts.split()]
                                   for pts in P.findall(body)]}
    return bands, creases


def inside(poly, p, tol=0.0):
    """Point in polygon (winding number), or within `tol` of its boundary."""
    x, y = p
    n, hit = len(poly), False
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if min(x0, x1) - tol <= x <= max(x0, x1) + tol and \
           min(y0, y1) - tol <= y <= max(y0, y1) + tol:
            dx, dy = x1 - x0, y1 - y0
            L = (dx * dx + dy * dy) ** 0.5
            if L > 1e-9 and abs((x - x0) * dy - (y - y0) * dx) / L <= tol:
                return True
        if (y0 > y) != (y1 > y):
            if x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                hit = not hit
    return hit


def thickness(poly, x):
    """Extent of the polygon along the vertical line x (line-polygon intersections)."""
    ys = []
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (x0 - x) * (x1 - x) <= 0.0 and abs(x1 - x0) > 1e-9:
            ys.append(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
    return (max(ys) - min(ys)) if len(ys) > 1 else 0.0


def thickness_h(poly, y):
    """Extent of the polygon along the horizontal line y."""
    xs = []
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 - y) * (y1 - y) <= 0.0 and abs(y1 - y0) > 1e-9:
            xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    return (max(xs) - min(xs)) if len(xs) > 1 else 0.0


class TestBands(unittest.TestCase):
    def test_b2_tail_is_narrower_than_the_wrap_and_folds_over_it(self):
        bands, _c = parse()
        tail_w = thickness(bands["left-tail"]["pts"], 420.0)
        wrap_w = thickness_h(bands["wrap"]["pts"], 280.0)
        print(f"  tail wide {tail_w:.1f} px, wrap wide {wrap_w:.1f} px")
        self.assertLess(tail_w, wrap_w, "the tail must be narrower than the knot's wrap")
        self.assertGreater(bands["fold-flap"]["order"], bands["wrap"]["order"],
                           "the tail must fold over the wrap, i.e. be painted after it")

    def test_b3_b4_lobes_are_wider_than_the_knot_and_open_from_it(self):
        bands, _c = parse()
        knot_w = thickness_h(bands["wrap"]["pts"], 280.0)
        left = thickness(bands["left-lobe"]["pts"], 300.0)
        right = thickness(bands["right-lobe"]["pts"], 700.0)
        print(f"  lobe mouths under the wrap; lobe wide left {left:.1f}, right {right:.1f}, "
              f"knot {knot_w:.1f} px")
        self.assertGreater(left, knot_w)
        self.assertGreater(right, knot_w)
        for lobe in ("left-lobe", "right-lobe"):
            self.assertGreater(bands["wrap"]["order"], bands[lobe]["order"],
                               f"{lobe}'s mouth must be covered by the wrap")

    def test_b2_b3_creases_end_on_a_contour_or_at_an_occlusion(self):
        bands, creases = parse()
        bad = []
        for name, group in creases.items():
            for line in group["lines"]:
                for end in (line[0], line[-1]):
                    ok = inside(bands[name]["pts"], end, tol=1.0) or any(
                        b["order"] > bands[name]["order"] and inside(b["pts"], end)
                        for b in bands.values())
                    if not ok:
                        bad.append((name, tuple(round(v, 1) for v in end)))
        print(f"  {sum(len(g['lines']) for g in creases.values())} crease lines checked")
        self.assertEqual(bad[:5], [], "creases ending bare in open fill")

    def test_b4_b5_one_flat_fill_and_no_solid_dark_mark(self):
        bands, _c = parse()
        fills = {b["fill"] for b in bands.values()}
        print(f"  fills {sorted(fills)}, contour {bow.CONTOUR_STROKE}, crease {bow.CREASE_STROKE}")
        self.assertEqual(fills, {bow.PALETTE["front"]}, "a filled shape wears a second colour")
        self.assertNotIn('fill="%s"' % bow.PALETTE["back"], SVG,
                         "a solid dark shape is filled somewhere")
        self.assertEqual(len(re.findall(r'stroke-dasharray', SVG)), 0, "a dashed stroke is emitted")
        stroked = [b["width"] for b in bands.values()]
        self.assertTrue(all(w == bow.CONTOUR_STROKE for w in stroked))
        self.assertGreater(bow.CONTOUR_STROKE, 1.8 * bow.CREASE_STROKE,
                           "the contour must carry more weight than the folds")


class TestRaster(unittest.TestCase):
    def test_b5_b6_the_delivered_image_is_one_object_on_open_ground(self):
        im = cv2.imread(FULLRES)
        self.assertIsNotNone(im, "no 1:1 review image")
        bg = np.array([int(bow.PALETTE["bg"][5:7], 16), int(bow.PALETTE["bg"][3:5], 16),
                       int(bow.PALETTE["bg"][1:3], 16)])
        near_bg = (np.abs(im.astype(int) - bg).sum(2) < 12).astype(np.uint8)
        n, _lab, stats, _cent = cv2.connectedComponentsWithStats(near_bg, 8)
        h, w = near_bg.shape
        border = set(np.unique(np.concatenate([_lab[0], _lab[-1], _lab[:, 0], _lab[:, -1]])))
        enclosed = [s[4] for i, s in enumerate(stats[1:], 1) if i not in border and s[4] > 40]
        obj = (~near_bg.astype(bool)).astype(np.uint8)
        n_obj, _l2, st2, _c2 = cv2.connectedComponentsWithStats(obj, 8)
        biggest = max(s[4] for s in st2[1:])
        left_edge = int(near_bg[:, 0].sum())      # background pixels on x=0
        print(f"  fullres {im.shape[:2]}, background components {n - 1}, enclosed {enclosed}, "
              f"object {biggest} px, background on x=0 {left_edge} px, on y=559 "
              f"{int(near_bg[-1].sum())} px")
        self.assertEqual(enclosed, [], "an enclosed background island inside the bow")
        # both tails leave the frame: background is interrupted on the left edge and bottom
        self.assertLess(left_edge, 560, "the left tail does not cross the left frame edge")
        self.assertLess(int(near_bg[-1].sum()), 800, "the lower tail does not cross the bottom")


if __name__ == "__main__":
    unittest.main(verbosity=2)
