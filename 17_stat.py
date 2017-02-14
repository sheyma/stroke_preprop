import os, sys
from nilearn import masking
import numpy as np
#import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
import nibabel as nb
from nipype.interfaces.fsl import MultiImageMaths
import h5py
import pickle

subject_id = 'sd27_d00'
comp_file = '/nobackup/ilz2/bayrak/subjects_group/mni3_component_1.nii.gz'

#subject_id = sys.argv[1]
#comp_file  = sys.argv[2]
data_dir   = '/nobackup/ilz2/bayrak/subjects/'
data_out   = '/nobackup/ilz2/bayrak/stroke_intrasubject/'

new_dir = os.path.splitext(os.path.splitext(os.path.basename(comp_file))[0])[0]
work_dir   = os.path.join(data_out, subject_id[0:4], new_dir)
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

#les_file = os.path.join(data_dir, subject_id, 'lesion/lesion_mask_mni.nii.gz')

gm_mask  = '/nobackup/ilz2/bayrak/subjects_group/mni3_rest_gm_mask.nii.gz'

lesOnGMmask = os.path.join(data_out, subject_id[0:4], 'subject_mask_03.nii.gz')

ken_file = os.path.join(data_out, subject_id[0:4], 'Kendall_W.nii.gz')

ccc_file = os.path.join(data_out, subject_id[0:4], 'ConCor.nii.gz')

sbj_mask = os.path.join(data_out, subject_id[0:4], 'subject_mask_final.nii.gz')

print comp_file
print gm_mask
print lesOnGMmask
print ken_file
print ccc_file
print sbj_mask

# Step 1, find indexes of voxels, where SD has concordance value

mask_array = nb.load(sbj_mask).get_data()
x    = np.where(mask_array==1)[0]
y    = np.where(mask_array==1)[1]
z    = np.where(mask_array==1)[2]

print "x-length: ", len(x)

# Step 2, find voxels on comp_file, which correspond to lesion on SD
A = masking.apply_mask(comp_file, lesOnGMmask)
A = A.reshape((len(A), 1))

print "A shape ", A.shape
print A

## Step 3, get the component boundaries and its distribution on SD

comp_hc  = masking.apply_mask(comp_file, sbj_mask)
comp_min = comp_hc.min()
comp_max = comp_hc.max() 

COMP        = np.array(nb.load(comp_file).get_data())
KENDAL      = np.array(nb.load(ken_file).get_data())
CCC         = np.array(nb.load(ccc_file).get_data())

