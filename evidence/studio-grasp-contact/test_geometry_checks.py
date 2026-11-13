import unittest
import numpy as np
from geometry_checks import transverse_crossing,skin_crossings

class Crossings(unittest.TestCase):
    def setUp(self):
        self.a=np.array([[-1.,-1,0],[1,-1,0],[0,1,0]])
        self.b=np.array([[0.,-.5,-1],[0,-.5,1],[0,.7,0]])

    def test_transverse_and_separated(self):
        self.assertTrue(transverse_crossing(self.a,self.b))
        self.assertFalse(transverse_crossing(self.a,self.b+[3,0,0]))
        self.assertFalse(transverse_crossing(self.a,self.b+[0,3,0]))

    def test_grazing_and_coplanar_are_not_strict_crossings(self):
        self.assertFalse(transverse_crossing(self.a,self.a*.5))
        self.assertFalse(transverse_crossing(self.a,self.b+[0,0,1]))

    def test_topological_neighbors_ignored_but_disconnected_crossing_found(self):
        v=np.vstack([self.a,self.b]);d=dict(vertices=v,faces=np.array([[0,1,2],[3,4,5]]))
        self.assertEqual(skin_crossings(d,v)['transverse_pairs'],[(0,1)])
        d=dict(vertices=self.a,faces=np.array([[0,1,2],[2,1,0]]))
        self.assertEqual(skin_crossings(d,self.a)['transverse_pairs'],[])

if __name__=='__main__':unittest.main()
