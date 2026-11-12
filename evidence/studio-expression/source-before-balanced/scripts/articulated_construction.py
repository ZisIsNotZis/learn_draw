"""Semantic articulated construction, support triangulation, and depth adapter.

Reimplements geometric ideas from MIT huashu-art-motion ``R.ik2``/``R.taper``
without vendor character coordinates, art, or frames. Visibility is delegated to
this project's opaque-triangle depth engine; the MIT code license does not clear
separately restricted character art or external references.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from scripts.vector_visibility import visible_fragments, visible_regions


@dataclass(frozen=True)
class Point:
    u: float
    v: float
    def __add__(self, other): return Point(self.u + other.u, self.v + other.v)
    def __sub__(self, other): return Point(self.u - other.u, self.v - other.v)
    def scale(self, factor): return Point(self.u * factor, self.v * factor)


@dataclass(frozen=True)
class SupportFrame:
    """Affine 3D plane: origin plus two linearly independent local axes."""
    support_id: str
    depth_ref: str
    origin: tuple[float, float, float] = (0., 0., 0.)
    u_axis: tuple[float, float, float] = (1., 0., 0.)
    v_axis: tuple[float, float, float] = (0., 1., 0.)
    def local_to_world(self, point):
        return tuple(self.origin[i] + point.u*self.u_axis[i] + point.v*self.v_axis[i] for i in range(3))


@dataclass(frozen=True)
class LimbParameters:
    shoulder: Point
    upper_length: float
    fore_length: float
    hand_target: Point
    elbow_branch: int
    upper_width_shoulder: float
    upper_width_elbow: float
    fore_width_elbow: float
    fore_width_wrist: float
    support: SupportFrame


@dataclass(frozen=True)
class TaperedSegment:
    start: Point
    end: Point
    outline: tuple[Point, ...]
    def world_outline(self, support): return tuple(support.local_to_world(p) for p in self.outline)


@dataclass(frozen=True)
class PalmAttachment:
    origin: Point
    tangent: Point
    support: SupportFrame


@dataclass(frozen=True)
class LimbConstruction:
    elbow: Point
    wrist: Point
    upper_arm: TaperedSegment
    forearm: TaperedSegment
    palm: PalmAttachment
    support: SupportFrame


def _length(point): return math.hypot(point.u, point.v)
def _unit(point):
    n = _length(point)
    if n <= 1e-12: raise ValueError("segment direction is degenerate")
    return point.scale(1/n)
def _finite(*values): return all(math.isfinite(v) for v in values)


def taper_profile(t, width_start, width_end):
    """Cubic smoothstep width law, with zero slope at both semantic endpoints."""
    s = t*t*(3-2*t)
    return width_start + (width_end-width_start)*s


def _taper(start, end, width_start, width_end, samples=16):
    direction = _unit(end-start); normal = Point(-direction.v, direction.u); delta=end-start
    side_a=[]; side_b=[]
    for i in range(samples+1):
        t=i/samples; width=taper_profile(t,width_start,width_end); center=start+delta.scale(t)
        side_a.append(center+normal.scale(width)); side_b.append(center-normal.scale(width))
    cap_end=[end+direction.scale(width_end*math.cos(math.pi/2-math.pi*i/samples))+normal.scale(width_end*math.sin(math.pi/2-math.pi*i/samples)) for i in range(samples+1)]
    cap_start=[start+direction.scale(width_start*math.cos(-math.pi/2-math.pi*i/samples))+normal.scale(width_start*math.sin(-math.pi/2-math.pi*i/samples)) for i in range(samples+1)]
    return TaperedSegment(start,end,tuple(side_a+cap_end+list(reversed(side_b))+cap_start))


def _validate_support(support):
    vals=(*support.origin,*support.u_axis,*support.v_axis)
    if not support.support_id or not support.depth_ref or not _finite(*vals): raise ValueError("support frame must be named and finite")
    a,b=support.u_axis,support.v_axis
    cross=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    if math.sqrt(sum(x*x for x in cross))<=1e-12: raise ValueError("support axes must span a surface")


def construct_limb(p):
    vals=(p.shoulder.u,p.shoulder.v,p.hand_target.u,p.hand_target.v,p.upper_length,p.fore_length,p.upper_width_shoulder,p.upper_width_elbow,p.fore_width_elbow,p.fore_width_wrist)
    if not _finite(*vals): raise ValueError("limb parameters must be finite")
    _validate_support(p.support)
    if p.elbow_branch not in (-1,1): raise ValueError("elbow_branch must be -1 or +1")
    if p.upper_length<=0 or p.fore_length<=0: raise ValueError("segment lengths must be positive")
    if min(p.upper_width_shoulder,p.upper_width_elbow,p.fore_width_elbow,p.fore_width_wrist)<=0: raise ValueError("taper widths must be positive")
    delta=p.hand_target-p.shoulder; d=_length(delta); a,b=p.upper_length,p.fore_length
    if d<=1e-12: raise ValueError("shoulder and hand target must differ")
    if d>a+b+1e-9 or d<abs(a-b)-1e-9: raise ValueError("hand target outside two-bone reachable interval")
    axis=delta.scale(1/d); along=(a*a-b*b+d*d)/(2*d); h2=a*a-along*along
    if h2 < -1e-9: raise ValueError("numerically unreachable")
    normal=Point(-axis.v,axis.u); elbow=p.shoulder+axis.scale(along)+normal.scale(p.elbow_branch*math.sqrt(max(0,h2)))
    return LimbConstruction(elbow,p.hand_target,_taper(p.shoulder,elbow,p.upper_width_shoulder,p.upper_width_elbow),_taper(elbow,p.hand_target,p.fore_width_elbow,p.fore_width_wrist),PalmAttachment(p.hand_target,_unit(p.hand_target-elbow),p.support),p.support)


@dataclass(frozen=True)
class Camera:
    """Orthographic basis: world X horizontal, world Y up, world Z depth."""
    horizontal: tuple[float, float, float] = (1., 0., 0.)
    vertical: tuple[float, float, float] = (0., 1., 0.)
    depth: tuple[float, float, float] = (0., 0., 1.)
    def project(self, xyz):
        return tuple(sum(axis[i] * xyz[i] for i in range(3))
                     for axis in (self.horizontal, self.vertical, self.depth))


@dataclass(frozen=True)
class Component:
    name: str
    intent: str
    support: SupportFrame
    outline: tuple[Point,...]
    fill: str
    attachments: tuple[tuple[str,str,str],...]=()
    anchors: tuple[tuple[str,Point],...]=()
    def world_outline(self): return tuple(self.support.local_to_world(p) for p in self.outline)


def _point_distance(a,b): return math.hypot(a.u-b.u,a.v-b.v)
def _clean_polygon(poly):
    clean=[]
    for p in poly:
        if not clean or _point_distance(p,clean[-1])>1e-10: clean.append(p)
    if len(clean)>1 and _point_distance(clean[0],clean[-1])<=1e-10: clean.pop()
    return clean


def triangulate_polygon(poly):
    """Ear-clip a simple polygon; supports concave boundaries, rejects invalid ones."""
    pts=_clean_polygon(list(poly))
    if len(pts)<3: raise ValueError("polygon needs at least three distinct vertices")
    area=sum(a.u*b.v-b.u*a.v for a,b in zip(pts,pts[1:]+pts[:1]))
    if area==0: raise ValueError("polygon has zero area")
    for i,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
        for j,(c,d) in enumerate(zip(pts,pts[1:]+pts[:1])):
            if j<=i or j in (i-1,i+1) or (i==0 and j==len(pts)-1): continue
            if _segments_cross(a,b,c,d): raise ValueError("polygon is self-intersecting")
    sign=1 if area>0 else -1; indices=list(range(len(pts))); triangles=[]
    def cross(a,b,c): return (b.u-a.u)*(c.v-a.v)-(b.v-a.v)*(c.u-a.u)
    def inside(p,a,b,c):
        vals=(cross(a,b,p)*sign,cross(b,c,p)*sign,cross(c,a,p)*sign)
        return min(vals)>=-1e-10
    budget=len(indices)**2
    while len(indices)>3 and budget:
        budget-=1; found=False
        for j,i in enumerate(indices):
            prev=indices[j-1]; nxt=indices[(j+1)%len(indices)]; a,b,c=pts[prev],pts[i],pts[nxt]
            if cross(a,b,c)*sign<=1e-12: continue
            if any(inside(pts[k],a,b,c) for k in indices if k not in (prev,i,nxt)): continue
            triangles.append((a,b,c)); indices.pop(j); found=True; break
        if not found: raise ValueError("polygon is self-intersecting or numerically non-simple")
    if len(indices)!=3: raise ValueError("polygon triangulation did not converge")
    triangles.append(tuple(pts[i] for i in indices))
    return tuple(triangles)


def component_faces(components,camera=Camera()):
    """Map semantic local contours through support/camera into engine triangle faces."""
    faces=[]
    for comp in components:
        _validate_support(comp.support)
        for tri in triangulate_polygon(comp.outline):
            projected=tuple(camera.project(comp.support.local_to_world(p)) for p in tri)
            faces.append((projected,comp.fill,comp.name))
    return tuple(faces)


def visible_scene(components,camera=Camera()):
    """Return depth-derived visibility using the project's opaque-triangle engine."""
    return tuple(visible_fragments(component_faces(components,camera)))


