"""Verify actual independent constraint following and preserve newer inherited illustrations."""
import hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import numpy as np
from shapely import Polygon,Point
from scripts.studio.model import read,write,node_by_id,fingerprint,engine_fingerprint
from scripts.studio.attachment import resolve_scene,get_anchor,mount_scale
from scripts.studio.components import component_data,component_outline
from scripts.studio.render import drawing,rasterize
out=Path('evidence/studio-endpoints/verification');base=Path('evidence/studio-endpoints/usability')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ends(s):
    n=node_by_id(resolve_scene(s),'water');d=component_data(n,s['canvas']);return np.array([d.rows[0].spine,d.rows[-1].spine])
def check(s):
    resolved=resolve_scene(s)
    for i,end in enumerate(('root','tip')):
        r=node_by_id(s,'water')['endpoints'][end];parent=node_by_id(resolved,r['to']);a=get_anchor(parent,s['canvas'],r['target']);normal=a['normal'] or [0,0]
        expected=np.array(a['point'])-np.array(normal)*r.get('inset',0)*mount_scale(parent,s['canvas'])+np.array(r.get('offset',[0,0]))*min(s['canvas'])
        np.testing.assert_allclose(ends(s)[i],expected,atol=1e-8,rtol=0)
    assert Polygon(component_outline(node_by_id(resolved,'soil'),s['canvas'])).covers(Point(*ends(s)[1]))
bound=read(base/'04-bind-tip/scene.json');person=read(base/'06-gardener-left/scene.json');pot=read(base/'08-planter-right/scene.json');final=read(base/'working.json')
for s in (bound,person,pot,final):check(s);assert node_by_id(s,'water')==node_by_id(bound,'water')
np.testing.assert_allclose(ends(bound)[1],ends(person)[1],atol=1e-8);np.testing.assert_allclose(ends(person)[0],ends(pot)[0],atol=1e-8)
np.testing.assert_allclose(ends(pot)[1]-ends(person)[1],[18,0],atol=1e-8)
assert final==read(base/'bound-before-release.json')
released=read(base/'released.json');results={}
scenes=[('independent',final,base/'final/artwork.png'),('released',released,base/'11-released/artwork.png'),('legacy-watering',read('examples/studio/watering.json'),Path('evidence/studio-watering/27-softer-knuckles/artwork.png')),('legacy-reframe',read('evidence/studio-watering/usability/working.json'),Path('evidence/studio-watering/usability/final/artwork.png')),('default-stroke',__import__('scripts.studio.__main__',fromlist=['default_scene']).default_scene('stroke'),Path('evidence/studio-stroke/03-default/artwork.png'))]
for name,s,known in scenes:
    svg=drawing(s);assert svg==drawing(s);p=out/(name+'.svg');p.write_text(svg,encoding='utf-8');rasterize(p,out/(name+'.png'))
    assert sha(out/(name+'.png'))==sha(known),name
    results[name]=dict(scene=fingerprint(s),png_sha256=sha(known),observed_png_preserved=True)
assert sha(out/'independent.png')==sha(out/'released.png')
write(out/'actor-and-legacy.json',dict(engine=engine_fingerprint(),raw_water_unchanged_across_independent_moves=True,both_contacts_match_actual_targets=True,landing_inside_soil=True,release_exact_paint=True,undo_exact_scene=True,results=results,scope='independent operation corroboration and inherited picture preservation; not a new generation benchmark or artwork verdict'))
print('independent contacts persist with unchanged author node; release/undo exact; actor and newer legacy pictures preserved')
