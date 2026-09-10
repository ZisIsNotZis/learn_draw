#!/usr/bin/env python3
"""Smoke tests for scene_render.py — run with .venv/bin/python."""
import os, sys, subprocess, tempfile
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
