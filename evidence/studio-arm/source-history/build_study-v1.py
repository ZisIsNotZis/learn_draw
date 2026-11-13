"""Compare a study sleeve with the native stroke through the actual depth renderer.
Only the chosen component factory is adapted in this process. No SVG visibility cuts.
Reports/selection are marked study-only and cannot be accepted as native proposals.
"""
from pathlib import Path
import sys,json,hashlib,copy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from study_arm import arm_data
from scripts.studio import components,attachment,render
from scripts.studio.model import read,write,select,engine_fingerprint
from scripts.studio.geometry import bounds
HERE=Path(__file__).resolve().parent

def build(case,scene,sid,mode):
 out=HERE/case
 if out.exists():raise ValueError('study output exists; choose a new case')
 source_hash=hashlib.sha256((Path(__file__).read_bytes()+(HERE/'study_arm.py').read_bytes())).hexdigest()
 host=engine_fingerprint();old=components.component_data;joint=None
 placed=attachment.resolve_scene(scene)
 direction=None
 if mode=='wrist-fit':direction=attachment.get_anchor(next(n for n in placed['nodes'] if n['id']=='flower-hand'),scene['canvas'],'wrist')['direction']
 def factory(node,canvas):
  nonlocal joint
  if node['id']!=sid or mode=='baseline':return old(node,canvas)
  data=arm_data(node,canvas,mode=mode,wrist_direction=direction);joint=data.joints
  return data
 with patch.object(components,'component_data',factory),patch.object(attachment,'component_data',factory),patch.object(render,'component_data',factory):
  render._scene_regions.cache_clear()
  view=select(scene,sid,feature='tip' if mode=='baseline' else 'elbow')
  report=render.bundle(scene,out,view)
  if joint is not None:write(out/'joint-data.json',joint)
 study=dict(mode=mode,host_engine=host,source_sha256=source_hash,adapter='process-local component_data replacement; real depth visibility',direction_from_named_wrist=direction)
 report.update(status='study-only',engine='study:'+source_hash,study=study)
 view.update(engine='study:'+source_hash,study=study)
 write(out/'report.json',report);write(out/'selection.json',view)
 print(case,report['renderer'],flush=True)

if __name__=='__main__':
 scene=read(ROOT/'examples/studio/person_flower.json')
 for name,mode in [('01-context-baseline','baseline'),('02-context-jointed','default'),('03-context-wristfit','wrist-fit')]:build(name,scene,'reaching-sleeve',mode)
 sample=dict(format='learn-draw/studio-1',canvas=[640,480],background='#f3ead9',nodes=[dict(id='sleeve-probe',kind='stroke',intent='a simple sleeved arm with a clear elbow',length=.58,thickness=.055,start_width=1.55,end_width=1,angle=90,bend=-.30,ink_width=.0025,depth=1,at=dict(anchor='upper_left',offset=[0,.25]),palette=dict(fill='#6c8d98',ink='#445b63'))])
 build('04-default-stroke',sample,'sleeve-probe','baseline');build('05-default-jointed',sample,'sleeve-probe','default')
