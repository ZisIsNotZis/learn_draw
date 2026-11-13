"""A fitted joint must preserve point and direction through the complete held-prop chain."""
import copy,tempfile,unittest,math
from pathlib import Path
from io import BytesIO
import numpy as np
from PIL import Image
import resvg_py
from scripts.studio.__main__ import default_scene
from scripts.studio.model import (read,write,select,preview,attachment_preview,detach_preview,remove_preview,parameter_preview,bind_endpoint_preview,node_by_id,validate,accept,undo)
from scripts.studio.attachment import resolve_scene,get_anchor,anchor_direction
from scripts.studio.render import drawing,bundle
from scripts.studio.alignment import aim_preview
from examples.studio.upper_body import scene as figure
ROOT=Path(__file__).resolve().parents[2]
def pixels(s):return np.asarray(Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=drawing(s)))))
def bind(s,sid,own,parent,target):return attachment_preview(s,select(s,sid,feature='anchors',anchor=own),select(s,parent,feature='anchors',anchor=target),own,target,0,'keep this observed joint opposed as the pose changes',orient='opposed')['scene']
class OrientedMounts(unittest.TestCase):
 def check(self,s):
  p=resolve_scene(s);canvas=s['canvas'];by={n['id']:n for n in p['nodes']}
  for n in s['nodes']:
   r=n.get('attachment',{})
   if not r.get('orient'):continue
   a=get_anchor(by[n['id']],canvas,r['self']);b=get_anchor(by[r['to']],canvas,r['target']);self.assertLess(math.dist(a['point'],b['point']),1e-8)
   self.assertLess(sum(x*y for x,y in zip(anchor_direction(a),anchor_direction(b))),-1+1e-9)
 def fixture(self):
  s=figure('offering');s=bind(s,'flower-hand','wrist','shirt','right-wrist')
  for sid in ('upper-stem','lower-stem'):s=bind(s,sid,'root','flower-hand',node_by_id(s,sid)['attachment']['target'])
  return s
 def test_elbow_and_wrist_edits_reorient_hand_and_both_held_stem_legs(self):
  s=self.fixture();self.check(s);a=resolve_scene(s)
  from scripts.studio.grip import grip_data
  span=grip_data(node_by_id(a,'flower-hand'),s['canvas']).dimensions['handle_thickness']
  for sid in ('upper-stem','lower-stem'):self.assertAlmostEqual(node_by_id(a,sid)['thickness']*min(s['canvas']),span)
  moved=preview(s,select(s,'shirt',feature='right-elbow'),'down',.035,'lower the elbow without breaking the held flower')['scene'];self.check(moved)
  b=resolve_scene(moved);self.assertNotAlmostEqual(node_by_id(a,'flower-hand')['angle'],node_by_id(b,'flower-hand')['angle'])
  self.assertEqual(node_by_id(a,'shirt')['at'],node_by_id(b,'shirt')['at'])
  moved=preview(moved,select(moved,'shirt',feature='right-wrist'),'up',.04,'raise the complete hand and flower assembly')['scene'];self.check(moved)
  for sid in ('flower-hand','upper-stem','lower-stem'):
   self.assertEqual(node_by_id(s,sid),node_by_id(moved,sid));self.assertNotIn('angle',node_by_id(moved,sid));self.assertNotIn('angle',select(moved,sid,feature='object')['controls'])
 def test_release_and_parent_deletion_bake_current_direction_without_paint_change(self):
  s=self.fixture();s=preview(s,select(s,'shirt',feature='right-elbow'),'down',.035,'turn the held assembly through the elbow')['scene'];image=pixels(s)
  detached=detach_preview(s,select(s,'flower-hand',feature='anchors',anchor='wrist'),'release at the actual current orientation')['scene'];self.assertTrue(np.array_equal(image,pixels(detached)));self.check(detached)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'working.json';write(p,s);candidate=detach_preview(s,select(s,'flower-hand',feature='anchors'),'release the hand without a rotation jump');candidate['status']='ready';accept(p,candidate);undo(p);self.assertEqual(read(p),s);self.assertTrue(np.array_equal(image,pixels(read(p))))
  removed=remove_preview(s,select(s,'flower-hand',feature='object'),'remove the hand and retain its exposed stem legs')['scene']
  a=resolve_scene(s);b=resolve_scene(removed)
  for sid in ('upper-stem','lower-stem'):
   self.assertEqual(node_by_id(a,sid)['angle'],node_by_id(b,sid)['angle']);self.assertEqual(node_by_id(a,sid)['at'],node_by_id(b,sid)['at'])
 def test_derived_angle_conflicts_directionless_targets_and_unsupported_operations_refuse(self):
  s=self.fixture();view=select(s,'flower-hand',feature='object')
  with self.assertRaises(ValueError):parameter_preview(s,view,'angle',20,'an attached direction cannot also be manually controlled')
  bad=copy.deepcopy(s);node_by_id(bad,'flower-hand')['angle']=20
  with self.assertRaisesRegex(ValueError,'derived'):validate(bad)
  with self.assertRaisesRegex(ValueError,'directional'):bind(s,'flower-hand','wrist','shirt','center')
  root=select(s,'upper-stem',feature='root');tip=select(s,'upper-stem',feature='tip');target=select(s,'shirt',feature='anchors',anchor='right-wrist')
  with self.assertRaises(ValueError):preview(s,tip,'left',.02,'cannot contradict an attached stroke direction')
  with self.assertRaises(ValueError):bind_endpoint_preview(s,root,target,'right-wrist',0,'cannot mix two different constraint modes')
  with self.assertRaises(ValueError):aim_preview(s,root,select(s,'flower-hand',feature='anchors',anchor=node_by_id(s,'upper-stem')['attachment']['target']),None,'cannot one-shot aim a persistent joint')
 def test_oriented_head_uses_rigid_frame_and_follows_neck_angle(self):
  s=read(ROOT/'scripts/tests/fixtures/legacy_greeting.json');s=bind(s,'greeter-head','chin','greeter-neck','tip');self.check(s)
  moved=parameter_preview(s,select(s,'greeter-neck',feature='object'),'angle',167,'tilt the neck and its attached head')['scene'];self.check(moved)
  changed=node_by_id(resolve_scene(moved),'greeter-head');self.assertAlmostEqual(changed['angle'],-13)
 def test_public_pending_joint_fit_and_current_feedback(self):
  from scripts.tests.test_studio_response import FocusedResponse
  cli=FocusedResponse().cli
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'work.json';s=default_scene('body');write(p,s)
   cli('inspect',p,'--feature','anchors','--anchor','right-wrist','--outdir',d/'target')
   cli('place',p,'--kind','hand','--id','hand','--change','length=.13','--reason','a small greeting hand','--outdir',d/'new')
   result=cli('place',p,'--revise',d/'new/candidate.json','--attach',d/'target/selection.json','--self-anchor','wrist','--target-anchor','right-wrist','--orient','opposed','--reason','fit the hand to the observed cuff','--outdir',d/'fit')
   self.assertIn('derived_angle',result['selected']);self.assertNotIn('angle',result['configure']['controls']);self.assertEqual(read(p),s)
   cli('accept',p,d/'fit/candidate.json');self.check(read(p))
   cli('inspect',p,'--object','upper-body','--feature','anchors','--anchor','right-wrist','--outdir',d/'observed-target')
   cli('inspect',p,'--object','hand','--feature','anchors','--anchor','wrist','--outdir',d/'observed-source')
   frozen=(d/'observed-target/selection.json').read_bytes()
   cli('preview',p,'--selection',d/'observed-source/selection.json','--attach',d/'observed-target/selection.json','--orient','opposed','--reason','target observations must remain intact','--outdir',d/'observed-target',expected=2)
   self.assertEqual((d/'observed-target/selection.json').read_bytes(),frozen)
   bad=cli('preview',p,'--selection',d/'target/selection.json','--move','left','--orient','opposed','--reason','unused option must refuse','--outdir',d/'bad',expected=2);self.assertIsNone(bad)
if __name__=='__main__':unittest.main()
