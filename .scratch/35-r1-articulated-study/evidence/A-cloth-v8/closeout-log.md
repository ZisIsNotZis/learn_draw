# Closeout log — A-cloth-v6-closeout against B1–B3 and N1–N7

Source of the defect list: an execution-verified independent review of `.scratch/35-r1-articulated-study/evidence/A-cloth-v6/`,
each item reproduced with a command.  This log records, per defect, what the code does at
this revision and the command output that shows it.  Directory scope: this package only;
`A-cloth-v6/` is untouched, and every other package, `scripts/`, `docs/` and `STATUS.md`
were read-only.

Verdict vocabulary: **fixed** = the code does the thing and a test or a printed build
fact shows it, with a mutation that fails before restoration; **partial** = the mechanism
is there but a named half is missing; **not fixed** = the defect is still present.

## Blocking defects

| id | disposition | what is true at this revision |
| --- | --- | --- |
| **B1** joint list incomplete, no completeness test | **fixed** | `seam_contract.unaccounted_anchors` returns four findings: declared anchors no joint reads and no reason excuses, `NON_JOINTS` entries with no reason, and inventory entries naming an anchor no part declares. `tests/test_anchor_inventory.py` (5 tests) holds it at zero, `source/build_a.py` prints it and exits non-zero. The two anchors the review named (`A-left-cuff.sleeve_seat`, `A-right-cuff.sleeve_seat`) were deleted, not excused: they pointed at the cuff frame's origin, which is the cuff's centre, not the sleeve's seat — the cuff is sewn at `contact_left`/`contact_right`, which *are* joints (S9/S10). Every text that claimed the missing test is corrected (README, `seam_contract` docstring, `NON_JOINTS` comment). Demonstration (block M1 of `tests/negative-control-output.txt`): re-adding the two anchors gives `anchors_declared 38`, two `ANCHOR UNACCOUNTED` lines, build exit 1, 2 failing tests; restoring gives `36 = 34 + 2 + 0` and a green suite. |
| **B2** tautological tests | **fixed** | `test_bow_width_is_continuous_through_the_knot` now measures the emitted grid: 121 rows, each spanning 34.000000 in 3D, the knot rows are rows of that same strip, both ends equal, every width finite. `test_second_cuff_is_authored_whole` now asserts the authored area is > 100 px² **and** the surviving area is < 1 % of it, so a cuff drawn small and a cuff nothing occludes both fail; `assertGreaterEqual(visible, 0.0)` is gone. Mutations (blocks M2, M2b, M3): a tapered width fails with "measured width varies by 13.600000", `HALF_WIDTH = nan` fails with "an emitted width is not a finite number" — the literal-based test could not fail on either — and lifting the second cuff to z 0.70 fails the occlusion assertion. Each passes again after `git checkout`. |
| **B3** declared authoring budget != actual | **fixed** | `bodice.authored_input_xy` now declares C0 as well as Cw and Eleft, so `A-bodice-upper.authored` is 3, which is what the code hand-types. The check is against the source, not the declaration: `source/authored.py` AST-scans every part module for two-number literal pairs and `tests/test_authoring_inventory.py` fails on any pair the inventory does not account for, on any part module it does not scan, and on any part whose declared `authored` list is not exactly its landmarks. `python3 source/authored.py` prints the per-part table: 49 hand-typed pairs over 9 modules, of which 24 are landmarks or shared stations and 25 are declared non-landmarks with a reason, leaving 0 unaccounted. |

## Non-blocking defects

