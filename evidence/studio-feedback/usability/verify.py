import pathlib,json,hashlib
root=pathlib.Path(__file__).resolve().parent
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def scene(path):return json.loads(path.read_text(encoding='utf-8'))
def eq(a,b):return scene(root/a)==scene(root/b)
checks={
 'source_matches_initial_export':scene(root.parent/'usability-inputs/initial.json')==scene(root/'initial/scene.json'),
 'undo_canonical_scene_recovered':eq('initial/scene.json','undo-view/scene.json'),
 'undo_png_recovered':digest(root/'initial/artwork.png')==digest(root/'undo-view/artwork.png'),
 'reaccept_canonical_scene_recovered':eq('hand-refined/scene.json','sleeve-inspect/scene.json'),
 'reaccept_png_recovered':digest(root/'hand-refined/artwork.png')==digest(root/'sleeve-inspect/artwork.png'),
 'final_preview_scene_matches_working':eq('cuff-refined/scene.json','working.json'),
 'final_preview_png_recovered':digest(root/'cuff-refined/artwork.png')==digest(root/'final/artwork.png')}
launches=[json.loads(p.read_text()) for p in sorted(root.glob('*.launch.json'))]
checks['all_cli_launches_observed_terminal']=all(p['state']=='terminal' and p['exit_code']==0 for p in launches)
result={'checks':checks,'full_report_data_used':False,'full_report_flag_used':False,'source_sha256':digest(root.parent/'usability-inputs/initial.json'),'cli_runs':len(launches),'responses':[{'tag':p.stem.removesuffix('.stdout'),**{k:v for k,v in json.loads(p.read_text()).items() if k in ['revision','engine','renderer']}} for p in sorted(root.glob('*.stdout.txt')) if p.read_text().startswith('{')]}
(root/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
assert all(checks.values())
manifest={str(p.relative_to(root)):digest(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='SHA256.json'}
(root/'SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
