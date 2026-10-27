# 5_PRODUCT — what the author can express and the decisions behind it

This file owns *what a spec can say*: the north star of the relational language, why the language
exists, the three tiers, the two orders, the relation taxonomy, the forms and primitives a spec may
name, the teacher role and its withdrawal, how the language grows, the canons, the family catalog, the
rules for adding a family, the families-vs-relations boundary, and the design directions adopted or
rejected. It does not own the compiled node format or the traced-data field list (`7_INTERFACE.md`),
module algorithms and generators (`8_DETAIL.md`), commands and tool usage (`9_IMPLEMENTATION.md`), the
binding rules `P1`–`P41` (`3_REQUIREMENT.md`), or what good means (`2_GOAL.md`).

The language described here is the authoring layer of the current 2D relational front end, resolved by
`scripts/relate.py` — the single canonical resolver, forks deleted. The component/surface contract and
the intended spatial architecture are `6_ARCHITECTURE.md`: 2D artwork on 3D support surfaces with
engine-calculated depth visibility. Its component-local coordinates are not frame-placement
coordinates. Existing global layers and relations are migration inputs, not the answer for a ribbon
alternating between near and far depth. Some catalog statuses and early canons below are historical —
verify an implemented family against `scripts/relate.py` before relying on the catalog. Transferable
2D artwork attaches to a support surface rather than encoding visibility cuts.

# EXPLICIT

## North star — humans never talk or think in coordinates

**Humans never talk or think in coordinates.** "The brim is about twice the head wide, tilted a bit
down to the right, sitting on the hair" is a complete drawing instruction for a person — so it must be
a complete instruction here. Two consequences:

- **Litmus test for every addition:** if expressing an idea needs coordinates, the *abstraction* has
  failed — add the relation or the vocabulary, never the numbers.
- **Human-phraseable is the completeness bar.** Anything a drawing teacher would say in words and this
  language cannot say is a missing feature, and the wording of the missing feature is the feature
  spec.

## Scope decisions — what the reviewed artwork must express

**Both sleeves.** A includes two sleeves. The reading that the reference shows one sleeve is rejected:
the second sleeve is small and partially covered, not absent. "hand goes according to our original
plan is fine, but there are two sleeves, not one, the other one is not invisible, it's just small,
partially covered, but not fully." A keeps its existing no-hand-claim scope; both sleeves must be
present, with the second one's visible shape produced by depth occlusion rather than a hand-drawn cut.

**Hair is the curved design.** Hair uses the two-sided head-attached sheet, i.e. the S1 mechanism, not
the flat single-colour band. "Yes use the curve design. If you can implement blocking/covering
properly, that would be nice."

**B's hand is built at the detailed level** — palm + four fingers + thumb, contact geometry — because
the project's point is detailed and reasonable drawing. His reading of that sheet — the hold reads as holding in both SUPPORT and VARIATION, the CONTROL panel
unchanged — is `1_PROBLEM.md`'s; what it requires here is the detailed construction.

# INFERRED

## Why the language exists

The alternative channel is absolute coordinates, and it asks the author for the one thing it cannot
do. Measured in `.scratch/05-portrait-scene/evidence/diagnosis/`: 824 hand-typed vertices across 58 polygons
and **zero** uses of the computed `trace` node, while a computed region decomposition of the same
reference reaches the character in 2.4s and hand-authored iteration does not.

The reason is structural: a VLM is strong at naming, grouping, ordering and judging, and weak at
coordinate regression — and at 1024² its own coordinate errors are invisible to it.

**Hard constraint (P18):** the engine must never depend on the target image. A reference may *seed*
the values in a spec (the teacher role, below), but a solver that needs the target cannot serve the
end goal of drawing without one. Test for any addition: *does this still work with the image deleted?*

Coordinates are never typed; they are what the resolver prints when it is done. The loop that
consumes a spec — resolve, render, judge — is `4_USECASE.md`, and its commands are
`9_IMPLEMENTATION.md`.

## Two classes of literal

Literal numbers are not forbidden, but they split by what they do:

