#!/usr/bin/env python3
"""scene_render.py — compile a scene.yaml (object-level drawing nodes) to SVG, render to PNG.

Spec: docs/drawing/scene-format.md
"""
import argparse, math, os, re, subprocess, sys
import yaml
try:
    import cv2
except ImportError as e:
    raise SystemExit(f"scene_render needs cv2 in the active interpreter: {e}; use .venv/bin/python")
import numpy as np

CHROME = os.path.expanduser(
    "~/.cache/ms-playwright/chromium_headless_shell-1234/"
    "chrome-headless-shell-linux64/chrome-headless-shell")

# per-type allowed keys; first key listed is the id-bearing type key
# SA3 starry probe copy: +desc on every type (resolver vocabulary carries intent comments),
# +poly (sharp, un-smoothed polygon — roofs), +swirl/+burst/+hill generators.
_DESC = {"desc"}
SCHEMA = {
    "layers": {"layers"},
    "rect":   {"rect", "at", "w", "h", "full", "fill", "z", "op", "rot"} | _DESC,
    "ellipse":{"ellipse", "at", "rx", "ry", "rot", "fill", "stroke", "sw", "z", "op", "blur"} | _DESC,
    "stroke": {"stroke", "spine", "w", "profile", "taper", "ink", "cap", "z", "op", "blur"} | _DESC,
    "blob":   {"blob", "poly", "spine", "w", "fill", "stroke", "sw", "z", "op", "blur", "rot"} | _DESC,
    "poly":   {"poly", "pts", "fill", "stroke", "sw", "z", "op"} | _DESC,
    "petal":  {"petal", "at", "n", "len", "wid", "curl", "spread", "angle0", "fill", "stroke", "sw", "z", "op", "blur"} | _DESC,
    "ribbon": {"ribbon", "spine", "w", "grad", "fill", "op", "z", "blur"} | _DESC,
    "region": {"region", "seed", "tol", "on", "fill", "grow", "z", "op"} | _DESC,
    "trace":  {"trace", "from", "class", "fit", "region", "z", "op", "fill"} | _DESC,
    "grad":   {"grad", "dir", "at", "r", "stops", "z"} | _DESC,
    "blur":   {"blur", "std"},
    "wave":   {"wave", "spine", "w", "amp", "len", "sag", "taper", "fill", "grad", "op", "z", "blur"} | _DESC,
    "strands": {"strands", "region", "n", "dir", "spread", "w", "wj", "ink", "op", "len", "z", "seed"} | _DESC,
    "ring":   {"ring", "at", "r", "w", "a0", "a1", "zig", "zn", "zq", "d0", "seed",
                "hue", "sat", "val", "nseg", "z", "op", "blur", "rx", "ry", "rot"} | _DESC,
    "swirl":  {"swirl", "at", "rx", "ry", "rot", "a0", "sweep", "bands", "w", "gap",
                "n", "wob", "cap", "hue", "sat", "val", "ink", "seed", "z", "op"} | _DESC,
    "burst":  {"burst", "at", "rays", "len", "w0", "w1", "a0", "spread", "ink", "seed", "z", "op"} | _DESC,
    "hill":   {"hill", "y0", "bands", "amp", "wl", "colors", "seed", "z", "op"} | _DESC,
}
TYPE_KEY = {"layers": "layers", "grad": "grad", "blur": "blur",
            "rect": "rect", "ellipse": "ellipse", "stroke": "stroke", "blob": "blob",
            "poly": "poly", "petal": "petal", "ribbon": "ribbon", "region": "region", "trace": "trace",
            "wave": "wave", "strands": "strands", "ring": "ring",
            "swirl": "swirl", "burst": "burst", "hill": "hill"}


def smooth_path(pts, closed=True):
    pts = [tuple(map(float, p)) for p in pts]
    if closed and pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    d = f"M {pts[0][0]:.0f} {pts[0][1]:.0f} "
    for i in range(1, len(pts) - 1):
        mx = (pts[i][0] + pts[i + 1][0]) / 2
        my = (pts[i][1] + pts[i + 1][1]) / 2
        d += f"Q {pts[i][0]:.0f} {pts[i][1]:.0f} {mx:.0f} {my:.0f} "
    return d + ("Z" if closed else f"L {pts[-1][0]:.0f} {pts[-1][1]:.0f}")


