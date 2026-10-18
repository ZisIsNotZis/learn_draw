# A-cloth-v6 — cloth on support surfaces, with a generated head boundary (M1a, A track)

Candidate for the A track of R1: an authored SVG study imitating only the clothing, head boundary
and broad composition of the registered reference crop (`image.jpg` source bbox `500,320,900,800`
→ 400×480 crop, crop SHA-256
`52e01f5e75e5d98fcd9a0a4c63be91ed09b8a18ca0f62e7e0348a021b2dd87d`, recovered here in
`ref/crop-400x480.png`). There is no hand claim and no pose claim. **No art verdict is recorded
here; the artwork verdict belongs to a fresh independent reviewer.**

Repair round status: `repair-log.md` maps every defect D1–D12 of the wave-3 dispatch to what the
code actually does at this revision. This README is written to that same rule — each mechanism
claim below was read off the code or printed by the build, and the claims that could not be proved
are listed under *Unverified* rather than softened.

## What this revision is

| | v5 (recorded) | v6 (this revision) |
| --- | --- | --- |
| head | none — a pink column leaving the top edge | `A-head-face`: generated chin/jaw relation below, labelled frame-cut closure above, no feature claim |
| neck | one column continuing past the crop | bounded by the jaw above and the collar opening at `Q` below; hidden boundary wraps behind the collar |
| hair route | two full-height strips | five crop landmarks + one generated catmull, a crown crossing above the frame, a sine taper and a shoulder curl |
| hair twist | claimed but not implemented (`StripSurface` built without `twist`) | `twist(t)` is passed and applied to every column of a station; the reverse side is a twist result |
| bow knot | three passes at one depth | three passes separated by `CLOTH_THICKNESS`, so depth decides the front layer |
| ink | per-part outlines | one policy by semantic class (`LINE_POLICY`), every mark naming its source |
| joints | 16 declared | 18 declared (16 seams, 2 attachments), all passing |

## Object inventory — every object and the one connected thing it is

`source/assemble.py:OBJECTS` is the machine-readable copy of this table; a test fails if a part is
missing from it or a split has no stated reason. 13 parts, 8 objects.

| object | parts | the single connected physical thing | split reason |
| --- | --- | --- | --- |
| head | `A-head-face` | one face field whose generated jaw boundary and frame-cut skull make a head read | — |
| collar | `A-collar-left`, `A-collar-right` | one sailor collar lying around the neck opening | the real collar is two leaves sewn at the shared front seam Q..Q′ |
| neck | `A-visible-neck-skin` | one neck field from the jaw down into the collar opening | — |
| bodice | `A-bodice-upper`, `A-derived-waist-band`, `A-bodice-continuation` | one blouse: chest cloth, gathered waist and the skirt below it | the band and skirt are sections of one width field, not separate garments |
| left sleeve | `A-left-sleeve`, `A-left-cuff` | one sleeve on the wearer's left: cap, puff, dark cuff | the cuff is one band sewn onto the sleeve's terminal section |
| right sleeve | `A-right-sleeve`, `A-right-cuff` | one sleeve on the wearer's right | same shared terminal section |
| bow | `A-bow-ribbon` | one magenta ribbon tied into a bow: knot, two lobes, two tails | — |
| hair | `A-hair-sheet` | one head-attached hair sheet whose reverse side faces the camera after the crown turn | — |

## Seam contract — 18 declared joints, checked geometrically

`kind="seam"` requires (a) both anchors on their own part's outline, (b) coincidence within
`1e-6`, (c) a shared tangent direction within `1e-6` (parallel *or* antiparallel), (d) the declared
depth relation. `kind="attachment"` — a piece set into another — requires (a), (b) and (d) but
**not** the tangent, because two sewn pieces have a shared boundary direction and a set-in piece
does not; the docstring, `NON_JOINTS` and this table say the same thing, so no claim of a shared
direction is made for an attachment. Depth rules: `SAME_SURFACE` = |Δdepth| ≤ 2×10⁻³ for two
pieces of one cloth; `CLOTH_LAYER` = the outer piece lies 0…0.30 in front of the inner one.

| joints | parts | kind | depth rule |
| --- | --- | --- | --- |
| S1 collar front | collar-left.Q′ ↔ collar-right.Q′ | seam | same surface |
| S2, S3 collar roots | bodice opening roots ↔ collar R | seam | cloth layer (collar over bodice) |
| S4, S5 skin roots | neck skin R_left/R_right ↔ collar R | seam | cloth layer (collar over skin) |
| S6 skin opening | bodice Q ↔ skin Q | seam | cloth layer (skin over bodice) |
| S7 waist section (2 anchors) | bodice waist ↔ band upper | seam | same surface |
| S8 band → continuation (2 anchors) | band lower ↔ continuation upper | seam | same surface |
| S9, S10 cuffs (2 anchors each) | sleeve terminal section ↔ cuff contact edge | seam | same surface |
| S11, S12 jaw | head jaw_left/jaw_right ↔ neck skin jaw_left/jaw_right | seam | same surface |
| A1, A2 sleeve seats | bodice shoulder stations ↔ sleeve seat | attachment | cloth layer |

