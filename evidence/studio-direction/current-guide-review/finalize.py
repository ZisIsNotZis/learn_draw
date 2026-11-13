import pathlib,json,hashlib
p=pathlib.Path(__file__).resolve().parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
manifest={str(f.relative_to(p)).replace('\\','/'):sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f.name!='artifact-sha256.json'}
external=p.parent/'00b-small-guides-contrast'
manifest['observed_external_inputs']={f.name:sha(f) for f in [external/'alignment.png',external/'object-closeup.png']}
(p/'artifact-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(len(manifest)-1,'own artifacts hashed')
