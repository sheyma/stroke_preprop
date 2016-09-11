import numpy as np
import nibabel as nb
import matplotlib.pyplot as plt
import os
import math
import time
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.gridspec import GridSpec
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas



def calc_FD_power(motion_pars):
    '''
    Method to calculate FD based on (Power, 2012)
    '''
    import os
    import numpy as np

    fd_out       =  os.path.join(os.getcwd(), 'FD.1D')
    lines        =  open(motion_pars, 'r').readlines()
    rows         = [[float(x) for x in line.split()] for line in lines]
    cols         = np.array([list(col) for col in zip(*rows)])
    translations = np.transpose(np.abs(np.diff(cols[0:3, :])))
    rotations    = np.transpose(np.abs(np.diff(cols[3:6, :])))
    FD_power     = np.sum(translations, axis = 1) + (50*3.141/180)*np.sum(rotations, axis =1)
    #FD is zero for the first time point
    FD_power = np.insert(FD_power, 0, 0)

    np.savetxt(fd_out, FD_power)

    return fd_out

A = '/scr/ilz2/bayrak/preprocess/hc01/rsd00_T1d00/denoise/motion_regressor_der1_ord2.txt'

print calc_FD_power(A)