- **Proportion / style constants** — `2.70`, `tilt: -14`, `0.30` — are allowed, but live in `vars:`
  with a one-line provenance comment (where the number came from: measured, a canon, or a taste
  choice). Unprovenanced magic numbers are the old failure in a fraction costume.
- **Placement numbers** — anything that positions a shape — must be *derived from other anchors*. Raw
  `frame.w*0.60` placement is an eyeballed absolute in disguise; the human phrase is "slightly right
  of centre, upper third", and the resolver should warn when placement does not reference another
  shape (pending).

## Three tiers

Ask for the picture the way you would describe it to a person: name the objects, give proportions,
state what overlaps what. The engine resolves everything numeric.

| tier | what it carries | example |
| --- | --- | --- |
| 1. anchors | the canvas frame, and every shape's handles | `frame.w`, `head.rx`, `brim.left`, `{along: head, t: 0.25}` |
| 2. relations | positions and sizes expressed *relative to other things* | `{along: brim, t: 0.62}`, `2.70*head.w`, `{between: [A, B, 0.35]}` |
| 3. vocabulary | parametric object families with drawing-sane structure | `{sunhat: hat, host: head, brim: 2.70*head.w, tilt: -14, pom: 2}` |

Relations alone are not enough: they can place a shape but not invent one. Tier 3 is where drawing
knowledge lives — a wide-brim hat *is* a squashed brim ellipse, a dome on the brim's own normal, and a
near edge painted over the crown. The model says "wide-brim sun hat, tilted 14°", not twelve
coordinates. Tier 3 is also what makes a starry-night-complexity scene tractable.

## Two orders, kept separate (P20)

- **Resolution order** — a node may reference any shape declared *above* it. Put the ruler first.
- **Paint order** — `layers` bottom→top, then declaration order within a layer (`z:`).

These are different orders on purpose. The head is declared first (everything is sized in units of it)
but painted *under* the hair. Keeping them apart is what removes the manual occlusion surgery that
absolute-coordinate authoring demands: occlusion is the renderer's job, never encoded in a path.

## Relation taxonomy

A `📋` status names the retired 2D milestone or exercise the relation was planned for — `0_ROADMAP.md`'s
naming note has a paragraph for those retired letters; it is a plan, not a promise, and the relation is not
implemented until `scripts/relate.py` resolves it.

Implemented vs needed. The needed rows are not speculation — each names the drawing that demands it.

| relation | status | meaning |
| --- | --- | --- |
| arithmetic over anchors (`1.8*head.rx`) | ✅ | sizes and positions in units of other things |
| `{at: SHAPE}` | ✅ | a shape's centre |
| `{along: SHAPE, t, out?}` | ✅ | point on an outline at parameter t, optional outward push |
| `{between: [A, B, t]}` | ✅ | interpolation / extrapolation along a segment |
| `{polar: P, angle, d}` | ✅ | polar offset (`off` is a YAML boolean word — SA3 finding 6) |
| `vars:` | ✅ | named intermediate scalars |
| `mirror` | ✅ (SA2, promoted) | reflect across an axis or a shape's centre line — eyes, poms |
| `inside` / containment | ❌ not needed | **resolved by encapsulation** (families vs relations, below): iris-in-sclera and glint-in-iris are intra-family arithmetic, not a cross-object relation |
| `align` | 📋 M2 | two shapes share an edge line or axis (eye line, mouth centre) |
| `distribute` / jitter-grid | 📋 10, SA3 | n instances along a curve with seeded spacing jitter (pleats, village) |
| `junction` | 📋 08 | where two outlines cross — P4 says these carry the character |
| `contact` / tangent | 📋 09 | a strand touches the jaw here; hand rests on hip |
| `flow` | 📋 SA3 | a spine following a direction field (hair, water, swirls) |
| `negative-space` | 📋 later | describe the gap, not the shape (P4) |

## Forms

Values are numbers, arithmetic, or a relation dict. Strings may reference anchors: `"1.8*head.rx + 4"`.

