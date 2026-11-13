"""Run one real CLI operation, retaining process identity and exact streams."""
from pathlib import Path
import datetime,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from scripts.studio.model import write
if __name__=='__main__':
 tag=sys.argv[1];command=[sys.executable,'-m','scripts.studio',*sys.argv[2:]]
 log=H/(tag+'-launch.json')
 if log.exists():raise SystemExit('operation record exists')
 entry=dict(command=command,started=datetime.datetime.now(datetime.UTC).isoformat(),state='starting');write(log,entry)
 child=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE);entry.update(pid=child.pid,state='running');write(log,entry)
 stdout,stderr=child.communicate();(H/(tag+'-stdout.txt')).write_bytes(stdout);(H/(tag+'-stderr.txt')).write_bytes(stderr)
 entry.update(state='terminal',exit_code=child.returncode,terminal=datetime.datetime.now(datetime.UTC).isoformat());write(log,entry)
 try:r=json.loads(stdout)
 except ValueError:r={}
 print(json.dumps(dict(tag=tag,state=entry['state'],exit_code=child.returncode,images=r.get('images'),selection=r.get('selection'),selected=r.get('selected'),files=r.get('files'))),flush=True)
 if stderr:print(stderr.decode(errors='replace'),file=sys.stderr)
 raise SystemExit(child.returncode)
