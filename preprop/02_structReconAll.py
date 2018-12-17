"""
running freesurfer reconall to get tissue segmentations from T1

subject_id = sd51_d01 
data_dir   = /data/pt_mar006/subjects
free_dir   = /data/pt_mar006/freesurfer

Usage:
$ python 02_structReconAll.py <subject_id> <data_dir> <free_dir>
"""

from nipype.interfaces.freesurfer.preprocess import ReconAll
import os, glob, sys

# subject_id and T1 scan directory: user given
subject_id = sys.argv[1]
data_dir   = sys.argv[2]
free_dir   = sys.argv[3]

Tscan 	   = os.path.join(data_dir, subject_id, 
	    		 'nifti/mprage', 'T1.nii.gz')

# run ReconAll
recon_all = ReconAll()
recon_all.inputs.subject_id   = subject_id
recon_all.inputs.subjects_dir = free_dir
recon_all.inputs.T1_files     = Tscan
recon_all.run()
