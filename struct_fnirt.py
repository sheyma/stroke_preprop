import os
from nipype.interfaces import fsl
from subprocess import call

data_dir = '/scr/ilz2/bayrak/TEST/05'
os.chdir(data_dir)

# MNI template (no skull)
mni_temp = os.path.join('/usr/share/fsl/5.0/data/standard', 
			'MNI152_T1_1mm_brain.nii.gz')

# MNI maks
mni_mask = os.path.join('/usr/share/fsl/data/standard/',
			'MNI152_T1_1mm_brain_mask_dil.nii.gz')

# MNI template (with skull)
#mni_skull = os.path.join('/usr/share/fsl/5.0/data/standard',
#			  'MNI152_T1_1mm.nii.gz')
 	
# convert .mgz to nifti-1 format
img_mgz = os.path.join(data_dir, 'brain.mgz')
img_nifti = os.path.join(data_dir, 'brain.nii.gz')

os.system("mri_convert %s %s" % (img_mgz, img_nifti))

# change the orientation of nifti-1 file
img_RPI = os.path.join(data_dir, 'brain_RPI.nii.gz')

os.system("fslswapdim %s RL PA IS %s" % (img_nifti, img_RPI))

# linear registration with FLIRT to MNI
flt = fsl.FLIRT()
flt.inputs.cost = 'mutualinfo'
flt.inputs.output_type = "NIFTI_GZ"
flt.inputs.in_file = img_RPI
flt.inputs.reference = mni_temp
flt.inputs.out_file = os.path.join(data_dir, 'brain_mni.nii.gz')
flt.inputs.out_matrix_file = os.path.join(data_dir, 'brain_mni_flirt.mat')
flt.run()

# non-linear registration with FNIRT
fnirt = fsl.FNIRT()
fnirt.inputs.in_file = 'brain_mni.nii.gz'
fnirt.inputs.ref_file = mni_temp
fnirt.inputs.refmask_file = mni_mask
fnirt.inputs.skip_implicit_ref_masking = False #
fnirt.inputs.skip_implicit_in_masking = False #
fnirt.inputs.refmask_val = 0
fnirt.inputs.inmask_val = 0
fnirt.inputs.subsampling_scheme = [4, 4, 2, 2, 1, 1]
fnirt.inputs.max_nonlin_iter = [5, 5, 5, 5, 5, 10]
fnirt.inputs.in_fwhm = [8, 6, 5, 4, 3, 2]
fnirt.inputs.ref_fwhm = [8, 6, 5, 4, 2, 0]
fnirt.inputs.regularization_lambda = [300, 150, 100, 50, 40, 30]
fnirt.inputs.apply_intensity_mapping = [1, 1, 1, 1, 1, 0]
fnirt.inputs.apply_refmask = [1, 1, 1, 1, 1, 1]
fnirt.inputs.apply_inmask = [1]
fnirt.inputs.warp_resolution = 10, 10, 10
fnirt.inputs.skip_lambda_ssq = False #
fnirt.inputs.regularization_model = 'bending_energy'
fnirt.inputs.intensity_mapping_model = 'global_non_linear_with_bias'
fnirt.inputs.intensity_mapping_order = 5
fnirt.inputs.biasfield_resolution = 50, 50, 50
fnirt.inputs.bias_regularization_lambda = 10000
fnirt.inputs.derive_from_ref = False
fnirt.inputs.fieldcoeff_file    = True
fnirt.inputs.jacobian_file      = True
fnirt.field_file =  'brain_mni_field.nii.gz'
fnirt.fieldcoeff_file = 'brain_mni_fieldcoef.nii.gz'
fnirt.warped_file = 'brain_mni_warped.nii.gz'

#print fnirt.cmdline

fnirt.run()

# non-linear reg. >> do it also for 1 mm
# fnirt --config=/scr/sambesi1/workspace/Projects/GluREST/registration/T1_2_MNI152_2mm.cnf  --cout=T1_mni_fieldwarp.nii.gz --in=/scr/ilz2/bayrak/TEST/01/T1_mni.nii.gz --jout=T1_mni_field_jacobian.nii.gz --logout=T1_mni_log.txt --ref=/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz --iout=T1_mni_warped.nii.gz


