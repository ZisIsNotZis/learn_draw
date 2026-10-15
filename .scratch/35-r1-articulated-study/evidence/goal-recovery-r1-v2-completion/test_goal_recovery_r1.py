from __future__ import annotations
import builtins
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import pytest

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
if str(REPO) not in sys.path: sys.path.insert(0,str(REPO))
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

import r1_scene
import spatial_adapter as adapter
from scripts.articulated_construction import Camera,Point,SupportFrame
from r1_scene import build_a_study,build_b_study
from run_r1 import build_case_svg,write_case


def test_goal_recovery_sources_only_compact_named_shapes_and_lines():
    studies=[build_a_study(),*(build_b_study(name)[0] for name in ("baseline","variant","control"))]
    required_a={"A-visible-neck-skin","A-bodice","A-right-sleeve-cap","A-right-sleeve-tube","A-right-cuff",
                "A-collar-left-leaf","A-collar-right-leaf","A-bow-left-lobe","A-bow-right-lobe",
                "A-bow-tail-left","A-bow-tail-right","A-bow-knot"}
    assert required_a <= {shape.name for shape in studies[0].shapes}
    for study in studies:
        assert study.shapes and all(shape.name and shape.intent and shape.family for shape in study.shapes)
        assert all(shape.support.support_id and shape.support.depth_ref for shape in study.shapes)
        assert all(1 <= len(shape.authored_anchors) <= 4 for shape in study.shapes)
        assert all(line.name and line.intent and len(line.authored_anchors) <= 4 for line in study.lines)
        assert all(line.owner in {shape.name for shape in study.shapes} for line in study.lines)
    # Families must materialize geometry from their compact semantic inputs, not pass those inputs through as frozen output.
    assert all(len(shape.controls) >= len(shape.authored_anchors) for study in studies for shape in study.shapes)
    assert all(any(a != b for a,b in zip(shape.controls,shape.authored_anchors))
               for study in studies for shape in study.shapes if shape.family not in {"elliptic_fruit","dish_rim","head_mass","neck_oval","leaf_ovoid","gathered_knot"})


def test_goal_recovery_b_support_contacts_variation_and_near_miss_are_scene_specific():
    cases={name:r1_scene._b_case(name) for name in ("baseline","variant","control")}
    for name,(shapes,lines,evidence) in cases.items():
        assert len({shape.name for shape in shapes})==len(shapes)
        assert all(shape.support.support_id and shape.support.depth_ref for shape in shapes)
        assert evidence["collision_check"]["scope"].startswith("Actual case component footprints/supports")
        assert all(contact["world_equality"] and not contact["projected_footprints_overlap"]
                   for contact in evidence["collision_check"]["declared_touches"])
    for name,(shapes,lines,_evidence) in cases.items():
        repeated_shapes,repeated_lines,_=r1_scene._b_case(name)
        assert [(shape.name,shape.controls,shape.support) for shape in shapes]==[
            (shape.name,shape.controls,shape.support) for shape in repeated_shapes]
        assert [(line.name,line.points,line.owner) for line in lines]==[
            (line.name,line.points,line.owner) for line in repeated_lines]
    base=cases["baseline"][2]; variant=cases["variant"][2]; control=cases["control"][2]
    assert base["dish_width_ratio"]==1.0 and variant["dish_width_ratio"]==1.12
    assert base["dish_center"] != variant["dish_center"]
    assert control["collision_check"]["declared_touches"]==[]
    assert "0.34 scene units" in control["control"]
    assert len(base["collision_check"]["declared_touches"])==1
    assert len(base["collision_check"]["declared_touches"][0]["points"])==3
    assert base["collision_check"]["declared_touches"][0]["parts"]==["baseline-dish-wall","baseline-hand-support"]
    assert "broad palm-foot edge" in base["successful_contact_world"]


