"""
    dilate the lesion mask on mni space to exclude any lesioned voxel effect later,
    get intra-subject epi brain mask for each stroke patient, 
    multiply stroke epi-mask with gm-mask (obtained across healthy controls), 
    find the intersection of the stroke lesion and the gm-mask,
    remove this intersection from the mask 

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
print lesion_mask_dil

###### Step 1: dilating lesion mask #############################
dilate = DilateImage()
dilate.inputs.in_file      = lesion_mask
dilate.inputs.operation    = 'modal'
dilate.inputs.out_file     = lesion_mask_dil
#print dilate.cmdline
dilate.run()

##### Step 2: get intra-subject gm mask #########################

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

maths = MultiImageMaths()
maths.inputs.in_file       = rest_list[0]
maths.inputs.op_string     = op_string_rest
maths.inputs.operand_files = rest_list[1:]
maths.inputs.out_file      = 'rest_intra_mask.nii.gz'
maths.run()

##### Step 3: gm mask lying on health controls ##################

maths = MultiImageMaths()
maths.inputs.in_file       = 'rest_intra_mask.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = gm_mask
maths.inputs.out_file      = 'gm_mask.nii.gz'
maths.run()

##### Step 4: lesions lying on gm ##############################
print "get lesion masks on gm..."

maths = MultiImageMaths()
maths.inputs.in_file       = 'gm_mask.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = lesion_mask_dil
maths.inputs.out_file      = 'lesion_mask_mni_dilated_gm.nii.gz'
maths.run()

maths = MultiImageMaths()
maths.inputs.in_file       = 'gm_mask.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = lesion_mask
maths.inputs.out_file      = 'lesion_mask_mni_gm.nii.gz'
maths.run()

##### Step 5: remove dilated lesion from gm #####################
maths = MultiImageMaths()
maths.inputs.in_file       = 'gm_mask.nii.gz'
maths.inputs.op_string     = '-sub %s'
maths.inputs.operand_files = 'lesion_mask_mni_dilated_gm.nii.gz'
maths.inputs.out_file      = 'gm_mask_no_lesion.nii.gz'
maths.run()

##### Step 6: check whether gm voxels have signals ##############
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

mask = os.path.abspath('gm_mask_no_lesion.nii.gz')

for img_rest in glob.glob(data_dir + subject_id[0:5] + '*' +
                      '/preprocessed/func/' +
                      'rest_preprocessed2mni_sm.nii.gz' ):
    print img_rest
    [voxel_zeros, t_series] = mask_check(img_rest, mask)
    if voxel_zeros != 0:
        print "voxels with zeros time-series!!!"
        sys.exit(1)    
