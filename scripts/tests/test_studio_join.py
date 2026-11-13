"""A semantic join must show both real ports without mutating working paint."""
import copy,math,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET
from scripts.studio.__main__ import default_scene
from scripts.studio.model import read,write,select,parameter_preview,validate,fingerprint,accept,undo
from scripts.studio.join import join_preview
from scripts.studio.placement import placement_preview
from scripts.studio.attachment import resolve_scene,get_anchor,anchor_direction
from scripts.studio.render import bundle,drawing
from scripts.studio.body import body_data,_construct

class VisibleJoin(unittest.TestCase):
 def fixture(self):
  s=default_scene('body');s['nodes'][0]['pose']='wave'
  hand=default_scene('hand')['nodes'][0];hand.update(id='palm',length=.13,angle=25,at=dict(anchor='upper_left'))
  s['nodes'].append(hand);return s
 def test_auto_point_and_directionless_target(self):
  s=self.fixture();original=copy.deepcopy(s)
  c=join_preview(s,'palm.wrist','upper-body.right-wrist',reason='seat the raised palm at the cuff')
  p=resolve_scene(c['scene']);a=get_anchor(p['nodes'][1],s['canvas'],'wrist');b=get_anchor(p['nodes'][0],s['canvas'],'right-wrist')
  self.assertLess(math.dist(a['point'],b['point']),1e-8)
  self.assertLess(sum(x*y for x,y in zip(anchor_direction(a),anchor_direction(b))),-.999999)
  self.assertEqual(c['operation']['join']['mode'],'opposed');self.assertEqual(s,original)
  c=join_preview(s,'palm.wrist','upper-body.right-wrist',mode='point',reason='retain the palm tilt')
  self.assertEqual(c['scene']['nodes'][1]['angle'],25)
  c=join_preview(s,'palm.wrist','upper-body.center',reason='an intentional central placement')
  self.assertEqual(c['operation']['join']['mode'],'point')
  with self.assertRaises(ValueError):join_preview(s,'palm.wrist','upper-body.center',mode='opposed',reason='no outward axis')
 def test_pending_six_images_and_recoverable_insertion(self):
  from scripts.tests.test_studio_response import FocusedResponse
  cli=FocusedResponse().cli
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'work.json';s=self.fixture();s['nodes'].pop();write(p,s);before=p.read_bytes()
   cli('place',p,'--kind','hand','--id','palm','--at','upper_left','--change','length=.13','--reason','a greeting palm','--outdir',d/'new')
   result=cli('join',p,'--pending',d/'new/candidate.json','--source','palm.wrist','--target','upper-body.right-wrist','--reason','seat the palm at the raised cuff','--outdir',d/'fit')
   c=read(d/'fit/candidate.json');r=read(d/'fit/report.json')
   self.assertEqual(c['operation']['action'],'place');self.assertEqual(c['selection']['anchor'],'wrist')
   self.assertEqual(len(r['images']),6);self.assertEqual(r['join']['mode'],'opposed');self.assertIn('span',r['join']['before']['source'])
   self.assertEqual(c['scene']['nodes'][0],s['nodes'][0]);self.assertEqual(p.read_bytes(),before)
   for name in ('before-closeup','edit-closeup'):
    xml=ET.fromstring((d/'fit'/f'{name}.svg').read_text());x,y,w,h=map(float,xml.get('viewBox').split())
    for role in ('source','target'):
     label=next(e for e in xml.iter() if e.get('id')==f'join-{role}-label')
     self.assertTrue(x<=float(label.get('x'))<=x+w);self.assertTrue(y<=float(label.get('y'))<=y+h)
   cli('join',p,'--pending',d/'fit/candidate.json','--source','palm.wrist','--target','upper-body.left-wrist','--reason','try the opposite cuff','--outdir',d/'other')
   cli('accept',p,d/'fit/candidate.json');cli('undo',p);self.assertEqual(p.read_bytes(),before)
   self.assertEqual(drawing(read(p)),drawing(s))
 def test_stale_pending_malformed_ports_cycles_and_before_binding_refuse(self):
  s=self.fixture()
  for source,target in [('palm','upper-body.right-wrist'),('palm.missing','upper-body.right-wrist'),('palm.wrist','palm.wrist')]:
   with self.assertRaises(ValueError):join_preview(s,source,target,reason='invalid connection')
  base=default_scene('body');pending=placement_preview(base,default_scene('hand')['nodes'][0],reason='a palm');pending['status']='ready'
  for key,value in [('base','stale'),('engine','stale'),('status','rendering')]:
   bad=copy.deepcopy(pending);bad[key]=value
   with self.assertRaises(ValueError):join_preview(base,'greeting-hand.wrist','upper-body.right-wrist',pending=bad,reason='a stale pending palm')
  c=join_preview(s,'palm.wrist','upper-body.right-wrist',reason='join the palm')
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,'exact before'):bundle(c['scene'],d,c['selection'],previous=s,join_before=default_scene('body'))
 def test_failed_render_and_input_aliases_leave_no_acceptance(self):
  from scripts.tests.test_studio_response import FocusedResponse
  cli=FocusedResponse().cli
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'work.json';s=self.fixture();write(p,s)
   args=('join',p,'--source','palm.wrist','--target','upper-body.right-wrist','--reason','seat the palm','--outdir',d/'fit')
   cli(*args)
   with patch('scripts.studio.render.rasterize',side_effect=RuntimeError('renderer failed')):cli(*args,expected=2)
   self.assertEqual(read(d/'fit/report.json')['images'],[])
   with self.assertRaises(ValueError):accept(p,read(d/'fit/candidate.json'))
   alias=d/'alias';alias.mkdir();(alias/'before-alignment.svg').hardlink_to(p)
   cli(*args[:-1],alias,expected=2);self.assertEqual(read(p),s)

