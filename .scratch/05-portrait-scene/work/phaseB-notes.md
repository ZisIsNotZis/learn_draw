# Phase B scene survey

Probe: enumerate node ids and sizes in scene.yaml (cannot read large files wholesale; using find/ls + targeted writes to reason about structure).

Plan: a sibling worker (read+bash enabled) or the parent must extract node inventory. This agent's allowlist lacks read/bash — I can still author the REPLACEMENT YAML content from the task spec's explicit geometry, but I cannot see the current 142 nodes' ids, so deletion targets are unknown. Writing the replacement nodes to a fragment file for integration.
