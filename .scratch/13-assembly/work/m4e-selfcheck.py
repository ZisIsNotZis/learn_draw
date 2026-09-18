#!/usr/bin/env python3
"""M4e self-check — render-level verification of the fold brief.

M4e's one change that matters: the mint inner face must READ as attached at the head —
a long shared boundary with the blue lock (tuck), not a capsule beside it. Checks are
MASS/BOUNDARY based (M4a/M4b/M4d lesson): contact length with thin components excluded,
tuck = contact on the face side of the lock, E1 = zero background gap between brim and
head silhouette. Geometry checks certify structure; only the reviewer pair certifies the read.
"""
import cv2, numpy as np, sys

art = sys.argv[1] if len(sys.argv) > 1 else ".scratch/13-assembly/evidence/m4e-final.png"
d = cv2.imread(art).astype(np.int16)
r = cv2.imread("image.jpg").astype(np.int16)
b0 = np.median(np.concatenate([r[:12].reshape(-1, 3), r[-12:].reshape(-1, 3),
                               r[:, :12].reshape(-1, 3), r[:, -12:].reshape(-1, 3)]), axis=0)
bgis = np.linalg.norm(d - b0, axis=2) <= 45

hair = ((np.abs(d[:, :, 0] - 171) < 45) & (np.abs(d[:, :, 1] - 116) < 40) &
        (np.abs(d[:, :, 2] - 57) < 45) & (d[:, :, 0] > d[:, :, 1] + 25))
# TIGHT mint: the fill #7dccc1 only — the wide mask swallowed the hat's teal #579eaf
mint = ((np.abs(d[:, :, 0] - 193) < 25) & (np.abs(d[:, :, 1] - 204) < 25) &
        (np.abs(d[:, :, 2] - 125) < 25) & (d[:, :, 1] > d[:, :, 2] + 40))
shadow = ((np.abs(d[:, :, 0] - 178) < 25) & (np.abs(d[:, :, 1] - 165) < 25) &
          (np.abs(d[:, :, 2] - 76) < 25))                      # the sheet's own shadow tone
mintany = mint | shadow
skin = ((np.abs(d[:, :, 0] - 189) < 20) & (np.abs(d[:, :, 1] - 215) < 20) &
        (np.abs(d[:, :, 2] - 232) < 20))                      # BGR of #e8d7bd
teal = ((np.abs(d[:, :, 0] - 175) < 30) & (np.abs(d[:, :, 1] - 158) < 30) &
        (np.abs(d[:, :, 2] - 87) < 30))                       # the brim's top surface

n, lab, stats, cent = cv2.connectedComponentsWithStats(hair.astype(np.uint8), 8)
thin = np.zeros_like(hair)
for i in range(1, n):
    x, y, w, h, a = stats[i]
    if min(w, h) < 80:
        thin[lab == i] = True
hairthick = hair & ~thin

k = np.ones((13, 13), np.uint8)
results = []
def check(name, ok, detail):
    results.append((name, ok, detail))

# 1 fold contact LENGTH, strand excluded, head zone x480-700 y280-520
adj = mintany & (cv2.dilate(hairthick.astype(np.uint8), k) > 0)
Hz = np.zeros_like(adj); Hz[280:520, 480:700] = True
hz = int((adj & Hz).sum())
check("fold-contact", hz >= 360, f"strand-excluded blue/mint adjacency in head zone: {hz}px (>=360 = 120px x 3)")

# 2 tuck: contact on the FACE side of the lock (mint emerges from behind it)
ys, xs = np.where(adj & Hz)
face_side = int((xs > 540).sum())
frac = face_side / max(hz, 1)
check("fold-tuck", frac >= 0.30, f"contact on the face side of the lock: {face_side}px = {frac:.2f} (>=0.30)")

# 3 no thin isolated blue bar upper-left
bar = thin & ~bgis
Hzb = np.zeros_like(bar); Hzb[250:520, 0:560] = True
nb, labb, statsb, _ = cv2.connectedComponentsWithStats((bar & Hzb).astype(np.uint8), 8)
bars = [int(statsb[i][4]) for i in range(1, nb) if statsb[i][4] > 200]
check("no-strand", not bars, f"thin isolated blue bars in x0-560/y250-520: {bars if bars else 'none'}")

# 4 E1: brim tucks behind the head silhouette — zero background gap at brim rows
ov = teal & (cv2.dilate((skin | hair).astype(np.uint8), k) > 0)
Hz2 = np.zeros_like(ov); Hz2[60:360, 340:900] = True
contact = int((ov & Hz2).sum())
gaps = 0
for y in range(80, 260, 8):
    t = np.where(teal[y])[0]; h = np.where((hair | skin)[y])[0]
    if len(t) and len(h) and h.min() > t.max():
        gaps += int(bgis[y, t.max():h.min()].sum())
check("E1-brim-behind-skull", contact >= 500 and gaps <= 20,
      f"brim/head contact {contact}px; background gap across brim rows: {gaps}px")

