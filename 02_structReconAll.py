"""
How to run:
$ python 02_structReconAll.py hc01_d00
"""
from nipype.interfaces.freesurfer.preprocess import ReconAll
import os, glob, sys

data_dir = '/nobackup/ilz2/bayrak/subjects'

# subject_id and T1 scan directory: user given
subject_id = sys.argv[1]

Tscan 	   = os.path.join(data_dir, subject_id, 
	    		 'nifti/mprage', 'T1.nii.gz')
print Tscan
# define working dir
work_dir = os.path.join(data_dir, subject_id, 'freesurfer')

# go into working dir
os.chdir(work_dir)

# run ReconAll
recon_all = ReconAll()
recon_all.inputs.subject_id   = subject_id
recon_all.inputs.subjects_dir = '/nobackup/ilz2/bayrak/freesurfer'
recon_all.inputs.T1_files     = Tscan
recon_all.run()
