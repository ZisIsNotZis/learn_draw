# Issue 50 — A v4 finite art acceptance and remaining gates

**Opened:** 2026-10-14T01:38:25+08:00. **Owner:** assigned documentation/evidence writer; Main retains routing and human synchronization. **Branch:** `master`. **Status:** A-cloth-construction-v4 passes only the bounded finite A art gate; broader A/R1 acceptance is open. No stage or commit.

## Scope / authority

Assigned task: archive supplied final-proof reports without overwriting them; record accurate bounded acceptance; synchronize current status and handoff. No drawing, source, candidate manifest, prior evidence, backend, environment, staging, or vendor changes authorized or made. Preserve existing dirty/index state. A v4 candidate/source/image remain unchanged. Prior issue 49 remains historical evidence of the candidate implementation allocation's NOTDONE outcome; this review disposition does not rewrite its execution history.

## Review disposition

Accept exactly the independent A finite art/readability gate for `.scratch/35-r1-articulated-study/evidence/A-cloth-construction-v4/`. The two formerly reviewed P1 findings are closed: pointed zero-front-width collar replacement, and background-colored waist discontinuity. Retain the reported P2 observations as nonblocking; do not imply exact full-reference matching. This is not full A/R1 acceptance, not a transfer PASS, and not human/user acceptance.

Final source reports are archived byte-preservingly under `evidence/A-cloth-construction-v4/acceptance-proof/`; their provenance/body hashes and scoped interpretation are recorded in [`evidence/acceptance-ledger.md`](../evidence/acceptance-ledger.md). The reviewed artifact's manifest digest is `0a1e42a46e9f733cd0da82e3acf4f3934a918d4cb67fdfc9421923aa72ec0a12`; reviewed image `artwork-a.png` digest is `07998d71693039294008f7c402ee46ed86a0a43edc8e0c9115a39d7e25284da3`. Report dispositions and scope limits are the evidence authority; tests/hash evidence does not substitute for visual judgment.

## Current open gates

B formal art/transfer remains OPEN; separate new heldout task/release remains OPEN; deterministic reference-absent reproduction remains OPEN; broader construction/depth and integration remain OPEN; user-facing presentation and feedback remain OPEN. No R1 or transfer PASS. No sealed heldout content was accessed. No new B work or runtime/provider operation is authorized by this record.

## Changes and proof

Created the current-fact acceptance ledger and archived exact copies of the three supplied reports. Updated `STATUS.md` and `.scratch/active-work.md` to name this bounded A PASS and accurate remaining gates; issue 49's historical content is unchanged. Source provenance, body hashes and candidate hashes are in the ledger.

Validation commands and results: `sha256sum` on each original report, then on each archived copy produced matching body hashes; see ledger. `git diff --check` and repository status/index checks are required after edits. Preserve pre-existing staged `.gitmodules` and vendor gitlinks and all unrelated dirty files; no new staging operation is allowed.
