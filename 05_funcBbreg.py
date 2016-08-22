import os, sys
from nipype.interfaces.fsl.maths import MeanImage
from nipype.interfaces.freesurfer import BBRegister
from subprocess import call
from nipype.interfaces.c3 import C3dAffineTool

# data dir's 
data_in  = '/scr/ilz2/bayrak/new_func/'
data_out = '/scr/ilz2/bayrak/new_bbreg/'

# subject id, resting scan, T1 scan
subject_id = sys.argv[1]
scan 	   = sys.argv[2]
Tscan 	   = sys.argv[3]

# freesurfer dir for recon_all outputs 
free_dir = '/scr/ilz2/bayrak/new_struc'

freesurfer_dir = os.path.join(free_dir, subject_id)
freesurfer_dir = os.path.join(freesurfer_dir, Tscan)	

# create a working directory	
if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)
# dir for 'resting scan registered to T1 scan'
rs_T1 = scan+'_'+Tscan
if not os.path.exists(os.path.join(work_dir, rs_T1)):
	os.makedirs(os.path.join(work_dir, rs_T1))
work_dir = os.path.join(work_dir, rs_T1)

# go into working directory
os.chdir(work_dir)

# get motion and slice-time corrected rs image
data_in_absol = os.path.join(data_in, subject_id, scan)
img_rest = os.path.join(data_in_absol, 'corr_rest_roi.nii.gz')
print img_rest
#os.system("cp %s %s" % (img_nifti, work_dir))

# get T-mean of rs image
fslmaths = MeanImage()
fslmaths.inputs.in_file   = img_rest
fslmaths.inputs.out_file  = 'rest_mean.nii.gz'
fslmaths.inputs.dimension = 'T'
fslmaths.run()

# do bbregister
bbreg = BBRegister()
bbreg.inputs.contrast_type   = 't2'
bbreg.inputs.source_file     = 'rest_mean.nii.gz'
bbreg.inputs.init 	     = 'fsl'
bbreg.inputs.subjects_dir    = freesurfer_dir
bbreg.inputs.subject_id      = 'recon_all'
bbreg.inputs.out_reg_file    = 'rest2anat.dat'
bbreg.inputs.out_fsl_file    = 'rest2anat.mat'
bbreg.inputs.registered_file = 'rest2anat_highRes.nii.gz'
bbreg.inputs.epi_mask 	     = True
bbreg.run()

# get structural image
img_struc = os.path.join(free_dir, subject_id, Tscan, 
			 'recon_all/mri/brain.mgz') 

# convert structural image into nifti 
os.system("mri_convert %s %s" % (img_struc, 'brain.nii.gz'))
		
# convert bbregister out into itk format for ants later...
c3 = C3dAffineTool()
c3.inputs.transform_file  = 'rest2anat.mat'
c3.inputs.itk_transform   = 'rest2anat_itk.mat'
c3.inputs.reference_file  = 'brain.nii.gz'
c3.inputs.source_file     = 'rest_mean.nii.gz'
c3.inputs.fsl2ras         = True
c3.run()
