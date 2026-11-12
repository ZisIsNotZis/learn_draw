"""Corroborate the independent reframe from actual authored scenes, not its prose verdict."""
import sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import numpy as np
from shapely import Polygon,Point
from scripts.studio.model import read,write,fingerprint,engine_fingerprint,node_by_id
from scripts.studio.attachment import resolve_scene
from scripts.studio.components import component_data,component_outline
from scripts.studio.render import drawing,rasterize
base=Path('evidence/studio-watering/usability');old=read(base/'source.json');new=read(base/'working.json');a=resolve_scene(old);b=resolve_scene(new);canvas=old['canvas']
assert old==read('examples/studio/watering.json')
unchanged=['window-frame','window-glass','window-upright','window-crossbar','sill','plant-pot','plant-stem','soil']+['leaf-'+str(i+1) for i in range(4)]
translated=['gardener','neck','shirt','resting-sleeve','reaching-sleeve','carrying-hand','can-body','can-handle','spout','grip-thumb','grip-fold']
for sid in unchanged:
    assert node_by_id(old,sid)==node_by_id(new,sid)
    assert np.allclose(component_outline(node_by_id(a,sid),canvas),component_outline(node_by_id(b,sid),canvas),rtol=0,atol=1e-8)
for sid in translated:
    pa=np.array(component_outline(node_by_id(a,sid),canvas));pb=np.array(component_outline(node_by_id(b,sid),canvas));assert np.allclose(pb-pa,[-36,0],rtol=0,atol=1e-7),sid
water=component_data(node_by_id(b,'water'),canvas);spout=component_data(node_by_id(b,'spout'),canvas);soil=Polygon(component_outline(node_by_id(b,'soil'),canvas))
assert np.allclose(water.rows[0].spine,spout.rows[-1].spine)
assert soil.covers(Point(*water.rows[-1].spine))
out=Path('evidence/studio-watering/verification');p=out/'independent-reframe.svg';p.write_text(drawing(new),encoding='utf-8');rasterize(p,out/'independent-reframe.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(out/'independent-reframe.png')==sha(base/'final/artwork.png')
write(out/'independent-reframe.json',dict(engine=engine_fingerprint(),source=fingerprint(old),result=fingerprint(new),unchanged_nodes=unchanged,translated_nodes=translated,translation=[-36,0],water_root_coincides_with_spout=True,water_tip_inside_actual_soil=True,png_sha256=sha(out/'independent-reframe.png'),actor_png_preserved=True,scope='actual bounded reframe and terminal repair corroborated; not new whole-scene creative transfer or aesthetic acceptance'))
print('12 stationary parts preserved, 11 held parts translate exactly, repaired water root/soil landing verified, actor PNG repeats')
