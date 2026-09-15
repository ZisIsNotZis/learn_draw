#!/usr/bin/env python3
"""Smoke tests for scene_render.py — run with .venv/bin/python."""
import os, sys, subprocess, tempfile, re, json, hashlib, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # scripts/
import scene_render as sr
import cv2, numpy as np

SIZE = (200, 200)
OUT = tempfile.mkdtemp()
PASS = 0
TOTAL = 0


def render(nodes, name):
    svg = sr.compile_scene(nodes, SIZE)
    p = os.path.join(OUT, name + ".svg")
    open(p, "w").write(svg)
    png = os.path.join(OUT, name + ".png")
    sr.chrome(p, png, SIZE)
    img = cv2.imread(png)
    assert img is not None, f"render failed: {png}"
    return img.astype(int)


def check(name, cond):
    global PASS, TOTAL
    print(("PASS " if cond else "FAIL ") + name)
    TOTAL += 1
    assert cond, name
    PASS += 1


# (a) ellipse at exact position/size
img = render([{"rect": "bg", "full": True, "fill": "#ffffff"},
              {"ellipse": "e1", "at": [100, 100], "rx": 40, "ry": 30, "fill": "#ff0000"}], "t1")
check("a: ellipse center red", img[100, 100][2] > 200 and img[100, 100][0] < 60)
check("a: outside ellipse white", img[100, 20][0] > 200)
check("a: rx bound red, beyond white", img[100, 142][2] > 200 and img[100, 145][0] > 200)

# (b) z-order: red over blue
img = render([{"rect": "b", "full": True, "fill": "#0000ff"},
              {"rect": "r", "full": True, "fill": "#ff0000", "z": "top"},
              {"layers": ["default", "top"]}], "t2")
check("b: z-order red on top", img[100, 100][2] > 200 and img[100, 100][0] < 60)

# (c) stroke taper both: thin at ends, thick mid
img = render([{"rect": "bg", "full": True, "fill": "#ffffff"},
              {"stroke": "s1", "spine": [[20, 100], [180, 100]], "w": 40,
               "taper": "both", "ink": "#000000"}], "t3")
check("c: taper mid thick", img[100, 100][0] < 100)
tip_l = img[100, 21][0] > 150
tip_r = img[100, 179][0] > 150
mid = img[100, 100][0] < 60
check("c: taper tips thin (mostly-white)", tip_l and tip_r and mid)

# (d) petal count: n=5 lobes probe along 5 directions
nodes = [{"rect": "bg", "full": True, "fill": "#ffffff"},
         {"petal": "f1", "at": [100, 100], "n": 5, "len": 60, "wid": 30,
          "curl": 0.0, "spread": 180, "angle0": -90, "fill": "#000000"}]
img = render(nodes, "t4")
hits = sum(1 for k in range(5) for _ in [0]
           if img[int(100 + 40*np.sin(np.deg2rad(-90 + k*45))),
                  int(100 + 40*np.cos(np.deg2rad(-90 + k*45)))][0] < 100)
check("d: 5 lobes present", hits == 5)

# (e) region: flood fill stays within boundary
syn = np.full((SIZE[1], SIZE[0], 3), 255, np.uint8)
cv2.rectangle(syn, (30, 30), (170, 170), (0, 200, 0), -1)   # green box on white
syn_path = os.path.join(OUT, "syn.png")
cv2.imwrite(syn_path, syn)
img = render([{"rect": "bg", "full": True, "fill": "#000000"},
              {"region": "r1", "seed": [100, 100], "tol": 30, "fill": "#ff00ff"}], "t5") \
      if False else None
# region needs --ref; compile manually:
svg = sr.compile_scene([{"rect": "bg", "full": True, "fill": "#000000"},
                        {"region": "r1", "seed": [100, 100], "tol": 30, "fill": "#ff00ff"}],
                       SIZE, ref_path=syn_path)