| form | meaning |
| --- | --- |
| `[x, y]` | point; each component is a number or expression |
| `{at: SHAPE}` | that shape's centre |
| `{along: SHAPE, t: 0.35}` | point on SHAPE's outline at `t` (wraps; works on rotated ellipses) |
| `{along: SHAPE, t: 0.1, out: D}` | same, pushed `D` outward along the outline normal |
| `{between: [A, B, t]}` | point `t` of the way from A to B; `t` outside 0..1 extrapolates |
| `{polar: P, angle: 90, d: 40}` | point at angle/distance from P (0° = right, 90° = down) |
| `vars:` | named intermediate scalars, evaluated once, referenced by bare name |

**YAML caveat:** `on`, `off`, `yes`, `no` parse as booleans, so this language uses `along` for outline
points, `host` for an object family's attachment, and `polar` for angle/distance offsets. `relate.py`
rejects boolean keys by name rather than failing cryptically.

## The primitives a spec may name

Everything else is a vocabulary node or a relation. Each takes `z:`, `desc:`, `fill:`, `stroke:`, `sw:`.

| shape | keys | is |
| --- | --- | --- |
| `ellipse` | `at`, `rx`, `ry`, `rot?` | an ellipse |
| `stroke` | `spine`, `w`, `ink` | an open stroke along a spine |
| `rect` | `full: true` or `at`, `w`, `h` | a rectangle / the backdrop |
| `blob` | **either** `poly` (closed polygon, fill-only) **or** `spine` (+ `w`, a tapered ribbon) | a closed filled shape |
| `region` | `seed`, `tol`, `box?`, `fixed?`, `eps?` | **teacher-only**: floods the reference raster *at render time*. Refuses to resolve without `--ref`. Use it to produce `traced` data, never as the artifact |
| `traced` | `from` (a path to frozen vertices), `fill`, `z` | a closed shape whose vertices were **computed once** by a `region` and frozen to disk. Opens no raster |

`blob`'s two forms are both first-class: a closed silhouette (blouse, skirt panel, brim slice) has no
spine, and a ribbon (hair mass, cloth fold) has no polygon. They compile to the same node type
(`7_INTERFACE.md`), so authoring in the wrong one silently looks like a dialect error — say which you
mean.

## The teacher measurement is materialized, never read live

A live `region` node breaks P18 — the spec would not render with `image.jpg` deleted. So the teacher
step is a **materialization**: the computed outlines are frozen into a sidecar once, and the spec's
`region` nodes are rewritten as `traced` nodes that point at that data. The spec then renders with the
image deleted.

The sidecar's fields, the staleness rule that makes a changed reference loud, and why the data is a
sidecar and not inline vertices are `7_INTERFACE.md`'s; the command that writes it is
`9_IMPLEMENTATION.md`'s.

A frozen contour is **not** a canon. A canon is proportion knowledge as a fraction of a host measure —
knowledge that transfers to a new subject. A traced outline transfers to nothing: it is one specific
shape and says nothing about how to draw the next head. A spec made mostly of `traced` nodes is
admissible and reproducible, yet carries little transferable learning, and it is exactly that share the
withdrawal phase must re-invent. Use the trace as ground truth to FIT the families to (brim outline →
`sunhat` parameters, hair silhouette → `hair-mass`, skin → `face`), then discard the trace. The honesty
hinge: **fit to the teacher's measurement, never to the evaluation metric** — fitting `sunhat` to a
traced outline is parameter extraction; nudging `brim` until `edge_f1` rises is the optimizer
regression invariant 4 forbids. The debt instrument is `work/measure-trace-debt.py`.

## The teacher role, and why it can be withdrawn

A reference is used in exactly two supported ways, both removable:

1. **Seeding values** — measure the reference (`measure`, boundary tracer, region decomposition) to
   fill in the numbers in a spec, then close the image. The spec, not the image, is the drawing.
2. **Setting the frame** — the canvas size and where the subject sits in it.

Tracing is never the engine. The curriculum depends on this: reproduce with the reference, then
reproduce the *same* subject from its own spec with the image closed, then a new subject from intent
alone. The ladder runs this withdrawal explicitly — rungs 08–13 draw with the reference available, and
the follow-on after 13 redraws the assembled figure from its own spec with the image closed.

