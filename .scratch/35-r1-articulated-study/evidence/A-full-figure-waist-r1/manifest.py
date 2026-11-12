"""Bind current package and required project scripts; --check never writes."""
from pathlib import Path
import argparse,hashlib
p=Path(__file__).resolve().parent
root=p.parents[3]
a=argparse.ArgumentParser(); a.add_argument('--check',action='store_true'); args=a.parse_args()
files=sorted(f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='manifest.sha256')
files += [root/'scripts/articulated_construction.py',root/'scripts/vector_visibility.py']
import os
text=''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+Path(os.path.relpath(f,p)).as_posix()+'\n' for f in files)
manifest=p/'manifest.sha256'
if args.check:
    if not manifest.exists() or manifest.read_text(encoding='utf-8')!=text:
        raise SystemExit('manifest mismatch')
    print('manifest OK:',len(files),'files')
else:
    manifest.write_text(text,encoding='utf-8'); print('manifest bound:',len(files),'files')
