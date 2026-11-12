"""python -m scripts.studio: inspect, preview, accept and undo semantic part edits."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .model import accept, fingerprint, parameter_preview, preview, read, select, undo, validate, write
from .render import bundle


def default_scene(kind='hair-lock'):
    if kind=='head':
        return dict(format='learn-draw/studio-1',canvas=[640,640],background='#f5eee4',nodes=[
            dict(id='portrait',kind='head',intent='a frontal flat cartoon head with a side-parted short haircut')])
    return {"format": "learn-draw/studio-1", "canvas": [640, 640], "background": "#f5eee4",
            "nodes": [{"id": "cheek-lock", "kind": "hair-lock",
                       "intent": "a soft blue lock swelling below the root and tapering to a pointed end"}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("new", help="create a head or lock from a useful preset; no path coordinates needed")
    p.add_argument("scene")
    p.add_argument('--kind',choices=('hair-lock','head'),default='hair-lock')
    p.add_argument('--id',help='optional semantic object name')
    p = sub.add_parser("demo", help="render a reproducible tuck/ease-back/undo sequence")
    p.add_argument("--outdir", required=True)
    p.add_argument('--kind',choices=('head','hair-lock'),default='hair-lock')
    p.add_argument("--svg-only", action="store_true")
    for command in ("inspect", "preview"):
        p = sub.add_parser(command, help="inspect a revision-bound edge" if command == "inspect" else "preview a local push without overwriting the working scene")
        p.add_argument("scene")
        p.add_argument("--outdir", required=True)
        p.add_argument("--svg-only", action="store_true")
        if command == "inspect":
            p.add_argument("--object",help='inferred when the scene contains one object')
            p.add_argument('--feature',help='head: object/eyes/face/hair/left-lock/right-lock; lock: object or an edge')
            p.add_argument("--side", choices=("left", "right"), default="left")
            p.add_argument("--at", type=float, default=.55)
            p.add_argument("--radius", type=float, default=.30)
        else:
            p.add_argument("--selection", required=True)
            operation=p.add_mutually_exclusive_group(required=True)
            operation.add_argument("--move", choices=("left", "right", "up", "down"))
            operation.add_argument('--set',dest='parameter',help='a semantic control exposed by inspect')
            p.add_argument('--value',help='numeric value, hairstyle name or hex colour for --set')
            p.add_argument("--amount", type=float, default=.10, help="fraction of this lock's nominal full width (default .10)")
            p.add_argument("--reason", required=True)
    p = sub.add_parser("accept", help="accept only if the scene still matches the preview base")
    p.add_argument("scene")
    p.add_argument("candidate")
    p = sub.add_parser("undo", help="restore the previous accepted scene exactly")
    p.add_argument("scene")
    args = parser.parse_args()
    try:
        if args.command == "demo":
            from .demo import run,run_head
            print(json.dumps((run_head if args.kind=='head' else run)(args.outdir,not args.svg_only)))
        elif args.command == "new":
            if Path(args.scene).exists():
                raise ValueError("scene already exists; choose a new path")
            scene=default_scene(args.kind)
            if args.id:
                scene['nodes'][0]['id']=args.id
            validate(scene)
            write(args.scene, scene)
            print(json.dumps(dict(scene=args.scene, revision=fingerprint(scene))))
        elif args.command == "inspect":
            scene = validate(read(args.scene))
            selection = select(scene, args.object, args.side, args.at, args.radius,args.feature)
            report = bundle(scene, args.outdir, selection, png=not args.svg_only)
            print(json.dumps(report))
        elif args.command == "preview":
            scene = validate(read(args.scene))
            selection=read(args.selection)
            if args.parameter:
                if args.value is None:
                    raise ValueError('--set requires --value')
                candidate=parameter_preview(scene,selection,args.parameter,args.value,args.reason)
            else:
                if args.value is not None:
                    raise ValueError('--value is used with --set')
                candidate = preview(scene,selection, args.move, args.amount, args.reason)
            write(Path(args.outdir)/'candidate.json',dict(status='rendering',base=candidate['base'],engine=candidate['engine']))
            report = bundle(candidate["scene"], args.outdir, candidate["selection"], previous=scene, png=not args.svg_only)
            write(Path(args.outdir) / "candidate.json",candidate|dict(status='ready'))
            print(json.dumps(report))
        elif args.command == "accept":
            print(accept(args.scene, read(args.candidate)))
        elif args.command == "undo":
            print(undo(args.scene))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(f"studio: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
