from pathlib import Path
import json,struct
import cv2
import numpy as np
from PIL import Image
out=Path('evidence/studio-hand/inspection-encoding');out.mkdir(parents=True,exist_ok=False)
source=Path('evidence/studio-hand/usability/17-final/artwork.png')
with Image.open(source) as image:
    image.convert('RGB').save(out/'pillow-rgb.png')
    image.convert('RGBA').save(out/'pillow-rgba.png')
a=cv2.imread(str(source),cv2.IMREAD_UNCHANGED)
cv2.imwrite(str(out/'opencv-rgba.png'),a)
def chunks(path):
    data=Path(path).read_bytes();i=8;result=[]
    while i<len(data):
        size=struct.unpack('>I',data[i:i+4])[0];kind=data[i+4:i+8].decode('ascii')
        result.append([kind,size]);i+=size+12
    return result
files=[source,Path('evidence/studio-hand/usability/check/draft-fullres.png')]+list(out.glob('*.png'))
reference=np.asarray(Image.open(source).convert('RGBA'))
report=[]
for path in files:
    pixels=np.asarray(Image.open(path).convert('RGBA'))
    assert np.array_equal(pixels,reference)
    report.append(dict(path=str(path),chunks=chunks(path),decoded_pixels_identical=True))
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(out/'source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(report))
