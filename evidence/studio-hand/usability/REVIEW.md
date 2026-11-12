# Independent hand creation and usability review

Date: 2026-11-13. Frozen implementation fingerprint: e70aab5f818eac7be1b95af6f6fa8e3e20fe0978cd39beb835951ad1f801df36.

## Outcome and scope

Created a wordless greeting asset through public Studio commands alone: a blue-haired smiling avatar on the left and a smaller right-hand open-palm icon, tilted -16 degrees, on the right. The paper gap deliberately makes these two sticker components; no arm attachment or complete body is claimed. Final scene: `greeting.json`, revision `5148750bfb5b5115e98b242d2d16a3d8381d8de526c926e56244aecf1f53046f`. Final real image: `18-final-reinspect/artwork.png`; final check bundle: `check-final/`.

No source code, older artwork/evidence, reference image or sealed brief was consulted. Authoring used no manual JSON/SVG changes. Read the drawing-studio skill, interface documentation and Studio command documentation/help. This report is the creator's operation assessment, not independent whole-artwork acceptance or natural-anatomy validation.

## Actual visual decisions

- `00-default`: viewed clean artwork and index alignment before any edit. Five separated digits, opposed thumb and palm crease grouping read immediately as a front-view open cartoon hand. Minimum usable as an icon without rebuilding its base. The long palm, fairly uniform tubular fingers and straight wrist cut are stylizations; this does not establish a natural anatomical hand or a general hand rig.
- `02-hand-size`: saw the .42 hand on the chosen 800x640 pale green paper; accepted the smaller scale to leave room for a portrait.
- `04-hand-tilt`: saw and accepted -16 degrees, opening the fingers toward the outside of the eventual composition.
- `05-tilted-index` and `06-index-left`: viewed the before alignment, preview alignment and clean result. A screen-left .04 move nudges the white index tip left despite the tilt. The green knuckle stays visually fixed; middle/ring/little/thumb and the palm grouping stay visually stable. The pink prior guide makes the small tip displacement understandable. The small extra spread offers little benefit at asset size, so this preview was deliberately NOT accepted. Its candidate remains as evidence. This is visual stability evidence, not a proof of exact pixel identity.
- `08-hand-right`: accepted rightward .27 canvas-short-side translation for the separate hand sticker.
- `09-added-head`: viewed the stock head in context. It was too large and overlapped the hand; no attempt was made to disguise that as attachment.
- `10-head-left`: moved head left .14; viewed result. It improved grouping but hair still crowded the thumb. Accepted as an intermediate placement.
- `12-head-size`: viewed and accepted .46 length, opening a visible gap between hair and thumb.
- `14-head-down`: viewed and accepted .06 downward translation, bringing the face beside the palm and roughly aligning cutout bottoms.
- `16-smile`: viewed and accepted smile. The mouth reads more welcoming; the coordinated narrowed lids remain a conspicuous style choice rather than a guarantee of natural emotion.
- `18-final-reinspect`: viewed the final clean image and expression overlay. Viewed both final check full-resolution and 256px layout images. All five fingers remain readable at reduced size. No additional finger tweak was needed.

## Tool usefulness and limitations

The existing hand primitive was minimally practical for this brief. Object size/tilt/translation plus finger-tip screen motion let a creator make and assess a small greeting composition without coordinates, source changes or hand rebuilding. Orange/pink guides, a white tip and a green knuckle were useful when actually seen. The finger preview need not be retained to demonstrate the capability.

The selected pose is restricted to a front-facing open palm, with no finger curling, hand turn or arm attachment. Those limitations do not block the requested separated-sticker composition. More varied knuckle shapes, palm proportions, crease styling, face expression and export transparency would be polish or expanded scope here, not necessary repairs to make this asset readable. The supplied paper is intentional; transparent export was not attempted.

One real output issue occurred: `17-final/artwork.png` was a blank pale background although inspect reported ready, and `17-final/object-closeup.png` visibly contained the complete head and hand. The first `check/` correctly bundled that blank input. A fresh public inspect into `18-final-reinspect/`, without scene or source edits, produced the complete clean image for the same revision. `check-final/` then preserved that complete image. These failure files remain intact. This is a reliability concern for ready/image validity; no cause is asserted and no environment repair was attempted.

Inspect and preview briefly exceeded the command timeout at the expression stage. Existing sessions 26256 and 84385 were drained to exit 0; no processes were intentionally left running. All other started commands also exited. Source remained untouched.

## Reproducible command record

Run from `D:/vibe/learn_draw_studio`, with `.venv/Scripts/python.exe`. Below `S` is only a readable abbreviation for `evidence/studio-hand/usability/`; use the full path in execution. All inspect/preview commands completed with ready PNGs except the visually invalid normal image noted above. All mutations/checks exited 0. Help inspected: `-m scripts.studio --help`, `new --help`, `add --help`.

