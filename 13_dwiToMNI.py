import os, sys
import nipype.interfaces.ants as ants
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl
from subprocess import call
from nipype.interfaces.c3 import C3dAffineTool

# data dir's 
data_dir   = '/nobackup/ilz2/bayrak/subjects'

mni_temp = os.path.join('/nobackup/ilz2/bayrak/subjects_group',
			            'MNI152_T1_3mm_brain.nii.gz')

# user given subject_id 
subject_id = sys.argv[1]

# define working dir
work_dir = os.path.join(data_dir, subject_id, 'lesion')

# go into work dir
os.chdir(work_dir)

# get dwi scan
dwi_image = os.path.join(data_dir, subject_id,
			            'nifti/dwi', 'dwi.nii.gz')

# get anat scan, where subject's T1 normalized to mni
#X = 'd01' 
X = sys.argv[2]

subject_dayX = subject_id[0:5] + X

T1_image = os.path.join(data_dir, subject_dayX, 
			            'preprocessed/anat', 'brain.nii.gz')

print dwi_image
print T1_image

##### Step 1, linear registration (dwi -->> T1) ###########################

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

flt = fsl.FLIRT()
flt.inputs.in_file   = 'dwi_brain.nii.gz'
flt.inputs.reference = T1_image
flt.inputs.dof 	     = 6
flt.inputs.out_matrix_file = 'transform_dwiToT1.mat'
flt.inputs.out_file        = 'dwi_brain_ToT1.nii.gz'
flt.inputs.output_type     = "NIFTI_GZ"
flt.run()

# convert fsl flirt out into itk format for ants later
c3 = C3dAffineTool()
c3.inputs.transform_file  = 'transform_dwiToT1.mat'
c3.inputs.itk_transform   = 'transform_dwiToT1_itk.mat'
c3.inputs.reference_file  = T1_image
c3.inputs.source_file     = dwi_image
c3.inputs.fsl2ras         = True
c3.run()

##### Step 2, apply all transforms (dwi -->> T1 -->  mni) #####################

# ants transform matrices (T1d00 -->> mni1mm)
ants_dir = os.path.join(data_dir, subject_dayX,  
		                'preprocessed/anat/transforms2mni')

flirt_dir = os.path.join(data_dir, subject_id,
			             'lesion/transforms2anat')

lesion_mask = os.path.join(data_dir, subject_id, 'lesion',
			               '%s_dwi00_lesionMask.nii.gz' % (subject_id[0:4]))

print ants_dir
print flirt_dir
print lesion_mask

at			               = ants.ApplyTransforms()
at.inputs.input_image      = lesion_mask
at.inputs.transforms	   = [os.path.join(ants_dir, 'transform1Warp.nii.gz'),
	      		         os.path.join(ants_dir, 'transform0GenericAffine.mat'),
	 		             os.path.join(flirt_dir, 'transform_dwiToT1_itk.mat')]
at.inputs.reference_image  = mni_temp
at.inputs.interpolation    = 'NearestNeighbor'

at.inputs.invert_transform_flags = [False, False, False]
at.inputs.output_image     = os.path.join(data_dir, subject_id, 'lesion',
					                      'lesion_mask_mni.nii.gz')
at.run()

