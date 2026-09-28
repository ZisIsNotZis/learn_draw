# Active work — spatial structural drawing

Status: **S0 tested opaque-triangle proof complete; S1 coarse figure is a probe, NOT accepted.**
Owner: local session. Branch: `master` (check current HEAD and worktree before resuming).
Architecture: `docs/drawing/spatial-model.md`; current state: `STATUS.md`.

## Delivered experiment

- `scripts/vector_visibility.py`: orthographic projected-triangle clipping by interpolated
  depth plane; author never marks visibility intervals.
- `scripts/spatial_sketch.py`: one continuous local-2D-striped loop and torso, two cameras.
  `.scratch/13-assembly/evidence/spatial-sketch.svg` / `.png`.
- `scripts/figure_scaffold.py`: coarse seated person, one twisting hair sheet whose visible face
  chooses mint/blue, one bow-attached continuous ribbon. Two-view Preview:
  `.scratch/13-assembly/evidence/figure-scaffold.png`.

## Validation / limitations

Tests: `scripts/tests/test_spatial_sketch.py`, `test_figure_scaffold.py`; old smoke tests must
still pass. Re-run after any edit. The renderer is a slow triangle-mesh *reference prototype*;
intersections/tangencies and seams are not production-proven. The figure is recognizable as a
coarse person but **not independently reviewed** and is not a reference fit; the ribbon's actual
spatial route remains ambiguous to the user, and the current ellipse is merely a hypothesis.
Do not migrate this into `.scratch/13-assembly/work/spec.yaml` or call M4 done.

## Next step / stop

S1 gate: use labelled views and image reference to evaluate layout and attachment; obtain a
sight-proven small-VLM comprehension check when available. Fix actual incorrect depth/seam cases
with isolated tests. The next substantive choice—what path the reference ribbon actually follows
around the body—is **S2 parked** pending better reference evidence or the user's visual feedback;
do not tune to metrics or guess again. Preserve the accepted M4j hair drawing.
