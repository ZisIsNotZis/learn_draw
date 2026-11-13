"""Observed direction fits preserve endpoints, existing joins and recoverable paint."""
import copy,contextlib,io,math,sys,tempfile,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
from scripts.studio.__main__ import default_scene,main
from scripts.studio.model import read,write,select,accept,undo,validate,fingerprint,node_by_id
from scripts.studio.alignment import aim_preview
from scripts.studio.attachment import resolve_scene,get_anchor,anchor_direction
from scripts.studio.stroke import stroke_data
from scripts.studio.render import drawing
ROOT=Path(__file__).resolve().parents[2]

def actual(scene,sid):return node_by_id(resolve_scene(scene),sid)
def water():return read(ROOT/'examples/studio/watering_grip.json')
def points(scene,sid):
 d=stroke_data(actual(scene,sid),scene['canvas']);return (d.rows[0].spine,d.rows[-1].spine)
class ObservedDirection(unittest.TestCase):
 def cli(self,*args,expected=0):
  with patch.object(sys,'argv',['studio',*map(str,args)]),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()) as err:r=main()
  self.assertEqual(r,expected,err.getvalue())
 def test_real_nozzle_fit_recovers_authored_flow_without_moving_either_pin(self):
  scene=water();node_by_id(scene,'water')['bend']=0
  c=aim_preview(scene,select(scene,'water',feature='root'),select(scene,'spout',feature='anchors',anchor='tip'),None,'Let water leave along the nozzle')
  self.assertAlmostEqual(node_by_id(c['scene'],'water')['bend'],.21921608423796685)
  self.assertEqual(points(scene,'water'),points(c['scene'],'water'))
  self.assertEqual([n for n in scene['nodes'] if n['id']!='water'],[n for n in c['scene']['nodes'] if n['id']!='water'])
  self.assertEqual(node_by_id(scene,'water')['endpoints'],node_by_id(c['scene'],'water')['endpoints'])
 def test_reverse_graph_wrist_join_fits_sleeve_without_moving_descendants(self):
  scene=water();node_by_id(scene,'reaching-sleeve')['bend']=0
  c=aim_preview(scene,select(scene,'reaching-sleeve',feature='tip'),select(scene,'carrying-hand',feature='anchors',anchor='wrist'),None,'Let the cuff enter along the wrist')
  self.assertAlmostEqual(node_by_id(c['scene'],'reaching-sleeve')['bend'],-.3910503065588981)
  for a,b in zip(points(scene,'reaching-sleeve'),points(c['scene'],'reaching-sleeve')):self.assertLess(math.dist(a,b),1e-9)
  old,new=resolve_scene(scene),resolve_scene(c['scene'])
  for a,b in zip(old['nodes'],new['nodes']):
   if a['id']!='reaching-sleeve':self.assertEqual(a,b)
 def test_directions_rotate_and_mirror_with_real_geometry_without_changing_inset_normals(self):
  for kind in ('hand','grip'):
   for angle in (-120,-35,0,90):
    n=default_scene(kind)['nodes'][0];n.update(angle=angle)
    if kind=='grip':n['thumb_side']='left'
    info=get_anchor(n,[960,540],'wrist');self.assertIsNone(info['normal'])
    d=anchor_direction(info);self.assertAlmostEqual(d[0],math.sin(math.radians(angle)));self.assertAlmostEqual(d[1],math.cos(math.radians(angle)))
  line=default_scene('stroke')['nodes'][0];line.update(angle=42,bend=.2)
  d=stroke_data(line,[960,540]);self.assertEqual(anchor_direction(get_anchor(line,[960,540],'root')),tuple(-x for x in d.tangents[0]))
 def test_directionless_unconnected_stale_and_wrong_feature_refuse(self):
  scene=water();a=select(scene,'water',feature='root');b=select(scene,'spout',feature='anchors',anchor='tip')
  for source,target,name in [(dict(a,base='old'),b,None),(a,dict(b,engine='old'),None),(select(scene,'water',feature='object'),b,None),(a,b,'root'),(a,select(scene,'spout',feature='anchors'),None)]:
   with self.assertRaises(ValueError):aim_preview(scene,source,target,name,'A visible join')
  n=default_scene('stroke')['nodes'][0];n['attachment']=dict(to='mass',self='root',target='center')
  scene=dict(format='learn-draw/studio-1',canvas=[640,640],nodes=[dict(id='mass',kind='shape',intent='support'),n])
  with self.assertRaisesRegex(ValueError,'no defined direction'):aim_preview(scene,select(scene,n['id'],feature='root'),select(scene,'mass',feature='anchors',anchor='center'),None,'No guessed center direction')
 def test_backward_or_extreme_fit_is_refused_instead_of_moving_endpoints(self):
  for angle in (0,-10):
   n=default_scene('stroke')['nodes'][0];n['attachment']=dict(to='mass',self='root',target='right')
   scene=dict(format='learn-draw/studio-1',canvas=[640,640],nodes=[dict(id='mass',kind='shape',intent='support',angle=angle),n])
   with self.assertRaisesRegex(ValueError,'direction'):aim_preview(scene,select(scene,n['id'],feature='root'),select(scene,'mass',feature='anchors',anchor='right'),None,'Cannot fit this chord')
 def test_actual_cli_preview_ready_accept_undo_and_target_alias_protection(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'working.json';scene=water();node_by_id(scene,'water')['bend']=0;write(p,scene)
   self.cli('inspect',p,'--object','water','--feature','root','--outdir',d/'source')
   self.cli('inspect',p,'--object','spout','--feature','anchors','--anchor','tip','--outdir',d/'target')
   self.cli('preview',p,'--selection',d/'source/selection.json','--aim',d/'target/selection.json','--reason','Let the stream leave the nozzle','--outdir',d/'fit')
   c=read(d/'fit/candidate.json');self.assertEqual(c['status'],'ready');self.assertEqual(read(p),scene)
   svg=(d/'fit/alignment.svg').read_text();self.assertIn('mount-direction-root',svg);self.assertIn('target-direction-tip',svg)
   self.cli('accept',p,d/'fit/candidate.json');self.cli('undo',p);self.assertEqual(read(p),scene)
   before=(d/'target/selection.json').read_bytes()
   self.cli('preview',p,'--selection',d/'source/selection.json','--aim',d/'target/selection.json','--reason','Protect target','--outdir',d/'target',expected=2)
   self.assertEqual((d/'target/selection.json').read_bytes(),before)
 def test_invalid_reuse_supersedes_prior_ready_direction_fit(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'working.json';scene=water();write(p,scene)
   self.cli('inspect',p,'--object','water','--feature','root','--outdir',d/'source')
   self.cli('inspect',p,'--object','spout','--feature','anchors','--anchor','tip','--outdir',d/'target')
   args=('preview',p,'--selection',d/'source/selection.json','--aim',d/'target/selection.json','--reason','A direction fit','--outdir',d/'fit')
   self.cli(*args);self.cli(*args,'--target-anchor','root',expected=2)
   self.assertNotEqual(read(d/'fit/candidate.json')['status'],'ready');self.assertEqual(read(d/'fit/report.json')['images'],[])
   with self.assertRaises(ValueError):accept(p,read(d/'fit/candidate.json'))
 def test_small_part_guides_keep_screen_scale_in_magnified_view(self):
  scene=read(ROOT/'examples/studio/camera.json');v=select(scene,'glass-glint',feature='anchors')
  zoom=[300,220,40,40];root=ET.fromstring(drawing(scene,v,viewbox=zoom));ns={'s':'http://www.w3.org/2000/svg'}
  text=root.find('s:text',ns);self.assertIsNotNone(text)
  self.assertAlmostEqual(float(text.attrib['font-size'])*min(640/40,480/40),13)
  circle=root.find("s:circle[@id='locked-center']",ns)
  self.assertAlmostEqual(float(circle.attrib['r'])*min(640/40,480/40),4)
  clean=drawing(scene);self.assertNotIn('mount-callout-',clean);self.assertNotIn('mount-direction-',clean)

if __name__=='__main__':unittest.main()
