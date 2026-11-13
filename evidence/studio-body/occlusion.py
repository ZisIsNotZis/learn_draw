"""Small native depth fixture: chest < pole < forearm, then a genuinely sloping pole."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.__main__ import default_scene
from scripts.studio.model import write,select
from scripts.studio.render import bundle
if __name__=='__main__':
 out=Path(sys.argv[1]).resolve()
 if out.exists():raise SystemExit('output exists')
 s=default_scene('body');s['nodes'][0].update(pose='folded',depth=0)
 s['nodes'].append(dict(id='pole',kind='stroke',intent='an upright red pole passes between chest and nearer forearm',length=.42,thickness=.025,depth=.5,at=dict(anchor='center',offset=[.045,-.17]),palette=dict(fill='#d2593d',ink='#d2593d'),ink_width=0))
 for mode in ('between','sloped'):
  if mode=='sloped':s['nodes'][1]['depth_slope']=1.5
  write(out/mode/'working.json',s);r=bundle(s,out/mode/'view',select(s,'upper-body',feature='right-elbow'));print(mode,r['revision'],r['renderer'],flush=True)
