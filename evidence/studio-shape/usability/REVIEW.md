# Independent shape creation and usability review

2026-11-13. Worktree: D:/vibe/learn_draw_studio. Interpreter: .venv/Scripts/python.exe. Frozen implementation fingerprint: `32635f2c63cec2e190bd8e18fe5258eef2c121a0a41381ed4bd38587c5e854dd`.

## Result

A bounded original warm, restrained flat icon of a desk lamp beside a closed book was constructed with seven named generic shape objects. Canvas 900x600 (3:2), cream paper, warm brown metal, amber shade, muted green cover, warm cream pages and one quiet page separation. Final scene `lamp-book.json`; final scene revision `271c2afa14ba336bcf99ab5e0cb4c00e0762a658b40b4116bc8bf39a0f3027f3`; final real image `final/artwork.png`; reference-free draw-check bundle `check/`.

The simple defaults and controls are usable for this bounded flat composition. The lamp has a distinct low oval foot, upright, angled reach and broad-bottomed shade. The horizontal book has a heavier left spine, green covers above and below a page block, and an exposed right page edge. At the actual 256px check preview, the two silhouettes and restrained palette remain legible. This is a creator usability finding, not independent artwork acceptance, user taste acceptance, natural realism or general drawing mastery.

## Scope and method

Read only the permitted drawing-studio skill and public new/add/preview CLI help. No studio source, old scenes/images, tests, reports, external reference, or image generation was used. No scene JSON or SVG was manually edited. `operate.py` and `plans.py` are this review's local command wrappers and authored operation plan: they only invoke public Studio CLI commands through subprocess, and record full arguments, reasons, outputs and exit statuses in `commands.log`. They never inspect or modify scene internals. All scene changes were public new/add/preview/accept operations. Undo was not needed or exercised in this attempt.

The initial construction choices were grouped per component: each parameter operation received a fresh inspect selection and ready preview, then was accepted as construction; the completed component was actually viewed before proceeding to the next component. This does not claim every intermediate construction preview received a separate visual judgement.

## Actual image observations and decisions

1. `00-default/artwork.png`: actually viewed the plain rounded tan block. It is a useful neutral colour mass, with no accidental subject-specific detail. A low oval made a clean lamp foot; `lamp-base-07-preview` was viewed before building the upright.
2. `lamp-stem-06-preview`: viewed narrow brown upright seated in the foot. `lamp-arm-07-preview`: viewed the angled support and elbow. Generic rotated masses were sufficient for this deliberately flat support silhouette; this is overlap, not an articulated attachment system.
3. `lamp-shade-08-preview`: viewed an amber shade with narrow top, broad bottom and gentle corners. Its silhouette made the lamp readable without extra marks or glow. The arm enters the left part of the shade; the icon does not claim mechanical engineering detail.
4. `book-cover-07-preview`: viewed the green mass beside the lamp on their shared baseline. `book-pages-07-preview`: viewed cream inset pages, but the border on all four sides risked reading as a frame. Moved the page block right by .012 of the shorter canvas dimension to expose the right edge. Viewed `book-pages-00-preview` after that correction; the heavier left spine and open right edge improved the book reading.
5. Viewed `local-before/alignment.png` to confirm the selected shade bottom. Tried a .06 screen-up local push at .5/radius .3, intending to suggest a subtle open lip while preserving corners. Actually viewed `local-lip/artwork.png`, `alignment.png` and `edit-closeup.png`. The endpoints stayed visibly fixed and the centre lifted, with useful orange/current and pink/prior guides. However, the resulting wave looked like a scalloped fabric edge rather than an improvement to the quiet lamp silhouette. Deliberately discarded this candidate. It is NOT in the final scene. An operation working mechanically does not make its result useful.
6. Added one short low-contrast page separation. Viewed `page-seam-06-preview/artwork.png`; retained the cue because it helps the closed page block read without texture or lettering. The line is thicker than originally wanted because of the width limit below.
7. Viewed the final check's actual 256px preview and reopened the complete final pre-accept image. A contradictory blank display of `final/artwork.png` was investigated by SHA256, not interpreted as missing geometry: `final/artwork.png`, `page-seam-06-preview/artwork.png` and `check/draft-fullres.png` are byte-identical SHA256 `0103f189278697c4bc2f48964f276781a860d1e1a3fc6feaa74bd3ddb9cfbb2b`. Reopening the earlier identical image showed the complete lamp/book, as did the reduced check image. Cause of the inconsistent display is undetermined; the files do not establish renderer or model failure. No art was changed in response.

