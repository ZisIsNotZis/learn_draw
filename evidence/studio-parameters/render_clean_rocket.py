import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import numpy as np
from PIL import Image
from scripts.studio.model import read,write,fingerprint,select,engine_fingerprint
from scripts.studio.render import bundle,rasterize
scene=read('evidence/studio-parameters/usability/rocket.json');out=Path('evidence/studio-parameters/rocket-clean')
bundle(scene,out,select(scene,'right-fin',feature='object'))
a=np.asarray(Image.open('evidence/studio-parameters/usability/final/artwork.png').convert('RGBA'))
b=np.asarray(Image.open(out/'artwork.png').convert('RGBA'))
ref=np.asarray(Image.open('evidence/studio-parameters/fin-diagnosis/noncrossing-reference.png').convert('RGBA'))
assert np.array_equal(b,ref)
facts=read('evidence/studio-parameters/fin-diagnosis/facts.json')
for x,y,old in facts['examples']: assert tuple(b[y,x])==(188,97,80,255)
rasterize(out/'artwork.svg',out/'artwork-repeat.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(out/'artwork.png')==sha(out/'artwork-repeat.png')
write(out/'verification.json',dict(scene=fingerprint(scene),scene_unchanged=scene==read('evidence/studio-parameters/usability/rocket.json'),engine=engine_fingerprint(),source_engine='d8fd65d5c5ec971c35ad074cf388706d771d96a893c467a4da7a3c47004c1d6b',png_sha256=sha(out/'artwork.png'),repeat_png_equal=True,all_pixels_equal_proved_noncrossing_reference=True,old_unexpected_interior_pixels=facts['unexpected_deep_interior_pixels'],old_interior_defects_cleared=facts['cleared_by_proved_noncrossing_draw'],total_changed_pixels=int(np.count_nonzero(np.any(a!=b,axis=2))),boundary_antialias_can_change=True))
write('examples/studio/rocket.json',scene)
print(json.dumps(read(out/'verification.json'),indent=2))
