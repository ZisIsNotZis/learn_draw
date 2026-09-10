# Drawing method — reference recreation via programmatic art

Loop: **observe → plan → draw → compare → reflect → revise**, cycled. Line art first, coloring second, soft fields last.

## The loop

1. **Observe**: describe the target semantically in words first — subject, pose, composition, palette, what each region *is*. Never start by writing paths.
2. **Plan**: shape inventory + draw order (painter's algorithm: background → body → clothes → hair → hat → face → details). The SVG layer structure mirrors this plan; that is what makes it explainable.
3. **Draw**: line art stage = strokes only, no fill, against `ref lineart` output. Big silhouette → medium structures → small details. Coloring stage = fills against `ref palette` swatches. Soft-field stage = gradients, blurred blobs, opacity, blend modes (see Tier ladder).
4. **Compare**: `compare` full-frame first; then `diff` (line or color mode) → pick 1–3 highest-value hint regions → `compare --region x,y,w,h --zoom 2` for detail passes.
5. **Reflect**: written note per iteration in `log.md` — what was wrong, what changed, why. Each reflection ends by asking: what is the *transferable* principle here? Distill into `docs/drawing/principles.md`.
6. **Revise**: edit the named paths, commit as `v<N>`, re-run diff. Git history = my learning curve; roll back when a "fix" makes it worse.

## Tier ladder

- **T1 line art** — SVG strokes, no fill. Reference: XDoG line extraction. Hardest sub-skill: spatial relationships (occlusion, where curves terminate) — diff hints for these look unexplainable; see invariant 3.
- **T2 flat color** — SVG fills. Reference: k-means palette.
- **T3 soft fields** — gradients, blurred blobs inside clipped silhouettes, opacity, `mix-blend-mode`. Core idiom: *hard silhouette clip + blurred color blobs inside it* (painter's clipping-mask workflow — every layer stays nameable). Needed for image.jpg background/ribbons.
- **T4 photo realism** — stacked blurred-blob decomposition, feathered silhouettes, texture. Research tier; needs field-decomposition tooling (gradient direction/extent hints). Not scheduled.

## SVG/CSS style guide (explainability contract)

- viewBox matches reference pixel size; coordinates in reference space.
- `<g id="...">` per semantic part, painter order top-to-bottom in document.
- Every shape: `id` + adjacent comment stating intent ("hair pull-point convergence curve"), not appearance trivia.
- Forward-compatible names (`hairStrand3`, not `path_17`); no magic numbers where a formula reads better.
- CSS allowed for soft fields (layered gradients, blur, blend modes); SVG for structure. One source file per iteration — either `.svg` or `.html` wrapper.

## Tool usage

- `compare REF SRC [--region x,y,w,h --zoom N]` — side-by-side, one attention pass. Detail comparison happens per region, never on the full frame.
- `diff` line mode: overlay of edge maps — **cyan = reference-only (missed line), magenta = mine-only (invented line), white = match**; numbered hint boxes on worst missing regions. Color mode: amplified color-distance heatmap + worst-region boxes; prints edge-F1 + mean color distance.
- `ref lineart` / `ref palette` — preprocessing; generate once per exercise, draw against these.
- `log` — appends iteration row (metrics + note) to the exercise's `log.md`.

## Guardrails

- Metrics are progress signal only (invariant 4 in repo AGENTS.md).
- Max ~3 focused fix attempts per problem; still failing → reformulate at design level (e.g. wrong occlusion order), propose once-and-for-all structure fix.
- Fresh-eyes critic (subagent given only REF vs DRAFT images, open question "what is wrong here?") at exercise end — catches blind spots from staring at my own draft.