def visible_scene_regions(components,camera=Camera()):
    return tuple(visible_regions(component_faces(components,camera)))


def _ellipse(center, rx, ry, count=32):
    return tuple(Point(center.u+rx*math.cos(2*math.pi*i/count), center.v+ry*math.sin(2*math.pi*i/count)) for i in range(count))


@dataclass(frozen=True)
class StudyCase:
    name: str
    components: tuple[Component,...]
    camera: Camera
    contact: Point
    elbow: Point
    hand_target: Point
    control: bool


def build_study_case(case):
    """Build frozen B baseline/variant/control geometry from semantic relations."""
    if case not in ("baseline","variant","control"):
        raise ValueError("case must be baseline, variant, or control")
    body_slope=0.04
    body=SupportFrame("body-front","body-depth",u_axis=(1,0,body_slope))
    torso_rx=0.9*(1.08 if case=="variant" else 1.)
    shoulder_angle=2*math.pi*5/32
    shoulder=Point(torso_rx*math.cos(shoulder_angle),1.2+1.2*math.sin(shoulder_angle))
    arm_slope=-0.10
    arm_intercept=(body_slope-arm_slope)*shoulder.u
    arm=SupportFrame("arm-surface","arm-depth",(0,0,arm_intercept),(1,0,arm_slope),(0,1,0))
    torso=Component("torso","clothed torso mass",body,_ellipse(Point(0,1.2),torso_rx,1.2),"#536d8a",
                    anchors=(("shoulder",shoulder),("neck-top",Point(0,2.4))))
    head=Component("head","separate head silhouette",body,_ellipse(Point(0,3.12),0.55,0.62),"#e9b997",
                   (("neck","neck-bottom","neck-top"),),(("neck-bottom",Point(0,2.5)),))
    neck=Component("neck","generated neck joining head and torso",body,_ellipse(Point(0,2.45),0.2,0.05),"#e9b997",
                   (("head","neck-top","neck-bottom"),("torso","neck-bottom","neck-top")),
                   (("neck-top",Point(0,2.5)),("neck-bottom",Point(0,2.4))))
    if case=="variant": contact=Point(2.00,1.45)
    else: contact=Point(2.05,1.65)
    upper=1.65*(1.08 if case=="variant" else 1.)
    fore=1.35
    # Wrist target sits one authored palm-reach relation behind the declared prop touch.
    target=Point(contact.u-0.45,contact.v)
    if case=="control":
        # Task-frozen 0.18 of total arm length shortfall along final approach.
        target=Point(target.u-0.18*(upper+fore),target.v)
    limb=construct_limb(LimbParameters(shoulder,upper,fore,target,1,0.25,0.21,0.19,0.15,arm))
    upper_component=Component("upper_arm","IK-derived shoulder-to-elbow tapered sleeve",arm,limb.upper_arm.outline,"#8398ad",
                              (("torso","shoulder","shoulder"),("forearm","elbow","elbow")),
                              (("shoulder",shoulder),("elbow",limb.elbow)))
    fore_component=Component("forearm","IK-derived elbow-to-wrist tapered sleeve",arm,limb.forearm.outline,"#9cafc1",
                             (("upper_arm","elbow","elbow"),("hand","wrist","wrist")),
                             (("elbow",limb.elbow),("wrist",target)))
    hand_slope=0.08
    wrist_depth=arm.local_to_world(target)[2]
    hand_intercept=wrist_depth-hand_slope*target.u
    hand_surface=SupportFrame("hand-surface","hand-depth",(0,0,hand_intercept),(1,0,hand_slope),(0,1,0))
    prop_slope=-0.04
    touch_depth=hand_surface.local_to_world(contact)[2]
    prop_intercept=touch_depth-prop_slope*contact.u
    prop_surface=SupportFrame("prop-surface","prop-depth",(0,0,prop_intercept),(1,0,prop_slope),(0,1,0))
    hand_center=Point(target.u+0.20,target.v)
    hand_touch=Point(target.u+0.45,target.v)
    hand_links=(("forearm","wrist","wrist"),) if case=="control" else (("forearm","wrist","wrist"),("prop","touch","touch"))
    hand=Component("hand","generated palm silhouette attached at wrist and reaching prop",hand_surface,_ellipse(hand_center,0.25,0.16),"#e9b997",
                   hand_links,(("wrist",target),("touch",hand_touch)))
    prop_center=Point(contact.u+0.24,contact.v)
    prop_links=() if case=="control" else (("hand","touch","touch"),)
    prop=Component("prop","simple authored oval prop with declared touch point",prop_surface,_ellipse(prop_center,0.24,0.4),"#d4a63e",
                   prop_links,(("touch",contact),))
    components=(torso,neck,head,upper_component,fore_component,hand,prop)
    return StudyCase(case,components,Camera(),contact,limb.elbow,target,case=="control")


