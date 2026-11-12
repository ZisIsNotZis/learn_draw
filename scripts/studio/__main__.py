"""python -m scripts.studio: inspect, preview, accept and undo semantic part edits."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .model import accept, fingerprint, preview, read, select, undo, validate, write
from .render import bundle


def default_scene():
    return {"format": "learn-draw/studio-1", "canvas": [640, 640], "background": "#f5eee4",
            "nodes": [{"id": "cheek-lock", "kind": "hair-lock",
                       "intent": "a soft blue lock swelling below the root and tapering to a pointed end"}]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("new", help="create a default hair lock; no path coordinates needed")
    p.add_argument("scene")
    p = sub.add_parser("demo", help="render a reproducible tuck/ease-back/undo sequence")
    p.add_argument("--outdir", required=True)
    p.add_argument("--svg-only", action="store_true")
    for command in ("inspect", "preview"):
        p = sub.add_parser(command, help="inspect a revision-bound edge" if command == "inspect" else "preview a local push without overwriting the working scene")
        p.add_argument("scene")
        p.add_argument("--outdir", required=True)
        p.add_argument("--svg-only", action="store_true")
        if command == "inspect":
            p.add_argument("--object", required=True)
            p.add_argument("--side", choices=("left", "right"), default="left")
            p.add_argument("--at", type=float, default=.55)
            p.add_argument("--radius", type=float, default=.30)
        else:
            p.add_argument("--selection", required=True)
            p.add_argument("--move", choices=("left", "right", "up", "down"), required=True)
            p.add_argument("--amount", type=float, required=True, help="fraction of this lock's nominal full width")
            p.add_argument("--reason", required=True)
    p = sub.add_parser("accept", help="accept only if the scene still matches the preview base")
    p.add_argument("scene")
    p.add_argument("candidate")
    p = sub.add_parser("undo", help="restore the previous accepted scene exactly")
    p.add_argument("scene")
    args = parser.parse_args()
    try:
        if args.command == "demo":
            from .demo import run
            print(json.dumps(run(args.outdir, not args.svg_only)))
        elif args.command == "new":
            if Path(args.scene).exists():
                raise ValueError("scene already exists; choose a new path")
            scene = validate(default_scene())
            write(args.scene, scene)
            print(json.dumps(dict(scene=args.scene, revision=fingerprint(scene))))
        elif args.command == "inspect":
            scene = validate(read(args.scene))
            selection = select(scene, args.object, args.side, args.at, args.radius)
            report = bundle(scene, args.outdir, selection, png=not args.svg_only)
            print(json.dumps(report))
        elif args.command == "preview":
            scene = validate(read(args.scene))
            candidate = preview(scene, read(args.selection), args.move, args.amount, args.reason)
            report = bundle(candidate["scene"], args.outdir, candidate["selection"], previous=scene, png=not args.svg_only)
            write(Path(args.outdir) / "candidate.json", candidate)
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
