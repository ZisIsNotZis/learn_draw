#!/usr/bin/env python3
"""Measure the registered A teacher crop and print the numbers the art-direction brief cites.

Source of truth: image.jpg, registered bbox 500,320,900,800 -> 400x480. The crop file
`evidence/A-cloth-v6/ref/crop-400x480.png` is verified against that bbox before any measurement, so
every number below is reproducible from either file.

No drawing and no target tuning: this script only reports what is in the reference. Coordinates are
crop pixels, origin at the crop's top-left. Deterministic: fixed anchors, no randomness.

Classification: each pixel goes to the nearest of the hand-picked flat-region anchors below (JPEG noise
is why anchors rather than exact colours). `ink` is the drawing's line work, `edge` is mid-grey
anti-aliasing and is never measured as a colour or counted as figure.
"""
import sys
import numpy as np
import cv2
from PIL import Image, ImageChops

CROP = ".scratch/35-r1-articulated-study/evidence/A-cloth-v6/ref/crop-400x480.png"
SRC = "image.jpg"
BBOX = (500, 320, 400, 480)  # x, y, w, h in image.jpg

# name -> (anchor rgb, measurement class)
ANCHORS = [
    ("bg_mint",     (114, 200, 192), "bg"),
    ("bg_teal",     (78, 165, 178), "bg"),
    ("bg_pale",     (209, 219, 223), "bg"),
    ("bg_pale_hi",  (185, 221, 237), "bg"),
    ("skin",        (242, 232, 213), "skin"),
    ("skin_shade",  (205, 175, 190), "skin"),
    ("cloth_white", (227, 231, 219), "cloth"),
    ("cloth_pale",  (213, 225, 215), "cloth"),
    ("cloth_blue",  (148, 192, 208), "cloth_blue"),
    ("hair",        (58, 114, 167), "hair"),
    ("hair_dark",   (25, 80, 110), "hair"),
    ("band",        (85, 115, 178), "band"),
    ("bow",         (206, 78, 126), "bow"),
    ("bow_dark",    (103, 35, 61), "bow"),
    ("navy",        (46, 69, 92), "navy"),
    ("ink",         (16, 40, 56), "ink"),
    ("ink_grey",    (90, 111, 118), "ink"),
    ("edge",        (139, 156, 158), "edge"),
]
NAMES = [a[0] for a in ANCHORS]
CLASS = [a[2] for a in ANCHORS]
ARR = np.array([a[1] for a in ANCHORS], np.float32)


def load():
    src = Image.open(SRC).convert("RGB")
    crop = Image.open(CROP).convert("RGB")
    x, y, w, h = BBOX
    ref = src.crop((x, y, x + w, y + h))
    same = ImageChops.difference(ref, crop).getbbox() is None
    print("== source ==")
    print(f"image.jpg {src.size}; registered bbox {BBOX} -> {w}x{h}; crop file {crop.size}")
    print(f"crop == image.jpg[bbox]: {same}" + ("" if same else "  *** MISMATCH, aborting"))
    if not same:
        sys.exit(1)
    return np.asarray(crop).astype(np.float32)


def classify(img):
    return ((img[:, :, None, :] - ARR[None, None, :, :]) ** 2).sum(-1).argmin(-1)


def cmask(lab, cls):
    return np.isin(lab, [i for i, c in enumerate(CLASS) if c == cls])


def runs(row_mask, min_len=4, xoff=0):
    out, start = [], None
    for x, v in enumerate(row_mask):
        if v and start is None:
            start = x
        elif not v and start is not None:
            if x - start >= min_len:
                out.append((start + xoff, x - 1 + xoff))
            start = None
    if start is not None and len(row_mask) - start >= min_len:
        out.append((start + xoff, len(row_mask) - 1 + xoff))
    return out


def row_classes(lab, y, min_len=4):
    row = lab[y]
    out, start, cur = [], 0, CLASS[row[0]]
    for x in range(1, len(row)):
        c = CLASS[row[x]]
        if c != cur:
            if x - start >= min_len:
                out.append((cur, start, x - 1))
            start, cur = x, c
    if len(row) - start >= min_len:
        out.append((cur, start, len(row) - 1))
    return out


def fmt(rs):
    return "  ".join(f"{c}[{a}-{b}]" for c, a, b in rs)


