# Historical — the similarity alarm's first readings

A record, copied out of the retired `docs/drawing/rubric.md`. The instrument and its rules are
`docs/2_GOAL.md`'s; this table is the calibration evidence it was first set against, and it is
history, not a threshold.

## Part III — the contextual similarity alarm (instrument, not a gate)

`scripts/similarity.py` computes a CLIP image-embedding cosine similarity between the draft and the
target (model: OpenAI `ViT-B-32`, 151M params, cached at `~/.cache/clip`). It is **contextual**, not
pixel-level, and it separates the project's own history cleanly:

| | cos to target |
| --- | --- |
| M3b (current) | **0.836** |
| M2 flat bust | 0.732 |
| M1 flat blobs | 0.637 |
| Starry probe (different subject) | 0.591 |
| random noise | 0.489 |

It is a **secondary alarm, never a gate** — the same reason the pixel metrics are alarms. A scalar
invites optimisation (P25), and a CLIP score is far easier to game than `edge_f1`: it measures
*semantic neighbourhood*, so a drawing can drift toward "anime girl with a hat" generally and the
number will rise while the drawing becomes less like the target. Use it to **catch regressions between
rubric rounds**, and to record history. Record the value in the log with each rubric review.
