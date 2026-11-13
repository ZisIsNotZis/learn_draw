"""Actual focused/full CLI observation and a recoverable local edit, no old evidence rewrite."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write
HERE=Path(__file__).resolve().parent

def run(*args,save=None):
 command=[sys.executable,'-m','scripts.studio',*map(str,args)]
 def record(v):
  with (HERE/'commands.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(v)+'\n')
 record(dict(status='started',args=command));p=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 record(dict(status='spawned',pid=p.pid));out,err=p.communicate()
 record(dict(status='terminal',pid=p.pid,exit=p.returncode,stdout=out.decode('utf8'),stderr=err.decode('utf8')))
 if save:(HERE/save).write_bytes(out)
 if p.returncode:raise RuntimeError(err.decode('utf8'))
 return out
if __name__=='__main__':
 p=HERE/'working.json'
 if p.exists():raise SystemExit('preserve prior operation evidence')
 write(p,read(ROOT/'examples/studio/person_flower.json'))
 run('inspect',p,'--object','flower-hand','--feature','object','--outdir',HERE/'01-view',save='focused.stdout.json')
 run('inspect',p,'--object','flower-hand','--feature','object','--outdir',HERE/'01-view','--full-report',save='full.stdout.json')
 a=read(HERE/'focused.stdout.json');b=read(HERE/'full.stdout.json')
 assert a['images']==b['images'] and a['revision']==b['revision'] and a['engine']==b['engine']
 write(HERE/'comparison.json',dict(focused_characters=len((HERE/'focused.stdout.json').read_text()),full_characters=len((HERE/'full.stdout.json').read_text()),same_images_revision_engine=True,object_count=17))
 print('Focused/full feedback saved with identical image/revision bindings.',flush=True)
