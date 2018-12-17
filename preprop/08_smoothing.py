"""
    # smoothing the preprocessed epi image at the mni template space
    # since smoothing might spread out the epi out of the mni space, 
    # the smoothed image is masked back
    
data_dir   = '/data/pt_mar006/subjects/'
subject_id = 'sd51_d00'
Usage: 
    $ python 08_smoothing.py <data_dir> <subject_id>
"""
import os, sys
import nipype.interfaces.fsl as fsl

data_dir   = sys.argv[1]
subject_id = sys.argv[2]

# define working dir
work_dir = os.path.join(data_dir, subject_id, 
			'preprocessed/func') 
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
