import os, sys
import nipype.interfaces.fsl as fsl

# data dir's
data_dir  = '/nobackup/ilz2/bayrak/preprocess'
data_out  = 'smooth'

# subject id, resting scan, T1 scan
subject_id = sys.argv[1]
scan 	   = sys.argv[2]
Tscan      = sys.argv[3]

# define working dir
rs_T1    = scan+'_'+Tscan

work_dir = os.path.join(data_dir, subject_id, rs_T1, 
			data_out) 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)

# go into working directory
os.chdir(work_dir)


rest_fun2mni = os.path.join(data_dir, subject_id, rs_T1,
			    'func2mni', 'rest_mni.nii.gz')
print rest_fun2mni
# Step#1 get a brain mask for func2mni image 
from nipype.interfaces import afni as afni
automask = afni.Automask()
automask.inputs.in_file    = rest_fun2mni 
automask.inputs.outputtype = "NIFTI_GZ"
automask.run()

# Step#2 smooth func2mni image
from nipype.interfaces.fsl import maths
smooth = maths.IsotropicSmooth()
smooth.inputs.in_file = rest_fun2mni
smooth.inputs.fwhm    = 6
smooth.run()
print smooth.cmdline

# Step#3 mask the smoothed image
from nipype.interfaces.fsl import maths
maskApp = maths.ApplyMask()
maskApp.inputs.in_file     = 'rest_mni_smooth.nii.gz'
maskApp.inputs.mask_file   = 'rest_mni_mask.nii.gz'
maskApp.inputs.out_file    = 'rest_mni_smooth_masked.nii.gz'
maskApp.inputs.output_type = 'NIFTI_GZ'
maskApp.run()