def _orient(a,b,c): return (b.u-a.u)*(c.v-a.v)-(b.v-a.v)*(c.u-a.u)
def _on_segment(a,b,p): return min(a.u,b.u)-1e-9<=p.u<=max(a.u,b.u)+1e-9 and min(a.v,b.v)-1e-9<=p.v<=max(a.v,b.v)+1e-9 and abs(_orient(a,b,p))<=1e-9
def _segments_cross(a,b,c,d):
    o1,o2,o3,o4=_orient(a,b,c),_orient(a,b,d),_orient(c,d,a),_orient(c,d,b)
    return (o1*o2<0 and o3*o4<0) or (abs(o1)<=1e-9 and _on_segment(a,b,c)) or (abs(o2)<=1e-9 and _on_segment(a,b,d)) or (abs(o3)<=1e-9 and _on_segment(c,d,a)) or (abs(o4)<=1e-9 and _on_segment(c,d,b))
def _inside(point,poly):
    result=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a.v>point.v)!=(b.v>point.v) and point.u<(b.u-a.u)*(point.v-a.v)/(b.v-a.v)+a.u: result=not result
    return result


def _on_boundary(point,poly):
    return any(_on_segment(a,b,point) for a,b in zip(poly,poly[1:]+poly[:1]))


def _edge_intersection(a,b,c,d):
    den=(a.u-b.u)*(c.v-d.v)-(a.v-b.v)*(c.u-d.u)
    if abs(den)<1e-12: return None
    det1=a.u*b.v-a.v*b.u; det2=c.u*d.v-c.v*d.u
    x=(det1*(c.u-d.u)-(a.u-b.u)*det2)/den
    y=(det1*(c.v-d.v)-(a.v-b.v)*det2)/den
    p=Point(x,y)
    return p if _on_segment(a,b,p) and _on_segment(c,d,p) else None


