#!/usr/bin/env python3
"""Reproducible numeric audit and unprompted-view image boards; no segmentation or fitting."""
import csv, hashlib, json
from pathlib import Path
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).parent
TEACHER=ROOT.parent/'A-teacher-recovery-v1'/'teacher-only'
SOURCE=ROOT.parents[3]/'image.jpg'
CSV=TEACHER/'landmarks.csv'; CROP=TEACHER/'source-crop-registered.png'
OUT=ROOT; PATCH=OUT/'zoom-patches'; PATCH.mkdir(exist_ok=True)
source=Image.open(SOURCE).convert('RGB'); crop=Image.open(CROP).convert('RGB')
rows=list(csv.DictReader(CSV.open(encoding='utf-8',newline='')))
assert len(rows)==19 and source.size==(1024,1024) and crop.size==(400,480)
assert source.crop((500,320,900,800)).tobytes()==crop.tobytes()
records=[]
for r in rows:
 x,y,sx,sy=map(int,(r['crop_x'],r['crop_y'],r['source_x'],r['source_y']))
 assert (sx,sy)==(500+x,320+y)
 rgb=crop.getpixel((x,y)); patch=crop.crop((max(0,x-5),max(0,y-5),min(400,x+6),min(480,y+6)))
 hist=Counter(patch.getdata()); patch.save(PATCH/f"{r['id']}-raw.png")
 records.append(dict(id=r['id'], feature=r['feature'],crop_xy=[x,y],source_xy=[sx,sy],mapping_valid=True,rgb=list(rgb),rgb_hex='#%02x%02x%02x'%rgb,patch_radius_px=5,patch_size=list(patch.size),patch_pixels=patch.width*patch.height,unique_rgb=len(hist),most_common_rgb=[{'rgb':list(c),'count':n} for c,n in hist.most_common(5)],teacher_confidence=r['confidence'],teacher_observation=r['source-pixel observation and limitation']))
# pristine full crop base preserved byte-equivalent via lossless copy
crop.save(OUT/'pristine-fullcrop.png',format='PNG')
# marker board uses crop RGB base with crosshairs and source coordinate labels
board=crop.resize((800,960),Image.Resampling.NEAREST); d=ImageDraw.Draw(board); font=ImageFont.load_default()
for a in records:
 x,y=a['crop_xy']; X,Y=x*2,y*2
 d.line((X-7,Y,X+7,Y),fill='white',width=1); d.line((X,Y-7,X,Y+7),fill='white',width=1); d.rectangle((X+4,Y-5,X+34,Y+7),fill='white'); d.text((X+5,Y-4),a['id'],fill='black',font=font)
board.save(OUT/'numbered-crosshair.png')
# zoom board displays untouched raw patch pixels enlarged nearest; labels include ID + source coord only
cellw,cellh=220,190; cols=4; board2=Image.new('RGB',(cols*cellw,((len(records)+cols-1)//cols)*cellh),'#eeeeee'); d=ImageDraw.Draw(board2)
for i,a in enumerate(records):
 im=Image.open(PATCH/f"{a['id']}-raw.png").convert('RGB'); im=im.resize((im.width*10,im.height*10),Image.Resampling.NEAREST)
 ox=(i%cols)*cellw; oy=(i//cols)*cellh; board2.paste(im,(ox+(cellw-im.width)//2,oy+20)); d.text((ox+5,oy+2),f"{a['id']}  source ({a['source_xy'][0]},{a['source_xy'][1]})",fill='black',font=font)
board2.save(OUT/'raw-zoom-board.png')
meta={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_dimensions':list(source.size),'crop_sha256':hashlib.sha256(CROP.read_bytes()).hexdigest(),'crop_dimensions':list(crop.size),'crop_xyxy':[500,320,900,800],'all_192000_pixels_exact':True,'landmarks_sha256':hashlib.sha256(CSV.read_bytes()).hexdigest(),'landmark_count':len(records),'patch_definition':'inclusive radius 5 pixels, clipped to crop; raw pixels, no annotation or resampling in individual patch files','landmarks':records}
(OUT/'numeric-audit.json').write_text(json.dumps(meta,indent=2)+'\n')
with (OUT/'numeric-audit.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f); w.writerow(['id','crop_x','crop_y','source_x','source_y','mapping_valid','rgb_r','rgb_g','rgb_b','patch_radius_px','patch_width','patch_height','unique_rgb','modal_rgb','modal_count','confidence','semantic_reading'])
 for a in records:
  m=a['most_common_rgb'][0]; w.writerow([a['id'],*a['crop_xy'],*a['source_xy'],a['mapping_valid'],*a['rgb'],5,*a['patch_size'],a['unique_rgb'],','.join(map(str,m['rgb'])),m['count'],a['teacher_confidence'],a['feature']])
print('source',meta['source_sha256'],'crop',meta['crop_sha256'],'landmarks',len(records),'mapping_exact',meta['all_192000_pixels_exact'])
for a in records: print(a['id'],a['crop_xy'],a['rgb_hex'],a['most_common_rgb'][0])
