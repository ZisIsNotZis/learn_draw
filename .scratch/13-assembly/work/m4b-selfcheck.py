#!/usr/bin/env python3
"""M4b self-check — MASS-BASED (the M4a lesson: any-pixel extents passed while the read failed).

Checks the RENDER (not the intent). All inputs are the draft PNG only.
"""
import sys
import cv2
import numpy as np

PNG = sys.argv[1] if len(sys.argv) > 1 else "/tmp/m4b.png"
d = cv2.imread(PNG).astype(int)
bg = np.array([195, 215, 220])  # the backdrop rect #c3d7dc in BGR
bgis = (np.linalg.norm(d - bg, axis=2) <= 45)

mint = ((np.abs(d[:,:,0]-193) < 40) & (np.abs(d[:,:,1]-204) < 35) &
        (np.abs(d[:,:,2]-125) < 40) & (d[:,:,1] > d[:,:,2] + 40)).astype(np.uint8)
# MASS-BASED connectivity: occluder strokes <=50px (streamer, collar edge) bridge; real
# separations do not. Without the bridge the bow's own outline splits the band in two —
# in the reference the wave also passes BEHIND the bow, so pixel separation there is
# correct occlusion, not a broken wave.
big = cv2.dilate(mint, np.ones((51, 51), np.uint8))
n, lab, stats, _ = cv2.connectedComponentsWithStats(big, 8)
i = 1 + int(np.argmax(stats[1:, 4]))
x, y, w2, h2, area = (int(v) for v in stats[i])
th = {cx: int(mint[:, cx].sum()) for cx in (300, 500, 650)}
wave_ok = (x + w2 >= 650) and all(v >= 100 for v in th.values())
print(f"1. wave     bridged largest comp x{x}-{x+w2} area{area}; visible mint thickness {th} "
      f"(>=100 each, extent >=650) -> {'PASS' if wave_ok else 'FAIL'}")

# 2 expression: eye sizes, red-free irises, lash over the iris top
hair = ((np.abs(d[:,:,0]-171) < 40) & (np.abs(d[:,:,1]-116) < 40) & (np.abs(d[:,:,2]-57) < 40))
def eyebox(cx, cy):
    # tight window around the eye anchor (head-relative, from the spec), sclera/iris/lash inks
    x0, x1, y0, y1 = cx-42, cx+42, cy-26, cy+30
    win = d[y0:y1, x0:x1]
    ink = ~((np.abs(win[:,:,0]-220) < 25) & (np.abs(win[:,:,1]-215) < 25) & (np.abs(win[:,:,2]-195) < 25)) \
        & ~((np.abs(win[:,:,0]-216) < 18) & (np.abs(win[:,:,1]-233) < 18) & (np.abs(win[:,:,2]-242) < 18)) \
        & ~((np.abs(win[:,:,0]-171) < 45) & (np.abs(win[:,:,1]-116) < 45) & (np.abs(win[:,:,2]-57) < 45)) \
        & ~((win[:,:,0] < 45) & (win[:,:,1] < 45) & (win[:,:,2] < 45))  # lash ink: style, not aperture
    ys, xs = np.where(ink)
    return (x0+int(xs.min()), x0+int(xs.max()), y0+int(ys.min()), y0+int(ys.max())) if len(xs) else None
rb = eyebox(754, 268); lb = eyebox(634, 262)
rw, lw = rb[1]-rb[0], lb[1]-lb[0]
rh, lh = rb[3]-rb[2], lb[3]-lb[2]
size_ok = abs(rw-lw)/max(rw,lw) <= 0.15 and abs(rh-lh)/max(rh,lh) <= 0.15
red = ((d[:,:,2] > 150) & (d[:,:,1] < 120) & (d[:,:,0] < 160)).astype(np.uint8)
n2, l2, s2, _ = cv2.connectedComponentsWithStats(red, 8)
red_in_iris = sum(int(s2[j][4]) for j in range(1, n2)
                  if s2[j][1] > 230 and s2[j][1] < 320 and s2[j][0] > 560 and s2[j][0] < 800)
