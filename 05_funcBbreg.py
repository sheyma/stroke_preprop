"""
    # registration from (mean) funcitonal to anatomical image
    # converting bbregister ouput into itk format
    
freesurfer_dir = '/data/pt_mar006/freesurfer'
data_dir       = '/data/pt_mar006/subjects'
subject_id     = 'sd51_d01'
Usage:
    $ python 05_funcBbreg.py <freesurfer_dir> <data_dir> <subjects_dir>
"""
import os, sys
from nipype.interfaces.freesurfer import BBRegister
from nipype.interfaces.c3 import C3dAffineTool

freesurfer_dir = sys.argv[1]
data_dir       = sys.argv[2]
subject_id     = sys.argv[3]

# define working dir
work_dir = os.path.join(data_dir, subject_id,  
			'preprocessed/func/coregister') 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

# Step#1 coregistering rest scan to T1
# get mean rest scan after alignment
rest_mean  = os.path.join(data_dir, subject_id,
			  'preprocessed/func/realign',
			  'mean_corr_rest_roi.nii.gz')

# define names for the bbregister outputs
reg_file  = os.path.abspath('rest2anat_highRes.nii.gz')
cost_file = os.path.abspath('rest2anat.dat.mincost')

# define working dir for transform matrices
work_dir_trf = os.path.abspath('transforms2anat') 
if not os.path.exists(work_dir_trf):
	os.makedirs(work_dir_trf)

# go into working dir
os.chdir(work_dir_trf)

# do bbregister
bbreg = BBRegister()
bbreg.inputs.contrast_type   = 't2'
bbreg.inputs.source_file     = rest_mean
bbreg.inputs.init 	     = 'fsl'
bbreg.inputs.subjects_dir    = freesurfer_dir
bbreg.inputs.subject_id      = subject_id
bbreg.inputs.out_reg_file    = 'rest2anat.dat'
bbreg.inputs.out_fsl_file    = 'rest2anat.mat'
bbreg.inputs.registered_file = reg_file
bbreg.inputs.epi_mask 	     = True
bbreg.run()

# Step#2 formatting bbregister output
# get structural reference image
ref_struc = os.path.join(data_dir, subject_id,
			 'preprocessed/anat', 'brain.nii.gz')

# convert bbregister out into itk format for ants later
c3 = C3dAffineTool()
c3.inputs.transform_file  = 'rest2anat.mat'
c3.inputs.itk_transform   = 'rest2anat_itk.mat'
c3.inputs.reference_file  = ref_struc
c3.inputs.source_file     = rest_mean
c3.inputs.fsl2ras         = True
c3.run()
