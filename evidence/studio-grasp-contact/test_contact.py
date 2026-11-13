import unittest,math
import numpy as np
from contact import PREVIOUS,tangent_step,surface_clearance,solve,bind_frame,joint_palmar_normals

class ContactMath(unittest.TestCase):
    def fixture(self,vertices):
        return dict(vertices=np.array(vertices,dtype=float),faces=np.array([[0,1,2]]),
            indices=np.zeros((3,4),dtype=int),weights=np.tile([1.,0,0,0],(3,1)))

    def rod(self,vertices):
        return dict(vertices=vertices,axis=np.array([1.,0,0]),forward=np.array([0.,1,0]),palmar=np.array([0.,0,1]),
            center=np.zeros(3),radius=1.,half_length=1.)

    def test_tangent_clearance_and_direction(self):
        p=np.array([0.,-3.]);end,direction,info=tangent_step(p,1.,4.)
        self.assertAlmostEqual(abs(p[0]*direction[1]-p[1]*direction[0]),1.)
        self.assertGreater(np.linalg.norm(end),1.)
        self.assertGreater(info['distance_to_contact'],0)
        self.assertAlmostEqual(np.linalg.norm(end-p),4.)

    def test_triangle_crossing_without_any_inside_vertex(self):
        d=self.fixture([[0,-2,-2],[0,2,-2],[0,0,2]])
        r=surface_clearance(d,self.rod(d['vertices']))
        self.assertEqual(r['skin_vertices_inside'],0)
        self.assertEqual(r['intersecting_triangles'],1)
        self.assertEqual(r['minimum_radial_clearance_in_slab'],-1.)

    def test_beyond_cap_cap_touch_and_side_clearance(self):
        for x in (2.,1.):
            d=self.fixture([[x,-2,-2],[x,2,-2],[x,0,2]])
            self.assertEqual(surface_clearance(d,self.rod(d['vertices']))['intersecting_triangles'],0)
        d=self.fixture([[0,2,0],[.5,2,.5],[-.5,2,.5]])
        self.assertAlmostEqual(surface_clearance(d,self.rod(d['vertices']))['minimum_radial_clearance_in_slab'],1.)

    def test_joint_roll_and_length_preservation(self):
        data=PREVIOUS['load']();palmar=joint_palmar_normals(data)
        for a,b in [(1,2),(2,3),(3,4),(6,7),(7,8),(8,9)]:
            f=bind_frame(data,a,b)
            self.assertTrue(np.allclose(f.T@f,np.eye(3),atol=1e-10))
            self.assertAlmostEqual(np.linalg.det(f),1.)
            self.assertGreater(np.dot(f[:,2],palmar[a]),.99)
        result=solve(data)
        for chain in [(1,2,3,4),(6,7,8,9),(11,12,13,14),(16,17,18,19),(21,22,23,24)]:
            for a,b in zip(chain,chain[1:]):
                self.assertAlmostEqual(np.linalg.norm(result['joints'][b]-result['joints'][a]),np.linalg.norm(data['bind'][b]-data['bind'][a]))
        self.assertEqual(result['diagnostic']['intersecting_triangles'],0)

if __name__=='__main__':unittest.main()
