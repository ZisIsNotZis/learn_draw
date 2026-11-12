# Scenic composition evidence — 2026-11-12

This unit tests high-level background/celestial presets and screen-space object placement through
the public studio CLI. It is a small graphic-background capability, not a completed general drawing
system. The reference portrait and its best record remain untouched. No reference, generated bitmap
asset or GPU/model workflow was used.

## Actual artifacts

- `moonrise/`: first dusk landscape; move moon down/inward and narrow its crescent.
- `daylight/`: first daylight variant; change atmosphere, sun placement and ridge colours.
- `moonrise-refined/final/`: add a foreground pine group rooted on the actual near ridge and brighten
  existing stars. The group supplies scale and a counterweight, while keeping a subdued silhouette.
- `daylight-refined/final-2/`: choose a different landform, move sun to the left, remove its crown,
  lift/lighten the ground. Seed 13 changed the initial slope too little; the final continuation uses
  seed 2, producing a clear opposing large-scale rhythm and depth-driven solar occlusion.

Each scene directory preserves working input, history, sequential inspection/preview images and
`commands.json` with actual CLI arguments/exits. `intent.json` states the bounded intended use.
Earlier stages remain history, not current selections. `examples/studio/compose.py --theme
moonrise|daylight --refined --outdir FRESH` reproduces the final semantic choices; reusable finished
inputs are `examples/studio/moonrise.json` and `daylight.json`.

## Independent image criticism and disposition

Two fresh image-only reviewers first saw the `check/report.txt` image lists and the open question
“what is wrong here?”. They agreed: empty sky, weak depth/scale in smooth colour bands, weak small
stars, a gear-like sun and almost identical compositions. There was no observed broken geometry or
accidental visibility leak. These are real art limitations, not a failed correctness test.

The first authoring error was treating a palette/symbol change as enough compositional variation.
The narrow correction changed the landform and focal-point placement, gave night a secondary scale
group, and removed the sunny crown where it conflicted with the soft landscape. A different seed did
not itself prove a different visual rhythm: seed 13 was inspected and superseded by seed 2.

Two new fresh reviewers saw only the refined images. They found readable subjects and no obvious
broken shapes, but still described smooth hills as colour bands, sparse scene character, repetitive
tree icons and weak tree/ground separation at small size. One noted a tight sun/mountain grouping.
These criticisms remain open. The refinements establish useful controls and distinct background
variants, **not an artwork-quality pass**. Do not use flat-background success to claim rich scene
creation or erase the open portrait gate. Subsequent artwork needs a clearer intended use and
foreground subject; adding marks indiscriminately is not the correction.

Reviewers were `composition_review_a/b` and `composition_refined_review_a/b`, with no source,
history, goal brief or expected verdict. Each actually opened full-resolution and thumbnail PNGs.
Locations were checked against the actual rendered layers/region bounds before acting.

## Verification

`validation.json` records 54 passing operation/head/scenery/depth/oracle tests and repeated current
SVG/CPU PNG byte identity. New tests exercise actual crescent transparency, depth-derived horizon
occlusion independent of node order, ray-gap opacity under exact clipping, screen-space moves with
unchanged neighbours, recoverable insertion, scoped controls and trees attached under ridge changes.
The source-only primitive implementation remains separate from the authored composition choices.
