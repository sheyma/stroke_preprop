"""
    # artefact detection (calculating outliers)
    # calculates motion regressors given motion corrections parameters 
    # creates binary masks for wm + csf, projecting to functional space
    # denoising with CompCor, normalization and band-pass filtering
    ### optional argument for intra-subject registration 
    
data_dir       = '/data/pt_mar006/subjects'
subject_id     = 'sd51_d00'
dayXX          = 'd01'
Usage:
    $ python 06_funcDenoise.py <data_dir> <subject_id> [dayXX]
"""
import os, sys
import matplotlib
matplotlib.use('Agg')
import nipype.interfaces.nipy as nipy
import nipype.algorithms.rapidart as ra
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
from functions import motion_regressors
from functions import nilearn_denoise

data_dir   = sys.argv[1]
subject_id = sys.argv[2]

# define working dir
work_dir = os.path.join(data_dir, subject_id, 
			'preprocessed/func', 'denoise') 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

# GET EXISTING FILENAMES
func_dir = os.path.join(data_dir,subject_id,'preprocessed/func/realign')
# motion corrected functional image
img_func = os.path.join(func_dir, 'corr_rest_roi.nii.gz') 
# motion correction parameters
params_func = os.path.join(func_dir, 'rest_roi.nii.gz.par')
# binary mask produced by skull stripping
mask_func = os.path.join(func_dir, 'corr_rest_roi_brain_mask.nii.gz')

# STEP #1 artefact detection 
work_dir_artefact = os.path.join(os.getcwd(), 'artefact')
if not os.path.exists(work_dir_artefact):
	os.makedirs(work_dir_artefact)
os.chdir(work_dir_artefact)
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
# get the name of the outlier file produced by ad 
outlier_file = os.path.abspath('art.corr_rest_roi_outliers.txt')

# STEP #2 motion regressors 
os.chdir(work_dir)
work_dir_regress = os.path.join(os.getcwd(), 'regress')
if not os.path.exists(work_dir_regress):
	os.makedirs(work_dir_regress)
os.chdir(work_dir_regress)

motionreg_file = motion_regressors(params_func,
				   order=2, derivatives=1)[0]

## STEP #3 projecting brain mask and wm+csf mask to rest space
os.chdir(work_dir)
work_dir_mask= os.path.join(os.getcwd(), 'mask')
if not os.path.exists(work_dir_mask):
	os.makedirs(work_dir_mask)
os.chdir(work_dir_mask)

#create names...
wmcsf_mask_func = os.path.abspath('wmcsf_mask_func.nii.gz')
brain_mask_func = os.path.abspath('brain_mask_func.nii.gz')

if len(sys.argv) > 3:
    # e.g. dayXX = 'd01'
    dayXX = sys.argv[3] 
    # get wmcsf_mask from dayXX
    wmcsf_mask = os.path.join(data_dir, subject_id[:5] + dayXX,
                              'preprocessed/func/denoise/mask/'
                              'wmcsf_mask.nii.gz')
    
    # get brain mask from dayXX
    brain_mask = os.path.join(data_dir, subject_id[:5] + dayXX,
                              'preprocessed/anat/brain_mask.nii.gz')  
    # tranform matrices...
    restToRest = os.path.join(data_dir, subject_id,
                              'preprocessed/func/transforms2rest' + dayXX[1:],
                              'transform_day' + dayXX[1:] + '_itk.mat')

    restToAnat = os.path.join(data_dir, subject_id[:5] + dayXX,
                              'preprocessed/func/coregister/transforms2anat',
                              'rest2anat_itk.mat')
    # reference mean rest...
    restRefere = os.path.join(data_dir, subject_id,
                              'preprocessed/func/realign',
                              'mean_corr_rest_roi.nii.gz')

    # project wmcsf mask from dayXX to functional space of subject_id     
    at			       = ants.ApplyTransforms()
    at.inputs.input_image      = wmcsf_mask
    at.inputs.output_image     = wmcsf_mask_func
    at.inputs.reference_image  = restRefere
    at.inputs.transforms       = [restToRest, restToAnat]
    at.inputs.invert_transform_flags = [True, True]
    at.inputs.interpolation    = 'NearestNeighbor'
    at.run()
    
    # project brain_mask from dayXX to functional space of subject_id
    at			   = ants.ApplyTransforms()
    at.inputs.input_image      = brain_mask
    at.inputs.output_image     = brain_mask_func
    at.inputs.reference_image  = restRefere
    at.inputs.transforms       = [restToRest, restToAnat]
    at.inputs.interpolation    = 'NearestNeighbor'
    at.inputs.invert_transform_flags = [True, True]
    at.run()
    
else:
    # create names...
    wmcsf_mask      = os.path.abspath('wmcsf_mask.nii.gz') 

    # get aparc+aseg from /anat/ dir
    aparc_aseg = os.path.join(data_dir, subject_id, 
                              'preprocessed/anat/aparc+aseg.nii.gz')
    # create wmcsf mask
    get_mask = fs.Binarize()
    get_mask.inputs.in_file     = aparc_aseg
    get_mask.inputs.wm_ven_csf  = True
    get_mask.inputs.erode       = 2
    get_mask.inputs.out_type    = 'nii.gz'
    get_mask.inputs.binary_file = wmcsf_mask
    get_mask.run()

    # project wmcsf mask to functional space (with bbregister outputs) 
    transform_matrix = os.path.join(data_dir, subject_id, 
			'preprocessed/func/coregister/transforms2anat',
			'rest2anat_itk.mat')
    rest_mean        = os.path.join(data_dir, subject_id,
                                    'preprocessed/func/realign',
                                    'mean_corr_rest_roi.nii.gz')

    at			   = ants.ApplyTransforms()
    at.inputs.input_image      = wmcsf_mask
    at.inputs.transforms       = [transform_matrix]
    at.inputs.reference_image  = rest_mean
    at.inputs.interpolation    = 'NearestNeighbor'
    at.inputs.invert_transform_flags = [True]
    at.inputs.output_image     = wmcsf_mask_func
    at.run()

    # projecting brain_mask to functional space
    brain_mask = os.path.join(data_dir, subject_id,
                            'preprocessed/anat/brain_mask.nii.gz')

    at			   = ants.ApplyTransforms()
    at.inputs.input_image      = brain_mask
    at.inputs.transforms       = [transform_matrix]
    at.inputs.reference_image  = rest_mean
    at.inputs.interpolation    = 'NearestNeighbor'
    at.inputs.invert_transform_flags = [True]
    at.inputs.output_image     = brain_mask_func
    at.run()

# STEP #4 denoising with CompCor, normalization and band-pass filtering...
os.chdir(work_dir)
os.chdir(work_dir_regress)

# create name...
rest_denoised = os.path.join(data_dir, subject_id, 'preprocessed/func/',
			     'rest_preprocessed.nii.gz')

nilearn_denoise(in_file = img_func, brain_mask = mask_func, 
		wm_csf_mask = wmcsf_mask_func, motreg_file = motionreg_file,
		outlier_file = outlier_file, bandpass = [0.1, 0.01],
		tr = 2.3, img_fname = rest_denoised)