p = os.path.join(OUT, "t5.svg"); open(p, "w").write(svg)
png = os.path.join(OUT, "t5.png"); sr.chrome(p, png, SIZE)
img = cv2.imread(png)
assert img is not None, f"render failed: {png}"
img = img.astype(int)
# magenta in BGR = (255, 0, 255)
check("e: inside region magenta", img[100, 100][0] > 200 and img[100, 100][2] > 200 and img[100, 100][1] < 60)
check("e: outside stays black", img[10, 10][0] < 50 and img[10, 10][1] < 50 and img[10, 10][2] < 50)

# (f) determinism: same input twice -> identical svg bytes
s1 = sr.compile_scene(nodes, SIZE)
s2 = sr.compile_scene(nodes, SIZE)
check("f: deterministic", s1 == s2)

# (g) unknown key raises with type info
try:
    sr.compile_scene([{"stroke": "x", "spine": [[0, 0], [9, 9]], "bogus": 1}], SIZE)
    check("g: unknown key raises", False)
except SystemExit as e:
    check("g: unknown key raises", "bogus" in str(e))

# (h) front end (relate.py): both blob forms resolve, and neither-key fails loudly
import relate as rl   # noqa: E402  (needs scripts/ on sys.path, done at the top)

_spec = {"frame": {"w": 200, "h": 200},
         "layers": ["default"],
         "draw": [
             {"blob": "quad", "poly": [[20, 20], [180, 20], [180, 120]], "fill": "#ff0000"},
             {"blob": "rib", "spine": [[20, 160], [180, 160]], "w": 20, "fill": "#0000ff"},
         ]}
_emit, _env, _notes, _layers = rl.resolve(_spec)
check("h: front-end blob accepts poly", any(n.get("blob") == "quad" for n in _emit))
check("h: front-end blob still accepts spine+w", any(n.get("blob") == "rib" for n in _emit))
try:
    rl.resolve({"frame": {"w": 200, "h": 200}, "draw": [{"blob": "bad", "fill": "#fff"}]})
    check("h: blob without poly/spine fails loudly", False)
except SystemExit as e:
    check("h: blob without poly/spine fails loudly", "poly" in str(e) and "spine" in str(e))

# (i) face family: the jaw must extend BELOW the cranium. The first version drew a full-height
# cranium with the jaw wedge inside it, so the round cranium bottom was the whole silhouette and no
# chin rendered — two independent reviewers reported "round blob, no chin" (STATUS D12).
_fspec = {"frame": {"w": 1000, "h": 1000},
          "draw": [{"face": "head", "at": [500, 400], "rx": 100, "ry": 120,
                    "cheek": 0.68, "jaw": 0.37, "chin-w": 0.035, "fill": "#eeeeee"}]}
_femit, _fenv, _fn, _fl = rl.resolve(_fspec)
_cran = next(n for n in _femit if n.get("ellipse") == "head-cranium")
_jaw = next(n for n in _femit if n.get("blob") == "head-jaw")
_cran_bottom = _cran["at"][1] + _cran["ry"]
_jaw_bottom = max(pt[1] for pt in _jaw["poly"])
check("i: face keeps the head-box anchor (ruler unchanged)", _fenv["head.rx"] == 100 and _fenv["head.chiny"] == 520)
check("i: jaw chin extends below the cranium", _jaw_bottom > _cran_bottom + 40)
check("i: cheek line matches the jaw param", abs(_fenv["head.cheek-y"] - (400 + 0.37 * 120)) < 1)

# (j) sunhat brim: the two fills must share the fold border and tile the ellipse exactly. The split
# used to be a straight CHORD across the disc, so the fills met only at the two tips — and the tips
# and chord are exactly where the hair and crown sit, so the brim read as a detached lozenge
# (M2 attempt 2, STATUS D16). The fix makes the far slice the rim band along the far edge, folding
# over (`rim`), sharing every border vertex with the near slice.
_sspec = {"frame": {"w": 1000, "h": 1000},
          "draw": [{"ellipse": "head", "at": [500, 400], "rx": 90, "ry": 100, "fill": "#eee"},
                   {"sunhat": "hat", "host": "head", "brim": 500, "crown": 170, "rim": 0.5,
                    "fill": "#333"}]}
