# Ex29 isolated native-runner runtime resolution — blocked

## Interpretation, scope, and outcome

Read-only inspection of the installed active pi-subagents 0.76.1 runner/configuration and installed Pi package metadata; documentation-only update. Preserve the Ex29 frozen delivery gate and prior VOID evidence. No runner launch, extension load, provider call, source/config/runtime edit, install, network, stage, or commit occurred. The actionable result is a genuine blocker: this version exposes no per-agent or per-run supported Pi SDK/package-root selection for native children. The installed alternate Pi 1.1.0 cannot be selected by a supported isolated native-runner setting.

## Source evidence

`pi-subagents/src/runs/background/async-execution.js:75-76` resolves the npm Pi package root once at module scope, in order: package containing the active process entrypoint, explicit `PI_SUBAGENTS_PI_CODING_AGENT_PACKAGE_ROOT` environment override, then installed package resolution. At launch (`:428-429, 471-476`) it chooses the runner executable from the existing host and constructs the child environment with `PI_CODING_AGENT_PACKAGE_ROOT` and `PI_PACKAGE_DIR` set to that resolved same root. No per-agent/run field participates. The matching source resolver in `src/runs/shared/pi-spawn.js:28-38` discovers the package containing the active entrypoint; config/frontmatter documentation (`docs/tool-reference.md`, `docs/agents.md`) describes runner type and agent controls but no SDK/runtime version selector. `PI_SUBAGENTS_PI_CODING_AGENT_PACKAGE_ROOT` is a process-level resolver override, not an isolated per-run choice; the launcher resolves and forwards it as the child host package root. It is not authorization or proof that the alternate host is compatible with active pi-subagents.

The alternate global `@earendil-works/pi-coding-agent` is 1.1.0 and its dependency range requires pi-ai `^1.1.0`; active Pi is 0.79.10 with pi-ai `^0.79.10`. A supported fetch/provider seam in the alternate package does not establish compatibility with pi-subagents 0.76.1, and the native runner does not expose a package namespace selector. External CLI is not an acceptable substitute under this task's frozen native-runner condition.

## Preferred route and exact authority needed

Stop here and request a concrete runtime-integration-maintainer proposal/authorization for a **separately isolated, supported native-runner runtime-resolution feature** (or an explicitly versioned compatible runtime bundle) before implementation. Authorization must name exact files/packages/configuration, supported compatibility pins and dependency treatment, and explicitly cover any dependency install/upgrade and global-vs-project scope. No inferred NODE_PATH, environment hack, package edit, foreground/CLI fallback, replacement transport, or options.onPayload acceptance substitution. If the owner cannot authorize a compatible supported integration without installation, no viable route exists in the current installed state; Ex29 stays frozen/blocked.

After authorization, bounded offline validation only: verify resolution selects the pinned package solely for the designated native child while parent/current default remains unchanged; test native startup and extension registration/protocol, cancellation/deadline, and exact serialized fetch-boundary forwarding with stub fetch; assert no global fetch/config mutation, no fallback, and compatibility of pi-subagents hooks/protocol. No provider call or acceptance relaxation. Roll back only the authorized isolated integration/config and its newly created artifacts. Actual delivery qualification remains separately gated by the frozen proof and independent review; this seam proposal is not a PASS.

## Limits

No proof was obtained that pi-subagents 0.76.1 supports alternate 1.1.0 SDK integration; source shows it does not provide a per-run selector. No package compatibility matrix or approved integration design was found in inspected runner/config docs. Historic VOID/hash, vendor dirt, and staging state are untouched; this note adds no delivery evidence and authorizes no run.
