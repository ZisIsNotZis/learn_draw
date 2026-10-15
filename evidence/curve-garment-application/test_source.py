import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import ANCHORS, build, derive_controls
from scripts.articulated_construction import triangulate_polygon

class GarmentApplicationTests(unittest.TestCase):
    def test_simple_contour_and_budget(self):
        cloth,_=build()
        self.assertLessEqual(len(ANCHORS),4)
        self.assertGreater(len(triangulate_polygon(cloth.outline)),0)
    def test_landmark_connections(self):
        _,lines=build()
        self.assertEqual(lines[0][1],ANCHORS['neckline'])
        self.assertEqual(lines[0][2],ANCHORS['sleeve_cap'])
        self.assertEqual(lines[1][2],ANCHORS['waist'])
    def test_support_world_depth_and_reference_absent(self):
        cloth,_=build()
        self.assertEqual(cloth.support.depth_ref,'torso-front-depth')
        self.assertTrue(all(abs(p[2]-.12)<1e-9 for p in cloth.world_outline()))
        self.assertNotIn('image.jpg',Path(__file__).with_name('source.py').read_text())
    def test_reproducible(self):
        self.assertEqual(derive_controls(),derive_controls())
if __name__=='__main__': unittest.main()
