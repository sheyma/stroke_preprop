import os, sys
from nilearn import masking
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import nibabel as nb
from nipype.interfaces.fsl import MultiImageMaths
import h5py
import pickle

#comp_file  = '/data/pt_mar006/subjects_group/mni3_component_1.nii.gz'
#subject_id = 'sd27'

comp_file  = sys.argv[1]
subject_id = sys.argv[2]

data_dir   = '/data/pt_mar006/stroke_intrasubject/'

new_name = os.path.splitext(os.path.splitext(os.path.basename(comp_file))[0])[0]
os.chdir(os.path.join(data_dir, subject_id))

les_file = os.path.join(data_dir, subject_id, 'lesion/lesion_mask_mni.nii.gz')

lesOnGMmask = os.path.join(data_dir, subject_id, 'subject_mask_03.nii.gz')

concordance = os.path.join(data_dir, subject_id, 'conc_ccc.nii.gz')

sbj_mask = os.path.join(data_dir, subject_id, 'subject_mask_final.nii.gz')

gm_mask  = '/data/pt_mar006/subjects_group/mni3_rest_gm_mask.nii.gz'

# Step 1, find indexes of voxels, where SD has concordance value
mask_array = nb.load(sbj_mask).get_data()
x    = np.where(mask_array==1)[0]
y    = np.where(mask_array==1)[1]
z    = np.where(mask_array==1)[2]

# Step 2, find voxels on comp_file, which correspond to lesion on SD
A = masking.apply_mask(comp_file, lesOnGMmask)
A = A.reshape((len(A), 1))

print "number of lesioned voxels ", A.shape

## Step 3, get the component boundaries and its distribution on SD
comp_hc  = masking.apply_mask(comp_file, sbj_mask)
comp_min = comp_hc.min()
comp_max = comp_hc.max() 

COMP          = np.array(nb.load(comp_file).get_data())
CONCORDANCE   = np.array(nb.load(concordance).get_data())

##for tot_box_num in range(50,1000,50):
for tot_box_num in range(20, 21):
    print "total box number: ", tot_box_num
    
    # bins' length should be 1 term longer than total box number
    bins = np.linspace(comp_min, comp_max, tot_box_num + 1)
      
    # for each comp element, find which bin it falls into 
    inds = np.digitize(COMP[x, y, z], bins)

    # how many elements does each bin have
    cnt_comp = np.histogram(COMP[x, y, z], bins)[0]
    
    tmp_x = {}
    tmp_y = {}
    tmp_z = {}

    box_concordance = {}
    box_proportion  = {}

    # how many elements in each bin correspond to the lesion
    cnt_les  = np.histogram(A, bins)[0]
   
    # go into each bin iteratively and find x,y,z coords of points there
    for box_num in range(inds.min(), inds.max(), 1):
        
        # which elements along component fall into the current box
        box_inds = np.where(inds == box_num)
    
        # reverse-indexing: find x,y,z of elements in current box
        tmp_x[box_num] = x[box_inds]
        tmp_y[box_num] = y[box_inds]
        tmp_z[box_num] = z[box_inds]

        #print COMP[tmp_x[box_num], tmp_y[box_num], tmp_z[box_num]].mean()
     
        voxel_values      = CONCORDANCE[tmp_x[box_num], tmp_y[box_num], tmp_z[box_num]]
        box_concordance[box_num] = voxel_values.mean()

        prop = cnt_les[box_num -1 ] / float(cnt_comp[box_num - 1]) * 100
        box_proportion[box_num] = prop

    begin = bins[0] + (bins[1]-bins[0]) / 2.0
    end   = bins[-1] - (bins[1]-bins[0]) / 2.0
    new_bins = np.linspace(begin, end, len(bins)-1 )


##### plotting

fig, ax1 = plt.subplots(figsize=(17, 11))

ax1.hist(COMP[x, y, z], bins, normed=True, color='orange')

ax1.plot(new_bins, box_proportion.values(), 'r', linewidth=5, 
             color='red', label='lesion %')

# make the y-axis label and tick labels match the line color
concordance_type = 'CCC'


ax2 = ax1.twinx()
ax2.plot(new_bins, box_concordance.values(), 'go', markersize=15, 
         label=concordance_type)
ax2.set_ylabel(concordance_type, color='g', fontsize=40)

for tl in ax2.get_yticklabels():
    tl.set_color('g')

ax1.set_title(subject_id, fontsize=40)
ax1.set_ylabel('number of voxels', fontsize=40)
ax1.set_xlabel('component spectrum', fontsize=40)
for tl in ax1.get_yticklabels():
    tl.set_color('k')

plt.legend(frameon=False)
#plt.savefig("/data/pt_mar006/figures/fig_%s_%s.png" % 
#            (new_name, subject_id))

plt.savefig("/data/pt_mar006/tmp/simdi.png")
#plt.show()

#plt.scatter(c2, c1, c=A, cmap='jet')
#plt.colorbar()
#plt.savefig('/data/pt_mar006/mmm.eps')

print "yess"