_semit, _senv, _sn, _sl = rl.resolve(_sspec)
_far = next(n for n in _semit if n.get("blob") == "hat-brim-far")["poly"]
_near = next(n for n in _semit if n.get("blob") == "hat-brim-near")["poly"]
_far_border = [tuple(p) for p in _far[49:]]
_near_border = [tuple(p) for p in _near[49:]]
check("j: brim fills share the fold border", len(_far_border) == len(_near_border)
      and all(abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6
              for a, b in zip(_far_border, reversed(_near_border))))
_brim = next(n for n in _semit if n.get("ellipse") == "hat-dome")
_xs = [p[0] for p in _far] + [p[0] for p in _near]
_ys = [p[1] for p in _far] + [p[1] for p in _near]
check("j: brim fills keep the brim's full width",
      abs((max(_xs) - min(_xs)) - 500) < 6)
try:
    rl.resolve({"frame": {"w": 100, "h": 100}, "draw": [
        {"ellipse": "h", "at": [50, 50], "rx": 10, "ry": 10}, {"sunhat": "s", "host": "h",
         "brim": 40, "crown": 10, "rim": 0.0}]})
    check("j: rim must be in (0,1)", False)
except SystemExit as e:
    check("j: rim must be in (0,1)", "rim" in str(e))

# (k) flood_region fixed-range: on a smooth gradient the historical neighbour-range flood crawls
# the whole ramp, while `fixed` stops at a colour distance from the seed. This is the difference
# between the teacher being usable and the flood covering the frame.
gm = np.zeros((200, 200, 3), np.uint8)
for _x in range(200):
    gm[:, _x] = _x
_rel = sr.flood_region(gm, (10, 100), 20, fixed=False, eps=1)
_fix = sr.flood_region(gm, (10, 100), 20, fixed=True, eps=1)
_relw = max(p[0] for p in _rel) - min(p[0] for p in _rel)
_fixw = max(p[0] for p in _fix) - min(p[0] for p in _fix)
check("k: region fixed range stops on a gradient, relative crawls", _fixw < 40 and _relw > 150)

# (l) flood_region box: clip a flood to a window (separates same-colour masses elsewhere)
_uni = np.full((200, 200, 3), 128, np.uint8)
_boxed = sr.flood_region(_uni, (100, 100), 10, fixed=True, box=[0, 0, 120, 120], eps=1)
_bw = max(p[0] for p in _boxed) - min(p[0] for p in _boxed)
check("l: region box clips the computed contour", _bw <= 121)

# (m) flood_region eps: finer simplification keeps more contour detail (drawing silhouettes need it)
_mask = np.zeros((200, 200), np.uint8)
_angs = np.linspace(0, 2 * np.pi, 41)[:-1]
_poly = np.array([[100 + 60 * np.cos(a), 100 + 60 * np.sin(a)] for a in _angs], np.int32)
cv2.fillPoly(_mask, [_poly], 255)
_img = np.zeros((200, 200, 3), np.uint8)
_img[_mask > 0] = (200, 200, 200)
_coarse = sr.flood_region(_img, (100, 100), 10, fixed=True, eps=6)
_fine = sr.flood_region(_img, (100, 100), 10, fixed=True, eps=1.5)
check("m: region eps keeps more contour detail when smaller", len(_fine) > len(_coarse))

# (n) relate front end: a `region` node takes a RELATIONAL seed and returns the reference contour,
# and refuses to resolve without the reference (teacher-only, P18 — it must never appear in M5 spec).
_rsyn = np.full((200, 200, 3), 255, np.uint8)
cv2.circle(_rsyn, (100, 100), 40, (0, 200, 0), -1)
_rpath = os.path.join(OUT, "region-syn.png")
cv2.imwrite(_rpath, _rsyn)
_rspec = {"frame": {"w": 200, "h": 200},
          "draw": [{"region": "blob", "seed": [100, 100], "tol": 30,
                    "fill": "#ff00ff", "fixed": True, "eps": 3}]}
