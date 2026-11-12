# Independent bounded studio transfer — two avatars

2026-11-12. The brief was a friendly science-community cover with two visibly different cartoon avatars, consistent style, clean negative space, and no text. This tests a limited tool/skill transfer, not general drawing ability or human aesthetic acceptance.

## Independence and method

Read only `skills/drawing-studio/SKILL.md`, the current studio portions of `docs/7_INTERFACE.md` and `docs/9_IMPLEMENTATION.md`, and public CLI help. Did not read source, previous artwork/evidence, a sealed brief, or portrait reference. The artwork was authored exclusively with `python -m scripts.studio`; no scene JSON, generated vertices, or SVG was manually edited. Source remained frozen throughout.

Chose a reversible square warm-paper composition: equal-size frontal avatars side by side, cool blue side-part hair on the left, copper bob and deeper warm skin on the right. Did not add scenic objects: they would compete with the two faces and the intended whitespace. Normal artwork and alignment were actually opened at the default, first size, left placement, inserted partner, partner size, separated pair, bob, copper, and skin checkpoints. Each accepted operation has the CLI candidate/report record. The intermediate insertions overlap; final placement separates both silhouettes.

## Commands and drawing reasons

All commands ran from the worktree with `.venv/Scripts/python.exe`. In the list below, `S` means `evidence/studio-transfer/two-avatars/scene.json`, and each view name is a subdirectory of that same evidence directory. These are shorthand for the actual CLI arguments, not a second input format.

1. `-m scripts.studio new S --kind head`; `inspect S --feature object --outdir 01-default` — establish the available frontal style.
2. `preview S --selection 01-default/selection.json --set length --value .36 --reason "Make room for two equal avatars and generous paper margins" --outdir 02-size`; accept candidate; inspect into `03-before-place`.
3. `preview S --selection 03-before-place/selection.json --move left --amount .235 --reason "Place the first avatar in the left half with space for a partner" --outdir 04-left`; accept candidate.
4. `add S --kind head --id partner`; `inspect S --object partner --feature object --outdir 05-partner`.
5. `preview S --selection 05-partner/selection.json --set length --value .36 --reason "Match the partner scale to the first equal community member" --outdir 06-partner-size`; accept candidate; inspect into `07-before-right`.
6. `preview S --selection 07-before-right/selection.json --move right --amount .235 --reason "Separate both silhouettes with a clean central gap" --outdir 08-right`; accept candidate; inspect partner hair into `09-hair`.
7. `preview S --selection 09-hair/selection.json --set hair --value bob --reason "Distinguish the partner through a rounded bob silhouette" --outdir 10-bob`; accept candidate; inspect partner hair into `11-color`.
8. `preview S --selection 11-color/selection.json --set hair_color --value '#b16e48' --reason "Give the second avatar warm copper hair against the first cool blue" --outdir 12-copper`; accept candidate; inspect partner face into `13-face`.
9. `preview S --selection 13-face/selection.json --set skin_color --value '#c99170' --reason "Distinguish the second member with a warmer deeper skin tone" --outdir 14-skin`; accept candidate.
10. `inspect S --object partner --feature object --outdir final` — final accepted scene record. Final check command and actual result are recorded below.

Every preview was accepted using `accept S VIEW/candidate.json`; inspection used the same selected object as the next preview. Reports bind revisions and the implementation fingerprint. Final accepted revision: `d28670436a588ace234a792c246bc9d6db8745a9bb4840c26b2106875b529912`. Engine fingerprint: `8220a432d4a0a72583bc85ba4ef21ea9b72573f396a683a4100855ec4d948381`. Renderer: `resvg-py-0.5.0-cpu`.

## Actual capability and limitations

The bounded composition, scale, placement, hairstyle and palette decisions were independently executable from the skill and public CLI. No developer intervention or lower-level redrawing was needed to generate the two-person artifact. This is composition and variation of one existing recipe, not invention of arbitrary head construction, expression, pose, clothing, or science-specific symbols. The bob changes the fringe while retaining a similar outer head/hair silhouette. The two faces share the recipe's facial expression and features; colour and fringe carry most differentiation.

Visible operation gap: after `hair_color` changed the partner to copper, one internal curved hair line remained blue. This survives in the final raw image. I did not bypass the gap or manually repaint it. General palette coherence needs an upstream operation correction; complete lower-level redrawing is not demonstrated to be necessary. Object intent text in reports also retains the default side-part description after the bob change; this is report/semantic consistency evidence, not an edited input.

The CLI exposes only the default square canvas through the new/add flow documented here; no supported canvas-format edit was discovered. A square cover is a reasonable reversible interpretation of the unspecified cover format. This trial does not establish landscape/banner delivery. Execution sometimes delayed output for tens of seconds; completed sessions were drained and successful reports used. No project fix was attempted for execution latency.

Final actual image: [final/artwork.png](final/artwork.png), with [alignment](final/alignment.png). Earlier raw checkpoints remain preserved. No claim of whole-artwork acceptance or human taste approval is made. A fresh-context reviewer must judge the check image list independently; this author has not promoted any baseline.

## Check result

Ran `.venv/Scripts/python.exe scripts/draw.py check evidence/studio-transfer/two-avatars/final/artwork.png --outdir evidence/studio-transfer/two-avatars/check`. Exit code 0. It produced `check/report.txt`, `check/draft-fullres.png` and `check/draft.png`. This is the original-artwork branch of the check, with no portrait metric comparison. Successful packaging is not an aesthetic verdict. Final studio inspection is ready and its artwork hash exactly matches the accepted `14-skin` preview: `86f915a52e2441aa17d91df11831d56ad119d779f2fd9bbccf19571eaf3b6fc1`.
