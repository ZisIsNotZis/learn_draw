import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.__main__ import default_scene
from scripts.studio.model import read,write,fingerprint,engine_fingerprint
from scripts.studio.render import drawing,rasterize
out=Path('evidence/studio-parameters/verification');out.mkdir(exist_ok=True)
results={}
expected={'head':'23ad96c4ac624d9dd75b3187d0e56bdb0da4635d774727c4c7022bdbdb8bc48a','hand':'2caeba8d69a6d36074b802b87ad83d9d5421d1a031fac9da1db143d85867bb2c','shape':'6993732e6a9662ba209a2c2d0f5a3b51887688f7c1ea1880c427703bba85d855'}
for name in expected:
    scene=default_scene(name);svg=drawing(scene);assert svg==drawing(scene)
    path=out/(name+'.svg');path.write_text(svg,encoding='utf-8')
    backend=rasterize(path,out/(name+'.png'));rasterize(path,out/(name+'-repeat.png'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(out/(name+'.png'))==sha(out/(name+'-repeat.png'))==expected[name]
    results[name]=dict(scene=fingerprint(scene),svg_sha256=sha(path),png_sha256=expected[name],repeat_svg_equal=True,repeat_png_equal=True,prior_default_preserved=True,renderer=backend)
lamp=read('evidence/studio-shape/usability/lamp-book.json')
lamp_svg=drawing(lamp);assert lamp_svg==drawing(lamp)
(out/'lamp.svg').write_text(lamp_svg,encoding='utf-8')
rasterize(out/'lamp.svg',out/'lamp.png')
assert sha(out/'lamp.png')=='0103f189278697c4bc2f48964f276781a860d1e1a3fc6feaa74bd3ddb9cfbb2b'
results['lamp-after-render-fix']=dict(scene=fingerprint(lamp),svg_sha256=sha(out/'lamp.svg'),png_sha256=sha(out/'lamp.png'),original_independent_png_preserved=True)
write(out/'validation.json',dict(engine=engine_fingerprint(),combined_tests=85,defaults=results,controlled_lamp_replay=read('evidence/studio-parameters/lamp-replay/comparison.json'),same_scene_rocket_render_repair=read('evidence/studio-parameters/rocket-clean/verification.json')))
print('current source repeats all three unchanged defaults; controlled lamp equality is recorded')
