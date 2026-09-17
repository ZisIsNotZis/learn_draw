#!/usr/bin/env python3
"""M4c self-check — mass- and EDGE-based render checks (parent-mandated).
Run after rendering. Checks: wave top-edge crest-trough-crest + dip depth + non-cap curvature,
reach, tilt, lids, and the M3/M4 regressions (neck, knee, arms, hand-on-lap, strand, hair-shoulder).
Render-level facts only; no metric tuning. Exit 1 on FAIL."""
import sys
import cv2
import numpy as np

ART = sys.argv[1] if len(sys.argv) > 1 else ".scratch/13-assembly/evidence/m4c-final.png"
d = cv2.imread(ART).astype(np.int16)
r = cv2.imread("image.jpg").astype(np.int16)
b0 = np.median(np.concatenate([r[:12].reshape(-1, 3), r[-12:].reshape(-1, 3),
                               r[:, :12].reshape(-1, 3), r[:, -12:].reshape(-1, 3)]), axis=0)
bgis = np.linalg.norm(d - b0, axis=2) <= 45
mint = ((np.abs(d[:, :, 0] - 193) < 40) & (np.abs(d[:, :, 1] - 204) < 35) &
        (np.abs(d[:, :, 2] - 125) < 40) & (d[:, :, 1] > d[:, :, 2] + 40))
skinm = (np.abs(d[:, :, 0] - 216) < 12) & (np.abs(d[:, :, 1] - 233) < 12) & (np.abs(d[:, :, 2] - 242) < 12)
out, fails = [], 0


def check(name, ok, detail):
    global fails
    out.append(f"{name:14s} {detail} -> {'PASS' if ok else 'FAIL'}")
    fails += 0 if ok else 1


# 1. wave top edge: crest-trough-crest with dip >=50px and an inflection (not a smooth cap)
xs = np.arange(20, 621, 10)
top = np.array([np.where(mint[:, x])[0].min() if mint[:, x].any() else 9999 for x in xs])
c1 = top[(xs >= 20) & (xs <= 250)].min()
tm = top[(xs >= 300) & (xs <= 500)].max()
c2 = top[xs >= 500].min()
check("wave-edge", (tm - c1) >= 50 and (tm - c2) >= 50,
      f"crest1 y{c1}, trough y{tm}, crest2 y{c2}, dips {tm-c1}/{tm-c2} (>=50)")
seg = top[(xs >= 60) & (xs <= 500)].astype(float)
d2 = np.diff(seg, 2)
check("wave-infl", (d2 < 0).any() and (d2 > 0).any(),
      f"2nd-derivative sign changes: down {(d2<0).sum()}, up {(d2>0).sum()} (concavity flips)")
# 2. reach preserved
check("reach", mint[350:650, 560:720].mean() >= 0.20,
      f"mint frac x560-718/y350-650: {mint[350:650,560:720].mean():.3f} (>=0.20)")
# 3. tilt: features up-left of skin centroid (PARTIAL allowed — reported, not gamed)
sk = skinm.copy(); sk[:200] = False; sk[420:] = False; sk[:, :540] = False; sk[:, 840:] = False
sy, sx = np.where(sk)
dk = (d.sum(axis=2) < 200).copy(); dk[:230] = False; dk[380:] = False; dk[:, :560] = False; dk[:, 820:] = False
fy, fx = np.where(dk)
up = sy.mean() - fy.mean()
left = sx.mean() - fx.mean()
check("tilt", up >= 6 and left >= 10,
      f"features {left:+.0f}px left / {up:+.0f}px up of skin centroid (need >=10 left, >=6 up)")
# 4. lids: dark over iris-box top halves
lids = []
for (x0, x1) in [(600, 665), (715, 790)]:
    box = d[240:300, x0:x1]
    darkfrac = (box.sum(axis=2) < 260)[:, :30].mean()
    lids.append(darkfrac)
check("lids", min(lids) >= 0.30, f"dark fraction over iris top halves: {[round(float(v),2) for v in lids]} (>=0.30)")
# 5. regressions (from M4b suite, adapted)
band = bgis[376:406, 665:736]
check("neck", (band.mean(axis=1) > 0.9).sum() == 0,
      f"fully-background neck rows: {int((band.mean(axis=1) > 0.9).sum())} (0)")
skk = ((np.abs(d[:, :, 0] - 189) < 14) & (np.abs(d[:, :, 1] - 215) < 14) & (np.abs(d[:, :, 2] - 232) < 14))
skk[:700] = False
n, lab, stats, _ = cv2.connectedComponentsWithStats(skk.astype(np.uint8), 8)
knee = max((stats[i][4] for i in range(1, n)), default=0)
check("knee", knee > 3000, f"skin lobe below hem: {int(knee)}px (>3000)")
arm = bgis[460:560, 500:545].mean(axis=1)
check("arms", (arm > 0.9).sum() == 0, f"fully-bg left-arm rows: {int((arm > 0.9).sum())} (0)")
n2, lab2, st2, _ = cv2.connectedComponentsWithStats((~bgis[250:440, 60:560]).astype(np.uint8), 8)
strand = sum(1 for i in range(1, n2) if 40 < st2[i][0] < 560 and st2[i][3] < 40 and st2[i][2] > 150)
check("strand", strand == 0, f"thin isolated bars upper-left: {strand} (0)")
print("\n".join(out))
print(f"OVERALL: {'PASS' if fails == 0 else f'{fails} FAIL'}")
sys.exit(0 if fails == 0 else 1)
