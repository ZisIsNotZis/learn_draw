# Narrow independent recheck: balanced smile gaze

2026-11-12. Original usability evidence was left untouched. Copied its post-undo scene.json without editing JSON. No source or other samples read. Current engine `c7190958d6d9a6ffd0ff3a37bc72748371fedc196d5c39d99974cad4299b1c67`; base revision `6f9fd7b9d973b55a15000465765ba3e963cb6f6df2be33f439d1113115186aaf`, gaze preview revision `fe250e0e4aae6d86eaf6ee142ada05ee517e4ea2ad872575985982c15c643c16`.

Actual images opened: expression/artwork.png and edit-closeup.png; eyes/edit-closeup.png; gaze-preview/artwork.png and edit-closeup.png.

The earlier thin brown iris-fragment problem is materially improved. In the current normal smile, both brown irises and dark pupils are visible rather than being mostly concealed in narrow slits. Gaze=1 moves both pupils screen right together, visibly increasing white space to their left. The glance can now be read in the normal image as well as the closeup. No obvious iris/pupil escape beyond the eye opening is visible. The selected eyes cover the changed regions; expression selection includes brows, eyelids and mouth.

Remaining artistic limits: the shift is moderate rather than an emphatic side glance. The pupils sit near the lower lid and the irises remain vertically clipped by the smiling opening, so the eyes retain a half-lidded/relaxed quality. The image reads as a mild pleasant smile, less exuberantly squinting than the earlier version; part of the screen-right brow is still hidden by fringe. These are bounded observations on this one smile/gaze combination. Curious, other expressions, poses and whole-artwork quality were not reviewed or accepted. No accept/undo rerun was requested or performed.

Commands run at repository root (`CLI` = `.venv/Scripts/python.exe -m scripts.studio`; `U` = `evidence/studio-expression/usability-balanced`):

```text
New-Item -ItemType Directory -Force evidence/studio-expression/usability-balanced | Out-Null
Copy-Item -LiteralPath evidence/studio-expression/usability/scene.json -Destination evidence/studio-expression/usability-balanced/scene.json
CLI inspect U/scene.json --feature expression --outdir U/expression
CLI inspect U/scene.json --feature eyes --outdir U/eyes
CLI preview U/scene.json --selection U/eyes/selection.json --set gaze --value 1 --reason "Check that a smiling rightward glance remains readable with both pupils visible" --outdir U/gaze-preview
```

All launched CLI sessions completed with exit 0; no running process remains from this review.
