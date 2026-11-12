"""CPU parameter study, not a studio candidate or a change to frozen source files."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scripts.studio.head as head
from scripts.studio.render import rasterize
from scripts.studio.model import engine_fingerprint

out=Path('evidence/studio-expression/lid-study');out.mkdir(exist_ok=False)
values=[None,-.42,-.2,0,.2,.4]
original=head.build_spec
pieces=[]
try:
    for i,value in enumerate(values):
        def spec(*args,**kwargs):
            result=original(*args,**kwargs)
            if value is not None:
                for part in result['draw']:
                    if part.get('eye')=='eye-left': part['lower-lid']=value
            return result
        head.build_spec=spec
        data=head.head_data(dict(id='study-'+str(i),kind='head',expression='gentle' if value is None else 'smile',
                                 at={'anchor':'center'},length=.65),[300,360])
        pieces.append(f'<g transform="translate({i*300} 0)">{data.svg}</g>')
        label='gentle default' if value is None else 'lower lid '+str(value)
        pieces.append(f'<text x="{i*300+150}" y="395" font-family="sans-serif" font-size="18" text-anchor="middle" fill="#493b40">{label}</text>')
finally:
    head.build_spec=original
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="420" viewBox="0 0 1800 420"><rect id="study-paper" width="1800" height="420" fill="#f5eee4"/>'+''.join(pieces)+'</svg>'
(out/'study.svg').write_text(svg,encoding='utf-8');rasterize(out/'study.svg',out/'study.png')
(out/'source.py').write_bytes(Path(__file__).read_bytes())
(out/'inputs.json').write_text(json.dumps(dict(values=values,engine=engine_fingerprint(),
 scope='isolated in-process specification parameter study; no frozen product source changed; no acceptance candidate',
 source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
print(out/'study.png')