class LocalCuffAndWave(unittest.TestCase):
 def test_narrow_cuff_preserves_skeleton_attached_hand_and_upper_sleeve(self):
  s=VisibleJoin().fixture();s=join_preview(s,'palm.wrist','upper-body.right-wrist',reason='fit the greeting hand')['scene']
  n=s['nodes'][0];a=body_data(n,s['canvas']);rawa=_construct(n,s['canvas'])
  c=parameter_preview(s,select(s,'upper-body',feature='right-wrist'),'right_cuff_width',.72,'taper the loose cuff without shrinking the hand')['scene']
  b=body_data(c['nodes'][0],s['canvas']);rawb=_construct(c['nodes'][0],s['canvas'])
  self.assertEqual(a.joints,b.joints);self.assertEqual(s['nodes'][1],c['nodes'][1]);self.assertEqual(a.mounts['right-wrist']['direction'],b.mounts['right-wrist']['direction'])
  self.assertAlmostEqual(b.mounts['right-wrist']['span']/a.mounts['right-wrist']['span'],.72)
  # Unchanged shoulder region, rather than merely unchanged nominal joint labels.
  from shapely import Point,Polygon
  region=Point(a.joints['right']['shoulder']).buffer(12)
  self.assertLess(Polygon(rawa.outline).symmetric_difference(Polygon(rawb.outline)).intersection(region).area,1e-6)
  self.assertNotIn('right_cuff_width',select(s,'upper-body',feature='object')['controls'])
  for value in (.49,1.41,True):
   with self.assertRaises(ValueError):parameter_preview(s,select(s,'upper-body',feature='right-wrist'),'right_cuff_width',value,'invalid cuff')
 def test_pose_set_applies_gesture_preserving_style_and_links(self):
  s=VisibleJoin().fixture();n=s['nodes'][0];n['arms']={'right':dict(wrist_height=.6,elbow_bend=.2,cuff_width=.8),'left':dict(wrist_spread=-.5)}
  c=parameter_preview(s,select(s,'upper-body',feature='object'),'pose','wave','raise the palm near the face')['scene']
  self.assertEqual(c['nodes'][0]['arms'],{'right':{'cuff_width':.8}});self.assertEqual(c['nodes'][1],s['nodes'][1])
  data=body_data(c['nodes'][0],s['canvas']);self.assertLess(data.mounts['right-wrist']['point'][1],data.mounts['neck']['point'][1]);self.assertEqual(n['arms']['right']['wrist_height'],.6)
  for height in (-.8,1.6):
   trial=copy.deepcopy(c);trial['nodes'][0]['arms']['right']['wrist_height']=height;validate(trial)
  bad=copy.deepcopy(c);bad['nodes'][0]['arms']['right']['wrist_height']=-.81
  with self.assertRaises(ValueError):validate(bad)

if __name__=='__main__':unittest.main()