`NON_JOINTS` accounts for the two anchors that are deliberately not joints
(`A-head-face.chin`, `A-bow-ribbon.knot`), and `tests/test_seam_contract.py` fails a declared
anchor that appears in neither a `Joint` nor `NON_JOINTS`, so the joint list is provably complete.

Negative controls actually present (**two**, see *Unverified* for the missing third):
`tests/negative-control-output.txt` is a transcript produced by breaking the build on purpose:
a 4 px translation of a collar leaf is reported as `S1-collar-front | boundary gap 4.000000 >
1e-06` (and legitimately also breaks the two root joints it drags), a cuff lifted 0.5 in depth as
`S10-left-cuff | depth gap 0.500000 > 0.002`, and the restored build reports `0 failed`.

## Mechanism claims, and how each is true at this revision

**The bow is one continuous strip.** One polyline, one constant half width
(`HALF_WIDTH = 17.0`), visited in the order left tail → knot → left lobe → knot → right lobe →
knot → down tail; the limbs' overlap is produced by their depth bands, and the three knot passes
are separated by one cloth thickness. Creases are three short curves lying *on* the strip surface,
each crossing the turning fold of a lobe or the wrap at the tie — no mark is built from a limb's
spine, so no long chord can exist. (`source/parts/bow.py`.)

**The hair's reverse side is a twist, not a hairpin artefact.** `hair.py:124` passes `twist=twist`
to `StripSurface`; `hair.twist(t)` is one angle that sweeps a quarter turn over
`TWIST_START..TWIST_SPAN`, and `frames.StripSurface.point` applies that **single angle to the whole
column**: both edges take `cos(ang)` on their offset and depth takes `half·sin(ang)·DEPTH_PER_UNIT`.
So the normal's camera component really does change sign, and the mint fill is the far side of the
cloth. Measured: 312 reverse-side faces as authored, 12 when `twist(t)` is replaced by 0.
`tests/test_hair_two_sided.py::test_the_twist_is_what_turns_the_sheet_over` asserts that ratio, so
the mint cannot come back as a self-overlap without failing.

**The neck is one field, not a column.** Its upper boundary *is* the face's jaw relation
(`families.jaw_section`, called with the same stations by `head.py` and `skin.py`, so the jaw cannot
drift), and its lower/side boundary follows the collar's opening relation down into `Q`. The
boundary that the collar hides is routed round the jaw's right end (`NECK_WRAP = 8.0`, generated):
a straight path from the right collar root to `Q` crosses the jaw relation, because the collar's
inner edge hugs the jaw to within about half a pixel, and that made the contour self-intersecting.
The wrap lies behind the collar leaves, which are layered in front of the skin, so it is not
visible and carries no ink edge. All five boundary stations the seam contract reads are unchanged.

**Two whole sleeves with whole cuffs.** Each sleeve is built from shoulder cap to terminal section
on its own support; each cuff is a whole band sewn to that section (joints S9/S10), and the cuff
whose visible area is smaller is smaller because other cloth is in front of it, not because any
outline was shortened: with the pieces in front lifted, its authored area (331.5 px²) reappears
within 2 % (`tests/test_two_sleeves.py`).

**No manual clipping.** Nothing in `source/` declares a visible range or a back/front copy. Fills
come from `scripts/vector_visibility.visible_regions` over projected triangles, and lines are
depth-clipped sample-by-sample in `source/lines.py`; both are depth results.

**Authoring budget — the real counts.** Declared hand-typed coordinates per part, printed from the
built scene: `A-bow-ribbon` 4 (knot, two lobe tips, left tail exit), `A-hair-sheet` 5 (five crop
landmarks), `A-head-face` 3 (chin, two jaw corners), `A-collar-left` 3 and `A-collar-right` 3
(root, shoulder, edge), `A-bodice-upper` 2, each sleeve 1, and 0 for `A-derived-waist-band`,
`A-bodice-continuation`, both cuffs and `A-visible-neck-skin`. Everything else — lobes, folds,
tail routes, widths, section profiles, the hair route, the hair widths and twist, and all frame
coordinates — is generated. The hair's 15-station hand-typed route of v5 is gone.

## Files in this candidate

| path | what it is |
| --- | --- |
| `source/` | part library: `assemble.py` (scene + SVG), `build_a.py` (build entry point, enforces the seam contract), `seam_contract.py`, `lines.py`, `parts/` (one module per object family, `families.py` for generated relations) |
| `tests/` | 22 tests, `unittest`, plus the negative-control transcript |
| `artwork-a.svg` / `artwork-a.png` | the built SVG and its 1:1 render (400×480) |
| `check-a/` | the `scripts/draw check` bundle: `draft-fullres.png` (1:1, identical bytes to `artwork-a.png`), `draft.png`, `side-by-side.png`, three region crops, `report.txt` |
| `ref/` | the reference crop and four zoom crops used while authoring |
| `manifest.json`, `manifest.sha256` | the file set of this revision with its hashes |
| `repair-log.md` | per-defect disposition against D1–D12 |
| `work-checkpoint.md` | the killed run's checkpoint (kept as evidence; its "complete and hash-verified" claim was false and is superseded by this file and the manifest) |

