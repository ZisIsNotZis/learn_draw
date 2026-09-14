# Drawing method — reference recreation via programmatic art

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

## Tier ladder

- **T1 line art** — SVG strokes, no fill. Hardest sub-skill: spatial relationships (occlusion, where curves terminate) — diff hints for these look unexplainable; see invariant 3.
  *Corrected 2026-09-14:* this reference has **no uniform black line art** — measured, only 12.6% of its
  pixels are below gray 95, and the figure's read comes from flat-colour boundaries plus compact dark
  regions. So XDoG extraction is a dead end here (P10 agrees: it turns anime interiors into noise).
  Structure comes from region decomposition and traced boundaries; a stroke is then drawn on the
  boundary that matters. See `05-portrait-scene/evidence/diagnosis/`.
- **T2 flat color** — SVG fills. Reference: k-means palette.
- **T3 soft fields** — gradients, blurred blobs inside clipped silhouettes, opacity, `mix-blend-mode`. Core idiom: *hard silhouette clip + blurred color blobs inside it* (painter's clipping-mask workflow — every layer stays nameable). Needed for image.jpg background/ribbons.
- **T4 photo realism** — stacked blurred-blob decomposition, feathered silhouettes, texture. Research tier; needs field-decomposition tooling (gradient direction/extent hints). Not scheduled.

## Curriculum (the ladder rungs)

`.scratch/08..13` — one rung teaches one thing; each closes with a `draw check` + fresh-eyes verdict,
clean resolver diagnostics, and no shape over 4 hand-typed coordinates.

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

## SVG/CSS style guide (explainability contract)

Applies to what the resolver *emits*; the authoring language is `abstraction.md`.

- viewBox matches reference pixel size; coordinates in reference space.
- `<g id="...">` per semantic part, painter order top-to-bottom in document.
- Every shape: `id` + adjacent comment stating intent ("hair pull-point convergence curve"), not appearance trivia.
- Forward-compatible names (`hairStrand3`, not `path_17`); no magic numbers where a formula reads better.
- CSS allowed for soft fields (layered gradients, blur, blend modes); SVG for structure. One source file per iteration — either `.svg` or `.html` wrapper.
- Blur never touches structure (silhouettes, outlines, face features). If a soft field cannot state why it is soft in one line, it is deleted (12-fields rule).

## Tool usage

- `check ART [--ref REF]` — **the whole visual feedback bundle in one command** (0.3s for a 1024² draft).
  Emits into `<exercise>/evidence/check/`: a whole-frame side-by-side (panes ≤600px), the 3 worst
  regions as 2x magnified REF|DRAFT crops (panes ≤256px, always exactly 3, grid-ranked and kept
  spatially apart), `report.txt`, and the metrics line. **It carries no verdict by design** — it
  refuses to tell you whether the drawing is good, because that judgment is the reviewer's.
  Omit `--ref` for the reference-free stage (bundle is just the drawing + an adjusted protocol).
- `compare REF SRC [--region x,y,w,h --zoom N]` — ad-hoc side-by-side, one attention pass. Detail
  comparison happens per region, never on the full frame.
- `diff` line mode: overlay of edge maps — **cyan = reference-only (missed line), magenta = mine-only (invented line), white = match**; numbered hint boxes on worst missing regions. Color mode: amplified color-distance heatmap + worst-region boxes; prints edge-F1 + mean color distance.
- `ref palette` — preprocessing; generate once per exercise, draw against these. (`ref lineart`/XDoG
  is available but **not** useful for this reference — see T1.)
- `log` — appends iteration row (metrics + note) to the exercise's `log.md`.

## Guardrails

- Metrics are progress signal only (invariant 4 in repo AGENTS.md). `check` prints them as a
  **breakage alarm**: a jump means something broke, a good number never means the drawing is good.
- Max ~3 focused fix attempts per problem; still failing → reformulate at design level (e.g. wrong occlusion order), propose once-and-for-all structure fix.
- **Never judge your own render.** Run `check`, then give `report.txt`'s image list — and nothing
  else — to a FRESH-context reviewer with the open question "what is wrong here?". No leaked intent,
  no history, no suspected verdict (a reviewer that knows what you were trying to do will confirm it).
- Critic findings are observations first and *locations* second: verify every spatial claim against a
  measurement or the crop's own coordinates before acting (P7). Reviewers reliably describe what they
  see and mislabel *where* they saw it; the `check` bundle names each region's coordinates so the two
  can be told apart.

## Judging (P14 reframe)

Primary criterion: the drawing looks like a proper artwork in the reference's style — judged by looking at the full render and by fresh-eyes critic review. Zone-distance/edge metrics are weak regression signals only (catch accidental breakage), never objectives to tune against. Holistic semantic shapes outrank pixel correspondence; a fragmented but "closer" draft is worse than a coherent drawing.
