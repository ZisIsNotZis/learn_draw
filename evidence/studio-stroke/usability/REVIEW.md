# Independent CLI usability attempt ¡ª friendly waving bust

## Result and boundary

Created an original cream-paper, plum-haired, teal-jacket bust with a smiling semantic head and a small raised semantic hand. The public CLI completed without source changes, direct scene editing, model imports, GPU, browser, or generated imagery. The final scene is `working.json`; the final exported scene and clean raster are `final/scene.json` and `final/artwork.png`. `check/report.txt` is the final check bundle. The final scene revision is `b7eea264b3257d58f273695ba9b2a5842ebfffb43799a54d135787b941e0cd9d` and the frozen engine fingerprint is `82dabe2b229d2e0350c157949400c5960d09a0d8695c60e5d3b9bb06d892bb26`.

This is a creator's usability report, not a whole-artwork acceptance verdict. `draw check` passed its export operation; it reports no comparison metrics because this original scene has no reference. Independent fresh-context artwork review and the person's gate remain outstanding. Source freeze is released; nothing remains running.

## What was actually exercised

- Head object sizing, expression, palette, depth, and placement; a generic jacket shape; neck and sleeve strokes; semantic hand sizing and placement.
- A neck root mounted to the actual head chin. Both source and target alignment PNGs were viewed before proposing the relation; clean artwork and overlay were viewed before accepting `neck-attached`.
- A sleeve root mounted to the explicitly inspected jacket `right@.2` shoulder. `sleeve-root/alignment.png`, `shoulder/alignment.png`, and `shoulder/edit-closeup.png` were viewed before the proposal. `shoulder-attached` clean artwork and overlay were viewed before acceptance.
- The hand wrist mounted to the sleeve tip after viewing both current alignment PNGs. `wrist-attached` clean artwork and overlay were viewed before acceptance.
- After composition, moved the free sleeve terminal upward by .055 canvas units with its root pinned. The attached hand followed, while the shoulder remained fixed. Viewed the terminal selection overlay and resulting clean artwork/overlay before accepting `cuff-raised`. This proposal made the wave visibly higher and reduced the sideways-arm reading, so I accepted it. The selection overlay was opened after making this proposal rather than before it; this is a sequencing deviation from the skill's preferred inspect/read/propose loop, though both attachment inspections always preceded their proposals.
- Shortened the initial long skin-coloured neck stroke into a shallow neckline; inspected both clean artwork and overlay before acceptance.

## Declined or failed attempts

- `head-raised`: an upward .16 move clipped the hair at the canvas edge. Kept the candidate, declined it, and accepted a .07 proposal instead.
- `jacket-low`: a downward .34 move clipped the jacket hem. Kept the candidate, declined it, and accepted .23 instead.
- First `wave-sized` proposal requested hand width .65. CLI refused it with `hand.width: must be between 0.75 and 1.3`; the successful proposal used .85. The refusal and subsequent success are both preserved in `commands.jsonl` even though they reused the same output directory name.

## Usability observations and limits

The inspected named mounts were legible enough to build a chin-neck and jacket-sleeve-hand chain without guessed path coordinates. Positioned shoulder addressing was discoverable from the supplied skill. Raising the free sleeve tip with its opposite end pinned was a useful concrete editing operation: it updated an already composed gesture and its hand descendant without redoing either attachment.

The main friction was repeated inspect/preview/view/accept for each individual sizing or placement adjustment. Object movement accepts a single direction, so a two-axis relocation needs separate revisions. The hand width limit was understandable only after attempting the value; the error was clear and did not block recovery. A few CPU render commands returned terminal session IDs and took tens of seconds; I polled each to completion before the next mutation.

The available controls readily make a friendly flat icon-like figure. They do not establish anatomical volume, natural clothing construction, or expressive body mechanics. The sleeve remains a broad smooth gesture, the hand line treatment is much finer than the face/hair, the head is large relative to the body, and the neckline is an abstract shallow rectangle. These are material limits of this attempt; I did not convert a mechanically valid attachment into a claim of finished illustration quality. The stock head's long hair and wide face also constrain how much visible shoulder/neck can be achieved through these few operations. I stopped at a coherent bounded attempt instead of decorating around those unresolved quality questions.

## Provenance

Read only `skills/drawing-studio/SKILL.md`, public CLI help, and this attempt's generated outputs. Did not read source, tests, prior scenes/images, or project docs. `run.py` wraps public CLI calls and appends exact argv, exit codes and raw combined stdout/stderr to `commands.jsonl`; `check-run.py` similarly preserves the check command in `check-command.json`. They do not import drawing models or patch scene data. The three setup/help shell calls before logging are transcribed in `initial-commands.txt`.

All ownership stayed within `evidence/studio-stroke/usability/`. No source, skill, baseline, or third-party files were modified. No additional agents were used. Final clean image absolute path: `D:/vibe/learn_draw_studio/evidence/studio-stroke/usability/final/artwork.png`.
`skill-read-snapshot.md` preserves the read skill text. The three CLI help calls were replayed through the logger after completion so their complete raw output is also preserved in `commands.jsonl`.