## Canons — proportion knowledge, in fractions

Canons are the "how to draw" facts a human teacher states in words: *eyes halfway down the head, one
eye-width apart*. They are stored as **fractions of a named host measure** (head height, head width),
never pixels — which is what makes them transferable to any subject and any canvas.

**Teacher loop (P18 made concrete):** the reference phase measures a subject and produces canon values;
the image then closes. A scene file is a *parameter vector in canon space*, not a geometry dump —
drawing without a reference means re-instantiating canons for a new subject, which is exactly what the
solo phase needs. A canon is what makes the object expressible as structure rather than as pixels —
the object, not the pixels (P14).

Canons are stated **relative to the host shape's anchors** — the units a spec actually uses
(`head.cx`, `head.ry`, …).

### Anime face canons — Set A, art-canonical

Head bbox: skull top → chin, H≈228; eye-line width W≈190. Sources: face-centre pixel scan x=690
(hair→skin y≈243, skin→collar y≈377, skull top ≈150) plus `02-portrait-face` traced geometry.

| canon | value | note |
| --- | --- | --- |
| eye-centre height | 0.54 · head H | the classic "eyes halfway down" holds in anime too |
| eye spacing (centre→centre) | ≈ 0.50 · head W | ≈ 2–2.7 eye widths — wider-set than realistic |
| nose y | 0.73 · head H | anime noses sit high and are a tick, not a shape |
| mouth y | 0.85–0.89 · head H | a short dash |
| hairline | 0.41 · head H | bangs cover the forehead; hairline ≠ skull top |
| head H : W | ≈ 1.2 | taller than wide |

### Anime face canons — Set B, host-relative (what a spec writes)

Source: SA2 face probe, image closed afterwards (`.scratch/14-abstraction-research/work/face/report.md`).
Near/far asymmetry is the 3/4 view — the far eye is 0.6× the near eye.

The host must be named with the fraction: these fractions are measured against a **face ellipse**
(hairline y≈243 → chin y378; cy 310.5, ry 67.5), **not** the head ellipse (skull top y150 → chin
y378; cy 264, ry 114) that the assembly uses as its ruler. Applied to the skull→chin host,
`head.cy − 0.58·head.ry` puts the eye line at **y198**, but the reference's eyes are at **y262–268** —
70px too high. Two different hosts, one set of numbers: the fractions are only portable if the host is
named with them. The
assembly's own values are measured directly from the reference and recorded in the spec's `vars:` with
provenance; treat this table as the *shape* of the canons, not as ready-to-use numbers for an arbitrary
host.

| canon | value (host = head ellipse) |
| --- | --- |
| eye centre x | head.cx ± 0.73 · head.rx |
| eye centre y | head.cy − 0.58 · head.ry |
| eye width | 0.55 · head.w (near), 0.33 (far) |
| eye height | 0.33 · head.h |
| iris | 0.44 · eye width; darker top ~50%; fills aperture |
| inner-corner gap | 0.44 · one eye width |
| brow | ≈ 0.2 · eye height above the lash, slants down toward nose |
| nose tick | head.cy + 0.05 · head.ry (slanted 2–3px dash) |
| mouth | head.cy + 0.52 · head.ry (soft 10px dash) |
| lash | 0.16–0.19 · eye height, thickest at outer half, wing past corner |
| glints | track the WORLD side of the light, not the eye's inner side |

**Ladder rule:** each vocabulary family's canon values are measured from the reference first (that is
the teacher phase), then live here as fractions. Generic art canons (Loomis-style) are a fallback when
no reference exists — not the primary source.

## Family catalog

Status: ✅ implemented · 🔨 in progress · 📋 needed (with the rung that demands it) · 🔬 proven in a
probe copy, awaiting promotion. This table is the catalog of families; a relation's status row in the
taxonomy above points here, and the two statuses must agree.