def comps(mask, min_area=100):
    n, _, stats, cent = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area >= min_area:
            out.append(dict(x=int(x), y=int(y), w=int(w), h=int(h), area=int(area),
                            cx=round(float(cent[i][0]), 1), cy=round(float(cent[i][1]), 1)))
    out.sort(key=lambda d: -d["area"])
    return out


def bbox_of(m):
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), int(len(xs)))


def region(mask, barrier, seed):
    """Flood the near-uniform region under `seed`, stopping at `barrier` pixels (the drawn lines)."""
    free = (mask & ~barrier).astype(np.uint8)
    n, lab_ = cv2.connectedComponents(free, 4)
    sx, sy = seed
    if not free[sy, sx]:
        # snap to the nearest free pixel inside the same 12 px window
        win = free[max(0, sy - 12):sy + 13, max(0, sx - 12):sx + 13]
        yy, xx = np.nonzero(win)
        if not len(xx):
            return None, None
        d = (xx - min(sx, 12)) ** 2 + (yy - min(sy, 12)) ** 2
        i = d.argmin()
        sx, sy = max(0, sx - 12) + xx[i], max(0, sy - 12) + yy[i]
        if not free[sy, sx]:
            return None, None
    k = lab_[sy, sx]
    m = lab_ == k
    return m, bbox_of(m)


