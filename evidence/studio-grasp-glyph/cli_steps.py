"""Small recorder for public-CLI drawing demonstrations; no engine bypass."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]

class Recorder:
    def __init__(self,path):self.path=Path(path);self.records=[]
    def run(self,*args):
        argv=[sys.executable,'-m','scripts.studio',*map(str,args)]
        result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True)
        self.records.append(dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
        self.path.write_text(json.dumps(self.records,indent=2),encoding='utf8')
        if result.returncode:raise RuntimeError(result.stderr or result.stdout)
        return result.stdout