| id | disposition | what is true at this revision |
| --- | --- | --- |
| **N1** two-sided fill uses one triangle's winding for both | **fixed** | `SheetPart.faces` paints each triangle from its own projected winding. `tests/test_fill_winding.py` asserts no face disagrees with its own winding, and its second test paints both triangles of every quad from the first triangle's winding and measures **48 of 1380** faces disagreeing (7 hair, 41 bow — the review's numbers), so the rule is not vacuous on this geometry. Mutation (block M4): restoring the shared fill fails the test; restoring the source passes it. |
| **N2** tangent clause has no discriminating power | **fixed as a declaration check, and said so** | Option taken: keep the clause, state plainly what it verifies, and add the missing third negative control. Measured first (that measurement is the reason the other option was rejected): all 16 seam tangents agree to ≤ 7e-15, and deriving each side's tangent from its own emitted outline instead would disagree by 3.6°–87.7°, with six seams over 40° (`S8-band-continuation` worst at 84.3°), because an outline is a sampled contour and its local chord at an anchor is not the seam. Rewriting the anchors from the outline would have changed the drawing, which this closeout may not do. So: `seam_contract`'s docstring and the README now say the clause verifies declaration consistency between two sides that name the same stations, `test_negative_control_rotated_tangent` rotates one leaf's declared direction by 30°, shows `S1-collar-front` failing with `tangent mismatch` and **no** `boundary gap`, then shows the restored build passing. Residual limit recorded: an outline that rotates about a static anchor is not detected. |
| **N3** dead code | **fixed** | Deleted from `families.py`: `folded_loop`, `gather_patch`, `ribbon_outline`, `tension_tail`, `_band_from_stations`, `hair_curlband`, `hair_shoulder_sheet`, and — forced by deleting `ribbon_outline`, their only remaining callers — `local_pink_band` and `anonymous_blue_band`, plus the unreachable `signed_area` and `point_in_polygon`. Reachability evidence: `grep -rn "\b<name>\b" source tests` returned **no** call site for each of the seven named functions and for the four extra ones (before deletion the only hits were `local_pink_band`/`anonymous_blue_band`/`_band_from_stations` calling `ribbon_outline`, and the two `hair_*` wrappers calling `_band_from_stations`); after deletion the same grep returns no reference at all, and the build and the rendered SVG are unchanged in face count (2018) and parts (13). Deletion is unconditional: no commented-out copy is kept, git history is the archive. |
| **N4** missing hole test and line-ownership test; dangling reference | **partial** | `tests/test_line_ownership.py` now exists (7 tests) and holds exactly what `assemble.py`'s comment claims: every emitted mark declares a class in `LINE_POLICY`, an owner that is a declared part, a source naming its geometry; every path on the SVG is a fill of a named part or a line of a known class; and two in-memory negative controls (an undeclared class, an undeclared owner) must raise. Moving the ownership stamp also exposed a false detail: sheet marks were stamped `owner=A` (the first hyphen-separated token), so the owner now comes from the mark's own declaration. **The hair-hole test is not fixed.** It was not written, and while measuring for it the delivered PNG was found to contain **two background-coloured regions fully enclosed by ink**: 1019 px at bbox (162,39,35,60) and 17 px at (243,82,5,10), both bordered almost entirely by `#2f3d47` silhouette ink. A hole test would therefore fail on the current drawing, and closing it means changing the drawing — out of scope for this closeout. Stopped and reported instead of writing a test the drawing cannot pass. |
| **N5** stale check bundle | **fixed** | `check-a/` was deleted and regenerated with the current `scripts/draw check`: `report.txt` now lists the 1:1 `draft-fullres.png` first with the "judge detail here" note, and carries the current protocol lines (1:1-only detail judging, no-verdict banner). `artwork-a.png` is a byte copy of `check-a/draft-fullres.png` (sha256 `2fef5e2b…37ef`). |
| **N6** `build_a.py` docstring points at v5 | **fixed** | The docstring now names this directory. It also says `python3` instead of `.venv/bin/python`, because this worktree has no `.venv` and `python3` is what runs. |
| **N7** knot pass 1 ties pass 2 in depth | **fixed** | `PIECE_DEPTH` now gives pass 1 the band `[0.600, 0.606]` (was `[0.600, 0.624]`, whose midpoint 0.612 equalled pass 2's flat band), pass 2 `0.618` and pass 3 `0.636`, so the three bands are at least one `CLOTH_THICKNESS` (0.012) apart over their whole spans. The ordering the tie used to break mid-station — pass 1 behind pass 2 behind pass 3 — now holds everywhere, which is a change of a few pixels in the knot and of nothing else. |

## Open items this closeout does not close

1. **Background holes inside the drawn silhouette (N4).**  Two enclosed background
   regions exist in the delivered PNG.  Closing them is a drawing change: either the hair
   route must reach the face boundary or the gap must be filled with cloth.  A reviewer
   or the user should decide which, and a hole test can be written the moment the drawing
   passes it.
2. **The second (left) cuff is fully occluded** (authored 331.5 px², visible ~3.6e-12 px²).
   The user's decision was "two sleeves, not one, the other one is not invisible, it's
   just small, partially covered".  The mechanism is proved (ablation test), the visible
   sliver is not there.  Unchanged here: it is a drawing decision.
3. **The tangent clause cannot see a rotated outline** (see N2).  Detecting it needs a
   generator-level boundary direction per anchor, which is a redesign of the anchor, not a
   closeout fix.
4. **Declared authored stations are stored in three representations** (crop pixels, plane
   coordinates, part-local coordinates).  The inventory test accepts any of the three; one
   spelling would be better and is a small future change.

## Claims audit — what the previous package said that was false, and how it now stands

| the false claim, and where it was | how it stands now |
| --- | --- |
| README, `repair-log.md` D9 and `seam_contract.py`'s comment: "`tests/test_seam_contract.py` fails a declared anchor that appears in neither a `Joint` nor `NON_JOINTS`, so the joint list is provably complete" | The test did not exist and two anchors were unaccounted. Now `tests/test_anchor_inventory.py` exists, the build refuses, and the text names the real file (`B1`). |
| README "22 tests, all passing" implying the suite distinguished success from failure | Two of the 22 could not fail on any input. Both are rewritten to measure delivered geometry, with mutations that fail and restore (`B2`). |
| README "Authoring budget — the real counts … `A-bodice-upper` 2" | The code hand-typed 3 (C0 was missing from the declaration). Now 3, and the count is checked against the source by AST (`B3`). |
| README "Declared hand-typed coordinates per part, printed from the built scene" (i.e. self-reported) | Replaced by a table cross-checked against the source text; the built scene's `authored` list must equal the inventory (`B3`). |
| `hair.py` lines 9–10 and `frames.py` docstring: "the fill of each face comes from its own projected winding" | False for 48 of 1380 faces (both triangles of a quad took the first triangle's fill). Now true and tested, with the 48-face measurement kept as the negative control (`N1`). |
| README: "a shared tangent direction within 1e-6 (parallel or antiparallel)" presented as a geometric check | The numbers come from two sides declaring the same direction, not from the outline. The clause is now described as declaration consistency and has its third control (`N2`). |
| README: "`NON_JOINTS` accounts for the two anchors that are deliberately not joints" and the joint table's "18 declared joints, all passing" | The two cuff anchors were in neither list, so the count was 36 anchors with 2 unaccounted. Both deleted, count now stated as 36 = 34 + 2 (`B1`). |
| README: "`tests/test_line_ownership.py` fails a mark that names neither its class nor its geometry" (comment in `assemble.py`) | The file did not exist. It exists now and holds the claim; the `owner` stamp is also fixed from `A` to the owning part (`N4`). |
| README "Unverified / limits" listing dead code, missing hole test, missing tangency control as open items | Dead code deleted and presence-checked (`N3`); tangency control added (`N2`); the hole test is still missing and the reason is now a measured fact about the image, not just an admission (`N4`). |
| `work-checkpoint.md`: "complete and hash-verified … No acceptance item is left unbuilt" | False at that revision (the bundle was missing and ten source hashes did not match). The file is removed here; this log and `README.md` supersede it, and the v6 copy keeps it in git. |

## Commands run, in order (this revision)

```bash
cd .scratch/35-r1-articulated-study/evidence/A-cloth-v6-closeout
python3 -m unittest discover -s tests -t .            # 44 tests, OK
python3 source/authored.py                            # per-part table, problems 0
python3 source/build_a.py --out artwork-a.svg --report source/build-report.json
scripts/draw check artwork-a.svg --ref ref/crop-400x480.png --outdir check-a
cp check-a/draft-fullres.png artwork-a.png
# reproducibility
python3 source/build_a.py --out /tmp/brep1/a.svg && python3 source/build_a.py --out /tmp/brep2/a.svg
cmp /tmp/brep1/a.svg /tmp/brep2/a.svg && cmp /tmp/brep1/a.svg artwork-a.svg
# mutations, one at a time, each restored (transcript: tests/negative-control-output.txt)
sha256sum -c manifest.sha256
```
