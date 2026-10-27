"""Sparse semantic-anchor cloth study; Catmull-Rom rule transferred from vendor R.smooth."""
from pathlib import Path

# Semantic anchors are local garment landmarks, not traced frame samples.
CASES = {
    "narrow": {"neck": (0, 0), "shoulder": (48, 8), "hem": (65, 108), "width": 32},
    "wide": {"neck": (0, 0), "shoulder": (58, 8), "hem": (79, 108), "width": 43},
}

def outline(a):
    n, s, h, w = a["neck"], a["shoulder"], a["hem"], a["width"]
    # derive outer and inner garment edge; only semantic anchors and width are authored.
    return [(n[0]-8,n[1]+8), (n[0],n[1]), s, (s[0]+w*.55,s[1]+28),
            (h[0]+w*.45,h[1]-12), (h[0],h[1]), (h[0]-w*.55,h[1]-7),
            (s[0]-w*.55,s[1]+25)]

def smooth_path(points, closed=True, k=.5):
    """Vendor R.smooth mechanism: Catmull-Rom tangents become cubic Bezier handles."""
    n=len(points)
    def p(i): return points[i % n] if closed else points[max(0,min(n-1,i))]
    d=[f'M {points[0][0]:.2f},{points[0][1]:.2f}']
    for i in range(n if closed else n-1):
        p0,p1,p2,p3=p(i-1),p(i),p(i+1),p(i+2)
        c1=(p1[0]+(p2[0]-p0[0])*k/6,p1[1]+(p2[1]-p0[1])*k/6)
        c2=(p2[0]-(p3[0]-p1[0])*k/6,p2[1]-(p3[1]-p1[1])*k/6)
        d.append(f'C {c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}')
    if closed: d.append('Z')
    return ' '.join(d)

def build_svg():
    panels=[]
    for col,(name,a) in enumerate(CASES.items()):
        pts=outline(a); x=col*310
        # Each panel contrasts the identical semantic outline as raw polygon vs smooth rule.
        poly=' '.join(f'{x+120+u*1.25:.1f},{35+v*1.25:.1f}' for u,v in pts)
        smooth=smooth_path([(x+120+u*1.25,35+v*1.25) for u,v in pts])
        panels += [f'<text x="{x+8}" y="20">{name}: same sparse garment anchors</text>',
          f'<polygon points="{poly}" transform="translate(0,0)" fill="#ddd" stroke="#554" stroke-width="2"/>',
          f'<path d="{smooth}" transform="translate(145,0)" fill="#7393ad" stroke="#263b4d" stroke-width="2"/>',
          f'<text x="{x+10}" y="245">polygon baseline</text><text x="{x+155}" y="245">R.smooth-generated</text>']
    return '<svg xmlns="http://www.w3.org/2000/svg" width="620" height="270" viewBox="0 0 620 270"><rect width="620" height="270" fill="#faf8f3"/>'+''.join(panels)+'</svg>'

if __name__ == '__main__':
    Path(__file__).with_name('study.svg').write_text(build_svg())
