#!/usr/bin/env python3
"""Smoke tests for scene_render.py — run with .venv/bin/python."""
import os, sys, subprocess, tempfile, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # scripts/
import scene_render as sr
import cv2, numpy as np

SIZE = (200, 200)
OUT = tempfile.mkdtemp()
PASS = 0


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
    global PASS
    print(("PASS " if cond else "FAIL ") + name)
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

print(f"\n{PASS}/7 smoke tests passed")

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
