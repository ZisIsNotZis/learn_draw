"""Removing paint must preserve retained structure, visible impact and recoverable history."""
import copy
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import numpy as np
from scripts.studio.__main__ import default_scene
from scripts.studio.model import read,write,select,remove_preview,attachment_preview,detach_preview,accept,undo,validate,parameters_preview
from scripts.studio.attachment import resolve_scene
from scripts.studio.components import component_data
from scripts.studio.render import bundle,drawing
from .test_studio_hand import pixels


def chain():
    s=default_scene('shape');s['canvas']=[900,600]
    s['nodes'][0].update(id='support',length=.2,width=.7,angle=19,depth=0)
    s['nodes'] += [dict(id='arm',kind='stroke',intent='a curved mark attached to the support',length=.23,bend=.2,angle=70,depth=2,
                       attachment=dict(to='support',self='root',target='right@.2',inset=.04)),
                   dict(id='hand',kind='hand',intent='a hand following the arm',length=.12,angle=-5,depth=3,
                        attachment=dict(to='arm',self='wrist',target='tip')),
                   dict(id='moon',kind='moon',intent='an unrelated moon',length=.08,depth=4)]
    return validate(s)


class RecoverableRemoval(unittest.TestCase):
    def test_parent_removal_releases_direct_children_without_teleporting_descendants(self):
        s=chain();original=copy.deepcopy(s);placed=resolve_scene(s)
        trial=remove_preview(s,select(s,'support',feature='object'),'Replace the support while retaining the gesture')
        self.assertEqual(s,original);self.assertEqual(trial['operation']['removed'],['support'])
        self.assertEqual(trial['operation']['detached_children'],['arm'])
        self.assertNotIn('attachment',trial['scene']['nodes'][0])
        self.assertEqual(trial['scene']['nodes'][1:],s['nodes'][2:])
        now=resolve_scene(trial['scene'])
        for before,after in zip(placed['nodes'][1:],now['nodes']):
            self.assertEqual(component_data(before,s['canvas']).svg,component_data(after,s['canvas']).svg)
        expected=copy.deepcopy(placed);expected['nodes']=expected['nodes'][1:]
        self.assertTrue(np.array_equal(pixels(expected),pixels(trial['scene'])))

    def test_cascade_removes_transitive_chain_but_preserves_unrelated_object_and_order(self):
        s=chain();s['nodes'].reverse()
        trial=remove_preview(s,select(s,'support',feature='object'),'Remove this entire unwanted assembly',True)
        self.assertEqual(trial['operation']['removed'],['hand','arm','support'])
        self.assertEqual(trial['operation']['detached_children'],[])
        self.assertEqual(trial['scene']['nodes'],[s['nodes'][0]])
        isolated=dict(s,nodes=[s['nodes'][0]])
        self.assertTrue(np.array_equal(pixels(isolated),pixels(trial['scene'])))

    def test_accept_undo_last_object_and_replay_restore_exact_scene_and_picture(self):
        s=default_scene('head');before=pixels(s)
        trial=remove_preview(s,select(s,feature='object'),'Clear this study for a different drawing')
        self.assertEqual(trial['scene']['nodes'],[])
        empty=pixels(trial['scene']);self.assertTrue(np.all(empty==empty[0,0]))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'working.json';write(p,s);accept(p,trial)
            self.assertEqual(read(p),trial['scene']);undo(p)
            self.assertEqual(read(p),s);self.assertTrue(np.array_equal(pixels(read(p)),before))
            accept(p,trial);self.assertEqual(read(p),trial['scene'])
        with self.assertRaisesRegex(ValueError,'empty canvas'): select(trial['scene'])

    def test_whole_object_reason_boolean_and_current_revision_are_required(self):
        s=chain();selection=select(s,'support',feature='object')
        with self.assertRaisesRegex(ValueError,'whole object'): remove_preview(s,select(s,'support',feature='left'),'Delete')
        with self.assertRaisesRegex(ValueError,'reason'): remove_preview(s,selection,' ')
        with self.assertRaisesRegex(ValueError,'boolean'): remove_preview(s,selection,'Delete','false')
        changed=parameters_preview(s,selection,{'angle':23},'Turn support')['scene']
        with self.assertRaisesRegex(ValueError,'stale selection'): remove_preview(changed,selection,'Delete')
        wrong=dict(selection,engine='obsolete')
        with self.assertRaisesRegex(ValueError,'implementation'): remove_preview(s,wrong,'Delete')

    def test_removal_bundle_clean_art_and_ghosts_describe_distinct_states(self):
        s=chain();trial=remove_preview(s,select(s,'support',feature='object'),'Remove only the support')
        with tempfile.TemporaryDirectory() as d:
            report=bundle(trial['scene'],d,trial['selection'],s)
            svg=(Path(d)/'artwork.svg').read_text();overlay=(Path(d)/'alignment.svg').read_text()
            ET.fromstring(svg);ET.fromstring(overlay)
            self.assertNotIn('id="support"',svg);self.assertNotIn('id="remove-support"',svg)
            self.assertIn('id="remove-support"',overlay);self.assertIn('id="keep-arm"',overlay)
            self.assertNotIn('id="remove-hand"',overlay)
            self.assertEqual(report['removal']['detached_children'],['arm'])
            self.assertEqual(report['nodes'].keys(),{'arm','hand','moon'})
        with self.assertRaisesRegex(ValueError,'previous scene'): drawing(trial['scene'],trial['selection'])

    def test_impact_view_cannot_be_reused_as_a_new_part_inspection(self):
        s=chain();trial=remove_preview(s,select(s,'support',feature='object'),'Consider removing support')
        # Declining removal leaves the original scene current. Its impact view is
        # nevertheless not a new feature inspection for another kind of edit.
        with self.assertRaisesRegex(ValueError,'impact'):
            parameters_preview(s,trial['selection'],{'angle':23},'Turn the support instead')
        with self.assertRaisesRegex(ValueError,'impact'):
            remove_preview(s,trial['selection'],'Remove only after a real inspection')
        mounting=attachment_preview(s,select(s,'arm',feature='anchors'),select(s,'moon',feature='anchors'),'root','center',0,'Consider a different mount')
        with self.assertRaisesRegex(ValueError,'impact'):
            detach_preview(s,mounting['selection'],'Release the existing mount instead')

    def test_cli_blank_add_delete_accept_undo_and_invalid_reuse_leave_safe_state(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'working.json'
            def run(*args,code=0):
                r=subprocess.run([sys.executable,'-m','scripts.studio',*map(str,args)],capture_output=True,text=True)
                self.assertEqual(r.returncode,code,r.stderr);return r
            run('new',p,'--kind','blank');run('inspect',p,'--outdir',d/'blank')
            self.assertEqual(read(d/'blank/report.json')['nodes'],{})
            run('add',p,'--kind','stroke','--id','mark')
            with_mark=read(p);run('inspect',p,'--feature','object','--outdir',d/'view')
            common=['preview',p,'--selection',d/'view/selection.json','--reason','Clear the mark','--outdir',d/'trial']
            run(*common,'--remove');ready=read(d/'trial/candidate.json')
            run(*common,'--move','left','--cascade',code=2)
            self.assertNotEqual(read(d/'trial/candidate.json')['status'],'ready')
            self.assertEqual(read(d/'trial/report.json')['images'],[])
            run('accept',p,d/'trial/candidate.json',code=2);self.assertEqual(read(p),with_mark)
            run(*common,'--remove');run('accept',p,d/'trial/candidate.json')
            self.assertEqual(read(p)['nodes'],[]);run('undo',p);self.assertEqual(read(p),with_mark)
            run('undo',p);self.assertEqual(read(p)['nodes'],[])


if __name__=='__main__': unittest.main()
