"""One root-authored opening/plant depth proposal, using existing generic primitives."""
import copy,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import read,write,validate,fingerprint,engine_fingerprint,node_by_id
from scripts.studio.render import bundle
s=read('evidence/studio-watering/working.json');after=copy.deepcopy(s)
node_by_id(after,'plant-stem')['attachment']['inset']=.07
node_by_id(after,'plant-stem')['depth']=5
for i in range(4):node_by_id(after,'leaf-'+str(i+1))['depth']=6+i*.1
after['nodes'].append(dict(id='soil',kind='shape',intent='a dark oval opening explains soil and the landing of the watering stream',profile='oval',length=.025,width=6,stroke=.1,depth=4,
                          palette=dict(fill='#74674f',ink='#467e88'),attachment=dict(to='plant-pot',self='center',target='top',offset=[0,.005])))
validate(after);out='evidence/studio-watering/23-soil-opening';bundle(after,out)
write(out+'/candidate.json',dict(base=fingerprint(s),engine=engine_fingerprint(),result=fingerprint(after),scene=after,status='ready',operation=dict(action='compose-opening',objects=['soil','plant-stem','leaf-1','leaf-2','leaf-3','leaf-4'],reason='Give the pot a visible soil opening and let the stem emerge in front of it')))
print('soil opening and related plant depth proposal, not accepted')
