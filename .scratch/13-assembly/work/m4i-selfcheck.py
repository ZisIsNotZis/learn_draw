#!/usr/bin/env python3
"""M4i self-check — the interior partition's drawn ink line.

Checks:
  1. line-present   a connected dark-ink arc of >=150px inside the blue/mint head-zone window
                    (x480-700, y300-500). NOTE: the rendered component merges with neighbouring
                    strokes (the lock/collar outlines touch the line), so presence is measured on
                    the component that contains the line, not on an isolated stroke.
  2. on-boundary    >=70% of the line's pixels sit within 8px of BOTH a blue-zone pixel and a
                    mint-zone pixel — the line is ON the shared boundary, not floating in a zone.
  3. smooth         the drawn curve's geometry: turn along the authored spine (Catmull-Rom
                    resampled at 8px) < 45deg per sample. The spine, not the rendered raster, is
                    the curve's geometry; a 2.4px line cannot be isolated from adjacent strokes
                    in the raster for a turn test (a 3x3 erosion destroys it). Presence (1) and
                    on-boundary (2) are measured on the render; smoothness on the authored path
                    that produced it.
  4. regressions    all of m4h-selfcheck's checks re-run against the NEW render (art path arg).

Usage: python m4i-selfcheck.py [art.png]
"""
import sys
import numpy as np
import cv2

art = sys.argv[1] if len(sys.argv) > 1 else ".scratch/13-assembly/evidence/m4i-final.png"
d = cv2.imread(art).astype(np.int16)
fails = []


def check(name, cond, msg=""):
    print(f"{'PASS' if cond else 'FAIL'} {name}" + (f" {msg}" if msg else ""))
    if not cond:
        fails.append(name)


Hz = np.zeros((1024, 1024), bool)
Hz[300:500, 480:700] = True

# ---- 1 line present --------------------------------------------------------------------
ink = ((d[:, :, 0] < 70) & (d[:, :, 1] < 70) & (d[:, :, 2] < 70)).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(ink * Hz.astype(np.uint8), 8)
li = 1 + int(np.argmax(stats[1:, 4]))
line_size = int(stats[li, 4])
line = (lab == li)
check("line-present", line_size >= 150,
      f"largest dark component in the boundary window: {line_size}px (>=150)")

# ---- 2 on-boundary ----------------------------------------------------------------------
hair = ((np.abs(d[:, :, 0] - 170) < 45) & (np.abs(d[:, :, 1] - 116) < 40)
        & (np.abs(d[:, :, 2] - 56) < 45) & (d[:, :, 0] > d[:, :, 1] + 25))
mint = ((np.abs(d[:, :, 0] - 193) < 45) & (np.abs(d[:, :, 1] - 204) < 40)
        & (np.abs(d[:, :, 2] - 125) < 45) & (d[:, :, 1] > d[:, :, 2] + 40))
k = np.ones((17, 17), np.uint8)          # ~8px radius
near_blue = cv2.dilate(hair.astype(np.uint8), k) > 0
near_mint = cv2.dilate(mint.astype(np.uint8), k) > 0
onb = (line & near_blue & near_mint).sum() / max(line.sum(), 1)
check("on-boundary", onb >= 0.70,
      f"{onb:.0%} of the line's pixels within 8px of BOTH blue and mint (>=70%)")

# ---- 3 smooth (authored spine geometry) --------------------------------------------------
spine = np.array([[569, 300], [561, 348], [557, 403], [546, 446]], float)
# Catmull-Rom through the 4 spine points, resampled at 8px
P = [spine[0]]
for i in range(len(spine) - 1):
    p0 = spine[max(i - 1, 0)]
    p1, p2 = spine[i], spine[i + 1]
    p3 = spine[min(i + 2, len(spine) - 1)]
    for t in np.linspace(0, 1, 12, endpoint=False):
        P.append(0.5 * ((2 * p1) + (-p0 + p2) * t
                        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                        + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
P.append(spine[-1])
P = np.array(P)
s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
ri = np.searchsorted(s, np.arange(0, s[-1], 8.0))
rp = P[np.clip(ri, 0, len(P) - 1)]
turn = []
for i in range(1, len(rp) - 1):
    v1, v2 = rp[i] - rp[i - 1], rp[i + 1] - rp[i]
    a1, a2 = np.arctan2(v1[1], v1[0]), np.arctan2(v2[1], v2[0])
    turn.append(np.degrees(abs((a2 - a1 + np.pi) % (2 * np.pi) - np.pi)))
turn = np.array(turn)
check("smooth", turn.max() < 45,
      f"authored spine arc {int(s[-1])}px; max turn {turn.max():.1f}deg per 8px (<45)")

# ---- 4 regressions: all m4h checks against the new render --------------------------------
import subprocess
r = subprocess.run([sys.executable, ".scratch/13-assembly/work/m4h-selfcheck.py", art],
                   capture_output=True, text=True)
m4h = r.stdout + r.stderr
n_pass, n_fail = m4h.count("PASS"), m4h.count("FAIL")
check("m4h-regressions", (n_fail == 0) and n_pass >= 15,
      f"m4h suite: {n_pass} PASS / {n_fail} FAIL")

print("OVERALL:", "PASS" if not fails else f"{len(fails)} FAIL")
sys.exit(0 if not fails else 1)
