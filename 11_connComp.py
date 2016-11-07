import os, sys
sys.path.append(os.path.expanduser('~/devel/mapalign/mapalign'))
import nibabel as nb
from nilearn import masking
import numpy as np
import hcp_corr
import numexpr as ne
from sklearn.metrics.pairwise import cosine_similarity
import embed
#import h5py

def fisher_r2z(R):
    return ne.evaluate('arctanh(R)')

def fisher_z2r(Z):
    X = ne.evaluate('exp(2*Z)')
    return ne.evaluate('(X - 1) / (X + 1)')

# get subject-id's as a list
fname = '/nobackup/ilz2/bayrak/documents/cool_hc.txt'
with open(fname) as f:
    content = f.readlines()
sbj_list = [x.strip('\n') for x in content]

# data dir's 
data_dir  = '/nobackup/ilz2/bayrak/subjects'

###### Step #1: get group level GM mask in MNI3mm ################
image_mask3D = os.path.join('/nobackup/ilz2/bayrak/subjects_group',
 			    'gm_mni3_ave_mask.nii.gz')

# get indices of voxels, which are equal to 1 in mask
mask_array = nb.load(image_mask3D).get_data()
voxel_x    = np.where(mask_array==1)[0]
voxel_y    = np.where(mask_array==1)[1]
voxel_z    = np.where(mask_array==1)[2]

print "%s voxels are in GM..." % len(voxel_x)

###### Step #2: get correlation matrix for subjects based on GM ###
## quick run
#sbj_list = ['hc01_d00', 'hc02_d00']

for i in range(0, len(sbj_list)):
	
        subject_id = sbj_list[i]
        print "do loop %d/%d, %s" % (i+1, len(sbj_list), subject_id)

	image_rest4D = os.path.join(data_dir, subject_id, 
	         	            'preprocessed/func', 
			            'rest_preprocessed2mni_sm.nii.gz') 
	
	t_series = masking.apply_mask(image_rest4D, image_mask3D)
	t_series = np.array(t_series).T

	corr_upper = hcp_corr.corrcoef_upper(t_series)

	###### Step #3: Fisher's r2z transform ######################	
	corr_upper = fisher_r2z(corr_upper)

	if i==0:
		SUM = corr_upper
	else:
		SUM += SUM

# TEMPORARY WAY TO GET RID OF NAN
SUM[np.where(np.isnan(SUM)==True)] = 0

###### Step #4: get average correlation matrix #######################
N   = len(sbj_list) 
SUM = ne.evaluate('SUM / N')

###### Step #5: Fisher's z2r transform ###############################
SUM = fisher_z2r(SUM)

###### Step #6: threshold each row at 10% of correlation values #####
thr_percent = 10
thr         = np.percentile(SUM, (100 - thr_percent))

print "1D upper-triang THR: ", thr         

SUM[np.where( SUM < thr) ] = 0
SUM=SUM.copy()

N_orig     = hcp_corr.N_original(SUM)
SUM.resize([N_orig, N_orig])
corr       = hcp_corr.upper_to_down(SUM)

##### Step #7: compute (1 - cosine distance) for each pair of rows ###

# ref: https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/
#scipy.spatial.distance.cosine.html
# ref: http://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html

K = cosine_similarity(corr)

##### Step #8:  compute diffusion embedding on affinity matrix ########

K +=1.0
K /=2.0 
print "do embedding..."
comp = 10
embedding, result = embed.compute_diffusion_map(K,
                                                n_components=comp)
print result['lambdas']
print "embedding done!"

##### Step #9: projecting 10 components back to MNI space as nifti ######

out_dir = '/nobackup/ilz2/bayrak/subjects_group/'
mni_3mm    = os.path.join(out_dir, 'MNI152_T1_3mm_brain.nii.gz')
mni_affine = nb.load(mni_3mm).get_affine()
data_temp  = np.zeros(nb.load(mni_3mm).get_data().shape)

for j in range(0, comp):
	data_temp[voxel_x, voxel_y, voxel_z] = embedding[:,j]
	img_temp  = nb.Nifti1Image(data_temp, mni_affine)
	name_temp = os.path.join(out_dir, 'component_%s.nii.gz' % (j+1))
	nb.save(img_temp, name_temp)

