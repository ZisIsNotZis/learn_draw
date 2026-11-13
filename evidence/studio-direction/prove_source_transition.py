"""Reconstruct the pre-halo engine and verify that the later change is guide-only.
Reconstructed source is labeled as such, not claimed to have been captured earlier.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import canonical,engine_fingerprint,write
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 directory=ROOT/'scripts/studio'
 sources={str(p.relative_to(directory.parent)):p.read_text(encoding='utf8') for p in sorted(directory.glob('*.py'))}
 for name in ('vector_visibility.py','articulated_construction.py','renderer.py','relate.py','scene_render.py'):
  sources[name]=(directory.parent/name).read_text(encoding='utf8')
 current=hashlib.sha256(canonical(sources).encode()).hexdigest()
 assert current==engine_fingerprint()=='46b8907650f18e1fb2b2f20e68bff94f3426bcf8781908d2f52d57519224eda2'
 diff=json.loads((HERE/'halo-diff.json').read_text());key=str(Path('studio')/'render.py');render=sources[key]
 assert render.count(diff['after'])==1
 old=render.replace(diff['after'],diff['before']);sources[key]=old
 prior=hashlib.sha256(canonical(sources).encode()).hexdigest()
 assert prior=='10fe6d92b45bb1401ddc5f5c76cd9d2d175fa0e983422a3e682d5de2cb1c49b8'
 history=HERE/'source-history';history.mkdir(exist_ok=True)
 (history/'render-v1-reconstructed.py').write_text(old,encoding='utf8')
 write(HERE/'source-transition.json',dict(prior_engine=prior,current_engine=current,
     exact_reconstructed_prior_engine=True,only_changed_module='studio/render.py',
     change='white underlay behind inspection direction arrows; clean artwork and alignment/model logic unchanged',
     reconstructed_source='source-history/render-v1-reconstructed.py'))
 print('Exact v1 engine reconstructed; only inspection-arrow halo changed.',flush=True)
