"""Head placement must move the actual painted geometry and its selections rigidly."""
import copy,math,tempfile,unittest
from pathlib import Path
from io import BytesIO
import numpy as np
from PIL import Image
import resvg_py
from scripts.studio.__main__ import default_scene
from scripts.studio.head import head_data
from scripts.studio.model import read,select,preview,attachment_preview,detach_preview,remove_preview,node_by_id,fingerprint,validate,parameter_preview
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.studio.render import drawing
ROOT=Path(__file__).resolve().parents[2]
def pixels(s):return np.asarray(Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=drawing(s)))))
class StableHeadFrame(unittest.TestCase):
 def test_new_head_placement_translates_paint_mounts_selections_and_locks(self):
  s=default_scene('head');n=s['nodes'][0];n.update(angle=23,id='face--study');a=head_data(n,s['canvas'])
  candidate=preview(s,select(s,feature='object'),'right',.0134,'move the head without redrawing its facial shape');b=head_data(candidate['scene']['nodes'][0],s['canvas']);shift=np.array([.0134*640,0])
  from xml.etree import ElementTree as ET
  ET.fromstring(b.svg)  # Moving a valid double-hyphen ID must not create an invalid XML comment.
  self.assertTrue(np.allclose(np.array(b.outline)-a.outline,shift,atol=1e-10))
  self.assertTrue(np.allclose(np.array(b.mounts['chin']['point'])-a.mounts['chin']['point'],shift,atol=1e-10))
  for name in a.features:
   self.assertTrue(np.allclose(np.array(b.features[name]['bounds'])-a.features[name]['bounds'],[*shift,*shift]))
   self.assertEqual([p['d'] for p in a.features[name]['paths']],[p['d'] for p in b.features[name]['paths']])
  for side in a.locks:
   self.assertTrue(np.allclose(np.array([r.spine for r in b.locks[side]['rows']])-np.array([r.spine for r in a.locks[side]['rows']]),shift))
  legacy=copy.deepcopy(n);legacy.pop('frame');self.assertEqual(head_data(legacy,s['canvas']).svg,a.svg)
 def migrated(self):
  s=read(ROOT/'scripts/tests/fixtures/legacy_greeting.json');before=copy.deepcopy(s)
  source=select(s,'greeter-head',feature='anchors',anchor='chin');target=select(s,'greeter-neck',feature='anchors',anchor='tip')
  candidate=attachment_preview(s,source,target,'chin','tip',0,'seat the chin precisely without reconstructing the head')
  self.assertEqual(s,before);self.assertIn('frame',node_by_id(candidate['scene'],'greeter-head'))
  return s,candidate['scene']
 def test_legacy_reattachment_and_parent_changes_keep_exact_actual_chin(self):
  old,s=self.migrated();canvas=s['canvas'];placed=resolve_scene(s)
  def error(scene):
   p=resolve_scene(scene);return math.dist(get_anchor(node_by_id(p,'greeter-head'),canvas,'chin')['point'],get_anchor(node_by_id(p,'greeter-neck'),canvas,'tip')['point'])
  self.assertGreater(error(old),.1);self.assertLess(error(s),1e-9)
  prior=head_data(node_by_id(resolve_scene(old),'greeter-head'),canvas);after=head_data(node_by_id(placed,'greeter-head'),canvas)
  shift=np.array(after.center)-prior.center;self.assertTrue(np.allclose(np.array(after.outline)-prior.outline,shift,atol=1e-10))
  moved=preview(s,select(s,'greeter-shirt',feature='object'),'left',.0173,'move the whole greeting assembly')['scene'];self.assertLess(error(moved),1e-9)
  changed=parameter_preview(moved,select(moved,'greeter-head',feature='face'),'jaw',.47,'soften the jaw while keeping its chin joined')['scene'];self.assertLess(error(changed),1e-9)
 def test_detach_and_parent_removal_preserve_paint_for_legacy_and_stable_heads(self):
  old,stable=self.migrated()
  for s in (old,stable):
   image=pixels(s);candidate=detach_preview(s,select(s,'greeter-head',feature='anchors',anchor='chin'),'release the head without moving any paint')['scene'];self.assertTrue(np.array_equal(image,pixels(candidate)))
   removed=remove_preview(s,select(s,'greeter-neck',feature='object'),'remove the neck and retain the head in place')['scene']
   before=head_data(node_by_id(resolve_scene(s),'greeter-head'),s['canvas']);after=head_data(node_by_id(resolve_scene(removed),'greeter-head'),s['canvas']);self.assertTrue(np.allclose(before.outline,after.outline));self.assertEqual(before.svg,after.svg)
 def test_legacy_attached_head_requires_observed_migration_before_protected_edits(self):
  old=read(ROOT/'scripts/tests/fixtures/legacy_greeting.json');original=fingerprint(old)
  for change in (lambda:preview(old,select(old,'greeter-head',feature='left-lock'),'left',.03,'keep lock endpoints fixed'),lambda:preview(old,select(old,'greeter-head',feature='object'),'right',.03,'move the head without a hidden pin correction'),lambda:parameter_preview(old,select(old,'greeter-head',feature='eyes'),'eye_scale',.95,'quiet the eyes without moving unrelated geometry')):
   with self.assertRaisesRegex(ValueError,'reattach'):change()
  self.assertEqual(fingerprint(old),original)
  _,stable=self.migrated();before=head_data(node_by_id(resolve_scene(stable),'greeter-head'),stable['canvas'])
  edited=preview(stable,select(stable,'greeter-head',feature='left-lock'),'left',.03,'relax the lock after stabilizing its frame')['scene'];after=head_data(node_by_id(resolve_scene(edited),'greeter-head'),stable['canvas'])
  for index in (0,-1):self.assertTrue(np.allclose(before.locks['left']['rows'][index].spine,after.locks['left']['rows'][index].spine))
 def test_frame_validation_and_local_hair_edit_after_translation(self):
  s=default_scene('head');s=preview(s,select(s,feature='object'),'down',.0123,'lower the head rigidly')['scene'];a=head_data(s['nodes'][0],s['canvas'])
  candidate=preview(s,select(s,feature='left-lock',at=.55,radius=.30),'left',.03,'relax the side lock without moving its ends')['scene'];b=head_data(candidate['nodes'][0],s['canvas'])
  for index in (0,-1):self.assertTrue(np.allclose(a.locks['left']['rows'][index].spine,b.locks['left']['rows'][index].spine))
  for frame in ({'absolute':[2,3]},{'offset':[True,0]},{'offset':[float('nan'),0]}):
   bad=copy.deepcopy(s);bad['nodes'][0]['frame']=frame
   with self.assertRaises(ValueError):validate(bad)
if __name__=='__main__':unittest.main()
