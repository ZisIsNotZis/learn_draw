# Superseded handoff (historical)

The previous version of this brief mistakenly prescribed projecting a 3D model to 2D anchors and
**manually** marking occlusion intervals. The user rejected that interpretation: the intended
system keeps each component's artwork in local 2D on a plane or 3D curve, and the engine resolves
occlusion automatically from depth. Do not use the former prescription.

**Current architecture and experiment:** [`spatial-model.md`](spatial-model.md) and
[`../../STATUS.md`](../../STATUS.md). The original text is recoverable in Git history; historical
iteration observations remain in `.scratch/13-assembly/log.md`.
