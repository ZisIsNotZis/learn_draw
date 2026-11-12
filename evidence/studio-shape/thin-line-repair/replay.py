import json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
import numpy as np
from PIL import Image
from scripts.studio.model import read,write,select,parameter_preview,accept
from scripts.studio.render import bundle
out=Path('evidence/studio-shape/thin-line-repair');out.mkdir(exist_ok=True)
scene=read('evidence/studio-shape/usability/lamp-book.json');write(out/'working.json',scene)
selection=select(scene,'page-seam',feature='object')
proposal=parameter_preview(scene,selection,'width',.008,'Keep the page separation fine instead of using a thick stripe forced by the old width floor')
write(out/'candidate.json',proposal)
bundle(proposal['scene'],out,selection,scene)
accept(out/'working.json',proposal)
a=np.asarray(Image.open('evidence/studio-shape/usability/final/artwork.png').convert('RGBA'));b=np.asarray(Image.open(out/'artwork.png').convert('RGBA'))
from scripts.studio.shape import shape_data
old=next(n for n in scene['nodes'] if n['id']=='page-seam')
x0,y0,x1,y1=shape_data(old,scene['canvas']).features['object']['bounds']
outside=np.ones(a.shape[:2],dtype=bool);outside[max(0,int(y0)-2):int(y1)+3,max(0,int(x0)-2):int(x1)+3]=False
assert np.array_equal(a[outside],b[outside])
write(out/'locality.json',dict(changed_parameter='page-seam.width',before=.05,after=.008,all_other_objects_unchanged=True,outside_old_mark_pixels_exact=True))
print('assisted fine-line repair rendered; unrelated pixels unchanged')
