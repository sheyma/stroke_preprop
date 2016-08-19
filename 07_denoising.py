import os, sys
import nipype.interfaces.nipy as nipy
import nipype.algorithms.rapidart as ra
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl

# data dir's 
# data_in MUST BE CHANGED!
data_in  = '/scr/ilz2/bayrak/new_func/'
data_out = '/scr/ilz2/bayrak/new_denoise/'
free_dir = '/scr/ilz2/bayrak/new_struc/'
recon_al = 'recon_all/mri'

# subject id, resting scan dir
subject_id = sys.argv[1]
scan 	   = sys.argv[2]
Tscan      = sys.argv[3]

# create a working directory	
if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)

if not os.path.exists(os.path.join(work_dir, scan)):
	os.makedirs(os.path.join(work_dir, scan))
work_dir = os.path.join(work_dir, scan)

# go into working directory
os.chdir(work_dir)

# motion corrected functional image
img_func = os.path.join(data_in, subject_id, scan,
			'corr_rest_roi.nii.gz')
# motion correction parameters
params_func = os.path.join(data_in, subject_id, scan,
			'rest_roi.nii.gz.par')
# binary mask produces by skull stripping
mask_func = os.path.join(data_in, subject_id, scan,
			'corr_rest_roi_brain_mask.nii.gz')

# STEP #1 ###########################################
# get the outlier by using motion and intensity params

ad = ra.ArtifactDetect()
ad.inputs.realigned_files 	 = img_func 
ad.inputs.parameter_source 	 = 'NiPy' 
ad.inputs.realignment_parameters = params_func
ad.inputs.norm_threshold         = 1
ad.inputs.zintensity_threshold   = 3
ad.inputs.use_differences        = [True, False]
ad.inputs.mask_type		 = 'file'
ad.inputs.mask_file 		 = mask_func
ad.run()

outlier_file = 'art.corr_rest_roi_outliers.txt'

# STEP #2 ############################################
# get motion regressors

def motion_regressors(motion_params, order=0, derivatives=1):
	"""Compute motion regressors upto given order and derivative
	motion + d(motion)/dt + d2(motion)/dt2 (linear + quadratic)
	"""
	from nipype.utils.filemanip import filename_to_list
	import numpy as np
	import os

	out_files = []
	for idx, filename in enumerate(filename_to_list(motion_params)):
		params = np.genfromtxt(filename)
		out_params = params
		
		for d in range(1, derivatives + 1):
			cparams = np.vstack((np.repeat(params[0, :][None, :], 
				 	     d, axis=0), params))
					    
			out_params = np.hstack((out_params, np.diff(cparams, 
						d, axis=0)))
		out_params2 = out_params

		for i in range(2, order + 1):
			out_params2 = np.hstack((out_params2, 
						 np.power(out_params, i)))
		
		filename = os.path.join(os.getcwd(), 
					"motion_regressor_der%d_ord%d.txt"
					 % (derivatives, order))

		np.savetxt(filename, out_params2, fmt="%.10f")
		out_files.append(filename)
	return out_files

motion_regressors(params_func, order=2, derivatives=1)[0]

motionreg_file = 'motion_regressor_der1_ord2.txt'

# STEP #3 ###########################################################
# get white matter mask

# get aparc+aseg.mgz from recon_all dir
aparc_aseg = os.path.join(free_dir, subject_id, Tscan, recon_al,
			  'aparc+aseg.mgz')
# define new filenames
aparc_aseg_nifti  = os.path.abspath('aparc_aseg.nii.gz')
aparc_aseg_mask   = os.path.abspath('aparc_aseg_mask.nii.gz')
aparc_aseg_filled = os.path.abspath('aparc_aseg_mask_filled.nii.gz')
wm_and_csf_mask   = os.path.abspath('wmcsf_mask.nii.gz')

# convert *mgz into *nii.gz
mricon = fs.MRIConvert()
mricon.inputs.in_file  = aparc_aseg
mricon.inputs.out_file = aparc_aseg_nifti
mricon.inputs.out_type = 'niigz'
mricon.run()

# create wmcsf mask
wmcsf_mask = fs.Binarize()
wmcsf_mask.inputs.in_file     = aparc_aseg_nifti
wmcsf_mask.inputs.wm_ven_csf  = True
wmcsf_mask.inputs.erode       = 2
wmcsf_mask.inputs.out_type    = 'nii.gz'
wmcsf_mask.inputs.binary_file = wm_and_csf_mask
wmcsf_mask.run()


