"""Isolated specification study; never edits the frozen product implementation."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scripts.studio.head as head
from scripts.studio.render import rasterize
out=Path('evidence/studio-expression/curious-study');out.mkdir(exist_ok=False)
values=[(1,1),(1.22,1.12),(1.4,1.2),(1.55,1.25)]
original=head.build_spec;pieces=[]
try:
    for i,(upper,lower) in enumerate(values):
        def spec(*args,**kwargs):
            result=original(*args,**kwargs)
            if i:
                for part in result['draw']:
                    if part.get('eye')=='eye-left': part.update({'upper-lid':upper,'lower-lid':lower})
            return result
        head.build_spec=spec
        data=head.head_data(dict(id='curious-study-'+str(i),kind='head',expression='gentle' if i==0 else 'curious',
                                 at={'anchor':'center'},length=.65),[300,360])
        pieces.append(f'<g transform="translate({i*300} 0)">{data.svg}</g>')
        label='gentle' if not i else f'upper {upper}, lower {lower}'
        pieces.append(f'<text x="{i*300+150}" y="395" font-family="sans-serif" font-size="16" text-anchor="middle" fill="#493b40">{label}</text>')
finally:
    head.build_spec=original
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420"><rect id="study-paper" width="1200" height="420" fill="#f5eee4"/>'+''.join(pieces)+'</svg>'
(out/'study.svg').write_text(svg,encoding='utf-8');rasterize(out/'study.svg',out/'study.png')
(out/'source.py').write_bytes(Path(__file__).read_bytes())
(out/'inputs.json').write_text(json.dumps(dict(values=values,scope='isolated spec study, not a studio candidate'),indent=2)+'\n',encoding='utf-8')
print(out/'study.png')
