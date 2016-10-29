import os, sys
import nipype.interfaces.freesurfer as fs
import nibabel as nb
import numpy as np
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects'

# subject id
#subject_id = 'hc01_d00'
subject_id = sys.argv[1]

# freesurfer dir for recon_all outputs
freesurfer_dir = '/nobackup/ilz2/bayrak/freesurfer'

# define working dir
work_dir = os.path.join(data_dir, subject_id,  
			'preprocessed/func/connectivity') 

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

# WAY 1

coolBinarize = fs.Binarize()
coolBinarize.inputs.in_file     = aseg_nifti
coolBinarize.inputs.match       = gm_labels
coolBinarize.out_type           = 'nii.gz'
coolBinarize.inputs.binary_file = 'gm_mask_anat.nii.gz'
coolBinarize.run()

######
mni_temp = os.path.join('/nobackup/ilz2/bayrak',
			'MNI152_T1_3mm_brain.nii.gz')

gm_mask = os.path.abspath('gm_mask_anat.nii.gz')

trans_dir = os.path.join(data_dir, subject_id, 
			 'preprocessed/anat/transforms2mni') 

at = ants.ApplyTransforms()
at.inputs.input_image            = gm_mask
at.inputs.transforms             = [os.path.join(trans_dir,
				   'transform1Warp.nii.gz'),
                                    os.path.join(trans_dir,
				   'transform0GenericAffine.mat')]
at.inputs.reference_image        = mni_temp
at.inputs.interpolation          = 'BSpline'
at.inputs.invert_transform_flags = [False, False]
at.inputs.output_image           = 'gm_mask_MNI.nii.gz'

at.run()


