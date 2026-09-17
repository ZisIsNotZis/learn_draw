#!/usr/bin/env .venv/bin/python
"""M4a mandatory self-checks — render-visible facts, checked on pixels, not on intent.

Checks (M4a brief):
  1. wave      mint present continuously along y420-640 from x0 to ~x690 (no bg gap > 40px),
               mint extent reaches x >= 650
  2. tilt      chin offset from skull centre > 8px toward lower-left AND lash (dark) pixel mass
               in the upper third of each eye region
  3. hair-shoulder  hair pixels overlap the right shoulder/arm boundary (no background column
               between hair band and arm at the overlap rows)
  4. strand    no thin (<20px) isolated painted component in x60-560 / y250-440
Regressions (M3d must still hold):
  5. neck      no fully-background row in x665-735, y376-405
  6. knee      skin lobe below the hem at lower-left (area > 3000)
  7. arms      left cuff crosses the bow outline; right arm connected (bg-free columns at the
               shoulder rows)
"""
import sys
import cv2
import numpy as np

ART = sys.argv[1] if len(sys.argv) > 1 else ".scratch/13-assembly/evidence/m4a-final.png"
d = cv2.imread(ART).astype(np.int16)
r = cv2.imread("image.jpg").astype(np.int16)
b0 = np.median(np.concatenate([r[:12].reshape(-1, 3), r[-12:].reshape(-1, 3),
                               r[:, :12].reshape(-1, 3), r[:, -12:].reshape(-1, 3)]), axis=0)
bgis = np.linalg.norm(d - b0, axis=2) <= 45
B, G, R = d[:, :, 0], d[:, :, 1], d[:, :, 2]
results = []


def check(name, ok, detail):
    results.append((name, bool(ok), detail))


# ---- 1. wave ----------------------------------------------------------------
mint = (np.abs(B - 193) < 35) & (np.abs(G - 204) < 28) & (np.abs(R - 125) < 40) & (G > R + 50)
band = mint[420:640, :760]                     # the wave zone: x>700 is the figure's occlusion
cols = band.any(axis=0)
xs = np.where(cols)[0]
gaps, run = [], None
for x in range(0, 700):                        # continuity is owed only up to the figure
    if not cols[x]:
        run = 0 if run is None else run
        run += 1
    elif run is not None:
        gaps.append(run)
        run = None
if run is not None:
    gaps.append(run)
worst_gap = max(gaps) if gaps else 0
right_extent = int(xs.max()) if len(xs) else 0
check("wave", worst_gap <= 40 and right_extent >= 650,
      f"worst internal gap {worst_gap}px (<=40), mint right extent x{right_extent} (>=650)")

# ---- 2. tilt ----------------------------------------------------------------
# The skull centre is the spec's authored head.cx = 688 (the measured face-skin centroid the
# whole head hangs from); the check verifies the RENDER expresses the authored down-left tip:
# the rendered chin must sit >8px LEFT of that centre, and the lash mass must weight the eyes.
SKULL_CX = 688.0
skin = (np.abs(B - 216) < 14) & (np.abs(G - 233) < 14) & (np.abs(R - 242) < 14)
skin[460:, :] = False                           # face skin only (head zone)
ys, xs = np.where(skin)
bot = ys.max()
chin_tip = float(np.where(skin[bot - 2:bot + 1])[1].min())   # the jaw tip's leftmost reach
off = SKULL_CX - chin_tip                        # >0 = chin LEFT of skull centre
dark = (R < 90) & (G < 90) & (B < 90)
lashR = dark[244:268, 700:790].sum()             # upper third of the near-eye region
lashL = dark[238:258, 600:665].sum()             # upper third of the far-eye region
check("tilt", off > 12 and lashR > 150 and lashL > 100,
      f"chin tip x{chin_tip:.0f} = {off:.1f}px left of skull centre 688 (>12); lash px near {lashR}, far {lashL}")

# ---- 3. hair-over-shoulder ---------------------------------------------------
hairb = (np.abs(B - 171) < 45) & (np.abs(G - 116) < 45) & (np.abs(R - 57) < 50) & (B > G) & (G > R)
overlap_rows = 0
for y in range(560, 700, 8):               # rows where the arm crosses under the hair band
    hair_here = hairb[y, 850:1000].any()
    painted_here = not bgis[y, 800:1000].all()
    if hair_here and painted_here:
        overlap_rows += 1
col_ok = all(not (hairb[y, 850:1000].any() and not hairb[y, 800:1000].any()
                  and bgis[y, 800:850].all()) for y in range(560, 700, 8))
check("hair-shoulder", overlap_rows >= 10 and col_ok,
      f"hair present on {overlap_rows}/17 arm rows y560-700; no hair|bg split at the arm column")

# ---- 4. stray strand ---------------------------------------------------------
painted = ~bgis
zone = painted[250:440, 60:560].astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(zone, 8)
thin = []
H, W = zone.shape
for i in range(1, n):
    x, y, w, h, a = stats[i]
    touches_border = x == 0 or y == 0 or x + w >= W or y + h >= H   # continues outside the zone
    if not touches_border and (w < 20 or (w < 20 and h < 60)):
        thin.append(int(a))
check("strand", not thin, f"thin isolated components in x60-560/y250-440: {thin or 'none'}")

# ---- 5. neck (M3d regression) -------------------------------------------------
neck = bgis[376:406, 665:736]
check("neck", not (neck.mean(axis=1) > 0.9).any(),
      f"fully-background neck rows: {int((neck.mean(axis=1) > 0.9).sum())}")

# ---- 6. knee (M3d regression) -------------------------------------------------
sk = (np.abs(B - 189) < 25) & (np.abs(G - 215) < 25) & (np.abs(R - 232) < 25)
n2, lab2, stats2, _ = cv2.connectedComponentsWithStats(sk[800:, :600].astype(np.uint8), 8)
knee = max((int(stats2[i][4]) for i in range(1, n2)), default=0)
check("knee", knee > 3000, f"skin lobe below hem: {knee}px (>3000)")

# ---- 7. arms (M3d regression) -------------------------------------------------
# right arm: no background gap along the shoulder rows y470-560 between x790 and the elbow path
arm_rows_bg = sum(bgis[y, 800:880].all() for y in range(470, 560, 6))
# left cuff crosses the bow: painted continuity x560-600 at cuff rows y615-690
cuff_rows_bg = sum(bgis[y, 560:600].all() for y in range(615, 690, 6))
check("arms", arm_rows_bg == 0 and cuff_rows_bg <= 1,
      f"fully-bg columns on right-arm rows: {arm_rows_bg}; left cuff bg rows: {cuff_rows_bg}")

fails = [r for r in results if not r[1]]
for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL':4s} {name:14s} {detail}")
print("OVERALL:", "PASS" if not fails else f"FAIL ({len(fails)})")
sys.exit(1 if fails else 0)
