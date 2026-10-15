# A teacher-only topology map — not artwork geometry

**Interpretation status:** provisional observations from the complete registered crop; all landmarks and object IDs are hypotheses for a fresh semantic reviewer to verify against source pixels. No region here is a segmentation mask or a traced boundary. The overlay's polylines/markers are visual pointers and topological hints, not drawable contours.

## Provenance and registration

- Source `image.jpg`, SHA-256 `322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb`, 1024x1024.
- Full teacher crop `source-crop-registered.png`, PNG SHA-256 `52e01f5e75e5d98fcd9a0a4ac63be91ed09b8a18ca0f62e7e0348a021b2dd87d`, exact source pixel rectangle `(500,320)-(900,800)`, 400x480, no resize/stretch. Recomputed crop/source file hash and dimensions on 2026-10-13 13:56+08.
- Registration: crop `(x,y)` = source `(500+x,320+y)`. `landmarks.csv` contains both coordinate pairs for each anchor. Crop origin is inclusive and crop max bounds are exclusive.
- Teacher overlay algorithm: Pillow 11-compatible `ImageDraw`/Lanczos; input is the byte-identical registered crop; display enlargement 2x only for annotation readability, no landmark coordinate transform except `display=(2*x,2*y)`. Draws finite ID markers and thin dashed schematic adjacency pointers; no pixel classification, frequency segmentation, edge detection, contour tracing, or runtime input. See `make_teacher_overlay.py` for exact colors, marker placements, command and input digest check.
- File role: teacher-only review evidence for A; not included in B or heldout and must not be imported by scene/renderer/reproduction. This map is independent of frame renderer geometry.

## Visible component inventory and topology hypotheses

| ID / object | Source-pixel evidence and semantic reading | Relation / edge meaning | Confidence and limits |
|---|---|---|---|
| `neck-skin` (`N1`) | Pink neck-skin field between the cropped lower-face region/hair and pale collar pieces. | Visible skin occupies the garment neckline opening; collar borders its lower/side perimeter. Upper/head extent is cropped and partly covered by hair. | Interior field high; full opening contour is not claimed. No face/anatomy reconstruction. |
| `collar-left` (`CL1`,`CL2`) | Light cream/blue collar leaf on image-left side of opening, with a dark navy curved trim along its lower/front edge. | Adjacent to neck skin and bodice; trim marks a real high-contrast edge/binding, not proof of a separate collar-to-bodice seam. | Medium; outer endpoint/hidden join overlaps hair/bow or is softened. |
| `collar-right` (`CR1`,`CR2`) | Broad light-blue collar area at image-right of the skin opening, with dark curved lower/front trim. | Frames the opening on the right and approaches shoulder/sleeve area; hair overlaps the upper/outer continuation. | Medium; any internal right leaf seam is uncertain. Do not invent two perfectly symmetric leaves. |
| `bodice` (`BD1`–`BD4`) | Pale garment visible at both sides of the bow and down the right torso; visible lower edge around the waist. | Underlies the collar and chest bow; joins shoulder/sleeve near `BD2`. Bow overlays the chest. Several portions are occluded by the bow and foreground non-target forms; the left outline is not fully visible. | Body identity high; exact complete silhouette/waist contour medium/low. `BD2` armhole construction and hidden sides remain unknown. |
| `right puff sleeve` (`SC1`–`SC3`) | One continuous pale sleeve mass from rounded upper cap around shoulder into a narrowing lower sleeve. | Attached to bodice in shoulder/armhole neighborhood; flows to dark cuff at `CU1`. The crop shows no reliable seam separating cap from tube, so cap→tube is a descriptive volume transition, not a proven garment seam. | Outer silhouette high where visible; attachment curve medium/low due hair, adjacent body and crop context. |
| `cuff` (`CU1`) | Dark navy band around sleeve opening near lower/right crop edge. | A real high-contrast trim/band edge at sleeve opening; sleeve fabric terminates at/under it. Its rightward continuation is clipped by crop x=400. | Band presence high; full circumference and far-side edge unknown. |
| `bow-knot` (`BK1`) | Central pink gathered/overlapping knot on chest. | Connects two unequal visible loop regions and two visible ribbon tails. Small interior strokes converge/fold toward knot; they are fold/tie indications, not extra cut edges. | High for object, approximate center. Exact hidden wrap geometry is unknown. |
| `bow-left-loop` (`BL1`) and `bow-right-loop` (`BR1`) | Two pink closed broad lobes to the left/right of knot; right loop is visibly broader. | Both meet/overlap at knot. Thin dark interior marks indicate folds/creases; the outer dark stroke/color transition is a real loop silhouette edge. | High; local boundary under knot is overlapped. Avoid treating internal fold strokes as separate ribbons. |
| `bow-leftward tail` (`TL1`) | Pink strip trails left from the knot to an overlap/contact neighborhood with a blue band around crop `(44,209)`. To the left of this point, only the blue band is visibly continuous to crop x=0; the pink does not visibly cross the crop edge. | The pink-to-blue overlap may be occlusion, attachment, or apparent endpoint; neither tail continuation beneath/within the blue band nor a true endpoint is established. The crop edge itself is not evidence that the pink tail is clipped. | Medium for visible pink/blue meeting; low/unknown for identity and continuation of the blue strip. Do not label the blue strip as part of the bow and do not complete a tail route. |
| `bow-down-tail` (`TD1`) | Pink descending ribbon strip from knot, tapering to a visible point below-left of knot. | Separate visible tail route; its tip is inside crop. Local overlap around its lower edge with dark/light forms makes the exact terminal pixels less certain. | Medium. Keep marked for reviewer check; do not infer hidden backside/folds. |
| `hair/foreground occluders` (not a garment label) | Blue hair overlaps parts of collar/shoulder; pale/dark foreground forms cross portions of lower chest/bow-tail neighborhood. | Occlusion boundary is not cloth seam. This map labels only visible clothing targets and does not classify these foreground forms as garment evidence. | Their full identities and continuation are out of scope/unknown; no hidden person/hand anatomy is inferred. |