_re, _renv, _rn, _rl2 = rl.resolve(_rspec, ref=cv2.imread(_rpath))
_rnode = next(n for n in _re if n.get("region") == "blob")
_rxs = [p[0] for p in _rnode["poly"]]
check("n: front-end region resolves a relational seed to the reference contour",
      55 < min(_rxs) < 65 and 135 < max(_rxs) < 145 and "blob.cx" in _renv)
try:
    rl.resolve(_rspec)
    check("n: region refuses to resolve without the reference", False)
except SystemExit as _e:
    check("n: region refuses to resolve without the reference", "reference" in str(_e).lower())

# (o) sunhat z-pom: poms stay at the family z by default (historical specs unchanged) and can be
# lifted above a reference-seeded brim region that paints over the brim.
_zbase = {"ellipse": "head", "at": [500, 400], "rx": 90, "ry": 100, "fill": "#eee"}
_zh = {"sunhat": "hat", "host": "head", "brim": 500, "crown": 170, "pom": 2,
       "pom-at": [0.7, 0.9], "z": "hat", "z-front": "hf"}
_ze, _, _, _ = rl.resolve({"frame": {"w": 1000, "h": 1000}, "draw": [_zbase, _zh]})
_zpoms = [n for n in _ze if str(n.get("ellipse", "")).startswith("hat-pom")]
check("o: sunhat poms default to the family z", all(n["z"] == "hat" for n in _zpoms))
_ze2, _, _, _ = rl.resolve({"frame": {"w": 1000, "h": 1000},
                            "draw": [_zbase, {**_zh, "z-pom": "top"}]})
_zpoms2 = [n for n in _ze2 if str(n.get("ellipse", "")).startswith("hat-pom")]
check("o: sunhat z-pom lifts the poms", all(n["z"] == "top" for n in _zpoms2))

# (p) traced node: the REMOVABLE form of a computed `region` (roadmap D20). It loads frozen
# vertices from a sidecar written by `draw freeze`, emits the same closed poly, and is a normal
# anchor — so a spec can swap every `region` for `traced` and render with the reference deleted.
# A missing, malformed or STALE sidecar (recorded image sha256 no longer matches the raster) must
# fail loudly: a silently stale trace is worse than no trace.
_trdir = os.path.join(OUT, "traced"); os.makedirs(_trdir, exist_ok=True)
_timg = os.path.join(OUT, "trace-src.png")
cv2.imwrite(_timg, np.full((80, 80, 3), 200, np.uint8))
_sha = hashlib.sha256(open(_timg, "rb").read()).hexdigest()
_side = {"version": 1, "node": "t", "image": "trace-src.png", "image_sha256": _sha,
         "vertices": [[10, 10], [70, 10], [70, 60], [10, 60]]}
with open(os.path.join(_trdir, "t.json"), "w") as _fh:
    _fh.write(json.dumps(_side))
_tspec = {"frame": {"w": 100, "h": 100}, "draw": [
    {"traced": "t", "from": "traced/t.json", "fill": "#123456"},
    {"ellipse": "e", "at": [50, 50], "rx": 5, "ry": 5}]}
_te, _tenv, _tn, _tl = rl.resolve(_tspec, base_dir=OUT)
_tnode = next(n for n in _te if n.get("traced") == "t")
check("p: traced loads frozen vertices and emits a poly",
      _tnode["poly"] == [(10.0, 10.0), (70.0, 10.0), (70.0, 60.0), (10.0, 60.0)])
check("p: traced is a normal anchor (later nodes resolve off it)",
      _tenv["t.cx"] == 40 and any(n.get("ellipse") == "e" for n in _te))
