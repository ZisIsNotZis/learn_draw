# A-cloth-v5 — one connected object per drawn part (M1a)

Candidate for the A track of R1: an authored SVG study imitating only the clothing and
broad composition of the registered reference crop (`image.jpg` source bbox
`500,320,900,800` → 400×480 crop, crop SHA-256
`52e01f5e75e5d98fcd9a0a4c63be91ed09b8a18ca0f62e7e0348a021b2dd87d`, re-derived here in
`ref/crop-400x480.png` and hash-identical to the registered digest). There is no hand
claim and no pose claim. **No art verdict is recorded here; the artwork verdict belongs
to a fresh independent reviewer.**

## What changed against A v4

| property | v4 (recorded) | v5 |
| --- | --- | --- |
| bow | gather patch + two separate loop solids + a separate tail wider than the knot | one continuous ribbon: knot → left lobe → knot → right lobe → knot → both tails, one constant width |
| sleeves | one sleeve | two whole sleeves, each shoulder-cap → puff → cuff, on its own support |
| second cuff | absent | authored whole; its surviving wedge is a depth result (see the ablation test) |
| hair | flat single-colour band extrusion | one head-attached sheet whose inside is painted by projected face orientation (blue outside, mint inside) |
| construction | one `build_scene()` | part library, one module per object family, each in its own local (u,v) frame |
| joints | three name strings, no geometric requirement | 16 declared joints checked for boundary coincidence, shared tangent and depth relation |

## Object inventory — every object and the one connected thing it is

| object | parts | the single connected physical thing | split reason |
| --- | --- | --- | --- |
| collar | `A-collar-left`, `A-collar-right` | one sailor collar lying around the neck opening | the real collar is two leaves sewn at the shared front seam Q..Q′; the seam is checked geometrically |
| neck | `A-visible-neck-skin` | one continuous skin field from the opening up past the crop | — |
| bodice | `A-bodice-upper`, `A-derived-waist-band`, `A-bodice-continuation` | one blouse: chest cloth, gathered waist, and the same cloth below | the band is a section of one width field, not a separate garment |
| left sleeve | `A-left-sleeve`, `A-left-cuff` | one sleeve on the wearer's left | the cuff is a band sewn onto the sleeve's terminal section (shared exactly) |
| right sleeve | `A-right-sleeve`, `A-right-cuff` | one sleeve on the wearer's right | same shared terminal section |
| bow | `A-bow-ribbon` | one magenta ribbon tied into a bow | — (one strip, one grid, one fill relation) |
| hair | `A-hair-sheet` | one head-attached hair sheet, blue outside and mint inside | — (one sheet parameterization) |

No object is an unexplained collection: `source/assemble.py:OBJECTS` holds this table and
`tests/test_identity.py` fails if a part is missing from it or a split has no reason.

## Seam inventory — every declared joint and what is enforced

`kind=seam` requires (a) both anchors **on their own part's outline**, (b) coincidence
within `1e-6`, (c) a shared tangent direction within `1e-6` (parallel or antiparallel),
(d) the declared depth relation. `kind=attachment` (a piece set into another) requires
(a), (b), (d) but no tangent, because no shared boundary direction exists. Depth rules:
`SAME_SURFACE` = |Δdepth| ≤ 2×10⁻³ for two pieces of one cloth; `CLOTH_LAYER` = the outer
piece lies 0…0.30 in front of the inner one (one cloth thickness over the body).

| joint | parts | kind | depth rule |
| --- | --- | --- | --- |
| S1-collar-front | collar-left.Q′ ↔ collar-right.Q′ | seam | same surface |
| S2/S3 collar roots | bodice opening roots ↔ collar R | seam | cloth layer (collar over bodice) |
| S4/S5 skin roots | neck skin R ↔ collar R | seam | cloth layer (collar over skin) |
| S6-skin-opening | bodice Q ↔ skin Q | seam | cloth layer (skin over bodice) |
| S7 waist section (×2 anchors) | bodice waist ↔ band upper | seam | same surface |
| S8 band → continuation (×2) | band lower ↔ continuation upper | seam | same surface |
| S9/S10 cuffs (×2 anchors each) | sleeve terminal section ↔ cuff contact edge | seam | same surface |
| A1/A2 sleeve seats | bodice shoulder stations ↔ sleeve seat | attachment | cloth layer |

The check fails a build (`build_a.py` returns non-zero) and fails the test suite. The
negative control breaks a joint on purpose, shows the failure, and restores it:
`tests/negative-control-output.txt` (a 4 px leaf displacement is reported as
`S1-collar-front | boundary gap 4.000000 > 1e-06`; lifting a cuff 0.5 in depth is
reported as `S10-left-cuff | depth gap 0.500000 > 0.002`; the restored build reports
0 failed).

## Observed in the crop vs artist hypothesis

Observed (used to place geometry; the reference is never read at build time):
light blouse field with a gathered waist and a dark waist band; light collar field with a
dark trim running to a V; a magenta bow left of centre with two lobes, a knot, a tail
leaving the left frame edge and a tail ending on the bodice; a large right sleeve ending
in a wide dark navy cuff near (343,283)-(403,343); a second small sleeve with its own dark
cuff near (84,257)-(105,271), partly covered by the pink tail, with a white sleeve sliver
beside it; blue hair masses on both sides of the face; pale skin at the neck.

