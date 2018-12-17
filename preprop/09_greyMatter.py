"""
    # for healthy controls:
    get individual GM masks, project to mni space:
    get individual rest masks (3dAutomask)
    
    # for stroke data:
    get individual rest masks (3dAutomask)


#mni_dir = '/data/pt_mar006/subjects_group/'
#freesurfer_dir = '/data/pt_mar006/freesurfer'
#data_dir   = '/data/pt_mar006/subjects'
#subject_id = 'hc01_d00' or 'sd51_d00'

"""
import os, sys
import nipype.interfaces.freesurfer as fs
import nibabel as nb
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
from nipype.interfaces.fsl.maths import MathsCommand
from nipype.interfaces import afni

mni_dir  = sys.argv[1]
freesurfer_dir = sys.argv[2]
data_dir   = sys.argv[3]
subject_id = sys.argv[4]

# define working dir
work_dir_con = os.path.join(data_dir, subject_id,  
		    'preprocessed/func/connectivity') 
if not os.path.exists(work_dir_con):
    os.makedirs(work_dir_con)

# only for healthy control data...
if subject_id[0:2] == 'hc' :
    # define working dir 
    work_dir = os.path.join(data_dir, subject_id,  
			    'preprocessed/anat') 

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

    ###### Step # 1: get gray matter mask by binarizing aparc+aseg with gm labels
    coolBinarize = fs.Binarize()
    coolBinarize.inputs.in_file     = aseg_nifti
    coolBinarize.inputs.match       = gm_labels
    coolBinarize.out_type           = 'nii.gz'
    coolBinarize.inputs.binary_file = 'brain_gmseg.nii.gz'
    coolBinarize.run()

    ###### Step #2: normalize GM mask to MNI (1mm) space
    os.chdir(work_dir_con)

    gm_mask  = os.path.join(data_dir, subject_id,
            		        'preprocessed/anat', 
            		        'brain_gmseg.nii.gz')

    at                          = ants.ApplyTransforms()
    at.inputs.input_image       = gm_mask
    at.inputs.reference_image   = os.path.join(mni_dir, 
                                              'MNI152_T1_1mm_brain.nii.gz' )

    trans_dir = os.path.join(data_dir, subject_id, 
			                 'preprocessed/anat/transforms2mni') 

    at.inputs.transforms = [os.path.join(trans_dir,
			                'transform1Warp.nii.gz'),
                            os.path.join(trans_dir,
			                'transform0GenericAffine.mat')]

    at.inputs.invert_transform_flags = [False, False]

    at.inputs.interpolation          = 'BSpline'
    at.inputs.output_image           = 'gm_mni1.nii.gz'
    at.run()

    ##### Step #3: resampling MNI1mm -->> MNI3mm
    os.chdir(work_dir_con)

    flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
    flt.inputs.apply_isoxfm = 3.0
    flt.inputs.in_file      = 'gm_mni1.nii.gz'
    flt.inputs.output_type  = "NIFTI_GZ"
    flt.inputs.out_file     = 'gm_prob_mni3.nii.gz'
    flt.inputs.reference    = os.path.join(mni_dir, 
                                           'MNI152_T1_3mm_brain.nii.gz')
    flt.run()

##### Step #4: get rest mask to exclude voxels having 0's 
os.chdir(work_dir_con)

image_rest4D = os.path.join(data_dir, subject_id, 
         	                'preprocessed/func', 
		                    'rest_preprocessed2mni_sm.nii.gz') 

automask = afni.Automask()
automask.inputs.in_file    = image_rest4D
automask.inputs.outputtype = 'NIFTI_GZ'
automask.inputs.brain_file = 'rest_masked_mni3.nii.gz'
automask.inputs.out_file   = 'rest_mask_mni3.nii.gz'
automask.run()  

