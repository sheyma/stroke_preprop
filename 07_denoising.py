import os, sys
import nipype.interfaces.nipy as nipy
import nipype.algorithms.rapidart as ra

# data dir's 
# data_in MUST BE CHANGED!
data_in  = '/scr/ilz2/bayrak/new_func/'
data_out = '/scr/ilz2/bayrak/new_denoise/'

# subject id, resting scan dir
subject_id = sys.argv[1]
scan 	   = sys.argv[2]

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

# Step#1 get the outlier...
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

# Step#2 get motion regressors
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
