# Issue 02 — local-art sight-capability precheck evaluation

## Authority and boundary

This is an independent, evaluator-only assessment of the one frozen ex28 capability control. Authority is limited to the approved capability contract in `design.md`, the evaluator-only key (used privately and referenced here only by hash), the frozen precheck payload/control-integrity metadata, the supplied response, and the exact reviewer run/session records. No formal comparison input was opened or delivered; the private mapping was not consulted. The evaluator does not judge the drawing/artwork or certify general vision capability. Key facts are deliberately omitted so this record cannot coach the same reviewer on a later task.

## Frozen method and result

The frozen rule scores four exact shape/color/quadrant triples; each full triple counts once and at least 3/4 meets the semantic threshold. The response's semantic score is **4/4**, so it meets that fact threshold. Dimension is not a field in those triples and is recorded separately, without changing the score: the response states **512×384**, while the actual frozen control PNG is **480×320**.

The overall capability qualification is **VOID**, not PASS and not a semantic failure. The raw reviewer session records the `read` tool returning image/png bytes; the recorded bytes hash to the exact frozen control PNG. This proves image content was returned into the reviewer session record. It does **not** prove those bytes were delivered in the provider's multimodal request: no provider/runner request trace or receipt tying the bytes to that invocation is present. The design makes unverifiable image delivery VOID. The formal comparison remains gated.

## Input and run identity

- Control path: `.scratch/28-local-art-identity/evidence/review/precheck/control-01.png`; PNG metadata dimensions **480×320**, 3,002 bytes, SHA-256 `2bbbf061ea4a16fef3d0a692e40638989eb08cb5529bdc51b252451964fd8ed0`. This matches the frozen control-integrity record.
- Reviewer response: `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/619d121e-e9f0-47e4-9fc9-5f5416daeacb/s1a/local-identity-sight-response.md`, SHA-256 `9463df82caf489e69d1f88e24480a68e8992a7b2f752ad26dd6d90c9fbd07fa1`.
- Run `cafdfd4f-97a6-49bc-86c0-cf88ef16edcb`, workflow `identity-sight-precheck`; runner process instance `a7eb7572-9424-445b-b22d-9f98d5e8d0a0`, exit code 0. Reviewer session ID `01a122fc-ebaa-73fe-b403-63bd16993171`; child session file `.../5df902dd-4196-4791-8136-f07133ff4c2a/run-0/session.jsonl` (SHA-256 recorded in the score JSON). The session's user input names only the control path and neutral prompt; the tool call at line 8 reads that path; its line-9 tool result contains an image attachment whose decoded bytes equal the frozen PNG. The final response begins with the supplied response artifact.
- Recorded provider/model metadata: `github-copilot` / `gpt-6-luna` (`openai-responses`; high thinking). The run status and raw session establish the recorded identity, not an independently authenticated provider receipt. The reviewer transcript export omits the binary image attachment; the raw session file preserves it.
- Frozen response/key linkage is by SHA-256 only. The answer key itself, its facts, the formal comparison input, and private mapping are not reproduced here.

## Evidence and qualification record

The compact machine-readable evidence and score are in `../evidence/review/precheck/evaluation/evaluation.json`. It records the response/key linkage hashes, frozen payload/audit/manifest hashes, actual input hash/dimensions, run/session/transcript/model/runner identifiers, and the distinction between session-tool evidence and provider receipt evidence. No source, control, key, schema, threshold, or response was edited; no image was rerun or dispatched. No tests were needed for this read-only evaluation.

**Dependency-gate result:** semantic facts meet 3/4, but capability qualification is **VOID** for lack of verifiable provider-delivery evidence. Do not dispatch the formal comparison on this record. The separate 512×384 statement is an outside-contract dimension discrepancy, not a retroactive change to the frozen fact score.
