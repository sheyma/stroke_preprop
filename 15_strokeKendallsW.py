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


def tied_rank(x):
    """
    https://github.com/cmoscardi/ox_ml_practical/blob/master/util.py
    
    Computes the tied rank of elements in x.
    This function computes the tied rank of elements in x.
    Parameters
    ----------
    x : list of numbers, numpy array
    Returns
    -------
    score : list of numbers
            The tied rank f each element in x
    """
    sorted_x = sorted(zip(x,range(len(x))))
    r = [0 for k in x]
    cur_val = sorted_x[0][0]
    last_rank = 0
    for i in range(len(sorted_x)):
        if cur_val != sorted_x[i][0]:
            cur_val = sorted_x[i][0]
            for j in range(last_rank, i): 
                r[sorted_x[j][1]] = float(last_rank+1+i)/2.0
            last_rank = i
        if i==len(sorted_x)-1:
            for j in range(last_rank, i+1): 
                r[sorted_x[j][1]] = float(last_rank+i+2)/2.0
    return r


def IPN_kendallW(X, tied=False):
    """
    Kendall's W
    """
    from scipy.stats import f
    import math

    [n, k] = np.shape(X)
    if tied:

        R_tmp = []
        for i in range(0, np.shape(X)[1]):
            r = tied_rank(X[:,i])
            R_tmp.append(r)
            R = np.array(R_tmp).T
        
        R_new = np.sort(np.round(R), axis=0)
        A = np.matlib.repmat(np.array(range(1,n+1)), k, 1).T
        T = np.sum(np.array((A-R_new), dtype=bool), axis=0) +1
        RS = np.sum(R, axis=1)
        S = np.sum(np.square(RS)) - n * math.pow(np.mean(RS),2)  
        F = k * k* (n * n * n-n)- k*np.sum(np.power(T, 3)-T)
        W = float(12)*S/F
       
    else:

        I = X.argsort(axis=0)
        R = I.argsort(axis=0)
        RS = np.sum(R, axis=1)
        RS = RS + k
        S = np.sum(np.square(RS)) - n*np.square(np.mean(RS))
        F = k*k*(n*n*n-n)
        W = float(12)*S / F  

    Fdist = W*(k-1) / (1-W)
    nu1 = n-1-(2/float(k));
    nu2 = nu1*(k-1);
    p = f.pdf(Fdist, nu1, nu2)

    return W, p, Fdist

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

##### Step 2, calculate Kendall's W for each voxel #######################

W_voxels = []
p_voxels = []
Fdist_voxels = []
tmp = []

for j in range(0, np.shape(corr_All)[1]):
    for i in range(0, np.shape(corr_All)[0]):
        tmp.append(corr_All[i,:,j])
    tmp = np.array(tmp).T
    W, p, Fdist = IPN_kendallW(tmp)    
    W_voxels.append(W)
    p_voxels.append(p)
    Fdist_voxels.append(Fdist)
    tmp = []
 
filena = os.path.join('/nobackup/ilz2/bayrak/stroke_intrasubject',
                      subject_id[0:4], 'KendallW.h5')   

h = h5py.File(filena, 'w')
h.create_dataset("W", data=(W_voxels))
h.create_dataset("p", data=(p_voxels))
h.create_dataset("Fdist", data=(Fdist_voxels))
h.close()


