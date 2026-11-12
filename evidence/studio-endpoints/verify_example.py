"""Check final bound helper output and overwrite refusal without regenerating history."""
import hashlib,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import read,write
base=Path.cwd();out=base/'evidence/studio-endpoints/verification/fresh-bound-focus'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert read(out/'working.json')==read('examples/studio/watering_bound.json')
assert sha(out/'view/artwork.png')==sha('evidence/studio-endpoints/13-open-landing/artwork.png')
selection=read(out/'view/selection.json');assert selection['object']=='water' and set(selection['endpoint_bindings'])=={'root','tip'}
assert not {'length','angle'}.intersection(selection['controls'])
before=sha(out/'working.json')
r=subprocess.run([sys.executable,str(base/'examples/studio/watering.py'),'--bound','--outdir',str(out)],cwd=base/'.tmp/endpoints-fresh-cwd',capture_output=True,text=True)
assert r.returncode!=0 and before==sha(out/'working.json')
write(base/'evidence/studio-endpoints/verification/example.json',dict(fresh_cwd_picture_preserved=True,both_pin_controls_visible=True,derived_controls_hidden=True,existing_output_preserved=True,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
print('fresh bound example matches observed picture, shows both pins, hides derived controls and protects existing work')