def resample(spine, n=24):
    """Resample a polyline to n points evenly by arc length."""
    pts = [np.array(p, float) for p in spine]
    if len(pts) < 2:
        return [pts[0]] * n
    pts_arr = np.array(pts)
    seg = np.linalg.norm(np.diff(pts_arr, axis=0), axis=1)
    total = float(seg.sum()) or 1.0
    ts = np.linspace(0.0, total, n)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    out = []
    for t in ts:
        j = int(np.searchsorted(cum, t, side="right") - 1)
        j = min(max(j, 0), len(seg) - 1)
        u = 0.0 if seg[j] == 0 else (t - cum[j]) / seg[j]
        out.append(pts_arr[j] + (pts_arr[j+1] - pts_arr[j]) * u)
    return out


def taper_outline(spine, width_at):
    """Closed outline polygon around spine with per-point width (taper)."""
    pts = [np.array(p, float) for p in resample(spine, max(12, len(spine)*2))]
    n = len(pts)
    left, right = [], []
    for i, p in enumerate(pts):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i+1] - pts[i-1]
        t = t / (np.linalg.norm(t) or 1.0)
        nrm = np.array([-t[1], t[0]])
        w = width_at(i / (n - 1)) / 2
        left.append(tuple(p + nrm * w))
        right.append(tuple(p - nrm * w))
    return smooth_path(left + right[::-1], closed=True)


def petal_path(at, angle, length, width, curl):
    """One petal: spine from `at` outward, bending by curl, elliptical width profile."""
    ax, ay = at
    a = np.deg2rad(angle)
    tip = np.array([ax + np.cos(a)*length, ay + np.sin(a)*length])
    mid = np.array([ax + np.cos(a)*length*0.5, ay + np.sin(a)*length*0.5])
    nrm = np.array([-np.sin(a), np.cos(a)])
    mid = mid + nrm * curl * length * 0.35
    spine = [np.array([ax, ay]), mid, tip]
    pts = [np.array(p, float) for p in resample(spine, 14)]
    n = len(pts)
    left, right = [], []
    for i, p in enumerate(pts):
        if i == 0: t = pts[1] - pts[0]
        elif i == n-1: t = pts[-1] - pts[-2]
        else: t = pts[i+1] - pts[i-1]
        t = t / (np.linalg.norm(t) or 1.0)
        nrm2 = np.array([-t[1], t[0]])
        prof = max(0.0, np.sin(np.pi * i / (n - 1))) ** 0.8 * width / 2   # elliptical width profile
        left.append(tuple(p + nrm2 * prof))
        right.append(tuple(p - nrm2 * prof))
    return smooth_path(left + right[::-1], closed=True)


def flood_region(ref_bgr, seed, tol):
    """Paint-bucket on the reference raster from seed with tolerance; returns outer contour pts."""
    h, w = ref_bgr.shape[:2]
    sx, sy = int(seed[0]), int(seed[1])
    if not (0 <= sx < w and 0 <= sy < h):
        raise ValueError(f"region seed {seed} outside image")
    m = np.zeros((h+2, w+2), np.uint8)
    lo, hi = int(tol), int(tol)
    cv2.floodFill(ref_bgr.copy(), m, (sx, sy), 0, (lo,)*3, (hi,)*3,
                  cv2.FLOODFILL_MASK_ONLY | (255 << 8))
    mask = m[1:-1, 1:-1]
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        raise ValueError(f"region seed {seed}: empty mask")
    c = max(cnts, key=cv2.contourArea)
    return cv2.approxPolyDP(c, 6, True).reshape(-1, 2).tolist()


