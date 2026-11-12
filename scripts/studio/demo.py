"""A reproducible observed edit sequence, distinct from visual acceptance."""
from pathlib import Path

from .model import accept, fingerprint, preview, read, select, undo, write
from .render import bundle


def run(directory, png=True):
    from .__main__ import default_scene
    directory = Path(directory)
    working = directory / "working.json"
    if working.exists():
        raise ValueError("demo working scene already exists; choose a fresh output directory")
    base = default_scene()
    write(working, base)
    initial = select(base, "cheek-lock")
    reports = [bundle(base, directory / "01-default", initial, png=png)]
    a = preview(base, initial, "right", .18,
                "The inner edge is too straight through the middle; tuck it inward while preserving root and tip")
    reports.append(bundle(a["scene"], directory / "02-tuck", initial, base, png))
    write(directory / "02-tuck/candidate.json", a)
    accept(working, a)
    revised = select(read(working), "cheek-lock")
    b = preview(read(working), revised, "left", .06,
                "The tuck makes the middle slightly pinched; ease the inner arc back while keeping some curvature")
    reports.append(bundle(b["scene"], directory / "03-ease-back", revised, read(working), png))
    write(directory / "03-ease-back/candidate.json", b)
    accept(working, b)
    final_hash = fingerprint(read(working))
    undo(working)
    if fingerprint(read(working)) != a["result"]:
        raise RuntimeError("undo did not recover the first edit")
    accept(working, b)
    if fingerprint(read(working)) != final_hash:
        raise RuntimeError("reaccept did not recover the final edit")
    summary = dict(revisions=[r["revision"] for r in reports], undo_reaccept_verified=True,
                   reference=None, metrics="edge-F1/colour-distance: not applicable to an original primitive study",
                   visual_acceptance="unverified; inspect the images independently")
    write(directory / "sequence.json", summary)
    return summary
