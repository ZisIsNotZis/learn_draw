kind:    report
from:    orient-learn_draw (package launched by root)
to:      root
spend:   idle-compute
id:      none — first contract, answered in the run final message

First orientation report, filed here by root. Body is the run report verbatim.

I oriented read-only inside the checkout, verified every state claim against files and commands, and made no edits. The report follows.

---

# Report → root (`/home/z/vibe`)

**Kind:** `contract`-adjacent completion, decision needed = which R1a writer stage root dispatches next (an internal-plan decision, not a user one).
**Node whose roadmap this changes:** root's `learn_draw` roadmap — it invalidates two rows of the R1a dispatch state, not the milestone list.

## (a) What the project is

`learn_draw` is an agent-run study project whose product is **programmatic, explainable vector illustration** — SVG authored as computed geometry, never diffusion/pixels — first by imitating the anime portrait `image.jpg`, then reference-free. The end-goal named in `README.md` and `docs/drawing/roadmap.md` is a Starry-Night-class scene drawn from intent alone. Its QA philosophy is explicit and unusual: geometry is computed and never eyeballed, the engine never reads the reference, metrics are alarms not targets, and **no agent may award its own art verdict** — a drawing is judged by a fresh sight-capable independent reviewer on the rendered image, and no candidate may be promoted or called final without its roadmap gate.

Technically it holds three layers that are deliberately distinct:

- **Architecture SSOT:** `docs/drawing/spatial-model.md` — independently drawn 2D components on planes/3D-curved supports, with visibility computed from depth; the model must never hand-label where an object disappears. `relate.py`/`scene_render.py` are the legacy flat-2D pipeline and do **not** implement it.
- **Forward plan:** `docs/drawing/roadmap.md` — R1a object studies → R1b articulated composition (deferred) → M2 sealed reference-free drawing (blocked on user release) → M3 integrated delivery → M4 user judgment; then R2 responsive poses, R3 reference-based composition. Four acceptance questions are kept separate everywhere: construction/attachment, physical geometry & visibility, drawing/art, object cohesion.
- **Observed state:** `STATUS.md` (29 KB of it), `.scratch/active-work.md` (stale, it stops around issues 46/52), per-candidate dispositions in `.scratch/35-r1-articulated-study/evidence/acceptance-ledger.md`, dispatch history in `work/wave-log.md`, and one directory per exercise under `.scratch/NN-slug/` with `source/`, `tests/`, `artwork.svg|png`, `check/`, `manifest.sha256`, `README.md`.

Where it actually stands: no candidate has ever passed an independent art gate at the original figure scope. A v4 passed one finite art gate that the user then contradicted; A v5 / B-hand-v2 image reviews failed; B-hand-v2-r1 passed mechanics and failed a further image review; A v6/v6-closeout/v8 were never image-reviewed. The user's only verdict is the qualified *"much better, maybe not the best, but at least somewhat acceptable"* on v8 and v2-r1, explicitly recorded as **user judgement, not a gate**. He then approved the reduced scope (*"Maybe just proceed, i.e. b?"*) — one object filling the frame — which split R1 into R1a (the bow; the hand-with-dish) and the deferred R1b. The recurring failure mode across the whole record is not engine capability but **object readability at the pixel**, and the recurring process failure is infrastructure: four runs died mid-flight, which is why the plan now sizes packages to a 30-minute harness stage and requires artefacts before documentation.

## (b) The milestone it proposes next

**R1a — object studies, on two frozen revisions, with per-study independent gates and one user presentation.** This is the roadmap's own next milestone, not a new one: `docs/drawing/roadmap.md` §"R1a — Object studies", exit line 34. Evidence pointer: `docs/drawing/roadmap.md:27-36` (gates and exit), `.scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md` (the two binding contracts: A bow 800×560 reference-seeded, B hand+dish 900×700 reference-free), `.scratch/35-r1-articulated-study/work/m1a-m1b-plan.md` (owners, paths, budgets), and per-candidate dispositions in `evidence/acceptance-ledger.md`.

Reaching it needs exactly two things, in this order, and **neither exists yet**:

**1. `A-bow-study-v2` is a half-finished package, and worse than `STATUS.md` reports.** Verified at commit `9bc2392`:

