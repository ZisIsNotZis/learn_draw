# S1a bounded teaching artifact — connected two-sided ribbon

## Before changes: interpretation, scope, proof plan

Interpretation: deliver only the roadmap's bounded teaching record: semantic strip inputs, generated connected local artwork on a computed support, depth-computed visible output, one causal contrast/failure, one fixed awkward crossing, one single-parameter shape variation, and a compact learner card. Existing code, tests, and prior evidence are the implementation and proof; this record links them rather than cloning them.

Scope: this is a code/method teaching slice, not a claim that a viewer or learner can read or reproduce the sheet. No code changes, new geometry/backend, image production, appearance tuning, learner run, baseline change, or edits to prior records. No construction-rule hypothesis was added: local source/evidence supports the existing connected-local-sheet + depth visibility method while also recording its communicative limit.

Acceptance/proof plan: verify relative links; run the focused existing ribbon family and visibility tests within the 120-second command limit; run a bounded reference-free generator smoke render in a temporary output directory and check generated SVG/PNG exist. Link checks and commands prove artifact integrity and implementation behavior only. Independent artifact review remains required; S1a perception and transfer stay open.

## Teaching example: semantic input → supported sheet → visible result

The compact input is a small group of semantic choices, not a contour. `length`, `width`, `tip_ratio`, `family`, `bend`, `depth`, and `twist` describe the strip; `origin` and `heading` attach its start and direction; `front`/`back` name its two material faces. Angles are radians, dimensions are world units, and `u,v` are unitless. Example below is the existing arch example (40 computed intervals):

```json
{
  "name": "teaching-example", "length": 3.0, "width": 0.36,
  "tip_ratio": 1.0, "bend": 0.42, "depth": 0.12, "twist": 0.0,
  "family": "arch", "origin": [-1.5, 0.0, 0.0], "heading": 0.0,
  "front": "#e68aa4", "back": "#7188bd", "segments": 40
}
```

The generator computes a continuous centre route `C(u)`, a transported frame and a width axis; taper changes width along `u`, twist rotates that axis, and `(u,v)` spans one connected artwork domain (`u∈[0,1]`, `v∈[-1,1]`). Mesh triangles are support subdivisions, not authored path pieces. A full-length local-v stripe is split within those triangles and inherits their consistent front/back face identity. Camera-facing winding selects face colour. Projection and the opaque triangle resolver compare depth and clip hidden fragments; the author supplies no visibility cut or crossing interval.

Runnable interface (existing source; emits SVG and adjacent PNG):

```sh
.venv/bin/python scripts/ribbon_family.py render \
  .scratch/19-ribbon-family/work/teaching-example.json \
  --name oblique --yaw 38 --pitch 22 \
  -o /tmp/s1a-teaching-example.svg
```

Source path: [`scripts/ribbon_family.py`](../../scripts/ribbon_family.py), especially `RibbonSpec`, `centerline`, `build_mesh`, `ribbon_artwork_triangles`, `face_side`, and `ribbon_faces`; visibility path: [`scripts/vector_visibility.py`](../../scripts/vector_visibility.py) (`visible_fragments` / `visible_regions`). The route is not hand traced and the visibility function receives projected depth-bearing triangles.

## Contrasted failure: valid construction is not sufficient communication

**Constructed candidate:** complete depth-visible semantic perimeter ink plus a side-consistent local-UV motif. Both are valid geometry derived from the same sheet, not arbitrary scribbles. The original untuned fill/stripe control, perimeter-only rule A, and perimeter-plus-motif rule B are recorded in [Exercise 20 drawing card](../20-ribbon-drawing-rule/teaching/drawing-card.md).

**Failure/limit:** the final bounded report says full perimeter ink crowds crossings/twist, the side-consistent motif does not clarify front order, and the saved learner's orange/blue join can read like separate tapered pieces rather than one turning two-sided strip. The two candidate cues therefore do not establish sheet identity. This is a recorded communicative failure/ambiguity, not a claim that the perimeter or motif is geometrically invalid. Details and frozen controls: [Exercise 19 outcome](../19-ribbon-family/outcome.md), [Exercise 20 card](../20-ribbon-drawing-rule/teaching/drawing-card.md). Do not promote either cue rule as accepted readability solution or patch the frozen answer.

