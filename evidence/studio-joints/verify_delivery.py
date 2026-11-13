"""Verify frame/direction delivery, historical source boundaries and current public examples."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,canonical,engine_fingerprint,accept
from scripts.studio.attachment import resolve_scene,get_anchor,anchor_direction
from scripts.studio.grip import grip_data
H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def j(p):return read(H/p)
def h(p):return sha((H/p).read_bytes())
def joins(scene):
 placed=resolve_scene(scene);by={n['id']:n for n in placed['nodes']};rows=[]
 for n in scene['nodes']:
  r=n.get('attachment',{})
  if not r or r.get('offset') or r.get('inset'):continue
  a=get_anchor(by[n['id']],scene['canvas'],r.get('self','center'));b=get_anchor(by[r['to']],scene['canvas'],r.get('target','center'));error=math.dist(a['point'],b['point']);assert error<1e-8,(n['id'],error)
  row=dict(object=n['id'],point_error_pixels=error)
  if r.get('orient'):
   row['direction_dot']=sum(x*y for x,y in zip(anchor_direction(a),anchor_direction(b)));assert row['direction_dot']<-1+1e-9
   assert 'angle' not in n
  rows.append(row)
 return rows

def frozen():
 v=j('usability/verification.json');assert all(v['checks'].values());assert v['cli_count']==28 and v['engine']=='58b302be5e3866dd5569788756fbe387a1b1909292fd6b93330295c65a927548'
 for p in v['processes']:assert p['exit']==0 and p['pid'] and p['start'] and p['terminal']
 m=j('usability/SHA256.json');assert len(m)==259
 for name,digest in m.items():assert sha((H/'usability'/name).read_bytes())==digest,name
 assert (H/'usability/pre-move.json').read_bytes()==(H/'usability/undone.json').read_bytes()
 assert (H/'usability/accepted.json').read_bytes()==(H/'usability/working.json').read_bytes()
 assert h('actor-release/artwork.png')==h('usability/reaccepted-wrist/artwork.png')
 actor=joins(j('usability/working.json'));greeting=joins(j('working.json'));assert sum('direction_dot'in x for x in actor)==3;assert sum('direction_dot'in x for x in greeting)==4
 assert read(ROOT/'examples/studio/greeting.json')==j('working.json')==j('24-final/scene.json')
 assert j('tests-release/test-run.json')['exit_code']==0;assert 'Ran 138 tests' in (H/'tests-release/tests.txt').read_text()
 assert j('targeted/run.json')['exit_code']==0 and 'Ran 10 tests' in (H/'targeted/stderr.txt').read_text()
 p=j('preservation-release/preservation.json');assert p['engine']==engine_fingerprint()
 for name,r in p['results'].items():assert r['prior_png_preserved'] and h('preservation-release/'+name+'.png')==r['png_sha256']
 # Reconstruct the actual pre-guard engine used by the independent operator.
 directory=ROOT/'scripts/studio';sources={str(p.relative_to(directory.parent)):p.read_text(encoding='utf8') for p in sorted(directory.glob('*.py'))}
 for name in ('vector_visibility.py','articulated_construction.py','renderer.py','relate.py','scene_render.py'):sources[name]=(directory.parent/name).read_text(encoding='utf8')
 assert sha(canonical(sources).encode())==engine_fingerprint()
 sources[str(Path('studio')/'head.py')]=(H/'source-history/head-before-frame-comment-guard.py').read_text(encoding='utf8')
 assert sha(canonical(sources).encode())=='44a0803cbce094ef14ddd8b298b0d1797b4544498b2891066d085e3d2c68770f'
 sources[str(Path('studio')/'model.py')]=(H/'source-history/model-before-legacy-lock-guard.py').read_text(encoding='utf8');assert sha(canonical(sources).encode())==v['engine']
 for name in ('model.py','__main__.py','render.py'):sources[str(Path('studio')/name)]=(H/'source-history'/name.replace('.py','-before-final-feedback.py')).read_text(encoding='utf8')
 assert sha(canonical(sources).encode())=='fb839161a044e6e137f0110dfb18495ea914eaba267b59406ce0ea1d8260e81e'
 for path in H.glob('*-launch.json'):
  r=read(path);assert r['state']=='terminal' and r['exit_code']==0
 with tempfile.TemporaryDirectory() as d:
  file=Path(d)/'legacy.json';initial=j('01-head/scene.json');write(file,initial)
  try:accept(file,j('03-head-fit/candidate.json'))
  except ValueError:pass
  else:raise AssertionError('old-engine candidate accepted')
  assert read(file)==initial
 return dict(engine=engine_fingerprint(),operator_engine=v['engine'],operator_digests=len(m),actor_current_png_exact=True,actor_joins=actor,greeting_joins=greeting,protocol_exception=v['protocol_exception'],scope='Old operator facts remain pre-guard; current source reconstruction adds legacy attached-head edit refusal and safe XML comments for double-hyphen IDs. Root repairs and current public replays are separately bound.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--outdir',required=True);a=p.parse_args();out=Path(a.outdir).resolve()
 if out.exists():raise SystemExit('output exists')
 out.mkdir(parents=True);result=frozen();runs=[]
 with tempfile.TemporaryDirectory() as empty:
  for name,args in [('offering',['--pose','offering']),('folded',['--pose','folded']),('greeting',['--scene','greeting'])]:
   command=[sys.executable,str(ROOT/'examples/studio/upper_body.py'),*args,'--outdir',str(out/name)];record=dict(command=command,cwd=empty,started=datetime.datetime.now(datetime.UTC).isoformat());write(out/(name+'-launch.json'),record)
   child=subprocess.Popen(command,cwd=empty,stdout=subprocess.PIPE,stderr=subprocess.PIPE);record['pid']=child.pid;write(out/(name+'-launch.json'),record);stdout,stderr=child.communicate();(out/(name+'-stdout.txt')).write_bytes(stdout);(out/(name+'-stderr.txt')).write_bytes(stderr);record.update(exit_code=child.returncode,terminal=datetime.datetime.now(datetime.UTC).isoformat());write(out/(name+'-launch.json'),record)
   assert child.returncode==0,stderr;scene=read(out/name/'working.json');report=read(out/name/'view/report.json');assert report['engine']==engine_fingerprint();row=dict(name=name,revision=report['revision'],joins=joins(scene),png_sha256=sha((out/name/'view/artwork.png').read_bytes()))
   if name=='greeting':assert scene==j('working.json');assert row['png_sha256']==h('24-final/artwork.png')
   else:
    placed=resolve_scene(scene);hand=next(n for n in placed['nodes'] if n['id']=='flower-hand');width=grip_data(hand,scene['canvas']).dimensions['handle_thickness']
    for sid in ('upper-stem','lower-stem'):assert abs(next(n for n in placed['nodes'] if n['id']==sid)['thickness']*min(scene['canvas'])-width)<1e-9
   runs.append(row)
 result['public_examples']=runs;write(out/'verification.json',result);print('Current frame/direction examples and frozen operation evidence verified; no whole-artwork claim.',flush=True)
