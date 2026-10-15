# Image-delivery evidence discovery

## Interpretation and scope

Bounded read-only discovery of the installed Pi SDK, GitHub Copilot/OpenAI Responses provider request path, and the governed native subagent extension. Determine whether supported hooks/logs can establish image presence in the *actual serialized request* and correlate it to the same reviewer response. This is infrastructure discovery only; no provider call, reviewer dispatch, probe, environment/config mutation, source/runtime edit, dependency install, staging, commit, or bypass is authorized.

Ex28 sight precheck remains **VOID** because actual provider multimodal-delivery evidence is missing. Its prior VOID is immutable; 4/4 semantic correctness and raw-tool-result PNG-byte equality do not prove the image reached the provider. The formal board/private mapping are out of bounds and must not be opened, sent, or decoded. Frozen payload, image, cases, evaluator, source and credentials remain unchanged; never access credential values or record secrets.

## Authority and limits

User authorizes read-only inspection and durable discovery/design/status notes only, with a 20-minute finite budget and commands bounded to 120 seconds. Do not weaken frozen proof/schema or invent a receipt. Do not run precheck, learner, reviewer, artwork or S1a acceptance. External/SDK fallback, provider call, probe implementation, config change, or any execution requires parent/user approval. Stop at an unavailable supported hook/receipt boundary and record it honestly.

## Options under investigation

1. Existing governed native subagent logs or receipts; preferred only if they expose same-run request metadata and image-byte evidence without bypassing orchestration.
2. Supported SDK before-send/request hook on the same governed path; distinguish inspectable transformed request from actual transport boundary and response correlation.
3. Isolated synthetic-control probe/script or foreground SDK fallback only as a *proposal*, not to run absent explicit approval.
4. If no provider receipt exists, document the strongest truthful pre-send plus response evidence and state that it cannot meet the frozen strict delivery criterion.

## Acceptance and proof

Deliver exact installed version/source/doc references; supported path and cancellation behavior; evidentiary boundary (transformed request, actual fetch/write, provider receipt/acceptance, semantic perception); minimal metadata+decoded-PNG-SHA256 schema; negative image-stripped control; privacy constraints; and one bounded safe next-leaf recommendation. Independently verify no forbidden formal/private artifact was opened and no source/provider state changed. Existing ex28 frozen contract requires trace evidence that image content—not only a filename—was delivered to the same multimodal invocation; a raw tool result alone is insufficient.

## Leaf decision

This is one cohesive read-only infrastructure-discovery leaf. No sibling delegation or execution is authorized. Durable outputs: this ticket/process record, `.scratch/29-image-delivery-evidence/design.md`, narrowly updated current status/active-work state, and the runtime-authoritative discovery report. Preserve all inherited staged/dirty work.

## Findings and disposition

Read ex28's `design.md`, frozen precheck `evaluation.json`, and `issues/02-sight-evaluation.md` only. The evaluator records 4/4 semantic triples (threshold 3/4), byte identity between the frozen control and session `read` tool attachment, but explicitly no provider delivery proof and no receipt; qualification remains VOID. The formal board and private mapping were not opened. The older finite numerical/kernel acceptance is unchanged.

Active package metadata confirms `/home/z/.pi/agent/npm/node_modules/pi-subagents` v0.76.1 (`package.json:3-4,127-134`) and installed Pi/pi-ai v1.1.0 (Node v24.18.1). Complete relevant docs read: installed Pi `sdk.md`, `extensions.md`, `custom-provider.md`, and `providers.md`; active pi-subagents `docs/agents.md` and `docs/tool-reference.md`; applicable execution/environment policy sections. No credential files/values, secret environment values, raw session transcript, formal board, or private mapping were inspected.

Pi's `before_provider_request` (`core/sdk.js:225-230`; event type `core/extensions/types.d.ts:679-683`) sees the adapter payload before OpenAI JSON serialization; it is not fetch-boundary proof. `after_provider_response` exposes status/headers and `provider_stream_event` exposes parsed events (`sdk.js:231-251`; types:693-705). Copilot Responses maps images to `input_image` data URIs (`pi-ai/api/openai-responses-shared.js:51-56,153-159`). A complete `githubCopilotProvider()` can be registered through `pi.registerProvider(provider)` (`core/extensions/types.d.ts:1334-1335`); wrap its `stream`/`streamSimple` only for `openai-responses`, pass all original options/auth through, replace `fetch` with a metadata-only observer, and pin `maxRetries:0`. Its factory carries original Copilot OAuth/API-key auth (`pi-ai/providers/github-copilot.js:8-17`); model runtime resolves auth into in-memory `apiKey`/headers (`core/model-runtime.js:447-475`). The fetch wrapper sees serialized body handed to fetch; `onResponse` plus `response.created.response.id` (`openai-responses.js:138-142`; shared:478-482) correlates the local response, not provider-issued image-hash proof, socket receipt, or perception.

Active runner seam: agent config `extensions` is a per-child allowlist (`docs/agents.md:479-493`; `child-tool-plan.js:272-291`). `extensionBindings` is bounded namespaced JSON and encoded as `PI_SUBAGENT_EXTENSION_BINDINGS` (`tool-reference.md:102`; `extension-bindings.js:1-6,54-77`; `child-launch.js:48-52`). Critically, `child-launch.js:224` injects this environment only for `host:"runner"`; local foreground is `host:"parent"` (`foreground/execution.js:316-319`), so foreground cannot pass the binding. Fresh native async runner + one-off agent profile is the exact supported route; external and retained-resume paths reject bindings. `timeoutMs:120000` is terminal (`tool-reference.md:97`); set API `maxRetries:0` and await managed terminal status. No global settings, installed-package edits, CLI/SDK fallback, external mode, or provider call occurred.

## Recommended next leaf — not authorized or started

After separate parent/user approval, create only the local extension, offline tests, synthetic control, and one-off project-scoped native agent profile in `design.md`; run exactly one fresh native async child with `extensions:[absolute local extension path]`, `context:"fresh"`, `timeoutMs:120000`, and `extensionBindings:{"learn-draw-image-evidence/1":{...non-secret control metadata...}}`. Pin provider `maxRetries:0`, require one image-bearing fetch, immediately wait for the governed runner's terminal state, never resume, and keep the control/reference/board boundary unchanged. If a managed async runner is disallowed by the earlier no-detach clause, stop; foreground does not propagate the required binding. The image-stripped offline test must reject proof without any second network request; privacy schema/allowlist remain in `design.md`.

The frozen ex28 phrase “runner/provider request trace” can be read to admit the local fetch-boundary trace plus correlated success response without changing acceptance; it does not establish remote receipt or perception. No provider-issued image-hash receipt exists. Parent must decide whether that stricter proof is required before qualification; if yes, block/VOID. This cannot retroactively validate ex28's old VOID.

## Evidence and validation boundary

Read-only source/evaluation evidence and exact interfaces are in `.scratch/29-image-delivery-evidence/design.md`; no source, runtime, extension, provider, credential, art, case, payload, or prior evidence was changed. No tests or provider calls ran. The formal board and private mapping were not opened. Inherited staged `.gitmodules`/vendor entries and unrelated dirty work remain protected; final status check confirms no new staged files. Independent review is still required; the proposed extension/control/provider call has not started.
