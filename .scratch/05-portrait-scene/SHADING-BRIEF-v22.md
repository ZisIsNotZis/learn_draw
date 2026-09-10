# SHADING & DENSITY BRIEF — v22 (final fidelity pass)

Start from `/home/z/vibe/learn_draw/.scratch/05-portrait-scene/work/v20.svg` — structure and color amounts are correct (orchestrator-verified). This pass adds what makes the ref look like an illustration instead of a coloring page: shading, density, luminosity.

## Worst zones (orchestrator-measured color distance vs ref)

torso 98.5 · curtain 89.6 · skirt 88.3 — attack in this order.

## Per-zone fixes (all measured from /home/z/vibe/learn_draw/image.jpg — VIEW it repeatedly)

### torso (x560-900, y430-730)

- Add soft shading: grey-blue shadow shapes under the collar, under the bow, along the blouse's right side (fill #c9d4cc, opacity 0.5, feathered with filter blur stdDeviation 4).
- Bow: add 2-3 fold lines (#a92f5c) and a darker knot bottom.
- Sleeves: gather strokes already exist — add 2 shadow crescents under each sleeve hem (#c9d4cc op .45).
- Ref also shows the blouse waist shadow where skirt meets: thin dark band.

### curtain (x790-1024, y270-770)

- The ref curtain is a THICK flowing mass with visible strand bands. Add: 4-6 curved strand bands (stroke #2c4a6e width 3-5, opacity .7) following the S-flow, + 3 lighter teal-tinted bands (#5a9bac op .4, width 8-14) between them for depth.
- The prong tips: add slight darker tips (small #26354a strokes at each tip).

### skirt (x400-900, y640-1020)

- The dark navy #112e4b placement per ref: heavy at top-left of the skirt and along the bottom-left hem; the white hem petals sit at bottom-center/right. Re-arrange if needed (compare with ref view).
- Add 4-5 long fold curves from waist to hem (alternate #2a4a66 on dark, #b8c4c0 on light), following the billow.
- Add subtle highlight: pale #e8efe6 wide soft strokes down the skirt's light center.

## Technique

- Feathering: `<filter id="soft"><feGaussianBlur stdDeviation="4"/></filter>` (exists in file as "soft"/"softer").
- Every shape id'd + commented (explainability contract).
- ALWAYS: view image.jpg + full rendered frame before/after each zone. Render: `scripts/draw render`. Use `.venv/bin/python` for probes.
- XML parse-check before render. Assert every edit landed.

## Rounds

4-6 view-fix rounds. Then measure per-zone distances (code snippet below) and report.
`ref = cv2.imread('image.jpg').astype(int); dr = cv2.imread(render).astype(int); np.linalg.norm(ref[y:y+h,x:x+w]-dr[...],axis=2).mean()`

## Goal

torso ≤80, curtain ≤75, skirt ≤75. Overall ≤58. Stop when reached or 6 rounds.

Output: overwrite v20.svg. Changelog appended. Do NOT git commit.
