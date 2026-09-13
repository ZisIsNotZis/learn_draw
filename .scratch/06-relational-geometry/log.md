# iteration log

| iter | edge-F1 | color-dist | note |
|---|---|---|---|
| 1 | n/a | n/a | Prototype resolver + proof spec. `relate.py` resolves relations → absolute geometry with zero coordinate literals; 10 emitted nodes, hat = one spec line (`sunhat` vocabulary: squashed brim ellipse, dome on the brim normal, near edge over the crown, poms at `along(brim,t)`). `--anchors` prints the full resolved handle table. Diagnostics caught 2 real defects in bust v1: CONTRADICTION (declared hair in front of shoulders, but layers painted hair first) and CLIPPED (shoulders 68px past the frame edge). v2 after 3 word-level edits: diagnostics clean. Found and fixed a language bug — YAML 1.1 parses `on:`/`off:` as booleans; renamed to `along:`/`host:` and added a named error. Metrics not applicable (no reference comparison in this ticket by design — the engine must stay target-free). |

## Transferable lessons

- P18 the engine must not need the target; tracing is a teacher, never the engine
- P19 geometry by computation, semantics by eye (>4 coordinates ⇒ must be computed)
- P20 resolution order ≠ paint order; keeping them separate removes occlusion surgery
- P21 the engine reports in words (OFF-CANVAS / CLIPPED / SUB-PIXEL / CONTRADICTION)
