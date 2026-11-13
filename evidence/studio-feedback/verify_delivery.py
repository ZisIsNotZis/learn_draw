"""Verify focused-response delivery records without treating logs as visual approval."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
j=lambda p:json.loads((H/p).read_text(encoding='utf8'))
c=j('comparison.json');assert c==dict(focused_characters=2550,full_characters=35371,same_images_revision_engine=True,object_count=17)
assert j('test-run.json')['exit_code']==0
assert 'Ran 122 tests' in (H/'tests.txt').read_text()
p=j('verification/preservation.json');assert len(p['results'])==10
for name,r in p['results'].items():
 assert r['prior_png_preserved'];assert hashlib.sha256((H/'verification'/f'{name}.png').read_bytes()).hexdigest()==r['png_sha256']
v=j('usability/verification.json');assert all(v['checks'].values());assert v['cli_runs']==12;assert not v['full_report_data_used'];assert not v['full_report_flag_used']
m=j('usability/SHA256.json');assert len(m)==131
for name,digest in m.items():assert hashlib.sha256((H/'usability'/name).read_bytes()).hexdigest()==digest,name
for name in ('focused.stdout.json','full.stdout.json'):
 r=j(name);assert r['engine']==p['engine']
print('Focused response parity, 122-test record, ten PNG digests and 131 independent-operation digests verified; visual-sequencing lapse separately qualified.')
