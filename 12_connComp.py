import os, sys
import numpy as np
import numexpr as ne
import h5py
import nibabel as nb
from sklearn.metrics import pairwise_distances
ne.set_num_threads(ne.ncores) # inclusive HyperThreading cores
sys.path.append(os.path.expanduser('~/devel/mapalign/mapalign'))
import embed

# get averaged correlation (Fisher z2r transformed)
ave_filena = '/data/pt_mar006/newtmp/avecorr.h5'
corr       = np.array(h5py.File(ave_filena, 'r')['data'])

print corr.shape
#corr[np.where(np.isnan(corr)==True)] = 0

####### Step #3: threshold each row of corr matrix at 90th percentile ##
print "thresholding each row at its 90th percentile..."
perc = np.array([np.percentile(x, 90) for x in corr])

for i in range(corr.shape[0]):
	#print "Row %d" % i
	corr[i, corr[i,:] < perc[i]] = 0
#
# Check for minimum & maximum value
print "Minimum value is %f" % corr.min()
print "Maximum value is %f" % corr.max()

## Count negative values per row
#neg_values = np.array([sum(corr[i,:] < 0) for i in range(N_orig)])
#print "Negative values occur in %d rows" % sum(neg_values > 0)

#if sum(neg_values) > 0:
#    corr[corr < 0] = 0


###### Step #4: get affinity matrix via cosine similarity ##############
os.chdir('/data/pt_mar006/newtmp/')

print "calculating affinity matrix..."
aff = 1 - pairwise_distances(corr, metric = 'cosine')

h = h5py.File('avecorr_affinity.h5','w')
h.create_dataset("data", data=aff)
h.close()


###### Step #5: get embedding components on affinity matrix ############
print "calculating connectivity components..."
comp = 9

emb, res = embed.compute_diffusion_map(aff, alpha = 0.5,
                                       n_components = comp)

#np.save('embedding_dense_emb.npy', emb)
#np.save('embedding_dense_res.npy', res)

###### Step #6: projecting components back to MNI space as nifti #######
#print "saving components as nifti..."
#mask_3D_nifti = os.path.join('/data/pt_mar006/subjects_group/',
#                             'gm_prob_mni3_ave_mask.nii.gz')

## get indices of voxels, which are equal to 1 in mask
#mask_array = nb.load(mask_3D_nifti).get_data()
#voxel_x    = np.where(mask_array==1)[0]
#voxel_y    = np.where(mask_array==1)[1]
#voxel_z    = np.where(mask_array==1)[2]

#print "%s voxels are in GM..." % len(voxel_x)

#out_dir = '/data/pt_mar006/newtmp/gradients'
#mni_3mm    = os.path.join(out_dir, 'MNI152_T1_3mm_brain.nii.gz')
#mni_affine = nb.load(mni_3mm).get_affine()
#data_temp  = np.zeros(nb.load(mni_3mm).get_data().shape)

#for j in range(0, comp):
#    print np.shape(emb[:,j])
#    data_temp[voxel_x, voxel_y, voxel_z] = emb[:,j]
#    img_temp  = nb.Nifti1Image(data_temp, mni_affine)
#    name_temp = os.path.join(out_dir, 'mni3_component_%s.nii.gz' % (j+1))
#    nb.save(img_temp, name_temp)

