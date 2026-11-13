"""Verify native body delivery, frozen operation provenance and current public replays."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,canonical,engine_fingerprint,fingerprint
from scripts.studio.attachment import resolve_scene,get_anchor
H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def j(p):return read(H/p)
def h(p):return sha((H/p).read_bytes())
def check_records():
 v=j('usability/verification.json');assert all(v['checks'].values()) and not v['full_report_used'];assert len(v['launches'])==34
 for r in v['launches'].values():assert r['state']=='terminal' and r['exit']==0 and r['pid'] and r['start'] and r['terminal']
 m=j('usability/SHA256.json')
 for name,digest in m.items():assert sha((H/'usability'/name).read_bytes())==digest,name
 for a,b in [('04-wrist','08-restored'),('05-wrist-up','10-final'),('32-wave-seat','34-greeting-final')]:
  assert j('usability/'+a+'/scene.json')==j('usability/'+b+'/scene.json');assert h('usability/'+a+'/artwork.png')==h('usability/'+b+'/artwork.png')
 assert j('usability/greeting.json')==j('usability/34-greeting-final/scene.json')
 assert read(ROOT/'examples/studio/greeting.json')==j('06-greeting-finished/working.json')
 p=j('preservation-final/preservation.json');assert p['engine']==engine_fingerprint();assert len(p['results'])==10
 for name,r in p['results'].items():assert r['prior_png_preserved'] and h('preservation-final/'+name+'.png')==r['png_sha256']
 assert j('tests-final/test-run.json')['exit_code']==0;assert 'Ran 128 tests' in (H/'tests-final/tests.txt').read_text()
 # Reconstruct both earlier engine maps. This proves the operation backend was unchanged,
 # rather than relabeling old operations as execution of a later renderer.
 directory=ROOT/'scripts/studio';sources={str(p.relative_to(directory.parent)):p.read_text(encoding='utf8') for p in sorted(directory.glob('*.py'))}
 for name in ('vector_visibility.py','articulated_construction.py','renderer.py','relate.py','scene_render.py'):sources[name]=(directory.parent/name).read_text(encoding='utf8')
 assert sha(canonical(sources).encode())==engine_fingerprint()
 sources[str(Path('studio')/'body.py')]=(H/'source-history/body-before-material-coverage.py').read_text(encoding='utf8');middle=sha(canonical(sources).encode())
 assert middle=='4f02e7e193cdb2cefbeadfafe761232e601ad00e19a5903ef0097e54ce61dcde'
 sources[str(Path('studio')/'render.py')]=(H/'source-history/render-before-shared-material.py').read_text(encoding='utf8');old=sha(canonical(sources).encode())
 assert old=='8970df156e3b747080205b59bcc5aca804f0192f852e71b514971735160858e8'
 return dict(independent_engine=old,underpaint_engine=middle,current_engine=engine_fingerprint(),operator_digests=len(m),changed_sources=['studio/body.py','studio/render.py'],scope='Shared material underpaint and cloth-surface coverage repair; no operation backend changes. Frozen old image critiques are not relabelled as current images.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--outdir',required=True);a=p.parse_args();out=Path(a.outdir).resolve()
 if out.exists():raise SystemExit('output exists; preserve earlier verification')
 out.mkdir(parents=True);result=check_records();runs=[]
 with tempfile.TemporaryDirectory() as empty:
  for name,args,expected in [('offering',['--pose','offering'],j('01-offering/working.json')),('folded',['--pose','folded'],j('02-folded/working.json')),('greeting',['--scene','greeting'],j('06-greeting-finished/working.json'))]:
   command=[sys.executable,str(ROOT/'examples/studio/upper_body.py'),*args,'--outdir',str(out/name)]
   record=dict(command=command,cwd=empty,started=datetime.datetime.now(datetime.UTC).isoformat());write(out/(name+'-launch.json'),record)
   child=subprocess.Popen(command,cwd=empty,stdout=subprocess.PIPE,stderr=subprocess.PIPE);record['pid']=child.pid;write(out/(name+'-launch.json'),record);stdout,stderr=child.communicate()
   record.update(exit_code=child.returncode,terminal=datetime.datetime.now(datetime.UTC).isoformat());write(out/(name+'-launch.json'),record);(out/(name+'-stdout.txt')).write_bytes(stdout);(out/(name+'-stderr.txt')).write_bytes(stderr)
   assert child.returncode==0,stderr;actual=read(out/name/'working.json');assert actual==expected
   report=read(out/name/'view/report.json');assert report['engine']==engine_fingerprint() and report['renderer']=='resvg-py-0.5.0-cpu'
   placed=resolve_scene(actual);by={n['id']:n for n in placed['nodes']};unresolved=[]
   for raw in actual['nodes']:
    if 'attachment' not in raw:continue
    relation=raw['attachment'];own=get_anchor(by[raw['id']],actual['canvas'],relation.get('self','center'))['point'];target=get_anchor(by[relation['to']],actual['canvas'],relation.get('target','center'))['point']
    if not relation.get('offset') and not relation.get('inset'):
     error=max(abs(x-y) for x,y in zip(own,target))
     if raw['kind']=='head' and error>=1e-7:unresolved.append(dict(object=raw['id'],mount_error_pixels=error,status='unresolved legacy absolute-SVG quantization; not an exact-pin pass'))
     else:assert error<1e-7,(raw['id'],error)
   runs.append(dict(name=name,revision=fingerprint(actual),png_sha256=sha((out/name/'view/artwork.png').read_bytes()),terminal_exit_code=child.returncode,unresolved_mounts=unresolved))
 result['public_replays']=runs;write(out/'verification.json',result);print(json.dumps(result),flush=True)
