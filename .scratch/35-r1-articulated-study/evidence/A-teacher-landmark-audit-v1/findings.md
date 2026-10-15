# A teacher landmark numeric cross-check (v1)

This is a bounded audit of the 19 existing teacher landmarks, not a redraw, refit, segmentation, or artwork judgment. Inputs are read-only: `image.jpg`, teacher-only `landmarks.csv`, `provenance.json`, `topology-map.md`, and `source-crop-registered.png`. Raw RGB is descriptive signal only and does not establish object identity.

## Findings

- Registration is exact: source SHA-256 `322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb`; crop SHA-256 `52e01f5e75e5d98fcd9a0a4c63be91ed09b8a18ca0f62e7e0348a021b2dd87d`; 400x480 crop equals source `(500+x,320+y)` at every one of 192,000 pixels. All 19 row coordinates map exactly.
- **N1 is a concrete semantic-coordinate contradiction.** Teacher labels crop `(232,47)` / source `(732,367)` “visible-neck-skin interior.” The point is exactly `#3877b2`; its raw 11x11 context shows it lies within the blue region adjoining pale/skin-colored pixels at the upper left. Its point and neighborhood contradict “skin interior”; blue RGB is not by itself a proof that this is hair, but spatial context strongly challenges N1's semantic label. This is a confirmed teacher-map defect at N1, not a validated replacement skin landmark. Do not move it or relabel it as another skin point absent independent semantic review.
- Point-type cross-check (not object labels inferred from color): N1, CR1, BD1, BD3, SC2, SC3, CU1, BL1, BR1, TD1 are visually interior samples of the named field/object; CL1 and BD4 land on colored transition/edge pixels rather than clean interiors; N2, CL2, CR2, BD2, SC1 and BK1 sit on/within a few pixels of a visible boundary, overlap, or detail, so their point does not establish an exact seam endpoint. TL1 is in the pink/blue contact band, not a reliable interior point or proven pink endpoint; its unknown continuation remains correctly unresolved. Classification describes sampled point placement, not a newly inferred contour.
- Full neighborhoods are available as unannotated 11x11 raw PNG crops (edge-clipped only at crop bounds), with per-point exact RGB, modal RGB/count, unique-color count and dimensions in JSON/CSV. The individual PNGs are not resampled or marked; the board enlarges them nearest-neighbor for inspection. Numeric values do not override topology or establish material identity.

## Artifacts / method

`audit_landmarks.py` verifies file dimensions/hashes by output, exact crop-to-source pixel equality and each row's translation, computes point RGB and finite radius-5 local histograms, exports fullcrop copy, crosshair board and raw zoom board. It performs no color segmentation, edge detection, contour tracing, model inference or rendering. `numeric-audit.json` is complete; CSV is a flat review table. Images: `pristine-fullcrop.png`, `numbered-crosshair.png`, `raw-zoom-board.png`, and `zoom-patches/<ID>-raw.png`.

Image-board text intentionally gives IDs and source coordinates only, never RGB or the expected semantic answer, to avoid leading a fresh image-only judgment. Preserve original teacher PASS and source materials unchanged; this audit marks a specific disputed landmark and does not claim all teacher evidence failed.
