import os, sys
import nipype.interfaces.ants as ants

data_in = '/scr/ilz2/bayrak/stroke_bbreg'
data_out = '/scr/ilz2/bayrak/stroke_rest2mni'
data_ants = '/scr/ilz2/bayrak/stroke_ants'
mni_dir = '/usr/share/fsl/5.0/data/standard'

subject_id = sys.argv[1]
scan = sys.argv[2]
Tscan = sys.argv[3]

if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)
if not os.path.exists(os.path.join(work_dir, scan + '_' + Tscan)):
	os.makedirs(os.path.join(work_dir, scan + '_' + Tscan))
work_dir = os.path.join(work_dir, scan + '_' + Tscan)

# go into working directory
os.chdir(work_dir)

# find functional data to be registered
img_rest = os.path.join(data_in, subject_id, scan + '_' + Tscan, 
			'rest_ss.nii.gz')

os.system("cp %s %s" % (img_rest, work_dir))

# apply all transform matrices ($bbregister & $ants.Register) on rs-image
at = ants.ApplyTransforms()
at.inputs.input_image_type = 3
at.inputs.input_image = 'rest_ss.nii.gz'
at.inputs.transforms = [os.path.join(data_ants, subject_id, Tscan, 'transform1Warp.nii.gz'),
			os.path.join(data_ants, subject_id, Tscan, 'transform0GenericAffine.mat'),
			os.path.join(data_in, subject_id, scan+'_'+Tscan, 'rest2anat_itk.mat')]
at.inputs.reference_image = os.path.join(mni_dir, 'MNI152_T1_2mm_brain.nii.gz')
at.inputs.interpolation = 'BSpline'
at.inputs.invert_transform_flags = [False, False, False]
at.inputs.output_image = 'rest_mni.nii.gz'
print at.cmdline
at.run()