def test_teacher_crop_is_registered_and_runtime_source_has_no_reference_path():
    observations=json.loads((ROOT/"teacher-observations.json").read_text())
    assert observations["source_sha256"]=="322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb"
    assert observations["registered_crop_source_xyxy"]==[500,320,900,800]
    assert observations["crop_dimensions"]==[400,480]
    assert observations["mapping"]=="crop (x,y) maps to source (500+x,320+y); no resize/stretch"
    crop=ROOT/"teacher-crop-registered.png"
    assert hashlib.sha256(crop.read_bytes()).hexdigest()==observations["evidence_files"][crop.name]
    assert set(observations["regions"])=={"bodice-and-shoulder","right-sleeve-cap","right-cuff","visible-neck-skin","layered-collar","bow-and-tails"}
    for region in observations["regions"].values():
        assert region["interpretation_limit"].startswith("rough teacher viewing window")
    runtime="\n".join((ROOT/name).read_text() for name in ("r1_scene.py","spatial_adapter.py","run_r1.py"))
    assert "image.jpg" not in runtime and "teacher-crop" not in runtime and "teacher-observations" not in runtime


def test_guarded_spatial_adapter_consumes_same_sample_for_fill_and_visible_line(monkeypatch):
    sampled=[]; projected=[]; visibility=[]
    original_sample=adapter.sample_closed_curve
    original_faces=adapter.component_faces
    original_regions=adapter.visible_regions
    original_segments=adapter.visible_segment_spans
    def sample(points,**kwargs):
        value=original_sample(points,**kwargs);sampled.append(value);return value
    def faces(parts,camera):
        result=original_faces(parts,camera);projected.append((parts,result));return result
    def regions(value):
        result=tuple(original_regions(value));visibility.append((value,result));return result
    def segments(*args,**kwargs):
        result=original_segments(*args,**kwargs);visibility.append((args[2],result));return result
    monkeypatch.setattr(adapter,"sample_closed_curve",sample)
    monkeypatch.setattr(adapter,"component_faces",faces)
    monkeypatch.setattr(adapter,"visible_regions",regions)
    monkeypatch.setattr(adapter,"visible_segment_spans",segments)
    subject=SupportFrame("fixture-subject","fixture-subject-depth")
    foreground=SupportFrame("fixture-front","fixture-front-depth",origin=(0,0,.5))
    controls=(Point(-1,-1),Point(1,-1),Point(1,1),Point(-1,1))
    front=adapter.build_visible_smooth_component((Point(-.4,-.4),Point(.4,-.4),Point(.4,.4),Point(-.4,.4)),
        "fixture-occluder",foreground,Camera(),(),intent="intentional foreground patch",fill="#b07050")
    result=adapter.build_visible_smooth_component(controls,"fixture-subject",subject,Camera(),(front.component,),
        intent="checked subject panel",fill="#8090a0")
    assert result.component.outline is result.validated_sampled_contour
    assert result.projected_faces and result.visible_fill_regions and result.authored_boundary_spans
    assert any(value is result.projected_faces for value,_regions_out in visibility)
    assert projected and sampled and len(visibility)>2
    line=adapter.project_visible_semantic_path((Point(-.8,0),Point(.8,0)),result.component,Camera(),
                                               (result.component,front.component))
    assert line and visibility
    with pytest.raises(ValueError,match="self-intersects|degenerate area"):
        adapter.build_visible_smooth_component((Point(-1,-1),Point(1,1),Point(-1,1),Point(1,-1)),
            "invalid-fixture",subject,Camera(),(),intent="invalid adversarial contour",fill="#ffffff")


