import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).with_name('study.py')
spec=importlib.util.spec_from_file_location('study',p); study=importlib.util.module_from_spec(spec); spec.loader.exec_module(study)

class SmoothStudyTests(unittest.TestCase):
    def test_closed_curve_and_shared_anchors(self):
        pts=study.outline(study.CASES['narrow']); d=study.smooth_path(pts)
        self.assertEqual(d.count('C '),len(pts)); self.assertTrue(d.endswith('Z'))
        self.assertIn(f'{pts[0][0]:.2f},{pts[0][1]:.2f}',d)
    def test_semantic_width_changes_generated_shape(self):
        a,b=study.CASES['narrow'],study.CASES['wide']
        self.assertNotEqual(study.smooth_path(study.outline(a)),study.smooth_path(study.outline(b)))
        self.assertLessEqual(len(study.outline(a)),8)  # derived outline, not reference samples
    def test_curve_has_finite_controls(self):
        import re, math
        vals=[float(x) for x in re.findall(r'[-+]?\d+\.\d+',study.smooth_path(study.outline(study.CASES['narrow'])))]
        self.assertTrue(all(math.isfinite(x) for x in vals))

if __name__=='__main__': unittest.main()
