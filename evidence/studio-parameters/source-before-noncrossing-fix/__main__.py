"""python -m scripts.studio: inspect, preview, accept and undo semantic part edits."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .model import accept, engine_fingerprint, fingerprint, parameter_preview, parameters_preview, preview, read, select, undo, validate, write
from .render import bundle


def default_scene(kind='hair-lock'):
    if kind=='shape':
        return dict(format='learn-draw/studio-1',canvas=[640,640],background='#f5eee4',nodes=[
            dict(id='colour-mass',kind='shape',intent='an editable rounded flat colour mass')])
    if kind=='hand':
        return dict(format='learn-draw/studio-1',canvas=[640,640],background='#f5eee4',nodes=[
            dict(id='greeting-hand',kind='hand',intent='a front-view flat cartoon open palm with five digits')])
    if kind=='landscape':
        return dict(format='learn-draw/studio-1',canvas=[960,640],background='#f5eee4',nodes=[
            dict(id='sky',kind='sky',intent='a quiet atmospheric sky with restrained detail'),
            dict(id='ridges',kind='hills',intent='three receding smooth ridges beneath the open sky')])
    if kind in ('sky','hills','moon','sun'):
        intents={'sky':'a quiet sky with restrained atmospheric detail','hills':'three receding smooth ridges',
                 'moon':'a warm moon above the horizon','sun':'a warm editable sun'}
        return dict(format='learn-draw/studio-1',canvas=[640,640],background='#f5eee4',nodes=[
            dict(id=kind,kind=kind,intent=intents[kind])])
    if kind=='head':
        return dict(format='learn-draw/studio-1',canvas=[640,640],background='#f5eee4',nodes=[
            dict(id='portrait',kind='head',intent='a frontal flat cartoon head with an editable hairstyle')])
    return {"format": "learn-draw/studio-1", "canvas": [640, 640], "background": "#f5eee4",
            "nodes": [{"id": "cheek-lock", "kind": "hair-lock",
                       "intent": "a soft lock swelling below the root and tapering to a pointed end"}]}


def canvas_arg(value):
    try:
        width,height=value.lower().split('x')
        return [int(width),int(height)]
    except ValueError:
        raise argparse.ArgumentTypeError('size must be integer WIDTHxHEIGHT') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    kinds=('hair-lock','head','hand','shape','sky','hills','moon','sun')
    p = sub.add_parser("new", help="create a useful preset; no path coordinates needed")
    p.add_argument("scene")
    p.add_argument('--kind',choices=kinds+('landscape',),default='hair-lock')
    p.add_argument('--id',help='optional semantic object name')
    p.add_argument('--size',type=canvas_arg,help='optional canvas WIDTHxHEIGHT, each 64–4096')
    p.add_argument('--background',help='optional paper colour #rrggbb')
    p = sub.add_parser('add',help='add a named preset object to an existing scene')
    p.add_argument('scene')
    p.add_argument('--kind',choices=kinds,required=True)
    p.add_argument('--id',help='defaults to the preset object name; must be unique')
    p.add_argument('--depth',type=float,help='optional explicit support depth; foreground parts otherwise start in front')
    p = sub.add_parser("demo", help="render a reproducible tuck/ease-back/undo sequence")
    p.add_argument("--outdir", required=True)
    p.add_argument('--kind',choices=('head','hair-lock'),default='hair-lock')
    p.add_argument("--svg-only", action="store_true")
    for command in ("inspect", "preview"):
        p = sub.add_parser(command, help="inspect a revision-bound feature or edge" if command == "inspect" else "preview a local push without overwriting the working scene")
        p.add_argument("scene")
        p.add_argument("--outdir", required=True)
        p.add_argument("--svg-only", action="store_true")
        if command == "inspect":
            p.add_argument("--object",help='inferred when the scene contains one object')
            p.add_argument('--feature',help='head: object/eyes/face/hair/expression/left-lock/right-lock; hand: object/index/middle/ring/little/thumb; lock: object or edge')
            p.add_argument("--side", choices=("left", "right"), default="left")
            p.add_argument("--at", type=float, default=.55)
            p.add_argument("--radius", type=float, default=.30)
        else:
            p.add_argument("--selection", required=True)
            operation=p.add_mutually_exclusive_group(required=True)
            operation.add_argument("--move", choices=("left", "right", "up", "down"))
            operation.add_argument('--set',dest='parameter',help='a semantic control exposed by inspect')
            operation.add_argument('--change',action='append',metavar='NAME=VALUE',help='repeat for one coherent multi-control preview; accept/undo as one edit')
            p.add_argument('--value',help='numeric value, hairstyle name or hex colour for --set')
            p.add_argument("--amount", type=float, default=.10, help="edge: lock width; object: shorter canvas dimension; digit tip: nominal digit span (default .10)")
            p.add_argument("--reason", required=True)
    p = sub.add_parser("accept", help="accept only if the scene still matches the preview base")
    p.add_argument("scene")
    p.add_argument("candidate")
    p = sub.add_parser("undo", help="restore the previous accepted scene exactly")
    p.add_argument("scene")
    args = parser.parse_args()
    try:
        if args.command in ('inspect','preview'):
            # A bundle exports scene.json, but a preview must never overwrite its
            # working source or selection even when the output directory is reused.
            output=Path(args.outdir)
            names=['scene.json','selection.json','report.json','report.txt','candidate.json']
            names += [name+suffix for name in ('artwork','alignment','object-closeup','edit-closeup') for suffix in ('.svg','.png')]
            inputs=[Path(args.scene)]
            if args.command=='preview': inputs.append(Path(args.selection))
            for source in inputs:
                for name in names:
                    target=output/name
                    if source.resolve()==target.resolve() or (source.exists() and target.exists() and source.samefile(target)):
                        raise ValueError('output would overwrite an input; choose a separate inspection/preview directory')
        if args.command == "demo":
            from .demo import run,run_head
            print(json.dumps((run_head if args.kind=='head' else run)(args.outdir,not args.svg_only)))
        elif args.command == "new":
            if Path(args.scene).exists():
                raise ValueError("scene already exists; choose a new path")
            scene=default_scene(args.kind)
            if args.size: scene['canvas']=args.size
            if args.background: scene['background']=args.background
            if args.id:
                if len(scene['nodes'])!=1: raise ValueError('--id applies to a single-object preset')
                scene['nodes'][0]['id']=args.id
            validate(scene)
            write(args.scene, scene)
            print(json.dumps(dict(scene=args.scene, revision=fingerprint(scene))))
        elif args.command=='add':
            scene=validate(read(args.scene))
            base=fingerprint(scene)
            node=default_scene(args.kind)['nodes'][0]
            if args.id: node['id']=args.id
            if args.depth is not None:
                node['depth']=args.depth
            elif args.kind in ('head','hand','hair-lock','shape'):
                from .components import depth_bounds
                canvas=scene.get('canvas',[640,640])
                node['depth']=max(depth_bounds(n,canvas)[1] for n in scene['nodes'])+1
            scene['nodes'].append(node)
            validate(scene)
            accept(args.scene,dict(base=base,engine=engine_fingerprint(),result=fingerprint(scene),scene=scene,
                                   operation=dict(action='add',object=node['id'],kind=node['kind'],reason=node['intent'])))
            print(json.dumps(dict(scene=args.scene,added=node['id'],revision=fingerprint(scene))))
        elif args.command == "inspect":
            scene = validate(read(args.scene))
            selection = select(scene, args.object, args.side, args.at, args.radius,args.feature)
            report = bundle(scene, args.outdir, selection, png=not args.svg_only)
            print(json.dumps(report))
        elif args.command == "preview":
            scene = validate(read(args.scene))
            # A new request supersedes the previous proposal even if its pose
            # proves invalid before rendering. Never leave an old ready edit
            # acceptable under the same preview-directory name.
            write(Path(args.outdir)/'candidate.json',dict(status='preparing',base=fingerprint(scene),engine=engine_fingerprint()))
            write(Path(args.outdir)/'report.json',dict(status='preparing',revision=fingerprint(scene),engine=engine_fingerprint(),images=[]))
            (Path(args.outdir)/'report.txt').write_text('',encoding='utf-8')
            selection=read(args.selection)
            if args.change:
                if args.value is not None:
                    raise ValueError('--change uses NAME=VALUE; --value is used with --set')
                changes={}
                for item in args.change:
                    if '=' not in item:
                        raise ValueError('--change requires NAME=VALUE')
                    name,value=item.split('=',1)
                    if not name or not value:
                        raise ValueError('--change requires a nonempty NAME and VALUE')
                    if name in changes:
                        raise ValueError('duplicate parameter in --change: '+name)
                    changes[name]=value
                candidate=parameters_preview(scene,selection,changes,args.reason)
            elif args.parameter:
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
