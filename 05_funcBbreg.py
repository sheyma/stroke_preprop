import os, sys
from nipype.interfaces.fsl.maths import MeanImage
from nipype.interfaces.freesurfer import BBRegister
from subprocess import call
from nipype.interfaces.c3 import C3dAffineTool

## data dir's for stroke data
#data_in = '/scr/ilz2/bayrak/stroke_func/'
#data_out = '/scr/ilz2/bayrak/stroke_bbreg'

# data dir's for healthy group
data_in = '/scr/ilz2/bayrak/healthy_func/'
data_out = '/scr/ilz2/bayrak/healthy_bbreg/'

subject_id = sys.argv[1]
scan = sys.argv[2]
Tscan = sys.argv[3]

## freesurfer dir for recon_all outputs -> stroke
#free_dir = '/scr/ilz2/bayrak/stroke_reconall'

# freesurfer dir for recon_all outputs -> healthy
free_dir = '/scr/ilz2/bayrak/healthy_reconall'

freesurfer_dir = os.path.join(free_dir, subject_id)
freesurfer_dir = os.path.join(freesurfer_dir, Tscan)	

# create a working directory	
if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)
if not os.path.exists(os.path.join(work_dir, scan+'_'+Tscan)):
	os.makedirs(os.path.join(work_dir, scan+'_'+Tscan))
work_dir = os.path.join(work_dir, scan+'_'+Tscan)

# go into working directory
os.chdir(work_dir)

# get motion corrected and skull stripped rs image
data_in_absol = os.path.join(data_in, subject_id, scan)
img_nifti = os.path.join(data_in_absol, 'rest_ss.nii.gz')
os.system("cp %s %s" % (img_nifti, work_dir))

# CHECK ORIENTATION PRIOR TO CO-REGISTRATION!!!

# get T-mean of rs image
fslmaths = MeanImage()
fslmaths.inputs.in_file = 'rest_ss.nii.gz'
fslmaths.inputs.out_file = 'rest_mean.nii.gz'
fslmaths.inputs.dimension = 'T'
fslmaths.run()

if not os.path.exists(freesurfer_dir):
	error_message = scan + " doesn't have " + Tscan + '!!!'''
	sys.exit(error_message)
else:
	# do bbregister
	bbreg = BBRegister()
	bbreg.inputs.contrast_type = 't2'
	bbreg.inputs.source_file = 'rest_mean.nii.gz'
	bbreg.inputs.init = 'fsl'
	bbreg.inputs.subjects_dir = freesurfer_dir
	bbreg.inputs.subject_id = 'recon_all'
	bbreg.inputs.out_reg_file = 'rest2anat.dat'
	bbreg.inputs.out_fsl_file = 'rest2anat.mat'
	bbreg.inputs.registered_file = 'rest2anat_highRes.nii.gz'
	bbreg.inputs.epi_mask = True
	bbreg.run()

	# get structural image
	img_struc = os.path.join(free_dir, subject_id, Tscan, 
				 'recon_all/mri/brain.mgz') 
	os.system("cp %s %s" % (img_struc, work_dir))

	# convert structural image into nifti 
	os.system("mri_convert %s %s" % (img_struc, 'brain.nii.gz'))
		
# convert bbregister out into itk format for ants later...
c3 = C3dAffineTool()
c3.inputs.transform_file = 'rest2anat.mat'
c3.inputs.itk_transform = 'rest2anat_itk.mat'
c3.inputs.reference_file = 'brain.nii.gz'
c3.inputs.source_file = 'rest_mean.nii.gz'
c3.inputs.fsl2ras = True
c3.run()
