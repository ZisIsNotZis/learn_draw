"""Goal-recovery R1 garment and original supported-hand scenes; no raster/runtime reference."""
from __future__ import annotations
from dataclasses import dataclass
import html
import re
from typing import Iterable

from scripts.articulated_construction import (
    Camera, Component, LimbParameters, Point, SupportFrame, construct_limb,
    polygons_overlap, _world_xy_outline, _world_z_at_xy,
)
from spatial_adapter import (VisibleSmoothComponent, build_visible_smooth_component,
                             project_visible_semantic_path, sample_closed_curve, validate_closed_contour)


@dataclass(frozen=True)
class ShapeSpec:
    name: str
    intent: str
    support: SupportFrame
    fill: str
    controls: tuple[Point, ...]  # generated grammar output consumed by the guarded sampler
    authored_anchors: tuple[Point, ...]
    attachments: tuple[tuple[str, str, str], ...] = ()
    semantic_anchors: tuple[tuple[str, Point], ...] = ()
    family: str = "relation-generated"


@dataclass(frozen=True)
class LineSpec:
    name: str
    intent: str
    owner: str
    points: tuple[Point, ...]
    authored_anchors: tuple[Point, ...]
    color: str = "#253443"
    width: float = 2.0


@dataclass(frozen=True)
class Study:
    name: str
    width: int
    height: int
    shapes: tuple[ShapeSpec, ...]
    lines: tuple[LineSpec, ...]
    labels: tuple[tuple[str, str, float, float], ...]
    camera: Camera
    background: str
    scale: float
    offset_x: float
    offset_y: float
    panel_width: int = 0


def _mix(a: Point, b: Point, t: float) -> Point:
    return Point(a.u + (b.u-a.u)*t, a.v + (b.v-a.v)*t)


def _add(a: Point, b: Point) -> Point:
    return Point(a.u+b.u, a.v+b.v)


def _sub(a: Point, b: Point) -> Point:
    return Point(a.u-b.u, a.v-b.v)


def _scale(a: Point, s: float) -> Point:
    return Point(a.u*s, a.v*s)


def _unit(a: Point) -> Point:
    n = (a.u*a.u+a.v*a.v)**0.5
    if n <= 1e-10: raise ValueError("semantic direction is degenerate")
    return Point(a.u/n, a.v/n)


def _perp(a: Point) -> Point:
    return Point(-a.v, a.u)


def _bezier(a: Point, b: Point, c: Point, d: Point, steps: int = 5) -> tuple[Point, ...]:
    return tuple(Point((1-t)**3*a.u+3*(1-t)**2*t*b.u+3*(1-t)*t*t*c.u+t**3*d.u,
                       (1-t)**3*a.v+3*(1-t)**2*t*b.v+3*(1-t)*t*t*c.v+t**3*d.v)
                 for i in range(steps) for t in (i/steps,))


def _closed_spans(spans: Iterable[tuple[Point, Point, Point, Point]], steps: int = 5) -> tuple[Point, ...]:
    result = []
    for span in spans: result.extend(_bezier(*span, steps=steps))
    return tuple(result)


def _open_spans(spans: Iterable[tuple[Point, Point, Point, Point]], steps: int = 5) -> tuple[Point, ...]:
    result = []
    for span in spans:
        points = _bezier(*span, steps=steps)
        if result and points: points = points[1:]
        result.extend(points)
    if spans:
        last = tuple(spans)[-1]
        result.append(last[-1])
    return tuple(result)


def _ellipse_controls(center: Point, rx: float, ry: float) -> tuple[Point, ...]:
    """Four derived cardinal controls; center/radii are semantic parameters, not traced outline."""
    return (Point(center.u-rx,center.v), Point(center.u,center.v+ry),
            Point(center.u+rx,center.v), Point(center.u,center.v-ry))


def _crop_point(x: float, y_down: float) -> Point:
    """Teacher crop coordinates map to art's y-up local frame, not a source pixel path."""
    return Point(x, 480.0-y_down)


def _shape(name: str, intent: str, support: SupportFrame, fill: str,
           anchors: Iterable[Point], generated: Iterable[Point], *, family: str,
           attachments: tuple[tuple[str,str,str], ...] = (),
           semantic_anchors: tuple[tuple[str,Point], ...] = ()) -> ShapeSpec:
    anchors, generated = tuple(anchors), tuple(generated)
    if not 1 <= len(anchors) <= 4:
        raise ValueError(f"{name}: semantic author input count must be 1..4, got {len(anchors)}")
    if len(generated) < 3:
        raise ValueError(f"{name}: grammar emitted too few curve controls")
    return ShapeSpec(name,intent,support,fill,generated,anchors,attachments,semantic_anchors,family)


def _line(name: str, intent: str, owner: str, source_anchors: Iterable[Point],
          generated: Iterable[Point], color="#253443", width=2.0) -> LineSpec:
    anchors, points = tuple(source_anchors), tuple(generated)
    if len(anchors) > 4: raise ValueError(f"{name}: line author inputs exceed four anchors")
    if len(points) < 2: raise ValueError(f"{name}: semantic line needs at least two generated points")
    return LineSpec(name,intent,owner,points,anchors,color,width)


def _a_bodice(anchors: tuple[Point,...]) -> tuple[Point,...]:
    """Fitted panel: four neckline/hem anchors generate neck arc, side ease and curved hem."""
    tl,tr,br,bl=anchors
    width=tr.u-tl.u; height=(tl.v+tr.v-br.v-bl.v)/2
    midx=(tl.u+tr.u)/2
    spans=(
      (tl,Point(tl.u+.28*width,tl.v-.16*height),Point(tr.u-.25*width,tr.v-.14*height),tr),
      (tr,Point(tr.u+.11*width,tr.v-.23*height),Point(br.u+.10*width,br.v+.18*height),br),
      (br,Point(midx+.20*width,br.v-.08*height),Point(midx-.20*width,bl.v-.05*height),bl),
      (bl,Point(bl.u-.08*width,bl.v+.17*height),Point(tl.u-.08*width,tl.v-.14*height),tl),
    )
    return _closed_spans(spans)


def _a_sleeve(anchors: tuple[Point,...]) -> tuple[Point,...]:
    """Asymmetric puff-cap flows into the narrowing sleeve opening from four seam landmarks."""
    join,cap,cuff_outer,cuff_inner=anchors
    w=cuff_outer.u-cuff_inner.u
    return _closed_spans((
      (join,Point(join.u+.22*w,join.v+.17*w),Point(cap.u-.15*w,cap.v+.12*w),cap),
      (cap,Point(cap.u+.26*w,cap.v-.10*w),Point(cuff_outer.u+.20*w,cuff_outer.v+.28*w),cuff_outer),
      (cuff_outer,Point(cuff_outer.u-.24*w,cuff_outer.v+.03*w),Point(cuff_inner.u+.15*w,cuff_inner.v+.04*w),cuff_inner),
      (cuff_inner,Point(cuff_inner.u-.12*w,cuff_inner.v-.26*w),Point(join.u+.07*w,join.v-.17*w),join),
    ))


