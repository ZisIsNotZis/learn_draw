import json,subprocess,sys,hashlib
from pathlib import Path
scene=Path('evidence/studio-shape/coast-refined/scene.json');candidate='evidence/studio-shape/04-cliff-proposal/candidate.json'
raw=scene.read_bytes();commands=[]
def run(*args):
    command=[sys.executable,'-m','scripts.studio',*args]
    result=subprocess.run(command,capture_output=True,text=True,check=True)
    commands.append(dict(command=command,stdout=result.stdout))
run('accept',str(scene),candidate)
accepted=scene.read_bytes()
run('undo',str(scene))
assert json.loads(raw)==json.loads(scene.read_bytes())
run('accept',str(scene),candidate)
assert json.loads(accepted)==json.loads(scene.read_bytes())
run('inspect',str(scene),'--object','rock-top','--feature','left','--at','.5','--radius','.3','--outdir','evidence/studio-shape/05-cliff-accepted')
Path('evidence/studio-shape/cliff-edit-record.json').write_text(json.dumps(dict(commands=commands,undo_exact_scene=True,replay_exact_scene=True),indent=2),encoding='utf-8')
print('accepted, exact semantic undo and replay verified')