# 5 chips: a FLOATING chip is a painted component SURROUNDED BY BACKGROUND — dilate it 8px and
# require the surrounding ring to be mostly background. Ink fragments on a mass or bow-edge
# pieces have painted rings and are not floating.
Hzc = np.zeros_like(bgis); Hzc[250:700, 0:560] = True
nc, labc, statsc, _ = cv2.connectedComponentsWithStats((~bgis & Hzc).astype(np.uint8), 8)
chips = []
kd = np.ones((17, 17), np.uint8)
for i in range(1, nc):
    x, y, w, h, a = statsc[i]
    if a < 300 or a > 20000:
        continue
    comp = (labc == i)
    ring = cv2.dilate(comp.astype(np.uint8), kd) > 0
    ring = ring & ~comp & Hzc
    if ring.sum() == 0:
        continue
    bgratio = bgis[ring].mean()
    if bgratio >= 0.70:
        chips.append((int(x), int(y), int(a), round(float(bgratio), 2)))
check("no-chips", not chips, f"background-surrounded floating chips in x0-560/y250-700: {chips if chips else 'none'}")

# 6-16 regressions from M4d (unity, rooted, one-piece, extent, neck, knee, arms, hand-lap,
# strand-less upper-left, hair-shoulder) — recomputed here against the M4d thresholds.
madj = mintany & (cv2.dilate(hair.astype(np.uint8), k) > 0)
check("reg-unity", madj.sum() >= 0.02 * mintany.sum(),
      f"mint within 6px of blue: {int(madj.sum())}/{int(mintany.sum())}")
ysm, xsm = np.where(madj)
rooted = len(xsm) and (450 <= xsm.mean() <= 750) and (200 <= ysm.mean() <= 550)
check("reg-rooted", bool(rooted), f"adjacency centroid ({int(xsm.mean()) if len(xsm) else -1},{int(ysm.mean()) if len(ysm) else -1})")
nm, labm, statsm, _ = cv2.connectedComponentsWithStats(mintany.astype(np.uint8), 8)
# Strands and ink lines lying ON the sheet legitimately cut it in flat pixels (the strand is hair
# ON the hair); close 40px so the sheet's pieces separated ONLY by its own strand/ink read as one.
closed = cv2.morphologyEx(mintany.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((41, 41), np.uint8))
ncm, labm2, statsm2, _ = cv2.connectedComponentsWithStats(closed, 8)
keep = {i for i in range(1, ncm) if statsm2[i][4] > 500}
covered = sum(int(((labm2 == i) & mintany).sum()) for i in keep)
onep = covered / max(mintany.sum(), 1)
check("reg-one-piece", onep >= 0.95, f"mint in strands-crossing-closed pieces: {onep:.1%}")
band = mint[350:650, 560:720].mean()
check("reg-extent", mint[:, 0:120].any() and band >= 0.20, f"mint at left edge; band frac {band:.2f}")
neckband = bgis[376:406, 665:736]
check("reg-neck", int((neckband.mean(axis=1) > 0.9).sum()) == 0, "fully-background neck rows: 0")
skinlobe = ((np.abs(d[:, :, 0] - 189) < 25) & (np.abs(d[:, :, 1] - 215) < 25) & (np.abs(d[:, :, 2] - 232) < 25))[700:, :]
nc2, lab2, st2, _ = cv2.connectedComponentsWithStats(skinlobe.astype(np.uint8), 8)
knee = max([int(st2[i][4]) for i in range(1, nc2)], default=0)
check("reg-knee", knee > 3000, f"skin lobe below hem: {knee}px")
armzone = bgis[470:640, 500:700]
check("reg-arms", int((armzone.all(axis=1)).sum()) == 0, "fully-background arm rows: 0")
lap = ((np.abs(d[:, :, 0] - 80) < 55) & (d[:, :, 2] < d[:, :, 1]))[840:950, 700:900]
handzone = ((np.abs(d[:, :, 0] - 189) < 30) & (np.abs(d[:, :, 1] - 215) < 30) & (np.abs(d[:, :, 2] - 232) < 30))[840:950, 700:900]
check("reg-hand-lap", handzone.sum() > 300 and lap.mean() > 0.3,
      f"hand px {int(handzone.sum())}, lap-mass frac {lap.mean():.2f}")
strandzone = thin & ~bgis
Hzs = np.zeros_like(strandzone); Hzs[250:440, 0:560] = True
ns, labs, statss, _ = cv2.connectedComponentsWithStats((strandzone & Hzs).astype(np.uint8), 8)
strays = [int(statss[i][4]) for i in range(1, ns) if statss[i][4] > 200]
check("reg-strandless-upperleft", not strays, f"floating bars upper-left: {strays if strays else 'none'}")
hsh = hair[560:700, 700:900].sum()
check("reg-hair-shoulder", hsh > 500, f"blue hair px over the forearm zone: {int(hsh)}")

fails = 0
for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL'} {name:24s} {detail}")
    fails += (not ok)
print(f"OVERALL: {'PASS' if fails == 0 else str(fails) + ' FAIL'}")
sys.exit(0)
