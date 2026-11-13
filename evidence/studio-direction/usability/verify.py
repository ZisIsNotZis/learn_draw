import json,pathlib,hashlib
p=pathlib.Path(__file__).resolve().parent
def read(x):return json.loads((p/x).read_text(encoding='utf-8-sig'))
def sha(x):return hashlib.sha256((p/x).read_bytes()).hexdigest()
def nodes(s):return {n['id']:n for n in s['nodes']}
initial=read('../usability-inputs/initial.json'); fit=read('03-fit/candidate.json')['scene']; raised=read('05-raise/candidate.json')['scene']; refit=read('09-refit/candidate.json')['scene']
checks={}
checks['initial_copied_unchanged_canonical']=read('01-tip/scene.json')==initial
checks['first_fit_changed_nodes']=[i for i,n in nodes(initial).items() if n!=nodes(fit)[i]]
checks['first_fit_sleeve_changed_fields']=[k for k in set(nodes(initial)['reaching-sleeve'])|set(nodes(fit)['reaching-sleeve']) if nodes(initial)['reaching-sleeve'].get(k)!=nodes(fit)['reaching-sleeve'].get(k)]
for a,b,label in [('01-tip','03-fit','first_fit'),('07-tip','09-refit','refit')]:
 r1=read(a+'/report.json');r2=read(b+'/report.json')
 checks[label+'_terminal_points_exact']={t:r1['nodes']['reaching-sleeve']['anchors'][t]['point']==r2['nodes']['reaching-sleeve']['anchors'][t]['point'] for t in ['root','tip']}
 checks[label+'_directions']={'sleeve':r2['nodes']['reaching-sleeve']['anchors']['tip']['direction'],'wrist':r2['nodes']['flower-hand']['anchors']['wrist']['direction']}
checks['raise_changed_nodes']=[i for i,n in nodes(fit).items() if n!=nodes(raised)[i]]
checks['undo_exact_canonical_scene']=read('undone.json')==raised
checks['reaccept_exact_scene_bytes']=sha('working.json')==sha('accepted-before-undo.json')
checks['undo_exact_png']=sha('11-undone/artwork.png')==sha('07-tip/artwork.png')
checks['reaccept_exact_png']=sha('10-accepted/artwork.png')==sha('12-reaccepted/artwork.png')==sha('09-refit/artwork.png')
checks['first_fit_scene']=read('03-fit/report.json')['revision']
checks['raised_scene']=read('07-tip/report.json')['revision']
checks['final_scene']=read('12-reaccepted/report.json')['revision']
checks['engine']=read('12-reaccepted/report.json')['engine']
checks['final_image']=sha('12-reaccepted/artwork.png')
(p/'verification.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks,indent=2))
