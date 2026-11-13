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
 out=HERE/('14-default-garment-soft' if len(sys.argv)>1 else '13-owned-garment-soft')
 if out.exists():raise SystemExit('study output exists')
 scene=read(ROOT/'examples/studio/person_flower.json');posed=attachment.resolve_scene(scene)
 shirt=next(n for n in posed['nodes'] if n['id']=='shirt');old=components.component_data
 origin=attachment.get_anchor(shirt,scene['canvas'],'top')['point']
 hand=next(n for n in posed['nodes'] if n['id']=='flower-hand');wrist=attachment.get_anchor(hand,scene['canvas'],'wrist')
 width=next(n['thickness'] for n in scene['nodes'] if n['id']=='reaching-sleeve')
 scene['nodes']=[n for n in scene['nodes'] if n['id'] not in ('resting-arm','reaching-sleeve')]
 if len(sys.argv)>1:
  scene=dict(format='learn-draw/studio-1',canvas=[640,640],background='#f3ead9',nodes=[dict(id='shirt',kind='shape',intent='a plain long-sleeved shirt with a collar and owned sleeves',length=.40,width=.9,stroke=.006,rounding=.92,palette=dict(fill='#6c8d98',ink='#445b63'))])
  origin=attachment.get_anchor(scene['nodes'][0],scene['canvas'],'top')['point']
  wrist=dict(point=None,direction=None);width=.05392156862745099
 generated=None
 def factory(node,canvas):
  global generated
  if node['id']!='shirt':return old(node,canvas)
  generated=upper_body(node,canvas,old,wrist['point'],wrist['direction'],width,origin);return generated
 with patch.object(components,'component_data',factory),patch.object(attachment,'component_data',factory),patch.object(render,'component_data',factory):
  render._scene_regions.cache_clear();view=select(scene,'shirt',feature='right-elbow');report=render.bundle(scene,out,view)
  write(out/'joints.json',generated.joints)
 source=hashlib.sha256(b''.join((HERE/p).read_bytes() for p in ('build_body.py','upper_body.py','study_arm.py','finish_arm.py'))).hexdigest()
 report.update(status='study-only',host_engine=engine_fingerprint(),engine='study:'+source,study=dict(source_sha256=source,scope='single offering pose; no native upper-body API or editing claim',owned_cloth=True))
 view['engine']='study:'+source;write(out/'report.json',report);write(out/'selection.json',view)
 print('Owned garment rendered:',report['renderer'],flush=True)
