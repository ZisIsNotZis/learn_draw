"""Rebuild the original flat watering illustration and begin an editable working copy."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.studio.model import read,write,select
from scripts.studio.render import bundle


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir',required=True,help='fresh directory for the working copy and views')
    parser.add_argument('--bound',action='store_true',help='keep both stream contacts attached during later edits')
    args=parser.parse_args();out=Path(args.outdir)
    if out.exists(): raise SystemExit('choose a fresh output directory; existing work is preserved')
    scene=read(Path(__file__).with_name('watering_bound.json') if args.bound else Path(__file__).with_suffix('.json'))
    out.mkdir(parents=True);write(out/'working.json',scene)
    report=bundle(scene,out/'view',select(scene,'water' if args.bound else 'carrying-hand',feature='object'))
    print('editable scene:',(out/'working.json').resolve())
    print('artwork:',(out/'view/artwork.png').resolve())
    print('stream detail:' if args.bound else 'grip detail:',(out/'view/object-closeup.png').resolve())
    print('report:',(out/'view/report.json').resolve())


if __name__=='__main__':main()
