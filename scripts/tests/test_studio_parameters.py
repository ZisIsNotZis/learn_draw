"""A grouped edit is one inspected proposal, including its failures and undo boundary."""
import copy
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

from scripts.studio.__main__ import default_scene
from scripts.studio.model import accept,fingerprint,parameter_preview,parameters_preview,read,select,undo,write
from scripts.studio.render import bundle,drawing


class ParameterGroups(unittest.TestCase):
    def test_group_matches_separate_changes_but_accepts_and_undoes_once(self):
        scene=default_scene('shape');original=copy.deepcopy(scene)
        changes={'length':.17,'width':1.8,'taper':.65,'rounding':.08,'stroke':0,'fill_color':'#c98d4a'}
        trial=parameters_preview(scene,select(scene,feature='object'),changes,'Build one coherent warm lamp shade')
        sequential=scene
        for key,value in changes.items():
            sequential=parameter_preview(sequential,select(sequential,feature='object'),key,value,'Reference serial operation')['scene']
        self.assertEqual(trial['scene'],sequential)
        self.assertEqual(drawing(trial['scene']),drawing(sequential))
        self.assertEqual(scene,original)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'working.json';write(p,scene)
            accept(p,trial)
            journal=read(p.parent/'working.history'/'journal.json')
            self.assertEqual(len(journal),1)
            self.assertEqual(journal[0]['operation']['parameters'],changes)
            undo(p);self.assertEqual(read(p),original)

    def test_bad_group_preserves_inputs_and_feature_scope(self):
        scene=default_scene('head');before=copy.deepcopy(scene);selection=select(scene,feature='eyes')
        for changes in ({'eye_scale':.9,'jaw':.3},{'eye_scale':.9,'gaze':2},{'eye_scale':False},{},['eye_scale']):
            with self.assertRaises(ValueError): parameters_preview(scene,selection,changes,'Check refusal before any working change')
            self.assertEqual(scene,before)
        trial=parameters_preview(scene,selection,{'eye_scale':.9,'gaze':.4},'Adjust aperture and shared attention together')
        self.assertEqual(trial['scene']['nodes'][0]['eye_scale'],.9)
        self.assertEqual(trial['scene']['nodes'][0]['gaze'],.4)
        with self.assertRaises(ValueError): parameters_preview(scene,selection,{'eye_scale':.9},' ')

    def test_group_cli_ready_failure_invalidation_and_duplicate_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'working.json';scene=default_scene('shape');write(p,scene)
            view=root/'view';bundle(scene,view,select(scene,feature='object'),png=False)
            output=root/'try'
            args=[sys.executable,'-m','scripts.studio','preview',str(p),'--selection',str(view/'selection.json'),
                  '--change','length=.17','--change','width=1.8','--change','intent=a shade = a single mass',
                  '--reason','Set a coherent object before judging its picture','--outdir',str(output),'--svg-only']
            good=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(good.returncode,0,good.stderr)
            candidate=read(output/'candidate.json');self.assertEqual(candidate['status'],'ready')
            self.assertEqual(candidate['scene']['nodes'][0]['intent'],'a shade = a single mass')
            self.assertEqual(read(p),scene)
            for extra in (['--change','width=2'],['--change','bad'],['--change','width='],['--change','angle=nan'],['--value','bad']):
                bad=subprocess.run(args+extra,capture_output=True,text=True)
                self.assertNotEqual(bad.returncode,0)
                self.assertEqual(read(output/'candidate.json')['status'],'preparing')
                self.assertEqual(read(output/'report.json')['images'],[])
                with self.assertRaises(ValueError): accept(p,read(output/'candidate.json'))
                self.assertEqual(read(p),scene)

    def test_single_control_api_keeps_its_existing_operation_record(self):
        scene=default_scene('shape')
        trial=parameter_preview(scene,select(scene,feature='object'),'width','1.5','Widen the mass')
        self.assertEqual(trial['operation']['parameter'],'width')
        self.assertEqual(trial['operation']['value'],1.5)
        self.assertNotIn('parameters',trial['operation'])
