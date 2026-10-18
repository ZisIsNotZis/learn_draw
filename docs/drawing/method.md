# Drawing method — observation and review loop

> The current 2D drawing loop below is historical/operational. For the component-on-surface
> method, [`spatial-model.md`](spatial-model.md) owns the architecture and [`roadmap.md`](roadmap.md)
> owns current product milestones, gates, and work-package rules. The concrete [R1 task contract](../../.scratch/35-r1-articulated-study/spec.md)
> specifies the current R1 plan. Do not prescribe manual occlusion splits or infer depth from global
> paint layers in new work.

## Current learning unit

Use the visible milestone and work-package contract in `roadmap.md`. A teaching example, generator, test, or fresh-model attempt is supporting evidence, never a substitute for a user-judgable rendered artwork. Learn from real examples, vary construction, retain causal failures, and generalize only after distinct uses. Models may inspect images but output text/code only; generated image assets are not a substitute. Construction/attachment, physical non-intersection, depth visibility, visual/art review and fresh-model transfer establish distinct claims. A rescued learner attempt is not unaided transfer.

## Current spatial learning loop

Follow [`roadmap.md`](roadmap.md): study applicable vendor and local methods, construct a bounded visible work, vary it, preserve success/failure and review the actual image. Establish plausible connected construction and attachment, separately check physical intersections, separately check depth visibility, then judge drawing/art; colour/material follows only when structure supports it. Reference observation may seed semantic parameters but never runtime geometry. Visual review needs actual image modality; code cannot substitute. If unavailable, mark the gate BLOCKED/UNVERIFIED and do not make runtime repair the objective.

## Legacy 2D loop (not the spatial authoring contract)

The following painter-order, path-edit and reference-compare guidance describes the retired/legacy
2D resolver workflow only. It must not override the spatial architecture or new milestone gates.

Loop: **observe → plan → draw → compare → reflect → revise**, cycled. Line art first, coloring second, soft fields last.

## The loop

