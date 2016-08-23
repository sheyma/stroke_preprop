import os, sys
import nipype.interfaces.nipy as nipy
import nipype.interfaces.fsl as fsl

# data dir's 
data_in  = '/scr/ilz2/bayrak/new_nifti/'
data_out = '/scr/ilz2/bayrak/new_func/'

# subject id, resting scan dir
subject_id = sys.argv[1]
scan 	   = sys.argv[2]

# resting state image
img_rest = os.path.join(data_in, subject_id, scan, 
			'rest.nii.gz')

# create a working directory	
if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)

if not os.path.exists(os.path.join(work_dir, scan)):
	os.makedirs(os.path.join(work_dir, scan))
work_dir = os.path.join(work_dir, scan)

# go into working directory
os.chdir(work_dir)

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
img_rois = strip_rois_func(img_rest, n_vol_remove)

# Step#2 simultaneous slice-time correction & motion correction
realigner  		     = nipy.SpaceTimeRealigner()
realigner.inputs.in_file     = img_rois
realigner.inputs.tr	     = 2.3
realigner.inputs.slice_times = 'asc_alt_2_1'
realigner.inputs.slice_info  = 2
realigner.run() 

## Step#3 get binary mask & skull stripped image
img_StMoco = os.path.abspath('corr_rest_roi.nii.gz')

btr 		     = fsl.BET()
btr.inputs.in_file   = img_StMoco 
btr.inputs.mask      = True
btr.run() 





