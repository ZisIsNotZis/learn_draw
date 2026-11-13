import pathlib,json,hashlib
r=pathlib.Path(__file__).resolve().parent
def j(p):return json.loads((r/p).read_text(encoding='utf-8'))
def h(p):return hashlib.sha256((r/p).read_bytes()).hexdigest()
checks={'frozen_matches_first_export':j('initial-frozen.json')==j('01-inspect/scene.json'),'undo_scene':j('04-wrist/scene.json')==j('08-restored/scene.json'),'undo_png':h('04-wrist/artwork.png')==h('08-restored/artwork.png'),'reaccept_scene':j('05-wrist-up/scene.json')==j('10-final/scene.json'),'reaccept_png':h('05-wrist-up/artwork.png')==h('10-final/artwork.png')}
before=j('01-inspect.stdout');after=j('04-wrist.stdout')
checks['elbow_kept_shoulder']=before['selection']['locks']['shoulder']==after['selection']['locks']['shoulder']
checks['elbow_kept_wrist']=before['selection']['locks']['wrist']==after['selection']['focus']
initial=j('initial-frozen.json');final=j('working.json')
checks['child_relation_preserved']=[n for n in initial['nodes'] if n['id']=='flower-hand']==[n for n in final['nodes'] if n['id']=='flower-hand']
greet=j('greeting.json')
checks['greeting_has_body_head_open_hand']={'body','head','hand'}.issubset({n['kind'] for n in greet['nodes']})
checks['greeting_scene_matches_preview']=greet==j('32-wave-seat/scene.json')
checks['greeting_png_matches_preview']=h('32-wave-seat/artwork.png')==h('34-greeting-final/artwork.png')
port=j('30-current-port.stdout')['selected']['anchors']['right-wrist']['point']
wrist=j('34-greeting-final.stdout')['selected']['anchors']['wrist']['point']
checks['greeting_hand_point_contact']=max(abs(a-b) for a,b in zip(port,wrist))<1e-8
launches={p.stem:j(p.name) for p in sorted(r.glob('*.launch.json'))}
checks['all_terminal']=all(e['state']=='terminal' for e in launches.values())
result={'checks':checks,'full_report_used':False,'launches':launches}
(r/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(checks));assert all(checks.values())
manifest={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(r.rglob('*')) if p.is_file() and p.name!='SHA256.json'}
(r/'SHA256.json').write_text(json.dumps(manifest,indent=2))
