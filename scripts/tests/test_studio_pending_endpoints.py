"""A new two-contact stroke must fit before any working paint is committed."""
import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scripts.studio.__main__ import default_scene
from scripts.studio.model import read,write,select,accept,undo,parameters_preview,node_by_id
from scripts.studio.placement import placement_preview
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.tests.test_studio_endpoints import fixture,ends

def base():
 s=fixture();s['nodes']=s['nodes'][1:];return s

def pending(s):
 n=default_scene('stroke')['nodes'][0];n['id']='bridge'
 p=placement_preview(s,n,reason='a new connection before it lands');p['status']='ready';return p

def bind(s,p,end,target,anchor):
 c=placement_preview(s,prior=p,feature=end,endpoint_target=select(s,target,feature='anchors',anchor=anchor),reason='seat this end at the inspected surface')
 c['status']='ready';return c

class PendingEndpointContacts(unittest.TestCase):
 def test_two_pending_contacts_preserve_inputs_then_derive_and_follow_both(self):
  s=base();original=copy.deepcopy(s);p=pending(s)
  a=bind(s,p,'root','source','left@.1');b=bind(s,a,'tip','destination','right@.9')
  self.assertEqual(s,original);self.assertEqual(b['scene']['nodes'][:-1],s['nodes'])
  self.assertEqual(b['selection']['anchor'],'tip');self.assertTrue(b['selection']['join_pair'])
  self.assertEqual(b['operation']['action'],'place');self.assertNotIn('angle',b['scene']['nodes'][-1]);self.assertNotIn('length',b['scene']['nodes'][-1])
  placed=resolve_scene(s)
  expected=[get_anchor(node_by_id(placed,sid),s['canvas'],port)['point'] for sid,port in [('source','left@.1'),('destination','right@.9')]]
  np.testing.assert_allclose(ends(b['scene']),expected,atol=1e-8)
  moved=parameters_preview(b['scene'],select(b['scene'],'destination',feature='object'),{'angle':35,'length':.20},'turn the far support')['scene']
  np.testing.assert_allclose(ends(moved)[0],expected[0],atol=1e-8);self.assertFalse(np.allclose(ends(moved)[1],expected[1]))
 def test_public_pending_render_accept_and_exact_undo(self):
  from scripts.tests.test_studio_response import FocusedResponse
  cli=FocusedResponse().cli
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);file=d/'working.json';s=base();write(file,s);original=file.read_bytes()
   cli('inspect',file,'--object','source','--feature','anchors','--anchor','left@.1','--outdir',d/'a')
   cli('inspect',file,'--object','destination','--feature','anchors','--anchor','right@.9','--outdir',d/'b')
   cli('place',file,'--kind','stroke','--id','bridge','--reason','a curved connecting mark','--outdir',d/'new')
   cli('place',file,'--revise',d/'new/candidate.json','--feature','root','--bind-end',d/'a/selection.json','--reason','fit the first contact before insertion','--outdir',d/'root')
   cli('place',file,'--revise',d/'root/candidate.json','--feature','tip','--bind-end',d/'b/selection.json','--reason','fit the second contact before insertion','--outdir',d/'tip')
   self.assertEqual(file.read_bytes(),original);r=read(d/'tip/report.json');self.assertEqual(len(r['images']),4)
   svg=(d/'tip/edit-closeup.svg').read_text();self.assertIn('join-source-label',svg);self.assertIn('destination.right@.9',svg)
   cli('place',file,'--revise',d/'tip/candidate.json','--change','bend=-.15','--change','thickness=.015','--reason','refine the curve between its fixed contacts','--outdir',d/'curve')
   np.testing.assert_allclose(ends(read(d/'tip/scene.json')),ends(read(d/'curve/scene.json')),atol=1e-8)
   cli('accept',file,d/'curve/candidate.json');self.assertEqual(len(read(file)['nodes']),3)
   cli('undo',file);self.assertEqual(file.read_bytes(),original)
 def test_invalid_modes_and_stale_targets_refuse(self):
  s=base();p=pending(s);target=select(s,'source',feature='anchors',anchor='left@.1')
  for extra in [dict(feature='object'),dict(feature='root',orient='opposed'),dict(feature='root',self_anchor='root')]:
   with self.assertRaises(ValueError):placement_preview(s,prior=p,endpoint_target=target,reason='invalid binding',**extra)
  with self.assertRaises(ValueError):placement_preview(s,default_scene('stroke')['nodes'][0],feature='root',endpoint_target=target,reason='unobserved new stroke')
  for key in ('base','engine'):
   bad=copy.deepcopy(target);bad[key]='stale'
   with self.assertRaises(ValueError):placement_preview(s,prior=p,feature='root',endpoint_target=bad,reason='stale target')
  n=default_scene('shape')['nodes'][0];shape=placement_preview(s,n,reason='a colour block');shape['status']='ready'
  with self.assertRaises(ValueError):placement_preview(s,prior=shape,feature='root',endpoint_target=target,reason='not a stroke')
 def test_aliases_and_failed_render_do_not_commit(self):
  from scripts.tests.test_studio_response import FocusedResponse
  cli=FocusedResponse().cli
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);file=d/'working.json';s=base();write(file,s)
   cli('inspect',file,'--object','source','--feature','anchors','--anchor','left@.1','--outdir',d/'target')
   cli('place',file,'--kind','stroke','--reason','a pending stroke','--outdir',d/'new')
   args=('place',file,'--revise',d/'new/candidate.json','--feature','root','--bind-end',d/'target/selection.json','--reason','fit without overwriting the observation','--outdir')
   frozen=(d/'target/selection.json').read_bytes();cli(*args,d/'target',expected=2);self.assertEqual((d/'target/selection.json').read_bytes(),frozen)
   cli(*args,d/'fit')
   with patch('scripts.studio.render.rasterize',side_effect=RuntimeError('renderer failed')):cli(*args,d/'fit',expected=2)
   self.assertEqual(read(d/'fit/report.json')['images'],[])
   with self.assertRaises(ValueError):accept(file,read(d/'fit/candidate.json'))
   self.assertEqual(read(file),s)

if __name__=='__main__':unittest.main()
