"""Study-only shared-material underpaint using exact computed winner regions; no cuts/expansion."""
from pathlib import Path
import sys,re,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,canonical,write,engine_fingerprint
from scripts.studio.render import drawing,_scene_regions
from scripts.studio.attachment import resolve_scene
import resvg_py
if __name__=='__main__':
 out=Path(sys.argv[1]).resolve()
 if out.exists():raise SystemExit('output exists')
 out.mkdir(parents=True)
 s=read(ROOT/'evidence/studio-body/04-occlusion/sloped/working.json');before=drawing(s)
 regions=_scene_regions(canonical(resolve_scene(s)));d=' '.join(p for p,c,name in regions if name.startswith('upper-body.plane-'))
 base=f'<path id="shared-cloth-base-study" d="{d}" fill="#6c8d98"/>'
 after=re.sub(r'(<rect id="paper"[^>]*/>)',lambda m:m[1]+base,before,count=1)
 for name,svg in [('before',before),('after',after)]:
  (out/(name+'.svg')).write_text(svg,encoding='utf8');(out/(name+'.png')).write_bytes(resvg_py.svg_to_bytes(svg_string=svg))
 write(out/'report.json',dict(status='study-only',host_engine=engine_fingerprint(),mechanism='One shared material fill from union-by-compound-path of existing depth winner regions; no visibility boundary expansion or depth changes'))
 print('Shared material underpaint study completed',flush=True)