def _area(poly):
    return abs(sum(a.u*b.v-b.u*a.v for a,b in zip(poly,poly[1:]+poly[:1])))/2


def _triangle_intersection(subject, clip):
    """Clip one convex triangle by another; zero-area boundary contact is excluded."""
    output=list(subject)
    orientation=1 if _orient(*clip)>0 else -1
    for a,b in zip(clip,clip[1:]+clip[:1]):
        source,output=output,[]
        if not source: break
        for p,q in zip(source,source[1:]+source[:1]):
            pin=_orient(a,b,p)*orientation>=0
            qin=_orient(a,b,q)*orientation>=0
            if pin and qin: output.append(q)
            elif pin != qin:
                edge=Point(b.u-a.u,b.v-a.v)
                direction=Point(q.u-p.u,q.v-p.v)
                den=direction.u*edge.v-direction.v*edge.u
                if den:
                    t=((a.u-p.u)*edge.v-(a.v-p.v)*edge.u)/den
                    crossing=Point(p.u+t*(q.u-p.u),p.v+t*(q.v-p.v))
                    output.append(crossing)
                if qin: output.append(q)
    return output if len(output)>=3 and _area(output)>0 else []


def _overlap_samples(a,b):
    """Return witnesses only for positive-area intersections of simple polygons."""
    at,bt=triangulate_polygon(a),triangulate_polygon(b)
    samples=[]
    for ta in at:
        for tb in bt:
            intersection=_triangle_intersection(ta,tb)
            if intersection:
                samples.extend(intersection)
                samples.append(Point(sum(p.u for p in intersection)/len(intersection),
                                     sum(p.v for p in intersection)/len(intersection)))
    return samples


