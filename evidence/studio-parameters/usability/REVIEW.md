# Grouped parameter creation/usability trial

2026-11-13. Independent creator; source frozen. Read only current drawing-studio skill and public preview help. No source/tests/old scenes/images/reports/reference or image generation. Scene edits were exclusively public CLI calls; `build.py` only constructs command argument lists and logs complete commands/results to `commands.log`. All outputs are CPU-rendered.

Intent: a warm flat toy-rocket emblem. Chose 640x640 cream paper, cream hull, brick-red nose and fins, dark brown rim/outline and blue round glass. Six generic named shape objects; no subject generator.

## Actual decisions

- Actually viewed `body-preview/artwork.png` before accepting the complete group: intent, length, width, rounding, taper, stroke and both colours. The tall softly rounded cream hull with quiet brown outline was useful.
- Tested one-step grouped undo immediately: accepted body, undid once, inspected `body-undone`. It restored the short stock tan mass, not a partially configured hull. Default `body-inspect/artwork.png` and undone image have identical SHA256 `6154977b9bb5546437ac101f5d0147f256d70acb720c5d8cce639366fb204b35`. Replayed the group into `body-replay`, actually viewed its complete image and accepted it.
- Viewed the complete red tapered nose group before accepting. The first screen-up placement `.19` left cream shoulders sticking out beside the cone (`nose-up-preview`); rejected that placement candidate. A fresh `.315` up preview seated the cap at the hull top and gave a clear pointed rocket silhouette; viewed and accepted `nose-seat-preview`. Both attempts remain intact.
- Viewed each complete fin group's alignment image before accepting: rotation, taper, size, flat red colour and intent together. Fins initially lay behind the opaque hull, so alignment was needed to see their configured contours. Viewed and accepted each successive horizontal and downward move. Final two fins flank the lower hull; depth keeps their buried roots behind it.
- Viewed the dark round porthole-rim group before accepting. The circular geometry and relative size were clear in the hull.

## What this establishes

Repeated --change configures a coherent component in one visible preview, with one reason and one accept/undo step. It avoids a series of half-configured colour/shape states and made this small original subject practical. The one-step undo was directly useful and exact at the displayed-image level. Every complete group was actually viewed before acceptance; no unseen auto-accept loop was used.

Placement remains separate screen-move operations; the group is one object's parameter decision, not a multi-object assembly or attachment constraint. Generic tapered shapes are sufficient for these simple fins/cap, not a general solid model. This is bounded creator usability evidence, not independent whole-artwork acceptance or general drawing mastery. No baseline promotion.

## Final delivery and limitations

The blue-glass group was actually viewed, then accepted. Final inspect and the check's 256px preview were viewed: the whole rocket reads clearly with a cream body, two red fins, pointed cap and circular blue porthole. Final files: `rocket.json`, `final/artwork.png`, `check/draft-fullres.png`, `check/draft.png`, and `check/report.txt`. Final/last-preview/check-fullres PNGs are byte-identical SHA256 `15781aad98961cea88a9fcedbb34d3dbbf5a2b81d4ca51b4451b45d583b4b423`. A transient last-preview display showed only the porthole region; reopening the identical final image showed the whole rocket. No scene change or renderer-failure conclusion followed that inconsistent display.

No CLI operation was refused in this trial. Waiting on the existing processes was sometimes slow (including the glass stage); all sessions were drained to exit 0, with no environment repair or duplicate mutation. All started processes have ended. Original previews, including the rejected nose placement, are preserved. Source and scene internals were untouched.

The cap/body joint retains the simple graphic seam of separate shapes, and the fin bottoms are stylized. These are bounded style/assembly choices, not claims of a complete rocket construction model. No flame or extra decoration was needed for the requested readable toy emblem. A drawing-quality verdict remains for a separate fresh-context picture review.

Full command arguments, grouped values, intents, reasons, revisions, renderer and SHA256 outputs are in `commands.log`; `build.py` is the replayable CLI-only plan. Direct final check command (exit 0):

```text
.venv/Scripts/python.exe scripts/draw.py check evidence/studio-parameters/usability/final/artwork.png --outdir evidence/studio-parameters/usability/check
```

The one grouped undo and replay, six part previews and rejected first nose placement establish a practical bounded authoring loop. The new --change option was useful here; it is not a whole-object placement group or cross-object rig. Trial complete; source freeze can be released.
