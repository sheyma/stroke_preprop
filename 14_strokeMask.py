"""
    get intra-subject rest mask for a stroke patient's different day measures 
    (subject_mask_01.nii.gz), multiply this rest mask with the group-level-
    healty-control-rest-and-gm-mask (subject_mask_02.nii.gz), find intersection
    of stroke lesion on top of previous mask (subject_mask_03.nii.gz), finally
    subtract lesion intersection from the mask (subject_mask_final.nii.gz)

gm_mask    = '/data/pt_mar006/subjects_group/mni3_rest_gm_mask.nii.gz'
data_dir   = '/data/pt_mar006/subjects/'
subject_id = 'sd51'
X          = 'd00'  #### lesion day

Usage:
    $ python 14_strokeMask.py  <gm_mask> <data_dir> <subject_id> <X>
"""
import os, sys, glob
from nilearn import masking
import numpy as np
from hcp_corr import corrcoef_upper
import h5py
import numexpr as ne
from nipype.interfaces.fsl import MultiImageMaths
from nipype.interfaces.fsl.maths import MathsCommand
from nipype.interfaces import afni
from hcp_corr import corrcoef_upper, N_original, upper_to_down


gm_mask    = sys.argv[1]
data_dir   = sys.argv[2]
subject_id = sys.argv[3]
X          = sys.argv[4]  

les_mask   = os.path.join(data_dir, subject_id + '_' + X, 
                         'lesion/lesion_mask_mni.nii.gz')
 
#### Step 1 ############################################################

# define working dir
work_dir = os.path.join('/data/pt_mar006/stroke_intrasubject', subject_id) 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

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

# get intra-subject rest mask
maths = MultiImageMaths()
maths.inputs.in_file       = rest_list[0]
maths.inputs.op_string     = op_string_rest
maths.inputs.operand_files = rest_list[1:]
maths.inputs.out_file      = 'subject_mask_01.nii.gz'
maths.run()

###### Step 2 #########################################

maths = MultiImageMaths()
maths.inputs.in_file       = 'subject_mask_01.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = gm_mask
maths.inputs.out_file      = 'subject_mask_02.nii.gz'
maths.run()

###### Step 3 ##########################################
print "get lesion mask..."
print les_mask

maths = MultiImageMaths()
maths.inputs.in_file       = 'subject_mask_02.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = les_mask
maths.inputs.out_file      = 'subject_mask_03.nii.gz'
maths.run()

maths = MultiImageMaths()
maths.inputs.in_file       = 'subject_mask_02.nii.gz'
maths.inputs.op_string     = '-sub %s'
maths.inputs.operand_files = 'subject_mask_03.nii.gz'
maths.inputs.out_file      = 'subject_mask_final.nii.gz'
maths.run()

###### Step 4 ############################################

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

mask = os.path.abspath('subject_mask_final.nii.gz')

for img_rest in glob.glob(data_dir + subject_id[0:5] + '*' +
                      '/preprocessed/func/' +
                      'rest_preprocessed2mni_sm.nii.gz' ):
    print img_rest
    [voxel_zeros, t_series] = mask_check(img_rest, mask)
    if voxel_zeros != 0:
        print "FUCK"
        sys.exit(1)    


