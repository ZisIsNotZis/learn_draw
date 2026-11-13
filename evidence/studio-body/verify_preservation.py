"""Recheck old artwork bytes in this unit's directory, never rewrite old evidence."""
import hashlib,json,sys,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.__main__ import default_scene
from scripts.studio.model import read,write,engine_fingerprint
from scripts.studio.render import drawing,rasterize
HERE=Path(__file__).resolve().parent

def run(destination=None):
    expected={'head':'23ad96c4ac624d9dd75b3187d0e56bdb0da4635d774727c4c7022bdbdb8bc48a',
        'hand':'2caeba8d69a6d36074b802b87ad83d9d5421d1a031fac9da1db143d85867bb2c',
        'shape':'6993732e6a9662ba209a2c2d0f5a3b51887688f7c1ea1880c427703bba85d855',
        'lamp':'0103f189278697c4bc2f48964f276781a860d1e1a3fc6feaa74bd3ddb9cfbb2b',
        'rocket':'e0e8e63fbbead611b7ea19e3388894fc48045f2ceeb8d8ecd688e949db0c2ada',
        'cactus':'13635f3bef95cbd48c5c5cad096ecbc5e255115cc9d5e1e96a550eb8cab13e74'}
    cases={k:default_scene(k) for k in ('head','hand','shape')}
    cases.update(lamp=read(ROOT/'examples/studio/lamp_book.json'),rocket=read(ROOT/'examples/studio/rocket.json'),
        cactus=read(ROOT/'evidence/studio-attachment/usability/working.json'),pinwheel=read(ROOT/'evidence/studio-attachment/pinwheel/working.json'))
    cases.update(flag=read(ROOT/'examples/studio/held_flag.json'),watering=read(ROOT/'examples/studio/watering_grip.json'),grip=default_scene('grip'))
    expected.update(flag='e8e195a8998113074e973f14bd249bdee9b5e152d75dcf0ebb247abd97548cee',watering='05830e421a4f967708953a3f4b463bad48b5fadf77d2b34396349950086cc30a',grip='823240384f7835b89a85161c9ceca9055655eee71d5a1dc0cfd30453d7f0e8d4')
    expected['pinwheel']=hashlib.sha256((ROOT/'evidence/studio-attachment/pinwheel/02-accepted/artwork.png').read_bytes()).hexdigest()
    out=Path(destination) if destination else HERE/'verification'
    if destination and (out/'preservation.json').exists():raise SystemExit('preservation record exists')
    out.mkdir(parents=True,exist_ok=True);results={}
    for name,scene in cases.items():
        p=out/(name+'.svg');p.write_text(drawing(scene),encoding='utf8');rasterize(p,out/(name+'.png'))
        sha=hashlib.sha256((out/(name+'.png')).read_bytes()).hexdigest();assert sha==expected[name],name
        results[name]=dict(png_sha256=sha,prior_png_preserved=True)
    write(out/'preservation.json',dict(engine=engine_fingerprint(),results=results))
    print('Ten prior/default PNGs preserved exactly.',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--outdir');run(parser.parse_args().outdir)
