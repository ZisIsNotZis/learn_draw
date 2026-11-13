import json,pathlib,hashlib,subprocess
p=pathlib.Path(__file__).resolve().parent
rows=[json.loads(x) for x in (p/'commands.jsonl').read_text(encoding='utf-8').splitlines()]
spawns=[x['pid'] for x in rows if x['event']=='spawned']; terminals={x['pid']:x for x in rows if x['event']=='terminal'}
audit={'spawned_count':len(spawns),'terminal_count':len(terminals),'missing_terminal':[x for x in spawns if x not in terminals]}
cmd='$ids=@('+','.join(str(x) for x in spawns)+'); Get-Process -Id $ids -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,StartTime | ConvertTo-Json'
r=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True)
audit['current_process_matches']=r.stdout.strip();audit['all_cli_terminal_outcomes_known']=not audit['missing_terminal']
(p/'process-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
manifest={str(x.relative_to(p)).replace('\\','/'):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(p.rglob('*')) if x.is_file() and x.name!='artifact-sha256.json'}
(p/'artifact-sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(audit,indent=2));print('artifact_count',len(manifest))
