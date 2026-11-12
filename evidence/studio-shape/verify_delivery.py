import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.__main__ import default_scene
from scripts.studio.model import read,write,fingerprint,engine_fingerprint
from scripts.studio.render import drawing,rasterize
out=Path('evidence/studio-shape/verification');out.mkdir(exist_ok=True)
results={}
scenes=[('default',default_scene('shape')),('coast',read('examples/studio/coast.json')),('head-default',default_scene('head')),('hand-default',default_scene('hand')),('independent-lamp',read('evidence/studio-shape/usability/lamp-book.json')),('assisted-lamp',read('evidence/studio-shape/thin-line-repair/working.json'))]
for name,scene in scenes:
    first=drawing(scene);assert first==drawing(scene)
    path=out/(name+'.svg');path.write_text(first,encoding='utf-8')
    backend=rasterize(path,out/(name+'.png'));rasterize(path,out/(name+'-repeat.png'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(out/(name+'.png'))==sha(out/(name+'-repeat.png'))
    results[name]=dict(scene=fingerprint(scene),svg_sha256=sha(path),png_sha256=sha(out/(name+'.png')),repeat_svg_equal=True,repeat_png_equal=True,renderer=backend)
assert results['head-default']['png_sha256']=='23ad96c4ac624d9dd75b3187d0e56bdb0da4635d774727c4c7022bdbdb8bc48a'
assert results['hand-default']['png_sha256']=='2caeba8d69a6d36074b802b87ad83d9d5421d1a031fac9da1db143d85867bb2c'
assert results['coast']['png_sha256']==hashlib.sha256(Path('evidence/studio-shape/05-cliff-accepted/artwork.png').read_bytes()).hexdigest()
write('examples/studio/shape.json',default_scene('shape'))
write(out/'validation.json',dict(engine=engine_fingerprint(),combined_tests=79,previous_cpu_smoke_checks=81,results=results))
print(json.dumps(results,indent=2))
