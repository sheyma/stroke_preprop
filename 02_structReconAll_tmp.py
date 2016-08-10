from nipype.interfaces.freesurfer.preprocess import ReconAll
import os, glob, sys

data_dir = '/scr/ilz2/bayrak/healthy_nifti/'
data_out = '/scr/ilz2/bayrak/healthy_reconall/'

# subject_id and T1 scan directory: user given
subject_id = sys.argv[1]
scan 	   = sys.argv[2] 

# create working dir
if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir_01 = os.path.join(data_out, subject_id)

if not os.path.exists(os.path.join(work_dir_01, scan)):
	os.makedirs(os.path.join(work_dir_01, scan))
work_dir_02 = os.path.join(work_dir_01, scan)

# go into working dir
os.chdir(work_dir_02)

# find out the T1.nii.gz to be preprocessed
struct_nifti = os.path.join(data_dir, subject_id, scan, 'T1.nii.gz')
# copy T1.nii.gz into working directory
os.system("cp %s %s" % (struct_nifti, work_dir_02))

# run ReconAll
recon_all = ReconAll()
recon_all.inputs.T1_files = 'T1.nii.gz'
recon_all.run()
