# A-full-figure-waist-r1 — bounded waist-section line cleanup

**Status: independently reviewed small-improvement candidate, not an overall art PASS.**
This revision weakens the unnecessary hard diagonal division above the waist. It does not
repair blouse volume, chest/shoulder-to-waist construction, or all remaining light traces.
The inherited hand, bow, hair and background issues remain out of scope. The person has
not accepted this candidate.

## What changed and why

The crop-library bodice is split into three generated sections on a shared support. In
this full-frame assembly those calculation sections retained a contrasting gray band,
two transverse fold-edge marks and a continuation contact mark, in addition to the
full-frame waist band. These made an internal construction section read as a second belt.
Only `source/full/figure.py` changes: it selects the same cloth material for the three
sections and omits those three transverse marks. No cover patch is added. All outlines,
frames, depths, anchors, longitudinal folds, real waist-band marks and non-bodice parts
are unchanged. `source/parts` is byte-for-byte frozen.

## Inspect actual images

- `artwork.png`: candidate whole image, 1024×1024.
- `check/whole-before-after.png`: baseline left / candidate right, same scale.
- `check/waist-before-after.png`: same crop and scale, baseline left / candidate right.
- `baseline/artwork.png`: CPU baseline rebuilt before edits.
- `check/candidate-diff.json`: 1834 changed pixels, bounding box [613,625,751,664).

Independent visual review relayed by Manager 2026-11-12 09:46: unnecessary waist-top
hard division reduced, no new silhouette/hair/hanging-ribbon damage noticed; light traces
remain, and body volume / shoulder-to-waist structure is still not solved. This is a
bounded observation, not an artwork acceptance or general drawing-skill claim.

## Reproduction and checks

Windows CPU interpreter used:
`D:/vibe/learn_draw/repair/cpu-venv/Scripts/python.exe` (Python 3.14.10,
numpy 2.5.4, Pillow 13.0.0). Geometry uses only numpy; PNG rendering uses Edge headless
with explicit `--disable-gpu`. User GPU pause is binding; no GPU task was launched.
CairoSVG was installed during environment setup but is not used by the reproduction.

From this package directory, using that interpreter (or equivalent numpy environment):

```
python reproduce.py
python tests/test_waist_continuity.py
python -m unittest discover -s tests -p test_full_figure.py
```

Three new discriminating tests pass: geometry/depth and all unrelated objects exactly
unchanged; old artificial-section semantics fail while candidate passes; frozen part
library bytes match. These tests do not assess art. All 9 inherited full-figure tests also pass (12 mechanical tests total); see VALIDATION.md. Repeated candidate SVG build and CPU PNG rendering are both byte-identical. Source, scripts and artifacts
are bound by `manifest.sha256`; original historical manifest is explicitly under baseline.

## Provenance and limitations

Baseline git commit: `1a72fe43393ba85abed46fc600c0ff9ad4bdc76e`.
`baseline/source` retains original source bytes before the single candidate.
Only minimal source/tests and two required project scripts were fetched, not old image
history. Old package was not written. Baseline PNG versus supplied original PNG differs
at 54 pixels, maximum channel delta 11, mean absolute channel delta 0.0000782; no pixel
exceeds delta 32. It is near-identical CPU reproduction, not pixel/byte equivalence.
Baseline SVG hash differs from the historical manifest; precise serialization/float-order
cause is unverified and no artistic equivalence is inferred from a hash. The actual PNG
comparison is recorded under `baseline/original-png-comparison.json`.
Historical review remains `baseline/review-log.md`, not current acceptance evidence.
No sealed brief read, no GPU used, no unrelated worktree deletions restored, no baseline
promotion or whole-tree commit made. Next action is Manager verification and evidence-based choice of the next bounded improvement.
