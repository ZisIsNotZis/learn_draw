"""Render a fresh current-engine direction proposal without touching the original art history."""
from pathlib import Path
import json,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,engine_fingerprint
HERE=Path(__file__).resolve().parent;OUT=HERE/'verification-current/aim'
def run(*args):
 command=[sys.executable,'-m','scripts.studio',*map(str,args)]
 def record(data):
  with (OUT/'commands.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(data)+'\n')
 record(dict(status='started',command=command))
 p=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 record(dict(status='spawned',pid=p.pid,command=command))
 out,err=p.communicate();record(dict(status='terminal',pid=p.pid,exit=p.returncode,stdout=out.decode('utf8'),stderr=err.decode('utf8')))
 if p.returncode:raise RuntimeError(err.decode('utf8'))
if __name__=='__main__':
 if OUT.exists():raise SystemExit('current proposal record exists')
 OUT.mkdir(parents=True);p=OUT/'working.json';before=read(HERE/'layered-working.json');write(p,before)
 run('inspect',p,'--object','reaching-sleeve','--feature','tip','--outdir',OUT/'source')
 run('inspect',p,'--object','flower-hand','--feature','anchors','--anchor','wrist','--outdir',OUT/'target')
 run('preview',p,'--selection',OUT/'source/selection.json','--aim',OUT/'target/selection.json','--reason','Confirm the same observed cuff fit on the guide-contrast revision','--outdir',OUT/'fit')
 c=read(OUT/'fit/candidate.json');assert c['status']=='ready' and c['engine']==engine_fingerprint()
 assert c['result']==read(HERE/'03-sleeve-aim/candidate.json')['result']
 assert (OUT/'fit/artwork.png').read_bytes()==(HERE/'03-sleeve-aim/artwork.png').read_bytes()
 assert read(p)==before
 write(OUT/'verification.json',dict(engine=engine_fingerprint(),status='ready',result=c['result'],
     clean_png_exact_to_v1=True,working_unchanged=True,commands_terminal=3,accepted=False))
 print('Fresh current-engine aim ready; clean PNG and canonical result match v1 exactly.',flush=True)
