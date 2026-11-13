"""Run the complete package-named studio suite, retaining raw child streams."""
from pathlib import Path
import subprocess,sys,json,argparse
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--outdir');args=parser.parse_args()
 out=Path(args.outdir) if args.outdir else HERE
 if args.outdir:
  if out.exists():raise SystemExit('test output exists; preserve earlier verification')
  out.mkdir(parents=True)
 command=[sys.executable,str(ROOT/'evidence/studio-grasp-glyph/run_tests.py')]
 p=subprocess.run(command,cwd=ROOT,capture_output=True)
 (out/'tests-stdout.txt').write_bytes(p.stdout);(out/'tests.txt').write_bytes(p.stderr)
 (out/'test-run.json').write_text(json.dumps(dict(command=command,exit_code=p.returncode),indent=2)+'\n',encoding='utf8')
 print(p.stderr.decode('utf8',errors='replace')[-180:],flush=True)
 raise SystemExit(p.returncode)
