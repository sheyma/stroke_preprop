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


def IPN_kendallW(X):
    """
    Kendall's W
    """
    from scipy.stats import f
    [n, k] = np.shape(X)
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

#A = np.random.randn(3, 100)
#np.savetxt('tmp.txt', A)

#A = np.loadtxt('tmp.txt')
#bla  = IPN_kendallW(A)
#print bla





#data_dir   = '/nobackup/ilz2/bayrak/subjects/'
#suffix     = 'preprocessed/func/connectivity/corrUpper.h5'

#Ma_name = os.path.join(data_dir, 'sd02_d00', suffix)
#Kb_name = os.path.join(data_dir, 'sd02_d01', suffix)
#Gh_name = os.path.join(data_dir, 'sd02_d05', suffix)

##print Ma_name
#Ma = h5py.File(Ma_name, 'r').get('data')
#Ma = np.array(Ma)
#N_orig     = N_original(Ma)
#Ma.resize([N_orig, N_orig])
#Ma_corr       = upper_to_down(Ma)
#print np.shape(Ma_corr)


#Kb = h5py.File(Kb_name, 'r').get('data')
#Kb = np.array(Kb)
#Kb.resize([N_orig, N_orig])
#Kb_corr       = upper_to_down(Kb)
#print np.shape(Kb_corr)



#Gh = h5py.File(Gh_name, 'r').get('data')
#Gh = np.array(Gh)
#Gh.resize([N_orig, N_orig])
#Kb_corr       = upper_to_down(Kb)
#print np.shape(Kb_corr)




def tied_rank(x):
    """
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

C = np.array([[ 0.34451582,  0.82713242],
       [ 0.42677927, -0.21582965],
       [ 0.27928397,  0.67561533],
       [-0.22274886, -0.07290921],
       [-0.09819769, -1.35265992]])

tied_rank(C)

#N_orig     = N_original(corr_upper)
#print np.shape(t_series)
#print N_orig
#corr_upper.resize([N_orig, N_orig])
#corr       = upper_to_down(corr_upper)
#print np.shape(corr_upper)

#h = h5py.File("corrMatrix.h5", 'w')
#h.create_dataset("data", data=corr)
#h.close()



