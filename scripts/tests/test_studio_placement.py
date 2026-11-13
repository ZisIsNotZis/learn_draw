"""Pending placement must be visible, correctable and recoverable without editing the working scene."""
import copy,contextlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from scripts.studio.__main__ import default_scene,main
from scripts.studio.model import read,write,fingerprint,engine_fingerprint,select,accept,undo,validate
from scripts.studio.placement import placement_preview
from scripts.studio.render import bundle,drawing
from scripts.studio.attachment import resolve_scene,get_anchor

class PendingPlacement(unittest.TestCase):
    def cli(self,*args,expected=0):
        with patch.object(sys,'argv',['studio',*map(str,args)]),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()) as err:
            result=main()
        self.assertEqual(result,expected,err.getvalue())
    def test_observe_revise_accept_and_exact_undo(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'working.json';scene=default_scene('grip');write(p,scene);original=p.read_bytes()
            self.cli('place',p,'--kind','shape','--id','banner','--change','length=.17','--change','width=2','--at','upper_left','--reason','A red pennant above the hand','--outdir',d/'first')
            first=read(d/'first/candidate.json');self.assertEqual(p.read_bytes(),original)
            self.assertFalse((d/'working.history').exists())
            report=read(d/'first/report.json');self.assertEqual(report['insertion'],{'object':'banner'})
            svg=(d/'first/alignment.svg').read_text();self.assertTrue('mount-callout-top' in svg);self.assertTrue('edit-before-' not in svg)
            self.assertEqual(len(report['images']),4)
            self.cli('place',p,'--revise',d/'first/candidate.json','--move','right','--amount','.1','--change','fill_color=#cc5544','--reason','Move the pennant away from the edge','--outdir',d/'second')
            second=read(d/'second/candidate.json');self.assertEqual(second['scene']['nodes'][0],scene['nodes'][0])
            self.assertEqual(second['scene']['nodes'][-1]['palette']['fill'],'#cc5544')
            self.assertEqual(second['scene']['nodes'][-1]['length'],.17)
            self.assertEqual(first['scene']['nodes'][-1]['at']['anchor'],'upper_left')
            self.assertAlmostEqual(second['scene']['nodes'][-1]['at']['offset'][0],.1)
            self.assertEqual(p.read_bytes(),original)
            self.cli('accept',p,d/'second/candidate.json');self.assertEqual(len(read(p)['nodes']),2)
            self.cli('undo',p);self.assertEqual(read(p),scene);self.assertEqual(drawing(read(p)),drawing(scene))
    def test_all_native_presets_can_be_staged_on_blank_paper(self):
        for kind in ('head','hand','grip','hair-lock','stroke','shape','sky','hills','moon','sun'):
            with self.subTest(kind=kind):
                base=default_scene('blank');node=default_scene(kind)['nodes'][0]
                c=placement_preview(base,node,reason='Establish the subject')
                self.assertEqual(base['nodes'],[]);self.assertEqual(c['scene']['nodes'][0]['id'],node['id'])
                validate(c['scene'])
    def test_revision_refuses_stale_failed_and_foreign_scene_edits(self):
        base=default_scene('grip');c=placement_preview(base,default_scene('shape')['nodes'][0],reason='A flag')|{'status':'ready'}
        cases=[]
        for key,value in [('engine','old'),('base','old'),('status','rendering')]:
            bad=copy.deepcopy(c);bad[key]=value;cases.append(bad)
        bad=copy.deepcopy(c);bad['scene']['background']='#ffffff';bad['result']=fingerprint(bad['scene']);cases.append(bad)
        bad=copy.deepcopy(c);bad['scene']['nodes'][0]['intent']='silently changed';bad['result']=fingerprint(bad['scene']);cases.append(bad)
        bad=copy.deepcopy(c);bad['operation']['action']='remove';cases.append(bad)
        for bad in cases:
            with self.subTest(bad=bad.get('status')):
                with self.assertRaises(ValueError):placement_preview(base,prior=bad,reason='Correct the pending shape')
        with self.assertRaises(ValueError):placement_preview(base,prior=c,at='center',reason='Ambiguous correction')
    def test_observed_mount_can_be_attached_before_accepting(self):
        scene=default_scene('grip');node=default_scene('stroke')['nodes'][0]
        first=placement_preview(scene,node,reason='A pole extension')|{'status':'ready'}
        target=select(scene,'carrying-grip',feature='anchors',anchor='handle_right')
        c=placement_preview(scene,prior=first,target=target,self_anchor='root',reason='Seat the pole at the visible handle end')
        resolved=resolve_scene(c['scene']);a=get_anchor(resolved['nodes'][0],[640,640],'handle_right')['point'];b=get_anchor(resolved['nodes'][1],[640,640],'root')['point']
        for x,y in zip(a,b):self.assertAlmostEqual(x,y)
        self.assertEqual(scene,default_scene('grip'))
        with self.assertRaises(ValueError):placement_preview(scene,node,target=target,reason='Unobserved source')
        bad=dict(target,base='old')
        with self.assertRaises(ValueError):placement_preview(scene,prior=first,target=bad,reason='Stale target')
    def test_failed_reused_output_cannot_accept_an_older_proposal(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'working.json';scene=default_scene('blank');write(p,scene)
            args=('place',p,'--kind','shape','--reason','A lantern','--outdir',d/'try')
            self.cli(*args)
            with patch('scripts.studio.render.rasterize',side_effect=RuntimeError('deliberate renderer failure')):
                self.cli(*args,expected=2)
            c=read(d/'try/candidate.json');self.assertEqual(c['status'],'rendering')
            self.assertEqual(read(d/'try/report.json')['images'],[])
            self.assertEqual((d/'try/report.txt').read_text(),'')
            with self.assertRaises(ValueError):accept(p,c)
            self.assertEqual(read(p),scene)
            self.cli('place',p,'--kind','shape','--change','width=-2','--reason','Invalid shape','--outdir',d/'try',expected=2)
            self.assertEqual(read(d/'try/candidate.json')['status'],'preparing')
    def test_output_aliases_refuse_before_overwriting_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'working.json';write(p,default_scene('blank'))
            self.cli('place',p,'--kind','shape','--reason','A lantern','--outdir',d/'first')
            prior=d/'first/candidate.json';before=prior.read_bytes()
            self.cli('place',p,'--revise',prior,'--move','left','--reason','Correction','--outdir',d/'first',expected=2)
            self.assertEqual(prior.read_bytes(),before)
            alias=d/'alias';alias.mkdir();(alias/'scene.json').hardlink_to(p);original=p.read_bytes()
            self.cli('place',p,'--kind','shape','--reason','A lantern','--outdir',alias,expected=2)
            self.assertEqual(p.read_bytes(),original)
    def test_invalid_initial_parameters_leave_source_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'working.json';scene=default_scene('blank');write(p,scene)
            self.cli('place',p,'--kind','shape','--change','length=.2','--change','length=.3','--reason','Ambiguous length','--outdir',d/'try',expected=2)
            self.assertEqual(read(p),scene);self.assertNotEqual(read(d/'try/candidate.json')['status'],'ready')
            with self.assertRaises(ValueError):placement_preview(scene,default_scene('shape')['nodes'][0],reason=' ')

if __name__=='__main__':unittest.main()
