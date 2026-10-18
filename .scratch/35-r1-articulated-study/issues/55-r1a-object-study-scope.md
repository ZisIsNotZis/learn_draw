# Issue 55 — R1a object-study scope: one object per image replaces the figure packages

Opened 2026-10-18. Owner: record keeper. Trigger: the user reviewed the latest A and B candidates and gave two decisions — a qualified verdict on those two images and an approved reduced scope. This issue owns the scope decision; [roadmap R1a/R1b](../../../docs/drawing/roadmap.md) owns the gates, [`work/r1a-object-study-contracts.md`](../work/r1a-object-study-contracts.md) owns the two study contracts, [the advance plan](../work/m1a-m1b-plan.md) owns the work packages, and the [acceptance ledger](../evidence/acceptance-ledger.md) owns per-candidate dispositions.

## User decisions recorded here

### 1. Qualified, partial acceptance of the two images he saw

The user's words, recorded verbatim:

> much better, maybe not the best, but at least somewhat acceptable

This is his own verdict on `A-cloth-v8`'s image and `B-hand-v2-r1`'s images as they stand at their current commits. It is a qualified acceptance of those two images and an explicit non-claim that they are the best or final.

It supersedes neither the independent image reviews that failed those candidates nor any roadmap gate: it closes no construction, geometry/visibility, art or object-cohesion gate, and it is not an R1 or transfer PASS. It is recorded as a distinct disposition, user judgement rather than independent review, in the [acceptance ledger](../evidence/acceptance-ledger.md).

### 2. Approved reduced scope — one object per image

The user's words, recorded verbatim:

> Maybe just proceed, i.e. b?

"b" is the earlier presentation's option b, the reduced scope of single-object studies filling the frame. Only that option is approved: no stronger model tier was authorized, and no scope beyond the two studies below was approved.

## What changed

R1 splits into R1a and R1b ([roadmap R1](../../../docs/drawing/roadmap.md)).

- **R1a — object studies:** the bow, and the hand-with-dish. Each is a real authored image filling its own frame, with its own construction/geometry/art gates and its own user presentation.
- **R1b — the deferred articulated composition:** the two objects composed into the shoulder/upper-torso study the original R1 described. Its exit conditions are unchanged and unweakened.

## Why

A figure at 400x480 is beyond what the current drawing vocabulary composes readably, while one object at large scale is not: every independent review of a full figure failed on object cohesion or object readability.

This is a product-level scope change approved by the user, not an agent decision. No worker, reviewer or integrator may reduce or widen it on its own.

## The two studies now in flight

`A-bow-study-v1` and `B-hand-study-v1` are dispatched: the bow alone, imitating only the reference's observed bow, and an original reference-free hand-with-dish with no head, torso, shoulder join or body connection. B presents a single image with no panel sheet and no captions.

Their canvases, artefacts, binding construction requirements, acceptance and what the reduced scope dropped relative to the M1a/M1b figure packages are owned by [`work/r1a-object-study-contracts.md`](../work/r1a-object-study-contracts.md) and are not restated here.

## Deferred, not deleted

The full-bust composition is DEFERRED, not deleted: it returns as the next milestone, R1b, once both object studies pass.

R1a passing does not satisfy R1b, and no object study may be recorded as satisfying R1's "imitate the reference's visible shoulder/upper-torso clothing/composition".

## Dispatch contracts (process gap, now closed)

A dispatched work package's contract belongs in the tree, committed at the moment it is issued; a contract that lives only in chat is lost to any reader of the repository and to any run killed mid-flight (P34).

This gap was found while recording these two studies: their contracts existed only as dispatch text. It is closed by [`work/r1a-object-study-contracts.md`](../work/r1a-object-study-contracts.md), which now holds both contracts, and later dispatches follow the earlier waves' pattern of a committed file under `work/` (for example `work/wave10-a-closeout.js`).

## Boundaries

No artwork is accepted by this issue; the user's qualified verdict is recorded in the ledger, not claimed here as acceptance. No candidate is replaced, no sealed/heldout content was read, and no baseline promotion is implied. R1b, M2, M3, M4, transfer, heldout, reproduction and integrated R1 acceptance remain open.
