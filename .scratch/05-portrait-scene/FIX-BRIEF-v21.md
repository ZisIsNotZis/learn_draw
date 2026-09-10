# FIX BRIEF — v21 (two surgical fixes, nothing else)

Start from `/home/z/vibe/learn_draw/.scratch/05-portrait-scene/work/v20.svg` (structure is good; 5/7 criteria verified by orchestrator). Fix ONLY these, measured against `/home/z/vibe/learn_draw/image.jpg` (view both full images first):

## Fix 1 — dark skirt mass too small (28k navy px, need ≥50k)

Orchestrator probe zone: x 500-860, y 700-1000. The dark navy #112e4b mass must dominate this zone. In the reference, the dark skirt fills the bottom-LEFT heavily (x 400-650) AND the hem band along the bottom (y 940-1010, x 450-800). Extend/enlarge `skirt-underlayer` + `skirt` dark shapes accordingly (keep white zigzag triangles + celadon pieces on top; they are correct). Re-probe until ≥50k.

## Fix 2 — hat brim band too thin (7.2k navy px, need ≥8k)

Probe zone: x 880-1024, y 220-380. The brim band (`hat-dome-band` silhouette's right part) must fill the diagonal from (840,208) to (1024,345-398) at ~60-90px thickness. Widen `hat-dome-band`'s band section and/or add the band polygon explicitly: `M 840 208 L 890 250 L 935 290 L 972 330 L 1002 370 L 1024 395 L 1024 342 L 1012 330 L 973 290 L 927 250 L 881 210 Z` (fill #32405b). Check against ref view: the band is thick and clearly sweeping. Re-probe until ≥8k.

## Protocol

1. View image.jpg full frame and the (500-900, 640-1024) region crop before editing.
2. Edit → `xml.etree` parse check → render via `scripts/draw render` → probe → view full frame.
3. 2-4 rounds max. Do not touch anything else (arms/neck/overlays pass).
4. Output: same file v20.svg (overwrite), changelog appended to v20-changelog.md.

## Pitfalls (from REBUILD-BRIEF.md — still apply)

replace() no-ops, nested-group regex, full-frame view after every change.