```text
-m scripts.studio new S/greeting.json --kind hand --id wave --size 800x640 --background '#eef3f1'
-m scripts.studio inspect S/greeting.json --feature index --outdir S/00-default
-m scripts.studio inspect S/greeting.json --feature object --outdir S/01-hand-object
-m scripts.studio preview S/greeting.json --selection S/01-hand-object/selection.json --set length --value .42 --reason 'Let the greeting hand accompany the portrait instead of dominating it' --outdir S/02-hand-size
-m scripts.studio accept S/greeting.json S/02-hand-size/candidate.json
-m scripts.studio inspect S/greeting.json --feature object --outdir S/03-size-inspect
-m scripts.studio preview S/greeting.json --selection S/03-size-inspect/selection.json --set angle --value -16 --reason 'Open the fingers outward to make the raised hand feel like a wave' --outdir S/04-hand-tilt
-m scripts.studio accept S/greeting.json S/04-hand-tilt/candidate.json
-m scripts.studio inspect S/greeting.json --feature index --outdir S/05-tilted-index
-m scripts.studio preview S/greeting.json --selection S/05-tilted-index/selection.json --move left --amount .04 --reason 'Ease the index tip toward the viewer left while preserving the knuckle and other fingers' --outdir S/06-index-left
# 06-index-left deliberately discarded, never accepted
-m scripts.studio inspect S/greeting.json --feature object --outdir S/07-hand-position
-m scripts.studio preview S/greeting.json --selection S/07-hand-position/selection.json --move right --amount .27 --reason 'Reserve the left area for the avatar and keep the hand as a separate greeting sticker' --outdir S/08-hand-right
-m scripts.studio accept S/greeting.json S/08-hand-right/candidate.json
-m scripts.studio add S/greeting.json --kind head --id friend
-m scripts.studio inspect S/greeting.json --object friend --feature object --outdir S/09-added-head
-m scripts.studio preview S/greeting.json --selection S/09-added-head/selection.json --move left --amount .14 --reason 'Separate the face and waving hand with clear paper between the sticker silhouettes' --outdir S/10-head-left
-m scripts.studio accept S/greeting.json S/10-head-left/candidate.json
-m scripts.studio inspect S/greeting.json --object friend --feature object --outdir S/11-head-object
-m scripts.studio preview S/greeting.json --selection S/11-head-object/selection.json --set length --value .46 --reason 'Reduce the avatar mass to clear the thumb and let both stickers breathe' --outdir S/12-head-size
-m scripts.studio accept S/greeting.json S/12-head-size/candidate.json
-m scripts.studio inspect S/greeting.json --object friend --feature object --outdir S/13-head-position
-m scripts.studio preview S/greeting.json --selection S/13-head-position/selection.json --move down --amount .06 --reason 'Align the two cutout bottoms and bring the face beside the lifted palm' --outdir S/14-head-down
-m scripts.studio accept S/greeting.json S/14-head-down/candidate.json
-m scripts.studio inspect S/greeting.json --object friend --feature expression --outdir S/15-expression
-m scripts.studio preview S/greeting.json --selection S/15-expression/selection.json --set expression --value smile --reason 'Give the greeting face a more legible welcoming smile' --outdir S/16-smile
-m scripts.studio accept S/greeting.json S/16-smile/candidate.json
-m scripts.studio inspect S/greeting.json --object wave --feature object --outdir S/17-final
scripts/draw.py check S/17-final/artwork.png --outdir S/check
-m scripts.studio inspect S/greeting.json --object friend --feature expression --outdir S/18-final-reinspect
scripts/draw.py check S/18-final-reinspect/artwork.png --outdir S/check-final
```

Final check emitted `draft-fullres.png`, `draft.png` and `report.txt`, with no reference metrics (original, reference-free composition). It supplies review inputs, not an art verdict. No baseline promotion or completion claim beyond this bounded usability exercise.

## Correction following independent file verification

The blank display recorded above was an observed viewing result, not established renderer corruption. The lead reviewer subsequently verified that `16-smile`, `17-final` and `18-final-reinspect` have identical SVG files (SHA256 prefix `f78e57`) and identical PNG files (SHA256 prefix `d88368`, 41,019 bytes). The two check full-resolution images are also byte-identical to each other. Pillow decoding found the four compared images pixel-identical in RGBA, containing 751 colours and the complete avatar/hand artwork. The lead reviewer directly viewed `17-final` successfully, while also observing a blank display for a check RGB image. These existing files therefore do not demonstrate damaged render output. The cause of the inconsistent display remains undetermined; no attribution to the model or renderer is justified. The original observation and all artifacts remain preserved; no image, scene or source was changed for this correction.
