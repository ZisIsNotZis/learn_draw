# S1a — learn a continuous two-sided ribbon family

## Authority, provenance and ownership

User said “go” after bounded S0 acceptance, continuing the approved learning roadmap and requested
`github-copilot/gpt-6-luna` implementation with parent orchestration. Repo /home/z/vibe/learn_draw,
master base HEAD 24693d4; S0 and planning changes are deliberately uncommitted. Preserve ALL those
changes plus user staged .gitmodules/vendor and untracked .agents. No commits, pushes, installs or
baseline promotion. Parent owns official docs/state; one worker owns this new component seam.

Read AGENTS.md, WORKSPACE.md, STATUS.md, docs/drawing/{roadmap,spatial-model,method}.md and S0's
parent-validation.md. Roadmap S1a is the contract. The renderer's known limited opaque-triangle and
coplanar tie behaviour remains. Do not edit S0 implementation/tests to rescue a new component.

## Learning question and scope

Can one local (u,v) strip, constructed from a compact set of meaningful bend/taper/twist/attachment
parameters, remain connected and readable across variations, with front/back colour determined by
surface orientation and visibility by depth?

This slice learns **ribbon**, not hair. A ribbon generator is not proof of hair silhouette/grouping.
Hair assessment remains an explicit S1a follow-on if not demonstrated. No figure fit, unknown
reference-ribbon route, detailed shading, animation, universal scene DSL or native image generation.
Models observe images but output text/code; no generated sprite, tracing or long coordinate lists.

## Exclusive edit seam

Add a small reusable generator in scripts/ribbon_family.py (or justify another single descriptive
new filename), dedicated scripts/tests/test_ribbon_family.py, and exercise work/evidence/teaching
files. Existing visibility, sketch, figure, art assembly, baseline, vendor and official docs are
read-only. Reuse visible_regions and existing Chromium rendering utilities. If their real limitation
blocks progress, isolate evidence and ask parent; don't widen this task or silently patch the engine.

## Public interface and geometry responsibilities

Define a compact inspectable input spec with human meanings, units, supported ranges and explicit
validation. Prefer width/taper, length, bend magnitude/family, twist and one attachment/frame over
arbitrary control-point arrays. Any authored shape must stay within the approximately four-point
rule; computed mesh coordinates are compiler output. Avoid separate contour lists per example.

Keep artwork in a continuous local u/v domain. Build a stable support frame; demonstrate its
behaviour under curvature/twist and avoid sudden normal sign flips. Winding-based facing chooses
consistent front/back artwork colours after projection, not manually assigned visible intervals.
Width is measured perpendicular to the centerline/frame; explain taper and endpoints. Keep
attachments fixed under the declared shape changes. Reject invalid inputs or document bounded
limitations rather than hiding singularities. Geometry/tessellation and line-design remain separate:
no triangle edges as art lines; simple fill-boundary identity is enough for this structural exercise.

## Preselected cases (lock before judging; don't cherry-pick)

Record exact parameter values and two fixed camera poses in work/cases.json before rendering a
candidate for acceptance. These classes are mandatory; variants reuse the same generator:

1. Teaching: a gently bent untwisted strip attached at one end, sides easy to identify.
2. Bend-only variation: increase/change curvature with all other semantics held constant.
3. Width/taper variation: visibly narrower tip while attachment and centerline remain fixed.
4. Twist-only variation: enough twist to expose both sides; no per-view colour flags.
5. Awkward projected crossing: distant u sections overlap in projection at different depths without
   true surface intersection; visibility must follow actual depth, not strip index or painter order.
6. Body-card interaction: continuous strip has near and far portions around a simple opaque support;
   show an unobstructed local/full-strip view as well as occluded views, without splitting artwork.

Use at least two meaningful camera views of the same cases (yaw/pitch permitted); avoid a wholly
edge-on width presentation as the only evidence. Do not invent figure anatomy. Prove at least one
positive and one negative depth probe independently of renderer paint ordering. State supported
parameter range and approximation/tessellation tolerance, not universal correctness.

## Deliverables and tests

- Runnable generator/CLI taking compact spec; deterministic named SVG paths plus PNG renders.
- Teaching card: parameter meanings and units, commands, one example, causal good/bad examples,
  limitations, and distinction between full component, support and generated visible fragments.
- Learning board: required cases and both cameras, legible sides/attachments, unobstructed versus
  occluded comparison. Labels explain diagnostics but an unlabelled companion permits visual reading.
- Tests: local continuity/shared boundary identity; attachment invariance; width/taper measurement;
  winding/facing and twist behaviour; stable frames/finite normals; depth-positive/negative probes;
  order reversal away from exact ties; parameter validation; deterministic regeneration; no mesh
  edges masquerading as art. Include genuine failing-input examples in teaching notes.
- Existing targeted S0/figure suites and scene smoke must still pass; run baseline read-only gate
  if applicable. Draw check the learning board and unlabelled view, preserve report.txt image lists.
  Hash deterministic renders and log commands/results against actual source hashes.
- Prepare a small learner packet: public interface + teaching card + example commands, sufficient
  for a new ordinary VLM to author a spec. No completed held-out answer. Parent selects and runs the
  unseen-use task after implementation/visual review; worker does NOT certify that gate.

## Acceptance division and stop rules

Worker implements and validates geometry; parent inspects diff/test results; fresh image-only reviewer
assesses readability; fresh ordinary VLM attempts unseen combination without developer rescue. Keep
implemented/test-passed/visually reviewed/transfer-passed separate. No claim full S1a passed merely
because the board rendered. Existing reference ribbon routing and hair-family claim remain open.

Use finite command deadlines and avoid long opaque loops. If progress runs into renderer cost,
reduce diagnostic subdivisions with stated tolerance, not scope or depth correctness. At deadline
checkpoint after active tools: changed paths, commands/results, artifacts and exact next step. New
backend/dependency or material contract requires parent decision. No child delegation.

Final report: public API and tested range; cases file; generator/tests/card/packet paths; actual checks
and hashes; report.txt image lists; failures/risks; what remains for visual/unseen-use/hair gates.
