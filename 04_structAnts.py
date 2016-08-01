"""
non-linear registration from T1 to MNI
"""
import os, sys
import nipype.interfaces.ants as ants
from subprocess import call

# data dir's 
data_in = '/scr/ilz2/bayrak/stroke_reconall/'
data_out = '/scr/ilz2/bayrak/stroke_ants/'
recon_path = 'recon_all/mri'

# user given subject_id and structural scan
subject_id = sys.argv[1]
scan = sys.argv[2]

# MNI template (no skull)
mni_temp = os.path.join('/usr/share/fsl/5.0/data/standard', 
			'MNI152_T1_1mm_brain.nii.gz')
	
# create a work dir
if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)
if not os.path.exists(os.path.join(work_dir, scan)):
	os.makedirs(os.path.join(work_dir, scan))
work_dir = os.path.join(work_dir, scan)

# go into working directory
os.chdir(work_dir)

# pull *mgz data from recon_all path and push into work_dir
data_dir = os.path.join(data_in, subject_id, scan, recon_path)
img_mgz = os.path.join(data_dir, 'brain.mgz')
os.system("cp %s %s" % (img_mgz, work_dir))

# convert .mgz to nifti-1 format
img_nifti = work_dir + '/brain.nii.gz'
os.system("mri_convert %s %s" % (img_mgz, img_nifti))

# change the orientation of nifti-1 file
img_RPI = work_dir + '/brain_RPI.nii.gz'
os.system("fslswapdim %s RL PA IS %s" % (img_nifti, img_RPI))

# ants registration on RPI oriented nifti-1 file
img_ants = work_dir + '/brain_RPI_mni.nii.gz'

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

ants_anat2mni.inputs.fixed_image = mni_temp
ants_anat2mni.inputs.moving_image = img_RPI
ants_anat2mni.inputs.output_warped_image = img_ants
ants_anat2mni.run()
#print ants_anat2mni.cmdline


