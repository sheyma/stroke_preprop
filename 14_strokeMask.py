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

# subject_id = 'sd01_d00'
subject_id = sys.argv[1]
data_dir   = '/nobackup/ilz2/bayrak/subjects/'
gm_mask    = '/nobackup/ilz2/bayrak/subjects_group/mni3_rest_gm_mask.nii.gz'

#X = 'd00'
X          = sys.argv[2]   ######  LESION DAY ######## 
les_mask   = os.path.join(data_dir, subject_id[0:5]+X, 'lesion', 
                          'lesion_mask_mni.nii.gz')

# write subject-id's into a list
fname = '/nobackup/ilz2/bayrak/documents/cool_sd.txt'
with open(fname) as f:
    content = f.readlines()
sbj_list = [x.strip('\n') for x in content]


def individual_rest_mask_generation(data_dir, sbj_list):
    for sbj in sbj_list:

        print sbj    

        work_dir_trf = os.path.join(data_dir, sbj,  
                                   'preprocessed/func/connectivity')

        if not os.path.exists(work_dir_trf):
            os.makedirs(work_dir_trf)
        os.chdir(work_dir_trf)

        image_rest4D = os.path.join(data_dir, sbj, 
             	            'preprocessed/func', 
		                    'rest_preprocessed2mni_sm.nii.gz') 

        automask = afni.Automask()
        automask.inputs.in_file    = image_rest4D
        automask.inputs.outputtype = 'NIFTI_GZ'
        automask.inputs.brain_file = 'rest_masked_mni3.nii.gz'
        automask.inputs.out_file   = 'rest_mask_mni3.nii.gz'
        automask.run()  


#individual_rest_mask_generation(data_dir, sbj_list)

 
#### Step 1 ############################################################

# define working dir
work_dir = os.path.join('/nobackup/ilz2/bayrak/stroke_intrasubject',
                        subject_id[0:4]) 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

rest_list = []
rest_str  = []
i = 0

print "intra-subject rest mask ..."
for name in glob.glob(data_dir + subject_id[0:5] + '*' +
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

