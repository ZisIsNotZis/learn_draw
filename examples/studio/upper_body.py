"""Open a native connected graphic figure; no study adapter, image or mesh input."""
from pathlib import Path
import argparse,copy,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,node_by_id,select,validate
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.studio.render import bundle
from scripts.studio.grip import grip_data

def scene(pose='offering'):
 s=read(ROOT/'examples/studio/person_flower.json');s['nodes']=[n for n in s['nodes'] if n['id'] not in ('resting-arm','reaching-sleeve')]
 n=node_by_id(s,'shirt');n.clear();n.update(id='shirt',kind='body',intent='a continuous long-sleeved shirt supports the offered flower hand',length=.4,width=.9,sleeve_width=.11,pose=pose,depth=4,attachment=dict(to='neck',self='neck',target='tip'),palette=dict(fill='#6c8d98',ink='#445b63'))
 head=node_by_id(s,'head');head.update(intent='a gentle front-facing person presents a flower',gaze=0,frame=copy.deepcopy(head['at']))
 hand=node_by_id(s,'flower-hand');hand.pop('at',None);hand.pop('angle',None)
 hand.update(length=.11*.4*1.02/.44,attachment=dict(to='shirt',self='wrist',target='right-wrist',orient='opposed'))
 # Choose the initially upper exposed handle end from the compiled semantic mounts.
 # Persistent relations then carry both stem sections through later wrist/elbow edits.
 placed=node_by_id(resolve_scene(s),'flower-hand')
 names=sorted(('handle_left','handle_right'),key=lambda k:get_anchor(placed,s['canvas'],k)['point'][1])
 stem_thickness=grip_data(placed,s['canvas']).dimensions['handle_thickness']/min(s['canvas'])
 for sid,target in [('upper-stem',names[0]),('lower-stem',names[1])]:
  stem=node_by_id(s,sid);stem.pop('angle',None);stem['depth']=4.5;stem['thickness']=stem_thickness;stem['attachment'].update(target=target,orient='opposed')
 validate(s);return s

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scene',choices=('flower','greeting'),default='flower');p.add_argument('--pose',choices=('relaxed','offering','folded'),default='offering');p.add_argument('--outdir',required=True);args=p.parse_args();out=Path(args.outdir).resolve()
 if out.exists():raise SystemExit('output exists; choose a fresh directory')
 s=read(ROOT/'examples/studio/greeting.json') if args.scene=='greeting' else scene(args.pose);write(out/'working.json',s);r=bundle(s,out/'view',select(s,'greeter-shirt' if args.scene=='greeting' else 'shirt',feature='right-elbow'));print('Native upper-body example:',r['revision'],r['renderer'])
