# A-cloth-v8 — v6-closeout with the second cuff visible and no background islands (M1a, A track)

This directory is `.scratch/35-r1-articulated-study/evidence/A-cloth-v6-closeout/`
copied and brought to conformance on the two points the user's review fixed (issue 54:
two sleeves, the second "not invisible, it's just small, partially covered"; and the
hair facts in `work/a-art-direction-brief.md`: no background-coloured hole inside a hair
mass).  Same drawing, same parts, same palette and composition; nothing else was
touched.  Nothing here decides whether the picture is good; **no art verdict is
recorded, and the artwork verdict belongs to a fresh independent reviewer.**

The reference is the registered crop of `image.jpg` (source bbox `500,320,900,800` →
400×480, crop SHA-256
`52e01f5e75e5d98fcd9a0a4c63be91ed09b8a18ca0f62e7e0348a021b2dd87d`), recovered here in
`ref/crop-400x480.png`.  The build reads no image: the crop seeded the numbers while
they were authored, and the engine sees geometry only.

What this revision changed, with the before/after numbers, the commands and the
mutation evidence for each: [`conformance-log.md`](conformance-log.md) — FIX 1 (the second
cuff's surviving wedge, 0.0 % → 16.4 % of the first cuff) and FIX 2 (both enclosed
background islands closed by routing the hair sheet's outline to the face, 2 → 0).  Two
source files change (`parts/sleeve.py`: one authored coordinate; `parts/hair.py`: one
generator reach term), plus two tests and one new test file.
[`closeout-log.md`](closeout-log.md) is the v6 record kept as it was, including its item
N4, which this revision closes.

## What this drawing is

13 parts, 8 objects, one `source/assemble.py:OBJECTS` entry per object.  A test fails if
a part is missing from the inventory or an object is split without a stated reason.

| object | parts | the single connected physical thing | split reason |
| --- | --- | --- | --- |
| head | `A-head-face` | one face field: generated chin/jaw boundary below, frame-cut skull above, no feature claim | — |
| collar | `A-collar-left`, `A-collar-right` | one sailor collar around the neck opening | two leaves sewn at the shared front seam Q..Q′, checked geometrically |
| neck | `A-visible-neck-skin` | one neck field between the jaw relation and the collar opening | — |
| bodice | `A-bodice-upper`, `A-derived-waist-band`, `A-bodice-continuation` | one blouse: chest cloth, gathered waist, skirt below | three sections of one width field, not separate garments |
| left sleeve | `A-left-sleeve`, `A-left-cuff` | one sleeve on the wearer's left: cap, puff, dark cuff | the cuff is one band sewn onto the sleeve's terminal section |
| right sleeve | `A-right-sleeve`, `A-right-cuff` | one sleeve on the wearer's right | same shared terminal section |
| bow | `A-bow-ribbon` | one magenta ribbon tied into a bow: knot, two lobes, two tails | — |
| hair | `A-hair-sheet` | one head-attached hair sheet whose reverse side faces the camera after the crown turn | — |

Generated at this revision: **2018 faces, 15 visible fill regions, 41 marks clipped into
62 paths, 18 declared joints, 0 failed, 36 declared anchors = 34 joint endpoints + 2
stated non-joints.**

## The seam contract, and what each clause proves

`kind="seam"` requires both anchors on their own part's outline, coincidence within
`1e-6`, a shared tangent direction within `1e-6`, and the declared depth relation.
`kind="attachment"` (a piece set into another) requires position and layering only —
an attachment has no shared boundary direction, and the docstring, `NON_JOINTS` and this
table say the same thing.  Depth rules: `SAME_SURFACE` |Δdepth| ≤ 2×10⁻³; `CLOTH_LAYER`
the outer piece 0…0.30 in front.

| joints | parts | kind | depth rule |
| --- | --- | --- | --- |
| S1 collar front | collar-left.Q′ ↔ collar-right.Q′ | seam | same surface |
| S2, S3 collar roots | bodice opening roots ↔ collar R | seam | cloth layer |
| S4, S5 skin roots | neck skin R_left/R_right ↔ collar R | seam | cloth layer |
| S6 skin opening | bodice Q ↔ skin Q | seam | cloth layer |
| S7 waist section (2 anchors) | bodice waist ↔ band upper | seam | same surface |
| S8 band → continuation (2 anchors) | band lower ↔ continuation upper | seam | same surface |
| S9, S10 cuffs (2 anchors each) | sleeve terminal section ↔ cuff contact edge | seam | same surface |
| S11, S12 jaw | head jaw_left/jaw_right ↔ neck skin jaw_left/jaw_right | seam | same surface |
| A1, A2 sleeve seats | bodice shoulder stations ↔ sleeve seat | attachment | cloth layer |

**The tangent clause verifies declaration consistency, not the outline.**  Each side's
tangent is the direction that side declares for the seam: a collar leaf's local +u is
defined as R→Q, a sleeve's cross direction is its terminal section, and the bodice, band
and skin anchors compute `_toward(anchor, anchor)` from two shared stations.  Because
both sides name the same two stations the clause compares two independent derivations of
one direction in two different frames; all 16 seam tangents agree to ≤ 7e-15.  Deriving
the tangent from the sampled outline was measured and rejected: at
`S8-band-continuation` the outline's local chord departs from the cloth's seam direction
by 84.3°, and six of the 16 seams exceed 40°, because an outline is a sampled contour and
not a seam.  The clause therefore catches a rotated *declared* direction
(`test_negative_control_rotated_tangent`) and cannot catch an outline that rotates while
its anchor stays put — recorded under *Unverified*.

**Anchor completeness is checked, not asserted.**  `seam_contract.unaccounted_anchors`
reports a declared anchor that no joint reads and no `NON_JOINTS` reason excuses, a
`NON_JOINTS` entry with no reason, and an inventory entry naming an anchor no part
declares.  `tests/test_anchor_inventory.py` holds it at zero; `source/build_a.py` adds
the same finding to the build report and **exits non-zero** when it is not empty.  The
demonstration: re-adding the two cuff `sleeve_seat` anchors gives `anchors_declared 38`,
two `ANCHOR UNACCOUNTED` lines, build exit 1 and two failing tests, and restoring gives
`36 = 34 + 2 + 0` and a passing suite (`tests/negative-control-output.txt`, block M1).

## Mechanism claims, and how each is true at this revision

**The bow is one continuous strip.**  One polyline, one constant half width
(`HALF_WIDTH = 17.0`), visited as left tail → knot → left lobe → knot → right lobe →
knot → down tail.  `test_bow_width_is_continuous_through_the_knot` measures the emitted
grid: every one of the 121 rows spans 34.000000 in 3D, the rows that pass the knot are
rows of that same strip, and the two ends of the strip carry the same width.  Creases are
three short curves lying on the strip surface.

**The three knot passes are separated in depth.**  `bow.PIECE_DEPTH` gives pass 1 the
band `[0.600, 0.606]`, pass 2 `0.618` and pass 3 `0.636`, so the three bands miss each
other by at least one `CLOTH_THICKNESS` (0.012) over their whole spans and depth — not
the visibility tie rule — decides which layer is in front.  (N7: pass 1 previously ramped
to 0.624, crossing pass 2's 0.612 exactly at its midpoint.)

**The hair's reverse side is a twist.**  `hair.py` passes `twist=twist` to
`StripSurface`, and `frames.StripSurface.point` applies that single angle to the whole
column (both edges take `cos(ang)` on the offset, depth takes
`half·sin(ang)·DEPTH_PER_UNIT`), so the normal's camera component changes sign and the
mint fill is the far side of the cloth.  `test_the_twist_is_what_turns_the_sheet_over`
asserts that replacing `twist(t)` by 0 collapses the reverse-side face count.

**Every face carries its own side's colour.**  `SheetPart.faces` paints each of a quad's
two triangles from that triangle's own projected winding.  The previous revision painted
both from the first triangle's, which gave 48 of 1380 faces the opposite side's colour (7
hair, 41 bow; `test_fill_winding.py` reports the number and fails if no face disagrees,
so the rule cannot be vacuous on this geometry).

**The neck is one field, not a column.**  Its upper boundary is the face's own jaw
relation (`families.jaw_section`, called with the same stations by `head.py` and
`skin.py`), its lower/side boundary follows the collar's opening relation into `Q`, and
the boundary the collar hides is routed round the jaw's right end (`NECK_WRAP = 8.0`)
because a straight path would cross the jaw relation and invert the contour.

**Two whole sleeves with whole cuffs, the second partly visible.**  Each sleeve runs
from its shoulder cap to the shared terminal section on its own support; each cuff is a
whole band sewn to that section (S9/S10).  The second (left) cuff's authored area is
331.5 px² and **88.37 px² of it survives — 16.4 % of the first cuff's 539.5 px²**
(`tests/test_two_sleeves.py::test_second_cuff_is_authored_whole` prints that number); the
bow (z 0.60) and the hair fall (z 0.45) are in front of it, so the wedge is depth's output
and not an authored cut.  The cuff is never cut, shortened or given a "visible part": its
one authored coordinate puts it clear of the fall, and lifting the front cloth restores
its whole authored area within 2 %.

**No background island inside the drawing.**  Two background-coloured regions used to be
enclosed by ink — 1023 px at bbox (162,39,35,60) and 17 px at (243,82,4,9) in the v6
render — and the count is now **0** on the delivered 400×480 PNG
(`tests/test_no_background_holes.py` prints the count and the rule: background = every
channel within 6 of #78a49b, 4-connected, a component touching the border is ignored, any
other component of ≥ 4 px is a hole).  They are closed by routing the hair sheet's
outline to the face field, not by drawing a patch over them; the same rule run against
`evidence/A-cloth-v6-closeout/artwork-a.png` still reports both islands, so the test can
fail.

**No manual clipping.**  Nothing in `source/` declares a visible range or a back/front
copy.  Fills come from `scripts/vector_visibility.visible_regions` over projected
triangles; marks are depth-clipped sample by sample in `source/lines.py`.

**Every mark names its class, its owner and its source.**  `assemble.LINE_POLICY` maps
`silhouette`, `free_edge`, `contact`, `fold_edge`, `trim` to one colour and one width
each; `mark_geometry` draws only declared semantic edges, stamps each mark with a class,
an owning part and the geometry that produced it, and raises if a class or an owner is
undeclared.  `tests/test_line_ownership.py` checks the same facts on the emitted marks
and on the SVG paths.

## Authoring budget — declared against the code, per part

`source/authored.py` scans every part module by AST for two-number literal pairs, and
`python3 source/authored.py` prints this table.  `tests/test_authoring_inventory.py`
fails on any pair the inventory does not account for, on any part module the inventory
does not scan, and on any part whose declared `authored` list is not exactly its
landmarks.  The budget is 5 landmarks for a sheet and 4 for a planar part.

| part | module | own landmarks | shared station | names |
| --- | --- | --- | --- | --- |
| `A-bodice-upper` | bodice | 3 | 0 | C0, Cw, Eleft |
| `A-bow-ribbon` | bow | 4 | 0 | knot, left_lobe_tip, right_lobe_tip, left_tail_exit |
| `A-collar-left` | collar | 3 | 1 | R, E, S |
| `A-collar-right` | collar | 3 | 1 | R, E, S |
| `A-hair-sheet` | hair | 5 | 0 | left_tip, left_bulge, crown, right_shoulder, right_tip |
| `A-head-face` | head | 3 | 0 | chin, jaw_left, jaw_right |
| `A-left-sleeve` | sleeve | 1 | 0 | C (its cuff centre) |
| `A-right-sleeve` | sleeve | 1 | 0 | C (its cuff centre) |
| `A-visible-neck-skin`, `A-derived-waist-band`, `A-bodice-continuation`, both cuffs | — | 0 | 0 | — |

The collar's shared station is `OPENING_XY`, the one opening relation the two leaves are
solved on.  The scan also accounts for every *other* two-number literal in the part
library — depth gradients, the down tail's direction, depth bands, gather fractions, the
head frame's origin, anchor tangents — and this revision has 49 such declared pairs over
9 modules: 24 landmarks and shared stations, 25 non-landmarks, 0 unaccounted.

## Claims audit — what the previous package said that was false

Every claim the v6 package made about itself that this closeout found false, and how it
stands now.  The full table with locations is in
[`closeout-log.md`](closeout-log.md#claims-audit--what-the-previous-package-said-that-was-false-and-how-it-now-stands).

| false claim | now |
| --- | --- |
| a completeness test for the joint list exists ("provably complete") | it did not; it does now, and the build refuses an unaccounted anchor |
| the test suite's 22 tests distinguished success from failure | two could not fail on any input; both rewritten to measure delivered geometry, with mutations |
| `A-bodice-upper` hand-types 2 coordinates | it hand-types 3; counts are now checked against the source by AST |
| the fill of each face comes from its own winding | false for 48 of 1380 faces; now true, with that count kept as the negative control |
| the shared tangent is a geometric boundary check | it is a declaration check; said so, and given its third negative control |
| `tests/test_line_ownership.py` enforces line ownership | the file did not exist; it exists now, and the `owner` stamp it checks was itself wrong |
| dead code, a missing hole test and a missing tangency control are merely "unverified" | dead code deleted with reachability evidence, tangency control added; the hole test was still missing in v6 **and the drawing had two enclosed background holes** — v8 adds the test and closes both holes (`conformance-log.md`, FIX 2) |

## Files

| path | what it is |
| --- | --- |
| `source/` | part library: `assemble.py` (scene + SVG), `build_a.py` (build entry point, enforces the seam contract and the anchor inventory), `seam_contract.py`, `authored.py` (the authoring inventory), `lines.py`, `parts/` (one module per object family) |
| `tests/` | 47 `unittest` tests, plus `negative-control-output.txt` (the v6 mutation transcript; the v8 mutation pairs live in the tests themselves) |
| `artwork-a.svg`, `artwork-a.png` | the built SVG and its 1:1 render (400×480) |
| `check-a/` | the `scripts/draw check` bundle from the current tooling: `draft-fullres.png` (1:1, bytes equal to `artwork-a.png`), `draft.png`, `side-by-side.png`, three region crops, `report.txt` with the current reviewer protocol |
| `ref/` | the reference crop and four zoom crops used while authoring |
| `manifest.json`, `manifest.sha256` | the file set with its hashes |
| `closeout-log.md` | the v6 record: B1–B3 and N1–N7, each with its disposition and the command that shows it |
| `conformance-log.md` | FIX 1 and FIX 2: what changed, before/after numbers, commands, mutation evidence |

The previous package's `repair-log.md` (D1–D12) and `work-checkpoint.md` were removed
here: the checkpoint's "complete and hash-verified" claim was false, and the repair log's
D9 and D11 claims are contradicted by this revision.  Both files remain in git at
`evidence/A-cloth-v6/`, and each false claim they carried is listed in the claims audit
below.

## Commands actually run at this revision

```bash
PKG=.scratch/35-r1-articulated-study/evidence/A-cloth-v8

# tests: 47, all passing (run from $PKG)
python3 -m unittest discover -s tests -t .

# the authoring table (declared against the source by AST)
python3 source/authored.py

# build, no reference input at any point
python3 $PKG/source/build_a.py --out $PKG/artwork-a.svg --report $PKG/source/build-report.json
#   prints: faces 2018, parts 13, seams_total 18, seams_failed 0, visible_fill_regions 15,
#           anchors_declared 36, anchors_joint_endpoints 34, anchors_non_joints 2

# the visual bundle from the CURRENT tooling, then the 1:1 render as the delivered PNG
scripts/draw check $PKG/artwork-a.svg --ref $PKG/ref/crop-400x480.png --outdir $PKG/check-a
cp $PKG/check-a/draft-fullres.png $PKG/artwork-a.png

# reproducibility: two builds into separate paths, compared byte for byte
python3 $PKG/source/build_a.py --out /tmp/brep1/a.svg
python3 $PKG/source/build_a.py --out /tmp/brep2/a.svg
cmp /tmp/brep1/a.svg /tmp/brep2/a.svg && cmp /tmp/brep1/a.svg $PKG/artwork-a.svg
#   identical; sha256 120579a26adb1d2e4bc20cdc3a5a4559344cd637485d0bccca7510554014bba2
#   artwork-a.png == check-a/draft-fullres.png, sha256
#   da9d92c9935697a6a8fa70e25f61b7a2218e7dbd414817433a8f0bd39febd38b

# the two measured facts of this revision, each with the test that prints it
python3 -m unittest tests.test_two_sleeves tests.test_no_background_holes -v
#   second cuff: authored 331.5 px2, visible 88.37 px2, 16.4 % of the first cuff's 539.5 px2
#   band 0.10..0.25: delivered 0.164, at the v6 coordinate 0.000, front cloth lifted 0.614
#   400x480 artwork-a.png: 0 enclosed background component(s) at tolerance 6, minimum 4 px
#   rule applied to A-cloth-v6-closeout/artwork-a.png: [(1023, (162,39,35,60)), (17, (243,82,4,9))]

# manifest, and the manifest pair's own handling
(cd $PKG && sha256sum -c manifest.sha256)
```

Manifest handling: `manifest.json` lists every delivered file except `manifest.json` and
`manifest.sha256` themselves, because a file cannot contain its own hash.
`manifest.sha256` is generated from `manifest.json`'s list *plus* `manifest.json`, so the
pair is bound to each other in one direction and nothing is left unverified except
`manifest.sha256` itself, which the reader can recompute from the same list.  At this
revision 46 entries verify OK (45 delivered files plus `manifest.json`) and
`manifest.sha256` itself is the one hash the pair cannot contain; its own value is the
last line of `manifest.json`'s companion list, recomputable from that list.  A full set
of OK means the delivered set is the set described; the
pair's own hashes are printed in this README's command block, so a stale manifest cannot
hide behind its own success.

## Verified at this revision (writer-verified; not an art verdict)

- `build_a.py` exits 0: 13 parts, 2018 faces, 18 declared joints, 0 failed, 36 anchors
  declared = 34 joint endpoints + 2 stated non-joints + 0 unaccounted.
- 47 tests pass, including: every declared joint passes; a 4 px translation fails and the
  restored build passes; a cuff on an unrelated support fails; a rotated declared tangent
  fails while the boundary stays put; an unaccounted anchor is reported by both the build
  and the test; both sleeves and both cuffs exist on four distinct supports; the second
  cuff's authored area reappears when the front cloth is lifted; the hair has both side
  fills and loses them without the twist; every face's fill agrees with its own winding;
  the bow's measured width is constant through the knot; the declared authoring inventory
  equals the hand-typed stations in the source for every part; the second cuff's surviving
  area is 16.4 % of the first cuff's and the band rejects both a hidden (0.000) and a fully
  exposed (0.614) cuff; the delivered render has zero enclosed background components while
  the same rule finds the v6 render's two.
- Four source mutations fail their test and pass after restoration (unaccounted anchor,
  bow width, cuff in front, per-quad fill): `tests/negative-control-output.txt`.
- Two builds are byte-identical and equal to the shipped `artwork-a.svg`.
- `sha256sum -c manifest.sha256` reports every listed file OK.
- `check-a/` was regenerated with the current `scripts/draw`, so `report.txt` lists the
  1:1 draft first and carries the current reviewer protocol.

## Unverified / limits — stated, not softened

- **No art verdict.**  Nobody has judged these images at this revision.
  `check-a/report.txt` lists the images for a fresh reviewer; the metrics in it (edge-F1
  0.282, coverage 0.416) are a breakage alarm, and nothing was tuned against them.
- **How the second cuff's wedge *reads* is unjudged.**  It is measured at 88.37 px²
  (16.4 % of the first cuff, against the reference's 17 %), but whether the dark wedge
  emerging between the hair fall and the bow's left tail looks like a cuff is an art
  judgement for a fresh reviewer.
- **The reach term changes the hair silhouette where the sheet meets the face.**  Those
  two places are filled now and were background before; their appearance is unjudged.
- **The tangent clause cannot see an outline that rotates about a static anchor.**  It
  compares declared directions; deriving them from the sampled outline is measured to be
  unfaithful (up to 84.3° at a corner).  A seam whose two outlines rotate together while
  the declarations stay is not detected.
- **The hole rule sees the raster, not the hair.**  `tests/test_no_background_holes.py`
  checks enclosed background components on the delivered PNG (4-connected, tolerance 6,
  ≥ 4 px); an island thinner than 4 px would not be reported, and the rule does not ask
  which part encloses the island — it rejects any enclosed background, which is stricter.
  `test_line_ownership.py` still checks the emitted marks and the SVG paths, not the
  raster.
- **The authoring scan covers two-number literal pairs only.**  A coordinate split into
  two separate scalar literals would not be counted; this revision's part modules do not
  do that (read, not checked).
- **Declared points are not one spelling.**  Some builders store the authored station as
  crop pixels, some in plane coordinates, some in the part's local frame; the inventory
  test accepts any of the three representations of the landmark.  Harmonising them is a
  small future change, not a claim defect.
- Interpenetration of the support surfaces is not inspected as a gate: the declared
  contacts are the joints above, and nothing checks physical overlap beyond those depth
  relations.
- The two collar leaves are generated in the shared plane and stored in local frames (a
  coordinated pair cannot be authored twice without breaking the shared front seam);
  every other part is generated in its own local frame.
- Reference-pixel facts a reviewer might check (bow lobe silhouettes, hair fold
  positions, the head's landmarks) are authored hypotheses chosen while the crop was
  open, not traced: the build reads no image, and `image.jpg` was not read for geometry
  in this closeout.
