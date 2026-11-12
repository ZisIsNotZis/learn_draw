"""Corroborate actual drawing revisions and the same free-ended negative control."""
import copy,hashlib,math,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import numpy as np
from shapely import Polygon,Point
from scripts.studio.model import read,write,select,preview,parameters_preview,unbind_endpoint_preview,node_by_id,engine_fingerprint,fingerprint
from scripts.studio.attachment import resolve_scene,get_anchor,mount_scale
from scripts.studio.components import component_data,component_outline
from scripts.studio.render import drawing,rasterize
out=Path('evidence/studio-endpoints/verification')
def data(s,id):return component_data(node_by_id(resolve_scene(s),id),s['canvas'])
def point(s,id,end):return np.array(data(s,id).rows[0 if end=='root' else -1].spine)
def target(s,id,end):
    r=node_by_id(s,id)['endpoints'][end];parent=node_by_id(resolve_scene(s),r['to']);a=get_anchor(parent,s['canvas'],r.get('target','center'));normal=a['normal'] or [0,0]
    return np.array(a['point'])-np.array(normal)*r.get('inset',0)*mount_scale(parent,s['canvas'])+np.array(r.get('offset',[0,0]))*min(s['canvas'])
def matches(s,id):
    for end in ('root','tip'):np.testing.assert_allclose(point(s,id,end),target(s,id,end),rtol=0,atol=1e-8)
old=read('examples/studio/watering.json');loose=preview(old,select(old,'gardener',feature='object'),'left',.05,'Negative control: original free landing')['scene']
np.testing.assert_allclose(point(loose,'water','tip')-point(old,'water','tip'),[-36,0],atol=1e-8)
bound=read('evidence/studio-endpoints/03-bound-stream/scene.json');moved=read('evidence/studio-endpoints/05-reframed-person/scene.json')
assert node_by_id(bound,'water')==node_by_id(moved,'water');matches(bound,'water');matches(moved,'water')
np.testing.assert_allclose(point(bound,'water','tip'),point(moved,'water','tip'),atol=1e-8)
np.testing.assert_allclose(point(moved,'water','root')-point(bound,'water','root'),[-36,0],atol=1e-8)
h0=read('evidence/studio-endpoints/09-two-ended-handle/scene.json');h1=read('evidence/studio-endpoints/11-vessel-tilt/scene.json');matches(h0,'can-handle');matches(h1,'can-handle')
assert node_by_id(h0,'can-handle')==node_by_id(h1,'can-handle')
free=unbind_endpoint_preview(h0,select(h0,'can-handle',feature='tip'),'Negative control: free handle tip')['scene']
free_tilt=parameters_preview(free,select(free,'can-body',feature='object'),{'angle':-50},'Apply the same vessel tilt')['scene']
drift=float(np.linalg.norm(point(free_tilt,'can-handle','tip')-target(h1,'can-handle','tip')));assert drift>1
final=read('evidence/studio-endpoints/working.json');matches(final,'water')
assert Polygon(component_outline(node_by_id(resolve_scene(final),'soil'),final['canvas'])).covers(Point(*point(final,'water','tip')))
p=out/'bound-example.svg';p.write_text(drawing(final),encoding='utf-8');rasterize(p,out/'bound-example.png');rasterize(p,out/'bound-example-repeat.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(out/'bound-example.png')==sha(out/'bound-example-repeat.png')==sha('evidence/studio-endpoints/13-open-landing/artwork.png')
write(out/'mechanics.json',dict(engine=engine_fingerprint(),scene=fingerprint(final),original_free_stream_drift=[-36,0],bound_stream_tip_fixed=True,stream_raw_node_unchanged_during_parent_move=True,handle_raw_node_unchanged_during_tilt=True,handle_free_tip_drift_from_intended_mount=drift,both_handle_mounts_follow=True,final_water_tip_inside_soil=True,repeat_png_equal=True,png_sha256=sha(out/'bound-example.png'),scope='projected named-target equality and repeatability; not art, fluid dynamics or grasp correctness'))
print('controlled free stream drifts36px; bound tip stays; both handle targets follow; final open-soil landing repeats')
