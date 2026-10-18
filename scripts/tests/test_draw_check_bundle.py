"""The check bundle must hand a reviewer a 1:1 drawing, never only a downscaled preview.

A review once received a 1350x640 sheet as a 256x121 thumbnail and could not judge digit
separation, so these tests bind the bundle's first listed drawing image to the artwork's own
pixel size — on both the reference-free and the with-reference path.

Fixtures are PNG artworks of an exact pixel size, so the bundle is exercised without a renderer.
Only cmd_check's bundling is invoked (output goes to a temp dir), never a real evidence bundle.
"""
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest

import cv2
import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import draw

WIDTH, HEIGHT = 700, 340  # wider than --pane, so any downscale is visible as a size change


def write_fixture(path, ink=True):
    """A flat-backdrop artwork of exactly WIDTH x HEIGHT (the reference reads the same way)."""
    img = np.full((HEIGHT, WIDTH, 3), 210, np.uint8)
    if ink:
        cv2.rectangle(img, (WIDTH // 5, HEIGHT // 5), (WIDTH // 2, HEIGHT // 2), (40, 60, 90), -1)
        cv2.line(img, (WIDTH // 3, HEIGHT // 2), (WIDTH * 2 // 3, HEIGHT * 3 // 4), (10, 10, 10), 3)
    cv2.imwrite(str(path), img)
    return str(path)


def listed_images(report):
    """(path, description) pairs of report.txt's image list, in the order a reviewer reads them."""
    rows, inside = [], False
    for line in Path(report).read_text().splitlines():
        if line.startswith("images ("):
            inside = True
            continue
        if inside:
            if not line.startswith("  "):
                break
            path, _, what = line.strip().partition("  -- ")
            rows.append((path, what))
    return rows


class CheckBundleFullResTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pane = 256

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self, art, ref=None):
        outdir = str(self.root / "check")
        draw.cmd_check(SimpleNamespace(art=art, ref=ref, outdir=outdir, resolver=None,
                                       regions=3, pane=self.pane, zoom_max=3.0))
        return outdir, os.path.join(outdir, "report.txt")

    def assert_primary_drawing_is_1to1(self, outdir, report):
        rows = listed_images(report)
        self.assertGreaterEqual(len(rows), 1, "bundle report lists no drawing image")
        first_path, first_what = rows[0]
        self.assertIn("1:1", first_what,
                      f"first listed drawing image does not declare itself 1:1: {first_what!r}")
        first = cv2.imread(first_path)
        self.assertIsNotNone(first, f"missing first listed drawing image {first_path}")
        self.assertEqual((first.shape[1], first.shape[0]), (WIDTH, HEIGHT),
                         "the first listed drawing image was downscaled from the artwork")

    def test_reference_free_bundle_primary_image_keeps_artwork_size(self):
        art = write_fixture(self.root / "art.png")
        outdir, report = self.run_check(art)
        self.assert_primary_drawing_is_1to1(outdir, report)
        # the bounded preview survives as an extra file and is labelled as a preview
        preview = cv2.imread(os.path.join(outdir, "draft.png"))
        self.assertIsNotNone(preview, "the bounded preview disappeared")
        self.assertEqual(preview.shape[1], self.pane)
        descriptions = [what for _, what in listed_images(report)]
        self.assertTrue(any("preview" in what for what in descriptions), descriptions)

    def test_with_reference_bundle_primary_image_keeps_artwork_size(self):
        art = write_fixture(self.root / "art.png", ink=False)
        ref = write_fixture(self.root / "ref.png")
        outdir, report = self.run_check(art, ref=ref)
        self.assert_primary_drawing_is_1to1(outdir, report)
        # existing bundle layout and region crops are unchanged
        self.assertTrue(os.path.exists(os.path.join(outdir, "side-by-side.png")))
        paths = {path for path, _ in listed_images(report)}
        for i in (1, 2, 3):
            self.assertIn(os.path.join(outdir, f"region-{i}.png"), paths,
                          f"region crop {i} disappeared from the bundle")
        if draw.load_baseline():
            self.assertIn("vs recorded best", Path(report).read_text(),
                          "the ratchet line disappeared from the report")

    def test_report_protocol_names_the_1to1_image_for_detail(self):
        art = write_fixture(self.root / "art.png")
        _, report = self.run_check(art)
        text = Path(report).read_text()
        self.assertIn("draft-fullres.png", text)
        self.assertIn("Judge detail only on the 1:1 images", text)
        self.assertIn("never line weight or separation", text)


if __name__ == "__main__":
    unittest.main()
