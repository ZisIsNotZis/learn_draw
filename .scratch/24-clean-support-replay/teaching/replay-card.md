# Current-producer support comparison replay

This is a provenance-clean replay of the five-row fine flat-versus-camber comparison, with the same five cases, ten panels, `.35` camber, author inputs, palettes, local stripe, cameras, and `96x12` sampling as exercise21. The only plan dependency change is the reviewed canonical visibility source SHA; the new plan additionally records the migration. The prior exercise21 plan, caches, images, board, width measurement, and failed learner answer remain historical and unmodified.

- Current plan: `work/cases-current.json`; derived from `.scratch/21-ribbon-cross-section/work/cases-fine.json`.
- Producer: `.scratch/21-ribbon-cross-section/work/build.py`, invoked with explicit `--plan`, `--evidence`, and `--progress` paths.
- Canonical visibility resolver: `scripts/vector_visibility.py` SHA-256 `fa4c31acf8ffc622352d1feb192e4adddc7931be9cdfc046fda70b1f4d23d3fa`.
- Support generator: `scripts/ribbon_surface.py` SHA-256 `5c32715a9359e3228a7cd91e2bed020f47badcc6df949f2f54e6c8ae493df2f4`.
- Boards: `evidence/comparison-labelled.svg` and `evidence/comparison-unlabelled.svg`; ten complete panel pairs and source/cache hashes are in `evidence/build-manifest.json`.
- Detailed current producer, imported module path, cache-key, case and determinism bindings: `evidence/provenance/replay-ledger.json`.
- Reference-free report image lists are recorded in the ledger. They are the only material to provide to a fresh visual reviewer; no worker image judgment is recorded.

This replay demonstrates artifact production against the reviewed bounded renderer, not that camber improves readability or that visibility is continuously/full-policy correct. S1a remains open. Finite near-policy exclusions, fragment-boundary exclusions, EPS/bbox deadbands, exact first-declared coplanar ties, and unrestricted-geometry limits remain as recorded by exercise23. Existing actual-mesh width evidence is referenced at its original exercise21 location, with 132 finite samples passing its declared 0.002-unit bound; it is not a continuous guarantee. Independent visual review of these exact new report-listed images is pending; no art, learner, S1a, S2, hair, or figure acceptance is implied.