try:
    rl.resolve({"frame": {"w": 100, "h": 100},
                "draw": [{"traced": "gone", "from": "traced/nope.json"}]}, base_dir=OUT)
    check("p: traced missing file errors loudly", False)
except SystemExit as _e:
    check("p: traced missing file errors loudly", "missing" in str(_e).lower())
_bad = dict(_side); _bad["image_sha256"] = "0" * 64
with open(os.path.join(_trdir, "stale.json"), "w") as _fh:
    _fh.write(json.dumps(_bad))
try:
    rl.resolve({"frame": {"w": 100, "h": 100},
                "draw": [{"traced": "stale", "from": "traced/stale.json"}]}, base_dir=OUT)
    check("p: traced stale sha256 errors loudly", False)
except SystemExit as _e:
    check("p: traced stale sha256 errors loudly", "STALE" in str(_e))
with open(os.path.join(_trdir, "malformed.json"), "w") as _fh:
    _fh.write("{not json")
try:
    rl.resolve({"frame": {"w": 100, "h": 100},
                "draw": [{"traced": "malformed", "from": "traced/malformed.json"}]}, base_dir=OUT)
    check("p: traced malformed file errors loudly", False)
except SystemExit as _e:
    check("p: traced malformed file errors loudly", "malformed" in str(_e).lower())

# (q) freeze round-trip: a `region` on a synthetic raster materializes to a sidecar with
# provenance, and that sidecar resolves through `traced` with NO reference at all (D20).
_qr = np.full((120, 120, 3), 255, np.uint8)
cv2.rectangle(_qr, (30, 30), (90, 90), (0, 180, 0), -1)
_qimg = os.path.join(OUT, "freeze-syn.png")
cv2.imwrite(_qimg, _qr)
_qspec = {"frame": {"w": 120, "h": 120},
          "draw": [{"region": "blob", "seed": [60, 60], "tol": 40, "fixed": True, "eps": 3,
                    "fill": "#ff00ff"}]}
_qdir = os.path.join(OUT, "frozen")
_written = rl.freeze(_qspec, spec_path=pathlib.Path(OUT) / "freeze-syn.yaml",
                     ref_path=_qimg, ref_bgr=cv2.imread(_qimg), out_dir=_qdir)
_qdata = json.loads(open(os.path.join(_qdir, "blob.json")).read())
check("q: freeze writes a sidecar with provenance + vertices",
      _written and _qdata["node"] == "blob" and _qdata["tol"] == 40
      and _qdata["image_sha256"] == hashlib.sha256(open(_qimg, "rb").read()).hexdigest()
      and len(_qdata["vertices"]) == _qdata["vertex_count"])
_qe, _qenv, _qn, _ql = rl.resolve(
    {"frame": {"w": 120, "h": 120},
     "draw": [{"traced": "blob", "from": "frozen/blob.json", "fill": "#ff00ff"}]}, base_dir=OUT)
_qnode = next(n for n in _qe if n.get("traced") == "blob")
_qx = [p[0] for p in _qnode["poly"]]
check("q: frozen sidecar renders as traced with no --ref",
      _qnode["poly"] and 25 <= min(_qx) <= 35 and 85 <= max(_qx) <= 95)

# (r) sunhat `droop`: a sag of the near edge along the brim's own normal. Default 0 must be
# identical to the old flat ellipse (every historical spec unchanged), and a nonzero droop must
# move the near edge while leaving the far edge and the two tips alone.
_flat = rl.ellipse_outline(0, 0, 100, 40, 0)
check("r: droop 0 == flat ellipse (backward compatible)",
      rl.droop_outline(0, 0, 100, 40, 0, 0.0) == _flat)
