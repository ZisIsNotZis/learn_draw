"""One relational opposing-contact silhouette probe on existing support geometry."""
from __future__ import annotations
from dataclasses import dataclass
import math
from scripts.articulated_construction import Point, PalmAttachment, SupportFrame, Component, Camera, component_faces
from scripts.vector_visibility import visible_regions
from scripts.articulated_line_visibility import visible_segment_spans

@dataclass(frozen=True)
class ContactSpec:
    palm: PalmAttachment
    prop_contact: Point
    approach: Point
    opening: Point
    palm_half_width: float
    thumb_reach: float
    band_thickness: float
    opposition: bool = True

def _unit(p):
    n=math.hypot(p.u,p.v)
    if not math.isfinite(n) or n<=1e-10: raise ValueError("contact direction is degenerate")
    return Point(p.u/n,p.v/n)
def _add(a,b): return Point(a.u+b.u,a.v+b.v)
def _mul(a,s): return Point(a.u*s,a.v*s)
def _sub(a,b): return Point(a.u-b.u,a.v-b.v)
def _finite(p): return math.isfinite(p.u) and math.isfinite(p.v)
def _poly(name,intent,support,points,fill,anchors=()):
    return Component(name,intent,support,tuple(points),fill,anchors=anchors)

def build_contact(spec: ContactSpec, prefix="hand", skin="#d99872"):
    """Generate palm, opposed thumb wedge and grouped finger band from semantic anchors."""
    if not _finite(spec.palm.origin) or not _finite(spec.palm.tangent) or not _finite(spec.prop_contact) or not _finite(spec.approach) or not _finite(spec.opening):
        raise ValueError("contact inputs must be finite")
    values=(spec.palm_half_width,spec.thumb_reach,spec.band_thickness)
    if not all(math.isfinite(x) and x>0 for x in values): raise ValueError("contact proportions must be positive finite")
    support=spec.palm.support
    tangent=_unit(spec.palm.tangent); approach=_unit(spec.approach); opening=_unit(spec.opening)
    if abs(tangent.u*approach.v-tangent.v*approach.u)<1e-4: raise ValueError("wrist tangent and approach must define a reachable side contact")
    if abs(approach.u*opening.u+approach.v*opening.v)>.25: raise ValueError("opening direction must be distinct from approach")
    origin=spec.palm.origin; half=spec.palm_half_width; thick=spec.band_thickness
    # Palm is anchored at wrist; remaining contour follows two anatomical axes.
    palm=(_add(origin,_mul(tangent,-.25*half)),_add(_add(origin,_mul(tangent,.8*half)),_mul(opening,half)),_add(_add(origin,_mul(tangent,1.7*half)),_mul(opening,.35*half)),_add(origin,_mul(tangent,1.7*half)),_add(_add(origin,_mul(tangent,.8*half)),_mul(opening,-half)),_add(_add(origin,_mul(tangent,-.25*half)),_mul(opening,-.65*half)))
    # Prop contact is the shared tip; wrist-side root and opening offset derive the wedge.
    root=_add(spec.prop_contact,_mul(approach,-spec.thumb_reach))
    thumb=(root,_add(root,_mul(opening,-thick)),_add(spec.prop_contact,_mul(opening,-.45*thick)),spec.prop_contact) if spec.opposition else ()
    # One band mass uses only ends derived from contact and opening axis, not finger stations.
    band_root=_add(origin,_mul(tangent,.65*half))
    band_tip=_sub(spec.prop_contact,_mul(approach,.15*thick))
    band=(band_root,_add(band_root,_mul(opening,thick)),_add(band_tip,_mul(opening,thick)),band_tip)
    components=[_poly(prefix+"-palm","palm mass attached at wrist",support,palm,skin,(("wrist",origin),))]
    if spec.opposition:
        components.extend((_poly(prefix+"-thumb","opposing thumb wedge closes at prop contact",support,thumb,skin,(("contact",spec.prop_contact),)),_poly(prefix+"-finger-band","grouped opposing finger band leaves an opening",support,band,skin,(("contact",spec.prop_contact),))))
    else:
        # Explicit near-miss is the same palm/band recipe shifted away from contact.
        near=tuple(_add(p,_mul(approach,-.32*half)) for p in band)
        components.append(_poly(prefix+"-finger-band","non-opposing finger band leaves a positive gap",support,near,skin))
    return tuple(components)

def render_sheet(cases, output):
    """Depth-render named fills and depth-clipped semantic contact strokes to a fixed SVG."""
    width,height=960,360; panels=[]; face_sets=[]
    for index,(label,components,prop) in enumerate(cases):
        camera=Camera(); faces=component_faces((*components,prop),camera); face_sets.append(faces)
        paths=[]
        for path,fill,name in visible_regions(faces):
            paths.append(f'<path id="{name}" d="{path}" fill="{fill}" fill-rule="nonzero"/>')
        # Named semantic boundaries; engine-derived spans, never hand-cut visibility intervals.
        for comp in (*components,prop):
            for a,b in zip(comp.outline,comp.outline[1:]+comp.outline[:1]):
                q0=camera.project(comp.support.local_to_world(a)); q1=camera.project(comp.support.local_to_world(b))
                for lo,hi in visible_segment_spans(q0,q1,faces,comp.name):
                    p0=tuple(q0[j]+(q1[j]-q0[j])*lo for j in range(3)); p1=tuple(q0[j]+(q1[j]-q0[j])*hi for j in range(3))
                    paths.append(f'<path data-owner="{comp.name}" d="M {p0[0]:.4f} {p0[1]:.4f} L {p1[0]:.4f} {p1[1]:.4f}" fill="none" stroke="#493a35" stroke-width=".025"/>')
        tx=index*240+120; ty=180
        panels.append(f'<g transform="translate({tx},{ty})"><g transform="scale(75,-75)">'+''.join(paths)+f'</g><text x="-95" y="-135" font-size="14" transform="scale(1,-1)">{label}</text></g>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#f8f5ef"/>'+''.join(panels)+'</svg>'
    output.write_text(svg)
    return svg
