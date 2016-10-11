import numpy as np
import nibabel as nb
import matplotlib.pyplot as plt
import os, sys
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf 


# Step 1: QUALITY CONTROL FOR MOTION CORRECTION 

# framewise displacement (FD) for a subject's motion parameters
def calc_FD_power(motion_pars_file):
    '''
    Method to calculate FD based on (Power, 2012)
    '''
    lines        =  open(motion_pars_file, 'r').readlines()
    rows         = [[float(x) for x in line.split()] for line in lines]
    cols         = np.array([list(col) for col in zip(*rows)])
    translations = np.transpose(np.abs(np.diff(cols[0:3, :])))
    rotations    = np.transpose(np.abs(np.diff(cols[3:6, :])))
    FD_power     = np.sum(translations, axis = 1) + (50*3.141/180)*np.sum(rotations, axis =1)
    #FD is zero for the first time point
    FD_power = np.insert(FD_power, 0, 0)
    #np.savetxt(fd_out, FD_power)
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

# plotting a horizontal line, used for mean_FD...
def plot_vline(cur_val, label, ax):
    ax.axvline(cur_val)
    ylim = ax.get_ylim()
    vloc = (ylim[0] + ylim[1]) / 2.0
    xlim = ax.get_xlim()
    pad = (xlim[0] + xlim[1]) / 100.0
    ax.text(cur_val - pad, vloc, label, color="blue", rotation=90, 
            verticalalignment='center', horizontalalignment='right')

# plotting a subject's FD distribution and optionally mean_FD line
def plot_FD(motion_pars_file, mean_FD_distribution=None, figsize=(11.7,8.3)):

    FD_power = calc_FD_power(motion_pars_file)

    fig = Figure(figsize=figsize)
    FigureCanvasPdf(fig)
   
    if mean_FD_distribution:
        grid = GridSpec(2, 4)
    else:
        grid = GridSpec(1, 4)

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
	   '/nobackup/ilz2/bayrak/preprocess/hc02/rsd00/func_prepro/rest_roi.nii.gz.par',
	   '/nobackup/ilz2/bayrak/preprocess/hc02/rsd00/func_prepro/rest_roi.nii.gz.par',
	   '/nobackup/ilz2/bayrak/preprocess/hc02/rsd00/func_prepro/rest_roi.nii.gz.par']

infile = infiles[0]

A = calc_FD_power(infile) 

mean_FD_dist, max_FD_dist = get_mean_FD_dist(infiles)

Figure = plot_FD(infile, mean_FD_distribution = mean_FD_dist, 
	         figsize=(11.7,8.3))

Figure.savefig('B.pdf', format='pdf')

#plt.savefig('/tmp/foo.png')