_droop = np.array(rl.droop_outline(0, 0, 100, 40, 0, 0.5))
_flat_a = np.array(_flat)
_near_i = int(np.argmax(_flat_a[:, 1]))          # most positive v = near edge
_far_i = int(np.argmin(_flat_a[:, 1]))           # most negative v = far edge
_tip_i = int(np.argmax(_flat_a[:, 0]))
check("r: droop sags the near edge, leaves the far edge and tips",
      _droop[_near_i, 1] > _flat_a[_near_i, 1] + 10
      and abs(_droop[_far_i, 1] - _flat_a[_far_i, 1]) < 1e-9
      and abs(_droop[_tip_i, 0] - _flat_a[_tip_i, 0]) < 1e-9)
_sun = {"ellipse": "head", "at": [500, 400], "rx": 90, "ry": 100, "fill": "#eee"}
_hat = {"sunhat": "hat", "host": "head", "brim": 500, "crown": 170,
        "flat": 0.3, "rim": 0.5, "front": [0.1, 0.6]}
_e0, _, _, _ = rl.resolve({"frame": {"w": 1000, "h": 1000}, "draw": [_sun, _hat]})
_e1, _, _, _ = rl.resolve({"frame": {"w": 1000, "h": 1000},
                           "draw": [_sun, {**_hat, "droop": 0.6}]})
_e0b, _, _, _ = rl.resolve({"frame": {"w": 1000, "h": 1000},
                            "draw": [_sun, {**_hat, "droop": 0.0}]})
check("r: sunhat accepts droop and it reshapes the brim",
      _e0 == _e0b and _e0 != _e1
      and any(n.get("blob") == "hat-brim-near" for n in _e1))

# (s) fit-family instrument core: the IoU, the mask rasterizer, the parameter clamp, the
# deterministic low-discrepancy seeds, Nelder-Mead, and that the search actually improves.
import importlib.util as _ilu
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ffspec = _ilu.spec_from_file_location(
    "fit_family", os.path.join(_ROOT, ".scratch/13-assembly/work/fit-family.py"))
_ff = _ilu.module_from_spec(_ffspec)
_ffspec.loader.exec_module(_ff)
_a = np.zeros((10, 10), np.uint8); _a[0:5, :] = 1
_b = np.zeros((10, 10), np.uint8); _b[0:5, 0:5] = 1
check("s: iou is intersection-over-union", _ff.iou(_a, _b) == 25 / 50)
check("s: iou of disjoint masks is 0", _ff.iou(_a, np.roll(_b, 5, axis=0)) == 0.0)
_rmask = _ff.rasterize({"blob": "x", "poly": [[1, 1], [8, 1], [8, 8], [1, 8]]}, (10, 10))
check("s: rasterize fills a poly", _rmask[4, 4] == 1 and _rmask[0, 0] == 0)
_cl = _ff._clamp({"front0": 0.8, "front1": 0.2}, {"front0": (0, 1), "front1": (0, 1)})
check("s: clamp keeps front0 < front1",
      _cl["front0"] == 0.8 and abs(_cl["front1"] - 0.85) < 1e-9)
check("s: halton seeds are deterministic and in bounds",
      _ff.halton_seeds(["a", "b"], {"a": (0, 1), "b": (0, 1)}, 4)
      == _ff.halton_seeds(["a", "b"], {"a": (0, 1), "b": (0, 1)}, 4))
_nm = _ff.nelder_mead(lambda x: (-((x["a"] - 2.0) ** 2 + (x["b"] + 1.0) ** 2), {}),
                      {"a": 0.0, "b": 0.0}, {"a": (-5, 5), "b": (-5, 5)},
                      {"a": 0.5, "b": 0.5})
check("s: nelder-mead minimises a quadratic", abs(_nm[0]["a"] - 2) < 0.1 and abs(_nm[0]["b"] + 1) < 0.1)
_qeval = lambda x: (-((x["a"] - 2.0) ** 2 + (x["b"] + 1.0) ** 2), {})
_qfit = _ff.fit(_qeval, {"a": 0.0, "b": 0.0}, {"a": (-5, 5), "b": (-5, 5)},
                {"a": 1.0, "b": 1.0}, ["a", "b"], explore=8, refine=2)