| family | status | params (beyond placement) | anchors exposed | carries |
| --- | --- | --- | --- | --- |
| `face` | ✅ (M2) | host, at, rx, ry, cheek (jaw half-width / rx at the cheek line), jaw (cheek line as a fraction of ry below cy), chin-w (chin half-width / rx), turn (deg) | all the ellipse handles (`cx/cy/rx/ry/w/h/left/right/top/bottom`) + `chinx/chiny`, `cheek-y`, `jaw.left/right` | cranium ball + jaw wedge; the jaw profile is taken from the measured taper (half-width 64 → 56 → 49 → 47 → 27 → 3.5 px) so the chin is a point, not an ellipse's round bottom. **The cranium stops just past the cheek line** — a full-height cranium hides the jaw inside it and renders a round blob (the M2 gate's finding) |
| `sunhat` | ✅ | brim, crown, tilt, lift, drop, flat, front arc, **rim** (fold-over depth, 0.45), pom count/at/r | `hat-brim.left/right/top/bottom`, `hat-brim@t`, `hat-dome.*`, `hat.*` (family id = brim footprint) | brim-as-squashed-ellipse, dome on brim normal, far edge folding over the top surface (`rim`; a straight chord across the disc is rejected — it meets only at the tips and the brim reads as a detached lozenge), near edge over crown. P17 z-split: the brim is ONE shape as two complementary slices (far → dome → near), so the dome sits behind the near brim, not a full ellipse plus a thin rim strip |
| `eye` | ✅ (SA2) | host, at (any relation), w, h, tilt, almond, mirror-of, glints, iris-w/h (auto-clamped to aperture), lash-w, line-w, glint-side (world light!), gaze, refl-fill, *-fill, z | aperture bbox, outerx/outery, innerx/innery, irisx/irisy, topx/topy, botx/boty, facing, `{along: eye, t}` | generated almond aperture (two lid arcs), two-tone iris, pupil, glints + green reflection, ONE-SIDED tapered lash anchored on the lid line with outer wing, sealing outline; `mirror-of` = whole second eye as one relation |
| `mirror` relation | ✅ (SA2) | `{mirror: P, across: SHAPE}` reflects a point across a shape's vertical axis; `mirror-of` is the family-level mirror | | |
| `brow`, `nose`, `mouth` | 📋 M2 (mine, as plain strokes) | length, angle, weight | ends, centre | mark-not-shape (P12) |
| `hair-mass` | 📋 08 | silhouette spine, width, tip zigzag, strand count | hairline, tips@t | one silhouette with zigzag bottom (P8), pink pockets as skin-through-notch |
| `sleeve`, `bow`, `collar` | 📋 09 | puff, gather count, knot size | knot, tails@t | cloth fold direction |
| `hand` | 📋 09 | pose preset, finger spread | knuckles@t, fingertips | z-plane tuck behind body (P17) |
| `pleats` | 📋 10 | count, depth, taper, seed | hem@t | fan from waist, alternating dark/light |
| `swirl` | 🔬 SA3 probe | centre, radii, turns, width, taper | start, end, @t | flow-field ribbon (Starry-Night sky) |
| `glow` | 🔬 SA3 probe | core r, halo r, rays, hue | centre, ray tips@t | radial gradient + rays |
| `flame-tree` | 🔬 SA3 probe | height, sway, lobe count | trunk base, tip | stacked flame lobes |
| `village`, `hill` | 🔬 SA3 probe | count, spacing curve, jitter seed | row@t | repetition with jitter |
| `flow` | 🔬 SA3 probe | region, dir, curv, waves, width | region bbox | broad ribbons following a direction field (sky wind, water, hair) |
| `stars` | 🔬 SA3 probe | region, n, size jitter, seed | region bbox | seeded scatter — jitter-grid made concrete |

The 🔬 families are proven in the SA3 starry-night probe copies at
`.scratch/14-abstraction-research/work/starry/`, not yet promoted to `scripts/`, reference-free from a
parameter-only spec and byte-deterministic. Two structural findings from `work/starry/report.md`:
back-end generators need a spec-level **generator bridge** — today each needs a hand-written
passthrough family in the resolver; and the three relations under the families — `flow`,
`distribute-along`, `jitter-grid` — should be promoted to first-class relation forms so they are
reusable beyond one family each.

`P17` in this catalog names the z-plane split the flat renderer requires, not a prescription for the
spatial model — that prescription is `P29` (`6_ARCHITECTURE.md`).

