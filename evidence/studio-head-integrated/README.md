# Integrated head editing — 2026-11-12

The user accepted the displayed simple flat-cartoon head as one default preset. This record tests
whether that useful recipe can be revised through the public studio interface, rather than by
editing generated SVG paths. It does not establish a complete artwork or general drawing mastery.

`demo/` contains a reproducible default → quieter eyes → narrower right temple lock → plum hair
sequence. Each stage contains clean artwork, alignment, closeups, input and revision bindings.
The sequence accepts all three operations, undoes them to the original input, and replays them to
the final input exactly. Run `python -m scripts.studio demo --kind head --outdir FRESH` to repeat.
`usability/REVIEW.md` records an independent operator using only the skill and public interface:
10 commands completed, actual normal/alignment/crop images inspected, semantic and local previews
accepted, and undo recovered the previous revision and PNG bytes. No execution blocker was found.
The operator suggested a colour legend and identified object translation as a composition gap.

`validation.json` records 48 operation/head/visibility/oracle tests, 81 CPU smoke checks and repeated
SVG/CPU PNG byte identity. `uv sync --locked` succeeds. The tests include actual raster locality,
depth ownership with multiple namespaced heads and crossing planes, screen-direction editing under
parent tilt, exact undo, stale revisions, and failed-render/pending-candidate rejection. Geometry
compilation works without discovering a browser; browser rendering resolves its browser lazily.

The head recipe lives only in `scripts/studio/head.py`; the old probe delegates to it. Recipe art
attributes match the accepted study. Integration changes outer SVG nesting/clipping and therefore
does not claim byte identity with the historical study PNG. The conservative depth-order fast path
is derived from nonoverlapping support-depth intervals; intersecting intervals still use the exact
triangle visibility engine. Internal head features are flat recipe artwork, not a 3D turning head.

`01-default`, `02-eyes`, `03-smaller-eyes` are earlier integration records; their bindings describe
the implementation at their creation, and must not be reused as current selections. The complete
demo and later operator review are the main evidence. No target image, GPU/model execution or
generated bitmap asset was used. The original portrait and its recorded best remain untouched.
