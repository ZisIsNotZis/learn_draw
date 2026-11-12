"""Named pins follow derived geometry while authored data and recoverable edits stay semantic."""
import copy
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
import numpy as np

from scripts.studio.__main__ import default_scene
from scripts.studio.attachment import anchors,mount_scale,resolve_scene
from scripts.studio.components import component_data
from scripts.studio.model import attachment_preview,detach_preview,parameters_preview,preview,read,select,validate,write,accept,undo,node_by_id
from scripts.studio.render import bundle,drawing
from .test_studio_hand import pixels


def pair():
    s=default_scene('shape');s['canvas']=[900,600]
    s['nodes'][0].update(id='base',depth=0,length=.1,width=2.2,profile='oval',angle=23,at={'anchor':'center','offset':[.1,.2]})
    s['nodes'].append(dict(id='stem',kind='shape',intent='a narrow support pinned to the base',length=.32,width=.09,angle=-35,stroke=0,depth=1,palette={'fill':'#705448'}))
    return s


def pin(scene,child='stem',parent='base',own='bottom',target='top',inset=.02):
    return attachment_preview(scene,select(scene,child,feature='anchors'),select(scene,parent,feature='anchors'),own,target,inset,'Seat the named material mounts before further drawing')


class GeometryPins(unittest.TestCase):
    def assertMount(self,scene,child):
        resolved=resolve_scene(scene);raw=node_by_id(scene,child);r=raw['attachment']
        node=node_by_id(resolved,child);parent=node_by_id(resolved,r['to']);canvas=scene['canvas']
        own=anchors(node,canvas)[r.get('self','center')]['point'];target=anchors(parent,canvas)[r.get('target','center')]
        normal=target['normal'] or (0,0);offset=r.get('offset',[0,0])
        for k in (0,1):
            self.assertAlmostEqual(own[k],target['point'][k]-normal[k]*r.get('inset',0)*mount_scale(parent,canvas)+offset[k]*min(canvas))
        self.assertNotIn('at',raw)
        return resolved

    def test_rotated_nonsquare_painted_mount_matches_without_changing_authored_positions(self):
        s=pair();before=copy.deepcopy(s);trial=pin(s)
        self.assertEqual(s,before);self.assertMount(trial['scene'],'stem')
        self.assertEqual(trial['scene']['nodes'][1]['angle'],-35)
        with self.assertRaisesRegex(ValueError,'resolve the scene'): component_data(trial['scene']['nodes'][1],s['canvas'])
        image=pixels(trial['scene']);self.assertEqual(image.shape[:2],(600,900))

    def test_chains_follow_parent_translation_resize_rotation_and_surface_sculpt(self):
        s=pin(pair())['scene']
        s['nodes'].append(dict(id='head',kind='shape',intent='a small top mounted above the support',length=.08,width=1.4,depth=2))
        s=pin(s,'head','stem','bottom','top',0)['scene']
        s['nodes'].append(dict(id='unrelated',kind='shape',intent='an unrelated mark',length=.06,width=1,depth=10,at={'anchor':'upper_left'}))
        untouched=component_data(s['nodes'][-1],s['canvas']).svg
        s=preview(s,select(s,'base',feature='object'),'left',.1,'Move the whole mounted assembly')['scene']
        s=parameters_preview(s,select(s,'base',feature='object'),{'length':.16,'angle':-17},'Change the support geometry while retaining its mount')['scene']
        s=preview(s,select(s,'base',feature='top',at=.5,radius=.3),'up',.08,'Lift only the supporting surface beneath its child')['scene']
        self.assertMount(s,'stem');self.assertMount(s,'head')
        self.assertEqual(component_data(s['nodes'][-1],s['canvas']).svg,untouched)
        s['nodes'].reverse();validate(s);self.assertMount(s,'stem');self.assertMount(s,'head')

    def test_accept_undo_and_detach_preserve_the_actual_rendered_placement(self):
        base=pair();trial=pin(base);s=trial['scene']
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'working.json';write(path,base)
            accept(path,trial);self.assertMount(read(path),'stem');undo(path);self.assertEqual(read(path),base)
            accept(path,trial)
            detached=detach_preview(s,select(s,'stem',feature='anchors'),'Release this pin without teleporting the support')
            self.assertTrue(np.array_equal(pixels(s),pixels(detached['scene'])))
            accept(path,detached);undo(path);self.assertEqual(read(path),s)
        with self.assertRaises(ValueError): detach_preview(base,select(base,'stem',feature='anchors'),'Already free')

    def test_attached_object_nudge_keeps_relation_and_pinned_edge_push_is_refused(self):
        s=pin(pair())['scene'];old=self.assertMount(s,'stem');oldp=anchors(node_by_id(old,'stem'),s['canvas'])['center']['point']
        moved=preview(s,select(s,'stem',feature='object'),'right',.04,'Adjust the retained offset from the mount')['scene']
        new=self.assertMount(moved,'stem');newp=anchors(node_by_id(new,'stem'),s['canvas'])['center']['point']
        self.assertAlmostEqual(newp[0]-oldp[0],.04*min(s['canvas']));self.assertAlmostEqual(newp[1],oldp[1])
        with self.assertRaisesRegex(ValueError,'attached anchor'):
            preview(s,select(s,'stem',feature='bottom',at=.5,radius=.25),'down',.04,'Cannot pull the fixed pin away')
        with self.assertRaisesRegex(ValueError,'attached anchor'):
            preview(s,select(s,'stem',feature='bottom',at=.35,radius=.14),'left',.04,'The adjacent tangent also supports the painted pin')
        edited=preview(s,select(s,'stem',feature='top',at=.5,radius=.25),'left',.04,'Refine the free end while preserving its lower mount')['scene']
        self.assertMount(edited,'stem')

    def test_missing_targets_cycles_unknown_mounts_and_invalid_relations_are_refused(self):
        s=pin(pair())['scene']
        for relation in ({'to':'missing'},{'to':'stem'},{'to':'base','self':'no-such-anchor'},{'to':'base','target':'center','inset':.1},{'to':'base','inset':float('nan')},{'to':'base','inset':True},{'to':'base','offset':[0]},{'to':'base','unexpected':1}):
            bad=copy.deepcopy(s);bad['nodes'][1]['attachment']=relation
            with self.assertRaises(ValueError): validate(bad)
        bad=copy.deepcopy(s);bad['nodes'][0].pop('at');bad['nodes'][0]['attachment']={'to':'stem'}
        with self.assertRaisesRegex(ValueError,'cycle'): validate(bad)
        bad=copy.deepcopy(s);bad['nodes'][1]['at']={'anchor':'center'}
        with self.assertRaisesRegex(ValueError,'not both'): validate(bad)
        bad=copy.deepcopy(s);bad['nodes'][1].update(kind='sky')
        with self.assertRaises(ValueError): validate(bad)

    def test_both_inspections_must_match_the_current_scene_and_be_anchor_views(self):
        s=pair();source=select(s,'stem',feature='anchors');target=select(s,'base',feature='anchors')
        changed=parameters_preview(s,select(s,'base',feature='object'),{'length':.12},'Change the target before attaching')['scene']
        with self.assertRaisesRegex(ValueError,'stale'): attachment_preview(changed,select(changed,'stem',feature='anchors'),target,'bottom','top',0,'Old target is stale')
        with self.assertRaisesRegex(ValueError,'inspect anchors'): attachment_preview(s,select(s,'stem',feature='object'),target,'bottom','top',0,'Use actual named pins')

    def test_attached_hand_tip_moves_in_screen_space_and_head_lock_inspects_in_context(self):
        for kind in ('hand','head','hair-lock'):
            s=pair();s['nodes'][1]=default_scene(kind)['nodes'][0];s['nodes'][1]['id']='child';s['nodes'][1]['depth']=1
            s=pin(s,'child','base','center','center',0)['scene'];self.assertMount(s,'child')
            if kind=='hand':
                before=select(s,'child',feature='index');after=preview(s,before,'left',.025,'Ease this fingertip in its mounted context')['scene']
                current=select(after,'child',feature='index')
                self.assertAlmostEqual(current['focus'][0]-before['focus'][0],-.025*before['nominal_span'])
                self.assertAlmostEqual(current['focus'][1],before['focus'][1]);self.assertMount(after,'child')
            if kind=='head':
                choice=select(s,'child',feature='left-lock');self.assertIn('locked-root',drawing(s,choice))

    def test_cli_attach_uses_two_inspections_and_protects_the_target_input(self):
        s=pair()
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'working.json';write(path,s)
            source=root/'source';target=root/'target';out=root/'try'
            bundle(s,source,select(s,'stem',feature='anchors'),png=False);bundle(s,target,select(s,'base',feature='anchors'),png=False)
            args=[sys.executable,'-m','scripts.studio','preview',str(path),'--selection',str(source/'selection.json'),'--attach',str(target/'selection.json'),'--self-anchor','bottom','--target-anchor','top','--inset','.02','--reason','Seat these two inspected mounts','--outdir',str(out),'--svg-only']
            result=subprocess.run(args,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
            trial=read(out/'candidate.json');self.assertEqual(trial['status'],'ready');self.assertEqual(read(path),s)
            self.assertIn('mount-target',(out/'alignment.svg').read_text(encoding='utf-8'))
            self.assertMount(trial['scene'],'stem')
            original=(target/'selection.json').read_bytes();args[args.index('--outdir')+1]=str(target)
            result=subprocess.run(args,capture_output=True,text=True);self.assertNotEqual(result.returncode,0)
            self.assertEqual((target/'selection.json').read_bytes(),original)

    def test_a_deeper_inset_is_a_valid_previewable_embedding_not_an_arbitrary_half_width_limit(self):
        scene=pin(pair(),inset=.65)['scene']
        self.assertMount(scene,'stem')
        with self.assertRaises(ValueError): pin(pair(),inset=2.01)
