"""Check actual direction edits, recovery, source transition and shipped study art.
Mechanical verification is distinct from the independent visual critiques.
"""
from pathlib import Path
import hashlib,json,re,sys,math
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,fingerprint,engine_fingerprint,node_by_id
from scripts.studio.attachment import resolve_scene
from scripts.studio.stroke import stroke_data
from scripts.studio.render import drawing,rasterize,global_depth_order
HERE=Path(__file__).resolve().parent
V1='10fe6d92b45bb1401ddc5f5c76cd9d2d175fa0e983422a3e682d5de2cb1c49b8'
CURRENT='46b8907650f18e1fb2b2f20e68bff94f3426bcf8781908d2f52d57519224eda2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashed(folder):
 hashes=read(folder/'artifact-sha256.json')
 external=hashes.pop('observed_external_inputs',{})
 if external:
  assert folder.name=='current-guide-review' and set(external)=={'alignment.png','object-closeup.png'}
  for name,digest in external.items():assert sha(HERE/'00b-small-guides-contrast'/name)==digest,name
 for name,digest in hashes.items():assert sha(folder/name)==digest,name
 return len(hashes)
def endpoints(scene):
 d=stroke_data(node_by_id(resolve_scene(scene),'reaching-sleeve'),scene['canvas'])
 return d.rows[0].spine,d.rows[-1].spine
if __name__=='__main__':
 assert engine_fingerprint()==CURRENT
 transition=read(HERE/'source-transition.json');assert transition['prior_engine']==V1 and transition['current_engine']==CURRENT and transition['exact_reconstructed_prior_engine']
 tests=(HERE/'verification-current/tests.txt').read_text();count=int(re.search(r'Ran (\d+) tests',tests).group(1));assert count==118 and tests.rstrip().endswith('OK')
 assert read(HERE/'verification-current/test-run.json')['exit_code']==0
 preserve=read(HERE/'verification-current/preservation.json');assert preserve['engine']==CURRENT and len(preserve['results'])==10 and all(r['prior_png_preserved'] for r in preserve['results'].values())
 before=read(HERE/'layered-working.json');c=read(HERE/'03-sleeve-aim/candidate.json');assert c['engine']==V1 and c['base']==fingerprint(before)
 changed=[(a['id'],[k for k in set(a)|set(b) if a.get(k)!=b.get(k)]) for a,b in zip(before['nodes'],c['scene']['nodes']) if a!=b]
 assert changed==[('reaching-sleeve',['bend'])]
 assert endpoints(before)==endpoints(c['scene'])
 assert read(HERE/'05-undone/scene.json')==before
 assert sha(HERE/'01b-sleeve-observe/artwork.png')==sha(HERE/'05-undone/artwork.png')
 assert sha(HERE/'03-sleeve-aim/artwork.png')==sha(HERE/'06-restored/artwork.png')
 assert sha(HERE/'16-current/artwork.png')==sha(HERE/'17-current-source/artwork.png')
 assert sha(HERE/'00-small-guides/artwork.png')==sha(HERE/'00b-small-guides-contrast/artwork.png')
 current_aim=read(HERE/'verification-current/aim/verification.json');assert current_aim['engine']==CURRENT and current_aim['clean_png_exact_to_v1'] and current_aim['working_unchanged'] and not current_aim['accepted']
 actor=HERE/'usability';actor_count=hashed(actor);assert actor_count==152
 actor_verify=read(actor/'verification.json');assert actor_verify['engine']==V1
 assert all(actor_verify[k] for k in ('undo_exact_canonical_scene','reaccept_exact_scene_bytes','undo_exact_png','reaccept_exact_png'))
 commands=[json.loads(line) for line in (actor/'commands.jsonl').read_text().splitlines()]
 spawned=[r['pid'] for r in commands if r['event']=='spawned'];terminal=[r for r in commands if r['event']=='terminal']
 assert len(spawned)==len(terminal)==17 and set(spawned)=={r['pid'] for r in terminal}
 assert sum(r['returncode']==2 for r in terminal)==1 and all(r['returncode'] in (0,2) for r in terminal)
 audit=read(actor/'process-audit.json');assert not audit['missing_terminal'] and audit['all_cli_terminal_outcomes_known']
 supplement=HERE/'current-guide-review';guide_count=hashed(supplement);assert guide_count==16
 assert read(supplement/'view/report.json')['engine']==CURRENT
 assert sha(supplement/'view/artwork.png')==actor_verify['final_image']
 scene=read(ROOT/'examples/studio/person_flower.json');assert scene==read(HERE/'working.json') and len(scene['nodes'])==17
 assert node_by_id(scene,'resting-arm')['attachment']['target']=='left@.77'
 assert global_depth_order(scene) is not None
 out=HERE/'verification-current';svg=out/'person-flower.svg';svg.write_text(drawing(scene),encoding='utf8');rasterize(svg,svg.with_suffix('.png'))
 assert sha(svg.with_suffix('.png'))==sha(HERE/'17-current-source/artwork.png')
 write(out/'delivery.json',dict(engine=CURRENT,operational_run_engine=V1,guide_only_source_transition_verified=True,
  studio_tests=count,prior_pngs_preserved=10,parent_fit_changed_only_bend=True,parent_fit_terminals_exact=True,
  actual_parent_undo_png_exact=True,actual_parent_reaccept_png_exact=True,current_aim_proposal_ready_and_same_clean_png=True,
  actor_artifacts_checked=actor_count,actor_commands_actual_terminal=17,actor_stale_refusals=1,
  actor_undo_and_reaccept_exact=True,current_guide_artifacts_checked=guide_count,current_guide_external_images_checked=2,current_guide_clean_png_unchanged=True,
  published_scene=fingerprint(scene),published_png=sha(svg.with_suffix('.png')),published_nodes=17,published_png_exact=True,
  canceled_equal_depth_candidate='recorded; no finished image claimed',human_whole_artwork_acceptance='unknown',whole_artwork_pass=False))
 print('Current direction delivery verified: 118 tests, 10 prior PNGs, actual recovery, 152+16 operator files and 2 external guide images and exact published study PNG.',flush=True)
