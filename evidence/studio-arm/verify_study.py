"""Verify frozen study source bindings and replay scope; not an art gate."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def sources(names):return sha(b''.join((H/n).read_bytes() for n in names))
def snap(n,v):return f'source-history/{n}-v{v}.py'
configs={}
for i in range(1,6):configs[i]=[snap('build_study',1),snap('study_arm',1)]
for i in (6,7):configs[i]=[snap('build_study',2),snap('study_arm',1),snap('finish_arm',1)]
for i in (8,9):configs[i]=['build_study.py',snap('study_arm',2),snap('finish_arm',1)]
for nums,b,u in [([10],1,1),([11,12],2,2),([13,14],3,3),([15,16],4,4),([17],5,5),([18],6,6),([19],7,6),([20],8,7),([21,22],9,8),([23,24],10,None)]:
 for i in nums:configs[i]=[snap('build_body',b),snap('upper_body',u) if u else 'upper_body.py',snap('study_arm',2),snap('finish_arm',1)]
for i,names in configs.items():
 d=next(H.glob(f'{i:02}-*'));r=json.loads((d/'report.json').read_text());assert r['status']=='study-only';assert r['study']['source_sha256']==sources(names),(i,names)
 assert r['engine'].startswith('study:');assert (d/'artwork.png').read_bytes().startswith(b'\x89PNG')
assert (H/'input-person.json').read_bytes()==(H.parents[1]/'examples/studio/person_flower.json').read_bytes()
r=json.loads((H/'replay-verification.json').read_text())
for row in r['results']:
 assert sha((H/row['reference']/'artwork.png').read_bytes())==row['png_sha256']
 assert row['study']['source_sha256']==sources(['build_body.py','upper_body.py','study_arm.py','finish_arm.py'])
 assert row['study']['input_sha256']==sha((H/'input-person.json').read_bytes())
 assert row['exact_png']
print('24 historical source bindings; 2 exact historical replays; 1 retained new crossed output. No native-body/art-quality claim.')
