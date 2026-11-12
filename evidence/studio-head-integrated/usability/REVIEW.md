# Integrated head CLI execution usability review

2026-11-12. Bounded P36 execution-usability review, not another judgement of the default head's artistic merit.

## Inputs and independence

I read `skills/drawing-studio/SKILL.md` and the current Studio-1 section of `docs/7_INTERFACE.md`, then used only the public CLI, generated reports, and generated PNGs. I did not read source, sealed briefs, or historical pictures. All new artifacts are under this directory. No source was changed. Working directory throughout: `D:/vibe/learn_draw_studio`. Python: `.venv/Scripts/python.exe`.

## Exact execution sequence

All commands below exited 0; all inspect/preview responses reported ready. No undocumented assistance or manually authored scene/path coordinates were needed.

```powershell
.venv/Scripts/python.exe -m scripts.studio new evidence/studio-head-integrated/usability/scene.json --kind head
.venv/Scripts/python.exe -m scripts.studio inspect evidence/studio-head-integrated/usability/scene.json --feature eyes --outdir evidence/studio-head-integrated/usability/eyes
.venv/Scripts/python.exe -m scripts.studio preview evidence/studio-head-integrated/usability/scene.json --selection evidence/studio-head-integrated/usability/eyes/selection.json --set eye_scale --value .92 --reason "Quieter eye proportions while keeping the face ruler and hair fixed" --outdir evidence/studio-head-integrated/usability/eyes-preview
.venv/Scripts/python.exe -m scripts.studio accept evidence/studio-head-integrated/usability/scene.json evidence/studio-head-integrated/usability/eyes-preview/candidate.json
.venv/Scripts/python.exe -m scripts.studio inspect evidence/studio-head-integrated/usability/scene.json --feature left-lock --side left --at .55 --radius .30 --outdir evidence/studio-head-integrated/usability/lock
.venv/Scripts/python.exe -m scripts.studio preview evidence/studio-head-integrated/usability/scene.json --selection evidence/studio-head-integrated/usability/lock/selection.json --move left --amount .10 --reason "Give the screen-left outer hair edge a slightly fuller middle while preserving both tips and the opposite lock" --outdir evidence/studio-head-integrated/usability/lock-preview
.venv/Scripts/python.exe -m scripts.studio accept evidence/studio-head-integrated/usability/scene.json evidence/studio-head-integrated/usability/lock-preview/candidate.json
.venv/Scripts/python.exe -m scripts.studio inspect evidence/studio-head-integrated/usability/scene.json --feature left-lock --side left --at .55 --radius .30 --outdir evidence/studio-head-integrated/usability/accepted
.venv/Scripts/python.exe -m scripts.studio undo evidence/studio-head-integrated/usability/scene.json
.venv/Scripts/python.exe -m scripts.studio inspect evidence/studio-head-integrated/usability/scene.json --feature left-lock --side left --at .55 --radius .30 --outdir evidence/studio-head-integrated/usability/undone
```

## What was actually viewed

Directly viewed artwork and alignment for `eyes`, `eyes-preview`, `lock-preview`, and `undone`; also viewed `eyes/edit-closeup.png`, `lock/alignment.png`, `lock/edit-closeup.png`, `lock-preview/edit-closeup.png`, and `accepted/artwork.png`.

- Eyes alignment traces both eye apertures in orange; the enlarged crop is unambiguous. This selection names the intended paired feature rather than requiring the author to recover individual generated paths. Inspect's response lists `eye_scale` and `iris_color` as permitted controls.
- Semantic preview visibly reduces both eyes modestly. Face boundary, nose, mouth, brow positions, hair and framing appear fixed. This supports the intended local meaning in this example.
- The child selection clearly identifies the screen-left outer hair edge: orange marks the editable interior interval, a circle locates its centre, and separate green endpoint handles identify protected root/tip. The crop is particularly useful for distinguishing the outer edge from the nearby inner ink line.
- The local preview bulges this edge screen-left around its middle. Its orange current edge and dashed pink previous edge make the direction and small magnitude clear. The endpoint region and opposite lock appear fixed; facial features remain fixed. The normal artwork has no author handles.
- Accept produces the previewed change; undo removes only the local push and preserves the already accepted smaller eyes. No manual file correction was necessary.

## Revision and rendered evidence

Engine fingerprint: `b10cb13c660712f4d18e317c1fd64344a189350e13e5f9a8b5644eab53f279ce`; renderer `resvg-py-0.5.0-cpu`.

- New scene: `eb147fef4b80b94da4501b71fe001cbc3512cdd416ffcef3ba8acb48dff15d1c`.
- Accepted eyes: `52c760268dc438111bd3aa22772deb4465b0192e733d8cf4a08cf9788fb1a8e0`.
- Accepted local push: `9d98e68c43ecd266dc254c276ed0bd55255cb51c90e92a0d4ccf914f3016dd4c`.
- Undo returned `52c760268dc438111bd3aa22772deb4465b0192e733d8cf4a08cf9788fb1a8e0`.

Direct `Get-FileHash` verification agrees with generated reports: lock-preview and accepted normal artwork both SHA256 `ace6dcda01608aefc580ab073e2012fad7d44672008b77a85b5f479c26cfec8a`; pre-push lock and undone normal artwork both `fbcff424a948ce37b33079e9678761ab357f49a116c7a88b8667136c1554adfd`. This verifies rendered restoration in this frozen implementation, in addition to revision restoration.

## Verdict and limits

**The supplied public instructions independently support the bounded loop: default head -> semantic eye edit -> accept -> child-lock alignment -> local push -> accept -> undo. No execution or alignment blocker was observed.** The enlarged crop and old/new contour overlay make a subtle local operation inspectable. The documented distinction between root-to-tip edge names and screen movement is necessary; it was sufficient here.

Minor usability refinement: the overlay has no embedded textual legend identifying orange current contour versus pink previous contour or the endpoint handle colours. The geometry and before/after views made this example clear, so it did not block execution; a short legend would reduce inference for new callers.

This run tests one head, one eye setting, one lock side and one small horizontal push at zero head tilt. It does not test tilted heads, other hairstyles, refusal paths, stale/tampered candidates, multi-object selection, extreme moves, 3D attachment, general drawing ability, heldout transfer, or whole-artwork acceptance. The final scene intentionally retains the accepted eye edit and has the local push undone.

## Known next boundary

The current interface only implements head and hair-lock families. It exposes no public object-translation operation for composition; manually writing relative `at` values is a separate authoring path. A future object movement operation would close that composition gap. This review does not count that missing capability, or unimplemented object families, as passed.
