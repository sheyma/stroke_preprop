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


