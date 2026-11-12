# Independent public-CLI usability review

2026-11-12. Read only `skills/drawing-studio/SKILL.md` and CLI help before executing; no source, reference, existing artwork or previous evidence consulted. No generated JSON/SVG manually edited. This is bounded operation and visual feedback evidence, not general expression capability or whole-artwork acceptance.

## Result

The documented loop was independently executable without intervention. Default, preview, selection and undo images were actually opened. Expression selection highlights both brows, eyelids and mouth, covering the visible changed parts; eyes selection covers both eye openings where gaze changes. The normal smile image visibly raises/curves brows, narrows the eyelids into smiling arcs and deepens/widens the upturned mouth. These changes read together as a happier expression than the default. Face outline, hair and nose appear stable.

For gaze=1, visible brown iris fragments move toward screen right together and remain inside the eye slits; no obvious escape outside the opening is visible. Artistic limitation: smile closes the eyes so far that pupils are largely hidden and gaze is subtle at native size. Closeup comparison makes the common direction easier to read, but the result is not a strong clearly directed glance. The brows are also partly hidden by fringe on screen right. No operation blocker occurred; silent processes sometimes required polling the same session for tens of seconds.

Both previews were accepted only after viewing. Undo returned the exact smile revision `6f9fd7b9d973b55a15000465765ba3e963cb6f6df2be33f439d1113115186aaf`; re-inspected normal artwork SHA256 equals smile-preview: `64a9817fcbedcb0d38436948c709f7fdcb9b7225171d36b3a41547ef18a6d90b`. All launched sessions finished with exit 0.

## Commands

Run at repository root with `.venv/Scripts/python.exe`; below `CLI` means `.venv/Scripts/python.exe -m scripts.studio`, and `U` means `evidence/studio-expression/usability` (substitute literally).

```text
CLI --help
CLI new U/scene.json --kind head
CLI inspect U/scene.json --feature expression --outdir U/default-expression
CLI preview U/scene.json --selection U/default-expression/selection.json --set expression --value smile --reason "A happier face should lift the mouth corners and soften the eyelids and brows together" --outdir U/smile-preview
CLI accept U/scene.json U/smile-preview/candidate.json
CLI inspect U/scene.json --feature eyes --outdir U/smile-eyes
CLI preview U/scene.json --selection U/smile-eyes/selection.json --set gaze --value 1 --reason "The smiling character should glance toward the head right with both eyes together" --outdir U/gaze-preview
CLI accept U/scene.json U/gaze-preview/candidate.json
CLI undo U/scene.json
CLI inspect U/scene.json --feature expression --outdir U/undo-expression
Get-FileHash U/smile-preview/artwork.png,U/undo-expression/artwork.png
```

Viewed `artwork.png`, `alignment.png`, `edit-closeup.png` in default-expression, smile-preview and gaze-preview; viewed smile-eyes/edit-closeup.png and undo-expression/artwork.png. Default revision: `44fe01cc53e9492e9f310d86d694348b483dcf19421006023be78fd1129194e6`; gaze revision: `fe250e0e4aae6d86eaf6ee142ada05ee517e4ea2ad872575985982c15c643c16`. Engine reported throughout: `5dccffe058decf40f5eed804a9a622917d3ac640fcb0d3af71f03251334ba380`.
