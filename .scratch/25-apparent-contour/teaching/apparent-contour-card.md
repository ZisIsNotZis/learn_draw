# Exercise25 teaching card — a camera-apparent surface-turn cue

## Drawing question

The clean Exercise24 replay gave no clear readability benefit to the `.35` transverse support: a blind observer still could not tell whether the positive arch half-turn was one continuous two-sided sheet or separate pieces meeting, in either view. Source triage confirms that this arch is a half-turn, not a crossback; the negative learner's one-third taper is intentional. This is one bounded perception result, not a claim that every transverse curve is useless.

## Rule tested

A local material edge is not automatically the camera's apparent silhouette. For the same unchanged `.35`, `96x12` surface, the renderer derives possible turn-contour candidates from its complete actual support mesh and current camera. A shared edge is considered only when its actual adjacent facet normals face opposite ways. Even then it is not drawn unless:

1. both projected facets fold to the same side of their shared edge and have positive-area projected overlap;
2. their actual projected depth planes separate by more than the already-established `1e-5 + EPS` tie band in the overlap; and
3. the edge interval remains depth-visible against every nonincident support face.

The single fixed treatment is a restrained `1.2` canvas-pixel ink footprint in `#253746`. Its finite coverage is clipped to the actual visible polygons of its incident support faces using the pinned opaque triangle visibility result. Hidden intervals are kept separate; round joins are only added where visible spans meet at the same original UV vertex. This uses existing clipping and line-footprint utilities and changes no support or kernel.

## Do not conflate roles

These are **faceted surface-turn apparent contours**: tessellated approximations to a camera-dependent turn/silhouette within one continuous supported sheet. They are not a contact edge between independently authored components, not a separate-surface overlap/contact line, not the local material perimeter, not a stripe/color seam, and not all mesh edges. Actual contact/occlusion boundaries have a different semantic origin. Support facets approximate a smoother cambered sheet, so changing tessellation can move these sampled contour segments; this finite case study does not establish a smooth-contour or retessellation-invariance guarantee.

## Cases and interpretation limits

The paired control/candidate boards use every frozen Exercise24 row/camera, with unchanged actual curved support and existing fill-only panel as the control. The two positive arch half-turn views are primary; the two untouched negative failed-learner examples are regression-only; the untwisted arch is a true negative control and should have no internal turn cue. Camera-facing classification is recomputed from the same mesh for each camera. A temporary foreground card is used only in geometry tests to verify hidden centerline/width clipping.

The selected edge weights are fixed before candidate images. The worker records geometric evidence and reference-free image lists but does not judge the comparison. S1a remains open until parent blind review and any later gate; this card is not a learner transfer pass, complete line-art method, or production framework.