dark = ((d[:,:,0] < 60) & (d[:,:,1] < 60) & (d[:,:,2] < 70))
lash = 0
for (bx0, bx1, by0, by1) in (rb, lb):
    top = dark[by0-14:by0+int((by1-by0)*0.34), bx0:bx1]
    lash += int(top.sum())
lash_ok = lash > 60
expr_ok = size_ok and red_in_iris == 0 and lash_ok
print(f"2. expr     eye w {rw} vs {lw}, h {rh} vs {lh} (within15%: {size_ok}); "
      f"red px in iris zone {red_in_iris}; lash-dark px {lash} -> {'PASS' if expr_ok else 'FAIL'}")

# 3 knee: skin below the hem, >=100px small dim, connected to the leg cloth region
skin = ((np.abs(d[:,:,0]-189) < 22) & (np.abs(d[:,:,1]-215) < 22) & (np.abs(d[:,:,2]-232) < 22))
low = skin[760:, :].astype(np.uint8)
n3, l3, s3, _ = cv2.connectedComponentsWithStats(low, 8)
ki = 1 + int(np.argmax(s3[1:, 4]))
kx, ky, kw, kh, ka = (int(v) for v in s3[ki])
# connectivity: from the blob, climb through skin or knee-cloth colours to above y860
cloth = ((np.abs(d[:,:,0]-216) < 14) & (np.abs(d[:,:,1]-226) < 14) & (np.abs(d[:,:,2]-210) < 14)) \
      | ((np.abs(d[:,:,0]-202) < 14) & (np.abs(d[:,:,1]-216) < 14) & (np.abs(d[:,:,2]-195) < 14))
path = skin | cloth
reach, yy, xx = (ky + 760) <= 870, ky + 760, kx + (kw // 2)
while yy > 855 and not reach:
    window = path[max(0, yy-14):yy+4, max(0, xx-40):xx+40]
    ys, xs = np.where(window)
    if len(ys) == 0: break
    yy = max(0, yy-14) + int(ys.min())
    xx = max(0, xx-40) + int(xs[np.argmin(ys)])
    if yy <= 860: reach = True
knee_ok = min(kw, kh) >= 100 and reach
print(f"3. knee     skin blob {kw}x{kh} at ({kx},{ky+760}) area{ka}; climb reached y{yy} "
      f"(<=860: {reach}) -> {'PASS' if knee_ok else 'FAIL'}")

# 4 hand on lap: lap-mass colour directly beneath the hand's bbox
navy = ((np.abs(d[:,:,0]-103) < 45) & (np.abs(d[:,:,1]-78) < 45) & (np.abs(d[:,:,2]-45) < 45))
zone = navy[915:1005, 776:838]  # below the hand's own pixels: the lap it rests ON
hand_ok = zone.mean() >= 0.5
print(f"4. hand     lap-mass frac beneath the hand {zone.mean():.2f} (>=0.50) -> {'PASS' if hand_ok else 'FAIL'}")

# 5 regressions from M3/M4a
band = bgis[376:406, 665:736]
neck_ok = not (band.mean(axis=1) > 0.9).any()
white = ((d[:,:,0] > 200) & (d[:,:,1] > 200) & (d[:,:,2] > 190))
col_ok = not bgis[600:660, 820:900].all(axis=0).any()
strand = mint[250:440, 60:560]
strand_ok = True  # mint is the wave's own crest now; the old floating bar was purple
purp = ((np.abs(d[:,:,0]-166) < 45) & (np.abs(d[:,:,1]-132) < 45) & (np.abs(d[:,:,2]-137) < 45)).astype(np.uint8)
n4, l4, s4, _ = cv2.connectedComponentsWithStats(purp, 8)
float_bar = any(s4[j][4] > 4000 and s4[j][0] < 560 and s4[j][1] < 440 and s4[j][3] < 200 for j in range(1, n4))
print(f"5. regr     neck fully-bg rows: {int((band.mean(axis=1) > 0.9).sum())} ({neck_ok}); "
      f"floating purple bar: {float_bar} -> {'PASS' if neck_ok and not float_bar else 'FAIL'}")

ok = wave_ok and expr_ok and knee_ok and hand_ok and neck_ok and not float_bar
print("OVERALL:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
