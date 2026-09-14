# Face probe — `eye` vocabulary family (14-abstraction-research)

Proves tier-3 vocabulary for faces: a layered anime `eye` family in the resolver
(`work/face/relate.py` — copy of the 06 resolver, extended), a fully relational face
spec with zero absolute coordinates (`work/face/face.yaml`), and 10 renders. The engine
never reads image.jpg; the image only seeded the canons below, then was closed.

## The eye family

Authoring call (no geometry):

```yaml
- {eye: eyeL, host: head,
   at: [head.cx - 0.73*head.rx, head.cy - 0.58*head.ry],
   w: 0.55*head.w, h: 0.33*head.h, tilt: 5, almond: 0.62,
   iris-top-fill: "#4470b3", iris-bot-fill: "#ef92ae", refl-fill: "#62c7a8", glints: 2}
- {eye: eyeR, host: head, mirror-of: eyeL}   # the whole second eye is one relation
```

**Parameters** — `eye` (id), `host` (mirror axis + ruler), `at` (center, any relation),
`w` (width in head units), `h` (default 0.62 w), `tilt` (deg), `almond` (0=round…
1=pointed: lid arch height, corner sharpness, lower-lid depth all derive from it),
`mirror-of` (other eye id: inherits every param, mirrors centre across host axis,
negates tilt, swaps inner/outer), `glints` (1|2), `iris-w`/`iris-h` (iris size as
fractions of w/h, auto-clamped to the aperture so the iris never pokes through a lid),
`lash-w` (upper-lash thickness, fraction of h), `line-w`, `glint-side` (±1, the WORLD
side of the light — deliberately not mirrored, both eyes catch the same lamp),
`gaze` (±1, the world side both irises look), `refl-fill` (coloured reflection dot),
`*‑fill` (sclera, iris top, iris bottom, pupil, lash, glint), `z`.

**Engine-supplied structure** (the knowledge a model must not re-derive): the aperture
is one generated almond curve (two cubic lid arcs sharing the corners — top lid arches,
bottom lid shallower and flatter under the iris); the iris is a two-tone disc (dark top
cap with a curved boundary, light bottom) sitting slightly off centre and auto-clamped
inside the aperture; the upper lash is a ONE-SIDED tapered band anchored on the lid line
(grows outward only, so no black intrudes into the eye), thin at the inner corner,
thick through the middle, with an outer wing; a thin lower-lash line and a sealing
outline finish it.

**Exposed anchors** (other shapes hang off these): `cx cy left right top bottom w h w2 h2`
(aperture bbox), `outerx/outery`, `innerx/innery` (corners), `irisx/irisy`,
`topx/topy` (lid apex), `botx/boty`, `facing`, and the outline itself for
`{along: eye, t: …}`. Brows in the spec are hung off `eyeL.outerx/topy/innerx`, so a
mirror eye gets brows with no copied numbers.

**General relations added** (only when needed): `{mirror: P, across: SHAPE}` reflects a
point across a shape's vertical axis (used for the right brow's spine); `mirror-of` is
the family-level mirror. Nothing else was needed.

## Canons measured from image.jpg (fractions, reference closed afterwards)

- eye height = **0.35 × head height** (47 px / 136 px at the near eye)
- eye width  = **0.55 × head width** (near eye 87 px / 148 px; far eye 53 px — perspective)
- eye centres = head.cx **± 0.73 × head.rx** (measured ±54 px / face half-width 74 px)
- eye centre y = head.cy **− 0.58 × head.ry** (eyes sit high under the fringe)
- inner-corner gap ≈ **0.44 × one eye width** (38 px / 87 px)
- iris ≈ 0.44 eye-widths wide, fills the aperture vertically; darker top ~50 % (blue
  #4470b3), lighter bottom (pink #ef92ae); glints track a world-side light (upper-left);
  a small coloured reflection dot sits below the glint
- upper lash ~0.16–0.19 of eye height, thickest at the outer half, wing past the corner
- brow line ≈ 0.2 eye-height above the lash, slants down toward the nose
- nose tick = head.cy + **0.05 × head.ry** (a slanted 2–3 px dash, ink #584d3a)
- mouth    = head.cy + **0.52 × head.ry** (a soft 10 px dash, ink #a08a74)
- visible face ≈ wider than tall (temples wide, chin pointed)

## What failed hardest

1. **Iris escape** (v1): the iris is an ellipse but the almond's bottom lid rises toward
   the corners, so the pink iris puddled below the eye. Fixed in the engine by clamping
   iris ry against the lid height at the iris's own x-extent — a containment rule, not a
   spec fix.
2. **The straddling lash** (v1–v2): a band offset ±half-width around the lid line put
   black inside the eye and a wedge at the inner corner. The fix (one-sided band anchored
   on the lid line, growing outward) is the single biggest readability win.
3. **Orientation/mirror bugs**: my inner/outer convention was inverted (the lash wing
   flicked toward the nose); the anchor table caught it, not the render. Mirrored glints
   looked wrong because glints must track the light, not the eye's inner side — that's a
   drawing rule (world-side light/gaze), now parameters.
4. **An ellipse can't host wide-set anime eyes**: at the canon height the ellipse is much
   narrower than at its centre, so the eye corners poked the silhouette. Worked around
   with temple hair (ref hides the same overlap), but the real answer is a face-shaped
   host.

## What the abstraction is MISSING for faces

- **A `face`/`head` vocabulary** (jaw + chin + temples: rounded-rectangle / superellipse /
  polygon silhouette, pointed chin). The ellipse host was the biggest structural
  limitation; the round chin is the weakest part of the final render.
- **Grouping / one-unit references**: the eye emits ~9 nodes; there is no way to address
  "the whole eye" as one z-unit or one anchor source except by convention.
- **Relations**: corner/junction points ("where the lid crosses the iris") and an
  offset variant of `{between: [A, B, t]}`; `{mirror: …}` only exists because this probe
  demanded it.
- **Tapered strokes as a first-class shape** (I built `taper_band` ad hoc for the lash;
  brows, strands, ribbons all want it).
- **Mouth/brow families** with variants (smile shapes, brow angles) — currently bare
  strokes in the spec.
- **Opacity/soft fields** for blush and iris gradients (the renderer's flat cel colours
  suffice; alpha plumbing is absent from emit).
- **Perspective/turn knobs** (3/4 view): the ref's far eye is 0.6× the near eye and the
  face is asymmetric; only a `turn` knob on a `face` family would capture it.

## Iteration renders (all in evidence/face/)

- v1: first eye family + mirrored eyes, iris bleeding, straddling lash
- v2: one-sided lash, iris containment clamp, hair moved behind face
- v3: facing sign fixed, hair dome reshaped, eyes retilted
- v4: iris fills aperture (deeper lid, wider host), wedge wing lash
- v5: brows above lash on eye anchors, green reflection dot
- v6: world-side glints, wider host + temple locks
- v7: glint smaller/higher, cel-scale pupil, slanted brows, smoothed locks
- v8: fringe strands (bangs) over the forehead
- v9: iris outward/wider (kills outer white crescent), bangs shortened
- v10: gaze as a world-side knob (both irises share the ref's screen-left look)

Final: v10 + `check` bundle at `evidence/face/check/` (worst regions are the ref's
hat/background, outside the face probe; metrics are a breakage alarm only).

Honest verdict: it reads as a face — two layered anime eyes (sclera / two-tone iris /
pupil / glints / green reflection / tapered lash with wings), brows, nose tick and mouth
all placed by the measured canons. The round ellipse chin and the lack of a smile/shape
variant are the visible remaining gaps, both root-caused to missing vocabulary above.
