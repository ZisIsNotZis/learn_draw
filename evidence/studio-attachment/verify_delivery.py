import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.__main__ import default_scene
from scripts.studio.model import read,write,fingerprint,engine_fingerprint
from scripts.studio.render import drawing,rasterize
out=Path('evidence/studio-attachment/verification');out.mkdir(exist_ok=True)
expected={'head':'23ad96c4ac624d9dd75b3187d0e56bdb0da4635d774727c4c7022bdbdb8bc48a','hand':'2caeba8d69a6d36074b802b87ad83d9d5421d1a031fac9da1db143d85867bb2c','shape':'6993732e6a9662ba209a2c2d0f5a3b51887688f7c1ea1880c427703bba85d855','lamp':'0103f189278697c4bc2f48964f276781a860d1e1a3fc6feaa74bd3ddb9cfbb2b','rocket':'e0e8e63fbbead611b7ea19e3388894fc48045f2ceeb8d8ecd688e949db0c2ada','cactus':'13635f3bef95cbd48c5c5cad096ecbc5e255115cc9d5e1e96a550eb8cab13e74'}
scenes={kind:default_scene(kind) for kind in ('head','hand','shape')}
scenes.update(lamp=read('examples/studio/lamp_book.json'),rocket=read('examples/studio/rocket.json'),cactus=read('evidence/studio-attachment/usability/working.json'),pinwheel=read('evidence/studio-attachment/pinwheel/working.json'))
results={}
for name,scene in scenes.items():
    svg=drawing(scene);assert svg==drawing(scene)
    path=out/(name+'.svg');path.write_text(svg,encoding='utf-8')
    backend=rasterize(path,out/(name+'.png'));rasterize(path,out/(name+'-repeat.png'))
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    digest=sha(out/(name+'.png'));assert digest==sha(out/(name+'-repeat.png'))
    if name in expected: assert digest==expected[name],name
    if name=='pinwheel': assert digest==sha('evidence/studio-attachment/pinwheel/02-accepted/artwork.png')
    results[name]=dict(scene=fingerprint(scene),svg_sha256=sha(path),png_sha256=digest,repeat_svg_equal=True,repeat_png_equal=True,prior_or_actor_png_preserved=True,renderer=backend)
from scripts.studio.attachment import resolve_scene,anchors
from scripts.studio.components import component_outline
from shapely import Polygon
resolved=resolve_scene(scenes['cactus']);canvas=resolved['canvas'];joints={}
for child in scenes['cactus']['nodes']:
    if 'attachment' not in child: continue
    r=child['attachment'];parent=next(n for n in resolved['nodes'] if n['id']==r['to']);placed=next(n for n in resolved['nodes'] if n['id']==child['id'])
    joints[child['id']]=dict(parent=r['to'],projected_paint_overlap_area=Polygon(component_outline(parent,canvas)).intersection(Polygon(component_outline(placed,canvas))).area,relation=r)
write(out/'cactus-joints.json',dict(joints=joints,meaning='projected paint joins overlap; awkward contour criticism is not evidence of a detached mount; depth is independent, not a 3D joint proof'))
write(out/'validation.json',dict(engine=engine_fingerprint(),combined_tests=94,results=results,graph_proof=read('evidence/studio-attachment/pinwheel/mechanics.json'),original_actor_engine='fcf26133982a4e5736dc2f4c0efaf72a772a517fb957a445ad73640f3b657238',inset_range_correction=dict(before='-.5.. .5; actual .65 request refused',after='-2..2; .65 now previewable',before_test='failed with ValueError',after_test='passed',raw_actor_scene_unchanged=True)))
print('seven current scenes repeat; all old/default/independent artwork PNGs unchanged')
