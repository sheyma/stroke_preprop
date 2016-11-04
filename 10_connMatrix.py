import os, sys
from nipype.interfaces.fsl import MultiImageMaths
from nipype.interfaces.fsl.maths import MathsCommand

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects'

###### get GM mask at group level ##########

# write subject-id's into a list
fname = '/nobackup/ilz2/bayrak/documents/cool_hc.txt'
with open(fname) as f:
    content = f.readlines()
sbj_list = [x.strip('\n') for x in content]

# write GM mask filenames into a list
msk_list = []
tmp_str  = []
i = 0
for sbj in sbj_list:
	msk_sbj = os.path.join(data_dir, sbj,
			       'preprocessed/func/connectivity',
			       'gm_mask_mni3.nii.gz')
	msk_list.append(msk_sbj)
	i += 1
	if i != 1:
		tmp_str.append('-add %s ') 

tmp_str.append(('-div %s' % len(msk_list)))	
op_string = " ".join((tmp_str))

# get average probabilistic GM of all subjects
gm_ave_grp = os.path.join('/nobackup/ilz2/bayrak/subjects_group',
			   'gm_mni3_ave.nii.gz')
maths = MultiImageMaths()
maths.inputs.in_file       = msk_list[0]
maths.inputs.op_string     = op_string
maths.inputs.operand_files = msk_list[1:]
maths.inputs.out_file      = gm_ave_grp
#maths.run()

# get mask out of average probabilistic GM
gm_ave_mask = os.path.join('/nobackup/ilz2/bayrak/subjects_group',
			   'bla.nii.gz')
binarize = MathsCommand()
binarize.inputs.args     = '-thr 1.0 -bin'
binarize.inputs.in_file  = gm_ave_grp
binarize.inputs.out_file = gm_ave_mask
binarize.run()






