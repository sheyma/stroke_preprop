"""
	calculate gradients of functional connectivity based on healthy controls
	the average connectivity matrix transformed to Fisher z-to-r
	transformed matrix thresholded at top 10 percent in each row
	an affinity matrix is calculates using cosine similarities
	diffusion embedding method is implemented on the affinity matrix
"""
import os, sys
import numpy as np
import hcp_corr
import numexpr as ne
import h5py
import nibabel as nb
from sklearn.metrics import pairwise_distances
ne.set_num_threads(ne.ncores) # inclusive HyperThreading cores
import argparse
sys.path.append(os.path.expanduser('~/devel/mapalign/mapalign'))
import embed


def fisher_z2r(Z):
    X = ne.evaluate('exp(2*Z)')
    return ne.evaluate('(X - 1) / (X + 1)')

# get averaged (upper triangular) 1D correlation (Fisher r2z transformed)
ave_filena = '/data/pt_mar006/subjects_group/corrFisherR2Z_upper.h5'
ave_array  = np.array(h5py.File(ave_filena, 'r')['data'])

###### Step #5: Fisher's z2r transform ###############################
print "Fisher z2r transform..."
ave_array = fisher_z2r(ave_array)

# get the full matrix
N_orig     = hcp_corr.N_original(ave_array)
ave_array.resize([N_orig, N_orig])
corr       = hcp_corr.upper_to_down(ave_array)

###### Step #6: threshold each row of corr matrix at 90th percentile ##
print "thresholding each row at its 90th percentile..."
perc = np.array([np.percentile(x, 90) for x in corr])

for i in range(corr.shape[0]):
	#print "Row %d" % i
	corr[i, corr[i,:] < perc[i]] = 0  

# Check for minimum & maximum value
print "Minimum value is %f" % corr.min()
print "Maximum value is %f" % corr.max()

## Count negative values per row
#neg_values = np.array([sum(corr[i,:] < 0) for i in range(N_orig)])
#print "Negative values occur in %d rows" % sum(neg_values > 0)

#if sum(neg_values) > 0:
#    corr[corr < 0] = 0

##### Step #7: get affinity matrix via cosine similarity ##############
print "calculating affinity matrix..."
aff = 1 - pairwise_distances(corr, metric = 'cosine')

os.chdir('/data/pt_mar006/subjects_group/')
h = h5py.File('affinity_matrix.h5','w')
h.create_dataset("data", data=aff)
h.close()

##### Step #8: get embedding components on affinity matrix ############
print "calculating connectivity components..."
comp = 9

emb, res = embed.compute_diffusion_map(aff, alpha = 0.5,
                                       n_components = comp)

np.save('embedding_dense_emb.npy', emb)
np.save('embedding_dense_res.npy', res)