def wave_spine(spine, amp, wl, sag, n=40):
    """Resample spine, displace perpendicular by amp*sin, droop by sag along x-progress (gravity +y)."""
    pts = resample(spine, n)
    P = np.array(pts)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    s = s / (s[-1] or 1.0)
    x0, x1 = P[0][0], P[-1][0]
    out = []
    for i, p in enumerate(P):
        t = P[min(i+1, len(P)-1)] - P[max(i-1, 0)]
        t = t / (np.linalg.norm(t) or 1.0)
        nrm = np.array([-t[1], t[0]])
        disp = amp * np.sin(2*np.pi * s[i] * (np.linalg.norm(np.array(spine[-1])-np.array(spine[0])) / max(wl,1)))
        droop = sag * (p[0] - x0) / max(x1 - x0, 1) * 100
        out.append(p + nrm*disp + [0, droop])
    return [list(map(float, q)) for q in out]


def wave_node(node):
    """Compile a wave node to a closed ribbon path."""
    spine = wave_spine(node["spine"], float(node.get("amp", 10)),
                       float(node.get("len", 200)), float(node.get("sag", 0)))
    w = float(node.get("w", 40))
    taper = node.get("taper", "none")
    wfun = (lambda t: w * (1 - t)) if taper == "end" else \
           (lambda t: w * (1 - abs(2*t - 1))) if taper == "both" else (lambda t: w)
    return taper_outline(spine, wfun)


def strand_paths(node):
    """Generate n deterministic strands inside region flowing along dir."""
    x0, y0, x1, y1 = node["region"]
    n = int(node.get("n", 8))
    base_dir = float(node.get("dir", 90))
    spread = float(node.get("spread", 20))
    w = float(node.get("w", 3))
    wj = float(node.get("wj", 0.4))
    ln = float(node.get("len", 60))
    rng = np.random.default_rng(int(node.get("seed", 7)))
    inks = node.get("ink", "#000")
    if isinstance(inks, str): inks = [inks]
    out = []
    for i in range(n):
        sx = rng.uniform(x0, x1); sy = rng.uniform(y0, y1)
        ang = np.radians(base_dir + rng.uniform(-spread, spread))
        L = ln * rng.uniform(0.8, 1.2)
        ex, ey = sx + L*np.cos(ang), sy + L*np.sin(ang)
        bow = rng.uniform(-0.12, 0.12) * L
        mx, my = (sx+ex)/2 - np.sin(ang)*bow, (sy+ey)/2 + np.cos(ang)*bow
        wi = w * rng.uniform(1-wj, 1+wj)
        ink = inks[i % len(inks)]
        out.append((f'M {sx:.0f} {sy:.0f} Q {mx:.0f} {my:.0f} {ex:.0f} {ey:.0f}', ink, f'{wi:.1f}'))
    return out


