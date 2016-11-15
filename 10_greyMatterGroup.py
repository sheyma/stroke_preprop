"""
get GM mask at group level 
get rest mask at group level
"""
import os, sys
from nipype.interfaces.fsl import MultiImageMaths
from nipype.interfaces.fsl.maths import MathsCommand

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects'

# define working dir 
work_dir = os.path.join('/nobackup/ilz2/bayrak/subjects_group') 

if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

# write subject-id's into a list
fname = '/nobackup/ilz2/bayrak/documents/cool_hc.txt'
with open(fname) as f:
    content = f.readlines()
sbj_list = [x.strip('\n') for x in content]

############# Step 1 ###########################################
# write GM probabilistic mask filenames into a list
gm_list = []
gm_str  = []

rest_list = []
rest_str  = []

i = 0
for sbj in sbj_list:
	gm_prob = os.path.join(data_dir, sbj,
			       'preprocessed/func/connectivity',
			       'gm_prob_mni3.nii.gz')
	gm_list.append(gm_prob)
	
	rest_msk = os.path.join(data_dir, sbj,
				'preprocessed/func/connectivity',
				'rest_mask_mni3.nii.gz')
	rest_list.append(rest_msk)

	i += 1
	if i != 1:
		gm_str.append('-add %s ') 
		rest_str.append('-mul %s')

# define final operational strings to be used
gm_str.append(('-div %s' % len(gm_list)))	
op_string_gm   = " ".join((gm_str))
op_string_rest = " ".join((rest_str))

# get group level probabilistic GM by averaging
maths = MultiImageMaths()
maths.inputs.in_file       = gm_list[0]
maths.inputs.op_string     = op_string_gm
maths.inputs.operand_files = gm_list[1:]
maths.inputs.out_file      = 'gm_prob_mni3_ave.nii.gz'
maths.run()
#print maths.cmdline

# get GM mask (binarize the probabilistic GM map)
binarize = MathsCommand()
binarize.inputs.args     = '-thr  0.30 -bin'
binarize.inputs.in_file  = 'gm_prob_mni3_ave.nii.gz'
binarize.inputs.out_file = 'gm_prob_mni3_ave_mask.nii.gz'
binarize.run()

# get group level resting mask by multiplying individual ones
maths = MultiImageMaths()
maths.inputs.in_file       = rest_list[0]
maths.inputs.op_string     = op_string_rest
maths.inputs.operand_files = rest_list[1:]
maths.inputs.out_file      = 'rest_mask_mni3_ave.nii.gz'
maths.run()

############# Step 2 #######################################
maths = MultiImageMaths()
maths.inputs.in_file       = 'gm_prob_mni3_ave_mask.nii.gz'
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = 'rest_mask_mni3_ave.nii.gz'
maths.inputs.out_file      = 'mni3_rest_gm_mask.nii.gz'
maths.run()

