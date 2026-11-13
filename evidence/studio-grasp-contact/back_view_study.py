"""Test the simpler back-of-hand view in the actual composition, same contact pose."""
from contact import PREVIOUS,OUT
from render_contact import run
from compose_watering import run as compose
import numpy as np

if __name__=='__main__':
    data=PREVIOUS['load']()|dict(np.load(OUT/'bind-06.npz'))
    result=dict(np.load(OUT/'pose-09.npz'))
    run(data,result,OUT/'14-back-grip',yaw=150,pitch=-15)
    compose(asset='14-back-grip',out='15-watering-back')
