"""An open hand is useful only if its visible tip edits preserve the rest of the rig."""
import copy
from io import BytesIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
import resvg_py
from shapely import Polygon,box

from scripts.studio.__main__ import default_scene
from scripts.studio.components import depth_bounds
from scripts.studio.hand import DIGITS,GEOMETRY_GRID,hand_data,transforms
from scripts.studio.model import accept,fingerprint,parameter_preview,preview,read,select,undo,validate,write
from scripts.studio.render import bundle,drawing,global_depth_order


def pixels(scene):
    return np.asarray(Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=drawing(scene)))).convert('RGBA'))


class OpenHand(unittest.TestCase):
    def test_hand_compiles_without_a_browser_or_reference_in_a_fresh_directory(self):
        project=Path(__file__).resolve().parents[2]
        code="""import sys
sys.path[:0]=[sys.argv[1],sys.argv[1]+'/scripts']
import renderer
from PIL import Image
import cv2
def forbidden(*args,**kwargs):
    raise RuntimeError('hand geometry attempted browser or image input')
renderer.chrome_path=forbidden
Image.open=forbidden
cv2.imread=forbidden
from scripts.studio.__main__ import default_scene
from scripts.studio.render import drawing
assert '--silhouette' in drawing(default_scene('hand'))
"""
        with tempfile.TemporaryDirectory() as directory:
            result=subprocess.run([sys.executable,'-c',code,str(project)],cwd=directory,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_multiple_hands_keep_their_own_clip_ids_and_visible_colours(self):
        scene=default_scene('hand')
        scene['nodes'][0].update(length=.42,depth=0,at={'anchor':'center','offset':[-.23,0]})
        other=copy.deepcopy(scene['nodes'][0])
        other.update(id='other-hand',depth=1,handedness='left',at={'anchor':'center','offset':[.23,0]},palette={'skin':'#9b674c'})
        scene['nodes'].append(other)
        svg=ET.fromstring(drawing(scene));ids=[el.get('id') for el in svg.iter() if el.get('id')]
        self.assertEqual(len(ids),len(set(ids)))
        image=pixels(scene)
        for node,colour in zip(scene['nodes'],((241,209,185),(155,103,76))):
            project,_inverse,_unit,_center=transforms(node,scene['canvas'])
            x,y=project((0,.40))
            self.assertEqual(tuple(image[int(y),int(x),:3]),colour)
        scene['nodes'].reverse()
        self.assertTrue(np.array_equal(image,pixels(scene)))

    def test_connected_five_digit_default_and_mirrored_handles(self):
        scene=default_scene('hand');validate(scene)
        right=hand_data(scene['nodes'][0],scene['canvas'])
        self.assertEqual(set(right.digits),set(DIGITS))
        self.assertTrue(Polygon(right.outline).is_valid)
        self.assertFalse(Polygon(right.outline).interiors)
        self.assertEqual(len({tuple(d['points'][0]) for d in right.digits.values()}),5)
        mirrored=copy.deepcopy(scene['nodes'][0]);mirrored['handedness']='left'
        left=hand_data(mirrored,scene['canvas'])
        for name in DIGITS:
            a,b=right.features[name]['focus'],left.features[name]['focus']
            self.assertAlmostEqual(a[0]+b[0],640)
            self.assertAlmostEqual(a[1],b[1])

    def test_screen_tip_target_is_exact_under_mirror_tilt_and_anisotropic_width(self):
        for handedness in ('right','left'):
            scene=default_scene('hand');scene['canvas']=[960,640]
            scene['nodes'][0].update(handedness=handedness,angle=33,width=1.15)
            original=copy.deepcopy(scene)
            for digit,direction in (('index','left'),('thumb','up')):
                with self.subTest(handedness=handedness,digit=digit):
                    before=hand_data(scene['nodes'][0],scene['canvas'])
                    selection=select(scene,feature=digit)
                    candidate=preview(scene,selection,direction,.02,'ease this tip while keeping the knuckle attached')
                    after=hand_data(candidate['scene']['nodes'][0],scene['canvas'])
                    a,b=before.features[digit],after.features[digit]
                    dx,dy=(-.02*a['nominal_span'],0) if direction=='left' else (0,-.02*a['nominal_span'])
                    self.assertAlmostEqual(b['focus'][0]-a['focus'][0],dx,places=8)
                    self.assertAlmostEqual(b['focus'][1]-a['focus'][1],dy,places=8)
                    self.assertEqual(a['locks'],b['locks'])
                    for name in DIGITS:
                        if name!=digit: self.assertEqual(before.features[name],after.features[name])
            self.assertEqual(scene,original)

    def test_tip_edit_is_visible_and_other_contours_stay_within_construction_precision(self):
        scene=default_scene('hand');data=hand_data(scene['nodes'][0],scene['canvas'])
        candidate=preview(scene,select(scene,feature='index'),'left',.04,'open the index spacing slightly')['scene']
        new=hand_data(candidate['nodes'][0],scene['canvas'])
        delta=np.any(pixels(scene)!=pixels(candidate),axis=2)
        self.assertTrue(delta.any())
        a,b=data.features['index']['bounds'],new.features['index']['bounds']
        x0,y0=min(a[0],b[0]),min(a[1],b[1]);x1,y1=max(a[2],b[2]),max(a[3],b[3])
        allowed=np.zeros(delta.shape,dtype=bool)
        allowed[int(y0)-4:int(y1)+5,int(x0)-4:int(x1)+5]=True
        self.assertTrue(np.any(delta & allowed),'the requested tip edit did not land')
        def painted_shape(data):
            root=ET.fromstring('<svg>'+data.svg+'</svg>')
            outline=next(el for el in root if el.get('id','').endswith('--silhouette'))
            tokens=outline.get('d').replace('M','').replace('L','').replace('Z','').split()
            return Polygon([tuple(map(float,token.split(','))) for token in tokens])
        region=box(x0-4,y0-4,x1+4,y1+4)
        old_outside=painted_shape(data).difference(region)
        new_outside=painted_shape(new).difference(region)
        _project,_inverse,unit,_center=transforms(scene['nodes'][0],scene['canvas'])
        tolerance=2*GEOMETRY_GRID*unit+.0001  # boolean grid + serialized coordinate rounding
        self.assertTrue(old_outside.buffer(tolerance).covers(new_outside))
        self.assertTrue(new_outside.buffer(tolerance).covers(old_outside))

    def test_scoped_length_and_tip_edits_accept_and_undo_exactly(self):
        base=default_scene('hand')
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'working.json';write(p,base)
            first=parameter_preview(base,select(base,feature='ring'),'finger_length',.94,'relax the ring finger reach')
            accept(p,first)
            second=preview(read(p),select(read(p),feature='index'),'left',.03,'ease the index outwards')
            accept(p,second);undo(p)
            self.assertEqual(read(p),first['scene'])
            undo(p);self.assertEqual(read(p),base)
        with self.assertRaises(ValueError):
            parameter_preview(base,select(base,feature='index'),'skin_color','#c99170','wrong selection')

    def test_invalid_poses_are_refused_before_merging_away_a_finger(self):
        bad=default_scene('hand')
        bad['nodes'][0].update(spread=.25,digits={'index':{'lean':12},'middle':{'lean':-12}})
        with self.assertRaisesRegex(ValueError,'overlap'):
            validate(bad)
        base=default_scene('hand')
        with self.assertRaises(ValueError):
            preview(base,select(base,feature='index'),'right',1,'an unsupported cross-hand movement')
        for controls in ({'unknown':{}},{'thumb':{'length':float('nan')}},{'index':{'lean':True}}):
            bad=copy.deepcopy(base);bad['nodes'][0]['digits']=controls
            with self.assertRaises(ValueError): validate(bad)

    def test_foreground_insertion_has_a_strict_depth_order_and_is_undoable(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'working.json';base=default_scene('head')
            base['nodes'][0]['depth_slope']=.4;write(p,base)
            result=subprocess.run([sys.executable,'-m','scripts.studio','add',str(p),'--kind','hand'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            scene=read(p)
            self.assertGreater(depth_bounds(scene['nodes'][1],scene['canvas'])[0],depth_bounds(scene['nodes'][0],scene['canvas'])[1])
            self.assertEqual([n['kind'] for n in global_depth_order(scene)],['head','hand'])
            undo(p);self.assertEqual(read(p),base)

    def test_a_failed_new_request_cannot_leave_an_old_candidate_acceptable(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'working.json';base=default_scene('hand');write(p,base)
            view=root/'view';bundle(base,view,select(base,feature='index'),png=False)
            target=root/'try'
            args=[sys.executable,'-m','scripts.studio','preview',str(p),'--selection',str(view/'selection.json'),
                  '--move','left','--amount','.02','--reason','ease this finger','--outdir',str(target),'--svg-only']
            good=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(good.returncode,0,good.stderr)
            args[args.index('--amount')+1]='2'
            bad=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(bad.returncode,2)
            with self.assertRaisesRegex(ValueError,'not completed'):
                accept(p,read(target/'candidate.json'))
            self.assertEqual(fingerprint(read(p)),fingerprint(base))
            self.assertEqual(read(target/'report.json')['images'],[])


if __name__=='__main__': unittest.main()
