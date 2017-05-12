__all__ = ['core', 'math', 'utils', 'units', 'plots']

import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())

import matplotlib


matplotlib.use('Agg')

mpl_rcParams_update = {
    'font.family': 'serif',
    'mathtext.fontset': 'cm',
    'mathtext.rm': 'serif',
    'xtick.top': True,
    'xtick.bottom': True,
    'ytick.right': True,
    'ytick.left': True,
}

matplotlib.rcParams.update(mpl_rcParams_update)

# set up platform-independent runtime cython compilation and imports
import numpy as _np
import pyximport


pyx_dir = os.path.join(os.path.dirname(__file__), '.pyxbld')
pyximport.install(setup_args = {"include_dirs": _np.get_include()},
                  build_dir = pyx_dir,
                  language_level = 3)

_np.set_printoptions(linewidth = 200)  # screw character limits

from simulacra.core import *
from simulacra import math, utils, plots