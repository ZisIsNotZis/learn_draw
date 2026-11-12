"""Two inspected targets preserve both gesture contacts through real composition revisions."""
import copy,sys,subprocess,tempfile,unittest,math
from pathlib import Path
import numpy as np
from scripts.studio.__main__ import default_scene
from scripts.studio.model import select,bind_endpoint_preview,unbind_endpoint_preview,parameters_preview,preview,detach_preview,remove_preview,validate,read,write,accept,undo,node_by_id
from scripts.studio.attachment import get_anchor,resolve_scene
from scripts.studio.components import component_data
from scripts.studio.render import drawing,bundle
from .test_studio_hand import pixels


def fixture():
    s=default_scene('stroke');s['canvas']=[900,600];s['nodes'][0].update(id='bridge',length=.3,thickness=.02,bend=.12,depth=4)
    s['nodes'] += [dict(id='source',kind='shape',intent='one movable support',length=.12,width=.8,depth=0,angle=20,at=dict(anchor='center',offset=[-.2,-.1])),
                   dict(id='destination',kind='shape',intent='a separately movable destination',length=.15,width=1.5,depth=1,angle=-12,at=dict(anchor='center',offset=[.2,.15]))]
    return s


def bind(s,end,target,anchor='center',inset=0):
    return bind_endpoint_preview(s,select(s,'bridge',feature=end),select(s,target,feature='anchors',anchor=anchor),None,inset,'Keep this gesture connected to the inspected surface')


def connected():
    s=bind(fixture(),'root','source','right',.1)['scene']
    return bind(s,'tip','destination','top@.3',.1)['scene']


def ends(s):
    n=node_by_id(resolve_scene(s),'bridge');d=component_data(n,s['canvas']);return np.array([d.rows[0].spine,d.rows[-1].spine])


