"""Focused feedback must retain usable selection/transaction handles without stale artifacts."""
import contextlib,io,json,tempfile,sys,unittest
from pathlib import Path
from unittest.mock import patch
from scripts.studio.__main__ import main,default_scene
from scripts.studio.model import read,write,accept
ROOT=Path(__file__).resolve().parents[2]
class FocusedResponse(unittest.TestCase):
 def cli(self,*args,expected=0):
  with patch.object(sys,'argv',['studio',*map(str,args)]),contextlib.redirect_stdout(io.StringIO()) as out,contextlib.redirect_stderr(io.StringIO()) as err:r=main()
  self.assertEqual(r,expected,err.getvalue())
  if r!=0:return None
  try:return json.loads(out.getvalue())
  except json.JSONDecodeError:return out.getvalue().strip()
 def test_selected_part_feedback_keeps_exact_anchor_images_and_full_report_handle(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'working.json';write(p,read(ROOT/'examples/studio/person_flower.json'))
   compact=self.cli('inspect',p,'--object','shirt','--feature','anchors','--anchor','left@.77','--outdir',d/'view')
   full=read(d/'view/report.json')
   self.assertEqual(compact['format'],'learn-draw/studio-response-1');self.assertNotIn('nodes',compact)
   self.assertEqual(compact['object_count'],17);self.assertEqual(compact['images'],full['images'])
   self.assertEqual(compact['selection'],read(d/'view/selection.json'))
   self.assertEqual(list(compact['selected']['anchors']),['left@.77'])
   self.assertTrue(Path(compact['files']['report']).samefile(d/'view/report.json'))
   self.assertNotIn('candidate',compact['files'])
   self.assertLess(len(json.dumps(compact)),len(json.dumps(full))/3)
   raw=self.cli('inspect',p,'--object','shirt','--feature','anchors','--anchor','left@.77','--outdir',d/'view','--full-report')
   self.assertEqual(raw,read(d/'view/report.json'));self.assertEqual(len(raw['nodes']),17)
 def test_place_and_remove_feedback_refer_to_the_current_candidate(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'working.json';write(p,default_scene('blank'))
   placed=self.cli('place',p,'--kind','stroke','--id','gesture','--reason','A continuous gesture','--outdir',d/'new')
   self.assertIn('bend',placed['configure']['controls']);self.assertEqual(placed['selected']['authored']['id'],'gesture')
   self.assertTrue(Path(placed['files']['candidate']).samefile(d/'new/candidate.json'));self.assertEqual(placed['operation']['action'],'place')
   self.cli('accept',p,d/'new/candidate.json')
   self.cli('inspect',p,'--object','gesture','--feature','object','--outdir',d/'view')
   removed=self.cli('preview',p,'--selection',d/'view/selection.json','--remove','--reason','Discard the obsolete gesture','--outdir',d/'removed')
   self.assertEqual(removed['selected'],{'id':'gesture','removed':True});self.assertEqual(removed['object_count'],0)
 def test_inspect_reuse_invalidates_candidate_and_blank_does_not_export_stale_selection(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'working.json';blank=default_scene('blank');write(p,blank)
   self.cli('place',p,'--kind','shape','--reason','A pending mass','--outdir',d/'reuse')
   self.assertEqual(read(d/'reuse/candidate.json')['status'],'ready')
   inspected=self.cli('inspect',p,'--outdir',d/'reuse')
   self.assertNotIn('selection',inspected['files']);self.assertNotIn('candidate',inspected['files']);self.assertNotIn('selected',inspected)
   with self.assertRaises(ValueError):accept(p,read(d/'reuse/candidate.json'))
   self.assertEqual(read(p),blank)
   self.cli('inspect',p,'--object','missing','--outdir',d/'reuse',expected=2)
   self.assertEqual(read(d/'reuse/report.json')['images'],[])
   self.assertEqual(read(d/'reuse/report.json')['status'],'preparing')
 def test_response_failure_never_leaves_ready_candidate(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);p=d/'working.json';write(p,default_scene('blank'))
   with patch('scripts.studio.__main__.response',side_effect=RuntimeError('deliberate feedback failure')):
    self.cli('place',p,'--kind','shape','--reason','A pending mass','--outdir',d/'try',expected=2)
   self.assertNotEqual(read(d/'try/candidate.json')['status'],'ready')
   self.assertEqual(read(p),default_scene('blank'))
if __name__=='__main__':unittest.main()