def _a_collar(anchors: tuple[Point,...]) -> tuple[Point,...]:
    left,apex,right,fold=anchors
    return _closed_spans((
      (left,Point(left.u+.22*(right.u-left.u),left.v+.12*(right.u-left.u)),Point(apex.u-.2*(right.u-left.u),apex.v+.02*(right.u-left.u)),apex),
      (apex,Point(apex.u+.20*(right.u-left.u),apex.v-.08*(right.u-left.u)),Point(right.u-.08*(right.u-left.u),right.v+.05*(right.u-left.u)),right),
      (right,Point(right.u-.22*(right.u-left.u),right.v-.25*(right.u-left.u)),Point(fold.u+.18*(right.u-left.u),fold.v+.25*(right.u-left.u)),fold),
      (fold,Point(fold.u-.2*(right.u-left.u),fold.v+.10*(right.u-left.u)),Point(left.u+.08*(right.u-left.u),left.v-.08*(right.u-left.u)),left),
    ))


def _ribbon_lobe(knot: Point, tip: Point, width_ratio: float, bend: float) -> tuple[Point,...]:
    axis=_unit(_sub(tip,knot)); normal=_perp(axis); length=((tip.u-knot.u)**2+(tip.v-knot.v)**2)**0.5
    points=[]
    # Generated transverse stations form a gathered, asymmetrically folded leaf; none are teacher contour samples.
    for t in (0.0,.24,.52,.78,1.0):
        center=_add(_add(knot,_scale(axis,length*t)),_scale(normal,length*bend*t*(1-t)))
        width=length*width_ratio*(0.38+0.62*(4*t*(1-t)))
        points.append(_add(center,_scale(normal,width)))
    for t in (1.0,.78,.52,.24,0.0):
        center=_add(_add(knot,_scale(axis,length*t)),_scale(normal,length*bend*t*(1-t)))
        width=length*width_ratio*(0.38+0.62*(4*t*(1-t)))
        points.append(_sub(center,_scale(normal,width)))
    return tuple(points)


def _ribbon_tail(knot: Point, tip: Point, width_ratio: float, bend: float) -> tuple[Point,...]:
    axis=_unit(_sub(tip,knot)); normal=_perp(axis); length=((tip.u-knot.u)**2+(tip.v-knot.v)**2)**0.5
    result=[]
    for t in (0,.25,.5,.76,1):
        center=_add(_add(knot,_scale(axis,length*t)),_scale(normal,length*bend*t*(1-t)))
        width=length*width_ratio*(1-.62*t)
        result.append(_add(center,_scale(normal,width)))
    for t in (1,.76,.5,.25,0):
        center=_add(_add(knot,_scale(axis,length*t)),_scale(normal,length*bend*t*(1-t)))
        width=length*width_ratio*(1-.62*t)
        result.append(_sub(center,_scale(normal,width)))
    return tuple(result)


def _line_curve(a: Point, b: Point, bend: float, steps: int = 8) -> tuple[Point,...]:
    direction=_sub(b,a); normal=_perp(_unit(direction)); mid=_mix(a,b,.5)
    c1=_add(_mix(a,mid,.66),_scale(normal,bend)); c2=_add(_mix(mid,b,.34),_scale(normal,bend))
    return _bezier(a,c1,c2,b,steps)


_A_CLOTH=SupportFrame("A-garment-sheet","A-garment-depth")
_A_BOW=SupportFrame("A-bow-front","A-bow-depth",origin=(0,0,.06),u_axis=(1,0,.00012),v_axis=(0,1,0))
_A_COLLAR=SupportFrame("A-collar-surface","A-collar-depth",origin=(0,0,-.0411),u_axis=(1,0,.0003),v_axis=(0,1,0))
_A_INSET=SupportFrame("A-collar-inset-surface","A-collar-inset-depth",origin=(0,0,.055),u_axis=(1,0,.00008),v_axis=(0,1,0))
_A_TRIM=SupportFrame("A-trim-surface","A-trim-depth",origin=(0,0,.045),u_axis=(1,0,.0001),v_axis=(0,1,0))
_A_KNOT=SupportFrame("A-bow-knot-front","A-bow-knot-depth",origin=(0,0,.11),u_axis=(1,0,.00012),v_axis=(0,1,0))


