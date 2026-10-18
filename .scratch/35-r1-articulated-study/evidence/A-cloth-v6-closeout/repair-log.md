# Repair log — A-cloth-v6 against the wave-3 defects D1–D12

Source of the defects: `.scratch/35-r1-articulated-study/work/wave3-a-repair.js`.
Every disposition below was read off the code and the build at this revision (2026-10-18), not
off `work-checkpoint.md`; the checkpoint's claim that the package was complete and hash-verified
was false at HEAD (the `check-a/` bundle was missing and ten `source/*.py` hashes did not match),
and this log records what is actually true now.

Verdict vocabulary: **fixed** = the code at this revision does the thing and a test or a printed
build fact shows it; **partial** = the mechanism exists but a required half of the fix (usually
its distinguishing test) is missing; **not fixed** = the code still has the defect.

| id | disposition | what the code actually does at this revision |
| --- | --- | --- |
| D1 bust readability | **partial** | A head boundary now exists: `source/parts/head.py` builds `A-head-face`, whose top boundary is a labelled frame-cut closure and whose lower boundary is the generated jaw relation (`families.jaw_section`, shared with the neck). `A-visible-neck-skin` is bounded by that jaw above and by the collar opening relation at `Q` below, so it tapers instead of running as a column to the frame. Waist band and skirt continuation (`A-derived-waist-band`, `A-bodice-continuation`) and both sleeves exist. Whether the delivered image *reads* as a bust is an art judgement and is not recorded here — no reviewer has seen this revision. One measured regression: the second (left) cuff is now **entirely** occluded (visible area 3.6e-12 px², the bow at z 0.60 and the hair fall at z 0.45 sit in front of it), so the small visible cuff of v5 is gone from the image. |
| D2 bow does not resolve | **partial** | The knot now reads as a crossing rather than a tie-rule artefact: the strip passes through the knot three times (`bow.py` `_bridge`/`through_knot_*`), the three passes sit at distinct depths, and the crease inventory is three short curves that cross the turning fold of each lobe and the wrap at the tie (`bow.py` `_marks`, 8 samples each, ~0.7 of one piece's parameter span). The whole-limb chord marks of v5 are gone by construction: no mark is built from a limb's spine. Lobe-boundary curvature is unchanged from v5 and is an art question. |
| D3 hair as paper ribbon | **partial** | Taper and width variation are real: `hair.WIDTH_TIP = 3.0` against `WIDTH_MAX = 40.0` with `half_width(t)` a sine profile, so the terminal is a taper, not a square cut; `_curl` adds a lateral bend at the shoulder. Background holes inside the hair silhouette were **not** tested at this revision: the required hole test does not exist in `tests/` and was not added. Treat "no background gaps inside the hair" as unverified. |
| D4 stray meaningless marks | **partial** | Every emitted mark now carries a semantic class and a named source: `assemble.mark_geometry` only draws an `Edge` whose type is a `LINE_POLICY` key, and stamps each path with `data-class`, `owner` and `source` in the SVG comments. But the required `tests/test_line_ownership.py` (named in `assemble.mark_geometry`'s docstring) **does not exist**, so line ownership is a mechanism without a check. |
| D5 inconsistent ink | **fixed** | One policy by semantic class: `assemble.LINE_POLICY` maps `silhouette`, `free_edge`, `contact`, `fold_edge`, `trim` to one colour and one width each, and `render_svg` reads it — no part sets its own ink. |
| D6 composition | **partial** | The hair route is now five crop landmarks plus a generated catmull (`hair.py` `_base_route`), with the crown crossing above the frame; this is a different distribution of mass than v5's two full-height strips. Whether it recovers the reference's composition is an art judgement and is not claimed. |
| D7 hair "twisting normal" unimplemented | **fixed** (mechanism) | `hair.py:124` passes `twist=twist` to `StripSurface`; `hair.twist(t)` is a quarter turn across `TWIST_START..TWIST_SPAN`, and `frames.StripSurface.point` applies **one angle per station to both edges** (`cos(ang)` on the offset, `sin(ang)·DEPTH_PER_UNIT` on depth), so all columns of a station turn together — a real twist, not a per-sample artefact. The mint region is the reverse side of that turn, not self-overlap: measured, the authored sheet has 312 reverse-side faces and with `twist(t) = 0` only 12. `tests/test_hair_two_sided.py::test_the_twist_is_what_turns_the_sheet_over` asserts exactly that ratio. |
| D8 authoring budget | **partial** | The 15-station hand-typed hair route is gone: five crop landmarks (`LEFT_TIP_XY`, `LEFT_BULGE_XY`, `CROWN_XY`, `RIGHT_SHOULDER_XY`, `RIGHT_TIP_XY`), everything else generated (catmull route, sine width, depth curve, twist). Declared hand-typed coordinates per part, measured: bow 4, hair 5, head 3, collar 3+3, bodice-upper 2, sleeves 1+1, cuffs/band/continuation/neck 0 — all within the ~4-per-shape rule (hair's 5 is the sheet's sheet-wide budget the test allows). **Not closed:** `tests/test_identity.py::test_authoring_budget_per_part` still counts `part.authored`, i.e. the list the builder declares about itself, so "declared == actual" is not independently proved; only the code reading above supports it. |
| D9 seam-contract overstatement | **fixed** | Code and text now agree: `seam_contract.check` boundary-checks only `kind == "seam"`, and the docstring, `NON_JOINTS` and README all say an attachment compares position and layering only. Completeness is enforced: `NON_JOINTS` accounts for the two anchors that are not joints (`A-head-face.chin`, `A-bow-ribbon.knot`) and `tests/test_seam_contract.py` fails if a declared anchor appears in neither a `Joint` nor `NON_JOINTS`. |
| D10 no tangency negative control | **not fixed** | Only two negative controls exist (`test_negative_control_breaks_a_joint_then_restores_it` translates a leaf 4 px; `test_negative_control_detects_an_unrelated_support` lifts a cuff 0.5 in depth). The third required control — rotate one leaf about its own anchor so the boundary stays coincident and the tangent rotates, then assert the seam fails — was not written, so the tangent clause is still unproven against a no-op. |
| D11 dead code | **not fixed** | `source/parts/families.py` still carries `folded_loop` (454), `gather_patch` (476), `ribbon_outline` (483), `tension_tail` (491), `_band_from_stations` (529), `hair_curlband` (545) and `hair_shoulder_sheet` (546). Reachability evidence: `grep -rn` over `source/` and `tests/` finds no caller for any of them; `ribbon_outline` is called only by the four dead wrappers above. Nothing was deleted at this revision. |
| D12 knot passes at one depth | **fixed** | `bow.py:116-131` gives each of the three knot passes its own depth band separated by `CLOTH_THICKNESS`, with the comment stating that equal depths would let the visibility tie rule decide the front layer. |

## What this revision changed, and why

Work resumed from a killed run whose tree did not build (`python3 -m unittest` errored twice, and
`source/build_a.py` could not render). Three changes were made, all inside this directory:

1. `families.neck_skin` produced a **self-intersecting** contour. The neck is bounded by the jaw
   relation above and by the collar opening at `Q` below, but the collar's inner edge hugs the jaw
   relation to within about half a pixel there, so the straight path from the right collar root to
   `Q` crossed the jaw and the polygon inverted. The hidden boundary now goes round the jaw's right
   end (`NECK_WRAP = 8.0`, a generated clearance) instead. That wrap lies behind the collar leaves,
   which are layered in front of the skin (joints S4/S5), so it is not visible and carries no ink
   edge. The five boundary stations the seam contract reads (`R_left`, `Q`, `R_right`, `jaw_left`,
   `jaw_right`) are unchanged, so all 18 joints still pass.
2. `tests/test_two_sleeves.py` stated the second cuff's depth result as "remove **the bow** and the
   cuff grows 1.5×". That was false at this revision — the bow *and* the hair hide the cuff, so the
   ablation left it hidden and the test failed on 0-vs-0 slivers. The ablation now lifts every named
   piece in front of the cuff (bow, hair) and additionally asserts that the shape which reappears is
   the authored outline within 2 %. The property is unchanged and stricter; the honest consequence,
   that the cuff currently has no surviving visible extent, is recorded above under D1.
3. `tests/negative-control-output.txt` was regenerated: it recorded "16 declared joints" while the
   build now reports 18, so the transcript was stale evidence. `tests/test_hair_two_sided.py`
   gained the twist-vs-no-twist test that D7 asked for.

## Still open (not attempted here)

- D3 hole test, D4 line-ownership test, D10 tangency negative control, D11 dead-code deletion,
  D8 declared-vs-actual budget proof.
- Nothing about the image reads as a verdict. `check-a/` bundles the images and the breakage alarm;
  an independent reviewer decides whether the drawing reads as a clothed bust with a bow.

## Known regression at this revision

The left (second) cuff is entirely behind the bow and the hair fall: `visible_area` 3.6e-12 px²
against an authored 331.5 px². Its wholeness and its depth origin are proved
(`tests/test_two_sleeves.py`), but the visible sliver v5 showed is not present. Whether that is
acceptable is a drawing decision, not a package decision, so it was not changed here.
