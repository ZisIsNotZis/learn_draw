# Ex29 active runtime stream repair — blocked

## Interpretation, scope, acceptance, and approach

The approved work was to repair the proven active Pi/pi-ai callback mismatch, observe a successful normalized `done` message's `responseId` while preserving stream/streamSimple API and native result/cancellation/options/hooks, and test both actual installed provider methods offline with stub fetch. Required proof included serialized-request hash and unchanged forwarding, successful normalized completion, missing-ID/error/abort/cancellation negatives, private metadata-only receipt, and a bounded exact reviewable next launch packet. Explicit stop rule: if active version does not support custom fetch, do not bypass with global fetch patch or a newly implemented transport.

Only read-only seam inspection and this blocker documentation proceeded. No runtime code/test changes, test rerun, extension load, provider call, launch, profile/global config change, install, credential/session/private artifact access, staging, or commit. Historic VOID status/hash preserved. No partial implementation diff exists. This remains blocked, not accepted.

## Exact active runtime findings

Active installed versions from package metadata:

- `/home/z/.pi/agent/npm/node_modules/@earendil-works/pi-ai`: **0.79.10**.
- `/home/z/.pi/agent/npm/node_modules/@earendil-works/pi-coding-agent`: **0.79.10**.
- `/home/z/.pi/agent/npm/node_modules/pi-subagents`: **0.76.1**.
- Alternate global coding-agent 1.1.0 is not the active npm tree; no active claims should identify 1.1.0 as runtime.

Active seams checked:

- `pi-ai/dist/types.d.ts:34-84` defines `StreamOptions`. It contains signal, apiKey, onPayload, onResponse, headers, timeout/retry settings and other fields, but **no `fetch` property**. `SimpleStreamOptions` extends it at `:151-155`. `StreamFunction` returns the typed `AssistantMessageEventStream` at `:156`. Assistant messages carry optional `responseId` (`:211-223`). No `onProviderStreamEvent` option exists or dispatches.
- The active OpenAI Responses provider is exported as `@earendil-works/pi-ai/openai-responses` (package exports map to `dist/providers/openai-responses.js` and `.d.ts`), exposing `streamOpenAIResponses` and `streamSimpleOpenAIResponses`; `register()` registers them for API `openai-responses` (`openai-responses.js:125-143`). Its provider-facing Copilot behavior is internal to this generic Responses adapter: it branches on `model.provider === "github-copilot"` for request headers (`:148-155`) and constructs the OpenAI client directly (`:145-179`). There is **no installed `githubCopilotProvider` factory export/source** in active pi-ai or coding-agent dist, despite the current extension's import statement.
- `createClient()` calls `new OpenAI({apiKey, baseURL, dangerouslyAllowBrowser, defaultHeaders})` at `openai-responses.js:173-178`; it does not pass a custom `fetch`. Grep of active pi-ai/coding-agent dist and the pi-ai package export map found no `githubCopilotProvider` declaration/export. Consequently neither a provider factory wrapper nor the existing StreamOptions custom-fetch pattern works in this exact runtime.
- Supported normalized stream seam is real: active `AssistantMessageEventStream` declaration (`utils/event-stream.d.ts:2-20`) implements `AsyncIterable`, `result()`, and its concrete class; source (`utils/event-stream.js:64-74`) resolves result on `done` to the `done.message` or to `error.error`. Active Responses adapter pushes normalized `done` with message and separately pushes `error` (`openai-responses.js:98-120`). This is a viable future response-ID observation seam, but by itself cannot establish the required actual serialized Request body/unchanged forwarding.
- `onPayload` and `onResponse` are supported declared callbacks (`types.d.ts:56-64`); the former observes/replaces pre-send structured payload, not actual serialized body. `onResponse` carries status/headers after HTTP response and before consuming body, not fetch input. Neither meets the mandatory fetch-boundary request proof.

## Genuine blocker and scope boundary

The required test must exercise the actual installed GitHub Copilot Responses implementation with a stub fetch, observe the serialized Request and exact forwarding, and link it to normalized completion. The active version gives no supported custom fetch injection to that implementation. User expressly disallowed global `fetch` patching, live provider invocation, installed monkeypatch/package/config changes, and a bespoke transport workaround; supervisor confirmed stop without any of those. Therefore the central acceptance criteria cannot be tested safely and no source repair is represented as complete.

The prior 14 offline tests and prior reviews tested fake provider/fetch seams and parent-correlation helper. They remain historical tests of those helpers, not installed-runtime integration evidence and not proof that the active extension could observe request bytes. No tests were added/changed, and none were run in this blocked leaf. Historical delivery remains VOID; preserve answer hash `e7187fb556ba86d55b5efe5e7c369325af53da720999e39aa162e0690948ef03` without score or interpretation.

## Current frozen control/launch constraints; not an executable packet

The inactive template currently records target `github-copilot/gpt-6-luna` / `openai-responses`, control SHA-256 `2bbbf061ea4a16fef3d0a692e40638989eb08cb5529bdc51b252451964fd8ed0`, 3002 bytes, one image attempt, at most three non-image setup requests, and native 120000ms bounded run constraints. These remain frozen facts only. Because the runtime proof is blocked, the template is **not a reviewable/approved launch packet** and must not be loaded or used. Its `deliveryEvidenceCore=63e8e27ecc2e9245c22cdb18fc76ac2456bd7944ca43ec08b32695182b147f02` and `deliveryEvidenceExtension=30f2ef52561862807ca8db694008e72980ff91a7df0ca2eb771a796d6fc2be49` revision pins describe prior source, not an active-runtime-qualified implementation. No new source revision pins are claimed.

## Bounded future choices and residual risks

At most two distinct paths for the parent to consider; neither is authorized/implemented here:

1. Obtain explicit covering authorization for a supported isolated runtime/provider seam that permits custom fetch, then repeat independent review and actual-export offline integration against that exact pinned runtime. This changes infrastructure/scope and cannot be inferred from current authority.
2. Explicitly revise delivery acceptance to use existing `onPayload`/`onResponse` plus independent perception. This would prove a pre-send transformed payload and HTTP response, **not serialized Request bytes handed to fetch**, would not meet the current frozen fetch-boundary criterion, and cannot retroactively qualify prior VOID evidence.

No global fetch patch, install/upgrade, custom network transport, CLI fallback, real provider request, or new probe is permitted by this result. Ex28 remains VOID/IMAGE BLOCKED; formal board/private mapping remain untouched.

## Commands and evidence limits

Read-only inspection commands used (all completed within 120s): active package metadata read; `nl -ba` over active `types.d.ts`, `openai-responses.js`, and `utils/event-stream.{d.ts,js}`; `rg` for `githubCopilotProvider` and `fetch` across active pi-ai/coding-agent dist and pi-ai package map. One attempted guessed import path `@earendil-works/pi-ai/providers/github-copilot` failed because that subpath is not in the active package exports; this is corroborated by its complete `package.json` exports list and successful separate source/export searches. No active provider was invoked. No full session/transcript, credentials, private key/mapping, or formal board read.
