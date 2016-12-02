"""
generates anatomical anatomical masks &
non-linear registration from T1 to MNI
How to run:
$ python 04_structAnts.py hc01_d00
"""
import os, sys
import nipype.interfaces.ants as ants
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl
from subprocess import call
from nipype.interfaces.c3 import C3dAffineTool

# data dir's 
data_dir   = '/nobackup/ilz2/bayrak/subjects'

# user given subject_id 
subject_id = sys.argv[1]

# MNI template (no skull)
mni_temp = os.path.join('/usr/share/fsl/5.0/data/standard', 
			'MNI152_T1_1mm_brain.nii.gz')

# define working dir
work_dir = os.path.join(data_dir, subject_id,  
			'preprocessed/anat')
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
	
# go into work dir
os.chdir(work_dir)
print "YESSSS"
#### Step1 # get the freesurfer output and convert it

# get skull stripped (recon_all) structural image
img_struc = os.path.join(data_dir, subject_id,  
			 'freesurfer/mri', 'brain.mgz') 

# convert *mgz into *nii.gz
mricon = fs.MRIConvert(in_file = img_struc,
		       out_file = 'brain.nii.gz',
		       out_type = 'niigz').run()

brain_nifti = os.path.abspath('brain.nii.gz')

#### Step2 # generate masks...##################

# create  brain mask 
get_mask = fs.Binarize()
get_mask.inputs.in_file     = 'brain.nii.gz'
get_mask.inputs.min         = 0.5
get_mask.inputs.dilate      = 1
get_mask.inputs.out_type    = 'nii.gz'
get_mask.inputs.binary_file = 'brain_mask.nii.gz'
get_mask.run()

# get the wm segmentation from aparc+aseg
aparc_aseg = os.path.join(data_dir, subject_id,
	                  'freesurfer/mri', 
			  'aparc+aseg.mgz')

mricon = fs.MRIConvert(in_file = aparc_aseg,
		       out_file = 'aparc+aseg.nii.gz',	
		       out_type = 'niigz').run()

coolBinarize = fs.Binarize()
coolBinarize.inputs.in_file     = 'aparc+aseg.nii.gz'
coolBinarize.inputs.match       = [2, 7, 41, 46, 16]
coolBinarize.out_type           = 'nii.gz'
coolBinarize.inputs.binary_file = 'brain_wmseg.nii.gz'
coolBinarize.run()

# make edge from wm seg. to use for quality control
edge = fsl.ApplyMask()
edge.inputs.in_file   = 'brain_wmseg.nii.gz'
edge.inputs.mask_file = 'brain_wmseg.nii.gz'
edge.inputs.args      = '-edge -bin'
edge.inputs.out_file  = 'brain_wmedge.nii.gz'
edge.run()

#### Step3 ##################################################################### 

if subject_id[5:8] == 'd01':
	####### run ants ################################
	# define ants output 
	img_ants = os.path.abspath('brain_mni.nii.gz')

	# define working dir for transform matrices
	work_dir_trf = os.path.join(data_dir, subject_id,  
				    'preprocessed/anat/transforms2mni')
	if not os.path.exists(work_dir_trf):
		os.makedirs(work_dir_trf)

	ants_anat2mni = ants.Registration(dimension=3,
			    transforms=['Rigid','Affine','SyN'],
			    metric=['MI','MI','CC'],
			    metric_weight=[1,1,1],
			    number_of_iterations=[[1000,500,250,100],[1000,500,250,100],
						  [100,70,50,20]],
			    convergence_threshold=[1e-6,1e-6,1e-6],
			    convergence_window_size=[10,10,10],
			    shrink_factors=[[8,4,2,1],[8,4,2,1],[8,4,2,1]],
			    smoothing_sigmas=[[3,2,1,0],[3,2,1,0],[3,2,1,0]],
			    sigma_units=['vox','vox','vox'],
			    initial_moving_transform_com=1,
			    transform_parameters=[(0.1,),(0.1,),(0.1,3.0,0.0)],
			    sampling_strategy=['Regular', 'Regular', 'None'],
			    sampling_percentage=[0.25,0.25,1],
			    radius_or_number_of_bins=[32,32,4],
			    num_threads=1,
			    interpolation='Linear',
			    winsorize_lower_quantile=0.005,
			    winsorize_upper_quantile=0.995,
			    collapse_output_transforms=True,
			    output_inverse_warped_image=True,
			    output_warped_image=True,
			    use_histogram_matching=True)
	ants_anat2mni.inputs.fixed_image 	 = mni_temp
	ants_anat2mni.inputs.moving_image 	 = brain_nifti
	ants_anat2mni.inputs.output_warped_image = img_ants
	ants_anat2mni.run()



