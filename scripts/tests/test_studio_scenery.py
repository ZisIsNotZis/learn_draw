"""Scenic composition, opaque support and recoverable screen-space placement."""
import copy
from io import BytesIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image
import resvg_py

from scripts.studio.__main__ import default_scene
from scripts.studio.components import component_data
from scripts.studio.model import accept, fingerprint, parameter_preview, preview, read, select, undo, validate, write
from scripts.studio.render import drawing


def pixels(scene):
    return np.asarray(Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=drawing(scene)))).convert('RGB'))


class ScenicComposition(unittest.TestCase):
    def test_foreground_trees_remain_connected_to_the_changed_ridge(self):
        from shapely import Polygon
        for horizon,side in ((.3,'left'),(.75,'right')):
            scene=default_scene('hills');node=scene['nodes'][0]
            node.update(trees=5,tree_scale=.35,horizon=horizon,relief=.12,tree_side=side)
            validate(scene)
            data=component_data(node,scene['canvas'])
            self.assertTrue(Polygon(data.outline).is_valid)
            # All five full crowns plus roots must be inside the connected support.
            self.assertEqual(data.svg.count('a tapered evergreen rooted on the near ridge'),5)

    def test_object_movement_uses_screen_space_and_preserves_others_and_undo(self):
        for kind in ('head','moon','sun','hair-lock'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as directory:
                scene=default_scene(kind);scene['canvas']=[960,640]
                scene['nodes'].append(dict(id='backdrop',kind='sky',intent='an unchanged background'))
                ident=scene['nodes'][0]['id']
                old=copy.deepcopy(scene)
                if kind=='hair-lock':
                    from scripts.studio.geometry import lock_rows
                    center=lambda n:lock_rows(n,scene['canvas'])[0].spine
                else: center=lambda n:component_data(n,scene['canvas']).center
                before=center(scene['nodes'][0]);p=Path(directory)/'scene.json';write(p,scene)
                candidate=preview(scene,select(scene,ident,feature='object'),'left',.1,'make room on the right')
                after=center(candidate['scene']['nodes'][0])
                self.assertAlmostEqual(before[0]-after[0],64)
                self.assertAlmostEqual(before[1],after[1])
                self.assertEqual(candidate['scene']['nodes'][1],scene['nodes'][1])
                self.assertEqual(scene,old)
                accept(p,candidate);undo(p);self.assertEqual(read(p),old)

    def test_crescent_hole_reveals_sky_and_ridge_depth_really_occludes(self):
        scene=default_scene('landscape');scene['canvas']=[320,320]
        moon=default_scene('moon')['nodes'][0]
        moon.update(at={'anchor':'center','offset':[0,.14]},length=.5)
        scene['nodes'].append(moon)
        image=pixels(scene)
        without=copy.deepcopy(scene);without['nodes'].pop();background=pixels(without)
        # Unilluminated side inside the implied disc must reveal the gradient.
        self.assertTrue(np.array_equal(image[170,202],background[170,202]))
        changed=np.any(image!=background,axis=2)
        self.assertTrue(changed.any())
        foreground=copy.deepcopy(scene);foreground['nodes'][-1]['depth']=30
        front=pixels(foreground)
        self.assertGreater(np.count_nonzero(np.any(front!=background,axis=2)),np.count_nonzero(changed))
        reordered=copy.deepcopy(scene);reordered['nodes'].reverse()
        self.assertTrue(np.array_equal(image,pixels(reordered)))

    def test_sun_support_has_no_invisible_ray_gap_occluder(self):
        scene=default_scene('sun');scene['canvas']=[320,320]
        data=component_data(scene['nodes'][0],scene['canvas'])
        from shapely import Polygon
        shape=Polygon(data.outline)
        self.assertTrue(shape.is_valid)
        # Against a full background, force the exact visibility path with equal depth.
        # Every fully paper pixel through a crown gap must remain background-colored.
        scene['nodes'].insert(0,dict(id='sky',kind='sky',intent='uniform negative control sky',depth=0,
                                   palette={'top':'#234567','bottom':'#234567'},stars=0))
        exact=pixels(scene)
        scene['nodes'][1]['depth']=1
        ordered=pixels(scene)
        bg=np.array([0x23,0x45,0x67]);mask=np.all(ordered==bg,axis=2)
        self.assertTrue(np.all(exact[mask]==bg))

    def test_semantic_controls_are_scoped_and_background_move_is_explicitly_refused(self):
        scene=default_scene('landscape')
        sky=select(scene,'sky')
        day=parameter_preview(scene,sky,'style','day','use a clear daylight mood')['scene']
        self.assertNotEqual(drawing(scene),drawing(day))
        self.assertEqual(scene['nodes'][1],day['nodes'][1])
        with self.assertRaises(ValueError): parameter_preview(scene,sky,'fullness',.3,'wrong object')
        with self.assertRaisesRegex(ValueError,'horizon/relief'): preview(scene,sky,'left',.1,'move sky')
        for kind,key,value in [('moon','fullness',0),('sun','rays',2),('sky','stars',1.5),('hills','relief',float('nan'))]:
            bad=default_scene(kind);bad['nodes'][0][key]=value
            with self.assertRaises(ValueError): validate(bad)

    def test_cli_insertion_is_undoable_without_touching_original_scene(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'scene.json';base=default_scene('landscape');write(p,base)
            result=subprocess.run([sys.executable,'-m','scripts.studio','add',str(p),'--kind','moon'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(len(read(p)['nodes']),3)
            undo(p);self.assertEqual(fingerprint(read(p)),fingerprint(base))


if __name__=='__main__': unittest.main()
