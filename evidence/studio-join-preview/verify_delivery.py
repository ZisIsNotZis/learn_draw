"""Verify the current paired-join unit without rewriting historical study evidence."""
from pathlib import Path
import argparse,hashlib,math,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,engine_fingerprint,accept
from scripts.studio.attachment import resolve_scene,get_anchor,anchor_direction
from scripts.studio.render import drawing,rasterize
H=Path(__file__).resolve().parent
ENGINE='5d491f0d1630c7b1b84a2a657661e4450d548982b153759bbb6cba206e85a006'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def joints(scene):
 placed=resolve_scene(scene);by={n['id']:n for n in placed['nodes']};rows=[]
 for n in scene['nodes']:
  r=n.get('attachment',{})
  if not r:continue
  a=get_anchor(by[n['id']],scene['canvas'],r.get('self','center'));b=get_anchor(by[r['to']],scene['canvas'],r.get('target','center'))
  # These study scenes use exact, zero-inset pins, not arbitrary contact patches.
  assert not r.get('inset') and not r.get('offset')
  error=math.dist(a['point'],b['point']);assert error<1e-8,(n['id'],error)
  row=dict(object=n['id'],point_error_pixels=error)
  if r.get('orient'):
   row['direction_dot']=sum(x*y for x,y in zip(anchor_direction(a),anchor_direction(b)));assert row['direction_dot']<-1+1e-9
  rows.append(row)
 return rows

def verify():
 assert engine_fingerprint()==ENGINE,'source changed; this is a version-bound study'
 m=read(H/'SHA256.json')
 paths={p.relative_to(H).as_posix() for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=H/'SHA256.json'}
 assert set(m)==paths,'evidence inventory changed'
 for name,digest in m.items():assert sha(H/name)==digest,name
 assert read(H/'tests-release/test-run.json')['exit_code']==0
 assert 'Ran 144 tests' in (H/'tests-release/tests.txt').read_text()
 preservation=read(H/'preservation-release/preservation.json');assert preservation['engine']==ENGINE and len(preservation['results'])==10
 for name,r in preservation['results'].items():assert r['prior_png_preserved'] and sha(H/'preservation-release'/f'{name}.png')==r['png_sha256']
 for p in H.glob('*-launch.json'):
  r=read(p);assert r['state']=='terminal' and r['exit_code']==0 and r['pid'] and r['started'] and r['terminal']
 current=read(H/'working.json');assert current==read(ROOT/'examples/studio/greeting.json')==read(H/'public-greeting/working.json')
 assert sha(H/'public-greeting/view/artwork.png')==sha(H/'14-elbow-rise/artwork.png')
 # Verify local cuff and elbow promises from compiled geometry, not their labels.
 raised=resolve_scene(read(H/'04-wave/scene.json'));cuffed=resolve_scene(read(H/'11-resting-taper/scene.json'));final=resolve_scene(current)
 for a,b in ((raised,cuffed),(cuffed,final)):
  for port in ('neck','right-shoulder','right-wrist','left-shoulder','left-wrist'):
   pa=get_anchor(a['nodes'][0],a['canvas'],port)['point'];pb=get_anchor(b['nodes'][0],b['canvas'],port)['point'];assert math.dist(pa,pb)<1e-8,port
 for check in read(H/'reviews.json')['checks']:assert sha(H/check['bundle']/'draft-fullres.png')==check['sha256']
 actor=H/'usability';recovery=read(actor/'recovery.json')
 for row in recovery.values():
  assert row['byte_equal'] and (actor/row['left']).read_bytes()==(actor/row['right']).read_bytes()
  assert sha(actor/row['left'])==row['left_sha256']==row['right_sha256']
 joined=read(actor/'10-joined/report.json');assert joined['status']=='ready' and joined['engine']==ENGINE
 assert len(joined['images'])==6 and joined['join']['pending'] and joined['join']['mode']=='point'
 assert read(actor/'17-stale/candidate.json')['status']=='preparing'
 assert read(actor/'working.json')==read(actor/'accepted-prop.json')
 for dirname in ('03-wave','06-taper','10-joined','12-accepted','14-undone','16-reaccepted'):
  assert read(actor/dirname/'report.json')['engine']==ENGINE
 with tempfile.TemporaryDirectory() as tmp:
  tmp=Path(tmp);old=tmp/'old.json';write(old,read(H/'03-current-body/scene.json'))
  try:accept(old,read(H/'04-wave/candidate.json'))
  except ValueError as e:assert 'implementation changed' in str(e)
  else:raise AssertionError('pre-cuff-clip source candidate accepted')
  svg=tmp/'current.svg';svg.write_text(drawing(current),encoding='utf8');rasterize(svg,tmp/'current.png')
  assert sha(tmp/'current.png')==sha(H/'public-greeting/view/artwork.png')
 return dict(engine=ENGINE,digests=len(m),studio_tests=144,preserved_pngs=10,greeting_joins=joints(current),operator_joins=joints(read(actor/'working.json')),operator_recovery_byte_comparisons=len(recovery),current_public_png_exact=True,
             scope='Current code/artifacts only. Earlier source-bound studies keep their original epochs; no whole-artwork or human acceptance claim.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--outdir',required=True);args=p.parse_args();out=Path(args.outdir)
 if out.exists():raise SystemExit('output exists; choose a fresh directory')
 result=verify();out.mkdir(parents=True);write(out/'verification.json',result);print(result)
