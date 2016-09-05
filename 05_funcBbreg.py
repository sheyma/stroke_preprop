import os, sys
from nipype.interfaces.fsl.maths import MeanImage
from nipype.interfaces.freesurfer import BBRegister
from subprocess import call
from nipype.interfaces.c3 import C3dAffineTool

# data dir's 
data_dir  = '/scr/ilz2/bayrak/preprocess/'

# subject id, resting scan, T1 scan
subject_id = sys.argv[1]
scan 	   = sys.argv[2]
Tscan 	   = sys.argv[3]

# freesurfer dir for recon_all outputs 
freesurfer_dir = os.path.join(data_dir, subject_id, Tscan)

# define working dir
rs_T1    = scan+'_'+Tscan
work_dir = os.path.join(data_dir, subject_id, rs_T1, 
			'bbregister') 

if not os.path.exists(work_dir):
	os.makedirs(work_dir)

# go into working dir
os.chdir(work_dir)

# get motion and slice-time corrected rs image
data_prepro = os.path.join(data_dir, subject_id, 
			     scan, 'func_prepro')

img_rest = os.path.join(data_prepro, 'corr_rest_roi.nii.gz')
print img_rest

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
img_struc = os.path.join(freesurfer_dir, 
			 'recon_all/mri/brain.mgz') 

# convert structural image into nifti 
from nipype.interfaces.freesurfer.preprocess import  MRIConvert
mc = MRIConvert()
mc.inputs.in_file = img_struc
mc.inputs.out_file = 'brain.nii.gz'
mc.inputs.out_type = 'niigz'
mc.run()
		
# convert bbregister out into itk format for ants later...
c3 = C3dAffineTool()
c3.inputs.transform_file  = 'rest2anat.mat'
c3.inputs.itk_transform   = 'rest2anat_itk.mat'
c3.inputs.reference_file  = 'brain.nii.gz'
c3.inputs.source_file     = 'rest_mean.nii.gz'
c3.inputs.fsl2ras         = True
c3.run()
