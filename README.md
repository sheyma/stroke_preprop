# neuroimaging software

fsl 5.0  
freesurfer 6.0.0  
afni 17.2.17  
dcmstack 0.7.dev  
ants 2.2.0  

# python (2.7.15) packages

numpy 1.15.4  
nibabel 2.3.1  
nilearn 0.4.2  
nipype 1.1.6  
matplotlib 2.2.3  
seaborn 0.7.1  
numexpr 2.6.4  
pandas 0.23.4  
scikit-learn 0.20.1  
scipy 1.1.0  

# preprop

- preprocessing resting state fmri data for healthy controls (HC) and stroke patients (SP)

- snippets from 01_... to 08_...: standard preprocessing pipelines 

- 09_greyMatter.py --> A group-level gray matter (GM) template was obtained across healthy controls. Using freesurfer T1 tissue segmentations, a GM probabilistic map was obtained from each healthy control. All GM probabilistic maps were averaged across 28 healthy controls.

- 10_greyMatterGroup.py --> The averaged GM map was binarized to obtain a GM mask (2). The binarization was implemented using fslmaths at the threshold value of 0.30. This means, all the probabilistic GM values below 0.30 were set to zeros, whereas values above to ones. Additionally, a group-level epi brain mask across healthy controls was obtained. To ensure not to include any GM voxels outside of the epi mask, the GM mask was multiplied with the epi mask. 

- 11_corrUpper.py --> A functional connectivity matrix was calculated using GM voxel time-series for each healthy control. Then, the connectivity matrices were averaged across all healthy participants.

- dense correlation matrices obtaibed with hcp_corr:

https://github.com/NeuroanatomyAndConnectivity/hcp_corr

(Note: no need to use hcp_corr anymore, since higher numpy versions does this job)

- 12_connComp.py --> Implementing the diffusion embedding algorithm on the average functional connectivity matrix, gradients of connectivity were obtained. 

- gradients obtained with mapalign package:
 
https://github.com/satra/mapalign/tree/master/mapalign

- 13_dwiToMNI.py --> lesions identified on dwi images were registered to the mni template. 

- 14_strokeMask.py --> For each of the stroke patient, we obtained an epi brain mask across fMRI scan sessions (across three consequtive days). The overlap between intra-subject epi-mask and the GM mask (that was derived from healthy controls) was calculated. This way, it was ensured with each subject mask that i) voxels are identical to those in the gradient space, and ii) voxels are placed insinde the functional brain mask. Note: dilated lesion masks were excluded from the final mask for each patient. This was done to exclude any direct effect of lesion on the main analysis.

- 15_strokeConcordance.py --> for each stroke patient, a concordance map was obtained across three functional connectivity matrices, which correspond to the fMRI scan days. 