def hsv_to_hex(h, s, v):
    """h in [0,360), s/v in [0,1] -> '#rrggbb'."""
    import colorsys
    r, g, b = colorsys.hsv_to_rgb((h % 360.0) / 360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return "#%02x%02x%02x" % (int(r*255), int(g*255), int(b*255))


def tri_zigzag(phi):
    """Triangle wave in [-1,1], period 1, sharp peaks at integer phi (zig-zag)."""
    p = phi - math.floor(phi)
    return 2.0 * abs(2.0 * p - 1.0) - 1.0


def ring_segments(node):
    """Compile a ring node to a list of (path_d, hex_color) segments.

    Continuous color-changing annulus arc with a zig-zag outer edge. Hue walks
    hue[0]->hue[1] along the arc; the arc is sliced into nseg filled segments so
    the colour change reads as a rainbow band, not a flat fill.

    Zig-zag phase is purely angular (tooth index = floor(a*zn/2pi)), so two ring
    nodes sharing geometry/seed but complementary a0..a1 (back + front halves,
    different z values) produce teeth that line up exactly at the seam — a
    z-plane split, not a manual path split. Jitter is per-angular-tooth from seed,
    so both halves agree everywhere.
    """
    cx, cy = node["at"]
    r = float(node.get("r", 300))
    rx = float(node.get("rx", r))   # elliptical support: rx/ry default to circular r
    ry = float(node.get("ry", r))
    rot = math.radians(float(node.get("rot", 0)))
    w = float(node.get("w", 60))
    a0 = math.radians(float(node.get("a0", 0)))
    a1 = math.radians(float(node.get("a1", 360)))
    zig = float(node.get("zig", 0.15))       # zigzag depth as fraction of w
    zn = int(node.get("zn", 24))             # teeth per full revolution
    zq = float(node.get("zq", 0.0))          # 0..1 random depth jitter (seeded)
    seed = int(node.get("seed", 7))
    hue0, hue1 = map(float, node.get("hue", [0.0, 300.0]))
    sat = float(node.get("sat", 0.75)); val = float(node.get("val", 0.9))
    nseg = int(node.get("nseg", 24))
    if a1 < a0:
        a1 += 2 * math.pi
    span = a1 - a0
    rng = np.random.default_rng(seed)
    jit = rng.uniform(1 - zq, 1 + zq, zn) if zq > 0 else np.ones(zn)

    segs = []
    N = 8  # samples per segment edge (outer + inner) for smooth curving
    cos_r, sin_r = math.cos(rot), math.sin(rot)
    for s in range(nseg):
        t0 = a0 + span * s / nseg
        t1 = a0 + span * (s + 1) / nseg
        tm = (t0 + t1) / 2
        h = hue0 + (hue1 - hue0) * ((tm - a0) / span)
        outer, inner = [], []
        for k in range(0, N + 1):
            a = t0 + (t1 - t0) * k / N
            tooth = int(math.floor(a * zn / (2 * math.pi))) % zn  # absolute-angle index
            amp = zig * w * jit[tooth] * tri_zigzag(a * zn / (2 * math.pi))
            # param point on ellipse, then rotate+translate; amp scales band half-width
            # along the radial direction (approx: scale the ellipse radii)
            ux, uy = math.cos(a), math.sin(a)
            def pt(kk):
                ex, ey = (rx + kk) * ux, (ry + kk) * uy
                return (cx + ex * cos_r - ey * sin_r, cy + ex * sin_r + ey * cos_r)
            outer.append(pt(w / 2 + amp))
            inner.append(pt(-w / 2))
        pts = outer + inner[::-1]
        segs.append((smooth_path(pts, closed=True), hsv_to_hex(h, sat, val)))
    return segs


# --------------------------------------------------------------------------------------
# SA3 starry probe generators: swirl / burst / hill — engine, not teacher (no reference)
# --------------------------------------------------------------------------------------

def swirl_paths(node):
    """Nested spiral ribbon bands around an elliptical centre — the sky's flow, coiled.

    Each band is one Archimedean spiral stroke: radius grows from the band's inner edge to
    its outer edge across `sweep` degrees, on an ellipse of half-extents (rx, ry) rotated
    by `rot`. Bands nest outside-in; hue walks hue[0] (innermost, brightest) to hue[1]
    (outermost). `wob` wobbles the radius per sample from `seed` so coils read as brush
    strokes, not compass arcs. Constant width per band; sky shows through `gap`.
    """
    cx, cy = float(node["at"][0]), float(node["at"][1])
    rx = float(node.get("rx", 300)); ry = float(node.get("ry", rx))
    rot = math.radians(float(node.get("rot", 0)))
    a0 = math.radians(float(node.get("a0", 0)))
    sweep = math.radians(float(node.get("sweep", 560)))
    bands = int(node.get("bands", 4))
    w = float(node.get("w", 26))
    gap = float(node.get("gap", 18))
    n = int(node.get("n", 72))
    wob = float(node.get("wob", 0.05))
    hue0, hue1 = map(float, node.get("hue", [195, 235]))
    sat = float(node.get("sat", 0.5)); val = float(node.get("val", 0.85))
    ink = node.get("ink")
    rng = np.random.default_rng(int(node.get("seed", 7)))
    rmax = bands * (w + gap)                      # outer edge of the outermost band
    cos_r, sin_r = math.cos(rot), math.sin(rot)
    out = []
    # centre cap: the first coil cannot itself reach radius 0, so without a cap the sky
    # shows through as a dark dot (the v1 render read as three giant "eyes"). Fill it.
    cap_f = float(node.get("cap", 0.62))
    if cap_f > 0:
        cap = [smooth_path([(cx + (cap_f * w / rmax) * rx * math.cos(2 * math.pi * i / 40),
                             cy + (cap_f * w / rmax) * ry * math.sin(2 * math.pi * i / 40))
                            for i in range(41)], closed=True),
               hsv_to_hex(hue0, sat, val)]
    else:
        cap = None
    for b in range(bands - 1, -1, -1):            # outermost first -> innermost paints on top
        s_in, s_out = b * (w + gap), b * (w + gap) + w
        ph1 = rng.uniform(0, 2 * math.pi)
        ph2 = rng.uniform(0, 2 * math.pi)
        drift = rng.uniform(-1, 1, 2) * wob * 40  # gentle per-band centre drift (organic)
        spine = []
        for k in range(n + 1):
            u = k / n
            th = a0 + sweep * u
            s = s_in + (s_out - s_in) * (u ** 1.1)
            wobble = 1 + wob * (0.6 * math.sin(3 * th + ph1) + 0.4 * math.sin(7 * th + ph2))
            ex = (s / rmax) * rx * math.cos(th) * wobble + drift[0] * u
            ey = (s / rmax) * ry * math.sin(th) * wobble + drift[1] * u
            spine.append((cx + ex * cos_r - ey * sin_r, cy + ex * sin_r + ey * cos_r))
        t = b / max(bands - 1, 1)
        color = ink or hsv_to_hex(hue0 + (hue1 - hue0) * t, sat, val)
        out.append((taper_outline(spine, lambda _t, _w=w: _w), color))
    if cap is not None:
        out.insert(0, cap)                          # cap behind every band
    return out


def burst_paths(node):
    """Radial rays around `at`, tapering w0 (core) -> w1 (tip), seeded length/angle jitter."""
    ax, ay = float(node["at"][0]), float(node["at"][1])
    rays = int(node.get("rays", 8))
    ln = float(node.get("len", 80))
    w0 = float(node.get("w0", 9)); w1 = float(node.get("w1", 1))
    a0 = math.radians(float(node.get("a0", 0)))
    spread = math.radians(float(node.get("spread", 360)))
    rng = np.random.default_rng(int(node.get("seed", 7)))
    out = []
    for i in range(rays):
        ang = a0 + spread * (i + 0.5 + rng.uniform(-0.25, 0.25)) / rays
        L = ln * rng.uniform(0.82, 1.18)
        spine = [(ax, ay), (ax + math.cos(ang) * L, ay + math.sin(ang) * L)]
        out.append(taper_outline(spine, lambda t, a=w0, b=w1: a + (b - a) * t))
    return out


def hill_paths(node, W, H):
    """Stacked rolling bands below a horizon line, far (light, painted first) to near (dark).

    Band i's top edge is a two-harmonic sine around baseline y0 + i*band_h; the band fills
    down to the frame bottom, so nearer bands overlap farther ones (occlusion is the
    renderer's job). Amplitude and wavelength grow slightly toward the viewer; phases are
    seeded so the same spec -> same hills.
    """
    y0 = float(node.get("y0", 0.62 * H))
    bands = int(node.get("bands", 4))
    amp = float(node.get("amp", 40))
    wl = float(node.get("wl", 380))
    colors = node.get("colors") or [hsv_to_hex(205 + 18 * i, 0.45, 0.62 - 0.09 * i)
                                    for i in range(bands)]
    rng = np.random.default_rng(int(node.get("seed", 7)))
    band_h = (H - y0) / bands
    xs = np.linspace(-4, W + 4, 160)
    out = []
    for i in range(bands):
        base = y0 + i * band_h
        a1 = amp * (0.35 + 0.65 * i / max(bands - 1, 1))
        a2 = a1 * rng.uniform(0.25, 0.5)
        l1 = wl * rng.uniform(0.85, 1.15)
        l2 = l1 * rng.uniform(0.4, 0.6)
        ph1 = rng.uniform(0, 2 * math.pi)
        ph2 = rng.uniform(0, 2 * math.pi)
        top = [float(base + a1 * math.sin(2 * math.pi * x / l1 + ph1)
                     + a2 * math.sin(2 * math.pi * x / l2 + ph2)) for x in xs]
        pts = [(float(x), y) for x, y in zip(xs, top)]
        pts += [(float(W + 4), float(H + 4)), (-4.0, float(H + 4))]
        out.append((smooth_path(pts, closed=True), colors[i % len(colors)]))
    return out


def compile_scene(nodes, size, ref_path=None):
    W, H = size
    # line numbers: yaml.safe_load loses them; re-walk source for id->line mapping
    defs, body = [], []
    layers = ["default"]
    blur_filters = {}
    grads = {}
    errors = []
    ref = cv2.imread(ref_path) if ref_path else None

    # first pass: schema validation + gather
    for idx, node in enumerate(nodes):
        if not isinstance(node, dict) or len(node) < 1:
            errors.append(f"node#{idx}: not a dict"); continue
        tkey = next(iter(node))
        if tkey not in SCHEMA:
            errors.append(f"node#{idx}: unknown node type '{tkey}'"); continue
        allowed = SCHEMA[tkey]
        extra = set(node) - allowed
        if extra:
            errors.append(f"node#{idx} ({tkey}): unknown keys {sorted(extra)}")
    if errors:
        raise SystemExit("scene errors:\n" + "\n".join(errors))

    # find layers node
    for node in nodes:
        if "layers" in node and isinstance(node["layers"], list):
            layers = [str(x) for x in node["layers"]] + ["default"]
            break

    def zindex(n):
        z = str(n.get("z", "default"))
        return layers.index(z) if z in layers else len(layers)

    ordered = sorted([n for n in nodes if "layers" not in n or n is nodes[0]],
                     key=lambda n: (zindex(n),))
    # stable doc order within layer: python sort is stable, iterate doc order
    ordered = [n for n in nodes if "layers" in n and isinstance(n.get("layers"), list)]
    ordered += sorted([n for n in nodes if not ("layers" in n and isinstance(n.get("layers"), list))],
                      key=zindex)

    # collect grads
    for node in nodes:
        if node.get("grad") and "stops" in node:
            grads[node["grad"]] = node

    svg_defs = []
    for name, g in grads.items():
        stops = g["stops"]
        if g.get("dir") == "radial":
            svg_defs.append(f'<radialGradient id="{name}">' +
                            "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) +
                            "</radialGradient>")
        else:
            x1, y1, x2, y2 = g.get("dir", [0, 0, 0, 1])
            svg_defs.append(f'<linearGradient id="{name}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">' +
                            "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) +
                            "</linearGradient>")
    for bid, std in blur_filters.items():
        svg_defs.append(f'<filter id="blur-{bid}" x="-30%" y="-30%" width="160%" height="160%">'
                        f'<feGaussianBlur stdDeviation="{std}"/></filter>')

    used_blurs = {}
    for node in ordered:
        tkey = next(iter(node))
        nid = node.get(tkey, f"{tkey}-{len(body)}")
        z = str(node.get("z", "default"))
        op = node.get("op", 1)
        common = f'id="{nid}"'
        if op != 1:
            common += f' opacity="{op}"'
        bv = node.get("blur")
        if bv is not None and tkey != "blur" and isinstance(bv, (int, float)):
            used_blurs[nid] = float(bv)  # per-node feathering (shadows etc.)
        s = ""
        if tkey == "rect":
            if node.get("full"):
                at, w, h = [0, 0], W, H
            else:
                at, w, h = node.get("at", [0, 0]), node.get("w", W), node.get("h", H)
            fill = node.get("fill", "#000")
            fill = f"url(#{fill.split(':')[1]})" if str(fill).startswith("grad:") else fill
            s = f'<rect {common} x="{at[0]}" y="{at[1]}" width="{w}" height="{h}" fill="{fill}"/>'
        elif tkey == "ellipse":
            fill = node.get("fill", "#000")
            fill = f"url(#{fill.split(':')[1]})" if str(fill).startswith("grad:") else fill
            rot = node.get("rot", 0)
            tr = f' transform="rotate({rot} {node["at"][0]} {node["at"][1]})"' if rot else ""
            st = f' stroke="{node["stroke"]}" stroke-width="{node.get("sw",3)}"' if node.get("stroke") else ""
            s = f'<ellipse {common} cx="{node["at"][0]}" cy="{node["at"][1]}" rx="{node["rx"]}" ry="{node["ry"]}"{tr} fill="{fill}"{st}/>'
        elif tkey == "stroke":
            ink = node.get("ink", "#000")
            if node.get("profile") or node.get("taper", "none") != "none":
                wid = node.get("w", 6)
                if node.get("profile"):
                    prof = dict((t, w) for t, w in node["profile"])
                    wfun = lambda t: np.interp(t, list(prof), list(prof.values()))
                else:
                    mode = node["taper"]
                    wfun = (lambda t: wid * (1 - t)) if mode == "start" else \
                           (lambda t: wid * t) if mode == "end" else \
                           (lambda t: wid * (1 - abs(2*t - 1)))
                d = taper_outline(node["spine"], wfun)
                s = f'<path {common} d="{d}" fill="{ink}"/>'
            else:
                d = smooth_path(node["spine"], closed=False)
                cap = node.get("cap", "round")
                s = f'<path {common} d="{d}" fill="none" stroke="{ink}" stroke-width="{node.get("w",6)}" stroke-linecap="{cap}"/>'
        elif tkey in ("blob", "ribbon"):
            fill = node.get("fill")
            if str(fill).startswith("grad:"):
                fill = f"url(#{fill.split(':')[1]})"
            elif node.get("grad"):
                fill = f"url(#{node['grad']})"
            if fill is None:
                fill = "none" if node.get("stroke") else "#888"  # stroke-only blob = outline
            stroke = f' stroke="{node["stroke"]}" stroke-width="{node.get("sw",3)}"' if node.get("stroke") else ""
            if "poly" in node:
                d = smooth_path(node["poly"], closed=True)
            else:
                w = node.get("w", 40)
                d = taper_outline(node["spine"], lambda t: w)
            s = f'<path {common} d="{d}" fill="{fill}"{stroke}/>'
        elif tkey == "petal":
            paths = []
            n = int(node.get("n", 5))
            spread = float(node.get("spread", 180))
            a0 = float(node.get("angle0", -90))
            step = spread / max(n - 1, 1)
            for k in range(n):
                ang = a0 + k * step
                paths.append(petal_path(node["at"], ang, node.get("len", 80), node.get("wid", 40), float(node.get("curl", 0.3))))
            fill = node.get("fill", "#f2b8c4")
            if str(fill).startswith("grad:"):
                fill = f"url(#{fill.split(':')[1]})"
            st = f' stroke="{node["stroke"]}" stroke-width="{node.get("sw",2)}"' if node.get("stroke") else ""
            s = f'<g {common}>{"".join(f"<path d={chr(34)}{p}{chr(34)} fill={chr(34)}{fill}{chr(34)}{st}/>" for p in paths)}</g>'
        elif tkey == "region":
            if ref is None:
                raise SystemExit(f"node {nid}: region needs --ref")
            pts = flood_region(ref, node["seed"], node.get("tol", 30))
            d = smooth_path(pts, closed=True)
            s = f'<path {common} d="{d}" fill="{node.get("fill","#888")}"/>'
        elif tkey == "trace":
            if ref is None:
                raise SystemExit(f"node {nid}: trace needs --ref")
            b, g, r = ref[:,:,0].astype(int), ref[:,:,1].astype(int), ref[:,:,2].astype(int)
            classes = {
                "hair": (b>r+30)&(b>120)&(r<120),
                "navy": (r<95)&(g<110)&(b<135),
                "pale": (r>195)&(g>200)&(b>170),
                "green": (g>r+15)&(g>130)&(b>g-45),
                "pink": (r>200)&(g>120)&(g<200)&(b>140),
            }
            cls = node.get("class", "hair")
            mask = classes[cls].astype(np.uint8)
            reg = node.get("region")
            if reg:
                x0,y0,x1,y1 = reg
                mm = np.zeros_like(mask); mm[y0:y1, x0:x1] = 1
                mask = mask * mm
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15,15),np.uint8))
            cnts,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            c = max(cnts, key=cv2.contourArea)
            d = smooth_path(cv2.approxPolyDP(c, 10, True).reshape(-1,2))
            s = f'<path {common} d="{d}" fill="{node.get("fill","#888")}"/>'
        elif tkey == "wave":
            fill = node.get("fill")
            if str(fill).startswith("grad:"):
                fill = f"url(#{fill.split(':')[1]})"
            elif node.get("grad"):
                fill = f"url(#{node['grad']})"
            fill = fill or "#888"
            d = wave_node(node)
            s = f'<path {common} d="{d}" fill="{fill}"/>'
        elif tkey == "strands":
            # note: op already embedded in `common`; do NOT emit it twice (duplicate attr = invalid XML)
            paths = "".join(f'<path d="{p}" fill="none" stroke="{ink}" stroke-width="{wi}" stroke-linecap="round"/>'
                            for p, ink, wi in strand_paths(node))
            s = f'<g {common}>{paths}</g>'
        elif tkey == "ring":
            # Each angular slice owns a flat colour; together they read as a continuous hue walk.
            # A back/front scene split is two complementary ring nodes sharing at/r/w/seed.
            paths = "".join(f'<path d="{d}" fill="{color}"/>'
                            for d, color in ring_segments(node))
            s = f'<g {common}>{paths}</g>'
        elif tkey == "poly":
            # sharp (un-smoothed) polygon — roofs, steeples, anything with deliberate corners
            pts = node["pts"]
            d = "M " + " L ".join(f'{float(x):.1f} {float(y):.1f}' for x, y in pts) + " Z"
            fill = node.get("fill", "#888")
            st = f' stroke="{node["stroke"]}" stroke-width="{node.get("sw",3)}"' if node.get("stroke") else ""
            s = f'<path {common} d="{d}" fill="{fill}"{st}/>'
        elif tkey == "swirl":
            paths = "".join(f'<path d="{d}" fill="{color}"/>' for d, color in swirl_paths(node))
            s = f'<g {common}>{paths}</g>'
        elif tkey == "burst":
            paths = "".join(f'<path d="{d}" fill="{node.get("ink", "#ffd75e")}"/>'
                            for d in burst_paths(node))
            s = f'<g {common}>{paths}</g>'
        elif tkey == "hill":
            paths = "".join(f'<path d="{d}" fill="{color}"/>' for d, color in hill_paths(node, W, H))
            s = f'<g {common}>{paths}</g>'
        elif tkey == "blur":
            ids = node["blur"]
            std = float(node.get("std", 6))
            if isinstance(ids, str): ids = [ids]
            for i in ids:
                used_blurs[i] = std
            continue  # applied as attribute injection below
        body.append(s)

    # inject blur filters into targeted nodes
    if used_blurs:
        for i, s in enumerate(body):
            m = re.search(r'id="([^"]+)"', s)
            if m and m.group(1) in used_blurs:
                std = used_blurs[m.group(1)]
                s2 = re.sub(r'^<(\w+) ', rf'<\1 filter="url(#blur-{std})" ', s)
                if f'blur-{std}' not in svg_defs and f'blur-{std}' not in "".join(svg_defs):
                    svg_defs.append(f'<filter id="blur-{std}" x="-30%" y="-30%" width="160%" height="160%">'
                                    f'<feGaussianBlur stdDeviation="{std}"/></filter>')
                body[i] = s2

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
           f'<defs>{"".join(svg_defs)}</defs>{"".join(body)}</svg>')
    return svg


def chrome(svg_path, png_path, size):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    f"--screenshot={os.path.abspath(png_path)}",
                    f"--window-size={size[0]},{size[1]}",
                    "file://" + os.path.abspath(svg_path)],
                   check=True, capture_output=True, timeout=60)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--svg", default=None)
    ap.add_argument("--ref", default=None)
    ap.add_argument("--size", default=None)
    a = ap.parse_args()
    nodes = yaml.safe_load(open(a.scene))
    if not isinstance(nodes, list):
        raise SystemExit("scene file top level must be a YAML list")
    size = tuple(map(int, a.size.split("x"))) if a.size else (1024, 1024)
    svg = compile_scene(nodes, size, a.ref)
    svg_path = a.svg or (a.out + ".svg")
    os.makedirs(os.path.dirname(os.path.abspath(svg_path)), exist_ok=True)
    open(svg_path, "w").write(svg)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    chrome(svg_path, a.out, size)
    print(a.out)


if __name__ == "__main__":
    main()
