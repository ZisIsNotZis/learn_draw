# Vocabulary — object families and canons

Where drawing knowledge lives. `abstraction.md` defines the language (anchors / relations /
vocabulary); this file catalogs the families, the proportion knowledge (**canons**) they carry, and
the rules for adding one. The resolver `.scratch/06-relational-geometry/work/relate.py` implements
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

Provenance: skull top / hairline / chin from pixel scan at face centre (x=690: hair → skin at y≈243,
skin → collar at y≈377, skull top ≈150); eye geometry from the boundary-traced face exercise
(`02-portrait-face`, itself scan-verified). Head = skull top → chin, H≈228; face width at eye line
W≈190. This is a 3/4 view — left/right eyes differ; canons below are the *view-neutral* core.

| canon | value | note |
| --- | --- | --- |
| eye-centre height | 0.54 · head H | the classic "eyes halfway down" holds in anime too |
| eye width | 0.18–0.26 · head W | near eye reads wider than far eye in 3/4 |
| eye spacing (centre→centre) | ≈ 0.50 · head W | ≈ 2–2.7 eye widths — wider-set than realistic |
| nose y | 0.73 · head H | anime noses sit high and are a tick, not a shape |
| mouth y | 0.85–0.89 · head H | a short dash |
| hairline | 0.41 · head H | bangs cover the forehead; hairline ≠ skull top |
| head H : W | ≈ 1.2 | taller than wide |

Ladder rule: each vocabulary family's canon values get **measured from the reference first** (that is
the teacher phase), then live here as fractions. Generic art canons (Loomis-style) are a fallback
when no reference exists — not the primary source.

## Family catalog

Status: ✅ implemented · 🔨 in progress · 📋 needed (with the rung that demands it).

| family | status | params (beyond placement) | anchors exposed | carries |
| --- | --- | --- | --- | --- |
| `sunhat` | ✅ | brim, crown, tilt, lift, drop, flat, front arc, pom count/at/r | brim.left/right/top/bottom, brim@t, dome.* | brim-as-squashed-ellipse, dome on brim normal, near edge over crown |
| `eye` | 🔨 SA2 | size, tilt/almond, lid, iris fraction, glints, lash | outer/inner corner, top, bottom, centre, iris centre | sclera→lid→iris→pupil→glint→lash layer order |
| `brow`, `nose`, `mouth` | 📋 08 | length, angle, weight | ends, centre | mark-not-shape (P12) |
| `hair-mass` | 📋 08 | silhouette spine, width, tip zigzag, strand count | hairline, tips@t | one silhouette with zigzag bottom (P8), pink pockets as skin-through-notch |
| `sleeve`, `bow`, `collar` | 📋 09 | puff, gather count, knot size | knot, tails@t | cloth fold direction |
| `hand` | 📋 09 | pose preset, finger spread | knuckles@t, fingertips | z-plane tuck behind body (P17) |
| `pleats` | 📋 10 | count, depth, taper, seed | hem@t | fan from waist, alternating dark/light |
| `swirl` | 📋 SA3 | centre, radii, turns, width, taper | start, end, @t | flow-field ribbon (Starry-Night sky) |
| `glow` | 📋 SA3 | core r, halo r, rays, hue | centre, ray tips@t | radial gradient + rays |
| `flame-tree` | 📋 SA3 | height, sway, lobe count | trunk base, tip | stacked flame lobes |
| `village`, `hill` | 📋 SA3 | count, spacing curve, jitter seed | row@t | repetition with jitter |

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
