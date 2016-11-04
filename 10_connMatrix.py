import os, sys
import nibabel as nb
import matplotlib.pyplot as plt
from nipype.interfaces.fsl import MultiImageMaths
import hcp_corr 
import numexpr as ne

#, Fisher's r-to-z transfrom 
def fisher_r2z(R):
    return ne.evaluate('arctanh(R)')

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects'


# load subjects via nibabel



###### STEP #1: get GM mask at group level ##########

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
		tmp_str.append('-mul %s ') 
	
op_string = " ".join((tmp_str))

# get GM mask at group level by multiplication
gm_mask_grp = os.path.join('/nobackup/ilz2/bayrak/subjects_group',
			   'gm_mask_mni3_group.nii.gz')
maths = MultiImageMaths()
maths.inputs.in_file       = msk_list[0]
maths.inputs.op_string     = op_string
maths.inputs.operand_files = msk_list[1:]
maths.inputs.out_file      = gm_mask_grp
#maths.run()

###### STEP #2: get time-series from GM ################
from nilearn import masking
import numpy as np
import nibabel as nb
from nipype.interfaces.fsl import maths

# subject id
subject_id = 'hc05_d00'

# define working dir
work_dir = os.path.join(data_dir, subject_id,  
			'preprocessed/func/connectivity') 

if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

image_rest4D = os.path.join(data_dir, subject_id, 
         	            'preprocessed/func', 
		            'rest_preprocessed2mni_sm.nii.gz') 

image_mask3D = gm_mask_grp

fsl_masking = maths.ApplyMask()
fsl_masking.inputs.in_file = image_rest4D
fsl_masking.inputs.mask_file = image_mask3D
fsl_masking.inputs.internal_datatype = 'float'
fsl_masking.inputs.output_type = 'NIFTI_GZ'
fsl_masking.inputs.out_file = 'rest_prepro_gm.nii.gz'
fsl_masking.inputs.output_datatype = 'float' 
#fsl_masking.run() 

# get indices of voxels, which are equal to 1 in mask
mask_array = nb.load(image_mask3D).get_data()
voxel_x    = np.where(mask_array==1)[0]
voxel_y    = np.where(mask_array==1)[1]
voxel_z    = np.where(mask_array==1)[2]

print voxel_x, np.shape(voxel_x)
print voxel_y, np.shape(voxel_y)
print voxel_z, np.shape(voxel_z)

###### Step #3: #############################
######
# niftis:
# gm_mask_grp (=image_mask3D): dtype('<f8')
# image_rest4D: dtype('<f8')
# 'rest_prepro_gm.nii.gz': dtype('<f4') !!!

# t-series DATA TYPE IS dtype('float64') !!!!

#t_series = masking.apply_mask(image_rest4D, image_mask3D, dtype='float64')

#t_series = np.array(t_series).T

#print "subject_id: ", subject_id
#print "t-series SHAPE :", np.shape(t_series)
#print "check if there is NaN in t-series: ", np.isnan(t_series).any()

#j = 0
#for i in range(0, np.shape(t_series)[0]):
#	if np.all(t_series[i,:] == np.zeros((145))) == True:
#		j +=1
#print j 

#corr_upper = hcp_corr.corrcoef_upper(t_series)
#N_orig     = hcp_corr.N_original(corr_upper)
#corr_upper.resize([N_orig, N_orig])
#corr       = hcp_corr.upper_to_down(corr_upper)
#print np.shape(corr)
#print np.isnan(corr).any()
#print np.where(np.isnan(corr)==True)
## corr_upper should not consume mem, change to corr later!