Artist hypothesis (not measured, not recovered 3D truth): the tying order of the ribbon
(left tail → knot → left lobe → knot → right lobe → knot → down tail); the ribbon's
constant half width 17 px and limb separation 30 px; the bow's lobe tips at (122,175) and
(262,186); the depth values and cloth-layer offsets; the hair's route (out at the lower
left, over the crest, above the frame behind the head, in on the right of the neck, down
the right fall), its widths and its depth sweep from 0.24 to 0.52; the collar's leaf
widths and bend; the body width field; the sleeve radii and cap heights; that the bow's
left tail passes in front of the second cuff (per the user's reading in issue 54, and it
is what makes the surviving wedge a depth result).

## Where the geometry comes from

No shape carries more than four hand-typed coordinates (`tests/test_identity.py`
enforces 4 for planar parts, 5 for the two sheet parts). Authored coordinates per part:
collar leaves 3 stations each (root, shoulder-edge, edge) plus one shared opening station;
bodice 2 stations; neck skin 1; each sleeve 1 (cuff centre, seat derived from the bodice
boundary relation); bow 4 (knot, two lobe tips, left tail exit); hair 5 landmarks. Lobes,
folds, tail routes, widths, section profiles and all frame coordinates are generated.

Sheet parts (bow ribbon, hair sheet) are parametric (u,v) surfaces with a generated spine,
a generated half-width and a generated depth; they fold back through depth, so their own
limbs occlude one another. Fill is chosen per face by that face's projected winding, so a
sheet's second side is a geometric fact, never a declared colour list.

## Commands actually run

```bash
# crop registration (re-derived, hash checked against the registered digest)
.venv/bin/python - <<'PY'   # PIL crop of image.jpg at (500,320,900,800)
PY

# build (no reference input at any point)
.venv/bin/python .scratch/35-r1-articulated-study/evidence/A-cloth-v5/source/build_a.py \
    --out .scratch/35-r1-articulated-study/evidence/A-cloth-v5/artwork-a.svg \
    --report .scratch/35-r1-articulated-study/evidence/A-cloth-v5/source/build-report.json

# the visual bundle (outdir inside this candidate; never the default path)
scripts/draw check .scratch/35-r1-articulated-study/evidence/A-cloth-v5/artwork-a.svg \
    --ref .scratch/35-r1-articulated-study/evidence/A-cloth-v5/ref/crop-400x480.png \
    --outdir .scratch/35-r1-articulated-study/evidence/A-cloth-v5/check-a
cp check-a/draft-fullres.png artwork-a.png        # 400x480, the delivered image

# tests (21 tests, alphabetically; includes the negative control)
cd .scratch/35-r1-articulated-study/evidence/A-cloth-v5
../../../..//.venv/bin/python -m unittest discover -s tests -t . -v

# manifest
sha256sum over every source and output file -> manifest.sha256
```

`artwork-a.png` is the 1:1 render produced by the project's own `scripts/draw` bundle, so
the delivered image is the artefact the reviewer's tooling measured.

## Verified in this candidate (writer-verified, not an art verdict)

- `build_a.py` exits 0 and prints `seams_failed: 0` for 16 declared joints.
- 21 tests pass (`tests/`), including: every declared joint passes; the deliberate
  4 px break fails and the restored build passes; a cuff on an unrelated support fails;
  both sleeves and both cuffs exist on four distinct supports; the second cuff's authored
  outline is larger than its visible extent and becomes ~2.4× more visible with the bow's
  faces removed (so its surviving shape is a depth result, not an authored cut); the hair
  sheet has both side fills, both appear in the rendered SVG, its faces turn over in
  projection and its depth range exceeds 0.05; the bow is one sheet with one width, its
  centreline returns to the knot at least three times and visits both lobe tips; the
  object inventory covers every part exactly once; the authoring budget holds.
- The check bundle exists at `check-a/` with `report.txt` listing its images.

## Unverified / limits

- **No art verdict.** Nobody has judged this image; a fresh independent image-only review
  is the next gate. The writer's own inspection noticed: the knot area is busy with
  converging crease marks, the hair sheets read as broad bands rather than hair volumes,
  and the bodice silhouette is a wedge — all left for review rather than tuned against a
  metric.
- Metrics in `check-a/report.txt` are breakage alarms only; nothing was tuned to them.
  They will read badly because this candidate deliberately does not draw the face, the
  full hair mass or the skirt.
- The `families.py` copy differs from A v4's `family-rules.py` by one line: the puff
  sleeve's outline now includes its terminal section (`reversed(side_a)` instead of
  `reversed(side_a[:-1])`). Without it the sleeve's boundary omitted the very section the
  cuff is sewn to, which is why the cuff joint could not be checked at all.
- Reference-pixel facts that a reviewer might check (e.g. exact bow lobe silhouettes, the
  hair's fold positions) are authored hypotheses, not traced. The reference was used to
  choose numbers, then closed; the build reads no image.
- Interpenetration was not inspected as a separate gate here (WP05's job). The bow, hair
  and sleeves are separate support surfaces; declared contacts are the cuff seam, the
  sleeve seats and the openings. Nothing was checked for hidden-surface physical overlap
  beyond the declared depth relations.
- The two collar leaves are still generated in the shared plane and stored in local
  frames: a coordinated pair cannot be authored twice without breaking the shared front
  seam. Every other part is generated in its own local frame.