## Limitations and failures

- A genuinely thin long shape was refused: `shape.width: must be between 0.05 and 6` when requesting .008 for the page separator. This matters for generic line-like marks. Kept the tested implementation frozen and used width .05 with length .20, rotation 90 degrees and a low-contrast colour. The final separator is a broad quiet mark rather than the originally desired fine page line. It did not prevent a bounded usable icon, but constrains fine graphic authoring. The real refusal is in commands.log.
- The first wrapper invocation passed an operation list through nested command-line JSON quoting and failed before any Studio operation (`JSONDecodeError`). Changed only the review-owned wrapper interface to use a Python plan module; all artwork operations still use public Studio CLI. This is orchestration failure, not a Studio defect.
- One later page-edge operation reused the `book-pages-00-inspect/preview` directory and overwrote that initial intermediate directory. `commands.log` preserves both command sequences, and the key completed book page stage is still `book-pages-07-preview`. Final and local-edit evidence were not overwritten. This is a review wrapper naming limitation.
- The command interface requires many inspect/preview/accept invocations to compose several masses; the wrapper reduced orchestration work while retaining guards and logs. No bulk semantic component placement, attachment constraint or fine-line primitive was assumed.
- Default rounded block and oval profiles plus taper, aspect, rotation and colours were sufficient here. The front-facing book and simple shaded-lamp silhouette do not test perspective, true lighting, depth-sloped intersection, curved solids or realistic joints. Those are outside this bounded icon, not hidden successes.
- Temporary long command/session delays were handled by draining existing sessions, not launching duplicate mutations or repairing the environment. Sessions 37582, 66037, 67997, 20510, 83503, 4096 and 43939 all completed. No launched review processes remain running.

## Commands and completion evidence

`commands.log` is the authoritative full public command sequence for all wrapper-driven inspect/preview/accept/add operations, with literal reasons and observed results. `plans.py` records the chosen construction values; `operate.py` records how the CLI was called. The following direct commands supplement that log (all from the worktree, using the interpreter above):

```text
-m scripts.studio new evidence/studio-shape/usability/lamp-book.json --kind shape --id lamp-base --size 900x600 --background '#f5eddf'
-m scripts.studio inspect evidence/studio-shape/usability/lamp-book.json --object lamp-base --feature object --outdir evidence/studio-shape/usability/00-default
-m scripts.studio inspect evidence/studio-shape/usability/lamp-book.json --object lamp-shade --feature bottom --at .5 --radius .3 --outdir evidence/studio-shape/usability/local-before
-m scripts.studio preview evidence/studio-shape/usability/lamp-book.json --selection evidence/studio-shape/usability/local-before/selection.json --move up --amount .06 --reason 'Lift the middle of the shade lip into a subtle opening while retaining both corners' --outdir evidence/studio-shape/usability/local-lip
# local-lip deliberately not accepted
-m scripts.studio inspect evidence/studio-shape/usability/lamp-book.json --object lamp-shade --feature object --outdir evidence/studio-shape/usability/final
scripts/draw.py check evidence/studio-shape/usability/final/artwork.png --outdir evidence/studio-shape/usability/check
```

Final inspect returned ready using resvg-py-0.5.0-cpu. Draw check exited 0 and emitted draft-fullres.png, draft.png and report.txt; no reference metrics are applicable to this original composition. These are real review inputs, not a verdict. No baseline was promoted. Source stayed frozen and untouched throughout this review.
