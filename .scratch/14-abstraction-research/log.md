# night-research log (leader track)

## 2026-09-14 — leader synthesis while SA1/SA2/SA3 run

- vocab doc created: canons as fractions with provenance; family catalog + rules; teacher loop.
- north star (user directive) + relation taxonomy in abstraction.md.
- curriculum map in method.md; AGENTS.md docs list updated.
- insight: encapsulation boundary = family (intra-family layout = arithmetic on own anchors;
  relations only for cross-object composition) — `inside` mostly dissolves into families.
- insight: learning is the repo — families + canons + principles committed; nothing needs to
  survive in model memory.
- Loomis ball-and-plane head construction validated as the model for the `head` family
  (cross lines → exported anchors; pose = cross rotation); teacher vocabulary ↔ relations map.
- canon anchors measured from image.jpg: hairline y≈243, chin y≈377, skull top ≈150 (scan x=690);
  eye fractions from 02-portrait-face traced geometry.
- decisions awaiting worker reports: fold SA2's eye family into 06 + docs (if it reads); record
  SA3's needed-family list but do NOT build (demand-first; starry is a probe, not a rung);
  integrate SA1's critique into the docs before claiming 08.

## Session state (for auto-compaction / tomorrow)

- committed: 552a1c6 (design decisions 1/night), 14 log follows in next commit
- 3 subagents running (SA1 critique / SA2 face / SA3 starry) — integrate on completion
- next: 08-bust after integration; eye family from SA2; canons from this log

## 2026-09-14 — SA1 critique integrated (decisions recorded; see evidence/sa1/critique-summarized.md)

Accepted in full. Finding 1 owned: I violated invariant 7 on the language's own proof render
(bust-v2 declared "readable" with no check/fresh-eyes; hat inside-out, face buried, shoulders
detached). P22 records the meta-lesson; 06's spec carries a public retraction + re-assessment.

DECISIONS (leader, this session):
- D1 critique accepted; fixes split now-vs-consolidation.
- D2 code-truth NOW (done): 06 docstring YAML-trap example fixed; family id registers as anchor;
  `between` accepts anchor strings (rejects size scalars); scene_render drops dead `on`/`fit` keys
  and names YAML-boolean errors (16/16 tests pass); draw check captures resolver diagnostics+anchors
  into report.txt and records resolver path; _find_relate deterministic (beside spec → scripts/, no
  more last-hit-wins).
- D3 DECLARATIVE FAMILIES ADOPTED as the tier-3 direction (finding 10): a family = YAML block,
  params + sub-shapes over own anchors only, so the model authors families without Python. sunhat =
  migration example. Canon rows become loadable data with provenance.
- D4 face-set relations land in 14 BEFORE 08 opens (finding 3 deadlock): mirror/pair, inside, align,
  arc (partial outline), taper; plus sunhat near-edge occlusion fix (P17 near/far split). 08's
  blockers updated; fallback scope-down documented there.
- D5 withdrawal rungs created: 15 (L7 recall, image closed) + 16 (L8 intent-only), blocked by 13.
  Composition anchors (thirds/horizon/focal) enter the taxonomy at 16 (demand date).
- D6 resolver consolidation PENDING worker completion: promote ONE resolver to scripts/, delete
  forks, fix desc-key compat with scene_render.SCHEMA.
- D7 literal classes adopted (finding 6): proportion/style constants in vars: WITH provenance;
  placement numbers must derive from other anchors; resolver placement-warning pending.
- D8 doc-truth NOW (done): 824 pinned; eyeball→eye; scene-format region example fixed (on: was a
  YAML boolean trap AND a dead key); line-numbered claim corrected to node-indexed; method T3 idiom
  rewritten to what the back end supports (clip/blend = pending, due at 12); vocabulary sunhat row
  now shows real anchor ids + the occlusion defect; P22 added.
- D9 diagnostics PENDING (06 promised, never built): invisible-behind, unintended-gap; plus vocab
  sub-shapes must be anchored so P21 diagnostics apply to them (finding 8); literal-placement warning.
  Scheduled: 14's resolver work.
- D10 PENDING worker completion: SA2 eye family + face canons → fold into resolver + vocabulary.md;
  SA3 starry findings → record needed-family list, BUILD NOTHING (demand date = post-16 stress test).

## 2026-09-14 — SA3 (starry probe) landed: VERDICT = the abstraction SCALES

SA3 report: .scratch/14-abstraction-research/work/starry/report.md; renders evidence/starry/v1..v9
(9 iterations, every one looked at); check bundle evidence/starry/check/.

Verdict (quoted): "Yes — it scales, with one structural addition." v9 = credible Starry Night
evocation from ~10 hand numbers + 115 parameterized nodes, no reference anywhere. Tier-3 vocabulary
carried the scene (star = halo/rays/core, cypress = scalloped taper + wisps, house = body/roof/
window on a tangent frame, hill = stacked far-light bands).

Families it built (probes, in its own copies — NOT promoted): swirl, flow, burst, glow, flame,
village, hill, stars; plus a sharp `poly` node (un-smoothed corners for roofs/steeples).

