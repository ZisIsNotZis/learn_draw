import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.__main__ import default_scene
from scripts.studio.model import read,write,fingerprint,engine_fingerprint
from scripts.studio.render import drawing,rasterize
out=Path('evidence/studio-hand/verification');out.mkdir(exist_ok=True)
results={}
for name,scene in [('default',default_scene('hand')),('greeting',read('evidence/studio-hand/usability/greeting.json')),('head-default',default_scene('head'))]:
    first=drawing(scene);second=drawing(scene)
    assert first==second
    path=out/(name+'.svg');path.write_text(first,encoding='utf-8')
    backend=rasterize(path,out/(name+'.png'))
    rasterize(path,out/(name+'-repeat.png'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(out/(name+'.png'))==sha(out/(name+'-repeat.png'))
    results[name]=dict(scene=fingerprint(scene),svg_sha256=sha(path),png_sha256=sha(out/(name+'.png')),repeat_svg_equal=True,repeat_png_equal=True,renderer=backend)
assert results['head-default']['png_sha256']=='23ad96c4ac624d9dd75b3187d0e56bdb0da4635d774727c4c7022bdbdb8bc48a'
assert results['greeting']['png_sha256']==hashlib.sha256(Path('evidence/studio-hand/usability/18-final-reinspect/artwork.png').read_bytes()).hexdigest()
write('examples/studio/hand.json',default_scene('hand'))
write('examples/studio/greeting.json',read('evidence/studio-hand/usability/greeting.json'))
write(out/'validation.json',dict(engine=engine_fingerprint(),unit_tests=71,cpu_smoke_checks=81,art_gate='not a whole-artwork pass',results=results))
print(json.dumps(results,indent=2))
