"""
    # concordance values per voxels calculated over stroke patients

mni_temp   = '/data/pt_mar006/subjects_group/MNI152_T1_3mm_brain.nii.gz'
data_dir   = '/data/pt_mar006/subjects'
out_dir    = '/data/pt_mar006/stroke_intrasubject'
subject_id = 'sd01'
Usage:
    $ python 15_strokeConcordance.py <mni_temp> <data_dir> <out_dir> <subject_id>

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
import nibabel as nb
from concordance import IPN_kendallW, IPN_ccc, IPN_icc

mni_temp   = sys.argv[1]
data_dir   = sys.argv[2]
out_dir    = sys.argv[3]
subject_id = sys.argv[4]

work_dir   = os.path.join(out_dir, subject_id)
os.chdir(work_dir)

image_mask = os.path.abspath('subject_mask_final.nii.gz')
print "get mask...", image_mask

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

#### Step 1, get all connectivity matrices of given subject #########
corr_All = []

for image_rest in glob.glob(data_dir + '/' + subject_id + '*' +
                      '/preprocessed/func/' +
                      'rest_preprocessed2mni_sm.nii.gz' ):
    [voxel_zeros, t_series] = mask_check(image_rest, image_mask)
    corr_upper = corrcoef_upper(t_series) 
    N_orig     = N_original(corr_upper)
    corr_upper.resize([N_orig, N_orig])
    corr       = upper_to_down(corr_upper)
    print image_rest, corr.shape
    corr_All.append(corr)

corr_All = np.array(corr_All)
corr_All = corr_All.T
print 'input data size...', corr_All.shape

##### Step 2, get concordance value per voxel ########################

W_voxels     = [] 
p_voxels     = []
Fdist_voxels = []

ccc_voxels   = []

ICC_voxels   = []

for i in xrange(corr_All.shape[0]):
    
    ## Kendall's W    
    W, p, Fdist = IPN_kendallW(corr_All[:,i,:]) 
    W_voxels.append(W)
    p_voxels.append(p)
    Fdist_voxels.append(Fdist)

    ## Concordance Correlation Coefficient
    ccc = IPN_ccc(corr_All[:,i,:]) 
    ccc_voxels.append(ccc)

    # Interclass Correlation Coefficient
    
    ICC = IPN_icc(corr_All[:,i,:], cse=3, typ='k')
    ICC_voxels.append(ICC)

#### Step 3, save concordance measures as nifti files ##################

mask_array = nb.load(image_mask).get_data()
voxel_x    = np.where(mask_array==1)[0]
voxel_y    = np.where(mask_array==1)[1]
voxel_z    = np.where(mask_array==1)[2]

mni_affine = nb.load(mni_temp).get_affine()

data_temp_W = np.zeros(nb.load(mni_temp).get_data().shape)
data_temp_W[voxel_x, voxel_y, voxel_z] = W_voxels
name_temp_W = os.path.join(work_dir, 'conc_kendall_w.nii.gz')
img_temp_W  = nb.Nifti1Image(data_temp_W, mni_affine)
nb.save(img_temp_W, name_temp_W)

data_temp_ccc  = np.zeros(nb.load(mni_temp).get_data().shape)
data_temp_ccc[voxel_x, voxel_y, voxel_z] = ccc_voxels
name_temp_ccc = os.path.join(work_dir, 'conc_ccc.nii.gz')
img_temp_ccc  = nb.Nifti1Image(data_temp_ccc, mni_affine)
nb.save(img_temp_ccc, name_temp_ccc)

data_temp_ICC  = np.zeros(nb.load(mni_temp).get_data().shape)
data_temp_ICC[voxel_x, voxel_y, voxel_z] = ICC_voxels
name_temp_ICC = os.path.join(work_dir, 'conc_intercc.nii.gz')
img_temp_ICC  = nb.Nifti1Image(data_temp_ICC, mni_affine)
nb.save(img_temp_ICC, name_temp_ICC)