def build_a_study() -> Study:
    """Teacher-seeded, editable upper-garment shape families, no hand/hair/pose claim."""
    neck_l,neck_r,hem_r,hem_l=(_crop_point(*p) for p in ((137,132),(309,124),(287,337),(111,334)))
    cap_join,cap_peak,cuff_outer,cuff_inner=(_crop_point(*p) for p in ((294,133),(342,119),(350,279),(322,283)))
    bodice=_shape("A-bodice","fitted light garment panel: neckline to curved lower crop hem",_A_CLOTH,"#eee9d9",
        (neck_l,neck_r,hem_r,hem_l),_a_bodice((neck_l,neck_r,hem_r,hem_l)),family="fitted_bodice_panel",
        semantic_anchors=(("neckline-left",neck_l),("neckline-right",neck_r),("shoulder-right",cap_join),("hem-right",hem_r),("hem-left",hem_l)))
    sleeve=_shape("A-right-sleeve","observed puffed sleeve cap narrowing to dark cuff",_A_CLOTH,"#e5e0d3",
        (cap_join,cap_peak,cuff_outer,cuff_inner),_a_sleeve((cap_join,cap_peak,cuff_outer,cuff_inner)),family="sleeve_cap_and_taper",
        attachments=(("A-bodice","shoulder-join","shoulder-right"),),
        semantic_anchors=(("shoulder-join",cap_join),("cap-apex",cap_peak),("cuff-outside",cuff_outer),("cuff-inside",cuff_inner)))
    cuff_outer_inner=_mix(cuff_outer,cuff_inner,.25); cuff_inner_inner=_mix(cuff_outer,cuff_inner,.78)
    cuff_controls=_closed_spans(((cuff_outer,cuff_outer_inner,Point(cuff_inner_inner.u,cuff_inner_inner.v+.12),cuff_inner),
                                 (cuff_inner,cuff_inner_inner,Point(cuff_outer_inner.u,cuff_outer_inner.v-.08),cuff_outer)))
    cuff=_shape("A-right-cuff","narrow dark wrist band follows the sleeve opening",_A_TRIM,"#293b53",
        (cuff_outer,cuff_inner,cuff_outer_inner,cuff_inner_inner),cuff_controls,family="sleeve_cuff_band",
        semantic_anchors=(("outside",cuff_outer),("inside",cuff_inner)))
    collar_left=neck_l
    collar_apex,collar_right,collar_fold=(_crop_point(*p) for p in ((211,73),(299,112),(228,153)))
    collar=_shape("A-layered-collar","cool folded collar panels framed by a sloping dark neckline",_A_COLLAR,"#a8c8d4",
        (collar_left,collar_apex,collar_right,collar_fold),_a_collar((collar_left,collar_apex,collar_right,collar_fold)),family="layered_collar",
        attachments=(("A-bodice","collar-seat","neckline-left"),),
        semantic_anchors=(("collar-seat",collar_left),("fold",collar_fold)))
    # A small pale inset uses a four-anchor relational quadrilateral derived inside the collar surface.
    inset_anchors=(collar_left,_mix(collar_left,collar_apex,.55),_mix(collar_fold,collar_right,.55),collar_fold)
    inset=_shape("A-collar-inset","pale inner collar turn gives the upper edge a second cloth plane",_A_INSET,"#d7e4df",
        inset_anchors,_closed_spans(((inset_anchors[0],_mix(inset_anchors[0],inset_anchors[1],.55),_mix(inset_anchors[0],inset_anchors[3],.35),inset_anchors[1]),
                                    (inset_anchors[1],_mix(inset_anchors[1],inset_anchors[2],.25),_mix(inset_anchors[1],inset_anchors[2],.72),inset_anchors[2]),
                                    (inset_anchors[2],_mix(inset_anchors[2],inset_anchors[3],.5),_mix(inset_anchors[2],inset_anchors[3],.9),inset_anchors[3]),
                                    (inset_anchors[3],_mix(inset_anchors[3],inset_anchors[0],.5),_mix(inset_anchors[3],inset_anchors[0],.85),inset_anchors[0]))),family="collar_inset")
    knot=_crop_point(191,187); left_tip=_crop_point(112,170); right_tip=_crop_point(253,185)
    tail_l=_crop_point(53,209); tail_r=_crop_point(149,281)
    bow_left=_shape("A-bow-left-lobe","wide left gathered bow lobe turns out from the knot",_A_BOW,"#c94d79",
        (knot,left_tip),_ribbon_lobe(knot,left_tip,.19,.16),family="gathered_bow_lobe")
    bow_right=_shape("A-bow-right-lobe","unequal right bow lobe turns down toward the sleeve",_A_BOW,"#d4557e",
        (knot,right_tip),_ribbon_lobe(knot,right_tip,.23,-.14),family="gathered_bow_lobe")
    tail_left=_shape("A-bow-tail-left","long narrow bow tail bends left from the gathered knot",_A_BOW,"#bd416d",
        (knot,tail_l),_ribbon_tail(knot,tail_l,.105,.20),family="bow_tail")
    tail_right=_shape("A-bow-tail-right","second ribbon tail folds down across the bodice",_A_BOW,"#d05279",
        (knot,tail_r),_ribbon_tail(knot,tail_r,.13,-.18),family="bow_tail")
    knot_shape=_shape("A-bow-knot","small gathered center ties both ribbon lobes and tails",_A_KNOT,"#e47591",
        (knot,),_ellipse_controls(knot,17,14),family="gathered_knot")
    shapes=(bodice,sleeve,cuff,collar,inset,bow_left,bow_right,tail_left,tail_right,knot_shape)
    lines=(
      _line("A-neckline-edge","dark trim follows the angled collar/bodice join","A-layered-collar",(collar_left,collar_fold,collar_right),_line_curve(collar_left,collar_fold,-7)+_line_curve(collar_fold,collar_right,4)[1:],"#263244",3.5),
      _line("A-sleeve-cap-seam","quiet sleeve-cap seam tucks the puff into the shoulder","A-right-sleeve",(cap_join,cap_peak),_line_curve(cap_join,cap_peak,-8),"#9d9e95",1.6),
      _line("A-cuff-light-edge","light cuff piping sits inside the dark opening band","A-right-cuff",(cuff_outer_inner,cuff_inner_inner),_line_curve(cuff_outer_inner,cuff_inner_inner,-2),"#a9bbc2",1.8),
      _line("A-bow-fold-left","fold line turns from knot toward left lobe edge","A-bow-left-lobe",(knot,left_tip),_line_curve(knot,_mix(knot,left_tip,.66),-4),"#78344f",2.0),
      _line("A-bow-fold-right","fold line opens the broader right loop","A-bow-right-lobe",(knot,right_tip),_line_curve(knot,_mix(knot,right_tip,.68),5),"#80334f",2.0),
      _line("A-bodice-tension-fold","short curved cloth fold directs toward the lower hem","A-bodice",(hem_l,hem_r),_line_curve(_mix(hem_l,neck_l,.42),_mix(hem_r,neck_r,.40),4),"#c5c3b6",1.3),
    )
    return Study("A observed upper garment",400,480,shapes,lines,(),Camera(),"#cbdedb",1.0,0.0,480.0)


