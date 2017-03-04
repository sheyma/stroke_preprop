import os, sys
import nibabel as nb 
from nilearn import masking, plotting
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

subject_id = 'sd27'

component = '/data/pt_mar006/subjects_group/mni3_component_1.nii.gz'

data_dir   = '/data/pt_mar006/stroke_intrasubject/'

gm_mask  = '/data/pt_mar006/subjects_group/mni3_rest_gm_mask.nii.gz'

sbj_mask = os.path.join(data_dir, subject_id, 'subject_mask_final.nii.gz')

lesOnGMmask = os.path.join(data_dir, subject_id, 'subject_mask_03.nii.gz')

concordance = os.path.join(data_dir, subject_id, 'conc_ccc.nii.gz')

# Step 1, find indexes of voxels, where SD has concordance value
mask_array = nb.load(sbj_mask).get_data()
x    = np.where(mask_array==1)[0]
y    = np.where(mask_array==1)[1]
z    = np.where(mask_array==1)[2]

COMP = np.array(nb.load(component).get_data())
comp_min  = COMP[x,y,z].min()
comp_max  = COMP[x,y,z].max()

CONCORDANCE   = np.array(nb.load(concordance).get_data())

#find voxels on comp_file, which correspond to lesion on SD
lesion = masking.apply_mask(component, lesOnGMmask)
lesion = lesion.reshape((len(lesion), 1))

# Step 2, binning...
tot_box_num = 100
bins = np.linspace(comp_min, comp_max, tot_box_num+1)

# for each comp element, find which bin it falls into 
inds = np.digitize(COMP[x, y, z], bins)

# how many elements does each bin have
cnt_comp = np.histogram(COMP[x, y, z], bins)[0]
cnt_les  = np.histogram(lesion, bins)[0]

tmp_x = {}
tmp_y = {}
tmp_z = {}

box_concordance = {}

box_proportion  = {}

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

# plotting...
fig  = plt.figure(figsize=(17,15))

bins = np.linspace(comp_min, comp_max, tot_box_num)

# MANUAL COLORBAR
#cmap = cmocean.cm.ice
#cmap = plt.cm.get_cmap('gnuplot')
#norm = mpl.colors.Normalize(vmin=comp_min, vmax=comp_max)
#ax1 = fig.add_axes([1.2, 0.05, 0.05, 0.5])
#mycb = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,norm=norm,
#                                 orientation='vertical', 
#                                 ticks=list(np.linspace(a,b,5)),
#                                 format='%1.2f')

# plot connectivity component along the brain
ax1 = fig.add_subplot(2,1,1,)

display = plotting.plot_stat_map(component, colorbar=True, cmap='gnuplot',                    
                                 figure=fig, annotate=True, black_bg=True, 
                                 cut_coords=[-10, 0, 22], axes=ax1,
                                 symmetric_cbar=False)

display.annotate(size=30)

cm = display._cbar.get_cmap()
cbar_ticks = display._cbar._ticker()[1]

import matplotlib
matplotlib.rcParams.update({'font.size': 25})

# plot histogram of the component
ax = fig.add_subplot(2,1,2,)

n, bins, patches = ax.hist(COMP[x, y, z], bins=bins, normed=1)
ax.xaxis.set_ticks(np.array(cbar_ticks, dtype='float64'))

ax.plot(0.5* (bins[1] - bins[0]) + bins, box_proportion.values(), 'r',
         linewidth=5, label='lesion %')
ax.legend(frameon=False)

bin_centers = 0.5 * (bins[:-1] + bins[1:])
col = bin_centers - min(bin_centers)
col /= max(col)
for c, p in zip(col, patches):
    plt.setp(p, 'facecolor', cm(c))

#ax.set_title(subject_id)
#ax.set_ylabel('number of voxels')
#ax.set_xlabel('component spectrum')

ax3 = ax.twinx()

ax3.plot(0.5* (bins[1] - bins[0]) + bins, box_concordance.values(), 'go', 
         markersize=7)
#       label=concordance_type)
#ax3.set_ylabel(concordance_type, color='g')

for tl in ax3.get_yticklabels():
    tl.set_color('g')
 
#plt.show()
#fig.savefig('/data/pt_mar006/figures_march/tmp_histo.png')