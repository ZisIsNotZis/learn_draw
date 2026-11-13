"""Hash this evidence tree, preserving nested manifests and excluding only own manifest/caches."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
if __name__=='__main__':
 paths=sorted(p for p in H.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=H/'SHA256.json')
 m={p.relative_to(H).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
 (H/'SHA256.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
 print(f'{H.name}: {len(m)} digests')
