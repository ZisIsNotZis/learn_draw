# R1a object-study dispatch contracts

Authoritative record of the two work packages dispatched on the user's approval of the reduced scope (issue 55). These contracts were issued as dispatch text before this file existed; this file is now their home. A later dispatch must be committed to `work/` the moment it is issued, so the tree — not a conversation — holds the contract (see P34: a run killed mid-flight leaves only what was committed).

## A-bow-study-v1

- **Owner:** one writer, directory `.scratch/35-r1-articulated-study/evidence/A-bow-study-v1/`.
- **Canvas:** 800 x 560 px, authored in that canvas, single image, no panels.
- **Object:** the bow of the registered reference crop (`image.jpg` bbox `500,320,900,800` -> the 400x480 crop), crop bbox `(33,134)-(271,285)`, 239x152 px, scaled about 3.3x to fill the canvas. The reference seeds parameters and is then closed; the build reads neither the crop nor any metric at runtime.
- **Must read as:** a ribbon tied into a bow — a knot where the ribbon wraps and crosses itself, two lobes with curved free edges opening away from the knot, two tails leaving the frame, creases that follow real folds. Failure readings: two closed pills, a bowtie, a flat sticker, a crumpled paper bag, two lobes joined by a chord.
- **Binding construction:** one continuous ribbon (knot -> left lobe -> knot -> right lobe -> knot -> tails) with one width field; lobe overlap and the knot's wrap produced by depth, knot passes separated by at least one cloth thickness; creases authored as short marks on the strip surface in its own (u,v), clipped by depth; at every self-crossing the rear edge is broken, with a test asserting no two authored edges cross without a depth break plus a mutation demonstration; the two strip faces may differ in colour from the reference palette, each triangle's fill from its own projected winding; about four hand-typed coordinates per shape; no author-specified visibility cuts.
- **Artefacts:** `source/`, `tests/`, `artwork.svg`, `artwork.png` (800x560), `check/` bundle with the 1:1 image listed first, `manifest.json` + `manifest.sha256` verifying over the real file set, `README.md` (object inventory, width field, crease table with endpoints, depth separation table, measured target vs author choice, commands, unverified items), and a self-check table against the art-direction brief's bow criteria (items 5, 6, 7).
- **Acceptance:** tests pass including the crossing-break mutation; width continuity measured on the emitted strip rather than on a literal; two builds byte-identical; delivered PNG equals a fresh build through the documented path; manifest verifies 100%; the 1:1 image is listed first. The art verdict belongs to a fresh image reviewer.

## B-hand-study-v1

- **Owner:** one writer, directory `.scratch/35-r1-articulated-study/evidence/B-hand-study-v1/`; may copy primitives from `B-hand-v2-r1/` read-only.
- **Canvas:** 900 x 700 px, single image, no panels, no captions.
- **Object:** a hand supporting a shallow dish, filling the frame. No torso, head, shoulder join or body connection.
- **Must read as:** a hand supporting a dish from below — the dish's underside visibly meets the palm/fingers, the digits curl around or lie along the dish rather than standing as prongs in front of it, a thumb opposes on the near side, the dish reads as a vessel. Failure readings: fingers as rake tines, a hand intersecting a plate, the dish balanced on the fingertips, a flat lens with one rim.
- **Binding construction:** contact derived from the dish's own emitted contour, with the test re-deriving that contour instead of reusing the producer's constant; digit separation reported at the roots and at the distal halves as a fraction of a digit's width, with the roots' merge stated rather than hidden; the dish carries a rim with thickness, an inner wall and an underside; palm/fingers and dish interleave in depth with the rear edge broken at every occlusion, asserted with a mutation demonstration; no drawn-on claws or crease lines standing in for form; reference-free, so `scripts/draw check` runs with no `--ref`.
- **Optional:** a second image of the same hand with the dish lifted 30 px, only if everything else is complete, purely to prove the pose is parameterised.
- **Artefacts:** `source/`, `tests/`, `artwork.svg`, `artwork.png` (900x700), `check/` bundle with the 1:1 image first, `manifest.json` + `manifest.sha256`, `README.md` (construction vocabulary, geometric consequence vs author hypothesis, contact derivation, separation values with the root/distal qualifier, commands, unverified items).
- **Acceptance:** tests pass with the contour re-derivation; separation measured on emitted outlines; occlusion-break test plus mutation; two builds byte-identical; delivered PNG equals a fresh build through the documented path; manifest verifies 100%; the 1:1 image is listed first. The art verdict belongs to a fresh image reviewer.

## Scope boundary these contracts inherit

Both studies are R1a. Passing either does not satisfy R1b, the deferred articulated composition the original R1 described (see `roadmap.md` and issue 55). The four acceptance questions apply unchanged to both.
