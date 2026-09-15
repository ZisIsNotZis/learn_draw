# Vocabulary — object families and canons

Where drawing knowledge lives. `abstraction.md` defines the language (anchors / relations /
vocabulary); this file catalogs the families, the proportion knowledge (**canons**) they carry, and
the rules for adding one. The resolver `scripts/relate.py` implements
them; `scene-format.md` is what they compile to.

## Why vocabulary is the important tier

Relations can place a shape; only vocabulary can *invent* one. A model told "sunhat, brim 2.7
head-widths, tilt −14°" gets a coherent hat because the engine already knows a hat's structure. That
knowledge is what the model cannot re-derive per drawing and must not re-type — it is the difference
between describing and drafting.

## Canons — proportion knowledge, in fractions

Canons are the "how to draw" facts a human teacher states in words: *eyes halfway down the head, one
eye-width apart*. They are stored as **fractions of a named host measure** (head height, head width),
never pixels — which is what makes them transferable to any subject and any canvas.

**Teacher loop (P18 made concrete):** the reference phase measures a subject and produces canon
values; the image then closes. A scene file is a *parameter vector in canon space*, not a geometry
dump — drawing without a reference means re-instantiating canons for a new subject, which is exactly
what the solo phase needs.

### Anime face canons (measured, image.jpg)

Canons are stated **relative to the host shape's anchors** — the units a spec actually uses
(`head.cx`, `head.ry`, …). Two provenance sets; the second is the one the resolver consumes.

**Set A — art-canonical (head bbox: skull top → chin, H≈228; eye-line width W≈190).** Sources:
face-centre pixel scan x=690 (hair→skin y≈243, skin→collar y≈377, skull top ≈150) +
`02-portrait-face` traced geometry.

| canon | value | note |
| --- | --- | --- |
| eye-centre height | 0.54 · head H | the classic "eyes halfway down" holds in anime too |
| eye spacing (centre→centre) | ≈ 0.50 · head W | ≈ 2–2.7 eye widths — wider-set than realistic |
| nose y | 0.73 · head H | anime noses sit high and are a tick, not a shape |
| mouth y | 0.85–0.89 · head H | a short dash |
| hairline | 0.41 · head H | bangs cover the forehead; hairline ≠ skull top |
| head H : W | ≈ 1.2 | taller than wide |

**Set B — host-relative (what a spec writes).** Source: SA2 face probe, 10 iterations, image closed
afterwards (`14-abstraction-research/work/face/report.md`). Near/far asymmetry is the 3/4 view —
the far eye is 0.6× the near eye.

> **Host corrected 2026-09-15 (see `STATUS.md` D13):** these fractions were measured against a **face
> ellipse** (hairline y≈243 → chin y378; cy 310.5, ry 67.5), **not** the head ellipse (skull top y150 →
> chin y378; cy 264, ry 114) that the assembly uses as its ruler. Applied to the skull→chin host,
> `head.cy − 0.58·head.ry` puts the eye line at **y198**, but the reference's eyes are at **y262–268** —
> 70px too high. Two different hosts, one set of numbers: the fractions are only portable if the host
> is named with them. The assembly's own values are measured directly from the reference and recorded
> in the spec's `vars:` with provenance; treat this table as the *shape* of the canons, not as
> ready-to-use numbers for an arbitrary host.

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

Ladder rule: each vocabulary family's canon values get **measured from the reference first** (that is
the teacher phase), then live here as fractions. Generic art canons (Loomis-style) are a fallback
when no reference exists — not the primary source.

## Family catalog

Status: ✅ implemented · 🔨 in progress · 📋 needed (with the rung that demands it) · 🔬 proven in a probe copy, awaiting promotion

