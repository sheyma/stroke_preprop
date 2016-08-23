import os, sys
import nipype.interfaces.nipy as nipy
import nipype.algorithms.rapidart as ra
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
from functions import motion_regressors
from functions import nilearn_denoise

# data dir's 
# data_in MUST BE CHANGED!
data_in  = '/scr/ilz2/bayrak/new_func/'
data_out = '/scr/ilz2/bayrak/new_denoise/'
free_dir = '/scr/ilz2/bayrak/new_struc/'
recon_al = 'recon_all/mri'
data_bbreg = '/scr/ilz2/bayrak/new_bbreg/'

# subject id, resting scan dir
subject_id = sys.argv[1]
scan 	   = sys.argv[2]
Tscan      = sys.argv[3]

# create a working directory	
rs_T1 = scan+'_'+Tscan

if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)

if not os.path.exists(os.path.join(work_dir, rs_T1)):
	os.makedirs(os.path.join(work_dir, rs_T1))
work_dir = os.path.join(work_dir, rs_T1)

# go into working directory
os.chdir(work_dir)

# EXISTING FILENAMES
# motion corrected functional image
img_func = os.path.join(data_in, subject_id, scan,
			'corr_rest_roi.nii.gz')
# motion correction parameters
params_func = os.path.join(data_in, subject_id, scan,
			'rest_roi.nii.gz.par')
# binary mask produced by skull stripping
mask_func = os.path.join(data_in, subject_id, scan,
			'corr_rest_roi_brain_mask.nii.gz')

# STEP #1 #################################################
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

# STEP #2 #####################################################
# get motion regressors, output saved in motionreg_file

motionreg_file = motion_regressors(params_func,
				   order=2, derivatives=1)[0]

# STEP #3 #####################################################
# get white matter & CSF mask

# get aparc+aseg.mgz from recon_all dir
aparc_aseg = os.path.join(free_dir, subject_id, Tscan, recon_al,
			  'aparc+aseg.mgz')
# define new filenames
aparc_aseg_nifti  = os.path.abspath('aparc_aseg.nii.gz')
wmcsf_mask        = os.path.abspath('wmcsf_mask.nii.gz')
wmcsf_mask_func	  = os.path.abspath('wmcsf_mask_func.nii.gz')

# convert *mgz into *nii.gz
mricon = fs.MRIConvert()
mricon.inputs.in_file  = aparc_aseg
mricon.inputs.out_file = aparc_aseg_nifti
mricon.inputs.out_type = 'niigz'
mricon.run()

# create wmcsf mask
get_mask = fs.Binarize()
get_mask.inputs.in_file     = aparc_aseg_nifti
get_mask.inputs.wm_ven_csf  = True
get_mask.inputs.erode       = 2
get_mask.inputs.out_type    = 'nii.gz'
get_mask.inputs.binary_file = wmcsf_mask
get_mask.run()

# project wmcsf mask to functional space
at			   = ants.ApplyTransforms()
at.inputs.input_image      = wmcsf_mask
at.inputs.transforms       = [os.path.join(data_bbreg, subject_id, rs_T1, 						   'rest2anat_itk.mat')]
at.inputs.reference_image  = os.path.join(data_bbreg, subject_id, rs_T1,
					   'rest_mean.nii.gz')
at.inputs.interpolation    = 'NearestNeighbor'
at.inputs.invert_transform_flags = [True]
at.inputs.output_image     = wmcsf_mask_func
at.run()

# STEP #4 #######################################################
# denoising

nilearn_denoise(in_file = img_func, brain_mask = mask_func, 
		wm_csf_mask = wmcsf_mask_func, motreg_file = motionreg_file,
		outlier_file = outlier_file, bandpass = [0.1, 0.01],
		tr = 2.3)