def main():
    img = load()
    lab = classify(img)
    H, W = lab.shape

    print("\n== palette (nearest-anchor pixel counts) ==")
    for i, n in enumerate(NAMES):
        cnt = int((lab == i).sum())
        print(f"  {n:12s} {'#%02x%02x%02x' % ANCHORS[i][1]} class={CLASS[i]:10s} px={cnt:6d} {100*cnt/(H*W):5.2f}%")

    m_bg, m_skin, m_cloth = cmask(lab, "bg"), cmask(lab, "skin"), cmask(lab, "cloth")
    m_cblue, m_hair, m_band = cmask(lab, "cloth_blue"), cmask(lab, "hair"), cmask(lab, "band")
    m_bow, m_navy, m_ink = cmask(lab, "bow"), cmask(lab, "navy"), cmask(lab, "ink")
    m_dark = m_navy | m_ink
    body = m_cloth | m_cblue
    figure = ~m_bg & ~cmask(lab, "edge")

    print("\n== large flat components (area >= 400 px) ==")
    for name, m in [("skin", m_skin), ("cloth", m_cloth), ("cloth_blue", m_cblue), ("hair", m_hair),
                    ("band", m_band), ("bow", m_bow), ("navy", m_navy), ("ink", m_ink)]:
        for c in comps(m, 400):
            print(f"  {name:11s} bbox=({c['x']},{c['y']})-({c['x']+c['w']-1},{c['y']+c['h']-1}) "
                  f"w={c['w']:3d} h={c['h']:3d} area={c['area']:6d} centroid=({c['cx']},{c['cy']})")

    # ---- 1. head, jaw, neck ------------------------------------------------------------------
    print("\n== 1. head, jaw, neck, mouth ==")
    face = m_skin.copy()
    face[60:] = False
    face[:, :125] = False
    face[:, 285:] = False
    print(f"face (lit skin, y<60): bbox={bbox_of(face)}")
    jaw = [(x, (lambda c: int(c.max()) if len(c) else None)(np.nonzero(face[:, x])[0]))
           for x in range(130, 281, 10)]
    print("jaw line, lowest lit-skin y per column: " + " ".join(f"{x}:{y}" for x, y in jaw))
    ys, xs = np.nonzero(face)
    print(f"lowest lit-skin row in the face box y={ys.max()} at x={xs[ys==ys.max()].min()}..{xs[ys==ys.max()].max()}")
    jm = np.zeros_like(m_ink)
    jm[0:65, 120:235] = True
    for c in comps((img.mean(2) < 150) & jm, 40):
        sub = (m_ink & jm)[c["y"]:c["y"] + c["h"], c["x"]:c["x"] + c["w"]]
        yy, xx = np.nonzero(sub)
        pts = np.stack([xx + c["x"], yy + c["y"]], 1).astype(float)
        ev, evec = np.linalg.eigh(np.cov(pts.T))
        d = evec[:, -1]
        proj = pts @ d
        p0, p1 = pts[proj.argmin()], pts[proj.argmax()]
        print(f"  drawn jaw line: bbox=({c['x']},{c['y']})-({c['x']+c['w']-1},{c['y']+c['h']-1}) "
              f"area={c['area']} ends=({p0[0]:.0f},{p0[1]:.0f})->({p1[0]:.0f},{p1[1]:.0f}) "
              f"length={np.hypot(*(p1-p0)):.0f}px")
    mo = (img.mean(2) < 150) & ~m_hair
    mo[:25] = False
    mo[45:] = False
    mo[:, :165] = False
    mo[:, 215:] = False
    print("mouth mark component(s) in x165-215,y25-45: " +
          (", ".join(f"({c['x']},{c['y']}) {c['w']}x{c['h']} area={c['area']}"
                     for c in comps(mo, 4)) or "none"))
    hair_lock = [c for c in comps(m_hair, 200) if 200 < c["x"] < 275 and c["w"] < 60 and c["y"] < 5]
    for c in hair_lock:
        print(f"hair lock crossing the jaw/face: bbox=({c['x']},{c['y']})-"
              f"({c['x']+c['w']-1},{c['y']+c['h']-1}) w={c['w']} h={c['h']} area={c['area']}")
    print("neck: lit-skin run per row (x window 150..320)")
    for y in [55, 65, 75, 85, 95, 105]:
        rs = runs(m_skin[y, 150:320], xoff=150)
        if rs:
            a, b = rs[0][0], rs[-1][1]
            print(f"  y={y}: x={a}..{b} width={b-a+1} centre={(a+b)/2:.1f} runs={rs}")
        else:
            print(f"  y={y}: no skin run")
    cx = 237
    col = lab[:, cx]
    seq, start, cur = [], 0, CLASS[col[0]]
    for y in range(1, H):
        c = CLASS[col[y]]
        if c != cur:
            if y - start >= 4:
                seq.append((cur, start, y - 1))
            start, cur = y, c
    print(f"classes down neck-centre column x={cx}: " + fmt(seq))
    print("neck crop: the neck's lower end is where cloth_blue (collar back) begins on this column.")

    # ---- 2. collar --------------------------------------------------------------------------
    print("\n== 2. collar ==")
    win = np.zeros_like(m_navy)
    win[85:215, :] = True
    for name, m in [("collar pale-blue body", m_cblue & win), ("collar navy stripe", m_navy & win)]:
        for c in comps(m, 150):
            print(f"  {name:22s} bbox=({c['x']},{c['y']})-({c['x']+c['w']-1},{c['y']+c['h']-1}) "
                  f"w={c['w']:3d} h={c['h']:3d} area={c['area']}")
    cb = bbox_of(m_cblue & win)
    print(f"  collar pale-blue union: x={cb[0]}..{cb[2]} y={cb[1]}..{cb[3]} "
          f"(w={cb[2]-cb[0]+1} h={cb[3]-cb[1]+1})")
    for y in [95, 110, 125, 140, 155, 170, 185, 200]:
        print(f"  row y={y}: {fmt(row_classes(lab, y))}")
    print("  neck opening: skin run inside the collar at the collar's top rows (see rows above)")

    # ---- 3. torso silhouette ---------------------------------------------------------------
    print("\n== 3. torso silhouette (figure = not a background tone) ==")
    print("  y | figure x-range (width) | left-edge class | right-edge class | cloth x-range (width)")
    for y in range(100, 440, 10):
        f = runs(figure[y])
        cw = runs(body[y])
        lc = CLASS[lab[y, f[0][0]]] if f else "-"
        rc = CLASS[lab[y, f[-1][1]]] if f else "-"
        ft = f"{f[0][0]}..{f[-1][1]} ({f[-1][1]-f[0][0]+1})" if f else "none"
        ct = f"{cw[0][0]}..{cw[-1][1]} ({cw[-1][1]-cw[0][0]+1})" if cw else "none"
        print(f"  {y:3d} | {ft:18s} | {lc:10s} | {rc:10s} | {ct}")
    print("  right-hand cloth edge per row (step 5) -- where it turns from shoulder into arm:")
    print("  " + " ".join(f"{y}:{(lambda c: c[-1][1] if c else None)(runs(body[y]))}"
                          for y in range(150, 340, 5)))
    print("  left-hand cloth edge per row (step 5):")
    print("  " + " ".join(f"{y}:{(lambda c: c[0][0] if c else None)(runs(body[y]))}"
                          for y in range(110, 400, 5)))

    # ---- 4. sleeves, cuffs, garment regions -------------------------------------------------
    print("\n== 4. sleeves / cuffs / garment regions ==")
    print("  drawn fold / seam lines crossing a row (ink runs strictly inside the cloth span):")
    for y in [170, 200, 230, 260, 290, 320, 350, 380]:
        cs = runs(body[y])
        if not cs:
            continue
        ir = [r for r in runs(m_ink[y] | m_navy[y], 1) if cs[0][0] + 3 < r[0] < cs[-1][1] - 3]
        print(f"    y={y}: " + "  ".join(f"{a}-{b}({b-a+1})" for a, b in ir))
    print("  navy / dark band components (area>=120):")
    for c in comps(m_navy, 120):
        sub = m_navy[c["y"]:c["y"] + c["h"], c["x"]:c["x"] + c["w"]]
        yy, xx = np.nonzero(sub)
        pts = np.stack([xx, yy], 1).astype(float) - [xx.mean(), yy.mean()]
        ev, evec = np.linalg.eigh(np.cov(pts.T))
        ang = np.degrees(np.arctan2(evec[1, -1], evec[0, -1])) % 180
        major = 2 * 2 * np.sqrt(ev[-1])
        thick = c["area"] / max(major, 1.0)
        print(f"    bbox=({c['x']},{c['y']})-({c['x']+c['w']-1},{c['y']+c['h']-1}) w={c['w']:3d} "
              f"h={c['h']:3d} area={c['area']:4d} axis={ang:5.1f}deg major_len~{major:.0f}px thickness=area/major~{thick:.0f}px")
    probe = np.zeros_like(m_dark)
    probe[250:282, 78:116] = True
    print(f"  second cuff (window x78-116,y250-282 from issue 54): dark bbox={bbox_of(m_dark & probe)}")
    win2 = np.zeros_like(m_dark)
    win2[235:258, 78:116] = True
    print(f"  pale cloth sliver above the second cuff (x78-116, y235-258): bbox={bbox_of(m_cloth & win2)}")
    print("  what covers the second cuff: classes in x78-116,y250-300")
    sub = lab[250:300, 78:116]
    cnt = {c: int((np.isin(sub, [i for i, cc in enumerate(CLASS) if cc == c])).sum())
           for c in sorted(set(CLASS))}
    print("    " + " ".join(f"{k}:{v}" for k, v in cnt.items() if v))

    # ---- 5. bow -----------------------------------------------------------------------------
    print("\n== 5. bow ==")
    bc = comps(m_bow, 500)
    m_bow = (m_bow & (cv2.connectedComponents(m_bow.astype(np.uint8), 8)[1] ==
                      cv2.connectedComponents(m_bow.astype(np.uint8), 8)[1][bc[0]["cy"].__int__(), bc[0]["cx"].__int__()]))
    bb = bbox_of(m_bow)
    print(f"bow (largest magenta component) bbox=({bb[0]},{bb[1]})-({bb[2]},{bb[3]}) w={bb[2]-bb[0]+1} h={bb[3]-bb[1]+1} px={bb[4]}")
    print("vertical extent per column (x: y0..y1 (height)), step 6 -- the minimum is the knot waist:")
    hx = {}
    for x in range(bb[0], bb[2] + 1, 6):
        c = np.nonzero(m_bow[:, x])[0]
        if len(c):
            hx[x] = (int(c.min()), int(c.max()), int(c.max() - c.min() + 1))
    print("  " + " ".join(f"{x}:{v[0]}..{v[1]}({v[2]})" for x, v in hx.items()))
    lo = min(x for x in hx if hx[x][2] > 20)  # ignore the thin tail tip at the crop edge
    cand = {x: v for x, v in hx.items() if 175 <= x <= 225}
    kx = min(cand, key=lambda x: cand[x][2])
    print(f"knot waist (narrowest vertical cross-section between the lobes, x in 175..225): "
          f"x={kx} y={hx[kx][0]}..{hx[kx][1]} height={hx[kx][2]}")
    print(f"  bow's first column whose span exceeds 20 px: x={lo} y={hx[lo][0]}..{hx[lo][1]}")
    print("horizontal extent per row (y: x0..x1 (width)), step 8:")
    for y in range(bb[1], bb[3] + 1, 8):
        r = runs(m_bow[y])
        print(f"  y={y}: " + (f"{r[0][0]}..{r[-1][1]} ({r[-1][1]-r[0][0]+1}) runs={r}" if r else "none"))
    lum_all = img.mean(2)
    filled = cv2.morphologyEx(m_bow.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
    interior = cv2.erode(filled, np.ones((9, 9), np.uint8)) > 0
    inner = interior & (lum_all < 112)
    cs = comps(inner, 25)
    print(f"crease/fold lines inside the bow silhouette: {len(cs)} components (>=25 px)")
    for c in cs:
        sub = inner[c["y"]:c["y"] + c["h"], c["x"]:c["x"] + c["w"]]
        yy, xx = np.nonzero(sub)
        pts = np.stack([xx + c["x"], yy + c["y"]], 1).astype(float)
        p0 = pts[0]
        if len(pts) > 3:
            ev, evec = np.linalg.eigh(np.cov(pts.T))
            d = evec[:, -1]
            proj = pts @ d
            p0, p1 = pts[proj.argmin()], pts[proj.argmax()]
            print(f"    area={c['area']:4d} bbox=({c['x']},{c['y']})-({c['x']+c['w']-1},{c['y']+c['h']-1}) "
                  f"len={np.hypot(*(p1-p0)):.0f}px axis={np.degrees(np.arctan2(d[1], d[0])):.0f}deg "
                  f"ends=({p0[0]:.0f},{p0[1]:.0f})->({p1[0]:.0f},{p1[1]:.0f})")
        else:
            print(f"    area={c['area']:4d} bbox=({c['x']},{c['y']})-({c['x']+c['w']-1},{c['y']+c['h']-1})")
    print("bow crossings (rows where the bow's own extent is split by another class):")
    for y in range(bb[1], bb[3] + 1, 4):
        rs = runs(m_bow[y])
        if len(rs) > 1:
            gaps = []
            for i in range(len(rs) - 1):
                a, b = rs[i][1] + 1, rs[i + 1][0] - 1
                cls = [c for c, _, _ in row_classes(lab, y) ]
                seg = lab[y, a:b + 1]
                names = {CLASS[v] for v in seg if CLASS[v] != "edge"}
                gaps.append(f"{a}-{b}={'/'.join(sorted(names)) or 'thin'}")
            print(f"  y={y}: runs={rs} gaps: " + "  ".join(gaps))

    # ---- 6. hair ----------------------------------------------------------------------------
    print("\n== 6. hair masses ==")
    for c in comps(m_hair, 250):
        sub = m_hair[c["y"]:c["y"] + c["h"], c["x"]:c["x"] + c["w"]]
        wrow = sub.sum(1)
        nz = np.nonzero(wrow)[0]
        tip = [(int(y + c["y"]), runs(sub[y])) for y in nz[-6:]]
        dil = cv2.dilate(sub.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        ring = dil & ~sub
        ring_lab = lab[c["y"]:c["y"] + c["h"], c["x"]:c["x"] + c["w"]][ring]
        near = {cc: int((np.isin(ring_lab, [i for i, x in enumerate(CLASS) if x == cc])).sum())
                for cc in sorted(set(CLASS))}
        near = {k: v for k, v in sorted(near.items(), key=lambda kv: -kv[1]) if v > 40}
        ink_in = m_ink[c["y"]:c["y"] + c["h"], c["x"]:c["x"] + c["w"]] & cv2.dilate(
            sub.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        strands = comps(ink_in, 15)
        print(f"  bbox=({c['x']},{c['y']})-({c['x']+c['w']-1},{c['y']+c['h']-1}) w={c['w']} h={c['h']} "
              f"area={c['area']}")
        print(f"    row width: top3={wrow[nz[:3]].mean():.1f} max={wrow.max()} "
              f"at_y={int(nz[wrow[nz].argmax()]) + c['y']} bottom3={wrow[nz[-3:]].mean():.1f}")
        print(f"    tip rows (y: runs): {tip}")
        print(f"    neighbouring classes (5x5 ring, px): {near}")
        print(f"    internal ink lines (>=15 px): {len(strands)}" + (
            "  " + " ".join(f"{s['w']}x{s['h']}@{s['x']+c['x']},{s['y']+c['y']}" for s in strands[:10])))

    # ---- 7. palette samples -----------------------------------------------------------------
    print("\n== 7. palette samples (stated coordinates) ==")
    SAMPLES = {
        "background mint": (30, 260), "background pale blue-grey": (12, 12),
        "background teal (lower right)": (300, 430), "skin lit (cheek)": (180, 20),
        "skin shade (neck)": (240, 60), "blouse white": (200, 300),
        "blouse pale-blue shade": (150, 430), "collar pale blue (back)": (300, 100),
        "navy collar stripe (left leaf)": (151, 110), "navy cuff (right)": (360, 300),
        "navy band, second cuff": (95, 266), "bow magenta (lobe)": (140, 175),
        "bow dark (fold shadow)": (140, 205), "hair blue (left mass)": (60, 60),
        "hair blue (right mass)": (370, 200), "lower cloth (lap)": (60, 450),
        "periwinkle band (left edge)": (12, 222),
    }
    for name, (x, y) in SAMPLES.items():
        px = img[y, x]
        print(f"  {name:32s} ({x:3d},{y:3d}) = ({int(px[0]):3d},{int(px[1]):3d},{int(px[2]):3d}) "
              f"#%02x%02x%02x" % tuple(int(v) for v in px))

    # ---- 8. ink widths ----------------------------------------------------------------------
    print("\n== 8. ink widths (longest dark run within +/-7 px of the probe; dark = luminance < 100,")
    print("          which excludes hair blue #3b71a1 at luminance 113) ==")
    lum = img.mean(2)

    def width_at(x, y, axis, win=7):
        """Longest dark run inside +/-win px of the probe, with its offset from the probe centre."""
        seg = lum[y, max(0, x - win):x + win + 1] if axis == "row" else lum[max(0, y - win):y + win + 1, x]
        dark = seg < 100
        best, i = (0, None), 0
        while i < len(dark):
            if dark[i]:
                j = i
                while j + 1 < len(dark) and dark[j + 1]:
                    j += 1
                if j - i + 1 > best[0]:
                    best = (j - i + 1, i - win)
                i = j + 1
            else:
                i += 1
        return best

    for name, x, y, axis in [
        ("figure silhouette, torso left (row 240)", 68, 240, "row"),
        ("figure silhouette, torso left (row 300)", 70, 300, "row"),
        ("silhouette against cloth, right (row 200)", 396, 200, "row"),
        ("collar navy stripe, upper edge (col 156)", 156, 122, "col"),
        ("cuff navy band, upper edge (col 370)", 370, 280, "col"),
        ("bow outline, left edge (row 200)", 118, 200, "row"),
        ("hair mass outline (row 300)", 70, 300, "row"),
        ("dark band at chest centre (row 320)", 155, 320, "row"),
        ("hair strand inside the mass (col 330)", 330, 60, "col"),
    ]:
        w, off = width_at(x, y, axis)
        print(f"  {name:38s} probe ({x},{y}) {axis}: {w} px dark, {'' if off is None else f'offset {off:+d}'}")
    print("  a colour boundary drawn with no line reads 0 by this method (see the cloth_blue edges).")

    print("\n== 9. uncertainty ==")
    print("  * JPEG noise: nearest-anchor assignment flips near two anchors ~10 RGB apart; the worst")
    print("    pair is blouse white #e3e7db vs lower pale cloth #d5e1d7 (b-r differs by 7).")
    print("  * The background has four values (mint, pale blue-grey, pale highlight, teal). 'figure'")
    print("    excludes all four, so a pale garment matching bg_pale would be dropped; no number above")
    print("    depends on such a region except the lower-left corner of the lap.")
    print("  * Occlusion: the right shoulder edge is behind the right hair mass, the left cuff behind")
    print("    the bow tail, the neck's right edge behind a hair lock. Those rows report the occluder.")
    print("  * Band thickness uses 2 sigma along the minor PCA axis: it assumes the band is an elongated")
    print("    blob and reads wide where two bounds of a band merge at a corner.")
    print("  * Ink width is one scan per class; it does not separate line weight by intent.")


if __name__ == "__main__":
    main()
