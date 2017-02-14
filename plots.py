

from nilearn import datasets, plotting, image

data = datasets.fetch_adhd(n_subjects=1)

# Print basic information on the dataset
print('First subject functional nifti image (4D) are located at: %s' %
      data.func[0])

first_epi_file = data.func[0]

# First the compute the mean image, from the 4D series of image
mean_func = image.mean_img(first_epi_file)

# Then we smooth, with a varying amount of smoothing, from none to 20mm
# by increments of 5mm
smoothing = 0

mean_func = '/nobackup/ilz2/bayrak/subjects_group/mni3_component_1.nii.gz'

#print mean_func

import matplotlib.pyplot as plt
#fig     = plt.figure(figsize=(15,7.5))
#display = plotting.plot_stat_map(mean_func, colorbar=True, cmap='gnuplot',                     #figure=fig, annotate=True, black_bg=True, cut_coords=[-10, 0, 22])
  
#display.annotate(size=35)
#display.title('1st component', size=35)
#plotting.show()


#K = '/nobackup/ilz2/bayrak/stroke_intrasubject/sd27/ConCor.nii.gz'
K = '/nobackup/ilz2/bayrak/stroke_intrasubject/sd27/Kendall_W.nii.gz'
#print K

import matplotlib.pyplot as plt
fig     = plt.figure(figsize=(15,7.5))
display = plotting.plot_stat_map(K, colorbar=True, cmap='jet', figure=fig, annotate=True, black_bg=True, cut_coords=[-10, 0, 22])
  
display.annotate(size=35)
display.title('Kendall\'s W (subject 27)', size=35)
#display.title('Concordance Correlation Coefficient (subject 27)', size=35)
plotting.show()

dwi_image = '/nobackup/ilz2/bayrak/subjects/sd02_d00/lesion/transforms2anat/dwi_brain.nii.gz'
lesion    = '/nobackup/ilz2/bayrak/subjects/sd02_d00/lesion/lesion_mask_mni.nii.gz'

#fig     = plt.figure(figsize=(15,7.5))
#display = plotting.plot_anat(anat_img=dwi_image, cut_coords=[-25, 1, 10], 
#dim=-1)

#plotting.plot_anat(lesion, cut_coords=[-25, 1, 10])

#plotting.plot_stat_map(lesion, bg_img=dwi_image,
                       
#                       cut_coords=[-25, 1, 10], dim=-1)


#plotting.show()