| family | status | params (beyond placement) | anchors exposed | carries |
| --- | --- | --- | --- | --- |
| `face` | ✅ (M2, 2026-09-15) | host, at, rx, ry, cheek (jaw half-width / rx at the cheek line), jaw (cheek line as a fraction of ry below cy), chin-w (chin half-width / rx), turn (deg) | all the ellipse handles (`cx/cy/rx/ry/w/h/left/right/top/bottom`) + `chinx/chiny`, `cheek-y`, `jaw.left/right` | cranium ball + jaw wedge; the jaw profile is taken from the measured taper (half-width 64 → 56 → 49 → 47 → 27 → 3.5 px) so the chin is a point, not an ellipse's round bottom. **The cranium stops just past the cheek line** — a full-height cranium hides the jaw inside it and renders a round blob (the bug the M2 gate caught) |
| `sunhat` | ✅ (occlusion fixed 2026-09-14) | brim, crown, tilt, lift, drop, flat, front arc, **rim** (fold-over depth, 0.45), pom count/at/r | `hat-brim.left/right/top/bottom`, `hat-brim@t`, `hat-dome.*`, `hat.*` (family id = brim footprint) | brim-as-squashed-ellipse, dome on brim normal, far edge folding over the top surface (`rim`, fixed 2026-09-15 — the split used to be a straight chord across the disc, so the two fills met only at the tips and the brim read as a detached lozenge), near edge over crown. **Fixed 2026-09-14:** P17 z-split — brim is now ONE shape as two complementary slices (far → dome → near), so the dome sits behind the near brim; the old full-ellipse + thin rim strip is gone |
| `eye` | ✅ (SA2, 10 iters) | host, at (any relation), w, h, tilt, almond, mirror-of, glints, iris-w/h (auto-clamped to aperture), lash-w, line-w, glint-side (world light!), gaze, refl-fill, *-fill, z | aperture bbox, outerx/outery, innerx/innery, irisx/irisy, topx/topy, botx/boty, facing, `{along: eye, t}` | generated almond aperture (two lid arcs), two-tone iris, pupil, glints + green reflection, ONE-SIDED tapered lash anchored on the lid line with outer wing, sealing outline; `mirror-of` = whole second eye as one relation |
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

(🔬 = proven in the SA3 starry-night probe copies at
`.scratch/14-abstraction-research/work/starry/`, not yet promoted to `scripts/`.)

SA3 probe note (starry-night, `.scratch/14-abstraction-research/work/starry/`): the five
scene families above were proven reference-free from a parameter-only spec (9 iterations,
byte-deterministic). Two structural findings recorded in `work/starry/report.md`:
(1) back-end generators need a spec-level **generator bridge** — today each needs a
hand-written passthrough family in the resolver; (2) the three relations under the
families — `flow`, `distribute-along`, `jitter-grid` — should be promoted to first-class
relation forms so they are reusable beyond one family each.

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
6. **The family gets an entry here the same session it lands**, with its parameter list — docs first,
   per SSOT.

## Encapsulation boundary: families vs relations (architectural principle)

Intra-family layout — iris inside sclera, glint inside iris, dome on brim normal — is **arithmetic on
the family's own anchors**, encapsulated so the spec never sees it. Relations are for **cross-object
composition**: placement, spacing, alignment, junctions, occlusion intent. Consequence for the
taxonomy (abstraction.md): a proposed relation should first be asked "is this really intra-family?
Should it be a parameter instead?" — `inside`, for instance, mostly disappears once a family owns
its parts; `mirror` survives because faces pair two *instances* of a family.

## Design directions (adopted or noted — demand first)

- **Declarative families (ADOPTED — SA1 finding 10).** A family should be a YAML block — parameters
  plus sub-shapes whose relations may only use the family's own anchors — so the *model* can author a
  family without writing Python. Generator families (swirl, glow, …) delegate to scene_render.
  Canon rows become loadable data with provenance. `sunhat` is the migration example. This is the
  highest-leverage change in the design; it also makes "learning is the repo" literally true
  (knowledge becomes readable spec, not Python).

- **Style as a preset layer.** Anime-cel = hard outlines + flat fills + defined stroke weight; a
  future "impasto" style would change stroke/blur/palette defaults globally. Direction: a `style:`
  header that adjusts engine defaults, so the model picks a look instead of restating it per node.
- **`pair` wrapper.** Mirror an instance (eyes, poms) with per-side tweaks for 3/4 view — the
  relation survives, the wrapper makes it ergonomic.
- **The `head` family follows Loomis ball-and-plane construction** (validated pattern from art
  pedagogy, 2026-09-14 web check): head = sphere + jaw block; a **cross** (mid-line + eye line)
  encodes pose; features attach to the cross by canon fractions. Mapping onto this system: the
  cross lines become exported anchors (`head.mid-line`, `head.eye-line`, `head.brow-line`,
  `head.chin-plane`), pose = rotating/offsetting the cross, features = `{along: head.eye-line, t}`
  + canon fractions. This is the model for how a family *constructs* rather than outlines.
- **Teacher vocabulary maps to artist vocabulary**: gesture ≈ `flow` relation, massing ≈ mass
  blobs before details, negative space ≈ P4 junctions, sight-size ≈ our `measure` step. When a
  human teaching term has no mechanical equivalent yet, that is a missing relation or family.

## Learning is the repo (framing)

The model's drawing knowledge is **this file + principles.md + measured canons**, all committed. Each
rung of the ladder appends a family entry, a canon row with provenance, and a principle. Nothing
needs to survive in model memory or weights — the repository is the learned drawing knowledge, which
is why docs-first is a hard rule and not a nicety.
