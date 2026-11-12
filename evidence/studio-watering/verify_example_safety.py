"""Check the published helper in the already-created fresh-cwd artifact without overwriting it."""
import hashlib,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import write
base=Path.cwd();out=base/'evidence/studio-watering/verification/fresh-cwd';working=out/'working.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=sha(working)
r=subprocess.run([sys.executable,str(base/'examples/studio/watering.py'),'--outdir',str(out)],cwd=base/'.tmp/watering-fresh-cwd',capture_output=True,text=True)
assert r.returncode!=0
assert sha(working)==before
observed=sha(base/'evidence/studio-watering/27-softer-knuckles/artwork.png')
assert sha(out/'view/artwork.png')==observed
write(base/'evidence/studio-watering/verification/example-safety.json',dict(fresh_cwd_picture_preserved=True,png_sha256=observed,existing_directory_refused=True,existing_working_scene_sha256=before,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,scope='helper rebuild/overwrite refusal, not fresh artistic transfer'))
print('fresh-cwd picture identical; existing working copy preserved under refusal')
