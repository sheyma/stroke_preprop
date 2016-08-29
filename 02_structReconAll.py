"""
How to run:
$ python 02_structReconAll.py hc01 T1d00
"""
from nipype.interfaces.freesurfer.preprocess import ReconAll
import os, glob, sys

data_dir = '/scr/ilz2/bayrak/preprocess'

# subject_id and T1 scan directory: user given
subject_id = sys.argv[1]
Tscan 	   = sys.argv[2] 

# define working dir
work_dir = os.path.join(data_dir, subject_id, Tscan)
# go into working dir
os.chdir(work_dir)

# find out the T1.nii.gz to be preprocessed
data_T1 = os.path.join(work_dir, 'T1.nii.gz')

# run ReconAll
recon_all = ReconAll()
recon_all.inputs.T1_files = data_T1
recon_all.run()
