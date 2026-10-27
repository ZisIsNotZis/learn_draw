# `.scratch/` — the record area

Everything here is a **record**: what was run, what it returned, which revision it was bound to, and
when. Records keep their dates, their commit ids and their dead links — a record that points at a path
which has since moved is a true statement about when it was written. Records are never edited to match
a later fact; a later fact lives in `docs/`.

Nothing here is a fact document. State, decisions and contracts live in `docs/`
(`docs/0_ROADMAP.md` owns where the project is), and a record is pointed at from there, never
duplicated into it.

## Shape

- `NN-slug/` — one directory per exercise. `spec.md` (what was asked), `work/` (in-flight plans and
  specs), `evidence/` (artifacts, renders, reviews, manifests), `log.md` (the run narrative),
  `ref/` (reference material).
- `NN-slug/evidence/…/README.md` — one package's own declaration: what it is, what it contains, the
  command that rebuilds it, and the hash that binds it. A package that does not name its own rebuild
  command and its own review image is defective, because the evidence and the thing it judges drift
  apart otherwise.
- `NN-slug/work/waveNN-contracts.md` — a wave's plan. It may already exist: read before writing at
  that path.
- `NN-slug/work/wave-log.md` — which packages a wave dispatched and what came back.
- `history/` — doc-shaped material that is no longer true or no longer binding: earlier versions of the
  roadmap and of the state file. It is kept for provenance, not for instruction.
- `00-tooling/baseline/` — **not a record**: the ratchet floor the project is measured against. One
  artifact, promoted only through `scripts/draw baseline` after a passed whole-drawing gate.

## Rules for a record

- One revision, one hash. A review names the artifact hash it judged, and the artifact that exists now
  must still be that hash; if it is not, the review's verdict does not carry over.
- Preserve failures. An attempt that failed stays, with its evidence, next to the attempt that
  replaced it.
- Never a second home for a fact that lives in `docs/`. A record says what happened; `docs/` says what
  is.
