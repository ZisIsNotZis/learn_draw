#!/usr/bin/env python3
"""Phase 0: component intake — extract plate + mask per component plate.

Plates: repo-root 2048x2048 RGBA, fully opaque, flat grey bg (~RGB 200).
Mask = distance-from-bg threshold + largest connected component + cleanup.
Outputs (1024-space, .scratch/05-portrait-scene/work/components/):
  {name}-plate.png  — downscaled plate with bg made transparent
  {name}-mask.png   — binary foreground mask (white=fg)
"""
from PIL import Image
import numpy as np
from scipy import ndimage
import os

COMP = ".scratch/05-portrait-scene/work/components"
os.makedirs(COMP, exist_ok=True)
NAMES = ["hat", "head", "head_hat", "dress", "cloth", "ribbon", "cutout"]

for name in NAMES:
    im = Image.open(f"{name}.png").convert("RGB")
    im = im.resize((1024, 1024), Image.Resampling.LANCZOS)
    a = np.asarray(im).astype(np.int16)

    # bg estimate: median of border pixels
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    dist = np.sqrt(((a - bg) ** 2).sum(axis=-1))

    m = dist > 40  # fg candidate
    # cleanup: close small holes, remove specks, keep largest component
    m = ndimage.binary_closing(m, np.ones((7, 7)))
    m = ndimage.binary_opening(m, np.ones((5, 5)))
    lab, n = ndimage.label(m)
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    m = ndimage.binary_fill_holes(m)

    # plate with transparent bg
    rgba = np.dstack([a.astype(np.uint8), (m * 255).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").save(f"{COMP}/{name}-plate.png")
    Image.fromarray((m * 255).astype(np.uint8)).save(f"{COMP}/{name}-mask.png")
    # bbox for placement back into the 1024 scene
    ys, xs = np.where(m)
    print(f"{name}: bg={bg.astype(int).tolist()} fgFrac={m.mean():.3f} "
          f"bbox=x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]")
print("done")
