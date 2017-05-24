"""
    dilate the lesion mask on mni space,
    get intra-subject rest mask for a stroke patient's different day measures, 
    multiply this rest mask with the group-level-healty-gm-mask, 
    find the intersection of stroke lesion along the gm-mask,
    subtract lesion intersection from the mask 

data_dir   = '/data/pt_mar006/subjects/'
out_dir    = '/data/pt_mar006/subjects_masks' 
gm_mask    = '/data/pt_mar006/subjects_group/mni3_rest_gm_mask.nii.gz'
subject_id = 'sd27'
X          = 'd00'  #### lesion day

Usage:
	$ python 14_strokeMask_dilated.py <d_dir> <o_dir> <gm_mask> <sbj_id> <X>	
"""

import os, sys, glob
from nipype.interfaces.fsl.maths import DilateImage
from nipype.interfaces.fsl import MultiImageMaths
from nilearn import masking
import numpy as np

data_dir   = sys.argv[1]
out_dir    = sys.argv[2]
gm_mask    = sys.argv[3]
subject_id = sys.argv[4]
X          = sys.argv[5]  

lesion_mask   = os.path.join(data_dir, subject_id + '_' + X, 
                            'lesion/lesion_mask_mni.nii.gz')

# define working dir
work_dir = os.path.join(out_dir, subject_id) 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)


lesion_mask_dil = os.path.join(work_dir, 
			       'lesion_mask_mni_dilated.nii.gz')

##### Step 1: dilating lesion mask #############################
dilate = DilateImage()
dilate.inputs.in_file      = lesion_mask
dilate.inputs.operation    = 'modal'
dilate.inputs.kernel_shape = 'gauss'
dilate.inputs.kernel_size  = 3
dilate.inputs.out_file     = lesion_mask_dil
print dilate.cmdline
dilate.run()

##### Step 2: get intra-subject rest mask #######################
rest_list = []
rest_str  = []
i = 0
print "intra-subject rest mask ..."
for name in glob.glob(data_dir + subject_id + '*' +
                      '/preprocessed/func/connectivity/' +
                      'rest_mask_mni3.nii.gz' ):
    print name
    rest_list.append(name)
    i += 1
    if i != 1:
        rest_str.append('-mul %s')
op_string_rest = " ".join((rest_str))

print os.getcwd()
maths = MultiImageMaths()
maths.inputs.in_file       = rest_list[0]
maths.inputs.op_string     = op_string_rest
maths.inputs.operand_files = rest_list[1:]
maths.inputs.out_file      = 'intra_rest_mask.nii.gz'
maths.run()

##### Step 3: mask on control group #############################
maths = MultiImageMaths()
maths.inputs.in_file       = 'intra_rest_mask.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = gm_mask
maths.inputs.out_file      = 'subject_gm_mask.nii.gz'
maths.run()

##### Step 4: lesion mask along gray matter #####################
print "get lesion mask..."
print lesion_mask_dil

maths = MultiImageMaths()
maths.inputs.in_file       = 'subject_gm_mask.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = lesion_mask_dil
maths.inputs.out_file      = 'lesion_mask_mni_dilated_gm.nii.gz'
maths.run()

##### Step 5: gm mask without lesion ############################ 
maths = MultiImageMaths()
maths.inputs.in_file       = 'subject_gm_mask.nii.gz'
maths.inputs.op_string     = '-sub %s'
maths.inputs.operand_files = 'lesion_mask_mni_dilated_gm.nii.gz'
maths.inputs.out_file      = 'subject_gm_mask_no_lesion.nii.gz'
maths.run()

##### Step 6: check zeros-voxels ################################
def mask_check(rest, mask):
	"""
	rest: 4D nifti-filename
	mask: 3D nifti-filename
	"""
	matrix = masking.apply_mask(rest, mask)
	matrix = matrix.T
	cnt_zeros = 0 
	for i in range(0, matrix.shape[0]):
		if np.count_nonzero(matrix[i, :]) == 0:
			cnt_zeros += 1
	return cnt_zeros, matrix

mask = os.path.abspath('subject_gm_mask_no_lesion.nii.gz')

for img_rest in glob.glob(data_dir + subject_id[0:5] + '*' +
                      '/preprocessed/func/' +
                      'rest_preprocessed2mni_sm.nii.gz' ):
    [voxel_zeros, t_series] = mask_check(img_rest, mask)
    print img_rest, np.shape(voxel_zeros)

    if voxel_zeros != 0:
        print "FUCK"
        sys.exit(1) 