## Commands actually run at this revision

```bash
PKG=.scratch/35-r1-articulated-study/evidence/A-cloth-v6

# tests (22)
python3 -m unittest discover -s tests -t .          # run from $PKG

# build (no reference input at any point)
python3 $PKG/source/build_a.py --out $PKG/artwork-a.svg --report $PKG/source/build-report.json
#   prints: faces 2018, parts 13, seams_total 18, seams_failed 0, visible_fill_regions 15

# the visual bundle, outdir inside this candidate
scripts/draw check $PKG/artwork-a.svg --ref $PKG/ref/crop-400x480.png --outdir $PKG/check-a
cp $PKG/check-a/draft-fullres.png $PKG/artwork-a.png

# reproducibility: two builds into separate paths, compared byte for byte
python3 $PKG/source/build_a.py --out /tmp/brep1/a.svg
python3 $PKG/source/build_a.py --out /tmp/brep2/a.svg
cmp /tmp/brep1/a.svg /tmp/brep2/a.svg && cmp /tmp/brep1/a.svg $PKG/artwork-a.svg
#   identical, sha256 d54bca51e8f0ff90847f300e1d9dbf24d4d2d882990e0354e3986d43c8284a98

# manifest
(cd $PKG && sha256sum -c manifest.sha256)
```

A note on the environment: this worktree has no `.venv` of its own; the interpreter used is the one
on `PATH` (`python3`, which carries cv2/numpy/Pillow/pyyaml). `scripts/draw` is run directly as a
shell script.

## Verified at this revision (writer-verified; not an art verdict)

- `build_a.py` exits 0 and prints `seams_failed: 0` for 18 declared joints; 13 parts, 2018 faces.
- 22 tests pass, including: every declared joint passes; a 4 px break fails and the restored build
  passes; a cuff on an unrelated support fails; both sleeves and both cuffs exist on four distinct
  supports; the cuff's authored area reappears when the front cloth is lifted; the hair has both
  side fills, they turn over in projection, its depth range exceeds 0.05 and its reverse side
  collapses when the twist is removed; the bow is one sheet of one width whose centreline visits
  the knot three times and both lobe tips; the object inventory covers every part exactly once;
  the authoring budget holds.
- Two builds into separate paths are byte-identical, and equal to the shipped `artwork-a.svg`.
- `sha256sum -c manifest.sha256` reports every listed file OK.
- `check-a/` exists with a 1:1 `draft-fullres.png` whose bytes equal `artwork-a.png`.

## Unverified / limits — stated, not softened

- **No art verdict.** Nobody has judged these images at this revision. `check-a/report.txt` lists
  the images for a fresh reviewer; the metrics in it (edge-F1 0.282, coverage 0.416) are a
  breakage alarm and nothing was tuned against them.
- **The second (left) cuff is fully occluded at this revision.** Its authored area is 331.5 px² and
  its visible area is 3.6e-12 px²; the bow (z 0.60) and the hair fall (z 0.45) are both in front of
  it. Wholeness and depth origin are proved by the ablation test, but the visible sliver v5 showed
  is absent from the image. Recorded under D1 in `repair-log.md`; not changed here because it is a
  drawing decision.
- **No hole test.** The dispatch asked for a test that the rendered PNG contains no
  background-coloured region enclosed by the hair silhouette. It does not exist, so "no background
  gaps inside the hair" is unverified.
- **No line-ownership test.** `assemble.mark_geometry` stamps every mark with a class and a source,
  and only draws declared semantic edges, but `tests/test_line_ownership.py` — the file
  `mark_geometry`'s docstring names — does not exist. The mechanism is present; the check is not.
- **No tangency negative control.** Only two negative controls run. The tangent clause is therefore
  still unproven against a rotation-only break and could be a no-op.
- **Dead code is still shipped.** `families.py` carries `folded_loop`, `gather_patch`,
  `ribbon_outline`, `tension_tail`, `_band_from_stations`, `hair_curlband` and
  `hair_shoulder_sheet`; `grep` finds no caller for any of them, and nothing was deleted.
- **The budget test counts the declared list.** `tests/test_identity.py` checks
  `len(part.authored)`, i.e. what the builder says about itself; the per-part counts above were
  read off the code separately, but no test proves declared == actual.
- Reference-pixel facts that a reviewer might check (bow lobe silhouettes, hair fold positions, the
  head's landmarks) are authored hypotheses chosen while the crop was open, not traced: the build
  reads no image, and `image.jpg` was not read for any geometry in this repair pass.
- Interpenetration of the support surfaces was not inspected as a gate. Declared contacts are the
  joint list above; nothing checks physical overlap beyond those depth relations.
- The two collar leaves are generated in the shared plane and stored in local frames (a coordinated
  pair cannot be authored twice without breaking the shared front seam). Every other part is
  generated in its own local frame.
