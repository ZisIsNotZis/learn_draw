"""Seal/check the two frozen grasp studies; integrity is not an artwork verdict."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
NAMES=('studio-grasp-contact','studio-grasp-glyph')
def entries(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'manifest.json'
        and '__pycache__' not in p.parts and p.suffix!='.pyc'}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seal',action='store_true',help='explicitly replace root manifests after an intentional study edit')
    args=parser.parse_args()
    for name in NAMES:
        folder=ROOT/'evidence'/name;current=entries(folder);dest=folder/'manifest.json'
        if args.seal:
            dest.write_text(json.dumps(dict(algorithm='sha256',scope='all files except this root manifest and Python caches; includes nested manifests',files=current),indent=2)+'\n',encoding='utf8')
        recorded=json.loads(dest.read_text(encoding='utf8'))['files']
        assert current==recorded,dict(study=name,missing=sorted(recorded.keys()-current.keys()),extra=sorted(current.keys()-recorded.keys()),changed=[k for k in current.keys()&recorded.keys() if current[k]!=recorded[k]])
        print(name,len(current),'file hashes verified',flush=True)
if __name__=='__main__':main()
