import os
from nipype.interfaces import fsl
from subprocess import call

data_dir = '/scr/ilz2/bayrak/TEST/01'
os.chdir(data_dir)

# MNI template (no skull)
mni_temp = os.path.join('/usr/share/fsl/5.0/data/standard', 
			'MNI152_T1_1mm_brain.nii.gz')

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
#flt = fsl.FLIRT()
#flt.inputs.cost = 'mutualinfo'
#flt.inputs.output_type = "NIFTI_GZ"
#flt.inputs.in_file = img_RPI
#flt.inputs.reference = mni_temp
#flt.inputs.out_file = os.path.join(data_dir, 'brain_mni.nii.gz')
#flt.inputs.out_matrix_file = os.path.join(data_dir, 'brain_mni_flirt.mat')
#flt.run()

# non-linear registration with FNIRT

fnirt = fsl.FNIRT()
fnirt.inputs.in_file = 'brain_mni.nii.gz'
fnirt.inputs.ref_file = mni_temp
fnirt.inputs.fieldcoeff_file    = True
fnirt.inputs.jacobian_file      = True
# fnirt outputs...
fnirt.field_file =  'brain_mni_field.nii.gz'
fnirt.fieldcoeff_file = 'brain_mni_fieldcoef.nii.gz'
fnirt.warped_file = 'brain_mni_warped.nii.gz'
print fnirt.cmdline
fnirt.run()

# non-linear reg. >> do it also for 1 mm
# fnirt --config=/scr/sambesi1/workspace/Projects/GluREST/registration/T1_2_MNI152_2mm.cnf  --cout=T1_mni_fieldwarp.nii.gz --in=/scr/ilz2/bayrak/TEST/01/T1_mni.nii.gz --jout=T1_mni_field_jacobian.nii.gz --logout=T1_mni_log.txt --ref=/usr/share/fsl/5.0/data/standard/MNI152_T1_2mm_brain.nii.gz --iout=T1_mni_warped.nii.gz


