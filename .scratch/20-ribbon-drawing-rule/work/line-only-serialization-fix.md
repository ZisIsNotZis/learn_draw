# Inline SVG line-only serialization correction

## Cause and scope

Parent found the current line-only board PNG rendered as the single board-paper background color even though cached panels contained named ink paths. `work/build_cached.py::_panel_parts` used ElementTree's generated `ns0:` prefix when serializing SVG child elements. Those prefix-qualified tags did not render when placed inline in the board's HTML/SVG foreign-content parser. The direct drawing compiler itself emitted ordinary unprefixed SVG and had not lost ink.

The exporter now registers the default SVG namespace before serializing the ground/path children and rejects any remaining `<ns0:` tags in the generated board. No geometry, visibility, path selection, width, motif, sampling, panel cache, cases, or cameras changed. The valid 24-panel fit-corrected cache was reused; no geometry or colour panel was recompiled.

The broken line-only SVG/PNG boards and their prior `draw check` bundles are preserved at `evidence/before-line-serialization-fix/`. The directory `SHA256SUMS` hash is `b474767da38ff91cde678bd8949b4077394437977bba89eac1187adfaaa119ed`. They are invalid rendered evidence and must not be passed to a perception reviewer.

## Raster equivalence regression

A persistent test, `scripts.tests.test_ribbon_drawing.RibbonDrawingTests.test_cached_line_only_export_raster_matches_direct_external_card`, compiles the frozen support-card case under rule B, extracts its cached ink, renders the extracted panel and direct `render_panel(line_only=True)` with Chromium at identical 442×255 framing, then compares complete pixel arrays. It requires no prefixed namespace tags and a non-background raster. This small sampling test passed as part of the affected 46-test suite.

The export driver repeats the same browser raster comparison at the frozen 128 intervals before assembling boards. For external-support-card rule B, direct/export were 442×255, had exactly 0 differing pixels, and contained 2,551 non-background pixels. The corrected complete unlabelled line-only board PNG has 108 pixels exactly equal to the authored ink color `#253746`; it is no longer a background-only raster. Both are rendering-integrity checks, not visual-quality criteria.

## Export and current artifacts

Command:

```bash
.venv/bin/python .scratch/20-ribbon-drawing-rule/work/build_cached.py \
  --case-plan .scratch/20-ribbon-drawing-rule/work/cases.json \
  --out-dir .scratch/20-ribbon-drawing-rule/evidence \
  --progress .scratch/20-ribbon-drawing-rule/work/build-progress.jsonl
```

It reused all 24 fit-corrected cached panels, verified direct/export raster equivalence, and reassembled the same four declared boards. No `<ns0:` tags occur in any board SVG. A cached re-export produced all four current board SVGs byte-for-byte identically. The corrected unlabelled line-only board was drawn a second time by Chromium and matched its check draft byte-for-byte.

Current board hashes:
- Colour-labelled SVG: `62ab9a281e4c512df8b3c4dee4624cfc5fb435b0a6cb30bea3c75a0098610bed`; PNG: `ec95dc6045ebfc0e31bf0f041dfb70fea8d5fea97c6d55db65a03b195d61402f`.
- Colour-unlabelled SVG: `af9c67519701018aba08b3328e0f4194f248b3dc2334807cc3db9cd00b880681`; PNG: `8f3af57948f1e74ae018526b9a2acc2d63f333a4e5817f463c030a1b5a90ae69`.
- Line-only-labelled SVG: `529baf9b0c9601095a2753d0d10d0e3d2a223b5adac744da8cfac847116aab73`; PNG: `9356018623ad042590ba3b6f4a63a4178c60df5e72161b1f0486cec32b8feb59`.
- Line-only-unlabelled SVG: `fd700b749fdee934e1189fe8a7a408da5d23e17d01c208532457e15b6b80559f`; PNG: `9150176c5c0b5744bf854b0e0c1e75458d5a037f05f8c1bc2f57a9c90a371854`.

All four current `draw check` commands completed and generated their expected full-frame PNG/report. They have no aesthetic verdict. Each report image list is the matching `evidence/check/<board>/draft.png` only, as spelled out in `log.md`. No reviewer has been given the invalid old line-only board as current evidence, and this worker makes no visual-quality or learning claim.
