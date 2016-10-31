import os, sys
import nibabel as nb
import matplotlib.pyplot as plt

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects'

###### STEP 1 - OPTION 1  #########################

# get subject list
fname = '/nobackup/ilz2/bayrak/documents/cool_hc.txt'
with open(fname) as f:
    content = f.readlines()
sbj_list = [x.strip('\n') for x in content]

# get mask list of subjects
msk_list = []
for sbj in sbj_list:
	msk_sbj = os.path.join(data_dir, sbj,
			       'preprocessed/func/connectivity',
			       'gm_mask_MNI_Neigh.nii.gz')
	msk_list.append(msk_sbj)

# define an operational string for fsl.MultiImageMaths
tmp = []
for msk in range(1, len(msk_list)):
	tmp.append('-mul %s ')  
op_string = " ".join((tmp))

# get a mask by multipylying individual brain masks
from nipype.interfaces.fsl import MultiImageMaths
maths = MultiImageMaths()
maths.inputs.in_file       = msk_list[0]
maths.inputs.op_string     = op_string
maths.inputs.operand_files = msk_list[1:]
maths.inputs.out_file      = 'bla.nii.gz'
#maths.run()
#print maths.cmdline


###### STEP 2 - #####################################

from nilearn import masking
import numpy as np
from hcp_corr import corrcoef_upper, N_original, upper_to_down
import numexpr as ne
import nibabel as nb

# subject id
subject_id = 'hc05_d00'

image_rest4D = os.path.join(data_dir, subject_id, 
         	     'preprocessed/func', 
		     'rest_preprocessed2mni_sm.nii.gz') 

image_mask3D = '/home/raid/bayrak/devel/stroke_preprop/bla.nii.gz'


# get indices of voxels, which are equal to 1 in mask

mask_array = nb.load(image_mask3D).get_data()
voxel_x    = np.where(mask_array==1)[0]
voxel_y    = np.where(mask_array==1)[1]
voxel_z    = np.where(mask_array==1)[2]

print voxel_x, np.shape(voxel_x)
print voxel_y, np.shape(voxel_y)
print voxel_z, np.shape(voxel_z)


image_array = nb.load(image_rest4D).get_data()

A = np.zeros((len(voxel_x), 145))
for i in range(0, len(voxel_x)):
	A[i,:] = image_array[voxel_x[i], voxel_y[i], voxel_z[i], :]
	if np.count_nonzero(A[i,:]) == 0:
		print i


t_series = masking.apply_mask(image_rest4D, image_mask3D)

t_series = np.array(t_series).T

#print "subject_id: ", subject_id
#print "t-series SHAPE :", np.shape(t_series)

#print np.where(t_series[1,:]==0)

#corr_upper = corrcoef_upper(t_series)
#N_orig     = N_original(corr_upper)
#corr_upper.resize([N_orig, N_orig])
#corr       = upper_to_down(corr_upper)
#print corr
#print np.isnan(corr).any()

## corr_upper should not consume mem, change to corr later!

## Step 3, Fisher's r-to-z transfrom 
#def fisher_r2z(R):
#    return ne.evaluate('arctanh(R)')


