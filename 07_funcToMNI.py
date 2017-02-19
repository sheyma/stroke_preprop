"""
    # coregistration from functional space to mni template
    # without the optional arg: rest -> T1 -> mni
    # with the optional arg: rest -> rest(dayXX) -> T1 -> mni

mni_temp   = '/data/pt_mar006/subjects_group/MNI152_T1_3mm_brain.nii.gz'    
data_dir   = '/data/pt_mar006/subjects'
subject_id = 'sd51_d00'
dayXX      = 'd01'
Usage:
    $ python 07_funcToMNI.py <min_temp> <data_dir> <subject_id> [dayXX]
"""
import os, sys
import nipype.interfaces.ants as ants

mni_temp   = sys.argv[1]
data_dir   = sys.argv[2]
subject_id = sys.argv[3]

# define working dir
work_dir = os.path.join(data_dir, subject_id, 'preprocessed/func') 
os.chdir(work_dir)

# get preprocessed functional data in native space
img_rest = os.path.join(data_dir, subject_id,
			'preprocessed/func/rest_preprocessed.nii.gz')

# initialize ants parameters
at			   = ants.ApplyTransforms()
at.inputs.input_image_type = 3
at.inputs.input_image      = img_rest
at.inputs.reference_image  = mni_temp
at.inputs.output_image     = os.path.abspath('rest_preprocessed2mni.nii.gz')

if len(sys.argv) > 4:
    # coregisteration ( rest -> rest(dayXX) -> T1 -> mni )
    # e.g. dayXX = 'd01'
    dayXX = sys.argv[4] 
    
    ants_dir = os.path.join(data_dir, subject_id[:5] + dayXX, 
                            'preprocessed/anat/transforms2mni/')
    bbre_dir = os.path.join(data_dir, subject_id[:5] + dayXX,
                            'preprocessed/func/coregister/transforms2anat')
    flir_dir = os.path.join(data_dir, subject_id,
                            'preprocessed/func/transforms2rest' + dayXX[1:])
    
    at.inputs.transforms    = [os.path.join(ants_dir,
                                            'transform1Warp.nii.gz'),
                               os.path.join(ants_dir,
                                            'transform0GenericAffine.mat'),
                               os.path.join(bbre_dir, 'rest2anat_itk.mat'),
                               os.path.join(flir_dir, 'transform_day'
                                            + dayXX[1:] + '_itk.mat')]
    at.inputs.interpolation = 'NearestNeighbor'
    at.inputs.invert_transform_flags = [False, False, False, False]
    print at.cmdline
    at.run()
    
else:
    # coregisteration ( rest -> T1 -> mni )
    
    ants_dir = os.path.join(data_dir, subject_id,  
                            'preprocessed/anat/transforms2mni')
    bbre_dir = os.path.join(data_dir, subject_id,
                            'preprocessed/func/coregister/transforms2anat')
 
    at.inputs.transforms       = [os.path.join(ants_dir, 						   				           'transform1Warp.nii.gz'),
                                   os.path.join(ants_dir,
                                               'transform0GenericAffine.mat'),
                                   os.path.join(bbre_dir, 						   	    'rest2anat_itk.mat')]
    at.inputs.interpolation    = 'NearestNeighbor'
    at.inputs.invert_transform_flags = [False, False, False]
    print at.cmdline
    at.run()