## Rules for adding a family

1. **Demanded by a drawing, not by foresight.** A family is added when a rung of the ladder fails
   without it — the ticket names the rung. No speculative families (the 05 lesson).
2. **Structure knowledge goes in the engine.** Layer order, sane proportions, and silhouette logic
   belong in the family, so the model states intent ("wide brim, tilted") instead of geometry.
3. **Anchors are part of the contract.** Every family exposes named handles other nodes can reference;
   an anchor that a later drawing will need but the family does not expose is a defect.
4. **Canons are fractions of a host measure**, with provenance (measured from which reference, or
   which art canon). No pixel values in this file.
5. **Deterministic and seeded.** Same spec → same pixels, byte-identical.
6. **The family gets an entry here the moment it lands**, with its parameter list — docs first, per
   SSOT.

A family is added only when a drawing fails without it; `sunhat` and `eye` are implemented, the rest
carry the milestone that demands them.

## Encapsulation boundary: families vs relations

Intra-family layout — iris inside sclera, glint inside iris, dome on brim normal — is **arithmetic on
the family's own anchors**, encapsulated so the spec never sees it. Relations are for **cross-object
composition**: placement, spacing, alignment, junctions, occlusion intent. Consequence for the
taxonomy: a proposed relation should first be asked "is this really intra-family? Should it be a
parameter instead?" — `inside`, for instance, mostly disappears once a family owns its parts; `mirror`
survives because faces pair two *instances* of a family.

## Measured targets, where a proportion was the whole argument

Scope decisions above are requirements; where one of them turns on a proportion, the number is the
requirement and not an impression:

- **Second cuff from depth:** its visible area reaches **10–25 %** of the first cuff's — the reference
  measures **17 %**, and the accepted `A-cloth-v8` reached **16.4 %**.
- **Enclosed background islands: zero.** An island of background colour enclosed by the garment is a
  hole in the cloth; `A-cloth-v8` reduced them from two to zero.

## What a construction must connect

Declared separation is not visual connection, and the language has to be able to say the difference.

- A build can give every part its own `Component`, support frame, local (u,v) and `intent` — collar
  left/right, bodice, waist band, sleeve, cuff, gather, two loops, two tails, local pink band,
  anonymous blue band, two hair bands — and still read as disconnected pieces: every part is built
  inside one `build_scene()` sharing one parameter file, and `attachment` stores three name strings
  with no geometric requirement.
- The bow reads as detached by construction, with numbers: `gather_patch` is a 12×15 px quad; the two
  `folded_loop` lobes are separate solids; `tension_tail` starts at `G + (-4,+5)` with half-width
  8.4 px, i.e. a 16.8 px band **wider than the 12 px knot** and offset from it, so its root edge is a
  straight cut beside the knot instead of an emergence from it. The physical object is one ribbon
  visiting knot → lobe → knot → lobe → knot → tails; the reference's lobes are solid cloth with
  visible crease/fold lines and the tails emerge from the knot.
- A flat polyline extrusion with one fill — no curvature across the width, no twist, no two-sided
  paint — is a mechanism regression against the head-attached curved sheet whose normal twists and
  whose fill is chosen by projected face orientation. This is the regression behind the curved-design
  decision recorded above.
- A second sleeve can exist and be occluded: in the registered crop the second cuff survives only as a
  dark wedge and a white sleeve sliver behind a bow tail. That is exactly the case the depth engine
  exists for — the component is authored whole and depth decides its surviving visible shape.

These are recorded in `issues/54-user-review-scope-hair-and-hand.md`.

## Design directions (adopted or noted — demand first)

- **Declarative families (ADOPTED — SA1 finding 10).** A family should be a YAML block — parameters
  plus sub-shapes whose relations may only use the family's own anchors — so the *model* can author a
  family without writing Python. Generator families (swirl, glow, …) delegate to the renderer. Canon
  rows become loadable data with provenance. `sunhat` is the migration example. This is the
  highest-leverage change in the design; it also makes "learning is the repo" literally true
  (knowledge becomes readable spec, not Python).
