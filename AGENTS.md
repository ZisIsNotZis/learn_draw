# learn_draw — rule overrides and the few things that must be known immediately

Learn to draw by authoring programmatic art: SVG/CSS built from computed relations and depth, never
diffusion or pixel generation — first by recreating the reference `image.jpg` (an anime-style
portrait), later with the reference closed, and at the end from intent alone. The drawing *skill* is
the deliverable; a picture is how it is judged.

Everything below is a rule that overrides habit, or a fact a newcomer must have before touching the
repo. Everything else lives in `docs/`, one home per meaning, and is reached from this list.

| if you need | read |
| --- | --- |
| why the work matters, what the person asked for | `docs/1_PROBLEM.md` |
| what success means, the acceptance questions, the rubric | `docs/2_GOAL.md` |
| the binding rules — `P1`–`P40` | `docs/3_REQUIREMENT.md` |
| who does what: the loop, the review protocol, the person's gate | `docs/4_USECASE.md` |
| what can be expressed: the authoring language, vocabulary, canons, adopted and rejected directions | `docs/5_PRODUCT.md` |
| subsystem boundaries, support surfaces, the depth-visibility principle | `docs/6_ARCHITECTURE.md` |
| the compiled node format, traced data, the renderer contract | `docs/7_INTERFACE.md` |
| module algorithms: resolution, clipping, generators, coordinates | `docs/8_DETAIL.md` |
| commands, gates to run, environment, where the records live | `docs/9_IMPLEMENTATION.md` |
| milestones, gates, the current advance and the next entry | `docs/0_ROADMAP.md` |
| a fact worth keeping that has no home yet | `docs/0_STAGING.md` |

## Invariant rules

1. **Semantic layer only.** Every path and layer gets a name and an intent comment. Every edit is
   justified by a statement about the drawing ("the brim ellipse is too flat"), never by "moved a point
   to lower a metric". Chasing pixel metrics is optimizer regression and is forbidden.
2. **Structure, line art and colouring are separate concerns.** Establish component identity,
   attachment and depth-based visibility first; then design and review line art separately from
   colouring; soft fields come last. A projected mesh edge is not automatically an art line.
3. **A weird hint means upstream error.** If a diff hint points at something the mental model cannot
   explain, the earlier drawing is structurally wrong — investigate backward, do not patch forward.
4. **Metrics are signal, never target.** Log edge-F1 and colour distance per iteration; never tune
   against them. `check` prints them as a breakage alarm only.
5. **Geometry is computed, never eyeballed** (`P19`). No shape carries more than about four hand-typed
   coordinates; anything larger comes from a relation, a vocabulary node, `trace`/`region`, or a
   generator. The authoring language is `docs/5_PRODUCT.md`; the spatial component model is
   `docs/6_ARCHITECTURE.md`. Absolute frame coordinates are compiler output, never an authoring target.
6. **The engine never sees the target** (`P18`). A reference may seed the values in a spec, and then it
   is closed: every addition is tested with the image deleted. Tracing is a teacher, never the engine.
   For spatial work, never hand-specify visibility cuts — component depth decides occlusion.
7. **Never judge your own render.** Run `draw check`, then give `report.txt`'s image list — and nothing
   else — to a fresh-context reviewer, asking "what is wrong here?". Verify a reviewer's spatial claims
   against the bundle's region coordinates (`P7`: observations are reliable, locations are not).
8. **Never regress the recorded best.** `check` prints `vs recorded best:`; structural sketches are not
   comparable finished drawings and must not replace the baseline. "Final", "readable" and "done"
   require the applicable gate in `docs/0_ROADMAP.md`. Promote a new best only through
   `scripts/draw baseline`, and only after a passed whole-drawing gate.

## Facts that must not be re-derived

- **The person judges the picture.** No metric, self-review or agent verdict substitutes for his; a
  picture its own review rejected is not put in front of him.
- **A milestone is an artwork**, never an engine, a test suite or a document.
- **A record is not a fact document.** `.scratch/`, `inbox/`, `mail/` and `teaching/` hold records, which
  keep their dates and their dead links. State and decisions live in `docs/`. See `.scratch/README.md`.
- **`mail/` is read before any other work in a session.** Reading a message means landing it — the fact
  into the document that owns it, the order carried out — then deleting the file.
- **`vendor/` is third-party** and is never edited; `image.jpg` and the plates cropped from it are study
  material outside the AGPL grant (`README.md`).
- **Push an atomic unit when it is finished**, and leave nothing running and nothing uncommitted at a
  stop (`docs/9_IMPLEMENTATION.md`).
