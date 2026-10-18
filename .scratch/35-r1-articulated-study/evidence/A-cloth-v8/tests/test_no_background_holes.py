"""No background-coloured region may sit enclosed by the drawing.

The reference has no background gap inside a hair mass (a-art-direction-brief.md, the
hair facts), and the v6 render had two: 1019 px2 under the left hair mass and 17 px2
where the sheet crosses in front of the face.  A drawing that leaves background islands
inside its own silhouette reads as a hole in the object, so this is measured on the
delivered raster, not on the vector model.

The rule, stated so it can be checked from the image alone:

1. A pixel is *background* when every channel is within `TOLERANCE` of the composition
   field's fill (`assemble.BACKGROUND`, #78a49b).  The field is one flat rectangle, so a
   tight tolerance is enough and it does not accept a neighbouring fill.
2. Background pixels form 4-connected components.
3. A component that touches the image border is the page's own background and is
   ignored; any other component of at least `MIN_HOLE_PX` pixels is enclosed by the
   drawing and fails the test.

`test_the_rule_fails_on_the_v6_render` runs the same function against the previous
package's delivered render and requires it to report the two known islands, so the rule
is demonstrated to be able to fail rather than passing on any input.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
ROOT = HERE.parents[4]
for path in (str(ROOT), str(EVIDENCE)):
    if path not in sys.path:
        sys.path.insert(0, path)

from source import assemble                                       # noqa: E402

TOLERANCE = 6      # per channel, against assemble.BACKGROUND
MIN_HOLE_PX = 4    # a 4-connected island smaller than this is antialiasing, not a hole
DELIVERED = EVIDENCE / "artwork-a.png"
V6_DELIVERED = EVIDENCE.parent / "A-cloth-v6-closeout" / "artwork-a.png"


def background_components(pixels: np.ndarray) -> list[tuple[int, tuple[int, int, int, int]]]:
    """Every 4-connected background component that does not touch the image border."""
    height, width, _ = pixels.shape
    background = np.array([int(assemble.BACKGROUND[1:3], 16),
                           int(assemble.BACKGROUND[3:5], 16),
                           int(assemble.BACKGROUND[5:7], 16)])
    mask = np.abs(pixels.astype(int) - background).max(axis=2) <= TOLERANCE
    reachable = np.zeros((height, width), dtype=bool)
    stack = [(y, x) for x in range(width) for y in (0, height - 1) if mask[y, x]]
    stack += [(y, x) for y in range(height) for x in (0, width - 1) if mask[y, x]]
    for y, x in stack:
        reachable[y, x] = True
    while stack:
        y, x = stack.pop()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not reachable[ny, nx]:
                reachable[ny, nx] = True
                stack.append((ny, nx))
    enclosed = mask & ~reachable
    found = []
    seen = np.zeros((height, width), dtype=bool)
    for y, x in zip(*np.nonzero(enclosed)):
        if seen[y, x]:
            continue
        seen[y, x] = True
        stack, component = [(y, x)], []
        while stack:
            cy, cx = stack.pop()
            component.append((cy, cx))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < height and 0 <= nx < width and enclosed[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(component) >= MIN_HOLE_PX:
            ys = [point[0] for point in component]
            xs = [point[1] for point in component]
            found.append((len(component), (min(xs), min(ys),
                                           max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)))
    return sorted(found, reverse=True)


def holes_in(path: Path):
    image = Image.open(path).convert("RGB")
    return background_components(np.asarray(image)), image.size


class BackgroundHoleTest(unittest.TestCase):
    def test_the_delivered_render_has_no_enclosed_background(self):
        """Measured on the delivered 1:1 raster, with the rule and tolerance above."""
        self.assertTrue(DELIVERED.exists(), msg=f"missing delivered render {DELIVERED}")
        holes, size = holes_in(DELIVERED)
        print(f"\n{size[0]}x{size[1]} {DELIVERED.name}: {len(holes)} enclosed background "
              f"component(s) at tolerance {TOLERANCE}, minimum {MIN_HOLE_PX} px"
              + ("" if not holes else f": {holes}"))
        self.assertEqual([], holes, msg=f"background islands inside the drawing: {holes}")

    @unittest.skipUnless(V6_DELIVERED.exists(), "the v6-closeout render is not beside this package")
    def test_the_rule_fails_on_the_v6_render(self):
        """The same function must find the two islands the v6 render really had."""
        holes, _size = holes_in(V6_DELIVERED)
        print(f"\nrule applied to {V6_DELIVERED.name}: {holes}")
        self.assertGreaterEqual(len(holes), 2,
                                msg=f"the rule cannot see the v6 holes, so it proves nothing: {holes}")
        self.assertGreater(holes[0][0], 500,
                           msg=f"the large v6 island is not reported at its measured size: {holes[0]}")
        self.assertGreaterEqual(holes[-1][0], MIN_HOLE_PX,
                                msg=f"the small v6 island is not reported: {holes}")


if __name__ == "__main__":
    unittest.main()
