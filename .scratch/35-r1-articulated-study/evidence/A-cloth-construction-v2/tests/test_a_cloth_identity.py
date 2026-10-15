from __future__ import annotations
import ast
import importlib.util
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[5]
CANDIDATE=ROOT/".scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2"
SOURCE=CANDIDATE/"source"
SMOOTH=ROOT/".scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial"
for path in (ROOT,SMOOTH):
    if str(path) not in sys.path: sys.path.insert(0,str(path))
_spec=importlib.util.spec_from_file_location("cloth_build_test",SOURCE/"build_a.py")
build=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=build;_spec.loader.exec_module(build)
from scripts.articulated_construction import Point,component_faces
from scripts.articulated_line_visibility import visible_segment_spans
from scripts.vector_visibility import visible_regions
import pytest

@pytest.fixture(scope="module")
def scene(): return build.build_scene()

def _xy(point): return (point[0],point[1])
def _dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
def _cross(a,b,c): return (b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
def _point_segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
    if den==0:return _dist(p,a)
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return _dist(p,(a[0]+t*dx,a[1]+t*dy))

def _attach_error(parts):
    by={p.component.name:p.component for p in parts}
    errs=[]
    for c in by.values():
        own=dict(c.anchors)
        for target,own_name,target_name in c.attachments:
            other=by[target];a=c.support.local_to_world(own[own_name]);b=other.support.local_to_world(dict(other.anchors)[target_name])
            errs.append(max(abs(x-y) for x,y in zip(a,b)))
    return errs


def test_wedge_shared_opening_and_nonelliptic_fold_identity(scene):
    parts,_,p=scene;by={x.component.name:x for x in parts}
    left=by["A-collar-left"].geometry;right=by["A-collar-right"].geometry;skin=by["A-visible-neck-skin"].geometry;body=by["A-bodice-upper"].geometry
    Q=tuple(p["parts"]["opening"]["stations_xy"]["Q"])
    assert left.named_stations["Q"]==right.named_stations["Q"]==skin.named_stations["Q"]==Q
    assert body.named_stations["waist_center"] is not None
    assert any(e.type=="contact" and "trim" in e.intent for e in left.edges+right.edges)
    for g in (left,right):
        R,E,S=(g.named_stations[k] for k in ("R","E","S"))
        incoming=(S[0]-E[0],S[1]-E[1]);outgoing=(R[0]-S[0],R[1]-S[1])
        cosine=sum(incoming[i]*outgoing[i] for i in range(2))/(math.hypot(*incoming)*math.hypot(*outgoing))
        assert cosine < .90, "fold station must preserve a corner tangent change; a closed smooth ellipse cannot pass"
        assert g.family=="opening-fold-wedge"
    # Negative-space probes remain inside the skin field and outside each collar leaf and bodice.
    for probe in ((201,101),(198,110),(204,110)):
        assert fam_point(probe,skin.outline)
        assert not fam_point(probe,left.outline)
        assert not fam_point(probe,right.outline)
        assert not fam_point(probe,body.outline)
    assert min(y for _,y in skin.outline)<0, "skin continuation must leave the viewport, not form an in-frame rounded cap"


def fam_point(probe,polygon): return build.fam.point_in_polygon(probe,polygon)


def test_tilted_bodice_waist_attachment_and_crop_continuation(scene):
    parts,_,p=scene;by={x.component.name:x for x in parts}
    body=p["parts"]["bodice"];c0=body["authored_xy"]["C0"];cw=body["authored_xy"]["Cw"]
    dx,dy=cw[0]-c0[0],cw[1]-c0[1]
    assert dx<0 and dy>0 and -.35 < dx/dy < -.12
    assert _attach_error(parts) and max(_attach_error(parts))<1e-8
    upper=by["A-bodice-upper"].geometry;band=by["A-derived-waist-band"].geometry;continuation=by["A-bodice-continuation"].geometry
    assert _dist(upper.named_stations["waist_left"],band.named_stations["upper_left"])<1e-8
    assert _dist(upper.named_stations["waist_right"],band.named_stations["upper_right"])<1e-8
    assert _dist(band.named_stations["lower_left"],continuation.named_stations["upper_left"])<1e-8
    assert _dist(band.named_stations["lower_right"],continuation.named_stations["upper_right"])<1e-8
    assert continuation.named_stations["out_of_crop_closure_left"][1]>480
    assert continuation.named_stations["out_of_crop_closure_right"][1]>480
    assert max(y for _,y in upper.outline)<480, "upper body piece must stop at the shared band, not an in-frame closed bag bottom"
    assert _dist(tuple(p["parts"]["bodice"]["authored_xy"]["Eleft"]),upper.named_stations["upper_left"])<40


def test_puff_cap_fullness_and_shared_transverse_cuff_identity(scene):
    parts,_,_=scene;by={x.component.name:x for x in parts}
    sleeve=by["A-continuous-puff-sleeve"].geometry;cuff=by["A-transverse-cuff-band"].geometry
    p=sleeve.named_stations;S,C=p["S"],p["C"];e=p["axis"]
    assert _dist(p["C"],cuff.named_stations["C"])<1e-8
    radii=[]
    rule_spec=json.loads((SOURCE/"semantic-parameters.json").read_text())["parts"]["sleeve"]
    famspec=dict(rule_spec);famspec["authored_xy"]={"S":S,"C":C}
    for i in range(1,100):
        t=i/100
        center=build.fam.sleeve_center(famspec,t)
        lo,hi=build.fam.sleeve_section(famspec,t)
        radii.append((t,_dist(lo,hi)/2))
    peak=max(radii,key=lambda x:x[1])
    assert peak[1]>=max(rule_spec["shoulder_radius"],rule_spec["cuff_radius"])*1.08
    assert .15<=peak[0]<=.65
    n=(-e[1],e[0]);cuff_axis=_subxy(cuff.named_stations["lower_right"],cuff.named_stations["lower_left"])
    assert abs((cuff_axis[0]*e[0]+cuff_axis[1]*e[1])/(math.hypot(*cuff_axis)))<.15
    # Cap bends opposite the sleeve action direction; no cap-to-tube ink edge exists.
    cap=sleeve.edges[0].points
    cap_mid=cap[len(cap)//2]
    assert (cap_mid[0]-S[0])*e[0]+(cap_mid[1]-S[1])*e[1] < -20
    assert not any(e.type=="fold_edge" and "seam" in e.intent for e in sleeve.edges)
    assert cuff.family=="shared-transverse-short-cuff"


def _subxy(a,b):return (a[0]-b[0],a[1]-b[1])


def test_folded_loop_tail_and_independent_crop_bands(scene):
    parts,_,p=scene;by={x.component.name:x for x in parts}
    for name in ("A-bow-left-loop","A-bow-right-loop"):
        g=by[name].geometry
        assert g.named_stations["root_half_width"]/g.named_stations["free_half_width"]<=.30
        assert any(e.type=="fold_edge" and "return" in e.intent for e in g.edges)
        turns=[_cross(g.outline[i-1],g.outline[i],g.outline[(i+1)%len(g.outline)]) for i in range(len(g.outline))]
        assert min(turns)<0<max(turns), "a true gather/return fold has a concave turn; an ellipse is everywhere convex"
    tail=by["A-down-tail-continuation"].geometry
    assert _dist(tail.named_stations["P0"],tail.named_stations["P1"])>0
    tangent=tail.named_stations["root_tangent"]
    assert tangent[1]>.5
    dti=(157,246);centerline=tail.named_stations["centerline"]
    assert min(_point_segment_distance(dti,a,b) for a,b in zip(centerline,centerline[1:]))<18
    blue=by["A-anonymous-blue-band"]
    assert blue.component.attachments==()
    assert by["A-left-local-pink-band"].component.attachments==()
    assert blue.geometry.named_stations["entry"][0]<0 and blue.geometry.named_stations["exit"][0]<0
    assert max(x for x,y in blue.geometry.named_stations["centerline"])>35
    assert _dist(blue.geometry.named_stations["centerline"][len(blue.geometry.named_stations["centerline"])//2],(44,209))<35
    assert "leftward-tail-centerline" not in json.dumps(p["provenance"]["fit_allowed"])
    # Hair context is explicitly separate and remains at most four actual center stations per part.
    for key in ("hair_neck_curlband","hair_right_shoulder_sheet"):
        assert len(p["parts"][key]["authored_center_xy"])<=4
    assert p["provenance"]["visible_context"]["fit_whitelist_change"].startswith("none")


def test_actual_author_inputs_are_audited_not_component_anchor_metadata(scene):
    parts,marks,p=scene;counts={x.component.name:x.authored_count for x in parts}
    assert max(counts.values())<=4
    assert counts=={
        "A-collar-left":3,"A-collar-right":3,"A-visible-neck-skin":1,
        "A-bodice-upper":3,"A-derived-waist-band":0,"A-bodice-continuation":0,
        "A-continuous-puff-sleeve":1,"A-transverse-cuff-band":0,
        "A-bow-gather":1,"A-bow-left-loop":1,"A-bow-right-loop":1,
        "A-down-tail-continuation":0,"A-left-local-pink-band":3,
        "A-anonymous-blue-band":4,"A-neck-curlband":4,"A-right-shoulder-hair-sheet":4}
    assert all(x.authored_count==len(x.geometry.authored_inputs) for x in parts)
    direct_marks=[x for x in marks if x.name.startswith("A-bodice_fold") or x.name.startswith("A-sleeve_soft_fold")]
    assert direct_marks and max(len(x.points) for x in direct_marks)<=4
    assert counts["A-bodice-upper"]==3 and len(dict(next(x for x in parts if x.component.name=="A-bodice-upper").component.anchors))==2


def test_backend_uses_real_support_depth_and_semantic_edge_adapter(scene):
    parts,marks,_=scene;components=tuple(x.component for x in parts)
    faces=component_faces(components,build.CAMERA)
    assert len(faces)>500
    assert tuple(visible_regions(faces))
    assert len({name for _,_,name in faces})==len(components)
    assert max(_attach_error(parts))<1e-8
    hidden_or_split=False;checked=0
    for mark in marks:
        owner=next(x.component for x in parts if x.component.name==mark.owner)
        for a,b in zip(mark.points,mark.points[1:]):
            wa=build.CAMERA.project(owner.support.local_to_world(a));wb=build.CAMERA.project(owner.support.local_to_world(b))
            spans=visible_segment_spans(wa,wb,faces,owner.name)
            checked+=1
            assert all(0<=lo<hi<=1 for lo,hi in spans)
            if sum(hi-lo for lo,hi in spans)<.999: hidden_or_split=True
            if checked>=80:break
        if checked>=80:break
    assert checked>0 and hidden_or_split, "at least one selected semantic line must be clipped by computed scene depth"
    svg1,meta=build.render_svg();svg2,_=build.render_svg()
    assert svg1==svg2
    assert meta["edges"]>len(parts) and meta["projected_faces"]==len(faces)
    assert 'data-edge-type="closure"' not in svg1
    assert "edge is depth-clipped" in svg1
    assert "A-bodice-continuation" in svg1 and "closure lies below crop" not in svg1


def test_runtime_is_reference_absent_and_only_reads_semantic_parameters(monkeypatch):
    reads=[];original=Path.read_text
    def record(path,*args,**kwargs):
        reads.append(path.resolve())
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,"read_text",record)
    build.build_scene()
    assert reads==[(SOURCE/"semantic-parameters.json").resolve()]
    source=(SOURCE/"build_a.py").read_text()
    assert "image.jpg" not in source and "pristine-fullcrop.png" not in source
    assert "trace" not in source.lower() and "landmark" not in source.lower()
    tree=ast.parse(source)
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="main")
    options=[n.value for n in ast.walk(main) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
    assert "--out" in options and "--ref" not in options
    assert "crop_entry" not in source
