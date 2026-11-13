import pathlib,json,hashlib,math
B=pathlib.Path(__file__).resolve().parent
def digest(p):return hashlib.sha256((B/p).read_bytes()).hexdigest()
def same(a,b):return (B/a).read_bytes()==(B/b).read_bytes()
rows=[json.loads(x) for x in (B/'commands.jsonl').read_text(encoding='utf-8').splitlines()]
def response(outdir):
    return next(json.loads(x['stdout']) for x in rows if '--outdir' in x['command'] and x['command'][-1].endswith('/'+outdir))
def anchor(view,name):return response(view)['selected']['anchors'][name]
joins=[]
for child,ca,parent,pa in [('final-hand','wrist','final-cuff','right-wrist'),('final-upper','root','final-hand','handle_left'),('final-lower','root','final-hand','handle_right')]:
    a,b=anchor(child,ca),anchor(parent,pa)
    joins.append({'join':f'{child}.{ca} -> {parent}.{pa}','point_distance_pixels':math.dist(a['point'],b['point']),'direction_dot':sum(x*y for x,y in zip(a['direction'],b['direction']))})
checks={'undo_scene_bytes_equal_pre_move':same('pre-move.json','undone.json'),'reaccept_scene_bytes_equal_accepted':same('accepted.json','working.json'),'undo_png_bytes_equal_before':same('before-wrist/artwork.png','undo-wrist/artwork.png'),'reaccept_png_bytes_equal_accepted':same('accepted-wrist/artwork.png','reaccepted-wrist/artwork.png'),'preview_png_bytes_equal_accepted':same('try-wrist/artwork.png','accepted-wrist/artwork.png'),'pose_png_differs':not same('before-wrist/artwork.png','accepted-wrist/artwork.png'),'all_cli_terminal_exit_0':all(x.get('terminal') and x['exit']==0 for x in rows)}
nodes={n['id']:n for n in json.loads((B/'working.json').read_text())['nodes']}
checks['three_persistent_opposed_relations']=all(nodes[n]['attachment'].get('orient')=='opposed' and 'angle' not in nodes[n] for n in ['flower-hand','upper-stem','lower-stem'])
v={'checks':checks,'joins':joins,'cli_count':len(rows),'engine':response('final-hand')['engine'],'renderer':response('final-hand')['renderer'],'processes':[{'pid':r['pid'],'start':r['start'],'terminal':r['terminal'],'exit':r['exit']} for r in rows],'protocol_exception':'Before polling live wrappers 57225, 41676, 47569, two inspections were started. All were then polled to terminal exit 0. Inspect source/target repeated serially in view-upper-serial and view-handle-left-serial. Duplicate number 7 is preserved in original log; identify records by PID/start or line index.'}
(B/'verification.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
files={str(p.relative_to(B)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in B.rglob('*') if p.is_file() and p.name!='SHA256.json'}
(B/'SHA256.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
print(json.dumps(v,indent=2))
