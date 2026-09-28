#!/usr/bin/env python3
"""Coarse seated figure: separate supported components, automatic vector depth.

A structural hypothesis, not a reconstruction of the reference or polished line art.
All surfaces are 3D; the stripe is 2D local art mapped onto ONE continuous ribbon.
"""
import argparse
import math
from pathlib import Path
from xml.sax.saxutils import escape

from vector_visibility import visible_fragments


def ellipsoid(name, center, radii, color, nu=20, nv=10, angle=0):
    ca, sa = math.cos(angle), math.sin(angle)
    cx, cy, cz = center
    rx, ry, rz = radii
    def point(i, j):
        lon = 2 * math.pi * i / nu
        lat = -math.pi / 2 + math.pi * j / nv
        x = rx * math.cos(lat) * math.cos(lon)
        y = ry * math.sin(lat)
        return (cx + ca*x - sa*y, cy + sa*x + ca*y,
                cz + rz * math.cos(lat) * math.sin(lon))
    for i in range(nu):
        for j in range(nv):
            p, q, r, s = point(i,j), point(i+1,j), point(i+1,j+1), point(i,j+1)
            yield (p,q,r), color, name
            yield (p,r,s), color, name


def hair_sheet():
    """One head-attached curved sheet; its normal twists blue→mint.

    Local (u,v): u flows from head, v crosses width. The support twists near
    its narrow root; view() chooses blue or mint by projected face orientation.
    This is a two-sided *hypothesis*, not yet a fit to the reference hair.
    """
    nu, nv = 20, 8
    def point(i,j):
        u, v = i/nu, 2*j/nv - 1
        width = 0.12 + 1.18 * math.sin(math.pi*u/2)
        twist = math.pi + math.pi*min(u/.28, 1.0)
        return (0.78 - 2.95*u,
                1.25 - 1.18*u + width*v*0.63*math.cos(twist)
                + 0.12*math.sin(math.pi*u),
                -0.48 + 0.20*math.cos(math.pi*u)
                + width*v*0.25*math.sin(twist) + 0.25*v*v)
    for i in range(nu):
        for j in range(nv):
            p,q,r,s = point(i,j),point(i+1,j),point(i+1,j+1),point(i,j+1)
            # Same geometric sheet; the reverse side has a different local paint.
            yield (p,q,r), '#83cbbd', 'hair-sheet'
            yield (p,r,s), '#83cbbd', 'hair-sheet'
    # The near blue lock is a separate named component attached at the same head.
    yield from ellipsoid('hair-fall', (1.19,0.47,0.70), (.23,1.04,.14), '#3974ab', 14,8, -.16)


def ribbon():
    """One continuous component, 2D stripes on a curved ring.

    t≈0.84 passes immediately below the bow, so the attachment is geometric,
    not an individually positioned visible ribbon tail.
    """
    n = 72
    def point(i,v):
        t=2*math.pi*i/n
        x=-.12+1.25*math.cos(t)
        y=-.46+.50*math.sin(t)+.13*math.sin(2*t)
        z=.18+.73*math.sin(t)
        return (x,y+v*.105*math.cos(t),z+v*.105*math.sin(t))
    for i in range(n):
        for a,b,color in ((-1,-.3,'#ca4b79'),(-.3,.3,'#e791a4'),(.3,1,'#ca4b79')):
            p,q,r,s=point(i,a),point(i+1,a),point(i+1,b),point(i,b)
            yield (p,q,r),color,'ribbon'
            yield (p,r,s),color,'ribbon'


def scene():
    # Back-to-front declaration is deliberately NOT relied on for visibility.
    yield from ribbon()
    yield from hair_sheet()
    yield from ellipsoid('lap',(-.30,-1.21,.00),(1.75,.50,.60),'#304d67',24,12)
    yield from ellipsoid('skirt',(.18,-.74,.37),(1.08,.56,.32),'#d4e5da',22,10,.17)
    yield from ellipsoid('torso',(.73,-.02,.12),(.62,.80,.34),'#e0eadc',20,10,-.13)
    yield from ellipsoid('arm-left',(.33,-.23,.53),(.18,.52,.18),'#e2eadd',12,8,-.40)
    yield from ellipsoid('arm-right',(1.26,-.50,.70),(.17,.68,.17),'#e0e9db',12,8,.35)
    yield from ellipsoid('hand',(1.40,-1.00,.78),(.21,.13,.11),'#f7e3cc',12,7)
    yield from ellipsoid('neck',(.82,.69,.35),(.22,.22,.19),'#f7e3cc',12,7)
    yield from ellipsoid('head',(.73,1.22,.50),(.46,.52,.35),'#f7e9d5',20,12)
    yield from ellipsoid('brim',(.66,1.65,.36),(1.18,.10,.59),'#5c9dab',28,5,-.10)
    yield from ellipsoid('crown',(.77,1.84,.39),(.49,.27,.43),'#344361',20,8)
    for x in (.25,1.15):
        yield from ellipsoid('hat-pom',(x,1.93,.62),(.13,.13,.12),'#e59ba9',10,6)
    for x in (.56,.95):
        yield from ellipsoid('eye',(x,1.27,.858),(.078,.051,.018),'#2f5279',10,6)
    yield from ellipsoid('bow',(.71,.24,.74),(.35,.21,.08),'#d54b83',14,8)


def project(p,yaw, ox):
    x,y,z=p
    a=math.radians(yaw)
    return (ox+235*(x*math.cos(a)+z*math.sin(a)),
            530-235*y, z*math.cos(a)-x*math.sin(a))


def view(yaw,ox):
    faces=[]
    for tri,color,name in scene():
        projected=[project(p,yaw,ox) for p in tri]
        if name == 'hair-sheet':
            a,b,c=projected
            orient=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            color='#3974ab' if orient < 0 else '#83cbbd'
        faces.append((projected,color,name))
    parts=[f'<text x="{ox-430}" y="42" font-size="24" fill="#243c53">'
           f'{escape(str(yaw))}° — coarse spatial hypothesis</text>']
    for frag,color,name in visible_fragments(faces):
        pts=' '.join(f'{x:.5f},{y:.5f}' for x,y,_ in frag)
        parts.append(f'<polygon points="{pts}" fill="{color}" stroke="{color}" '
                     f'stroke-width="0.22" data-component="{name}"/>')
    return '\n'.join(parts)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-o','--output',type=Path,required=True)
    args=ap.parse_args()
    svg=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 1024">'
         '<rect width="2048" height="1024" fill="#c7dade"/>'
         +view(0,510)+view(43,1530)
         +'<text x="32" y="1000" font-size="19" fill="#243c53">'
          'Component geometry is uncut; projected visibility is derived from depth. '
          'Pose, camera and ribbon route are hypotheses, not reference fits.'
          '</text></svg>')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(svg,encoding='utf-8')
    print(args.output)


if __name__=='__main__':
    main()
