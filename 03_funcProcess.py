import os, sys
import nipype.interfaces.nipy as nipy
import nipype.interfaces.fsl as fsl
from nipype.interfaces.fsl.maths import MeanImage
import nipype.algorithms.misc as misc

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects/'

subject_id = sys.argv[1]

# define working dir
work_dir = os.path.join(data_dir, subject_id, 
			'preprocessed/func/realign')
if not os.path.exists(work_dir):
	os.makedirs(work_dir)

# go into working directory
os.chdir(work_dir)

# resting state image
img_rest = os.path.join(data_dir, subject_id, 
                        'nifti/resting', 'rest.nii.gz')
print "resting state: ", img_rest
# Step#1 dropping first volumes
def strip_rois_func(in_file, t_min):
	import numpy as np
	import nibabel as nb
	import os
	from nipype.utils.filemanip import split_filename

	nii = nb.load(in_file)
	new_nii = nb.Nifti1Image(nii.get_data()[:,:,:,t_min:], 
				 nii.get_affine(), nii.get_header())
	new_nii.set_data_dtype(np.float32)
	_, base, _ = split_filename(in_file)
	nb.save(new_nii, base + "_roi.nii.gz")
	return os.path.abspath(base + "_roi.nii.gz")

n_vol_remove = 5 
img_rois     = strip_rois_func(img_rest, n_vol_remove)

# Step#2 simultaneous slice-time & motion correction
realigner  		     = nipy.SpaceTimeRealigner()
realigner.inputs.in_file     = img_rois
realigner.inputs.tr	     = 2.3

# get slice time sequence depending on subject_id 
# reads the sequence from text file for stroke data 
# assigns it to "asc_alt_2_1" for healthy controls
if subject_id[0:2] == 'sd':
	# find slice sequence text file
	filename = os.path.join(data_dir, subject_id,
				'nifti/resting', 'slice_timing.txt')
	print "getting slice time sequence from", filename 
	with open(filename) as f:
		st = map(float, f)
	print st
	realigner.inputs.slice_times = st
else:
	# ascend alternate every 2nd slice, starting at 2nd slice
	realigner.inputs.slice_times = 'asc_alt_2_1'	

realigner.inputs.slice_info  = 2
realigner.run() 

# Step#3 get T-mean of rs image after realignment 
fslmaths = MeanImage()
fslmaths.inputs.in_file   = 'corr_rest_roi.nii.gz'
fslmaths.inputs.out_file  = 'mean_corr_rest_roi.nii.gz'
fslmaths.inputs.dimension = 'T'
fslmaths.run()

## Step#4 get binary mask & skull stripped imag
img_StMoco = os.path.abspath('corr_rest_roi.nii.gz')

btr 		     = fsl.BET()
btr.inputs.in_file   = img_StMoco 
btr.inputs.mask      = True
btr.run() 

# Step#5 tsnr calculation on realigned image
tsnr = misc.TSNR()
tsnr.inputs.in_file = 'corr_rest_roi.nii.gz'
tsnr.run()


