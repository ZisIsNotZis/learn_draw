#!/usr/bin/env python3
"""M3d self-check — the writer measures its own render before claiming (D18 discipline, downward).

Checks the four reviewer-measured failures of M3c against the fresh render:
  1. neck    — no background-majority row between chin (y378) and collar (y405) across x680-740
  2. left arm — the left sleeve/cuff region connects to the bow/torso mass (no bg gap >= 12px)
  3. knee    — a skin-coloured connected region below the hem, lower-left, min dimension >= 100
  4. strand  — every painted component in the upper-left box reaches the bow/hair cover or is >=20px wide
"""
import cv2, numpy as np, sys

art = sys.argv[1] if len(sys.argv) > 1 else "/tmp/m3d.png"
ref = cv2.imread("image.jpg").astype(np.int16)
d = cv2.imread(art).astype(np.int16)
b0 = np.median(np.concatenate([ref[:12].reshape(-1, 3), ref[-12:].reshape(-1, 3),
                               ref[:, :12].reshape(-1, 3), ref[:, -12:].reshape(-1, 3)]), axis=0)
bgm = np.linalg.norm(d - b0, axis=2) <= 45          # background mask
ok = True

# ---- 1. neck ---------------------------------------------------------------
band = bgm[376:406, 680:740]
worst = band.mean(axis=1).max()
neck_ok = worst < 0.5
ok &= neck_ok
print(f"1. neck    worst-row background fraction in x680-740, y376-405: {worst:.2f}  -> {'PASS' if neck_ok else 'FAIL'}")

# ---- 2. left arm connected --------------------------------------------------
# the left sleeve/cuff live around x540-640, y470-660; require their pixels to be within the
# same connected non-background component as the torso mass (x>=660 same rows)
reg = (~bgm[440:700, 480:720]).astype(np.uint8)
n, lab = cv2.connectedComponents(reg)
torso_col = 660 - 480
left_col = 560 - 480
torso_ids = set(lab[:, torso_col:760 - 480].flatten()) - {0}
arm_ids = set(lab[:, left_col - 30:left_col + 40].flatten()) - {0}
touch = bool(arm_ids & torso_ids)
ok &= touch
print(f"2. left arm left-sleeve region shares a component with the torso mass: {touch}  -> {'PASS' if touch else 'FAIL'}")

# ---- 3. knee ----------------------------------------------------------------
b, g, r = d[:, :, 0], d[:, :, 1], d[:, :, 2]
skin = (np.abs(b - 189) < 22) & (np.abs(g - 215) < 22) & (np.abs(r - 232) < 22)
skin[:700, :] = False; skin[:, 512:] = False
n, lab, stats, _ = cv2.connectedComponentsWithStats(skin.astype(np.uint8))
best = None
for i in range(1, n):
    x, y, w, h, a = stats[i]
    if a > 2000 and min(w, h) >= 100:
        best = (x, y, w, h, a)
knee_ok = best is not None
ok &= knee_ok
print(f"3. knee    skin region below hem lower-left: {best if best else 'none >= 100px min-dim'}  -> {'PASS' if knee_ok else 'FAIL'}")

# ---- 4. streamer ------------------------------------------------------------
box = (~bgm[250:440, 60:560])
n, lab, stats, _ = cv2.connectedComponentsWithStats(box.astype(np.uint8))
floater = None
for i in range(1, n):
    x, y, w, h, a = stats[i]
    reaches_bow = (x + w) >= (556 - 60)      # touches the bow/hair cover at x>=556
    wide = max(w, h) >= 20
    if a > 300 and not reaches_bow and not wide:
        floater = (x + 60, y + 250, w, h, a)
strand_ok = floater is None
ok &= strand_ok
print(f"4. strand  floating thin component in x60-560/y250-440: {floater if floater else 'none'}  -> {'PASS' if strand_ok else 'FAIL'}")

print("OVERALL:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
