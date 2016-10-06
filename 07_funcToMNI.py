import os, sys
import nipype.interfaces.ants as ants

# data dir's
data_dir = '/scr/ilz2/bayrak/preprocess/'
mni_dir  = '/scr/ilz2/bayrak'

# subject id, resting scan, T1 scan
subject_id = sys.argv[1]
scan 	   = sys.argv[2]
Tscan      = sys.argv[3]

# create a working directory	
rs_T1 = scan+'_'+Tscan

# define working dir
rs_T1    = scan+'_'+Tscan

work_dir = os.path.join(data_dir, subject_id, rs_T1, 
			'func2mni') 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)

# go into working directory
os.chdir(work_dir)

# data dir's to
ants_dir = os.path.join(data_dir, subject_id, Tscan, 
			'ants_all')
func_dir = os.path.join(data_dir, subject_id, rs_T1,
			'denoise')
bbre_dir = os.path.join(data_dir, subject_id, rs_T1,
			'bbregister')

# find functional data to be registered

img_rest = os.path.join(func_dir,
			'corr_rest_roi_denoised.nii.gz')

# apply all transform matrices ($bbregister & $ants.Register) 
# on resting-state image
at			   = ants.ApplyTransforms()
at.inputs.input_image_type = 3
at.inputs.input_image      = img_rest
at.inputs.transforms	   = [os.path.join(ants_dir, 						   'transform1Warp.nii.gz'),
              		      os.path.join(ants_dir, 						   'transform0GenericAffine.mat'),
         		      os.path.join(bbre_dir, 						   'rest2anat_itk.mat')]
at.inputs.reference_image  = os.path.join(mni_dir, 
					  'MNI152_T1_3mm_brain.nii.gz')
at.inputs.interpolation    = 'BSpline'
at.inputs.invert_transform_flags = [False, False, False]
at.inputs.output_image     = os.path.abspath('rest_mni.nii.gz')
#print at.cmdline
at.run()



