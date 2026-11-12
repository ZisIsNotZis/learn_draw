"""Nonoverlapping projected paint commutes; real depth crossings must retain clipping."""
import copy
import unittest
import numpy as np
from .test_studio_hand import pixels
from scripts.studio.__main__ import default_scene
from scripts.studio.render import global_depth_order


class NoncrossingLayers(unittest.TestCase):
    def test_disjoint_coplanar_fins_render_identically_when_the_depth_tie_is_broken(self):
        scene=default_scene('shape');scene['background']='#f6ecdf'
        body=scene['nodes'][0]
        body.update(id='body',length=.46,width=.5,rounding=.65,taper=.05,stroke=.012,palette={'fill':'#ead8b5','ink':'#76564a'})
        for name,sign in [('left-fin',-1),('right-fin',1)]:
            scene['nodes'].append(dict(id=name,kind='shape',intent='a red fin buried behind the hull',depth=-1,length=.22,width=.8,rounding=.03,taper=.9,angle=sign*18,stroke=0,palette={'fill':'#bc6150'},at={'anchor':'center','offset':[sign*.12,.16]}))
        separated=copy.deepcopy(scene);separated['nodes'][2]['depth']=-2
        self.assertTrue(np.array_equal(pixels(scene),pixels(separated)),'a depth tie between disjoint painted parts changed the artwork')
        scene['nodes'].reverse()
        self.assertTrue(np.array_equal(pixels(scene),pixels(separated)))

    def test_an_intervening_disjoint_object_cannot_hide_a_real_depth_crossing(self):
        scene=default_scene('shape');a=scene['nodes'][0]
        a.update(id='sloping',length=.5,width=.5,depth=0,depth_slope=2,stroke=0,palette={'fill':'#285b85'})
        b=copy.deepcopy(a);b.update(id='distant',length=.2,depth=-.5,depth_slope=0,at={'anchor':'upper_right'},palette={'fill':'#569c7a'})
        c=copy.deepcopy(a);c.update(id='front',depth=.5,depth_slope=0,palette={'fill':'#c46855'})
        scene['nodes']=[a,b,c]
        self.assertIsNone(global_depth_order(scene))
        image=pixels(scene)
        self.assertEqual(tuple(image[260,320,:3]),(196,104,85))
        self.assertEqual(tuple(image[450,320,:3]),(40,91,133))
