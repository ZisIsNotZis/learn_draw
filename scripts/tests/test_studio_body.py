"""A body must support local correction, linked props and actual internal/external occlusion."""
import copy,math,subprocess,sys,tempfile,unittest
from pathlib import Path
from io import BytesIO
from unittest.mock import patch
import numpy as np
from PIL import Image
import resvg_py
from shapely import Polygon,Point
from scripts.studio.__main__ import default_scene
from scripts.studio.body import body_data
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.studio.model import validate,select,preview,parameter_preview,fingerprint,write,read,accept,undo,node_by_id
from scripts.studio.render import drawing,global_depth_order
ROOT=Path(__file__).resolve().parents[2]
def pixels(s):return np.asarray(Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=drawing(s)))).convert('RGB'))
class EditableBody(unittest.TestCase):
 def test_local_elbow_move_preserves_endpoints_and_other_arm_under_rotation(self):
  s=default_scene('body');s['canvas']=[800,600];n=s['nodes'][0];n.update(pose='offering',angle=31)
  a=body_data(n,s['canvas']);candidate=preview(s,select(s,feature='right-elbow'),'left',.035,'bring the elbow inward without disturbing the wrist')
  b=body_data(candidate['scene']['nodes'][0],s['canvas']);h=.4*600
  self.assertTrue(np.allclose(np.array(b.joints['right']['elbow'])-a.joints['right']['elbow'],[-.035*h,0]))
  for key in ('neck','right-shoulder','right-wrist','left-elbow','left-wrist'):self.assertEqual(a.mounts[key]['point'],b.mounts[key]['point'])
  self.assertEqual(s['nodes'][0],n);self.assertNotIn('arms',n)
 def test_wrist_move_updates_attached_hand_and_undo_recovers_exact_paint(self):
  s=default_scene('body');n=s['nodes'][0];n.update(pose='offering',depth=0)
  s['nodes'].append(dict(id='hand',kind='grip',intent='a compact hand at the cuff',length=.10,depth=2,angle=-110,attachment=dict(to=n['id'],target='right-wrist',self='wrist')))
  validate(s);before=pixels(s);candidate=preview(s,select(s,n['id'],feature='right-wrist'),'up',.05,'lift the offered hand and keep it joined to the sleeve')
  placed=resolve_scene(candidate['scene']);a=get_anchor(placed['nodes'][0],s['canvas'],'right-wrist')['point'];b=get_anchor(placed['nodes'][1],s['canvas'],'wrist')['point'];self.assertTrue(np.allclose(a,b))
  self.assertEqual(candidate['scene']['nodes'][1],s['nodes'][1]);self.assertEqual(body_data(n,s['canvas']).mounts['right-shoulder'],body_data(candidate['scene']['nodes'][0],s['canvas']).mounts['right-shoulder'])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'work.json';write(p,s);candidate['status']='ready';accept(p,candidate);undo(p);self.assertEqual(read(p),s);self.assertTrue(np.array_equal(before,pixels(read(p))))
 def test_external_pole_between_torso_and_forearm_obeys_compound_depth(self):
  s=default_scene('body');n=s['nodes'][0];n.update(pose='folded',depth=0)
  s['nodes'].append(dict(id='pole',kind='stroke',intent='a red upright pole between chest and nearer sleeve',length=.42,thickness=.025,depth=.5,at=dict(anchor='center',offset=[.045,-.17]),palette=dict(fill='#d2593d',ink='#d2593d'),ink_width=0))
  from scripts.studio.components import component_outline
  data=body_data(n,s['canvas']);parts={p.name:Polygon(p.outline) for p in data.surfaces};rod=Polygon(component_outline(s['nodes'][1],s['canvas']))
  front=parts['right'].buffer(-4).intersection(rod.buffer(-3));chest=parts['torso'].buffer(-4).intersection(rod.buffer(-3)).difference(parts['right'].buffer(4))
  self.assertFalse(front.is_empty);self.assertFalse(chest.is_empty)
  def colour(image,region):
   p=region.representative_point();return tuple(image[round(p.y),round(p.x)])
  image=pixels(s);self.assertEqual(colour(image,front),(108,141,152));self.assertEqual(colour(image,chest),(210,89,61))
  reordered=copy.deepcopy(s);reordered['nodes'].reverse();self.assertTrue(np.array_equal(image,pixels(reordered)))
  # Force the existing triangle oracle to verify the same interior visibility.
  with patch('scripts.studio.render.global_depth_order',return_value=None):oracle=pixels(s)
  self.assertEqual(colour(oracle,front),(108,141,152));self.assertEqual(colour(oracle,chest),(210,89,61))
  sloped=copy.deepcopy(s);sloped['nodes'][1]['depth_slope']=1.5
  self.assertIsNone(global_depth_order(sloped))
  crossed=pixels(sloped);self.assertEqual(colour(crossed,front),(210,89,61));self.assertEqual(colour(crossed,chest),(210,89,61))
  # Paper must not leak through adjacent masks inside one continuous cloth material.
  from shapely import contains_xy
  yy,xx=np.indices(crossed.shape[:2]);inside=Polygon(data.outline).buffer(-3).difference(rod.buffer(3))
  mask=contains_xy(inside,xx+.5,yy+.5)
  self.assertFalse(np.any((crossed.max(axis=2)>190)&mask))
 def test_defaults_poses_and_invalid_controls_are_real_geometry(self):
  from xml.etree import ElementTree as ET
  for pose in ('relaxed','offering','folded'):
   s=default_scene('body');s['nodes'][0]['pose']=pose;validate(s);data=body_data(s['nodes'][0],s['canvas']);self.assertTrue(Polygon(data.outline).is_valid);self.assertEqual(len(data.surfaces),3)
   xml=ET.fromstring(drawing(s));ids=[e.get('id') for e in xml.iter() if e.get('id')];self.assertEqual(len(ids),len(set(ids)))
  s=default_scene('body');base=fingerprint(s)
  for change in ({'sleeve_width':True},{'arms':{'right':{'elbow_bend':float('nan')}}},{'arms':{'right':{'mystery':.1}}},{'pose':'unknown'}):
   bad=copy.deepcopy(s);bad['nodes'][0].update(change)
   with self.assertRaises(ValueError):validate(bad)
  self.assertEqual(fingerprint(s),base)
 def test_reference_free_fresh_directory(self):
  code="""import sys
sys.path[:0]=[sys.argv[1],sys.argv[1]+'/scripts']
def audit(event,args):
 if event=='open' and isinstance(args[0],str) and args[0].lower().endswith(('.jpg','.jpeg','.png','.svg','.glb')):raise RuntimeError('unexpected visual input')
sys.addaudithook(audit)
from scripts.studio.__main__ import default_scene
from scripts.studio.render import drawing
s=drawing(default_scene('body'));assert '.plane-right' in s and '<image' not in s
"""
  with tempfile.TemporaryDirectory() as d:
   r=subprocess.run([sys.executable,'-c',code,str(ROOT)],cwd=d,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
 def test_public_pending_body_and_local_edit(self):
  from scripts.tests.test_studio_response import FocusedResponse
  cli=FocusedResponse().cli
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'work.json';write(p,default_scene('blank'))
   cli('place',p,'--kind','body','--id','shirt','--change','pose=offering','--reason','a simple long-sleeved offering pose','--outdir',d/'new');self.assertEqual(read(p)['nodes'],[])
   cli('accept',p,d/'new/candidate.json');original=read(p)
   view=cli('inspect',p,'--object','shirt','--feature','right-elbow','--outdir',d/'view');self.assertEqual(view['selection']['interaction'],'body-joint')
   cli('preview',p,'--selection',d/'view/selection.json','--move','down','--amount','.025','--reason','lower the elbow while retaining the wrist','--outdir',d/'edit');cli('accept',p,d/'edit/candidate.json');cli('undo',p);self.assertEqual(read(p),original)
if __name__=='__main__':unittest.main()