- **Style as a preset layer.** Anime-cel = hard outlines + flat fills + defined stroke weight; a
  future "impasto" style would change stroke/blur/palette defaults globally. Direction: a `style:`
  header that adjusts engine defaults, so the model picks a look instead of restating it per node.
- **`pair` wrapper.** Mirror an instance (eyes, poms) with per-side tweaks for 3/4 view — the relation
  survives, the wrapper makes it ergonomic.
- **The `head` family follows Loomis ball-and-plane construction** (validated pattern from art
  pedagogy): head = sphere + jaw block; a **cross** (mid-line + eye line) encodes pose; features
  attach to the cross by canon fractions. Mapping onto this system: the cross lines become exported
  anchors (`head.mid-line`, `head.eye-line`, `head.brow-line`, `head.chin-plane`), pose =
  rotating/offsetting the cross, features = `{along: head.eye-line, t}` + canon fractions. This is the
  model for how a family *constructs* rather than outlines.
- **Teacher vocabulary maps to artist vocabulary**: gesture ≈ `flow` relation, massing ≈ mass blobs
  before details, negative space ≈ P4 junctions, sight-size ≈ our `measure` step. When a human
  teaching term has no mechanical equivalent yet, that is a missing relation or family.

## How the language grows

One rule: **a new relation or vocabulary node is added only when a real drawing failed without it.**
No speculative generality. The renderer's `blur`/T3 machinery is the counter-example — built for
soft-field realism, then pointed at flat cel art, it produced mush.

Second rule (see `.scratch/14-abstraction-research/spec.md` → Verdict): **a language change is only progress if
the artifact does not regress.** Compare the new render against the recorded best — the
`baseline`/`check` delta prints it, commands in `9_IMPLEMENTATION.md` — because a growing language and
a shrinking drawing is exactly how a bust gets committed as a final image. Direction and gates:
`0_ROADMAP.md`.

## Learning is the repo

The model's drawing knowledge is **this file + the principles `P1`–`P41` (`3_REQUIREMENT.md`) +
measured canons**, all committed. Each rung of the ladder appends a family entry, a canon row with
provenance, and a principle. Nothing needs to survive in model memory or weights — the repository is
the learned drawing knowledge, which is why docs-first is a hard rule and not a nicety.

## Open questions

- Does `along`-at-`t` need a companion for "where this outline crosses that one" (junction points,
  which P4 says carry the character)? Only if a drawing demands it.
- Sizes are currently uniform (`w:`). Wrapping elements need taper; `scene_render` already has width
  profiles — reach for them when a ribbon or strand actually needs one.

## Curriculum coverage — the vendor methods, their evidence and their disposition

This is the one inventory of methods assessed from the local vendored `huashu-art-motion` and
`huashu-design` trees, their migration relevance, evidence and disposition. `huashu-art-motion` is the
primary art/motion exemplar; `huashu-design` is supplementary and does not create a UI/product-design
learning track. Naming a source is not evidence of learning it: a disposition changes only against an
inspectable project artifact at a named revision. Vendor content is never presumed correct.

