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

def IPN_ssd(X):
    """
    X is a 1D array, 1xR
    """
    R = len(X)
    ssd = 0
    for k in range(0, R):
        ssd = ssd + np.multiply((X[k+1:R] - X[k]) , (X[k+1:R] - X[k])).sum()
    return ssd

def IPN_ccc(Y):
    """
    Y is a 2D array, NxR
    """
    Ybar = np.mean(Y, axis=0) 
    S = np.cov(Y, rowvar=False, bias=True)
    R = np.shape(Y)[1]
    tmp = np.triu(S,1)
    rc = 2*tmp.ravel(order='F').sum() / ((R-1)*np.trace(S, 0) + IPN_ssd(Ybar))
    return rc

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

data_dir   = '/nobackup/ilz2/bayrak/subjects/'
#subject_id = 'sd01_d00'
subject_id = sys.argv[1]

work_dir   = os.path.join('/nobackup/ilz2/bayrak/stroke_intrasubject',
                          subject_id[0:4])
os.chdir(work_dir)

image_mask = os.path.abspath('subject_mask_final.nii.gz')

print "get mask..."
print image_mask

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
print np.shape(corr_All)     

rc_voxels = []
tmp = []

##### Step 2, calculate CCC for each voxel #######################

for j in range(0, np.shape(corr_All)[1]):
    for i in range(0, np.shape(corr_All)[0]):
        tmp.append(corr_All[i,:,j])
    tmp = np.array(tmp).T
    rc = IPN_ccc(tmp)
    rc_voxels.append(rc)
    tmp = []

print np.shape(rc_voxels)

filena = os.path.join('/nobackup/ilz2/bayrak/stroke_intrasubject',
                      subject_id[0:4], 'ConCor.h5')   
h = h5py.File(filena, 'w')
h.create_dataset("ccc", data=(rc_voxels))
h.close()

#### Step 3, save CCC as nifti file ############################

mask_array = nb.load(image_mask).get_data()
voxel_x    = np.where(mask_array==1)[0]
voxel_y    = np.where(mask_array==1)[1]
voxel_z    = np.where(mask_array==1)[2]

out_dir = '/nobackup/ilz2/bayrak/subjects_group/'
mni_3mm    = os.path.join(out_dir, 'MNI152_T1_3mm_brain.nii.gz')
mni_affine = nb.load(mni_3mm).get_affine()
data_temp  = np.zeros(nb.load(mni_3mm).get_data().shape)

data_temp[voxel_x, voxel_y, voxel_z] = rc_voxels
img_temp   = nb.Nifti1Image(data_temp, mni_affine)
name_temp  = 'ConCor.nii.gz'
nb.save(img_temp, name_temp)








