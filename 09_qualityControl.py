import numpy as np
from scipy.stats import norm
import nibabel as nb
#import matplotlib as mpl
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


# Step 1: QUALITY CONTROL FOR MOTION CORRECTION 

# framewise displacement for a subject's "rest_roi.nii.gz.par"
def calc_FD_power(motion_pars):
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
    #return np.mean(FD_power)
    return FD_power

# get mean and max FD for all subjects iteratively 
def get_mean_FD_dist(motion_pars_files):
    mean_FDs = []
    max_FDs = [] 
    for motion_pars in motion_pars_files:
        FD_power = calc_FD_power(motion_pars)
        mean_FDs.append(FD_power.mean())
        max_FDs.append(FD_power.max())        
    return mean_FDs, max_FDs

def plot_frame_displacement(realignment_parameters_file, mean_FD_distribution=None, figsize=(11.7,8.3)):

    FD_power = calc_FD_power(realignment_parameters_file)
    print FD_power
    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
   
    if mean_FD_distribution:
        grid = GridSpec(2, 4)
    else:
        grid = GridSpec(1, 4)
    print grid
    ax = fig.add_subplot(grid[0,:-1])
    ax.plot(FD_power)
    ax.set_xlim((0, len(FD_power)))
    ax.set_ylabel("Frame Displacement [mm]")
    ax.set_xlabel("Frame number")
    ylim = ax.get_ylim()
    
    ax = fig.add_subplot(grid[0,-1])
    sns.distplot(FD_power, vertical=True, ax=ax)
    ax.set_ylim(ylim)
    
    if mean_FD_distribution:
        ax = fig.add_subplot(grid[1,:])
        sns.distplot(mean_FD_distribution, ax=ax)
        ax.set_xlabel("Mean Frame Displacement (over all subjects) [mm]")
        MeanFD = FD_power.mean()
        label = "MeanFD = %g"%MeanFD
        plot_vline(MeanFD, label, ax=ax)
        
    fig.suptitle('motion', fontsize='14')
        
    return fig


infiles = ['/nobackup/ilz2/bayrak/preprocess/hc01/rsd00/func_prepro/rest_roi.nii.gz.par',
	   '/nobackup/ilz2/bayrak/preprocess/hc02/rsd00/func_prepro/rest_roi.nii.gz.par']

infile = infiles[0]

A = calc_FD_power(infile)
B = get_mean_FD_dist(infiles)
#print A
#print B 

Figure = plot_frame_displacement(infile, mean_FD_distribution=None, figsize=(11.7,8.3))
plt.show()

#for infile in sys.argv[1:]:
#    print "%s ..." % (infile)
#    outfile = os.path.join(os.path.dirname(infile))
##   mean = calc_FD_power(infile)
#    print mean	
#    print np.shape(mean)
#    get_mean_frame_displacement_disttribution(infile)

    #print "mean: %f" % (mean)
#    means_dict[outfile] = mean
#    means[i] = mean
#    i += 1

#print means


#plt.hist(means, bins=15)

#plt.xlabel('FD (mm)' , fontsize = 22)
#plt.ylabel('Number of Subjects' , fontsize = 22)
#plt.tick_params(labelsize=20)

#plt.title("FD Distribution", fontsize = 22)
#plt.show()
#plt.savefig('/tmp/foo.png')

