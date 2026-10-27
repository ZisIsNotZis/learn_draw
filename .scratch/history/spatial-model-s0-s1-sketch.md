# Historical — the S0/S1 spatial sketch and assembly sequence

A record, kept because a newcomer may meet it cited. It is not current architecture: the architecture
is `docs/6_ARCHITECTURE.md`, and nothing here is a workflow, a gate or a validated result. Copied
verbatim out of the retired `docs/drawing/spatial-model.md` when the docs were migrated to levels.

## Historical S0/S1 sketch and assembly sequence (archival; not current workflow)

The former S0 technical exercise used a simple torso/lap occluder, one continuous bent ribbon
surface with a recognizable 2D stripe, and two camera views (reference-like and side/oblique); its
input represented the whole strip once. The retained `spatial_sketch.py` and `vector_visibility.py`
artifacts demonstrate bounded opaque-triangle visibility cases. `figure_scaffold.py` was a coarse S1
pose probe, not an approved reconstruction. Its technical success condition was automatic near/far
visibility change with viewpoint, no per-view redraw/manual visibility cuts, and preservation of the
strip's local `(u,v)` continuity. The historical sequence proposed adding a two-sided hair sheet and
coarse seated figure next, and cautioned against detailed character work at that stage. This records
the old technical sketch and its limited evidence; it is not a current R1 prerequisite, completed art
milestone, or direction to expand the old scaffold.

The associated former validation plan asked for separate attachment, projected silhouette,
crossing, generated-depth and object-identity inspection, plus small-VLM descriptions on held-out
views; it then proposed using the sketch to inform the legacy 2D assembly. That workflow is archival:
it does **not** authorize automatic progression from sketch to assembly, and it does not establish a
small-VLM, S1a readability, learner-transfer, or user-art acceptance pass. Record ambiguity about
reference-derived depth rather than claim unique recovered 3D truth. For current milestone work,
follow [`roadmap.md`](roadmap.md) and its linked concrete R1 contract for package ordering and gates;
actual-image readability/art review and user feedback remain separate, explicit gates. The spatial
architecture described above remains current: components are 2D art on support surfaces and engine
depth determines visibility. Reference is a teacher, not runtime geometry; retain compact,
explainable authored construction rather than traced contours or a one-off fitted mesh.
