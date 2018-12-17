"""
    registering lesions (identified on dwi) to mni template
    a linear (dwi -> T1) a nonlinear (T1 -> mni) registration used at single interpol.
    (note: X is the day at which T1 was normalized to mni previously,
    subject_id has the day info, at which the lesion was deliniated)

mni_temp   = '/data/pt_mar006/subjects_group/MNI152_T1_3mm_brain.nii.gz'
data_dir   = '/data/pt_mar006/subjects'
subject_id = 'sd51_d00'
X          = 'd01'

Usage: 
    $ python 13_dwiToMNI.py <mni_temp> <data_dir> <subject_id> <X>
"""
import os, sys
import nipype.interfaces.ants as ants
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl
from subprocess import call
from nipype.interfaces.c3 import C3dAffineTool

mni_temp   = sys.argv[1]
data_dir   = sys.argv[2]
subject_id = sys.argv[3]
X          = sys.argv[4]

# define working dir
work_dir = os.path.join(data_dir, subject_id, 'lesion')
os.chdir(work_dir)

dwi_image = os.path.join(data_dir, subject_id, 'nifti/dwi', 'dwi.nii.gz')

subject_dayX = subject_id[0:5] + X

T1_image     = os.path.join(data_dir, subject_dayX, 
			    'preprocessed/anat', 'brain.nii.gz')
print dwi_image
print T1_image

##### Step 1, linear registration (dwi -->> T1) ###############

# define working dir for transform matrices
work_dir_trf = os.path.join(data_dir, subject_id,  
            	            'lesion/transforms2anat')

if not os.path.exists(work_dir_trf):
	os.makedirs(work_dir_trf)
os.chdir(work_dir_trf)

##### skull-stripping dwi image
from nipype.interfaces import fsl
btr = fsl.BET()
btr.inputs.in_file = dwi_image
btr.inputs.frac    = 0.25
btr.out_file       = 'dwi_brain.nii.gz'
btr.run() 

##### registering dwi to T1
flt = fsl.FLIRT()
flt.inputs.in_file         = 'dwi_brain.nii.gz'
flt.inputs.reference       = T1_image
flt.inputs.dof 	           = 6
flt.inputs.out_matrix_file = 'transform_dwiToT1.mat'
flt.inputs.out_file        = 'dwi_brain_ToT1.nii.gz'
flt.inputs.output_type     = "NIFTI_GZ"
flt.run()

# convert fsl-flirt out into itk format for ants later
c3 = C3dAffineTool()
c3.inputs.transform_file  = 'transform_dwiToT1.mat'
c3.inputs.itk_transform   = 'transform_dwiToT1_itk.mat'
c3.inputs.reference_file  = T1_image
c3.inputs.source_file     = dwi_image
c3.inputs.fsl2ras         = True
c3.run()

##### Step 2, apply all transforms (dwi -->> T1 -->  mni) ####

# ants transform matrices (T1 -->> mni1mm)
ants_dir = os.path.join(data_dir, subject_dayX,  
                       'preprocessed/anat/transforms2mni')

# flirt transform matrices (dwi -->> T1)
flirt_dir = os.path.join(data_dir, subject_id,
    	                 'lesion/transforms2anat')

lesion_mask = os.path.join(data_dir, subject_id, 'lesion',
			   %s_dwi00_lesionMask.nii.gz' % (subject_id[0:4]))

# lesion (@dwi) --> T1 --> mni 
at		      = ants.ApplyTransforms()
at.inputs.input_image = lesion_mask
at.inputs.transforms  = [os.path.join(ants_dir, 'transform1Warp.nii.gz'),
	      		 os.path.join(ants_dir, 'transform0GenericAffine.mat'),
	 		 os.path.join(flirt_dir, 'transform_dwiToT1_itk.mat')]
at.inputs.output_image = os.path.join(data_dir, subject_id, 'lesion',
			 'lesion_mask_mni.nii.gz')

at.inputs.interpolation    = 'NearestNeighbor'
at.inputs.reference_image  = mni_temp
at.inputs.invert_transform_flags = [False, False, False]
at.run()