| Method family and source | Migration/use | Evidence and disposition |
|---|---|---|
| Semantic rig/pose separate from style renderer; anchors, IK, taper (`references/04-纯代码绘制.md`; `scripts/engine/lib/rig.js`: `R.ik2`, `R.taper`, `G.A`, `GIRL_ORDER`) | Adapt semantic joints/attachment and generated shape to local spatial support/depth; separate pose from 2D appearance. | Not yet demonstrated in the project. Ex32 rotated existing arm/hand geometry; it implements none of these rig methods. Candidate for R1. |
| Component slots, renderer hooks, semantic line responsibility (`rig.js`: `drawGirl`, `visibleLines`, hooks) | Learn part ownership and deliberate line selection; compare with semantic depth boundaries. | Source identified, migration not demonstrated. Vendor flat painter order is not project depth visibility. Candidate once structure is readable. |
| Real instances before generalizing; awkward cases and retained failures (`references/07-正面经验.md` §§23–25) | Build a concrete construction and a second distinct use before a shared abstraction. | The exercise process references the method; it does not establish an accepted visual migration. Applies across milestones; preserve the control and the failure. |
| Visual grammar, focal hierarchy, motif and scene organization (`references/02-机制.md` §§1–3; `07-正面经验.md` §§1,5,31) | Use visual focus, silhouette and shape rhythm to improve composition; compare the intended variation. | Cited only; no accepted visual migration evidence. Assess as part of reference imitation and original composition. |
| Regional palette, material/process renderer, static/dynamic separation (`04-纯代码绘制.md`; `07-正面经验.md` §§6–10,19; `lib/paint.js`) | After structural acceptance, map semantic regions to explainable material treatment and coherent colour. | Deferred until the structure reads; not learned. Assess in R3 when useful, as a method, not a mandatory technology. |
| Time functions, continuous response and pose transition (`scripts/engine/lib/motion.js`: `MO.seg/anim/step/spring/settle/float/lagged`; `02` §2; `07` §§3,12–14) | Use a few poses and responses to expose attachment, contact and shape construction; animation is a validation method where useful. | Not demonstrated in the project; Ex32 is a fixed transform. Do not expand into video/beat/audio production. Candidate for R2. |
| Independent review and hostile/unseen examples (`07` §16,23–25) | Separate artifact and source correctness from actual visual reading and held-out transfer. | The project uses review concepts; earlier experience claims with undocumented sight qualification stay informal. Follow the actual-modality gates. |
| Dense hand-coded reference contours and coordinates | Could reproduce detail, but conflicts with compact, explainable procedural construction. | Excluded as an endpoint; the reference teaches semantic parameters, not runtime geometry. |
| Native generated images, generated characters/sprites/video (`SKILL.md`; `03-一帧先行四条路线.md`; vendor README) | Not compatible with a text/code-authored output boundary. | Excluded; no generator or vendor service is invoked. |
| Painter-order line extraction; finished-film QA | Some review ideas may transfer, but flat global painter ordering cannot establish depth-derived visibility or physical non-intersection. | Do not import the algorithm as spatial visibility or as evidence. Take only a specific review principle, and only against a project gate. |
| Beat-grid, audio and whole-video pipeline; production delivery | Relevant only if a future goal explicitly requires film production. | Outside the drawing goal; not a general exclusion of useful motion and pose construction. |
| Supplementary `huashu-design` visual-brief and critique ideas (`vendor/huashu-design/SKILL.md`, `README.md`; selected references and demos) | Consider a specific visual-composition or critique method only when it serves a drawing workpackage; do not import UI/product deliverable process as a learning track. | Secondary to `huashu-art-motion`. The coverage ticket sampled skill/overview material and enumerated demos, not complete source families; no local migration or learning is demonstrated. No skill, generator or service is invoked. |
| Other scenes and recipes in either vendored tree | May contain further useful methods. | Not yet comprehensively read or classified. At a relevant workpackage, inspect the source families and classify each as useful / adapted / not applicable / excluded, with evidence. This table claims no completeness. |

**Use protocol.** For each selected method, record the source location, the concrete drawing question,
the local prior-art baseline, the rule adapted, the output artifact, the changed condition, the causal
contrast or failure, and what is not transferred. A teaching card or a test supports but never
substitutes for the visible artwork; method acceptance is never inferred from vendor QA or from reading
the source. A disposition changes only against inspectable project evidence and a final artifact
revision.

## Proposed, not adopted — the per-object part library and the seam contract

A direction was put forward and has not been executed or decided: a per-object part library, a seam
contract the compiler checks at every declared joint, the bow rebuilt as one continuous ribbon, the
hair as one two-sided curved sheet, both sleeves with the second one's surviving shape coming from
depth visibility, hand primitives for B, and object cohesion as an acceptance dimension of its own.
It is recorded here as a considered and undecided branch rather than filed as a decision; the object
cohesion dimension it proposes is already one of the four acceptance questions (`2_GOAL.md`), and
whether the rest becomes scope is `0_ROADMAP.md`'s question. Source:
`.scratch/35-r1-articulated-study/issues/54-user-review-scope-hair-and-hand.md`.
