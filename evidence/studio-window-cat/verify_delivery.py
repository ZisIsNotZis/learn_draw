"""Check this version-bound capability and study; deliberately award no artwork verdict."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,canonical,engine_fingerprint,select,node_by_id,accept
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.studio.render import global_depth_order
H=Path(__file__).resolve().parent
ENGINE='9a610ba4951fd3dca30c01c4a05a23bb36d52e1d2b96555cafeb64b2090ab305'
OLD='5d491f0d1630c7b1b84a2a657661e4450d548982b153759bbb6cba206e85a006'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def host_record(path):
 """Preserve raw PowerShell records; decode their declared BOM, never rewrite them."""
 raw=path.read_bytes()
 return json.loads(raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'))

def verify():
 assert engine_fingerprint()==ENGINE,'source changed; this study retains its actual epoch'
 manifest=read(H/'SHA256.json')
 actual={p.relative_to(H).as_posix() for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=H/'SHA256.json'}
 assert actual==set(manifest),'inventory changed'
 for name,digest in manifest.items():assert sha(H/name)==digest,name
 sources={str(p.relative_to(ROOT/'scripts')):p.read_text(encoding='utf8') for p in sorted((ROOT/'scripts/studio').glob('*.py'))}
 for name in ('vector_visibility.py','articulated_construction.py','renderer.py','relate.py','scene_render.py'):sources[name]=(ROOT/'scripts'/name).read_text(encoding='utf8')
 for name in ('placement','__main__'):sources[str(Path('studio')/(name+'.py'))]=(H/'source-history'/(name+'-before-pending-endpoints.py')).read_text(encoding='utf8')
 assert hashlib.sha256(canonical(sources).encode()).hexdigest()==OLD
 assert read(H/'tests-release/test-run.json')['exit_code']==0
 assert 'Ran 148 tests' in (H/'tests-release/tests.txt').read_text()
 preservation=read(H/'preservation-release/preservation.json');assert preservation['engine']==ENGINE and len(preservation['results'])==10
 for name,r in preservation['results'].items():assert r['prior_png_preserved'] and sha(H/'preservation-release'/f'{name}.png')==r['png_sha256']
 for p in H.glob('*-launch.json'):
  r=read(p);assert r['state']=='terminal' and r['exit_code']==0 and r['pid'] and r['started'] and r['terminal']
 canceled=read(H/'01-sketch/view/report.json');assert canceled['status']=='rendering' and canceled['images']==[]
 assert not (H/'01-sketch/view/artwork.png').exists()
 assert global_depth_order(read(H/'01-sketch/working.json')) is None # Do not restart the canceled ambiguous rendering.
 current=read(H/'working.json');assert current==read(ROOT/'examples/studio/window_cat.json')==read(H/'public-current-study/working.json')
 assert sha(H/'public-current-study/view/artwork.png')==sha(H/'53-tail-closer/artwork.png')
 for review in read(H/'reviews.json')['checks']:assert sha(H/review['bundle']/'draft-fullres.png')==review['png_sha256']
 actor=H/'usability';proof=host_record(actor/'recovery-proof.json')
 pairs=[('inputs/seed.json','undone.json','seed_sha256','undo_sha256'),('accepted-first.json','working.json','accepted_first_sha256','reaccepted_sha256'),
        ('04-right-mount/artwork.png','14-undone/artwork.png','seed_png_sha256','undo_png_sha256'),
        ('10-accepted/artwork.png','16-reaccepted/artwork.png','accepted_png_sha256','reaccepted_png_sha256')]
 for a,b,ha,hb in pairs:
  assert (actor/a).read_bytes()==(actor/b).read_bytes()
  assert sha(actor/a)==proof[ha].lower()==proof[hb].lower()
 proposal=read(actor/'08-refined/candidate.json');assert proposal['engine']==ENGINE and proposal['status']=='ready'
 assert proposal['scene']['nodes'][:-1]==read(actor/'inputs/seed.json')['nodes']
 assert len(proposal['scene']['nodes'])==24 and proof['original_nodes_unchanged']
 # Confirm real book contacts, including the parent's later underside correction.
 compiled=resolve_scene(current);cover=node_by_id(compiled,'book-cover');contacts=[]
 for end,parent,port in [('root','book-left','bottom@.95'),('tip','book-right','bottom@.05')]:
  a=get_anchor(cover,current['canvas'],end)['point'];b=get_anchor(node_by_id(compiled,parent),current['canvas'],port)['point']
  error=math.dist(a,b);assert error<1e-8;contacts.append(dict(end=end,parent=parent,port=port,error_pixels=error))
 # A local underside edit must preserve actual support/attachment points, not just labels.
 before=resolve_scene(read(H/'46-shared-coat/scene.json'));after=resolve_scene(read(H/'50-ground-haunch/scene.json'))
 for sid,ports in [('sleeping-body',('bottom','right','left')),('sleeping-head',('center',)),('tucked-tail',('root','tip'))]:
  for port in ports:
   a=get_anchor(node_by_id(before,sid),current['canvas'],port)['point'];b=get_anchor(node_by_id(after,sid),current['canvas'],port)['point'];assert math.dist(a,b)<1e-8,(sid,port)
 assert node_by_id(current,'tucked-tail')['depth']<node_by_id(current,'sleeping-body')['depth']<node_by_id(current,'sleeping-head')['depth']
 with tempfile.TemporaryDirectory() as tmp:
  file=Path(tmp)/'old.json';old=read(H/'03-supported-sketch/working.json');write(file,old)
  try:accept(file,read(H/'05-head-nest/candidate.json'))
  except ValueError as e:assert 'implementation changed' in str(e)
  else:raise AssertionError('old-source candidate accepted')
  assert read(file)==old
 return dict(engine=ENGINE,old_engine_reconstructed=OLD,digests=len(manifest),studio_tests=148,preserved_pngs=10,book_contacts=contacts,
             operator_recovery_byte_pairs=len(pairs),protected_haunch_mounts=True,scope='Mechanical/artifact capability only. Four image-review pairs retain unresolved cat anatomy; no whole-artwork/human acceptance.')

def child(command,cwd,out,tag):
 entry=dict(command=command,started=datetime.datetime.now(datetime.UTC).isoformat())
 p=subprocess.Popen(command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);entry['pid']=p.pid
 stdout,stderr=p.communicate();entry.update(exit_code=p.returncode,terminal=datetime.datetime.now(datetime.UTC).isoformat())
 (out/(tag+'-stdout.txt')).write_bytes(stdout);(out/(tag+'-stderr.txt')).write_bytes(stderr);write(out/(tag+'-run.json'),entry)
 assert p.returncode==0,stderr.decode(errors='replace')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--outdir',required=True);args=p.parse_args();out=Path(args.outdir).resolve()
 if out.exists():raise SystemExit('output exists; choose a fresh directory outside frozen evidence')
 result=verify();out.mkdir(parents=True)
 with tempfile.TemporaryDirectory() as cwd:
  child([sys.executable,str(ROOT/'examples/studio/window_cat.py'),'--outdir',str(out/'fresh-cwd-example')],cwd,out,'example')
  assert sha(out/'fresh-cwd-example/view/artwork.png')==sha(H/'53-tail-closer/artwork.png')
  audit="""import sys,hashlib
sys.path.insert(0,sys.argv[1])
def guard(event,args):
 if event=='open' and isinstance(args[0],str) and args[0].lower().endswith(('.jpg','.jpeg','.png','.svg','.glb')):raise RuntimeError('unexpected visual input')
sys.addaudithook(guard)
from examples.studio.window_cat import scene
from scripts.studio.render import drawing
svg=drawing(scene());assert '<image' not in svg
print(hashlib.sha256(svg.encode()).hexdigest())
"""
  child([sys.executable,'-c',audit,str(ROOT)],cwd,out,'reference-free')
  assert (out/'reference-free-stdout.txt').read_text().strip()==hashlib.sha256((H/'53-tail-closer/artwork.svg').read_text(encoding='utf8').encode()).hexdigest()
 result.update(fresh_cwd_png_exact=True,visual_input_audit_passed=True);write(out/'verification.json',result);print(result)
