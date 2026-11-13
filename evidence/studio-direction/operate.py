"""Public operations, one observed stage at a time; frozen evidence is not an in-place replay target."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;WORK=HERE/'working.json'
def run(*args):
 record=dict(args=list(map(str,args)),status='started')
 with (HERE/'commands.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(record)+'\n')
 p=subprocess.run([sys.executable,'-m','scripts.studio',*map(str,args)],cwd=ROOT,capture_output=True,text=True,encoding='utf8')
 with (HERE/'commands.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(record|dict(status='terminal',exit=p.returncode,stdout=p.stdout,stderr=p.stderr))+'\n')
 if p.returncode:raise RuntimeError(p.stderr)
def main(stage):
 if stage=='observe':
  run('inspect',WORK,'--object','reaching-sleeve','--feature','tip','--outdir',HERE/'01b-sleeve-observe')
  run('inspect',WORK,'--object','flower-hand','--feature','anchors','--anchor','wrist','--outdir',HERE/'02-wrist-observe')
 elif stage=='aim':
  run('preview',WORK,'--selection',HERE/'01b-sleeve-observe/selection.json','--aim',HERE/'02-wrist-observe/selection.json','--reason','Let the flat cuff enter along the actual wrist while both endpoints remain fixed','--outdir',HERE/'03-sleeve-aim')
 elif stage=='accept':
  run('accept',WORK,HERE/'03-sleeve-aim/candidate.json')
  run('inspect',WORK,'--object','reaching-sleeve','--feature','tip','--outdir',HERE/'04-accepted')
 elif stage=='undo':
  run('undo',WORK);run('inspect',WORK,'--object','reaching-sleeve','--outdir',HERE/'05-undone')
 elif stage=='restore':
  run('accept',WORK,HERE/'03-sleeve-aim/candidate.json');run('inspect',WORK,'--object','reaching-sleeve','--outdir',HERE/'06-restored')
 elif stage=='shoulders':
  run('inspect',WORK,'--object','shirt','--feature','object','--outdir',HERE/'07-shirt-observe')
  run('preview',WORK,'--selection',HERE/'07-shirt-observe/selection.json','--change','rounding=.92','--change','width=.90','--change','taper=-.25','--reason','Replace the rigid shirt slab with sloped softer shoulders and a narrower lower torso','--outdir',HERE/'08-softer-shirt')
 elif stage=='accept-shoulders':
  run('accept',WORK,HERE/'08-softer-shirt/candidate.json')
  run('inspect',WORK,'--object','reaching-sleeve','--feature','tip','--outdir',HERE/'09-cuff-observe')
  run('inspect',WORK,'--object','flower-hand','--feature','anchors','--anchor','wrist','--outdir',HERE/'10-wrist-observe')
 elif stage=='reaim':
  run('preview',WORK,'--selection',HERE/'09-cuff-observe/selection.json','--aim',HERE/'10-wrist-observe/selection.json','--reason','Recheck the cuff direction after reshaping the connected shoulder','--outdir',HERE/'11-cuff-refit')
 elif stage=='accept-refit':
  run('accept',WORK,HERE/'11-cuff-refit/candidate.json');run('inspect',WORK,'--object','flower-hand','--outdir',HERE/'12-current')
 elif stage=='resting-observe':
  run('inspect',WORK,'--object','resting-arm','--feature','anchors','--anchor','root','--outdir',HERE/'13-resting-root-observe')
  run('inspect',WORK,'--object','shirt','--feature','anchors','--anchor','left@.77','--outdir',HERE/'14-left-shoulder-observe')
 elif stage=='resting-seat':
  run('preview',WORK,'--selection',HERE/'13-resting-root-observe/selection.json','--attach',HERE/'14-left-shoulder-observe/selection.json','--self-anchor','root','--inset','.06','--reason','The far sleeve belongs at the upper left shoulder, not the lower left torso','--outdir',HERE/'15-resting-arm-seated')
 elif stage=='accept-resting':
  run('accept',WORK,HERE/'15-resting-arm-seated/candidate.json');run('inspect',WORK,'--object','resting-arm','--outdir',HERE/'16-current')
 elif stage=='guides':
  run('inspect',ROOT/'examples/studio/camera.json','--object','glass-glint','--feature','anchors','--outdir',HERE/'00-small-guides')
 else:raise ValueError(stage)
if __name__=='__main__':main(sys.argv[1])