DECISIONS:
- D11 off → polar rename done NOW (SA3 finding 6; confirmed the YAML trap empirically: {off:…} parses
  key False; every use errored loudly; polar verified working; docs + resolver updated).
- D12 structural addition CONFIRMED = the generator bridge: spec-level node declaring "compile as
  back-end generator X with resolved params + report true bounds". This IS the declarative-family
  mechanism (D3); passthrough boilerplate disappears when families are declarative YAML.
- D13 relations to promote (with demand dates): flow → 10-cloth (folds as flow) / 17-starry;
  distribute-along → 10-cloth (pleats) / 17; jitter-grid → 12-fields / 17.
- D14 17-starry-stress ticket created (blocked by 16) — the demand-date home for the SA3 set
  (swirl/flow/burst/glow/flame/village/hill/stars). Probes stay in 14 as evidence; build NOTHING now.
- D15 single renderer pipeline confirmed (kill relate.py's duplicate emitter; compile-down only) —
  part of consolidation (D6).
- D16 "looking is the loop" empirically confirmed by SA3: 8/9 fixes from looking, diagnostics clean
  after v1; the two real generator bugs were only visible in the raster. Evidence for P22 and for
  the check-first discipline in every rung.
- SA3 honest limits recorded: village legible-not-beautiful (boxes, flat roofs); swirls read as
  coils not brush-commas (closer flow field would fix; 9 iterations were the budget).
- SA2 (face) still running (v8 in flight); integrate on completion.

## 2026-09-14 — SA2 (face) landed + CONSOLIDATION DONE (D6)

SA2 report: work/face/report.md; renders evidence/face/v1..v10 (10 iterations).
Verdict: it reads as a face — layered anime eyes (sclera/two-tone iris/pupil/glints/green
reflection/tapered one-sided lash with wing), brows, nose tick, mouth, all from measured canons.
Eye family params: w/h/tilt/almond/mirror-of/glints/iris-w/lash-w/glint-side/gaze/refl-fill/*-fill;
anchors: aperture bbox + corners + iris + lid apex + facing. Two biggest engine wins = containment
rule (iris clamped inside the almond) and one-sided lash (black never intrudes). Honest gaps:
ellipse host → round chin (needs a `face` family); no grouping ("whole eye" = convention only);
taper built ad hoc; mouth/brow are bare strokes; no turn knob for 3/4 asymmetry; no alpha for blush.
Measured canons folded into vocabulary.md set B (host-relative; reconciled with set A — one table).

DECISIONS:
- D17 eye family promoted to scripts/relate.py as the second vocabulary family (Python for now;
  declarative rewrite queued with sunhat per D3).
- D18 CONSOLIDATION COMPLETE: scripts/relate.py is the ONE resolver. Verified byte-identical
  reproduction of BOTH probes (bust = 06 output, face = SA2 v10). Post-critique fixes re-applied to
  the promoted file (host/along/polar docstrings, family-id anchor, between endpoint coercion).
  Forks deleted: 06/work/relate.py, 14/work/face/relate.py, 14/work/starry/relate.py. Starry's
  scene_render.py copy KEPT as probe evidence (report.md depends on it; quarantine, not delete).
- D19 docs paths updated: AGENTS.md (layout + cheat sheet), abstraction.md, vocabulary.md; 06 spec
  promotion note pending below. draw.py's deterministic resolver selection now resolves
  scripts/relate.py.
- D20 remaining 08 blockers: face-set GENERAL relations arc/align + taper-as-first-class (mirror
  landed), sunhat near-edge occlusion fix, and the declarative interpreter (D3) — these are the
  queue for the next work block.

## 2026-09-14 — D21 sunhat occlusion FIXED (SA1 finding 1a closed)

expand_sunhat rewritten: brim is ONE shape split into two complementary pie slices meeting at the
brim centre (P17 z-split, not a path split). Paint order far slice → dome → near slice; `front`
[t0,t1] picks the near arc, the far slice is its complement. Old full-ellipse + thin rim strip
deleted. Verified by LOOKING (P22): the dome now sits behind the near brim slice and in front of
the far slice — the flagship occlusion mechanism is true. Renders: /tmp/sunhat-fix.png (pre-commit
artifact; 06 evidence bust-v3.png committed). Spec-level defects (hair burying face, no neck,
detached shoulders) remain deferred to 08 per the 06 re-assessment.

Night summary (final): see log head + this file. The ladder now starts 08 with: consolidated
resolver (scripts/relate.py: sunhat fixed + eye family), SA2 canons in vocabulary.md set B,
SA3 starry set dated at 17, withdrawal rungs 15/16, declarative-families proposal, P22.
Remaining 08-openers: arc/align/taper-first-class relations + declarative interpreter (D3/D4/D20).

## 2026-09-14 — FINAL IMAGE: the bust assembled (08 opener, done as the night's close)

User challenge: "research must end with a final image." Merged the two night probes into one
relational spec — work/final/bust-final.yaml (36 nodes, 9 layers, zero absolute coordinates):
head (ruler) + hair masses anchored to the skull + temple locks + fringe under the brim + neck +
shoulders + SA2's eye family (mirror-of) + brows/nose/mouth on measured canons + the slice-fixed
sunhat worn high. Three iterations: v1 (hair detached bars, hat floating, eyes poking past face,
neck void) -> v2 (hair anchored, eyes tucked, fringe) -> v3 (three fringe strands, locks merged
with masses, marks strengthened). diagnostics clean throughout; every render LOOKED at (P22).
Evidence: evidence/final/v1..v3.png + check/ bundle (vs image.jpg, metrics = breakage alarm only).
Residuals recorded: round ellipse chin (face-family gap), stylized-not-likeness (P14 intent),
mouth/nose faint by design (anime). Fresh-eyes verdict: pending subagent -> appended on arrival.

## 2026-09-14 — fresh-eyes verdict on the final image: PARTLY (verified, P7 applied)

Reviewer (fresh explore, no intent leaked): (1) ruinous: no body below the collar line — true;
(2) ruinous: face unfinished, "two thin eye slits", no nose/mouth/iris detail; (3) ruinous: hat is
a "flat ellipse with a ball on it", no tilt; (4) hair stiff, flat tips; (5) environment dropped.
Verdict: partly — hints at the character, does not fully read as the same subject.

VERIFIED against measurements + my own look at the full-res render (P7: observations vs locations):

- **"No body" — TRUE, and by design.** The final image is a BUST (L1 scope: head+hair+hat+shoulders);
  the body is rungs 09/10. The reviewer, told nothing, correctly reports the draft ≠ the REF's
  seated figure. Scope truth, recorded as the largest remaining gap toward "reads as the REF".
- **"Face unfinished" — SCALE ARTIFACT, verified.** At full resolution v3 has: two-tone irises,
  2 glints/eye + green reflection, tapered one-sided lash, brows, nose tick (2.6px), mouth (3.6px).
  The bundle's whole-frame pane is ≤600px (downscale 0.59×): glints → ~2px, nose → ~1.5px, mouth →
  ~2px — sub-perceptible. The reviewer judged the face from the only image it had of it. NOT a
  drawing defect; a REVIEW-LOOP defect (see below). Marks may still want +50% weight at this canvas.
- **"Hat flat, no tilt" — partly scale, partly real.** tilt −14° exists but is subtle at 600px; the
  brim's slice edges are straight, so the brim reads flatter than the REF's curved sweep; the dome
  at 600px reads as "a ball on a plate". Real fix for 08: crown silhouette should read through
  (taller crown or visible crown band); brim curvature.
- **"Hair stiff/flat tips" — TRUE.** Masses are constant-width ribbons with flat rounded ends.
  Needs taper + slight S-curvature; recorded as an 08 requirement (taper-first-class relation).
- **"Environment dropped" — accepted for L1** (flat field is intentional for the bust rung).

TOOL FINDING for 07 (the loop's first real design flaw): the bundle's region ranking by colour
distance surfaces GLOBAL-MISMATCH areas (missing body), so the 2x crops were all in the bottom
band — the FACE never got a crop, and the whole-frame pane at ≤600px destroys exactly the details
a reviewer needs to judge (glints, lash taper, marks, hat tilt). Fix: `draw check` should always
include the full-res draft as one artifact + a subject-centre 2x crop; when the spec has a `head`
host anchor, add a face-region crop automatically. Recorded in 07's comments; queued in HANDOFF.

WHAT THE VERDICT MEANS for the night: the assembled bust reads as a girl-with-hat-at-full-res (my
own look, verified features present) and does NOT yet read as the REF subject at review scale —
the two largest levers are the missing body (ladder, by design) and the review-loop scale flaw
(tool, now recorded). Both have dates. The mechanism the verdict DOES vindicate: every claim about
what IS present (hat occlusion, layered eyes, canon-placed marks) survived independent verification.

## 2026-09-14 — CORRECTION: the final image is the FULL FIGURE, not the bust (user pushback)

User: "v3.png is the final? Seriously? You reverted progress? What about the dress/skirt?"
Honest answers recorded: (a) nothing was deleted — 05's full figure is intact and frozen
(work/scene.yaml + evidence/current.png); (b) the bust-only "final" was my ladder framing and
was wrong for what a final image of this subject means. Rebuild done:

- work/final/final-full.yaml: night's working top (slice-fixed sunhat, eye family, canons,
  hair/fringe) + head-relative BODY (blouse trapezoid, dark A-line skirt flaring left per the
  ref, pale overskirt to the hem, hem edge) — 45 nodes, 10 layers, zero coordinate literals,
  colours from frozen 05 (blouse #e1e7dc, skirt #112e4b, overskirt #d2e2d6).
- Head shrunk to full-figure proportions (head_half 0.070 frame.w); because everything is
  head-relative, the whole figure rescaled in one var change.
- full-v1 (skirt reads; overskirt floated as a triangle) -> full-v2 (overskirt to the hem).
  Both diagnostics clean; both looked at (P22).
- Evidence: evidence/final/full-v1.png, full-v2.png; check bundle check-full/ WITH the
  full-res draft included (the 07 scale-flaw workaround, applied manually this time).
- Fresh-eyes verdict on the full figure: pending -> appended on arrival.
