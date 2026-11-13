"""Compare an owned upper-body garment through unchanged depth visibility, not manual masks."""
from pathlib import Path
from unittest.mock import patch
import sys,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from upper_body import upper_body
from scripts.studio import components,attachment,render
from scripts.studio.model import read,write,select,engine_fingerprint
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 out=HERE/('19-crossed-person' if len(sys.argv)>1 and sys.argv[1]=='cross-person' else '18-crossed-front-surfaces' if len(sys.argv)>1 and sys.argv[1]=='planes' else '17-crossed-union' if len(sys.argv)>1 and sys.argv[1]=='cross' else '16-default-garment-rounded' if len(sys.argv)>1 else '15-owned-garment-rounded')
 if out.exists():raise SystemExit('study output exists')
 scene=read(ROOT/'examples/studio/person_flower.json');posed=attachment.resolve_scene(scene)
 shirt=next(n for n in posed['nodes'] if n['id']=='shirt');old=components.component_data
 origin=attachment.get_anchor(shirt,scene['canvas'],'top')['point']
 hand=next(n for n in posed['nodes'] if n['id']=='flower-hand');wrist=attachment.get_anchor(hand,scene['canvas'],'wrist')
 width=next(n['thickness'] for n in scene['nodes'] if n['id']=='reaching-sleeve')
 if len(sys.argv)>1 and sys.argv[1]=='cross-person':
  h=shirt['length']*min(scene['canvas']);w=h*shirt['width'];desired=[origin[0]+w*.05,origin[1]+h*.65]
  raw=next(n for n in scene['nodes'] if n['id']=='flower-hand');raw['angle']=90
  own=attachment.get_anchor(raw,scene['canvas'],'wrist')['point'];center=old(raw,scene['canvas']).center
  raw['at']=dict(anchor='center',offset=[(center[k]+desired[k]-own[k])/scene['canvas'][k]-.5 for k in (0,1)])
  wrist=attachment.get_anchor(raw,scene['canvas'],'wrist')
  for n in scene['nodes']:
   if n['id']=='upper-stem':n['angle']=180;n['attachment']['target']='handle_right'
   if n['id']=='lower-stem':n['angle']=0;n['attachment']['target']='handle_left'

 scene['nodes']=[n for n in scene['nodes'] if n['id'] not in ('resting-arm','reaching-sleeve')]
 if len(sys.argv)>1 and sys.argv[1]!='cross-person':
  scene=dict(format='learn-draw/studio-1',canvas=[640,640],background='#f3ead9',nodes=[dict(id='shirt',kind='shape',intent='a plain long-sleeved shirt with a collar and owned sleeves',length=.40,width=.9,stroke=.006,rounding=.92,palette=dict(fill='#6c8d98',ink='#445b63'))])
  origin=attachment.get_anchor(scene['nodes'][0],scene['canvas'],'top')['point']
  wrist=dict(point=None,direction=None);width=.05392156862745099
  if sys.argv[1] in ('cross','planes'):
   h=scene['nodes'][0]['length']*min(scene['canvas']);w=h*scene['nodes'][0]['width']
   wrist=dict(point=[origin[0]+w*.05,origin[1]+h*.50],direction=(1,0))
 generated=None
 def factory(node,canvas):
  global generated
  if node['id']!='shirt':return old(node,canvas)
  generated=upper_body(node,canvas,old,wrist['point'],wrist['direction'],width,origin,front_contours=len(sys.argv)>1 and sys.argv[1] in ('planes','cross-person'));return generated
 with patch.object(components,'component_data',factory),patch.object(attachment,'component_data',factory),patch.object(render,'component_data',factory):
  render._scene_regions.cache_clear();view=select(scene,'shirt',feature='right-elbow');report=render.bundle(scene,out,view)
  write(out/'joints.json',generated.joints)
 source=hashlib.sha256(b''.join((HERE/p).read_bytes() for p in ('build_body.py','upper_body.py','study_arm.py','finish_arm.py'))).hexdigest()
 report.update(status='study-only',host_engine=engine_fingerprint(),engine='study:'+source,study=dict(source_sha256=source,scope='single offering pose; no native upper-body API or editing claim',owned_cloth=True,internal_front_contours=len(sys.argv)>1 and sys.argv[1] in ('planes','cross-person'),local_surface_depths=dict(left_arm=-1,torso=0,right_arm=1),external_interposed_prop_support='not implemented/verified by this study'))
 view['engine']='study:'+source;write(out/'report.json',report);write(out/'selection.json',view)
 print('Owned garment rendered:',report['renderer'],flush=True)
