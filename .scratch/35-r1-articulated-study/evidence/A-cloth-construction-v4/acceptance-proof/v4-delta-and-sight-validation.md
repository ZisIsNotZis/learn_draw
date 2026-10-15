# A-cloth-construction-v4 scoped source and sight validation

## Verdict and boundary

**PASS for the bounded source/delta/tests/manifest and supplied sight-fact checks only.** This is not an A-art verdict, not teacher acceptance, and not an R1 PASS. No whole-image artistic judgment was made. The previously supplied visual qualification is treated as evidence only for the two reported interior regions; it does not establish construction quality, correctness of their semantics, or full-image acceptance.

Validation was read-only: no source edits, render/check invocation, sealed material, B candidate, environment changes, or staging operations were performed. Tests were run with Python `-B`, pytest cache disabled, each suite under a 115-second timeout.

## Candidate integrity and v3 delta

Candidate: `.scratch/35-r1-articulated-study/evidence/A-cloth-construction-v4`.

- SHA-256 of `manifest.json`: `0a1e42a46e9f733cd0da82e3acf4f3934a918d4cb67fdfc9421923aa72ec0a12`; `manifest.sha256` agrees.
- Independently checked all 16 manifest file entries against on-disk byte counts and SHA-256: all matched.
- The v4 manifest's recorded baseline v3 SHA-256 values were independently confirmed against the original v3 files for `source/build_a.py`, `source/family-rules.py`, `source/semantic-parameters.json`, `tests/test_a_cloth_identity.py`, and `tests/test_scoped_repair.py`: all five originals remain unchanged.
- Direct comparison shows the v4 changes relative to v3 are restricted to the candidate's collar implementation and its checks: collar wrap-strip/support-pair logic in build/family rules; collar front-width/root-width/floor parameters; updated collar/trim expectations in inherited tests; and new `test_collar_wrap_strip.py`. No unrelated garment family, renderer/backend, B, teacher, or sealed input is present in the v4 manifest delta.
- The test changes in v4 also correct their candidate path to be relative to the test file, so the suite tests this v4 candidate rather than hard-coding v3.

## Independent command results

Commands run from the repo root; all passed:

1. `timeout 115s python3 -B -m pytest -p no:cacheprovider -q .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v4/tests/test_a_cloth_identity.py` — **7 passed** (61.06s).
2. `timeout 115s python3 -B -m pytest -p no:cacheprovider -q .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v4/tests/test_scoped_repair.py` — **4 passed** (11.84s).
3. `timeout 115s python3 -B -m pytest -p no:cacheprovider -q .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v4/tests/test_collar_wrap_strip.py` — **6 passed** (30.13s).
4. A read-only Python `-B` verification script checked every manifest entry, manifest sidecar, candidate PNG dimensions/probes/pixel equivalence, and the five v3 source/test hashes listed above — **passed**.
5. A read-only `diff -u` comparison of the five v3/v4 source/test files — observed only the scoped collar behavior and the v4 test-root/path updates described above.

These checks establish that the declared regression suites pass on the actual v4 source. They do not independently prove all physical intersections, whole-scene depth correctness, artistic quality, or runtime behavior outside those tests.

## Sight facts and pixel verification

The provided sight qualification reports direct viewing of the five listed images, with the full-resolution draft at 400 × 480 px and upper-left origin, and two visually stable interior probes. I independently sampled actual pixels in the three manifest-listed draft/output PNGs; all three have 400 × 480 dimensions and are pixel-identical, despite `draft-fullres.png` having a different PNG byte hash/encoding from `artwork-a.png` and `draft.png`.

- `(240,120)`, the reported upper-central pale blue/gray-blue collar interior above the bow: center RGB `(145,185,202)`; the 17×17 crop centered there has all 289 pixels exactly `(145,185,202)`. This supports the reported pale blue/gray-blue color-class description and interior stability at that coordinate.
- `(235,185)`, the reported magenta/rose right bow lobe below the collar, extending rightward: center RGB `(214,83,129)`; 278 of 289 pixels in the 17×17 crop are `(214,83,129)`, with the remaining 11 near-color edge/antialias samples. This supports the reported magenta/rose category and interior stability at that coordinate.
- Both locations are within the draft bounds; their relative y positions confirm the bow probe is below the collar probe. Pixel samples verify color and local stability only; color alone cannot establish component identity, construction intent, or a formal artistic judgment.

Exact image hashes: `artwork-a.png` and `check-a/draft.png` are both `07998d71693039294008f7c402ee46ed86a0a43edc8e0c9115a39d7e25284da3`. `check-a/draft-fullres.png` is `ae61780d4f10677a307abbc389c04506cdabe5e3601a7358cd0b76e6c992344f`. Despite its different encoding/hash, its decoded pixels are identical to the other two 400×480 images.

## Scoped geometry claims supported by source/tests

The six collar regressions cover positive-width rejection of the old zero-front-width/shared-Q triangular case, finite sampled offsets and self-intersection rejection, degenerate shared-normal rejection, shared inner Q and derived Q-prime plus sweep continuity, the 101-point Q-to-Q-prime world-depth seam and preserved transverse gradient, and the typed trim path going through depth clipping and SVG emission. The identity suite covers the skin negative-opening probes and authored-input budget; inherited scoped repairs cover waist fill/pixel continuity and cuff world-depth contact. These are implemented-test checks, not a substitute for independent geometric proof beyond tested cases.

## Limits / residual risks

- No render/check was run by this validator and no new pixels were generated. Sight verification is based on the provided five-image visual qualification plus direct sampling of existing PNGs.
- No art verdict, complete garment assessment, corrected-teacher-v2 gate, broader physical-intersection/depth acceptance, teacher acceptance, or human synchronization was attempted. Manifest status correctly leaves AArt and R1 not PASS.
- The report does not claim universal volume physics or prove all possible inputs; geometry guards and tests cover the candidate's intended two-leaf construction and described regressions.
- Repository status had extensive unrelated pre-existing work. The initial `git status --short` showed staged `.gitmodules`, `vendor/huashu-art-motion`, and `vendor/huashu-design`; they are unrelated/pre-existing and untouched. No v4 task files were staged and no staging operation was made. Thus the repository does **not** have an empty index, though this validation added no staged files.
