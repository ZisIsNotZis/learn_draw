"""Verify evidence integrity and import mechanics; this is not an art pass."""
from pathlib import Path
import hashlib,json,runpy,sys,xml.etree.ElementTree as ET
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
HERE=Path(__file__).resolve().parent
from scripts.studio.model import engine_fingerprint

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    expected='4e070f369e44fec419b2be5b1bcb71094a1da3b83da8475e3baaafa9caa4c4b9'
    assert engine_fingerprint()==expected, 'this study must not silently change production defaults'
    manifest=HERE/'manifest.json'
    if manifest.exists():
        frozen=json.loads(manifest.read_text())['files']
        for record in frozen:
            p=HERE/record['path']
            assert p.stat().st_size==record['bytes'] and sha(p)==record['sha256'], record['path']
        actual={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts and p.suffix!='.pyc'}
        assert actual=={r['path'] for r in frozen}, 'manifest must account for the complete frozen study'
    folder=HERE/'third-party/webxr-generic-hand-1.0.20'
    for record in json.loads((folder/'provenance.json').read_text())['files']:
        assert sha(folder/record['file'])==record['sha256']
    pairs=[('04-exterior-ink/palm.png','palm-check'),('04-exterior-ink/back-carry.png','back-check'),
           ('07-exterior-contact/palm.png','palm-07-check'),('09-thumb-side-camera/thumb-palm.png','thumb-check'),
           ('11-mesh-contact-contours/closed.png','mesh-check')]
    for source,bundle in pairs:
        assert (HERE/source).read_bytes()==(HERE/bundle/'draft-fullres.png').read_bytes()
    svgs=list(HERE.glob('*/*.svg'))
    for p in svgs:ET.parse(p)
    module=runpy.run_path(str(HERE/'probe_webxr.py'))
    data=module['load']();v,n,posed=module['pose'](data,True)
    module['pose'](data,False)
    assert data['bind_matrix_error']<1e-6
    for chain in [range(1,5),range(5,10),range(10,15),range(15,20),range(20,25)]:
        parent=0
        for child in chain:
            assert abs(np.linalg.norm(posed[child]-posed[parent])-np.linalg.norm(data['bind'][child]-data['bind'][parent]))<1e-10
            parent=child
    diagnostic=json.loads((HERE/'11-mesh-contact-contours/closed.json').read_text())
    assert diagnostic['bar']['skin_vertices_inside']>0 and diagnostic['bar']['contact_solved'] is False
    print(json.dumps(dict(production_engine_unchanged=True,licensed_asset_bytes_verified=True,
        preserved_check_images=len(pairs),parsed_svgs=len(svgs),bind_matrix_error=data['bind_matrix_error'],
        articulated_bone_lengths_preserved=True,grasp_default_ready=False,
        sampled_skin_vertices_inside_rod=diagnostic['bar']['skin_vertices_inside']),indent=2))

if __name__=='__main__':run()
