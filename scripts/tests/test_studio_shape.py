"""Generic masses must preserve a visible bounded edit and survive the normal edit journal."""
import copy
from pathlib import Path
import tempfile
import unittest
from scripts.studio.__main__ import default_scene
from scripts.studio.model import select,preview,parameter_preview,accept,undo,write,read,validate,fingerprint
from scripts.studio.shape import SIDES,shape_data,span,local_t
from scripts.studio.render import drawing


class ColourMass(unittest.TestCase):
    def test_every_side_moves_in_screen_space_only_inside_its_visible_interval(self):
        for profile in ('block','oval'):
            for side in SIDES:
                scene=default_scene('shape');node=scene['nodes'][0]
                node.update(profile=profile,angle=31,taper=.25,width=1.7)
                scene['canvas']=[960,540]
                before=shape_data(node,scene['canvas'])
                selection=select(scene,feature=side,at=.5,radius=.25)
                trial=preview(scene,selection,'left',.06,'Soften just this side of the mass')
                after=shape_data(trial['scene']['nodes'][0],scene['canvas'])
                changed=0
                for (q,a),(other_q,b) in zip(before.boundary,after.boundary):
                    self.assertEqual(q,other_q)
                    self.assertEqual(a[1],b[1])
                    if abs(local_t(q,side)-.5)>=.25:
                        self.assertEqual(a,b)
                    if q==next(q for q,p in before.boundary if abs(local_t(q,side)-.5)<1e-10):
                        self.assertAlmostEqual(b[0]-a[0],-.06*span(node,scene['canvas']))
                    changed+=a!=b
                self.assertGreater(changed,20)
                self.assertEqual(select(trial['scene'],feature=side,at=.5,radius=.25)['locks'],selection['locks'])

    def test_preview_accept_undo_and_parameter_edits_keep_the_original_scene(self):
        scene=default_scene('shape');before=copy.deepcopy(scene)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'scene.json';write(path,scene)
            trial=preview(scene,select(scene,feature='right'),'right',.1,'Bow the exposed right edge')
            self.assertEqual(scene,before)
            accept(path,trial);self.assertNotEqual(read(path),scene)
            trial2=parameter_preview(read(path),select(read(path),feature='object'),'profile','oval','Round the mass into a stone')
            accept(path,trial2);undo(path);undo(path)
            self.assertEqual(read(path),scene)

    def test_refuses_crossing_edits_invalid_parameters_and_unknown_fields(self):
        scene=default_scene('shape')
        with self.assertRaisesRegex(ValueError,'crosses|collapses'):
            preview(scene,select(scene,feature='left',at=.5,radius=.35),'right',2,'Test collapse refusal')
        for updates in ({'width':True},{'rounding':float('nan')},{'profile':'triangle'},{'taper':1}, {'points':[[0,0]]}):
            bad=copy.deepcopy(scene);bad['nodes'][0].update(updates)
            with self.assertRaises(ValueError): validate(bad)
        with self.assertRaises(ValueError): select(scene,feature='left',at=.1,radius=.3)

    def test_fill_ink_and_ids_are_separate_and_repeatable(self):
        scene=default_scene('shape');other=copy.deepcopy(scene['nodes'][0])
        other.update(id='other',depth=1,palette={'fill':'#b65d4f'},at={'anchor':'upper_right'})
        scene['nodes'].append(other)
        svg=drawing(scene)
        self.assertIn('colour-mass-mass',svg);self.assertIn('other-mass',svg)
        self.assertIn('#b65d4f',svg);self.assertEqual(svg,drawing(scene))
        scene['nodes'].reverse();self.assertEqual(svg,drawing(scene))

    def test_no_subject_or_pixel_input_required(self):
        scene=default_scene('shape')
        for profile in ('block','oval'):
            scene['nodes'][0]['profile']=profile
            self.assertIn('<path',drawing(scene))
            self.assertEqual(len(shape_data(scene['nodes'][0],scene['canvas']).boundary),256)

    def test_rotating_a_sculpted_mass_rotates_the_edit_with_its_material(self):
        import math
        scene=default_scene('shape')
        trial=preview(scene,select(scene,feature='left',at=.5,radius=.3),'left',.12,'Bulge the middle of the exposed side')
        before=shape_data(trial['scene']['nodes'][0],scene['canvas'])
        turned=parameter_preview(trial['scene'],select(trial['scene'],feature='object'),'angle',40,'Tilt the entire sculpted mass')
        after=shape_data(turned['scene']['nodes'][0],scene['canvas'])
        a=math.radians(40);cx,cy=before.center
        for (_,p),(_,q) in zip(before.boundary,after.boundary):
            x,y=p[0]-cx,p[1]-cy
            self.assertAlmostEqual(q[0],cx+x*math.cos(a)+y*math.sin(a))
            self.assertAlmostEqual(q[1],cy-x*math.sin(a)+y*math.cos(a))

    def test_thin_filled_mark_is_valid_without_a_subject_specific_stroke(self):
        scene=default_scene('shape');node=scene['nodes'][0]
        node.update(width=.008,stroke=0,palette={'fill':'#344b57'})
        validate(scene)
        data=shape_data(node,scene['canvas'])
        from .test_studio_hand import pixels
        import numpy as np
        image=pixels(scene)
        # A sub-two-pixel mark is antialiased; exact fill-colour pixels are not required.
        ink=np.all(image[:,:,:3]<150,axis=2)
        self.assertGreater(int(np.count_nonzero(ink)),150)
        self.assertLess(data.features['object']['bounds'][2]-data.features['object']['bounds'][0],2)

    def test_cli_refuses_inspection_output_that_would_overwrite_an_input(self):
        import subprocess,sys
        scene=default_scene('shape')
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            selection_path=base/'input-selection.json';write(selection_path,select(scene,feature='left'))
            for filename,command in [('scene.json','inspect'),('candidate.json','preview')]:
                out=base/command;out.mkdir()
                source=out/filename;write(source,scene);original=source.read_bytes()
                args=[sys.executable,'-m','scripts.studio',command,str(source),'--outdir',str(out),'--svg-only']
                if command=='preview': args+=['--selection',str(selection_path),'--move','left','--amount','.1','--reason','Test output collision refusal']
                result=subprocess.run(args,capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0,result.stdout)
                self.assertEqual(source.read_bytes(),original)
                self.assertIn('overwrite an input',result.stderr)
