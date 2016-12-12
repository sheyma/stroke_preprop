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

#subject_id = 'sd22_d00'
#comp_file = '/nobackup/ilz2/bayrak/subjects_group/mni3_component_1.nii.gz'

subject_id = sys.argv[1]
comp_file  = sys.argv[2]
data_dir   = '/nobackup/ilz2/bayrak/subjects/'
data_out   = '/nobackup/ilz2/bayrak/stroke_intrasubject/'

new_dir = os.path.splitext(os.path.splitext(os.path.basename(comp_file))[0])[0]
work_dir   = os.path.join(data_out, subject_id[0:4], new_dir)
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

les_file = os.path.join(data_dir, subject_id, 'lesion/lesion_mask_mni.nii.gz')

gm_mask  = '/nobackup/ilz2/bayrak/subjects_group/mni3_rest_gm_mask.nii.gz'

ken_file = os.path.join(data_out, subject_id[0:4], 'Kendall_W.nii.gz')

ccc_file = os.path.join(data_out, subject_id[0:4], 'ConCor.nii.gz')

sbj_mask = os.path.join(data_out, subject_id[0:4], 'subject_mask_final.nii.gz')

print les_file
print ken_file
print ccc_file
print sbj_mask

# Step 1, find indexes of voxels, where SD has concordance value

mask_array = nb.load(sbj_mask).get_data()
x    = np.where(mask_array==1)[0]
y    = np.where(mask_array==1)[1]
z    = np.where(mask_array==1)[2]

# get lesion lying on component space (change it with subject_mask_03 !!!)
maths = MultiImageMaths()
maths.inputs.in_file       = les_file
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = gm_mask
maths.inputs.out_file      = 'tmp.nii.gz'
maths.run()

A = masking.apply_mask(comp_file, 'tmp.nii.gz')
A = A.reshape((len(A), 1))


# Step 2, get the component boundaries and its distribution on SD

comp_hc  = masking.apply_mask(comp_file, sbj_mask)
comp_min = comp_hc.min()
comp_max = comp_hc.max() 

COMP        = np.array(nb.load(comp_file).get_data())
KENDAL      = np.array(nb.load(ken_file).get_data())
CCC         = np.array(nb.load(ccc_file).get_data())

for tot_box_num in range(50,1000,50):
    print tot_box_num
    
    # bins always 1 element longer than total box number
    bins = np.linspace(comp_min, comp_max, tot_box_num + 1)

    inds = np.digitize(COMP[x, y, z], bins)

    tmp_x = {}
    tmp_y = {}
    tmp_z = {}

    box_kendal = {}
    box_ccc    = {}

    cnt_comp = np.histogram(COMP[x, y, z], bins)[0]
    cnt_les  = np.histogram(A, bins)[0]

    box_proportion  = {}

    for box_num in range(1, tot_box_num + 1):

        box_inds = np.where(inds == box_num)
        #print box_num, box_inds   

        tmp_x[box_num] = x[box_inds]
        tmp_y[box_num] = y[box_inds]
        tmp_z[box_num] = z[box_inds]
     
        voxel_values   = KENDAL[tmp_x[box_num], tmp_y[box_num], tmp_z[box_num]] 
        voxel_ccc      = CCC[tmp_x[box_num], tmp_y[box_num], tmp_z[box_num]]


        box_kendal[box_num] = np.mean(voxel_values)
        box_ccc[box_num] = np.mean(voxel_ccc)

        prop = cnt_les[box_num -1 ] / float(cnt_comp[box_num - 1]) * 100

        box_proportion[box_num] = prop

    # save dictionaries
    file_prop = "prop_%s.pickle" % (tot_box_num)
    file_kenw = "kenw_%s.pickle" % (tot_box_num)
    file_ccc = "ccc_%s.pickle" % (tot_box_num)


    with open(file_prop, 'wb') as handle:
        pickle.dump(box_proportion, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(file_kenw, 'wb') as handle:
        pickle.dump(box_kendal, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(file_ccc, 'wb') as handle:
        pickle.dump(box_ccc, handle, protocol=pickle.HIGHEST_PROTOCOL)

    
    # plotting
    begin = bins[0] + (bins[1]-bins[0]) / 2.0
    end   = bins[-1] - (bins[1]-bins[0]) / 2.0
    new_bins = np.linspace(begin, end, len(bins)-1 )

    plt.figure(figsize=(25, 15))
    plt.title("bins = %s " % tot_box_num)
    plt.hist(COMP[x, y, z], bins, color='blue', label='comp - HC')
    plt.hist(A, bins, color='red', label='lesion - SD')
    plt.plot(new_bins, box_proportion.values(), 'o', linewidth=5, 
             color='green', label='prop')
    plt.plot(new_bins, box_kendal.values(), 'o', color='black', 
            linewidth = 4, label='KendallsW')
    plt.plot(new_bins, box_ccc.values(), 'o', color='violet', 
            linewidth = 4, label='CCC')
    plt.legend()
    plt.axis([comp_min, comp_max, 0, 1000 ])
    plt.savefig("fig01_%s.png" % tot_box_num)
    plt.close('all')


    plt.figure(figsize=(25, 15))
    plt.title("bins = %s " % tot_box_num)
    plt.hist(A, bins, color='red', label='lesion - SD')
    plt.plot(new_bins, box_proportion.values(), 'o', linewidth=5, 
             color='green', label='prop')
    plt.plot(new_bins, box_kendal.values(), 'o', color='black', 
            linewidth = 4, label='KendallsW')
    plt.plot(new_bins, box_ccc.values(), 'o', color='violet', 
            linewidth = 4, label='CCC')
    plt.legend()
    plt.axis([comp_min, comp_max, 0, 15  ])
    plt.savefig("fig02_%s.png" % tot_box_num)
    plt.close('all')


#with open("ccc_%s.pickle" % tot_box_num, 'rb') as handle:
#    b = pickle.load(handle)




