"""Visible feature-local character intent without changing head construction."""
import copy
from io import BytesIO
import unittest

import numpy as np
from PIL import Image
import resvg_py

from scripts.studio.__main__ import default_scene
from scripts.studio.geometry import bounds
from scripts.studio.head import _sample_path,compile_recipe,head_data
from scripts.studio.model import parameter_preview,select,validate
from scripts.studio.render import drawing
from scripts.tests.test_studio_head_editing import pixels


class ExpressionControls(unittest.TestCase):
    def test_open_eye_smile_does_not_clip_away_the_pupil_centers(self):
        from shapely import Point,Polygon
        def centers_are_visible(parts):
            apertures={p['blob'].removesuffix('-sclera'):Polygon(p['poly']) for p in parts if p.get('blob','').endswith('-sclera')}
            return all(apertures[p['ellipse'].removesuffix('-pupil')].covers(Point(*p['at']))
                       for p in parts if p.get('ellipse','').endswith('-pupil'))
        for gaze in (-1,0,1):
            self.assertTrue(centers_are_visible(compile_recipe(expression='smile',gaze=gaze)['nodes']))
        # Negative control: the rejected, over-closed prototype hid the pupil center.
        from unittest.mock import patch
        import scripts.studio.head as head
        original=head.build_spec
        def overclosed(*args,**kwargs):
            spec=original(*args,**kwargs)
            for part in spec['draw']:
                if part.get('eye')=='eye-left': part['lower-lid']=-.42
            return spec
        with patch.object(head,'build_spec',side_effect=overclosed):
            self.assertFalse(centers_are_visible(compile_recipe(expression='smile')['nodes']))

    def test_zoom_margin_is_opaque_and_visibly_separate_from_document_paper(self):
        svg=drawing(default_scene('head'),viewbox=[620,0,80,80])
        image=np.asarray(Image.open(BytesIO(resvg_py.svg_to_bytes(svg_string=svg))).convert('RGBA'))
        self.assertTrue(np.all(image[:,:,3]==255))
        self.assertFalse(np.array_equal(image[10,10,:3],image[10,-10,:3]))

    def test_expression_changes_only_the_actual_selected_feature_guides(self):
        base=default_scene('head');before=pixels(base)
        original=head_data(base['nodes'][0],base['canvas'])
        for expression in ('neutral','smile','curious'):
            with self.subTest(expression=expression):
                selection=select(base,feature='expression')
                scene=parameter_preview(base,selection,'expression',expression,'give this character a distinct intention')['scene']
                data=head_data(scene['nodes'][0],scene['canvas'])
                after=pixels(scene);delta=np.any(before!=after,axis=2)
                self.assertTrue(delta.any())
                allowed=np.zeros(delta.shape,dtype=bool)
                for feature in (original.features['expression'],data.features['expression']):
                    for guide in feature['paths']:
                        x0,y0,x1,y1=bounds(_sample_path(guide['d']))
                        allowed[max(0,int(y0)-3):int(y1)+4,max(0,int(x0)-3):int(x1)+4]=True
                self.assertFalse(np.any(delta & ~allowed),'expression changed an unselected face/hair region')
                self.assertEqual(original.outline,data.outline)

    def test_gaze_moves_both_pupils_the_same_way_and_stays_in_the_eyelids(self):
        base=default_scene('head');before=pixels(base)
        default=compile_recipe()['nodes']
        pupils=lambda nodes:{p['ellipse']:p['at'][0] for p in nodes if p.get('ellipse','').endswith('-pupil')}
        old=pupils(default);self.assertEqual(len(old),2)
        x0,y0,x1,y1=head_data(base['nodes'][0],base['canvas']).features['eyes']['bounds']
        allowed=np.zeros(before.shape[:2],dtype=bool)
        allowed[int(y0)-2:int(y1)+3,int(x0)-2:int(x1)+3]=True
        for gaze in (-1,1):
            moved=pupils(compile_recipe(gaze=gaze)['nodes'])
            for sid in old: self.assertGreater((moved[sid]-old[sid])*gaze,0,sid)
            scene=parameter_preview(base,select(base,feature='eyes'),'gaze',gaze,'look towards the partner')['scene']
            delta=np.any(pixels(scene)!=before,axis=2)
            self.assertTrue(delta.any())
            self.assertFalse(np.any(delta & ~allowed))

    def test_default_is_unchanged_and_expression_controls_cannot_leak_to_other_features(self):
        base=default_scene('head');explicit=copy.deepcopy(base)
        explicit['nodes'][0].update(expression='gentle',gaze=0)
        self.assertTrue(np.array_equal(pixels(base),pixels(explicit)))
        with self.assertRaises(ValueError):
            parameter_preview(base,select(base,feature='hair'),'expression','curious','wrong feature')
        for key,value in (('expression','unimplemented'),('gaze',1.1)):
            bad=copy.deepcopy(base);bad['nodes'][0][key]=value
            with self.assertRaises(ValueError): validate(bad)


if __name__=='__main__': unittest.main()