## Preselected challenge and variation

- **Awkward crossing:** frozen `awkward-crossing` from [Exercise 19 cases](../19-ribbon-family/work/cases.json), case 5. It is a crossback, with distant longitudinal sections overlapping in projection at different depths; `length=3`, `width=.34`, `tip_ratio=.78`, `bend=.8`, `depth=.72`, `twist=0`, 48 intervals. It is the preselected crossing, not an author-selected screen-space cut. Use existing two-camera case evidence; avoid implying true surface intersection.
- **Shape variation:** the preselected teaching arch's bend-only variation, case 2 in the same frozen plan: `bend` changes `.42 → 1.05` while length, width, frame, and twist remain fixed. This demonstrates parameter mapping to center-route shape without hand-patching projected coordinates; it is not a second failure test. The crossing above exposes the depth/communication limit: depth-resolved overlaps can be constructed without guaranteeing that the sheet reads clearly. Existing generated board/evidence is in [Exercise 19](../19-ribbon-family/evidence/).

## Learner card (for later transfer packet; no author reasoning)

**Interface.** Choose `family` (`arch`, `s-curve`, `crossback`), dimensions `length`/`width`, taper `tip_ratio`, route `bend`/`depth`, twist, attachment `origin`/`heading`, and front/back colours. Render with `scripts/ribbon_family.py render SPEC --name VIEW --yaw DEGREES --pitch DEGREES -o OUTPUT.svg`. The compiler computes the frame, local surface, mesh, face assignment, projection, and visible fragments. Do not enter screen coordinates or visibility intervals.

**Construction rationale.** Keep the artwork on one connected local `(u,v)` sheet; let the support frame carry it through space. A local motif stays attached as the sheet bends/twists. The support mesh discretizes that surface; it is not a collection of separate drawn ribbon pieces. Depth comparison, rather than manually chosen front/back cuts, determines what survives in a view. Change a semantic parameter, not emitted vertices.

**Known limits.** A geometrically valid connected two-sided ribbon may still fail to read as one turning sheet: joins/crossings can remain ambiguous and extra perimeter ink can crowd them. This family and opaque-triangle visibility are bounded; exact coplanar ties are declaration-order dependent, and arbitrary intersections, degeneracies, transparency, and continuous/global collision correctness are not established. Colours or stripes do not guarantee readable face identity. Construction tests are not visual acceptance. No reference fit, accepted perception result, or learner transfer is claimed.

## Evidence and state

- Implementation/tests: [`scripts/ribbon_family.py`](../../scripts/ribbon_family.py), [`scripts/tests/test_ribbon_family.py`](../../scripts/tests/test_ribbon_family.py), [`scripts/tests/test_vector_visibility.py`](../../scripts/tests/test_vector_visibility.py).
- Prior validated interface/construction record: [Exercise 19 outcome](../19-ribbon-family/outcome.md).
- Drawing-rule positive/negative evidence and limits: [Exercise 20 card](../20-ribbon-drawing-rule/teaching/drawing-card.md), [Exercise 20 outcome](../20-ribbon-drawing-rule/outcome.md).
- Support variation rationale and finite-mesh limits: [Exercise 21 card](../21-ribbon-cross-section/teaching/transverse-support-card.md).
- Vendor method mapping: `docs/drawing/roadmap.md` dispositions; `vendor/huashu-art-motion/references/02-机制.md`, `04-纯代码绘制.md`, and `07-正面经验.md` are adapted only for semantic structure/reuse and independent review. Flat painter order, animation, finish and generated characters are excluded.

Transfer status: **UNRUN**. `.scratch/28-local-art-identity/teaching/learner-packet.md` prerequisites are unmet. This artifact does not pass S1a visual readability or transfer; fresh independent artifact review is still required.
