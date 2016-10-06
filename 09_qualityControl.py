import numpy as np
from scipy.stats import norm
import nibabel as nb
import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import math
import time
import seaborn as sns
import matplotlib.cm as cm
from matplotlib.gridspec import GridSpec
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas



def calc_FD_power(motion_pars, fd_out):
    '''
    Method to calculate FD based on (Power, 2012)
    '''

    lines        =  open(motion_pars, 'r').readlines()
    rows         = [[float(x) for x in line.split()] for line in lines]
    cols         = np.array([list(col) for col in zip(*rows)])
    translations = np.transpose(np.abs(np.diff(cols[0:3, :])))
    rotations    = np.transpose(np.abs(np.diff(cols[3:6, :])))
    FD_power     = np.sum(translations, axis = 1) + (50*3.141/180)*np.sum(rotations, axis =1)
    #FD is zero for the first time point
    FD_power = np.insert(FD_power, 0, 0)

    #np.savetxt(fd_out, FD_power)

    return np.mean(FD_power)




if len(sys.argv) < 2:
    print "error: no input files given"
    sys.exit(1)

means_dict = dict()
means = np.zeros(len(sys.argv[1:]))

# for all args write "FD.1D" file to the same path
i=0
for infile in sys.argv[1:]:
    print "%s ..." % (infile)
    outfile = os.path.join(os.path.dirname(infile), 'FD.1D')
    mean = calc_FD_power(infile, outfile)
    print "mean: %f" % (mean)
    means_dict[outfile] = mean
    means[i] = mean
    i += 1

print means


plt.hist(means, bins=15)

plt.xlabel('FD (mm)' , fontsize = 22)
plt.ylabel('Number of Subjects' , fontsize = 22)
plt.tick_params(labelsize=20)



plt.title("FD Distribution", fontsize = 22)
plt.show()
#plt.savefig('/tmp/foo.png')