- The repair *is* there in source: `source/parts/bow.py` differs from v1 by 299 diff lines (new `R_FOLD`/`R_WRAP`/`H_FOLD`, knot placed at `KNOT_X = 553`, loop limbs brought back over each other so a lobe is filled cloth) and says "Repair r2 changed the turn generation". `source/build.py`, `source/ribbon.py`, `source/manifest.py` and all four test files are **byte-identical to v1**.
- `README.md` is **byte-identical to v1's** (both `46e772ff…`): it still calls the package "A-bow-study-v1", and its route table, width field, depth table and crease table describe v1's numbers, which the source no longer produces.
- Contrary to `STATUS.md`'s "no artwork", `artwork.svg` (`3ea56b4b…`) and `artwork.png` (`015a55a6…`) exist, and the SVG is **exactly** the output of the committed source: a fresh build to `/tmp` compared `cmp`-identical, and `test_the_delivered_png_is_a_fresh_build` passes in place, so the delivered PNG is the render of the delivered SVG.
- The committed (v1) suite now **fails 8 of 17 tests against the v2 source**, run in place with `PYTHONDONTWRITEBYTECODE=1` and `git status` clean afterwards: 8 of 13 self-crossings have under one cloth thickness of depth separation (0.7–15.8 px) with rear edges drawn through them; 4 of 1240 triangles disagree with their own winding; width ratio `max/min` = 3.88 (test floor 4.0); the knot is **not a waist** (113.5 px vs 159.6 px median loops); a 9.03 px single-station width jump remains. There is no `check/` bundle, no `manifest.json`, no `manifest.sha256`, no `negative-control-output.txt` (13 files vs v1's 19).
- v1 itself passes its own suite (17 tests, manifest 17/17, winding 0 disagreements, 10 crossings broken) — so these failures are the v2 source, not the harness.

So v2 is not "source and tests awaiting artwork" as `STATUS.md` and `wave-log.md` row 22 say. It is: **a repaired construction, reproducible, with a stale README, no manifest, no review bundle, and a test suite that the repair contradicts.** The package is not reviewable and not self-consistent.

**2. `B-hand-study-v1` does not exist in this tree, though three current-fact documents say it produced an artefact.** `STATUS.md:33`, `evidence/acceptance-ledger.md:112`, and `wave-log.md` row 24 all assert "artwork, source, tests and a check bundle exist" at `.scratch/35-r1-articulated-study/evidence/B-hand-study-v1/`. Absence, claimed from searches that would have found it: `find . -path ./.git -prune -o -iname '*B-hand-study*' -print` → **0 hits**; `git log --all --oneline -- '.scratch/…/evidence/B-hand-study-v1'` → **0 commits**; `git branch -a` → only `master`; `git worktree list` → only this checkout; `git stash list` → empty; `git status --porcelain --ignored` → nothing under that path, not even ignored. The directory listing of `evidence/` contains `A-bow-study-v1`, `A-bow-study-v2`, and no B study. There is also **no dispatch script** for that wave under `work/` (the wave-log's own last row says every other dispatch committed one). So the B half of R1a is at zero, and the tree currently records a fiction about it.

## (c) What it cannot answer, with the effort and the reopen condition

1. **Did the `B-hand-study-v1` run ever produce anything, and if so where did it go?**
 Tried: project-wide `find` by name (0), `git log --all` on the path (0 commits), all branches, `git worktree list`, `git stash`, ignored-file scan, `evidence/` listing, and the wave log and issue 55 for a dispatch record. The tree holds no run record, no dispatch payload and no artefact for that writer — the only trace is the parent's claim in three documents. It cannot be established from the tree whether the run never started, died before its first commit, or wrote into a worktree that was never landed (cf. P36/P37's earlier losses).
 *What would reopen it:* a session/dispatch record outside this checkout — the ledger already cites artefacts of that shape under `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/` — or a surviving worktree/branch naming `B-hand-study-v1`. Absent either, the honest reading is "no artefact; re-dispatch".

2. **Whether to recover v2 or restart it — a scope/plan choice root owns, not this package.**
 The evidence now makes the choice sharp: the v2 construction is committed, deterministic and reproducible but fails its own inherited suite in the *law* layer (crossing depth, width continuity, knot waist), and its documentation describes the old drawing. Option 1: resume v2 — retune the turn geometry until the committed law holds, then author the six defect tests the contract demands, replace the README, emit `check/` and the manifest. Option 2: treat v2 as a second failed hypothesis and go back to construction. The roadmap caps a study at **two distinct structural approaches** before reporting unresolved rather than lowering acceptance, so this choice consumes budget and cannot be taken silently. Nothing in the tree records which approach v1 and v2 count as.

3. **Whether the sealed M2 brief may be released.** `.scratch/35-r1-articulated-study/work/holdout-brief.sealed.md` exists (569 B) and I did **not** read it. M2 is blocked on a user decision (release + authorizing a new creator role, issue 51 / plan §M2) that no agent can take. Not reopened by evidence; reopened only by the user.

## State corrections root should land (not made here — read-only contract)

- `STATUS.md` R1 advance section and `wave-log.md` row 22: v2 has artwork (source-derived, hashes above), no manifest/bundle, a v1 README, and a suite it fails 8/17.
- `STATUS.md:33`, `acceptance-ledger.md:112`, `wave-log.md` row 24: no `B-hand-study-v1` artefact exists; the B study is not "in flight" but absent.
- `.scratch/active-work.md` is two waves stale (stops at issues 46/52) and now competes with `STATUS.md` as a state source; `STATUS.md` is the SSOT per its own header.

No edits, no staging, no sealed content read, no network write; idle-compute only.