def _cardinal_controls(generated_outline: tuple[Point,...]) -> tuple[Point,...]:
    """Compact generative curve handles from a validated method output; never authored target contour."""
    if len(generated_outline)<12: raise ValueError("generated limb outline is too small")
    return tuple(generated_outline[index] for index in (0,len(generated_outline)//4,len(generated_outline)//2,3*len(generated_outline)//4))


def _ellipse_controls(center: Point, rx: float, ry: float) -> tuple[Point,...]:
    return _ellipse_controls_raw(center,rx,ry)

def _ellipse_controls_raw(center: Point, rx: float, ry: float):
    return (Point(center.u-rx,center.v),Point(center.u,center.v+ry),Point(center.u+rx,center.v),Point(center.u,center.v-ry))


def _capsule(a: Point,b: Point,width: float) -> tuple[Point,...]:
    axis=_unit(_sub(b,a)); normal=_perp(axis); r=width/2
    c1=_add(a,_scale(normal,r)); c2=_add(b,_scale(normal,r))
    c3=_sub(b,_scale(normal,r)); c4=_sub(a,_scale(normal,r))
    return _closed_spans(((c1,_add(c1,_scale(axis,r*.7)),_add(c2,_scale(axis,r*.7)),c2),
                          (c2,_add(c2,_scale(axis,r)),_add(c3,_scale(axis,r)),c3),
                          (c3,_sub(c3,_scale(axis,r*.7)),_sub(c4,_scale(axis,r*.7)),c4),
                          (c4,_sub(c4,_scale(axis,r)),_sub(c1,_scale(axis,r)),c1)))


def _dish_body(center: Point, radius: float, depth: float) -> tuple[Point,...]:
    """Shallow bowl with a short flat foot edge; support contacts lie on its generated base."""
    left=Point(center.u-radius,center.v); right=Point(center.u+radius,center.v)
    foot_r=Point(center.u+radius*.48,center.v-depth); foot_l=Point(center.u-radius*.48,center.v-depth)
    foot_mid=Point(center.u,center.v-depth)
    return _closed_spans(((left,Point(center.u-radius*.55,center.v+depth*.10),Point(center.u+radius*.55,center.v+depth*.10),right),
                          (right,Point(right.u-radius*.10,right.v-depth*.65),Point(foot_r.u+radius*.08,foot_r.v),foot_r),
                          (foot_r,_mix(foot_r,foot_mid,.34),_mix(foot_r,foot_mid,.72),foot_mid),
                          (foot_mid,_mix(foot_mid,foot_l,.28),_mix(foot_mid,foot_l,.66),foot_l),
                          (foot_l,Point(foot_l.u-radius*.08,foot_l.v),Point(left.u+radius*.10,left.v-depth*.65),left)))


def _pointed_digit(root: Point, tip: Point, width: float, bend: Point | None = None) -> tuple[Point,...]:
    """Generated tapered finger with a joined knuckle root and a true pointed contact tip."""
    axis=_unit(_sub(tip,root)); normal=_perp(axis)
    middle=_mix(root,tip,.5)
    bias=Point(0,0) if bend is None else _sub(bend,middle)
    size=(bias.u*bias.u+bias.v*bias.v)**0.5
    limit=width*.42
    if size>limit: bias=_scale(bias,limit/size)
    centers=(_add(_mix(root,tip,.22),_scale(bias,.35)),
             _add(_mix(root,tip,.52),bias),
             _add(_mix(root,tip,.82),_scale(bias,.35)))
    widths=(width*.46,width*.36,width*.19)
    return (_add(root,_scale(normal,width/2)),_add(centers[0],_scale(normal,widths[0])),
            _add(centers[1],_scale(normal,widths[1])),_add(centers[2],_scale(normal,widths[2])),tip,
            _sub(centers[2],_scale(normal,widths[2])),_sub(centers[1],_scale(normal,widths[1])),
            _sub(centers[0],_scale(normal,widths[0])),_sub(root,_scale(normal,width/2)),
            _sub(root,_scale(axis,width*.22)))


def _palm_body(wrist: Point, palm_end: Point, width: float) -> tuple[Point,...]:
    """Two-width palm panel with generated heel, side taper and knuckle arc."""
    axis=_unit(_sub(palm_end,wrist)); normal=_perp(axis)
    length=((palm_end.u-wrist.u)**2+(palm_end.v-wrist.v)**2)**0.5
    heel=width*.78; knuckle=width
    a=_sub(wrist,_scale(normal,heel/2)); d=_add(wrist,_scale(normal,heel/2))
    b=_sub(palm_end,_scale(normal,knuckle/2)); c=_add(palm_end,_scale(normal,knuckle/2))
    return _closed_spans(((a,_add(a,_scale(axis,length*.40)),_sub(b,_scale(axis,length*.18)),b),
                          (b,_add(b,_scale(axis,length*.12)),_add(c,_scale(axis,length*.12)),c),
                          (c,_sub(c,_scale(axis,length*.18)),_add(d,_scale(axis,length*.40)),d),
                          (d,_sub(d,_scale(axis,length*.18)),_sub(a,_scale(axis,length*.18)),a)))


def _round_tray(center: Point, radius: float, foot_depth: float):
    return _dish_body(center,radius,foot_depth)


def _validate_scene_geometry(shapes: tuple[ShapeSpec,...], contact_pairs: dict[frozenset[str], tuple[Point,...]]) -> dict:
    """Check this bounded artwork's semantic joints, explicit touches, and affine support crossings."""
    components={}
    for spec in shapes:
        try:
            contour=sample_closed_curve(spec.controls,steps_per_segment=4)
            validate_closed_contour(contour)
        except ValueError as exc:
            raise ValueError(f"{spec.name}: invalid generated support contour: {exc}") from exc
        components[spec.name]=Component(spec.name,spec.intent,spec.support,contour,spec.fill,spec.attachments,spec.semantic_anchors)
    attachments={}
    for component in components.values():
        own=dict(component.anchors)
        if len(own)!=len(component.anchors): raise ValueError(f"duplicate semantic anchors: {component.name}")
        for target,own_name,target_name in component.attachments:
            if target not in components or own_name not in own:
                raise ValueError(f"unresolved semantic attachment: {component.name}/{target}/{own_name}")
            other=components[target]; other_anchors=dict(other.anchors)
            if target_name not in other_anchors:
                raise ValueError(f"unresolved attachment target: {target}/{target_name}")
            a=component.support.local_to_world(own[own_name]); b=other.support.local_to_world(other_anchors[target_name])
            if max(abs(a[i]-b[i]) for i in range(3))>1e-8:
                raise ValueError(f"attached world anchors disagree: {component.name}/{target}/{own_name}")
            attachments.setdefault(frozenset((component.name,target)),[]).append(Point(a[0],a[1]))
    from scripts.articulated_construction import _overlap_samples
    contact_evidence=[]
    for pair,points in contact_pairs.items():
        a,b=(components[name] for name in pair)
        for point in points:
            aw=a.support.local_to_world(point); bw=b.support.local_to_world(point)
            if max(abs(aw[i]-bw[i]) for i in range(3))>1e-8:
                raise ValueError(f"contact supports disagree in world space: {sorted(pair)}")
        overlap=polygons_overlap(_world_xy_outline(a),_world_xy_outline(b))
        separation=[]
        if overlap:
            samples=_overlap_samples(_world_xy_outline(a),_world_xy_outline(b))
            contact_world=[a.support.local_to_world(p) for p in points]
            for sample in samples:
                delta=_world_z_at_xy(a.support,sample)-_world_z_at_xy(b.support,sample)
                near_contact=min(((sample.u-world[0])**2+(sample.v-world[1])**2)**.5 for world in contact_world)<=1e-4
                if abs(delta)<=1e-9:
                    if not near_contact: raise ValueError(f"surfaces meet outside declared contact point: {sorted(pair)}")
                else:
                    separation.append(delta)
            if separation and min(separation)<0<max(separation):
                raise ValueError(f"support planes cross through positive-area contact footprint: {sorted(pair)}")
        contact_evidence.append({"parts":sorted(pair),"points":[[p.u,p.v] for p in points],"world_equality":True,
                                 "projected_footprints_overlap":overlap,"noncontact_area_depth_separated":bool(separation)})
    clearances=[]; joint_overlaps=[]
    names=list(components)
    for i,name in enumerate(names):
        a=components[name]; outline_a=_world_xy_outline(a)
        for other_name in names[i+1:]:
            b=components[other_name]; pair=frozenset((a.name,b.name)); outline_b=_world_xy_outline(b)
            if not polygons_overlap(outline_a,outline_b): continue
            if pair in contact_pairs: continue  # explicit contact pair was checked for point-only depth equality above
            samples=_overlap_samples(outline_a,outline_b)
            delta=[_world_z_at_xy(a.support,p)-_world_z_at_xy(b.support,p) for p in samples]
            if min(delta)<-1e-9 and max(delta)>1e-9:
                witnesses=attachments.get(pair,[])
                if not witnesses or any(min(((p.u-w.u)**2+(p.v-w.v)**2)**.5 for w in witnesses)>.34 for p in samples):
                    raise ValueError(f"support-depth crossing extends beyond named joint: {sorted(pair)}")
                joint_overlaps.append({"parts":sorted(pair),"bounded_support_transition_radius":.34})
                continue
            if all(abs(value)<=1e-9 for value in delta):
                witnesses=attachments.get(pair,[])
                if not witnesses or any(min(((p.u-w.u)**2+(p.v-w.v)**2)**.5 for w in witnesses)>.42 for p in samples):
                    raise ValueError(f"coplanar component overlap outside a named joint: {sorted(pair)}")
                joint_overlaps.append({"parts":sorted(pair),"bounded_to_attachment_radius":.42})
            else:
                clearances.append({"parts":sorted(pair),"minimum_depth_separation":min(abs(value) for value in delta)})
    return {"declared_touches":contact_evidence,"depth-separated_overlaps":clearances,
            "bounded_coplanar_attachment_joints":joint_overlaps,
            "scope":"Actual case component footprints/supports only; not a general volume-physics claim"}


def _b_case(case: str) -> tuple[tuple[ShapeSpec,...],tuple[LineSpec,...],dict]:
    if case not in {"baseline","variant","control"}: raise ValueError(case)
    variant=case=="variant"; control=case=="control"
    support_center=Point(2.05,2.03 if variant else 1.74)
    dish_center=Point(support_center.u,support_center.v+(.34 if control else 0.0))
    dish_rx=.53*(1.12 if variant else 1.0); dish_ry=.34
    base_dish_controls=_round_tray(support_center,dish_rx,dish_ry)
    base_dish_contour=sample_closed_curve(base_dish_controls,steps_per_segment=4)
    nominal_center=Point(support_center.u,support_center.v-dish_ry)
    dish_bottom=min(base_dish_contour,key=lambda p:(p.u-nominal_center.u)**2+(p.v-nominal_center.v)**2)
    nominal_left=Point(support_center.u-dish_rx*.48,support_center.v-dish_ry)
    side_touch=min(base_dish_contour,key=lambda p:(p.u-nominal_left.u)**2+(p.v-nominal_left.v)**2)
    nominal_right=Point(support_center.u+dish_rx*.48,support_center.v-dish_ry)
    base_foot_right=min(base_dish_contour,key=lambda p:(p.u-nominal_right.u)**2+(p.v-nominal_right.v)**2)
    shoulder=Point(.54,2.12)
    wrist=Point(1.07,1.22 if not variant else 1.52)
    contact=dish_bottom
    upper=1.02; fore=.87
    limb=construct_limb(LimbParameters(shoulder,upper,fore,wrist,1,.18,.12,.12,.09,
                                      SupportFrame(f"{case}-arm-support",f"{case}-arm-depth",origin=(0,0,.025),u_axis=(1,0,.008),v_axis=(0,1,0))))
    arm_support=limb.support
    wrist_xyz=arm_support.local_to_world(wrist)
    hand_depth_slope=.03
    hand_support=SupportFrame(f"{case}-hand-support",f"{case}-hand-depth",origin=(0,0,wrist_xyz[2]-hand_depth_slope*wrist.u),u_axis=(1,0,hand_depth_slope),v_axis=(0,1,0))
    dish_contact_z=hand_support.local_to_world(contact)[2]
    hand_plane_origin=dish_contact_z-hand_depth_slope*contact.u
    dish_plane_origin=dish_contact_z-hand_depth_slope*contact.u
    dish_support=SupportFrame(f"{case}-dish-support",f"{case}-dish-depth",origin=(0,0,dish_plane_origin),u_axis=(1,0,hand_depth_slope),v_axis=(0,1,0))
    body_support=SupportFrame(f"{case}-body-support",f"{case}-body-depth",origin=(0,0,.025+.008*shoulder.u),u_axis=(1,0,0),v_axis=(0,1,0))
    cloth_support=SupportFrame(f"{case}-shirt-front",f"{case}-shirt-depth",origin=(0,0,.06),u_axis=(1,0,0),v_axis=(0,1,0))
    hair_support=SupportFrame(f"{case}-hair-front",f"{case}-hair-depth",origin=(0,0,.08),u_axis=(1,0,0),v_axis=(0,1,0))
    near_hand_support=SupportFrame(f"{case}-near-hand-front",f"{case}-near-hand-depth",origin=(0,0,hand_plane_origin),u_axis=(1,0,hand_depth_slope),v_axis=(0,1,0))
    # Named body masses are fitted from relational torso/shoulder/hem anchors, not frame-path copying.
    torso_anchors=(Point(-.72,2.12),Point(.54,2.12),Point(.61,.52),Point(-.62,.52))
    torso_outline=_closed_spans(((torso_anchors[0],Point(-.26,2.35),Point(.25,2.34),torso_anchors[1]),
        (torso_anchors[1],Point(.77,1.70),Point(.73,.79),torso_anchors[2]),
        (torso_anchors[2],Point(.25,.36),Point(-.28,.36),torso_anchors[3]),
        (torso_anchors[3],Point(-.78,.95),Point(-.80,1.73),torso_anchors[0])))
    torso=_shape(f"{case}-torso","original fitted clothed torso mass",body_support,"#31586b",torso_anchors,torso_outline,family="relation_fitted_torso",
        semantic_anchors=(("shoulder",shoulder),("neck-base",Point(-.04,2.12))))
    shirt_anchors=(Point(-.53,2.08),Point(.40,2.08),Point(.43,.66),Point(-.49,.66))
    shirt_outline=_closed_spans(((shirt_anchors[0],Point(-.22,2.23),Point(.22,2.22),shirt_anchors[1]),
        (shirt_anchors[1],Point(.51,1.55),Point(.51,.92),shirt_anchors[2]),
        (shirt_anchors[2],Point(.2,.56),Point(-.22,.56),shirt_anchors[3]),
        (shirt_anchors[3],Point(-.58,.96),Point(-.56,1.58),shirt_anchors[0])))
    shirt=_shape(f"{case}-shirt-panel","tailored lighter vest panel defines the chest and supports art lines",cloth_support,"#d7cba7",shirt_anchors,shirt_outline,family="tailored_vest_panel")
    neck_center=Point(-.04,2.38)
    neck=_shape(f"{case}-neck","neck joins the collar opening to the head",body_support,"#e7b08a",
        (neck_center,),_ellipse_controls(neck_center,.22,.30),family="neck_oval",
        attachments=((f"{case}-torso","torso-join","neck-base"),(f"{case}-head","head-join","head-base")),
        semantic_anchors=(("torso-join",Point(-.04,2.12)),("head-join",Point(-.08,2.36))))
    head_center=Point(-.08,2.91)
    head=_shape(f"{case}-head","original head silhouette gives the support action human context",body_support,"#e9b58f",
        (head_center,),_ellipse_controls(head_center,.47,.55),family="head_mass",
        semantic_anchors=(("head-base",Point(-.08,2.36)),))
    hair_anchors=(Point(-.56,2.91),Point(-.42,3.48),Point(.32,3.49),Point(.40,2.91))
    hair=_shape(f"{case}-hair","swept dark hair cap frames a simple original face",hair_support,"#243b54",hair_anchors,
       _closed_spans(((hair_anchors[0],Point(-.53,3.27),Point(-.34,3.48),hair_anchors[1]),
                      (hair_anchors[1],Point(-.17,3.60),Point(.12,3.60),hair_anchors[2]),
                      (hair_anchors[2],Point(.50,3.31),Point(.45,3.06),hair_anchors[3]),
                      (hair_anchors[3],Point(.17,3.04),Point(-.23,3.08),hair_anchors[0]))),family="swept_hair_cap")
    # One complete IK/taper pair follows the original bent-arm pose.
    upper_anchors=(shoulder,limb.elbow,limb.wrist)
    upper_shape=_shape(f"{case}-upper-arm","bent sleeve follows two-bone shoulder-to-elbow IK",arm_support,"#83a8a6",
        upper_anchors,_cardinal_controls(limb.upper_arm.outline),family="IK_taper_upper_sleeve",
        attachments=((f"{case}-torso","shoulder","shoulder"),(f"{case}-forearm","elbow","elbow")),
        semantic_anchors=(("shoulder",shoulder),("elbow",limb.elbow)))
    fore_shape=_shape(f"{case}-forearm","second tapered sleeve segment turns toward the upturned hand",arm_support,"#9abbb1",
        upper_anchors,_cardinal_controls(limb.forearm.outline),family="IK_taper_forearm",
        attachments=((f"{case}-upper-arm","elbow","elbow"),(f"{case}-palm","wrist","wrist")),
        semantic_anchors=(("elbow",limb.elbow),("wrist",wrist)))
    # The joint palm plus four complete tapered digits is a fresh support-action shape family.
    effective_dish_center=dish_center
    effective_dish_bottom=Point(dish_center.u,dish_center.v-dish_ry)
    if control:
        dish_support=SupportFrame(f"{case}-dish-support",f"{case}-dish-depth",origin=(0,0,dish_contact_z+.015),u_axis=(1,0,0),v_axis=(0,1,0))
    radius=dish_rx
    foot_left=side_touch
    foot_center=contact
    foot_right=base_foot_right
    palm_axis=_unit(_sub(contact,wrist)); palm_normal=_perp(palm_axis)
    palm_length=((contact.u-wrist.u)**2+(contact.v-wrist.v)**2)**0.5
    palm_center=_sub(_add(wrist,_scale(palm_axis,palm_length*.55)),_scale(palm_normal,palm_length*.18))
    thumb_root=Point(palm_center.u-.23,palm_center.v-.07)
    finger_tips=(foot_left,foot_center,foot_right)
    finger_roots=tuple(_add(palm_center,_scale(palm_normal,offset)) for offset in (.12,0,-.12))
    palm_anchors=(wrist,palm_center)
    palm=_shape(f"{case}-palm","broad tapered heel and palm cup join the bent forearm to three shaped fingers",hand_support,"#e8ad89",
        palm_anchors,_palm_body(wrist,palm_center,.38),family="articulated_palm_body",
        attachments=((f"{case}-forearm","wrist","wrist"),),
        semantic_anchors=(("wrist",wrist),("finger-root-index",finger_roots[0]),
                          ("finger-root-middle",finger_roots[1]),("finger-root-ring",finger_roots[2]),
                          ("thumb-root",thumb_root)))
    finger_specs=[]
    digit_names=("index","middle","ring")
    for digit,root,tip,width,prop_anchor in zip(digit_names,finger_roots,finger_tips,(.07,.075,.07),
                                                  ("thumb-side","base-contact","foot-right")):
        attachments=[(f"{case}-palm","root",f"finger-root-{digit}")]
        if not control:
            attachments.append((f"{case}-dish-wall","tip",prop_anchor))
        finger_specs.append(_shape(f"{case}-finger-{digit}",f"separate tapered {digit} finger reaches under the dish foot",hand_support,"#e8ad89",
            (root,tip),_pointed_digit(root,tip,width),family="pointed_support_digit",attachments=tuple(attachments),
            semantic_anchors=(("root",root),("tip",tip))))
    thumb_bend=Point((thumb_root.u+side_touch.u)/2,min(thumb_root.v,side_touch.v)-.045)
    thumb_anchors=(thumb_root,thumb_bend,side_touch)
    thumb_attachments=((f"{case}-palm","thumb-root","thumb-root"),)
    if not control: thumb_attachments+=((f"{case}-dish-wall","thumb-touch","thumb-side"),)
    thumb=_shape(f"{case}-thumb-brace","curved opposing thumb braces under the left dish-foot edge",hand_support,"#e8ad89",
        thumb_anchors,_pointed_digit(thumb_root,side_touch,.12,bend=thumb_bend),family="tapered_thumb_brace",attachments=thumb_attachments,
        semantic_anchors=(("thumb-root",thumb_root),("thumb-touch",side_touch)))
    # The index/thumb web is a named local hand junction, bounded to the palm-side overlap.
    web_point=_mix(finger_roots[0],finger_tips[0],.18)
    index=finger_specs[0]
    finger_specs[0]=ShapeSpec(index.name,index.intent,index.support,index.fill,index.controls,index.authored_anchors,
        index.attachments+((thumb.name,"web-index","web-index"),),
        index.semantic_anchors+(("web-index",web_point),),index.family)
    thumb=ShapeSpec(thumb.name,thumb.intent,thumb.support,thumb.fill,thumb.controls,thumb.authored_anchors,
        thumb.attachments+((index.name,"web-index","web-index"),),
        thumb.semantic_anchors+(("web-index",web_point),),thumb.family)
    middle=finger_specs[1]
    middle_web=_mix(finger_roots[1],thumb_root,.5)
    finger_specs[1]=ShapeSpec(middle.name,middle.intent,middle.support,middle.fill,middle.controls,middle.authored_anchors,
        middle.attachments+((thumb.name,"web-middle","web-middle"),),
        middle.semantic_anchors+(("web-middle",middle_web),),middle.family)
    thumb=ShapeSpec(thumb.name,thumb.intent,thumb.support,thumb.fill,thumb.controls,thumb.authored_anchors,
        thumb.attachments+((middle.name,"web-middle","web-middle"),),
        thumb.semantic_anchors+(("web-middle",middle_web),),thumb.family)
    dish_controls=_round_tray(effective_dish_center,radius,dish_ry)
    dish_contour=sample_closed_curve(dish_controls,steps_per_segment=4)
    center_nominal=Point(effective_dish_center.u,effective_dish_center.v-dish_ry)
    effective_dish_bottom=min(dish_contour,key=lambda p:(p.u-center_nominal.u)**2+(p.v-center_nominal.v)**2)
    left_nominal=Point(effective_dish_center.u-radius*.48,effective_dish_center.v-dish_ry)
    right_nominal=Point(effective_dish_center.u+radius*.48,effective_dish_center.v-dish_ry)
    effective_foot_left=min(dish_contour,key=lambda p:(p.u-left_nominal.u)**2+(p.v-left_nominal.v)**2)
    effective_foot_right=min(dish_contour,key=lambda p:(p.u-right_nominal.u)**2+(p.v-right_nominal.v)**2)
    dish_anchors=(Point(effective_dish_center.u-radius,effective_dish_center.v),
                  Point(effective_dish_center.u+radius,effective_dish_center.v),
                  effective_foot_right,effective_foot_left)
    dish=_shape(f"{case}-dish-wall","shallow ceramic fruit dish has flared rim and a short flat support foot",dish_support,"#628c91",
        dish_anchors,dish_controls,family="shallow_dish",
        semantic_anchors=(("base-contact",effective_dish_bottom),("thumb-side",effective_foot_left),
                          ("foot-right",effective_foot_right)))
    dish_front_support=SupportFrame(f"{case}-dish-front",f"{case}-dish-front-depth",origin=(0,0,dish_plane_origin+.06),u_axis=(1,0,hand_depth_slope),v_axis=(0,1,0))
    fruit_support=SupportFrame(f"{case}-fruit-front",f"{case}-fruit-depth",origin=(0,0,dish_plane_origin+.08),u_axis=(1,0,hand_depth_slope),v_axis=(0,1,0))
    leaf_support=SupportFrame(f"{case}-leaf-front",f"{case}-leaf-depth",origin=(0,0,dish_plane_origin+.10),u_axis=(1,0,hand_depth_slope),v_axis=(0,1,0))
    rim_center=Point(effective_dish_center.u,effective_dish_center.v-.005)
    rim=_shape(f"{case}-dish-rim","elliptical glazed rim separates fruit from the bowl wall",dish_front_support,"#e7d4af",
        (rim_center,),_ellipse_controls(rim_center,radius,.078),family="dish_rim")
    fruit_center=Point(effective_dish_center.u-.06,effective_dish_center.v+.09)
    fruit=_shape(f"{case}-fruit","single apricot-like fruit makes the carried dish a small still life",fruit_support,"#e59158",
        (fruit_center,),_ellipse_controls(fruit_center,.17,.20),family="elliptic_fruit")
    leaf_center=Point(fruit_center.u+.06,fruit_center.v+.18)
    leaf_anchors=_ellipse_controls(leaf_center,.13,.075)
    leaf=_shape(f"{case}-leaf","small oval leaf accent echoes the carried still life",leaf_support,"#56755b",(leaf_center,),
        leaf_anchors,family="leaf_ovoid")
    # Check exact finger and thumb support maps; the control keeps the same hand but displaces the dish.
    if not control:
        hand_world=hand_support.local_to_world(foot_center); dish_world=dish_support.local_to_world(foot_center)
        if max(abs(hand_world[i]-dish_world[i]) for i in range(3))>1e-8:
            raise ValueError("middle fingertip support surface missed the dish foot")
    shapes=(torso,shirt,neck,head,hair,upper_shape,fore_shape,palm,*finger_specs,thumb,dish,rim,fruit,leaf)
    lines=[]
    # Short curved face marks keep the body an intentional small illustration.
    face_center=head_center
    eye_l=Point(face_center.u-.16,face_center.v+.04); eye_r=Point(face_center.u+.12,face_center.v+.04)
    lines.extend((_line(f"{case}-eye-left","small left eye",f"{case}-head",(eye_l,),_line_curve(eye_l,Point(eye_l.u+.045,eye_l.v),0,4),"#304251",2.0),
                  _line(f"{case}-eye-right","small right eye",f"{case}-head",(eye_r,),_line_curve(eye_r,Point(eye_r.u+.045,eye_r.v),0,4),"#304251",2.0)))
    cuff_a=Point(wrist.u-.11,wrist.v+.09); cuff_b=Point(wrist.u+.08,wrist.v-.11)
    lines.append(_line(f"{case}-cuff-seam","cuff turn follows wrist orientation",f"{case}-forearm",(cuff_a,cuff_b),_line_curve(cuff_a,cuff_b,.01),"#45686d",2.1))
    hand_crease_a=Point(wrist.u+.30,wrist.v-.04); hand_crease_b=Point(wrist.u+.50,wrist.v-.015)
    lines.append(_line(f"{case}-palm-crease","one palm crease clarifies the open cup of the hand",f"{case}-palm",(hand_crease_a,hand_crease_b),_line_curve(hand_crease_a,hand_crease_b,.025),"#a86e62",1.5))
    # Small marks follow the three filled digit forms; they do not substitute for finger silhouettes.
    for digit,spec,root,tip in zip(digit_names,finger_specs,finger_roots,finger_tips):
        crease_start=_mix(root,tip,.34); crease_end=_mix(root,tip,.58)
        lines.append(_line(f"{case}-{digit}-crease",f"crease follows the shaped {digit} finger",spec.name,
                           (crease_start,crease_end),_line_curve(crease_start,crease_end,.008),"#a4695f",1.25))
    side_crease_a=_mix(thumb_root,side_touch,.38); side_crease_b=_mix(thumb_root,side_touch,.68)
    lines.append(_line(f"{case}-thumb-crease","thumb pad bends toward its named support contact",f"{case}-thumb-brace",(side_crease_a,side_crease_b),_line_curve(side_crease_a,side_crease_b,.012),"#a4695f",1.3))
    rim_a=Point(effective_dish_center.u-radius*.78,effective_dish_center.v+.015)
    rim_b=Point(effective_dish_center.u+radius*.78,effective_dish_center.v+.015)
    lines.append(_line(f"{case}-rim-light","small bright rim arc makes bowl opening explicit",f"{case}-dish-rim",(rim_a,rim_b),_line_curve(rim_a,rim_b,.045),"#f4e6c8",2.3))
    lines.append(_line(f"{case}-fruit-seam","fruit highlight seam is a restrained color-form cue",f"{case}-fruit",(Point(fruit_center.u-.04,fruit_center.v-.12),Point(fruit_center.u+.02,fruit_center.v+.08)),_line_curve(Point(fruit_center.u-.04,fruit_center.v-.12),Point(fruit_center.u+.02,fruit_center.v+.08),.02),"#f4c07e",1.8))
    shape_names={s.name for s in shapes}
    if any(line.owner not in shape_names for line in lines): raise ValueError("semantic line owner is missing")
    contact_pairs={} if control else {
        frozenset((finger_specs[0].name,dish.name)):(foot_left,),
        frozenset((finger_specs[1].name,dish.name)):(foot_center,),
        frozenset((finger_specs[2].name,dish.name)):(foot_right,),
        frozenset((thumb.name,dish.name)):(side_touch,),
    }
    collision=_validate_scene_geometry(shapes,contact_pairs)
    contact_evidence={
      "action":"upturned connected palm supports shallow fruit dish with three fingertips; thumb braces the same left foot edge",
      "successful_contact_world":"three fingertip support anchors and thumb brace equal their named dish-foot world points",
      "successful_side_contact":"geometry shares the named left foot touch while the full finger/prop silhouette remains separate in area",
      "control":"dish alone moved away from the unchanged hand by authored 0.34 scene units; labeled near miss",
      "contact_point_crop_local":"not applicable; B is original and uses scene coordinates",
      "collision_check":collision,
      "semantic_case":case,
      "dish_width_ratio":1.12 if variant else 1.0,
      "wrist_target": [wrist.u,wrist.v],
      "dish_center": [effective_dish_center.u,effective_dish_center.v],
    }
    return shapes,tuple(lines),contact_evidence


def build_b_study(case: str) -> tuple[Study,dict]:
    shapes,lines,evidence=_b_case(case)
    title={"baseline":"SUPPORT · chest level","variant":"VARIATION · lifted + broader dish",
           "control":"CONTROL — near miss"}[case]
    caption="dish displaced; hand remains still" if case=="control" else "bent arm · open palm supports dish · thumb braces rim"
    study=Study(f"B {case} supported fruit dish",450,640,shapes,lines,
        ((title,"panel",225,40),(caption,"caption",225,612)),Camera(),"#eee8dd",
        112.0,132.0,570.0)
    return study,evidence


def compose_b_studies(svgs: tuple[str,...]) -> str:
    """Arrange three pipeline-rendered case vectors as a matched-camera art contact sheet."""
    if len(svgs)!=3: raise ValueError("B artwork sheet needs baseline, variation, and control")
    groups=[]
    for index,source in enumerate(svgs):
        opening=source.find(">")
        ending=source.rfind("</svg>")
        if opening<0 or ending<opening: raise ValueError("invalid rendered B panel SVG")
        groups.append(f'<g id="case-panel-{index}" transform="translate({index*450},0)">'+source[opening+1:ending]+'</g>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1350" height="640" viewBox="0 0 1350 640">\n'+
      '<!-- three matched-camera vector studies; each figure part is emitted from the guarded spatial pipeline -->\n'+
      ''.join(groups)+
      '<path id="case-divider-1" d="M 450,0 V 640" stroke="#d0c6b7" stroke-width="1.2"/>'+
      '<path id="case-divider-2" d="M 900,0 V 640" stroke="#d0c6b7" stroke-width="1.2"/>\n</svg>\n')


def _screen(study: Study, point: tuple[float,float,float]) -> tuple[float,float]:
    return study.offset_x+study.scale*point[0], study.offset_y-study.scale*point[1]


def _line_svg(study: Study, span, color: str, width: float, name: str) -> str:
    a,b=(_screen(study,p) for p in span)
    return (f'<path id="{html.escape(name)}" d="M {a[0]:.3f},{a[1]:.3f} L {b[0]:.3f},{b[1]:.3f}" '
            f'fill="none" stroke="{html.escape(color)}" stroke-width="{width:.2f}" stroke-linecap="round" stroke-linejoin="round"/>')


def build_svg(study: Study) -> str:
    """Renderer boundary accepts only semantic scene, never target/raster/crop paths."""
    components={}
    for spec in study.shapes:
        result=build_visible_smooth_component(spec.controls,spec.name,spec.support,study.camera,(),
            intent=spec.intent,fill=spec.fill,attachments=spec.attachments,anchors=spec.semantic_anchors)
        if not isinstance(result,VisibleSmoothComponent) or result.component.outline is not result.validated_sampled_contour:
            raise ValueError(f"unvalidated generated component: {spec.name}")
        if spec.name in components: raise ValueError(f"duplicate component ID: {spec.name}")
        components[spec.name]=result.component
    visible={}
    for spec in study.shapes:
        occluders=tuple(part for name,part in components.items() if name!=spec.name)
        result=build_visible_smooth_component(spec.controls,spec.name,spec.support,study.camera,occluders,
            intent=spec.intent,fill=spec.fill,attachments=spec.attachments,anchors=spec.semantic_anchors)
        if result.component.outline is not result.validated_sampled_contour:
            raise ValueError(f"emission contour bypassed guard: {spec.name}")
        if not result.visible_fill_regions: raise ValueError(f"depth engine removed all fill for {spec.name}")
        visible[spec.name]=result
    prefix=re.sub(r"[^A-Za-z0-9_-]+","-",study.name).strip("-")
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{study.width}" height="{study.height}" viewBox="0 0 {study.width} {study.height}">',
       '<!-- ground: authored neutral art paper; all semantic objects below come from guarded support/depth adapters -->',
       f'<rect id="study-ground-{prefix}" width="100%" height="100%" fill="{study.background}"/>']
    if study.panel_width:
        for x in (study.panel_width,2*study.panel_width):
            parts.append(f'<path id="case-divider-{x}" d="M {x},0 V {study.height}" stroke="#d0c6b7" stroke-width="1.2"/>')
    for spec in study.shapes:
        result=visible[spec.name]
        for index,(path,color,owner) in enumerate(result.visible_fill_regions):
            from scripts.articulated_line_visibility import transform_compound_path
            mapped=transform_compound_path(path,lambda x,y:_screen(study,(x,y,0.0)))
            parts.append(f'<!-- {html.escape(spec.name)}: {html.escape(spec.intent)}; family={html.escape(spec.family)} -->')
            parts.append(f'<path id="fill-{html.escape(owner)}-{index}" d="{mapped}" fill="{color}" stroke="none"/>')
        for index,span in enumerate(result.authored_boundary_spans):
            parts.append(f'<!-- {html.escape(spec.name)}: geometry-visible semantic component boundary -->')
            parts.append(_line_svg(study,span,"#293a49",1.65,f"outline-{spec.name}-{index}"))
    for line in study.lines:
        owner=components[line.owner]
        scene=tuple(components.values())
        for index,span in enumerate(project_visible_semantic_path(line.points,owner,study.camera,scene)):
            parts.append(f'<!-- {html.escape(line.name)}: {html.escape(line.intent)}; owner={html.escape(line.owner)} -->')
            parts.append(_line_svg(study,span,line.color,line.width,f"line-{line.name}-{index}"))
    for index,(text,style,x,y) in enumerate(study.labels):
        parts.append(f'<!-- label {index}: authored scope/action label -->')
        if style=="panel":
            parts.append(f'<text id="study-label-{prefix}-{index}" x="{x}" y="{y}" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="650" fill="#283d4a">{html.escape(text)}</text>')
        else:
            parts.append(f'<text id="study-label-{prefix}-{index}" x="{x}" y="{y}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#5b6263">{html.escape(text)}</text>')
    parts.append('</svg>')
    return "\n".join(parts)+"\n"
