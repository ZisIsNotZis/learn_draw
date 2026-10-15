from pathlib import Path
from contact_primitive import ContactSpec, build_contact, render_sheet
from scripts.articulated_construction import Point, PalmAttachment, SupportFrame, Component

hand=SupportFrame("hand-plane","hand-depth",(0,0,0),(1,0,.025),(0,1,0))
def make(name, kind, opposition=True, generic=False):
    palm=Point(-.72,0); contact=Point(0,0)
    spec=ContactSpec(PalmAttachment(palm,Point(.94,.34),hand),contact,Point(1,0),Point(0,1),.31 if kind=="grip" else .38,.39 if kind=="grip" else .50,.12 if kind=="grip" else .16,opposition)
    components=build_contact(spec,prefix=name)
    if generic: components=components[:1]
    if kind=="grip":
        # Chamfered narrow upright cylinder-like vessel; visible rim and side wall.
        outline=(Point(0,-.34),Point(.30,-.34),Point(.37,-.27),Point(.37,.27),Point(.30,.34),Point(0,.34))
        intent="narrow chamfered cylinder prop with readable vertical side and rim"
    else:
        # Broad shallow rim/edge, a visibly planar ledge rather than a generic oval.
        outline=(Point(0,-.20),Point(.78,-.20),Point(.92,-.12),Point(.92,.12),Point(.78,.20),Point(0,.20))
        intent="broad flat rim edge with shallow thickness and long top boundary"
    prop_support=SupportFrame("prop-plane","prop-depth",(0,0,0),(1,0,.045),(0,1,0))
    prop=Component(name+"-prop",intent,prop_support,outline,"#bd8847",anchors=(("contact",Point(0,0)),))
    return name,components,prop

cases=(make("narrow-grip","grip"),make("wide-rim-pinch","rim"),make("generic-palm-control","grip",generic=True),make("opposition-disabled-gap","grip",opposition=False))
out=Path(__file__).parent/"contact-pair-sheet.svg"
render_sheet(cases,out)
print(out)
