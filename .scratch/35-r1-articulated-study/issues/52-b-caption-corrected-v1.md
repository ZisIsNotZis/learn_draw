# Issue 52 — B truthful presentation caption derivative

Opened 2026-10-14T02:31:11+08:00. Main authorized a narrowly scoped, presentation-only truthful-caption repair after the supplied independent disposition: B body/action finite gate PASS; presentation claim blocked only by unsupported “thumb braces rim” wording. Owner: single writer. Main owns fresh image-only delta review. No delegation, art/body rebuild, hand/pose/geometry change, or expansion to full R1.

## Scope and boundaries

New output only: `.scratch/35-r1-articulated-study/evidence/B-caption-corrected-v1/`, this issue, acceptance-ledger addition, STATUS and active-work current pointers. The base is `goal-recovery-r1-v2-completion/rendered/B-original-support.svg`; the old completion directory, all source/SVG/PNG/manifest bytes remain read-only. Sealed/brief/A/source-context not read or modified. No tests, environment/backend/vendor/`.agents`, network, staging, or commit. Pre-existing broad dirt/staging preserved.

Implementation copied the frozen B sheet and made two raw exact string replacements, and nothing else: `bent arm · open palm supports dish · thumb braces rim` → `bent arm - open hand supports dish from below` in baseline and variant caption text nodes. The right-hand `CONTROL — near miss` label is unchanged. XML parses; reverting those two text strings recreates the base SVG byte-for-byte. Thus SVG geometry/path/style/transform/node order/colour/viewport all remain unchanged. Old internal geometry vocabulary remains source history only; the new public disposition distinguishes that hypothesis from what the image supports and does not claim an image-verified thumb.

## Artifacts and evidence

- Derivative SVG: `evidence/B-caption-corrected-v1/B-original-support.svg`
- Rendered PNG: `evidence/B-caption-corrected-v1/B-original-support.png`
- Reference-absent `scripts/draw check` image list: `evidence/B-caption-corrected-v1/checks/B/report.txt` (only `checks/B/draft.png`, the drawing)
- Current public-caption scope: `evidence/B-caption-corrected-v1/public-caption-disposition.md`
- Hash and pixel proof: `evidence/B-caption-corrected-v1/manifest.json`

Base SVG SHA-256 `2fce35f4503ad806f22c8e2e9e737f12939cbd9d977050a34eddff26b5da538d`, matching the old manifest. Derivative SVG `daf5dfd2afabc7ed639942c180d209f0380e147c75aad353da50f859bc7c03c9`; derivative PNG `cc62191fae497922f8eb0582a0080a3dbf0694791d59edc10f4627c6a16bf733`. Frozen old PNG SHA-256 `81860c9da0a4d7be7f8a6cd04e1f30ef64a9712c6063ca8e42cb65f44311c193`. Pixel difference is confined to declared rectangles derived from the SVG caption text anchors and enclosing panel transforms: `[60,595,390,616)` and `[510,595,840,616)`; total changed bbox `[79,603,821,615)`. Every decoded pixel outside those rectangles is exactly equal. Two additional sight-probe crops at the hand-support (`375,420`) and head (`225,205`) are equal. The changed bbox naturally spans both text labels; no pose/head/hand regions were masked.

Existing 33-field source manifest is not amended. Its self-hash, recorded in derivative manifest, is `e76a94dcabd3bfa6c5a6f249c715d969f9fce21780c89f32b1940022967319d2`. It remains historical base proof, not replaced by this derivative.

## Commands and results

- `scripts/draw render <new-svg> -o <new-png>` — PASS; run once, 1350×640.
- `scripts/draw check <new-png> --outdir <new-checks/B>` — PASS; reference absent; image list records only the draft drawing. This consumes the one rendered PNG; the source SVG is not re-posed or regenerated.
- Bounded Python verifier — PASS: XML parse, exact restoration of frozen SVG bytes after text-only reverse substitution, zero old claim occurrences, exactly two changed text nodes, control label intact, hand/head probe equality, and exhaustive per-pixel equality outside SVG-node-derived caption rectangles. Initial verifier attempts exposed Pillow RGBA `getbbox()` alpha semantics and missing parent-panel translation in coordinate derivation; corrected verifier used RGB pixel diff and the explicit parent `translate(450,0)` and passed; no artifact was changed by those verification-script corrections.
- Independent frozen-source/hash crosscheck verified all 35 entries in the old manifest's source/render/teacher/review maps plus completion/preflight record hashes; old manifest SHA-256 `e76a94dcabd3bfa6c5a6f249c715d969f9fce21780c89f32b1940022967319d2` remains unchanged. The draw-check creates a 256×121 review preview (not a replacement for the full-resolution 1350×640 rendered PNG); report lists only that drawing and confirms reference absent. Its hash and the disposition/report hashes are bound in the new derivative manifest (SHA-256 `abcbccfa8f6a4f329c1abe82474d717e0062db8ea144aabef8744ac47e292dc6`).
- Final `git diff --check -- STATUS.md .scratch/active-work.md .scratch/35-r1-articulated-study/evidence/acceptance-ledger.md` — PASS. `git diff --cached --name-only` reports only pre-existing `.gitmodules`, `vendor/huashu-art-motion`, and `vendor/huashu-design`; none were staged by this task.

## Disposition and gates

The supplied independent adjudication report is `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/ab8928de-eafd-4072-9a6c-6e0ce3e620ee/r1/b-art-acceptance-disposition.md`. It grants only finite B body/action art PASS and identifies this wording as the sole current presentation-claim blocker. This writer does not self-review the drawing. Status after this change: **B finite body/action art PASS; truthful caption emitted, fresh caption presentation review pending**. R1, transfer, heldout, integrated geometry/depth, and user acceptance remain open and are not PASS. Main routes fresh delta review using only the image list.
