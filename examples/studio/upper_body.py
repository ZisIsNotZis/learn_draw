"""Open a native connected graphic figure; no study adapter, image or mesh input."""
from pathlib import Path
import argparse,math,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,node_by_id,select,validate
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.studio.body import body_data
from scripts.studio.grip import grip_data
from scripts.studio.render import bundle

def scene(pose='offering'):
 s=read(ROOT/'examples/studio/person_flower.json');s['nodes']=[n for n in s['nodes'] if n['id'] not in ('resting-arm','reaching-sleeve')]
 n=node_by_id(s,'shirt');n.clear();n.update(id='shirt',kind='body',intent='a continuous long-sleeved shirt supports the offered flower hand',length=.4,width=.9,sleeve_width=.11,pose=pose,depth=4,attachment=dict(to='neck',self='neck',target='tip'),palette=dict(fill='#6c8d98',ink='#445b63'))
 head=node_by_id(s,'head');head.update(intent='a gentle front-facing person presents a flower',gaze=0)
 body=node_by_id(resolve_scene(s),'shirt');direction=body_data(body,s['canvas']).mounts['right-wrist']['direction']
 hand=node_by_id(s,'flower-hand');hand.pop('at',None);hand.update(length=.11*.4*1.02/.44,angle=math.degrees(math.atan2(-direction[0],-direction[1])),attachment=dict(to='shirt',self='wrist',target='right-wrist'))
 # Initial pose alignment is computed once. Ordinary pins subsequently preserve a point,
 # not child orientation; wrist edits still need visual direction inspection.
 data=grip_data(dict((k,v) for k,v in hand.items() if k!='attachment'),s['canvas'])
 names=sorted(('handle_left','handle_right'),key=lambda k:data.mounts[k]['point'][1]);a,b=[data.mounts[k]['point'] for k in names]
 up=math.degrees(math.atan2(a[0]-b[0],a[1]-b[1]))
 for sid,target,angle in [('upper-stem',names[0],up),('lower-stem',names[1],up-180 if up>0 else up+180)]:
  node_by_id(s,sid).update(angle=angle,depth=4.5);node_by_id(s,sid)['attachment']['target']=target
 validate(s);return s

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scene',choices=('flower','greeting'),default='flower');p.add_argument('--pose',choices=('relaxed','offering','folded'),default='offering');p.add_argument('--outdir',required=True);args=p.parse_args();out=Path(args.outdir).resolve()
 if out.exists():raise SystemExit('output exists; choose a fresh directory')
 s=read(ROOT/'examples/studio/greeting.json') if args.scene=='greeting' else scene(args.pose);write(out/'working.json',s);r=bundle(s,out/'view',select(s,'greeter-shirt' if args.scene=='greeting' else 'shirt',feature='right-elbow'));print('Native upper-body example:',r['revision'],r['renderer'])
