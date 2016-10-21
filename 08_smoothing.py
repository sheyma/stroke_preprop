import os, sys
import nipype.interfaces.fsl as fsl

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects'

# subject id
subject_id = sys.argv[1]

# define working dir
work_dir = os.path.join(data_dir, subject_id, 
			'preprocessed/func') 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

rest_mni = os.path.join(work_dir,
			'rest_preprocessed2mni.nii.gz')

# define working dir for smoothing
work_dir_smooth = os.path.join(os.getcwd(), 'smooth')
if not os.path.exists(work_dir_smooth):
	os.makedirs(work_dir_smooth)
os.chdir(work_dir_smooth)

# Step#1 get a brain mask for func2mni image 
from nipype.interfaces import afni as afni
automask = afni.Automask()
automask.inputs.in_file    = rest_mni 
automask.inputs.outputtype = "NIFTI_GZ"
automask.run()

# Step#2 smooth func2mni image
from nipype.interfaces.fsl import maths
smooth = maths.IsotropicSmooth()
smooth.inputs.in_file = rest_mni
smooth.inputs.fwhm    = 6
smooth.run()

## Step#3 mask the smoothed image
from nipype.interfaces.fsl import maths
maskApp = maths.ApplyMask()
maskApp.inputs.in_file     = 'rest_preprocessed2mni_smooth.nii.gz'
maskApp.inputs.mask_file   = 'rest_preprocessed2mni_mask.nii.gz'
maskApp.inputs.out_file    = os.path.join(work_dir, 
		             'rest_preprocessed2mni_sm.nii.gz')
maskApp.inputs.output_type = 'NIFTI_GZ'
maskApp.run()
