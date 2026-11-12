"""A reproducible observed edit sequence, distinct from visual acceptance."""
from pathlib import Path

from .model import accept, fingerprint, parameter_preview, preview, read, select, undo, write
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


def run_head(directory,png=True):
    """A high-level recipe and a child curve use the same recoverable edit loop."""
    from .__main__ import default_scene
    directory=Path(directory);working=directory/'working.json'
    if working.exists():
        raise ValueError('demo working scene already exists; choose a fresh output directory')
    base=default_scene('head');write(working,base)
    reports=[bundle(base,directory/'01-default',select(base,feature='eyes'),png=png)]
    steps=[]
    scene=base
    for name,feature,parameter,value,direction,amount,reason in (
        ('02-eyes','eyes','eye_scale',.92,None,None,'Use quieter eye proportions while preserving face and haircut'),
        ('03-temple-lock','right-lock',None,None,'left',.12,'Reduce the right outer lock fullness; retain its root and tip'),
        ('04-palette','hair','hair_color','#7c5369',None,None,'Try a warm plum hair palette without changing its contours')):
        selection=select(scene,feature=feature,side='right')
        candidate=parameter_preview(scene,selection,parameter,value,reason) if parameter else preview(scene,selection,direction,amount,reason)
        reports.append(bundle(candidate['scene'],directory/name,selection,scene,png))
        write(directory/name/'candidate.json',candidate|dict(status='ready'))
        accept(working,candidate)
        steps.append(candidate);scene=candidate['scene']
    final=fingerprint(scene)
    for _ in steps:
        undo(working)
    if fingerprint(read(working))!=fingerprint(base):
        raise RuntimeError('mixed edit undo did not restore the original scene')
    for candidate in steps:
        accept(working,candidate)
    if fingerprint(read(working))!=final:
        raise RuntimeError('mixed edit replay did not restore the final scene')
    summary=dict(revisions=[r['revision'] for r in reports],undo_replay_verified=True,
                 reference=None,default='user accepted the simple flat-cartoon preset direction',
                 limits='variants and complete artwork are not human-approved; no 3D head rotation claim')
    write(directory/'sequence.json',summary)
    return summary
