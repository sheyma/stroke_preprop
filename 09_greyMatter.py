"""
get individual GM masks, project to MNI3mm &
get individual rest masks (3dAutomask)
"""
import os, sys
import nipype.interfaces.freesurfer as fs
import nibabel as nb
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
from nipype.interfaces.fsl.maths import MathsCommand
from nipype.interfaces import afni

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects'

# subject id
subject_id = sys.argv[1]

# freesurfer dir for recon_all outputs
freesurfer_dir = '/nobackup/ilz2/bayrak/freesurfer'

# define working dir 
work_dir = os.path.join(data_dir, subject_id,  
			'preprocessed/anat') 

if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

gm_labels = [3,8,42,17,18,53,54,11,12,13,26,50,
	     51,52,58,9,10,47,48,49,16,28,60]

# get the freesurfer recon_all segmentation output
aseg_mgz = os.path.join(freesurfer_dir, subject_id, 'mri', 
			'aseg.mgz')

# convert *mgz into *nii.gz
mricon = fs.MRIConvert(in_file  = aseg_mgz,
		       out_file = 'aseg.nii.gz',
		       out_type = 'niigz').run()

aseg_nifti  = os.path.abspath('aseg.nii.gz')

###### Step # 1: binarize aseg.nii.gz via GM labels
coolBinarize = fs.Binarize()
coolBinarize.inputs.in_file     = aseg_nifti
coolBinarize.inputs.match       = gm_labels
coolBinarize.out_type           = 'nii.gz'
coolBinarize.inputs.binary_file = 'brain_gmseg.nii.gz'
coolBinarize.run()

# define working dir
work_dir = os.path.join(data_dir, subject_id,  
			'preprocessed/func/connectivity') 

if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

###### Step #2: normalize GM mask to MNI space

gm_mask  = os.path.join(data_dir, subject_id,
		        'preprocessed/anat', 
		        'brain_gmseg.nii.gz')

mni_temp = os.path.join('/usr/share/fsl/5.0/data/standard', 
			'MNI152_T1_1mm_brain.nii.gz')

at                          = ants.ApplyTransforms()
at.inputs.input_image       = gm_mask
at.inputs.reference_image   = mni_temp

# design transformation matrices 
if subject_id[5:8] == 'd00':
	# (T1_d00 -->> mni)

	trans_dir = os.path.join(data_dir, subject_id, 
				 'preprocessed/anat/transforms2mni') 

	at.inputs.transforms             = [os.path.join(trans_dir,
					   'transform1Warp.nii.gz'),
		                            os.path.join(trans_dir,
					   'transform0GenericAffine.mat')]
	
	at.inputs.invert_transform_flags = [False, False]

else: 
	# (T1_dXX -->> T1_d00 -->> mni)

	subject_day00 = subject_id[0:5] + 'd00'
	
	# fsl-flirt transform matrices (T1_XX -->> T1_d00)
	flirt_dir = os.path.join(data_dir, subject_id,
				 'preprocessed/anat/transforms2day00')

	# ants transform matrices (T1_d00 -->> mni3mm)
	ants_dir = os.path.join(data_dir, subject_day00,  
				'preprocessed/anat/transforms2mni')

	at.inputs.transforms  = [os.path.join(ants_dir, 						   						   'transform1Warp.nii.gz'),
	      		         os.path.join(ants_dir, 						   						   'transform0GenericAffine.mat'),
			         os.path.join(flirt_dir,
				           'transform_day00_itk.mat')]	
	
	at.inputs.invert_transform_flags = [False, False, False]	

at.inputs.interpolation          = 'BSpline'
at.inputs.output_image           = 'gm_mni1.nii.gz'
at.run()


###### Step #3: resampling MNI1mm -->> MNI3mm
flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
flt.inputs.apply_isoxfm = 3.0
flt.inputs.in_file      = os.path.join(data_dir, subject_id,
		                      'preprocessed/func/connectivity',
				      'gm_mni1.nii.gz')
flt.inputs.reference    = os.path.join('/nobackup/ilz2/bayrak',
				       'MNI152_T1_3mm_brain.nii.gz')
flt.inputs.output_type  = "NIFTI_GZ"
flt.inputs.out_file     = os.path.join(data_dir, subject_id,
		                       'preprocessed/func/connectivity',
				       'gm_prob_mni3.nii.gz')
flt.run()


###### Step #4: get rest mask to exclude voxels having 0's 
image_rest4D = os.path.join(data_dir, subject_id, 
         	            'preprocessed/func', 
		            'rest_preprocessed2mni_sm.nii.gz') 

automask = afni.Automask()
automask.inputs.in_file    = image_rest4D
automask.inputs.outputtype = 'NIFTI_GZ'
automask.inputs.brain_file = 'rest_masked_mni3.nii.gz'
automask.inputs.out_file   = 'rest_mask_mni3.nii.gz'
automask.run()  

