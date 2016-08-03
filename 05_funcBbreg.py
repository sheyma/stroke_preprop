import os, sys
from nipype.interfaces.fsl.maths import MeanImage
from nipype.interfaces.freesurfer import BBRegister
from subprocess import call
from nipype.interfaces.c3 import C3dAffineTool

data_in = '/scr/ilz2/bayrak/stroke_func/'
data_out = '/scr/ilz2/bayrak/stroke_bbreg'
free_dir = '/scr/ilz2/bayrak/stroke_reconall'

subject_id = sys.argv[1]
scan = sys.argv[2]
	
if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)
if not os.path.exists(os.path.join(work_dir, scan)):
	os.makedirs(os.path.join(work_dir, scan))
work_dir = os.path.join(work_dir, scan)

# go into working directory
os.chdir(work_dir)

# get motion corrected and skull stripped rs image
data_in_absol = os.path.join(data_in, subject_id, scan)
img_nifti = os.path.join(data_in_absol, 'rest_ss.nii.gz')
os.system("cp %s %s" % (img_nifti, work_dir))

print img_nifti

# CHECK ORIENTATION PRIOR TO CO-REGISTRATION!!!

# get T-mean of rs image
fslmaths = MeanImage()
fslmaths.inputs.in_file = 'rest_ss.nii.gz'
fslmaths.inputs.out_file = 'rest_mean.nii.gz'
fslmaths.inputs.dimension = 'T'
fslmaths.run()

# get freesurfer directory for recon_all outputs
freesurfer_dir = os.path.join(free_dir, subject_id)
T_scan = 'T1d' + scan[3:5] 
freesurfer_dir = os.path.join(freesurfer_dir, T_scan)	

if not os.path.exists(freesurfer_dir):
	error_message = scan + " doesn't have " + T_scan + '!!!'''
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
	bbreg.inputs.registered_file = 'rest_mean2anat_highres.nii.gz'
	bbreg.inputs.epi_mask = True
	bbreg.run()
	
#cd3_affine_tool
c3 = C3dAffineTool()
c3.inputs.transform_file = work_dir + '/rest2anat.mat'
c3.inputs.itk_transform = work_dir + '/bla.mat'
c3.inputs.fsl2ras = True
c3.run()
