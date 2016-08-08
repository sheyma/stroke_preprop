import os, sys
import nipype.interfaces.ants as ants

data_in = '/scr/ilz2/bayrak/stroke_bbreg'
data_out = '/scr/ilz2/bayrak/stroke_rs2mni'

subject_id = '01'
scan = 'rsd01'
Tscan = 'T1d01'

if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)
if not os.path.exists(os.path.join(work_dir, scan)):
	os.makedirs(os.path.join(work_dir, scan))
work_dir = os.path.join(work_dir, scan)

# go into working directory
os.chdir(work_dir)

# find functional data to be registered
img_rest = os.path.join(data_in, subject_id, scan, 'rest_ss.nii.gz')
os.system("cp %s %s" % (img_rest, work_dir))

# MNI template (no skull)
mni_temp = os.path.join('/usr/share/fsl/5.0/data/standard', 
			'MNI152_T1_1mm_brain.nii.gz')

# specify ants registration out dir
ants_reg = os.path.join('/scr/ilz2/bayrak/stroke_ants/',
			subject_id, Tscan)

# apply all transforms
print "WORK DIR", work_dir

#at = ants.ApplyTransforms()
##at.inputs.dimension = 3
#at.inputs.input_image_type = 3
#at.inputs.input_image = '/scr/ilz2/bayrak/stroke_rs2mni/01/rsd01/rest_ss.nii.gz'
#at.inputs.transforms = '/scr/ilz2/bayrak/stroke_bbreg/01/rsd01/rest2anat_itk.mat'
#at.inputs.reference_image = '/scr/ilz2/bayrak/stroke_bbreg/01/rsd01/brain.nii.gz'
#at.inputs.interpolation = 'BSpline'
#at.inputs.invert_transform_flags = [False]
#at.inputs.output_image = '/scr/ilz2/bayrak/stroke_rs2mni/01/rsd01/rest_01.nii.gz'
#print at.cmdline
#at.run()


at = ants.ApplyTransforms()
#at.inputs.dimension = 3
at.inputs.input_image_type = 3
at.inputs.input_image = '/scr/ilz2/bayrak/stroke_rs2mni/01/rsd01/rest_01.nii.gz'
at.inputs.transforms = ['/scr/ilz2/bayrak/stroke_ants/01/T1d01/transform1InverseWarp.nii.gz',
			'/scr/ilz2/bayrak/stroke_ants/01/T1d01/transform0GenericAffine.mat']
at.inputs.reference_image = mni_temp
at.inputs.interpolation = 'BSpline'
at.inputs.invert_transform_flags = [False, False]
at.inputs.output_image = '/scr/ilz2/bayrak/stroke_rs2mni/01/rsd01/rest_02.nii.gz'
print at.cmdline
at.run()


#applytransform = Node(ants.ApplyTransforms(input_image_type = 3,
#                                           #output_image='rest_preprocessed2mni.nii.gz',
#                                           interpolation = 'BSpline',
#                                           invert_transform_flags=[False, False]),
#                      name='applytransform')
   
#applytransform.inputs.reference_image=template
#applytransform.plugin_args={'submit_specs': 'request_memory = 30000'}
#mni.connect([(selectfiles, applytransform, [('rest', 'input_image')]),
 #            (translist, applytransform, [('out', 'transforms')])
#])