class TwoEndpointGestures(unittest.TestCase):
    def test_two_targets_derive_chord_and_follow_independent_rotated_nonsquare_changes(self):
        s=connected();before=copy.deepcopy(s);old=ends(s)
        self.assertNotIn('length',s['nodes'][0]);self.assertNotIn('angle',s['nodes'][0]);self.assertNotIn('at',s['nodes'][0])
        moved=preview(s,select(s,'source',feature='object'),'left',.08,'Move the source independently')['scene']
        np.testing.assert_allclose(ends(moved)[0]-old[0],[-48,0],atol=1e-8);np.testing.assert_allclose(ends(moved)[1],old[1],atol=1e-8)
        moved=parameters_preview(moved,select(moved,'destination',feature='object'),{'angle':37,'length':.21},'Reshape and turn the receiving support')['scene']
        np.testing.assert_allclose(ends(moved)[0],ends(s)[0]+[-48,0],atol=1e-8)
        self.assertFalse(np.allclose(ends(moved)[1],old[1]));self.assertEqual(s,before)
        self.assertEqual(moved['nodes'][0],s['nodes'][0]);moved['nodes'].reverse();np.testing.assert_allclose(ends(moved),ends(dict(moved,nodes=list(reversed(moved['nodes'])))))

    def test_bound_controls_do_not_offer_ignored_length_angle_or_moves(self):
        s=connected();selection=select(s,'bridge',feature='object')
        self.assertNotIn('length',selection['controls']);self.assertNotIn('angle',selection['controls']);self.assertIn('bend',selection['controls'])
        with self.assertRaisesRegex(ValueError,'exposed'): parameters_preview(s,selection,{'length':.4},'Do not silently ignore this')
        with self.assertRaisesRegex(ValueError,'both endpoints'): preview(s,selection,'left',.1,'Cannot translate two pinned contacts')
        for end in ('root','tip'):
            with self.assertRaisesRegex(ValueError,'attached pin'): preview(s,select(s,'bridge',feature=end),'up',.01,'Do not move a pinned terminal')
        bad=copy.deepcopy(s);bad['nodes'][0]['angle']=1
        with self.assertRaisesRegex(ValueError,'derive'): validate(bad)
        with self.assertRaisesRegex(ValueError,'resolve'): component_data(s['nodes'][0],s['canvas'])

    def test_local_push_uses_derived_angle_and_protects_both_contacts_and_thickness(self):
        s=connected();before=component_data(node_by_id(resolve_scene(s),'bridge'),s['canvas'])
        changed=preview(s,select(s,'bridge',feature='spine',at=.5,radius=.25),'up',.3,'Refine the middle while retaining both targets')['scene']
        after=component_data(node_by_id(resolve_scene(changed),'bridge'),s['canvas'])
        np.testing.assert_allclose(ends(changed),ends(s),atol=1e-8)
        np.testing.assert_allclose(np.array(after.rows[40].spine)-before.rows[40].spine,[0,-.3*.02*600],atol=1e-8)
        for a,b in zip(before.rows,after.rows):self.assertAlmostEqual(math.dist(a.left,a.right),math.dist(b.left,b.right))

    def test_release_either_or_both_keeps_exact_paint_and_allows_free_terminal_work(self):
        s=connected();original=pixels(s)
        for end in ('root','tip'):
            trial=unbind_endpoint_preview(s,select(s,'bridge',feature=end),'Release this end without teleporting the curve')
            self.assertTrue(np.array_equal(original,pixels(trial['scene'])))
            moved=preview(trial['scene'],select(trial['scene'],'bridge',feature=end),'right',.02,'Adjust only the freed contact')['scene']
            i=0 if end=='root' else 1;np.testing.assert_allclose(ends(moved)[i]-ends(s)[i],[12,0],atol=1e-8)
            np.testing.assert_allclose(ends(moved)[1-i],ends(s)[1-i],atol=1e-8)
        detached=detach_preview(s,select(s,'bridge',feature='anchors'),'Release the complete bridge without changing paint')['scene']
        self.assertNotIn('endpoints',detached['nodes'][0]);self.assertTrue(np.array_equal(original,pixels(detached)))

    def test_deleting_either_target_releases_only_affected_end_and_cascade_traverses_both_links(self):
        s=connected()
        for target in ('source','destination'):
            trial=remove_preview(s,select(s,target,feature='object'),'Remove this support, preserve the visible bridge')['scene']
            np.testing.assert_allclose(ends(trial),ends(s),atol=1e-8)
            self.assertEqual(len(trial['nodes'][0]['endpoints']),1)
            cascade=remove_preview(s,select(s,target,feature='object'),'Remove every dependent part',True)['scene']
            self.assertNotIn('bridge',[n['id'] for n in cascade['nodes']])

    def test_inspection_cycles_invalid_spans_and_undo_remain_safe(self):
        s=fixture();wrong=select(s,'bridge',feature='object')
        with self.assertRaisesRegex(ValueError,'root or tip'): bind_endpoint_preview(s,wrong,select(s,'source',feature='anchors'),None,0,'Wrong feature')
        with self.assertRaisesRegex(ValueError,'exact'): bind_endpoint_preview(s,select(s,'bridge',feature='root'),select(s,'source',feature='anchors'),'right@.3',0,'Uninspected position')
        one=bind(s,'root','source')['scene']
        with self.assertRaisesRegex(ValueError,'length'): bind(one,'tip','source')
        bad=copy.deepcopy(connected());bad['nodes'][1]['attachment']=dict(to='bridge');bad['nodes'][1].pop('at')
        with self.assertRaisesRegex(ValueError,'cycle'):validate(bad)
        trial=bind(one,'tip','destination');before=copy.deepcopy(one)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'working.json';write(p,one);accept(p,trial);undo(p);self.assertEqual(read(p),before);accept(p,trial)
        changed=preview(one,select(one,'source',feature='object'),'left',.02,'Change source')['scene']
        with self.assertRaisesRegex(ValueError,'stale'): bind_endpoint_preview(changed,select(one,'bridge',feature='tip'),select(one,'destination',feature='anchors'),None,0,'Old target inspection')

    def test_actual_watering_reframe_has_a_discriminating_free_tip_control(self):
        old=read('examples/studio/watering.json');selection=select(old,'gardener',feature='object')
        loose=preview(old,selection,'left',.05,'Reframe the original person')['scene']
        def tip(s):return component_data(node_by_id(resolve_scene(s),'water'),s['canvas']).rows[-1].spine
        np.testing.assert_allclose(np.array(tip(loose))-tip(old),[-36,0],atol=1e-8)
        fixed=bind_endpoint_preview(old,select(old,'water',feature='tip'),select(old,'soil',feature='anchors',anchor='center'),None,0,'Keep pouring onto soil when the gardener moves')['scene']
        reframed=preview(fixed,select(fixed,'gardener',feature='object'),'left',.05,'Reframe with a two-ended stream')['scene']
        np.testing.assert_allclose(tip(reframed),tip(fixed),atol=1e-8)
        self.assertEqual(node_by_id(reframed,'water'),node_by_id(fixed,'water'))

    def test_cli_binding_reports_derived_span_pin_guides_and_can_be_released(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'working.json';s=bind(fixture(),'root','source')['scene'];write(p,s)
            def run(*args,code=0):
                r=subprocess.run([sys.executable,'-m','scripts.studio',*map(str,args)],capture_output=True,text=True)
                self.assertEqual(r.returncode,code,r.stderr);return r
            run('inspect',p,'--object','bridge','--feature','tip','--outdir',d/'tip')
            run('inspect',p,'--object','destination','--feature','anchors','--anchor','top@.3','--outdir',d/'target')
            original_target=(d/'target/selection.json').read_bytes()
            run('preview',p,'--selection',d/'tip/selection.json','--bind-end',d/'target/selection.json','--reason','Must preserve target input','--outdir',d/'target',code=2)
            self.assertEqual((d/'target/selection.json').read_bytes(),original_target)
            self.assertFalse((d/'target/candidate.json').exists())
            run('preview',p,'--selection',d/'tip/selection.json','--bind-end',d/'target/selection.json','--reason','Join the receiving surface','--outdir',d/'try')
            report=read(d/'try/report.json');self.assertIn('derived_chord',report['nodes']['bridge'])
            self.assertNotIn('length',report['nodes']['bridge']['features']['object']['controls'])
            self.assertIn('id="pinned-tip"',(d/'try/alignment.svg').read_text())
            run('accept',p,d/'try/candidate.json');run('inspect',p,'--object','bridge','--feature','tip','--outdir',d/'bound')
            run('preview',p,'--selection',d/'bound/selection.json','--unbind-end','--reason','Release only the receiving contact','--outdir',d/'release')
            self.assertTrue(np.array_equal(pixels(read(p)),pixels(read(d/'release/scene.json'))))


if __name__=='__main__':unittest.main()