1. **Observe**: describe the target semantically in words first — subject, pose, composition, palette, what each region *is*. Never start by writing paths.
2. **Plan**: shape inventory + draw order (painter's algorithm: background → body → clothes → hair → hat → face → details). The SVG layer structure mirrors this plan; that is what makes it explainable.
3. **Draw**: line art stage = strokes on region boundaries and compact dark regions, no fill (this
   reference has no uniform black line art — see T1 correction). Big silhouette → medium structures →
   small details. Coloring stage = fills against `ref palette` swatches. Soft-field stage = gradients,
   blurred blobs, opacity, blend modes (see Tier ladder) — *last* (12-fields), never before structure.
4. **Compare**: `check ART --ref image.jpg` — one command, whole bundle. Then read `report.txt` and
   hand its image list to a fresh-context reviewer (see Guardrails). For a targeted question, fall back
   to `compare --region x,y,w,h --zoom 2` / `diff`.
5. **Reflect**: written note per iteration in `log.md` — what was wrong, what changed, why. Each reflection ends by asking: what is the *transferable* principle here? Distill into `docs/drawing/principles.md`.
6. **Revise**: edit the named paths, commit as `v<N>`, re-run diff. Git history = my learning curve; roll back when a "fix" makes it worse.

## Historical legacy 2D resolver tier ladder

- **T1 line art** — SVG strokes, no fill. Hardest sub-skill: spatial relationships (occlusion, where curves terminate) — diff hints for these look unexplainable; see invariant 3.
  *Corrected 2026-09-14:* this reference has **no uniform black line art** — measured, only 12.6% of its
  pixels are below gray 95, and the figure's read comes from flat-colour boundaries plus compact dark
  regions. So XDoG extraction is a dead end here (P10 agrees: it turns anime interiors into noise).
  Structure comes from region decomposition and traced boundaries; a stroke is then drawn on the
  boundary that matters. See `05-portrait-scene/evidence/diagnosis/`.
- **T2 flat color** — SVG fills. Reference: k-means palette.
- **T3 soft fields** — gradients, blurred blobs, opacity. Core idiom available *today*: **layered flat blobs under a shared silhouette, painted bottom-up** (every layer stays nameable). The painter's clipping-mask idiom (hard silhouette clip + blurred blobs inside, `mix-blend-mode`) is documented aspirationally but the back end has no clipPath/blend support yet — do not write a spec that needs them until 12-fields lands the capability. Soft fields come **last** (rung 12), never before line structure.
- **T4 photo realism** — stacked blurred-blob decomposition, feathered silhouettes, texture. Research tier; needs field-decomposition tooling (gradient direction/extent hints). Not scheduled.

## Historical legacy 2D curriculum (archival, not current milestone sequence)

`.scratch/08..13` records the former 2D resolver exercise ladder. Its rung order, `draw check` closure,
resolver diagnostics and path-coordinate rules are historical evidence; they are not current R1–R4
work-package instructions or automatic gates. Current milestones, review modality and feedback order
are governed by `roadmap.md`; retain any old rung outputs only as historical evidence.

| rung | teaches | vocabulary it is allowed to demand |
| --- | --- | --- |
| L1 bust (08) | line-art discipline, relational basics, the hardest small part: the face | `eye`, `brow/nose/mouth` marks, `hair-mass` |
| L2 torso (09) | occlusion as *declared relations*, cloth around the body | `sleeve`, `bow`, `collar`, `hand` |
| L3 cloth (10) | regular structure from generators, folds as flow | `pleats`, fold `flow` |
| L4 ribbon (11) | generated band + wrap-around z-split | `ribbon` refinements |
| L5 fields (12) | the soft tier, and why it comes **last** | blur discipline, clip+blob idiom |
| L6 assembly (13) | the composition itself as relations | none — proves the level holds |

Then the withdrawal that makes the end goal real: (a) redraw the assembled figure from its own
spec with the image closed (canon extraction already happened during the ladder); (b) draw a *new*
subject from intent alone. Starry-Night-class complexity is the stress test after that, not before.

## Legacy resolver SVG/CSS output notes (not the spatial authoring contract)

These describe only what the retired/current-2D resolver emits; the authoring language is `abstraction.md`. For new component artwork use the support-surface architecture and the roadmap/R1 task contract.

- viewBox matches reference pixel size; coordinates in reference space.
- `<g id="...">` per semantic part, painter order top-to-bottom in document.
- Every shape: `id` + adjacent comment stating intent ("hair pull-point convergence curve"), not appearance trivia.
- Forward-compatible names (`hairStrand3`, not `path_17`); no magic numbers where a formula reads better.
- CSS allowed for soft fields (layered gradients, blur, blend modes); SVG for structure. One source file per iteration — either `.svg` or `.html` wrapper.
- Blur never touches structure (silhouettes, outlines, face features). If a soft field cannot state why it is soft in one line, it is deleted (12-fields rule).

## Legacy resolver tool usage

The commands below are documented for the legacy 2D resolver/evidence format. Current milestone
artifacts still need an image-list evidence bundle where applicable, but follow `roadmap.md` and the
linked WP contract for authoritative acceptance, not legacy metrics or exercise sequencing.

- `check ART [--ref REF]` — **the whole visual feedback bundle in one command** (0.3s for a 1024² draft).
  Emits into `<exercise>/evidence/check/`: a whole-frame side-by-side (panes ≤600px), the **1:1 draft
  at full resolution**, the worst regions as 2x magnified REF|DRAFT crops — including one crop on the
  worst error *where the draft actually drew something*, so detail is judged where it exists rather
  than only where mass is missing — `report.txt`, and the metrics line with the delta against the
  recorded best. **It carries no verdict by design** — it refuses to tell you whether the drawing is
  good, because that judgment is the reviewer's.
  Omit `--ref` for the reference-free stage: the bundle is the **1:1 drawing** (`draft-fullres.png`,
  listed first) plus a bounded `draft.png` preview for layout only, with an adjusted protocol — a
  reviewer judges detail on the 1:1 image, never on the preview.
- `baseline ART [--ref REF]` — record ART as the project's best artifact (the ratchet floor). Only
  ever called after a passed gate; `check` compares every later render against it.
- `compare REF SRC [--region x,y,w,h --zoom N]` — ad-hoc side-by-side, one attention pass. Detail
  comparison happens per region, never on the full frame.
- `diff` line mode: overlay of edge maps — **cyan = reference-only (missed line), magenta = mine-only (invented line), white = match**; numbered hint boxes on worst missing regions. Color mode: amplified color-distance heatmap + worst-region boxes; prints edge-F1 + mean color distance.
- `ref palette` — preprocessing; generate once per exercise, draw against these. (`ref lineart`/XDoG
  is available but **not** useful for this reference — see T1.)
- `log` — appends iteration row (metrics + note) to the exercise's `log.md`.

## Guardrails

- **Historical legacy 2D baseline rule:** old `draw check` bundles compared against
  `.scratch/00-tooling/baseline/`, and old baseline promotion required the then-applicable gate.
  These baseline records remain historical; they do not define the current R2 contract or waive any
  roadmap/R1 gate.
- Metrics are progress signal only (invariant 4 in repo AGENTS.md). `check` prints them as a
  **breakage alarm**: a jump means something broke, a good number never means the drawing is good.
  `coverage` is additionally an **omission floor** — it answers "how much did you leave out?", the
  question `color_dist` cannot answer. Floors and alarms, never targets.
- Historical legacy 2D-loop note: former exercises allowed up to ~3 focused fixes per problem. This is not the current R1 attempt budget; use the concrete R1 contract and roadmap for current candidate/repair limits.
- **Never judge your own render.** Run `check`, then give `report.txt`'s image list — and nothing
  else — to a FRESH-context reviewer with the open question "what is wrong here?". No leaked intent,
  no history, no suspected verdict (a reviewer that knows what you were trying to do will confirm it).
- **A reviewer must prove it can see before its verdict counts (added 2026-09-15).** Vision is not
  stable across subagent instances in this environment — some are sighted, some return "model does not
  support images", and the orchestrator has no vision at all. So the first thing a reviewer is asked
  for is **one fact only a sighted agent could state**, checkable against a measurement already in the
  repo: e.g. "the target has a large field shape left of centre — what colour is it, and roughly where
  does its right edge stop?" (mint `#7dccc1`, right edge ≈ x718). A reviewer that cannot answer is not
  sighted, and **its verdict is void — not negative**. Fall back to measurement plus source-level
  structure, and record explicitly that the visual half of the gate was not run. A fabricated visual
  verdict is worse than a missing one.
- **Record the A/B mapping in the log the same session it is handed over**, and confirm it by pixel
  comparison against the two source files — never from memory. A swapped pair inverts the verdict.
- Critic findings are observations first and *locations* second: verify every spatial claim against a
  measurement or the crop's own coordinates before acting (P7). Reviewers reliably describe what they
  see and mislabel *where* they saw it; the `check` bundle names each region's coordinates so the two
  can be told apart.

## Running the loop by delegation (harness facts)

The loop above is executed by a parent that dispatches writers and reviewers, and the harness decides whether a dispatch can do anything at all. What each dispatch must do about the facts that bind it:

- **Size a writer budget inside the harness wall (P34).** A subagent run is killed at the harness wall — 1,800,000 ms (~30 min) observed here — so a dispatch budget larger than that wall is fiction; fit the package inside the limit or raise the timeout explicitly at dispatch, and have the writer commit a checkpoint every few minutes, since reaping (P35) takes uncommitted work without warning.
- **Order the deliverables so the package is true at any kill point (P34).** Source, renders, manifest and `check` bundle first, documentation last — a kill then leaves a smaller package rather than a false one. The mechanical test for "this package is true" is `sha256sum -c manifest.sha256` plus the existence of every listed file, run before any reviewer is dispatched.
- **Never read liveness off `status` (P35).** Runs reaped this session were still reported as running; sample a live process, a new event timestamp and a growing artefact, and treat no process, no new events and no new files as death whatever the status says.
- **Commit the dispatch script before launching worktree-isolated children.** Managed worktree isolation refuses a dirty tree, and writing the script is the dirt; every dispatch script in `.scratch/35-r1-articulated-study/work/` is committed under a `plan:` message for that reason.
- **Pair an image-only reviewer with an execution-capable one (P36).** One judges the picture; the other re-runs the tests, manifests and negative controls and reports the commands that produced them. Pairing is not a substitute for `rubric.md`'s two independent reviewers on the image half.
- **Name the 1:1 image in the review dispatch, and check the bundle is current.** A review this session judged a thumbnail — `.scratch/35-r1-articulated-study/evidence/B-hand-v2/check/draft.png` is 256×121 for a 1350×640 sheet — and its reviewer reported "the image arrived at thumbnail scale". `scripts/draw.py` now writes `draft-fullres.png` and lists it first; a bundle older than that change is stale evidence to regenerate, not to dispatch.
- **Run a documented command before trusting it (P38).** At session start none of the loop's commands ran — a missing `.venv`, a module absent from the environment, a deleted renderer revision, no committed dependency file. A command surface that cannot run is a gate failure, and the repair is declared dependencies, dynamically resolved paths and a wrapper that degrades to an available interpreter.

## Judging (P14 reframe)

Primary criterion: the drawing looks like a proper artwork in the reference's style — judged by looking at the full render and by fresh-eyes critic review. Zone-distance/edge metrics are weak regression signals only (catch accidental breakage), never objectives to tune against. Holistic semantic shapes outrank pixel correspondence; a fragmented but "closer" draft is worse than a coherent drawing.