def polygons_overlap(a,b):
    """Positive-area overlap for simple polygons; shared boundary alone is legal."""
    return bool(_overlap_samples(a,b))


def _world_xy_outline(component):
    """Map a support contour to common world XY; reject frames not XY-projectable."""
    support=component.support
    ux,uy=support.u_axis[:2]; vx,vy=support.v_axis[:2]
    determinant=ux*vy-uy*vx
    if determinant==0 or not math.isfinite(determinant):
        raise ValueError(f"unsupported support frame for XY collision check: {support.support_id}")
    return tuple(Point(support.origin[0]+p.u*ux+p.v*vx,
                       support.origin[1]+p.u*uy+p.v*vy) for p in component.outline)


def _world_z_at_xy(support, point):
    ux,uy=support.u_axis[:2]; vx,vy=support.v_axis[:2]
    det=ux*vy-uy*vx
    dx,dy=point.u-support.origin[0],point.v-support.origin[1]
    u=(dx*vy-dy*vx)/det; v=(ux*dy-uy*dx)/det
    return support.origin[2]+u*support.u_axis[2]+v*support.v_axis[2]


def validate_study_case(study):
    """Check anchors/reachability and bounded XY-footprint surface intersections."""
    by_name={c.name:c for c in study.components}
    required={"head","neck","torso","upper_arm","forearm","hand","prop"}
    if set(by_name)!=required: raise ValueError("semantic component set incomplete")
    prop=by_name["prop"]
    left=min(p.u for p in prop.outline)
    if abs(left-study.contact.u)>1e-8: raise ValueError("prop contact anchor mismatch")
    hand=by_name["hand"]
    hand_right=max(p.u for p in hand.outline)
    if study.control:
        if not hand_right < study.contact.u-0.1: raise ValueError("near-miss control lacks a visible contact gap")
    elif abs(hand_right-study.contact.u)>1e-8: raise ValueError("successful hand/prop contact anchors differ")
    allowed={}
    for component in study.components:
        anchors=dict(component.anchors)
        if len(anchors)!=len(component.anchors): raise ValueError(f"duplicate anchor names on {component.name}")
        if any(not (_inside(point,component.outline) or _on_boundary(point,component.outline)) for point in anchors.values()):
            raise ValueError(f"anchor lies outside component solid: {component.name}")
        for target_name, own_anchor, target_anchor in component.attachments:
            if target_name not in by_name or own_anchor not in anchors:
                raise ValueError(f"unresolved attachment on {component.name}: {target_name}/{own_anchor}")
            other=by_name[target_name]; other_anchors=dict(other.anchors)
            if target_anchor not in other_anchors:
                raise ValueError(f"unresolved target anchor: {target_name}/{target_anchor}")
            own_world=component.support.local_to_world(anchors[own_anchor])
            target_world=other.support.local_to_world(other_anchors[target_anchor])
            if any(abs(a-b)>1e-8 for a,b in zip(own_world,target_world)):
                raise ValueError(f"attachment coordinates disagree: {component.name}/{target_name}")
            allowed.setdefault(frozenset((component.name,target_name)),[]).append(anchors[own_anchor])
    world_outlines={component.name:_world_xy_outline(component) for component in study.components}
    for i,a in enumerate(study.components):
        for b in study.components[i+1:]:
            outline_a,outline_b=world_outlines[a.name],world_outlines[b.name]
            samples=_overlap_samples(outline_a,outline_b)
            if not samples: continue
            pair=frozenset((a.name,b.name))
            if pair in allowed:
                anchors=[]
                for component in (a,b):
                    for target_name,own_anchor,_target_anchor in component.attachments:
                        if target_name in pair:
                            world=component.support.local_to_world(dict(component.anchors)[own_anchor])
                            anchors.append(Point(world[0],world[1]))
                if any(min(_point_distance(point,anchor) for anchor in anchors)>0.90 for point in samples):
                    raise ValueError(f"attachment overlap exceeds joint bound: {a.name}/{b.name}")
                continue
            depth_delta=[_world_z_at_xy(a.support,p)-_world_z_at_xy(b.support,p) for p in samples]
            if min(depth_delta)<=0 and max(depth_delta)>=0:
                raise ValueError(f"undeclared 3D surface intersection: {a.name}/{b.name}")
    return True