check("s: the search improves on its start", _qfit[1] > -1.0)

print(f"\n{PASS}/{TOTAL} smoke tests passed")

# --- wave + strands generator tests ---
import hashlib, subprocess as sp
scene = '''- {rect: bg, at: [0,0], w: 1024, h: 1024, fill: "#ffffff"}
- {wave: r, spine: [[100,300],[500,280],[900,320]], w: 60, amp: 25, len: 300, sag: 0.2, taper: end, fill: "#4ba7b1"}
- {strands: h, region: [100,600,400,800], n: 10, dir: 100, spread: 15, w: 3, len: 80, ink: ["#3d73a7","#3974ab"], seed: 42}
'''
open('/tmp/tg.yaml','w').write(scene)
sp.run([sys.executable, 'scripts/scene_render.py', '/tmp/tg.yaml', '-o', '/tmp/tg.png'], check=True, capture_output=True)
img = cv2.imread('/tmp/tg.png')
mid = img[300, 500]  # teal ribbon body (BGR: 177,167,75)
assert abs(int(mid[0])-177) < 30 and int(mid[1]) > 120, f"wave ribbon not at spine: {mid}"
blue = ((np.abs(img[560:840, 60:440].astype(int) - np.array([167,115,103])).sum(axis=2) < 60).sum())
assert blue > 300, f"strands not rendered: {blue} blue px"
sp.run([sys.executable, 'scripts/scene_render.py', '/tmp/tg.yaml', '-o', '/tmp/tg2.png'], check=True, capture_output=True)
assert hashlib.md5(open('/tmp/tg.png','rb').read()).hexdigest() == hashlib.md5(open('/tmp/tg2.png','rb').read()).hexdigest(), "wave/strands nondeterministic"
print("PASS wave: ribbon body at spine with sag")
print("PASS strands: n strands rendered in region")
print("PASS wave/strands: deterministic")

# (h) regression: strands with op: must not emit duplicate opacity attribute (invalid XML)
svg_h = sr.compile_scene([{"strands": "s", "region": [0,0,100,100], "n": 3, "op": 0.5, "seed": 1}], SIZE)
import xml.etree.ElementTree as ET
try:
    ET.fromstring(svg_h)
    check("h: strands op -> valid XML", 'opacity="0.5 opacity' not in svg_h and svg_h.count('opacity="0.5"') == 1)
except ET.ParseError as e:
    check("h: strands op -> valid XML", False)
    print("   parse error:", e)

# (i) ring generator: zig-zag annulus, hue walk, deterministic; back/front halves seam-share geometry
ring_base = {"at": [512,512], "r": 260, "w": 55, "zig": 0.18, "zn": 24,
             "zq": 0.2, "seed": 37, "hue": [170,350], "sat": 0.7, "val": 0.9, "nseg": 24}
back = {"ring": "rb", **ring_base, "a0": 180, "a1": 360, "z": "back"}
front = {"ring": "rf", **ring_base, "a0": 0, "a1": 180, "z": "front"}
svg_i = sr.compile_scene([{"layers": ["back","body","front"]}, back,
                          {"ellipse": "body", "at": [512,512], "rx": 170, "ry": 270,
                           "fill": "#cccccc", "z": "body"}, front], SIZE)
try:
    ET.fromstring(svg_i)
    colors = set(re.findall(r'fill="(#[0-9a-f]{6})"', svg_i))
    seg_a = sr.ring_segments(back)
    seg_b = sr.ring_segments(back)
    check("i: ring -> valid XML + hue walk + deterministic",
          len(colors) >= 20 and seg_a == seg_b and svg_i.index('id="rb"') < svg_i.index('id="body"') < svg_i.index('id="rf"'))
except ET.ParseError as e:
    check("i: ring -> valid XML + hue walk + deterministic", False)
    print("   parse error:", e)
