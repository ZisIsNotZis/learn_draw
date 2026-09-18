#!/usr/bin/env python3
"""M4d self-check — the hair-structure rebuild (USER DESIGN READING implemented).

MASS-BASED render checks (the M4a lesson) + occlusion-correct continuity (new):
the hair's inner face must be ROOTED at the head (adjacent to the blue hair across a real
shared boundary), be ONE structure (connected through painted pixels — occluders bridge,
background gaps do not), keep the measured extent, and regress nothing from M3/M4a/b.
Run: .venv/bin/python work/m4d-selfcheck.py [png]. Exit 1 on FAIL.
"""
import sys
import cv2
import numpy as np

ART = sys.argv[1] if len(sys.argv) > 1 else ".scratch/13-assembly/evidence/m4d-final.png"
d = cv2.imread(ART).astype(np.int16)
r = cv2.imread("image.jpg").astype(np.int16)
b0 = np.median(np.concatenate([r[:12].reshape(-1, 3), r[-12:].reshape(-1, 3),
                               r[:, :12].reshape(-1, 3), r[:, -12:].reshape(-1, 3)]), axis=0)
bgis = np.linalg.norm(d - b0, axis=2) <= 45
mint = ((np.abs(d[:, :, 0] - 193) < 40) & (np.abs(d[:, :, 1] - 204) < 35) &
        (np.abs(d[:, :, 2] - 125) < 40) & (d[:, :, 1] > d[:, :, 2] + 40)).astype(np.uint8)
blue = ((np.abs(d[:, :, 0] - 171) < 40) & (np.abs(d[:, :, 1] - 116) < 40) &
        (np.abs(d[:, :, 2] - 57) < 40)).astype(np.uint8)
out, fails = [], 0


def check(name, ok, detail):
    global fails
    out.append(f"{name:14s} {detail} -> {'PASS' if ok else 'FAIL'}")
    fails += 0 if ok else 1


# 1 UNITY: mint adjacent (<=6px) to blue near the head — the fold is a real shared boundary
db = cv2.dilate(blue, np.ones((13, 13), np.uint8)) > 0
win = np.zeros_like(mint, bool)
win[250:500, 450:750] = True
mw = win & (mint > 0)
adj = mw & db
ys, xs = np.nonzero(adj)
rooted = len(xs) and 450 <= int(np.median(xs)) <= 750 and 200 <= int(np.median(ys)) <= 550
check("unity", mw.sum() and adj.sum() >= 0.02 * mw.sum(),
      f"mint within 6px of blue in the head window: {int(adj.sum())}/{int(mw.sum())} "
      f"({adj.sum()/max(mw.sum(),1):.1%}, >=2%)")
check("rooted", bool(rooted),
      f"adjacency centroid ({int(np.median(xs)) if len(xs) else '-'},"
      f"{int(np.median(ys)) if len(ys) else '-'}) in x450-750/y200-550: {bool(rooted)}")

# 2 ONE PIECE: every mint component (>=50px) reachable through PAINTED pixels (occluders bridge;
#   background gaps do not — this is what failed M4a's two puddles)
painted = (~bgis).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(painted, 8)
mi = 1 + int(np.argmax(stats[1:, 4]))
nm, lm, sm, _ = cv2.connectedComponentsWithStats(mint, 8)
ok_px = tot = 0
for j in range(1, nm):
    a = int(sm[j][4])
    if a < 50:
        continue
    tot += a
    ys, xs = np.nonzero(lm == j)
    if float((lab[ys, xs] == mi).mean()) > 0.5:
        ok_px += a
frac = ok_px / max(tot, 1)
check("one-piece", frac >= 0.95, f"mint connected through painted pixels: {ok_px}/{tot} "
      f"({frac:.1%}, >=95%)")

# 3 EXTENT: the sheet still reaches the left edge; the behind-the-jaw band is minted
xs_all = np.nonzero(mint.any(axis=0))[0]
check("extent", (len(xs_all) and xs_all.min() <= 120) and mint[350:650, 560:720].mean() >= 0.20,
      f"mint min x {int(xs_all.min()) if len(xs_all) else '-'} (<=120); "
      f"band x560-718/y350-650 frac {mint[350:650,560:720].mean():.3f} (>=0.20)")

# 4 NO CHIPS: no painted component <900px fully surrounded by background in x0-560/y250-700
zone = (~bgis).astype(np.uint8)
zone[:250] = 0; zone[700:] = 0; zone[:, 560:] = 0
nc, lc, sc, _ = cv2.connectedComponentsWithStats(zone, 8)
chips = [int(sc[j][4]) for j in range(1, nc)
         if sc[j][4] < 900 and sc[j][0] > 0 and sc[j][1] > 250
         and sc[j][0] + sc[j][2] < 560 and sc[j][1] + sc[j][3] < 700]
check("no-chips", len(chips) == 0, f"background-surrounded chips <900px: {len(chips)} {chips[:4]}")

# 5 REGRESSIONS (M3/M4a/b gains)
band = bgis[376:406, 665:736]
check("neck", (band.mean(axis=1) > 0.9).sum() == 0,
      f"fully-background neck rows: {int((band.mean(axis=1) > 0.9).sum())} (0)")
skk = ((np.abs(d[:, :, 0] - 189) < 14) & (np.abs(d[:, :, 1] - 215) < 14) &
       (np.abs(d[:, :, 2] - 232) < 14))
skk[:700] = False
n3, l3, s3, _ = cv2.connectedComponentsWithStats(skk.astype(np.uint8), 8)
knee = max((int(s3[i][4]) for i in range(1, n3)), default=0)
check("knee", knee > 3000, f"skin lobe below hem: {knee}px (>3000)")
arm = bgis[460:560, 500:545].mean(axis=1)
check("arms", (arm > 0.9).sum() == 0, f"fully-bg left-arm rows: {int((arm > 0.9).sum())} (0)")
navy = ((np.abs(d[:, :, 0] - 103) < 45) & (np.abs(d[:, :, 1] - 78) < 45) &
        (np.abs(d[:, :, 2] - 45) < 45))
hzone = navy[915:1005, 776:838]
check("hand-lap", hzone.mean() >= 0.5, f"lap-mass frac beneath the hand {hzone.mean():.2f} (>=0.50)")
n4, l4, s4, _ = cv2.connectedComponentsWithStats(
    ((np.abs(d[:, :, 0] - 166) < 45) & (np.abs(d[:, :, 1] - 132) < 45) &
     (np.abs(d[:, :, 2] - 137) < 45)).astype(np.uint8), 8)
fbar = any(s4[j][4] > 4000 and s4[j][0] < 560 and s4[j][1] < 440 and s4[j][3] < 200
           for j in range(1, n4))
check("strand", not fbar, f"floating purple bar upper-left: {fbar} (False)")
hover = int(blue[700:790, 840:1020].sum())
check("hair-shoulder", hover > 500, f"blue hair px over the forearm zone y700-790: {hover} (>500)")

print("\n".join(out))
print(f"OVERALL: {'PASS' if fails == 0 else f'{fails} FAIL'}")
sys.exit(0 if fails == 0 else 1)
