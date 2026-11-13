"""Open either native held-prop example in a fresh editable inspection bundle."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,select
from scripts.studio.render import bundle

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',choices=('watering','flag'),default='watering')
    parser.add_argument('--outdir',required=True)
    args=parser.parse_args();out=Path(args.outdir).resolve()
    if out.exists():raise SystemExit('output directory exists; choose a fresh editable copy')
    filename='watering_grip.json' if args.scene=='watering' else 'held_flag.json'
    scene=read(Path(__file__).parent/filename)
    grip=next(n['id'] for n in scene['nodes'] if n['kind']=='grip')
    write(out/'working.json',scene)
    report=bundle(scene,out/'view',select(scene,grip,feature='anchors'))
    print(json.dumps(dict(scene=str(out/'working.json'),images=report['images'],engine=report['engine'])))

if __name__=='__main__':main()
