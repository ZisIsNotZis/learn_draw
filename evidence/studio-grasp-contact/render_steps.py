"""Render the saved geometric experiments without rebuilding or altering poses."""
from contact import PREVIOUS,OUT
from render_contact import run
import numpy as np

if __name__=='__main__':
    data=PREVIOUS['load']()
    for number,name in [('02','02-opposed-thumb'),('04','04-surface-response')]:
        run(data,dict(np.load(OUT/('pose-'+number+'.npz'))),OUT/name)
