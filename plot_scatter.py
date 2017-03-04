import os, sys
import numpy as np
import nibabel as nb
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

comp_file    = '/data/pt_mar006/subjects_group/mni3_component_1.nii.gz'

comp_file_02 = '/data/pt_mar006/subjects_group/mni3_component_2.nii.gz'

gm_file = '/data/pt_mar006/stroke_intrasubject/sd27/subject_mask_final.nii.gz'

lesOnGMmask = '/data/pt_mar006/stroke_intrasubject/sd27/subject_mask_03.nii.gz'

concor = '/data/pt_mar006/stroke_intrasubject/sd27/conc_ccc.nii.gz'

# here we go 
COMP     = np.array(nb.load(comp_file).get_data())
COMP_02  = np.array(nb.load(comp_file_02).get_data())
CONCOR   = np.array(nb.load(concor).get_data())

gm_mask = nb.load(gm_file).get_data()
x    = np.where(gm_mask==1)[0]
y    = np.where(gm_mask==1)[1]
z    = np.where(gm_mask==1)[2]

c1 = COMP[x,y,z]
c2 = COMP_02[x,y,z]
K  = CONCOR[x,y,z]

fig  = plt.figure(1, figsize=(17,12))

# make colors on dots visible by making its linewidth smaller
mpl.rcParams['patch.linewidth'] = 0.3
mpl.rcParams.update({'font.size': 20})

plt.title('concordance along components')
plt.scatter(c2, c1, c=K, cmap='jet_r', s=2)
plt.colorbar()

#fig.savefig('/data/pt_mar006/figures_march/tmp_scatter.png')