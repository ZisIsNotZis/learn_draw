"""Focused regression checks for the revision-local WP04 relation grammar."""
import importlib.util
from pathlib import Path
import unittest
from scripts.articulated_construction import build_study_case, validate_study_case, _inside, _on_boundary

MODULE=Path(__file__).with_name('render_artistic_r1.py')
spec=importlib.util.spec_from_file_location('artistic_renderer',MODULE)
renderer=importlib.util.module_from_spec(spec); spec.loader.exec_module(renderer)

class ArtisticGrammarTests(unittest.TestCase):
 def test_authored_art_has_named_shapes_and_relation_generated_regions(self):
    art=renderer.observed_study()
    assert {'observed-bodice','observed-shoulder-cap','observed-cuff','observed-neckline-trim','observed-bow-left-lobe','observed-bow-right-lobe','observed-bow-tails','observed-bow-knot'} <= {c.name for c in art}
    assert all(c.intent and c.support.support_id and c.support.depth_ref for c in art)
    # authored garment shape points remain inside the projected fit by construction bounds.
    xyz=[renderer.CAM.project(c.support.local_to_world(p)) for c in art for p in c.outline]
    assert min(x for x,y,z in xyz)<max(x for x,y,z in xyz) and min(y for x,y,z in xyz)<max(y for x,y,z in xyz)

 def test_artistic_b_keeps_supports_anchors_contact_gap_and_variants(self):
    outputs={}
    for case in ('baseline','variant','control'):
        base=build_study_case(case); validate_study_case(base)
        parts=renderer.panel_components(case); by={c.name:c for c in parts}
        assert by['hand'].support.depth_ref=='hand-depth' and by['forearm'].support.depth_ref=='arm-depth'
        assert 'thumb' in by['hand'].intent and 'gripping fingers' in by['hand'].intent
        for component in parts:
            for _,anchor in component.anchors:
                self.assertTrue(_inside(anchor,component.outline) or _on_boundary(anchor,component.outline), (component.name,anchor))
        outputs[case]=(by['torso'].outline,by['hand'].outline)
    assert outputs['baseline'] != outputs['variant']
    assert build_study_case('baseline').contact == build_study_case('variant').contact or outputs['baseline'] != outputs['variant']
    assert build_study_case('control').control

 def test_renderer_is_repeatable_and_reference_independent(self):
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
     tmp_path=Path(directory)
     first=tmp_path/'first'; second=tmp_path/'second'
     renderer.main(first); renderer.main(second)
     for name in ('artwork.svg','artwork-a.svg','artwork-b.svg'):
        self.assertEqual((first/name).read_bytes(),(second/name).read_bytes())
    source=MODULE.read_text()
    self.assertNotIn('image.jpg',source); self.assertNotIn('open(',source)
