import os, sys
import nipype.interfaces.ants as ants

# data dir's
data_bbreg = '/scr/ilz2/bayrak/new_bbreg'
data_ants  = '/scr/ilz2/bayrak/new_ants'
data_rest  = '/scr/ilz2/bayrak/new_func'
data_out   = '/scr/ilz2/bayrak/new_func2mni'

mni_dir = '/scr/ilz2/bayrak'

# subject id, resting scan, T1 scan
subject_id = sys.argv[1]
scan 	   = sys.argv[2]
Tscan      = sys.argv[3]

# dir for 'resting scan registered to T1 scan'
rs_T1 = scan+'_'+Tscan

if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)
if not os.path.exists(os.path.join(work_dir, rs_T1)):
	os.makedirs(os.path.join(work_dir, rs_T1))
work_dir = os.path.join(work_dir, rs_T1)

# go into working directory
os.chdir(work_dir)

# find functional data to be registered
img_rest = os.path.join(data_rest, subject_id, scan, 
			'corr_rest_roi.nii.gz')

# apply all transform matrices ($bbregister & $ants.Register) 
# on resting-state image
at			   = ants.ApplyTransforms()
at.inputs.input_image_type = 3
at.inputs.input_image      = img_rest
at.inputs.transforms	   = [os.path.join(data_ants, subject_id, Tscan, 						   'transform1Warp.nii.gz'),
              		      os.path.join(data_ants, subject_id, Tscan, 						   'transform0GenericAffine.mat'),
         		      os.path.join(data_bbreg, subject_id, rs_T1, 						   'rest2anat_itk.mat')]
at.inputs.reference_image  = os.path.join(mni_dir, 
					  'MNI152_T1_3mm_brain.nii.gz')
at.inputs.interpolation    = 'BSpline'
at.inputs.invert_transform_flags = [False, False, False]
at.inputs.output_image     = os.path.abspath('rest_mni.nii.gz')
#print at.cmdline
at.run()


