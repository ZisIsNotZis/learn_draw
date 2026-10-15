from __future__ import annotations
import copy
import json
import math
from pathlib import Path
import pytest

SOURCE=Path(__file__).resolve().parents[1]/"source"
import importlib.util,sys
spec=importlib.util.spec_from_file_location("collar_wrap_build",SOURCE/"build_a.py")
build=importlib.util.module_from_spec(spec);sys.modules[spec.name]=build;spec.loader.exec_module(build)


def _collar_specs():
    params=json.loads((SOURCE/"semantic-parameters.json").read_text())
    parts=params["parts"];opening_record=parts["opening"];opening=opening_record["stations_xy"];result=[]
    for key in ("collar_left","collar_right"):
        spec=copy.deepcopy(parts[key])
        spec["authored_xy"]["Q"]=opening["Q"]
        spec["front_width"]=opening_record["collar_front_width"]
        spec["authored_input_xy"]={k:parts[key]["authored_xy"][k] for k in ("R","E","S")}
        result.append(spec)
    return params,tuple(result)


def test_wrap_strip_rejects_zero_front_width_from_old_shared_q_triangle():
    _,specs=_collar_specs()
    legacy=[copy.deepcopy(spec) for spec in specs]
    for spec in legacy: spec["front_width"]=0.0
    with pytest.raises(ValueError,match="positive"):
        build.fam.wrap_strips(tuple(legacy),("left","right"))


def test_generated_offsets_are_positive_finite_and_self_cross_guard_checks_samples():
    _,specs=_collar_specs()
    left,right=build.fam.wrap_strips(specs,("A-collar-left","A-collar-right"))
    for geometry in (left,right):
        assert tuple(key for key,_ in geometry.authored_inputs)==("R","E","S")
        stations=geometry.named_stations
        assert stations["front_width"]>0
        assert len(stations["width_samples"])>=100
        assert min(stations["width_samples"])>=1.5
        assert all(math.isfinite(v) for point in geometry.outline for v in point)
        outer=next(edge.points for edge in geometry.edges if edge.type=="trim")
        assert len(outer)>50 and outer[-1]==stations["Q_prime"]
        assert all(any(math.dist(point,vertex)<1e-8 for vertex in geometry.outline) for point in outer)
    with pytest.raises(ValueError,match="self-intersects"):
        build.fam._assert_simple_offset(((0,0),(2,2),(0,2),(2,0)),(2,2,2,2),1)


def test_wrap_strip_rejects_degenerate_shared_outward_normal_bisector():
    q=(0.0,0.0)
    left={"authored_xy":{"R":(-10.0,0.0),"S":(-7.0,3.0),"E":(-4.0,5.0),"Q":q},
          "inner_bend":0.0,"root_width":3.0,"front_width":2.0,"width_floor":0.5}
    right={"authored_xy":{"R":(10.0,0.0),"S":(7.0,-3.0),"E":(4.0,-5.0),"Q":q},
           "inner_bend":0.0,"root_width":3.0,"front_width":2.0,"width_floor":0.5}
    with pytest.raises(ValueError,match="degenerate shared bisector"):
        build.fam.wrap_strips((left,right),("left","right"))


def test_shared_inner_q_positive_outer_qprime_and_continuous_sweep():
    parts,_,_=build.build_scene();by={p.component.name:p for p in parts}
    left=by["A-collar-left"].geometry;right=by["A-collar-right"].geometry
    q=left.named_stations["Q"]
    assert q==right.named_stations["Q"]
    assert left.named_stations["inner"][-1]==q==right.named_stations["inner"][-1]
    ql,qr=left.named_stations["Q_prime"],right.named_stations["Q_prime"]
    assert math.dist(ql,qr)<1e-10 and math.dist(q,ql)>0
    assert math.dist(left.named_stations["outer"][-1],right.named_stations["outer"][-1])<1e-10
    assert math.dist(left.named_stations["outer_tangent"],tuple(-v for v in right.named_stations["outer_tangent"]))<1e-8


def test_both_collar_support_planes_match_complete_q_to_qprime_world_seam_and_preserve_transverse_gradient():
    parts,_,params=build.build_scene();by={p.component.name:p.component for p in parts}
    left,right=by["A-collar-left"],by["A-collar-right"]
    q=tuple(params["parts"]["opening"]["stations_xy"]["Q"])
    geometry_by={p.component.name:p.geometry for p in parts}
    q_prime=geometry_by["A-collar-left"].named_stations["Q_prime"]
    start,end=build.P(q),build.P(q_prime)
    tangent=(end.u-start.u,end.v-start.v);length=math.hypot(*tangent);tangent=(tangent[0]/length,tangent[1]/length)
    transverse=(-tangent[1],tangent[0])
    base_left=build.support("base-left",params["supports"]["collar_left"])
    base_right=build.support("base-right",params["supports"]["collar_right"])
    for actual,base in ((left.support,base_left),(right.support,base_right)):
        before=(base.u_axis[2],base.v_axis[2]);after=(actual.u_axis[2],actual.v_axis[2])
        assert abs((before[0]-after[0])*transverse[0]+(before[1]-after[1])*transverse[1])<1e-12
    for i in range(101):
        t=i/100
        local=build.Point(start.u+(end.u-start.u)*t,start.v+(end.v-start.v)*t)
        a=left.support.local_to_world(local);b=right.support.local_to_world(local)
        assert max(abs(a[k]-b[k]) for k in range(3))<=1e-8


def test_typed_generated_trim_uses_actual_depth_visibility_line_flow():
    parts,marks,_=build.build_scene();by={p.component.name:p.component for p in parts}
    collars={"A-collar-left","A-collar-right"}
    trim_marks=[mark for mark in marks if mark.owner in collars and "trim" in mark.name]
    assert len(trim_marks)==2
    components=tuple(part.component for part in parts);faces=build.component_faces(components,build.CAMERA)
    for mark in trim_marks:
        owner=by[mark.owner]
        assert len(mark.points)>50
        for a,b in zip(mark.points,mark.points[1:]):
            wa=build.CAMERA.project(owner.support.local_to_world(a));wb=build.CAMERA.project(owner.support.local_to_world(b))
            spans=build.visible_segment_spans(wa,wb,faces,owner.name)
            assert all(0<=lo<hi<=1 for lo,hi in spans)
        segments=build._segments_svg(mark,owner,faces)
        assert segments, f"{mark.owner}: generated trim must traverse real depth clipping"
    svg,_=build.render_svg()
    assert "A-collar-left-trim" in svg and "A-collar-right-trim" in svg