##for tot_box_num in range(50,1000,50):
for tot_box_num in range(100, 101):
    print "total box number: ", tot_box_num
    
    # bins' length should be 1 term longer than total box number
    bins = np.linspace(comp_min, comp_max, tot_box_num + 1)
      
    #print "shape of component: ", COMP[x, y, z].shape

    # component's hist distribution into the bins
    #fig = plt.figure(figsize=(15,7.5))
    fig = plt.figure(figsize=(14,10))

    #plt.title("bins = %s " % tot_box_num)
    
    # without pdf
    #plt.hist(COMP[x, y, z], bins, color='blue', label='comp - HC')    
    # with pdf    
    #plt.hist(COMP[x, y, z], bins, normed=True, color='blue', label='comp - HC')
    #plt.show()

    # for each comp element, find which bin it falls into 
    inds = np.digitize(COMP[x, y, z], bins)

    #print "shape of inds: ", inds.shape

    # how many elements does each bin have
    cnt_comp = np.histogram(COMP[x, y, z], bins)[0]
    
    #print "count comp bins: ", cnt_comp
    
    tmp_x = {}
    tmp_y = {}
    tmp_z = {}

    box_kendal = {}
    box_ccc    = {}
    box_proportion  = {}

    # how many elements in each bin correspond to the lesion
    cnt_les  = np.histogram(A, bins)[0]
   
    #print "lesion counting ", cnt_les

    # go into each bin iteratively and find x,y,z coords of points there
    for box_num in range(inds.min(), inds.max(), 1):
        
        # which elements along component fall into the current box
        box_inds = np.where(inds == box_num)
    
        # reverse-indexing: find x,y,z of elements in current box
        tmp_x[box_num] = x[box_inds]
        tmp_y[box_num] = y[box_inds]
        tmp_z[box_num] = z[box_inds]

        #print COMP[tmp_x[box_num], tmp_y[box_num], tmp_z[box_num]].mean()
     
        voxel_kendal   = KENDAL[tmp_x[box_num], tmp_y[box_num], tmp_z[box_num]] 
        box_kendal[box_num] = voxel_kendal.mean()
        #print box_kendal[box_num]

        voxel_ccc      = CCC[tmp_x[box_num], tmp_y[box_num], tmp_z[box_num]]
        box_ccc[box_num] = voxel_ccc.mean()
        #print box_ccc[box_num]

        prop = cnt_les[box_num -1 ] / float(cnt_comp[box_num - 1]) * 100
        box_proportion[box_num] = prop


    begin = bins[0] + (bins[1]-bins[0]) / 2.0
    end   = bins[-1] - (bins[1]-bins[0]) / 2.0
    new_bins = np.linspace(begin, end, len(bins)-1 )

    ## without pdf
    #plt.hist(COMP[x, y, z], bins, color='blue', label='comp - HC')    
    # with pdf    
    plt.hist(COMP[x, y, z], bins, normed=True, color='orange', label='1st component')
    
    #ccc_all = CCC[x,y,z]
    #print ccc_all
    #ax = fig.add_subplot(111)
    #ax.plot(range(0, len(ccc_all)), ccc_all, 'o', color='green')
    #plt.ylabel('CCC', fontsize=40)
    #plt.xlabel('voxel index', fontsize=40)
    ##plt.axis([0, len(ccc_all), -1, 1  ])
    #plt.tick_params(axis='both', which='major', labelsize=30)
    #from matplotlib.ticker import ScalarFormatter
    #fmt = ScalarFormatter()
    #fmt.set_powerlimits((-3, 3))
    #ax.xaxis.set_major_formatter(fmt)


    #plt.hist(A, bins, normed=True, color='red', label='lesion - SD')
    #plt.plot(new_bins, box_proportion.values(), 'r', linewidth=5, 
    #         color='red', label='lesion %')

    plt.plot(new_bins, box_ccc.values(), 'go', markersize=15,  
             label='CCC')

    plt.legend(frameon=False)
    plt.title('%s' % subject_id[0:4] )
    plt.ylabel('number of voxels', fontsize=40)
    plt.xlabel('component spectrum', fontsize=40)
    plt.axis([comp_min, comp_max, 0, 0.7])
    plt.tick_params(axis='both', which='major', labelsize=30)
    #plt.show()



    ## save dictionaries
    #file_prop = "prop_%s.pickle" % (tot_box_num)
    #file_kenw = "kenw_%s.pickle" % (tot_box_num)
    #file_ccc = "ccc_%s.pickle" % (tot_box_num)


    #with open(file_prop, 'wb') as handle:
    #    pickle.dump(box_proportion, handle, protocol=pickle.HIGHEST_PROTOCOL)

    #with open(file_kenw, 'wb') as handle:
    #    pickle.dump(box_kendal, handle, protocol=pickle.HIGHEST_PROTOCOL)

    #with open(file_ccc, 'wb') as handle:
    #    pickle.dump(box_ccc, handle, protocol=pickle.HIGHEST_PROTOCOL)

    
    # plotting
    #begin = bins[0] + (bins[1]-bins[0]) / 2.0
    #end   = bins[-1] - (bins[1]-bins[0]) / 2.0
    #new_bins = np.linspace(begin, end, len(bins)-1 )

    #plt.figure(figsize=(25, 15))
    #plt.title("bins = %s " % tot_box_num)
    #plt.hist(COMP[x, y, z], bins, color='blue', label='comp - HC')
    #plt.hist(A, bins, color='red', label='lesion - SD')
    #plt.plot(new_bins, box_proportion.values(), 'o', linewidth=5, 
    #         color='green', label='prop')
    #plt.plot(new_bins, box_kendal.values(), 'o', color='red', 
    #        linewidth = 4, label='KendallsW')
    #plt.plot(new_bins, box_ccc.values(), 'o', color='violet', 
    #        linewidth = 4, label='CCC')
    #plt.legend()
    #plt.axis([comp_min, comp_max, 0.2, 0.9])
    #plt.savefig("fig01_%s.png" % tot_box_num)
    #plt.close('all')
    #plt.show()

    #plt.figure(figsize=(25, 15))
    #plt.title("bins = %s " % tot_box_num)
    #plt.hist(A, bins, color='red', label='lesion - SD')
    #plt.plot(new_bins, box_proportion.values(), 'o', linewidth=5, 
    #         color='green', label='prop')
    #plt.plot(new_bins, box_kendal.values(), 'o', color='black', 
    #        linewidth = 4, label='KendallsW')
    #plt.plot(new_bins, box_ccc.values(), 'o', color='violet', 
    #        linewidth = 4, label='CCC')
    #plt.legend()
    #plt.axis([comp_min, comp_max, 0, 15  ])
    #plt.savefig("fig02_%s.png" % tot_box_num)
    #plt.close('all')


#with open("ccc_%s.pickle" % tot_box_num, 'rb') as handle:
#    b = pickle.load(handle)


import numpy as np
import matplotlib.pyplot as plt

#fig = plt.figure(figsize=(14,10))
#fig, ax1 = plt.subplots(figsize=(15, 11))
fig, ax1 = plt.subplots(figsize=(15, 7.5))

ax1.hist(COMP[x, y, z], bins, normed=True, color='orange')
ax1.set_xlabel('time (s)')
# Make the y-axis label and tick labels match the line color.
ax1.set_title('subject 27', fontsize=40)
ax1.set_ylabel('number of voxels', fontsize=40)
ax1.set_xlabel('component spectrum', fontsize=40)
for tl in ax1.get_yticklabels():
    tl.set_color('k')
#plt.plot(new_bins, box_proportion.values(), 'r', linewidth=5, 
#            color='red', label='lesion %')
plt.legend(frameon=False)

ax2 = ax1.twinx()

ax2.plot(new_bins, box_ccc.values(), 'go', markersize=15,  
             label='CCC')
ax2.set_ylabel('CCC', color='g', fontsize=40)
for tl in ax2.get_yticklabels():
    tl.set_color('g')
#plt.legend()
plt.show()


