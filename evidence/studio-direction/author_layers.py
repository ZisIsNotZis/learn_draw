"""Author the petal overlap order after the equal-depth diagnosis; preserve its initial input."""
from pathlib import Path
import sys
from compose import compose
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.studio.model import read,write,fingerprint
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
 before=read(HERE/'working.json');assert fingerprint(before)==fingerprint(compose(False))
 after=compose(True)
 write(HERE/'layer-correction.json',dict(before=fingerprint(before),after=fingerprint(after),
     reason='Overlapping petals are separate sheets. Author a clockwise back-to-front order below the flower heart; no visibility cuts or image metrics.',
     canceled_render='01-sleeve-observe',terminal_observed=True,
     layers={n['id']:n['depth'] for n in after['nodes'] if n['id'].startswith('petal-')}))
 write(HERE/'layered-working.json',after);write(HERE/'working.json',after)
