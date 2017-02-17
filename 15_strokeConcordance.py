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

#subject_id = 'sd01_d00'
subject_id = sys.argv[1]

data_dir   = '/data/pt_mar006/subjects/'
work_dir   = os.path.join('/data/pt_mar006/stroke_intrasubject',
                          subject_id[0:4])
os.chdir(work_dir)

image_mask = os.path.abspath('subject_mask_final.nii.gz')
print "get mask...", image_mask

##### Step 1, get all connectivity matrices of given subject #############

corr_All = []

for image_rest in glob.glob(data_dir + subject_id[0:5] + '*' +
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

##### Step 2, get concordance value per voxel ############################

W_voxels = [] 
p_voxels = []
Fdist_voxels = []

ccc_voxels = []

ICC_voxels = []

for i in range(0, corr_All.shape[0]):
    
    # Kendall's W    
    W, p, Fdist = IPN_kendallW(corr_All[:,i,:]) 
    W_voxels.append(W)
    p_voxels.append(p)
    Fdist_voxels.append(Fdist)

    # Concordance Correlation Coefficient
    ccc = IPN_ccc(corr_All[:,i,:]) 
    ccc_voxels.append(ccc)

    # Interclass Correlation Coefficient
    
    ICC = IPN_icc(corr_All[:,i,:], cse=3, typ='k')
    ICC_voxels.append(ICC)

    #print i, W, ccc, ICC

np.savetxt('/data/pt_mar006/RkenW_tied_python.txt', W_voxels)

np.savetxt('/data/pt_mar006/Rccc_python.txt', ccc_voxels)

np.savetxt('/data/pt_mar006/Ricc_python.txt', ICC_voxels)










