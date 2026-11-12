"""Root-authored semantic insertion proposal; inspect clean render before normal CLI acceptance."""
import copy,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from scripts.studio.model import read,write,validate,fingerprint,engine_fingerprint
from scripts.studio.render import bundle
s=read('evidence/studio-watering/working.json');after=copy.deepcopy(s)
after['nodes'] += [dict(id='grip-thumb',kind='stroke',intent='the thumb crosses the folded fingers over the carrying handle',length=.034,thickness=.013,angle=87,bend=.08,depth=32,
                       palette=dict(fill='#f1d0b8',ink='#b5836d'),ink_width=.001,
                       attachment=dict(to='carrying-hand',self='root',target='left@.35',inset=.1)),
                  dict(id='grip-fold',kind='stroke',intent='one small crease indicates folded fingers rather than an open palm',length=.017,thickness=.0014,angle=0,bend=.08,depth=33,palette=dict(fill='#b5836d'),
                       attachment=dict(to='carrying-hand',self='root',target='top@.72',inset=.18))]
validate(after);out='evidence/studio-watering/14-thumb-and-fold'
bundle(after,out)
write(out+'/candidate.json',dict(base=fingerprint(s),engine=engine_fingerprint(),result=fingerprint(after),scene=after,status='ready',operation=dict(action='insert-authored-group',objects=['grip-thumb','grip-fold'],reason='A crossing thumb and folded-finger crease explain the closed carrying hand')))
print('two existing gesture marks proposed, not accepted')
