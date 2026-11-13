"""Check actual placement operations and retained art; tests do not judge artwork."""
from pathlib import Path
import hashlib,json,re,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,fingerprint,engine_fingerprint
from scripts.studio.attachment import resolve_scene,anchors
from scripts.studio.render import drawing,rasterize
HERE=Path(__file__).resolve().parent
ENGINE='6f3b918e9ee6dca625e031b8522eb0102e05f81354da8de902eee7d65a321ef4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    assert engine_fingerprint()==ENGINE
    base=read(ROOT/'examples/studio/held_flag.json');c=read(HERE/'03-badge-seated/candidate.json')
    assert c['base']==fingerprint(base) and c['engine']==ENGINE and c['status']=='ready'
    before=resolve_scene(base);after=resolve_scene(c['scene'])
    assert c['scene']['nodes'][:-1]==base['nodes']
    assert after['nodes'][:-1]==before['nodes']
    assert read(HERE/'working.json')==c['scene']
    assert read(HERE/'05-undone/scene.json')==base
    assert sha(HERE/'05-undone/artwork.png')==sha(ROOT/'evidence/studio-grasp-glyph/11-flag-continuous-pole/artwork.png')
    assert sha(HERE/'04-accepted/artwork.png')==sha(HERE/'06-restored/artwork.png')
    assert read(HERE/'07-extra-emblem/candidate.json')['base']==fingerprint(c['scene'])
    assert len(read(HERE/'07-extra-emblem/scene.json')['nodes'])==len(c['scene']['nodes'])+1
    # Pixel differences are a regression witness, never an art/target optimization.
    old=np.asarray(Image.open(HERE/'05-undone/artwork.png').convert('RGBA'))
    new=np.asarray(Image.open(HERE/'06-restored/artwork.png').convert('RGBA'))
    y,x=np.nonzero(np.any(old!=new,axis=2));box=read(HERE/'06-restored/report.json')['nodes']['sun-badge']['bounds']
    assert x.min()>=box[0]-2 and x.max()<=box[2]+2 and y.min()>=box[1]-2 and y.max()<=box[3]+2
    tests=(HERE/'tests.txt').read_text(encoding='utf-8-sig');count=int(re.search(r'Ran (\d+) tests',tests).group(1))
    assert count==110 and tests.rstrip().endswith('OK')
    preserve=read(HERE/'verification/preservation.json');assert preserve['engine']==ENGINE
    assert len(preserve['results'])==10 and all(r['prior_png_preserved'] for r in preserve['results'].values())
    actor=HERE/'usability';hashes={}
    for line in (actor/'HASHES.sha256').read_text(encoding='utf8').splitlines():
        digest,name=line.split('  ',1);assert sha(actor/name)==digest,name;hashes[name]=digest
    assert len(hashes)==155
    assert read(actor/'00-blank/scene.json')==read(actor/'03-undo-blank/scene.json')
    assert (actor/'00-blank/artwork.png').read_bytes()==(actor/'03-undo-blank/artwork.png').read_bytes()
    commands=read(actor/'commands.json');assert all(r.get('exit')==0 for r in commands)
    actions=[r['args'][0] for r in commands]
    assert all(x in actions for x in ('place','accept','undo','inspect'))
    assert any('--revise' in r['args'] and '--move' in r['args'] for r in commands)
    camera=read(ROOT/'examples/studio/camera.json');assert camera==read(actor/'working.json')
    assert len(camera['nodes'])==7
    svg=HERE/'verification/camera.svg';svg.write_text(drawing(camera),encoding='utf8');rasterize(svg,svg.with_suffix('.png'))
    assert sha(svg.with_suffix('.png'))==sha(actor/'11-final/artwork.png')
    assert read(actor/'09-strap-discard/candidate.json')['scene']!=camera
    result=dict(engine=ENGINE,studio_tests=count,prior_pngs_preserved=10,
        actual_added_node='sun-badge',previews_before_accept=['01-badge-default','02-badge-quiet','03-badge-seated'],
        existing_authored_and_resolved_nodes_exact=True,paint_difference_confined_to_badge=True,
        actual_undo_scene_and_png_exact=True,reaccept_png_exact=True,
        extra_emblem_discarded_without_scene_mutation=True,accepted_scene=fingerprint(c['scene']),
        png_sha256=sha(HERE/'06-restored/artwork.png'),
        actor_artifacts_checked=len(hashes),actor_original_camera_scene=fingerprint(camera),
        actor_camera_png_sha256=sha(actor/'11-final/artwork.png'),
        actor_blank_undo_scene_and_png_exact=True,shipped_camera_png_exact=True,
        actor_interrupted_attempt_historical_termination='unverified; operational audit retained; current process query empty',
        whole_artwork_pass=False)
    write(HERE/'verification/delivery.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':run()