## Landmark semantics and confidence

`landmarks.csv` records ID, crop pixel, corresponding source pixel, semantic purpose, confidence, and pixel-observation limitation. Marked points are **anchors on visible evidence**, not a dense tracing, inferred feature boundary, or claim of exact subpixel intersection. High confidence means the indicated interior/transition/object is directly visible at the point, not that its full contour is known. Medium means local object evidence exists but a boundary/overlap is ambiguous. Low is deliberately retained for the sleeve/body attachment zone.

Topology relations to check:

1. collar-left + collar-right frame visible neck-skin opening; hair occludes some outer continuation;
2. collar/bodice meet near shoulders; bodice remains a connected torso cloth region but portions are hidden;
3. right shoulder cap transitions continuously into sleeve tube, terminating at a dark cuff band; no unsupported cap seam;
4. chest bow knot joins two unequal loops and two visible unequal-direction pink tail segments; the leftward tail meets a blue band around `(44,209)` and its continuation/end is unknown; do not use the crop edge as proof of a pink-tail truncation;
5. bow sits over bodice; visible thin interior lines are fold marks, while outer high-contrast silhouette/trim edges are actual part boundaries. Where occlusion prevents distinguishing a seam from a fold, the map says unknown.

## Unknowns and crop limits

- The crop includes a partial lower face at the top; it is not evidence for reconstructing a head/face. Neck skin is visible, but hidden neck/body anatomy is unknown.
- The leftward pink tail meets/overlaps a blue strip near `(44,209)`; only that blue strip is seen continuing left to crop x=0. Whether the pink tail ends, turns beneath the blue strip, or continues as some distinct object is unknown. There is no visible pink pixel at the crop boundary; do not assert a crop-truncated pink endpoint or infer the blue strip belongs to the bow.
- Sleeve cuff reaches the right edge neighborhood; complete cuff circumference/right continuation is not visible. Bodice/lower garment continue toward the bottom crop edge and are not to be completed.
- Bow and foreground forms occlude parts of bodice; hair occludes collar/shoulder. Hidden seams, back surfaces, far sleeve, and full torso are unknown.
- Square ROIs/RGB-frequency summaries in the older `teacher-observations.json` identify viewing windows only; they are not masks or evidence of segmentation. The narrower focus crop `(74,65)-(384,418)` omits bow-left evidence from x<74; this package uses the full 400x480 crop.

## Fresh semantic-review threshold (not art gate)

PASS only if reviewer independently locates each required object and its relevant adjacency/opening/seam/fold/occlusion in the registered crop; verifies landmarks against both crop/source mapping; finds the left-tail/blue-band ambiguity and other unknowns correctly disclosed; and identifies no invented hidden anatomy or unsupported endpoint. A specific local annotation/mapping defect may receive one bounded correction and narrow re-review. Unclear required topology remains UNVERIFIED/FAIL and blocks family fitting. This does not judge the art, renderer or R1/user milestone.