def test_complete_a_svg_uses_guarded_components_and_reference_absent_reproduces(monkeypatch,tmp_path):
    observed=[]
    original=r1_scene.build_visible_smooth_component
    def record(*args,**kwargs):
        result=original(*args,**kwargs);observed.append((args[1],result.component.outline,result.visible_fill_regions));return result
    monkeypatch.setattr(r1_scene,"build_visible_smooth_component",record)
    original_open=builtins.open
    def guarded_open(file,*args,**kwargs):
        if Path(file).name=="image.jpg": raise AssertionError("renderer received reference image")
        return original_open(file,*args,**kwargs)
    monkeypatch.setattr(builtins,"open",guarded_open)
    first=write_case("A",tmp_path/"one");second=write_case("A",tmp_path/"two")
    assert hashlib.sha256(first.read_bytes()).digest()==hashlib.sha256(second.read_bytes()).digest()
    svg=first.read_text()
    assert "A-bodice" in svg and "A-right-sleeve-cap" in svg and "A-right-sleeve-tube" in svg
    assert "A-visible-neck-skin" in svg and "A-collar-left-leaf" in svg and "A-collar-right-leaf" in svg
    assert "A-bow-left-lobe" in svg and "A-bow-right-lobe" in svg and "A-bow-knot" in svg
    expected=len(build_a_study().shapes)
    assert len({name for name,_contour,_fills in observed})==expected
    assert all(contour and fills for _name,contour,fills in observed)


def test_complete_b_baseline_svg_emits_supported_palm_and_depth_visible_prop():
    svg=build_case_svg("baseline")
    for token in ("baseline-hand-support","baseline-dish-wall","baseline-dish-rim","baseline-fruit",
                  "baseline-finger-web-1","baseline-finger-web-2","baseline-thumb-fold",
                  "geometry-visible semantic component boundary"):
        assert token in svg
    assert "visible semantic component boundary" in svg
    assert "image.jpg" not in svg
    assert "&#xB7;" in svg and "Â" not in svg and "â€”" not in svg
    control=build_case_svg("control")
    assert "&#x2014;" in control and "Â" not in control and "â€”" not in control
    repeated=build_case_svg("baseline")
    assert hashlib.sha256(svg.encode()).digest()==hashlib.sha256(repeated.encode()).digest()


def test_all_b_case_captions_round_trip_through_utf8_svg_numeric_references():
    expected={
        "baseline":("SUPPORT · chest level","bent arm · open palm supports dish · thumb braces rim"),
        "variant":("VARIATION · lifted + broader dish","bent arm · open palm supports dish · thumb braces rim"),
        "control":("CONTROL — near miss","dish displaced; hand remains still"),
    }
    for case,(title,caption) in expected.items():
        svg=build_case_svg(case)
        assert svg.isascii()
        assert "Â" not in svg and "â€”" not in svg
        labels=[node.text for node in ET.fromstring(svg).iter()
                if node.tag.endswith("text")]
        assert labels==[title,caption]


def test_actual_a_b_generated_bounds_and_line_owners_fit_registered_views():
    for study in (build_a_study(),build_b_study("baseline")[0],build_b_study("variant")[0],build_b_study("control")[0]):
        for shape in study.shapes:
            contour=adapter.sample_closed_curve(shape.controls,steps_per_segment=4)
            points=[study.camera.project(shape.support.local_to_world(point)) for point in contour]
            screen=[(study.offset_x+study.scale*point[0],study.offset_y-study.scale*point[1]) for point in points]
            assert min(x for x,_ in screen)>=0 and max(x for x,_ in screen)<=study.width,shape.name
            assert min(y for _,y in screen)>=0 and max(y for _,y in screen)<=study.height,shape.name
        support_by_name={shape.name:shape.support for shape in study.shapes}
        for line in study.lines:
            projected=[study.camera.project(support_by_name[line.owner].local_to_world(point))
                       for point in line.points]
            screen=[(study.offset_x+study.scale*p[0],study.offset_y-study.scale*p[1]) for p in projected]
            assert min(x for x,_ in screen)>=0 and max(x for x,_ in screen)<=study.width,line.name
            assert min(y for _,y in screen)>=0 and max(y for _,y in screen)<=study.height,line.name
