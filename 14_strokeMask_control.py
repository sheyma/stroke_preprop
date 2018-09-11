"""
data_dir       = '/data/pt_mar006/subjects'
freesurfer_dir = '/data/pt_mar006/freesurfer/'
mni_dir        = '/data/pt_mar006/subjects_group/'
gm_healthy     = '/data/pt_mar006/newtmp/gm_prob_mni3_ave_rest.nii.gz'
out_dir        = '/data/pt_mar006/newtmp/subjects_masks' 
subject_id     = 'sd02_d01'   ### freesurfer day
X              = 'd00'        ### lesion day

Usage:
	$ python 14_strokeMask_dilated.py <data_dir> <freesurfer_dir> <mni_dir>
 <gm_healthy> <out_dir> <subject_id> <X>
"""

import os, sys, glob
from shutil import copyfile
from nipype.interfaces.fsl.maths import DilateImage
from nipype.interfaces.fsl import MultiImageMaths
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
from nipype.interfaces.fsl.maths import MathsCommand

data_dir       = sys.argv[1]
freesurfer_dir = sys.argv[2]
mni_dir        = sys.argv[3]
gm_healthy     = sys.argv[4]
out_dir        = sys.argv[5]
subject_id     = sys.argv[6]
X              = sys.argv[7]

work_dir = os.path.join(out_dir, subject_id[0:4]) 
if not os.path.exists(work_dir):
	os.makedirs(work_dir)
# go into working dir
os.chdir(work_dir)

###### Step 1: get patient specific GM template
anat_dir = os.path.join(data_dir, subject_id,  
                        'preprocessed/anat') 

gm_labels = [3,8,42,17,18,53,54,11,12,13,26,50,
             51,52,58,9,10,47,48,49,16,28,60]

# get the freesurfer recon_all segmentation output
aseg_mgz = os.path.join(freesurfer_dir, subject_id, 
                        'mri', 'aseg.mgz')
print aseg_mgz
# convert *mgz into *nii.gz
mricon = fs.MRIConvert(in_file  = aseg_mgz,
                       out_file = 'aseg.nii.gz', 
                       out_type = 'niigz').run()

aseg_nifti  = os.path.abspath('aseg.nii.gz')

###### Step # 2: get gray matter mask by binarizing aparc+aseg with gm labels
coolBinarize = fs.Binarize()
coolBinarize.inputs.in_file     = aseg_nifti
coolBinarize.inputs.match       = gm_labels
coolBinarize.out_type           = 'nii.gz'
coolBinarize.inputs.binary_file = 'brain_gmseg.nii.gz'
coolBinarize.run()

###### Step #3: normalize GM mask to MNI (1mm) space
gm_mask  = os.path.join(out_dir, subject_id[0:4],
        		        'brain_gmseg.nii.gz')

at                          = ants.ApplyTransforms()
at.inputs.input_image       = gm_mask
at.inputs.dimension         = 3
at.inputs.reference_image   = os.path.join(mni_dir, 
                                              'MNI152_T1_1mm_brain.nii.gz' )

trans_dir = os.path.join(data_dir, subject_id, 
                         'preprocessed/anat/transforms2mni') 

at.inputs.transforms = [os.path.join(trans_dir,
                                     'transform1Warp.nii.gz'),
                        os.path.join(trans_dir,
                                     'transform0GenericAffine.mat')]

at.inputs.invert_transform_flags = [False, False]

at.inputs.interpolation          = 'BSpline'
at.inputs.output_image           = os.path.join(out_dir, subject_id[0:4],
                                                'brain_gmseg_mni1.nii.gz')
print at.cmdline
os.system(at.cmdline)
#at.run()

##### Step #4: resampling MNI1mm -->> MNI3mm
flt = fsl.FLIRT(bins=640, cost_func='mutualinfo')
flt.inputs.apply_isoxfm = 3.0
flt.inputs.in_file      = os.path.join(out_dir, subject_id[0:4],
                                       'brain_gmseg_mni1.nii.gz')
flt.inputs.output_type  = "NIFTI_GZ"
flt.inputs.out_file     = os.path.join(out_dir, subject_id[0:4],
                                       'brain_gmseg_mni3.nii.gz')
flt.inputs.reference    = os.path.join(mni_dir, 
                                       'MNI152_T1_3mm_brain.nii.gz')
flt.run()

##### Step #5: binarize the probabilistic GM map
binarize = MathsCommand()
binarize.inputs.args     = '-thr  0.30 -bin'
binarize.inputs.in_file  = os.path.join(out_dir, subject_id[0:4],
                                       'brain_gmseg_mni3.nii.gz')
binarize.inputs.out_file = os.path.join(out_dir, subject_id[0:4],
                                       'brain_gmseg_mni3_mask.nii.gz')
binarize.run()

####### Step #6: get intra-subject rest mask 
rest_list = []
rest_str  = []
i = 0
for name in glob.glob(data_dir + '/' + subject_id[0:4] + '*' +
                      '/preprocessed/func/connectivity/' +
                      'rest_mask_mni3.nii.gz' ):
    rest_list.append(name)
    i += 1
    if i != 1:
        rest_str.append('-mul %s')

op_string_rest = " ".join((rest_str))

maths = MultiImageMaths()
maths.inputs.in_file       = rest_list[0]
maths.inputs.op_string     = op_string_rest
maths.inputs.operand_files = rest_list[1:]
maths.inputs.out_file      = os.path.join(out_dir, subject_id[0:4],
                                          'rest_intra_mask.nii.gz')
maths.run()

###### Step #7: gm mask lying intra-subject rest mask 
maths = MultiImageMaths()
maths.inputs.in_file       = os.path.join(out_dir, subject_id[0:4],
                                          'rest_intra_mask.nii.gz')
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = os.path.join(out_dir, subject_id[0:4],
                                         'brain_gmseg_mni3_mask.nii.gz')
maths.inputs.out_file      = os.path.join(out_dir, subject_id[0:4],
                                         'brain_gmseg_mni3_mask_rest.nii.gz')
maths.run()


###### Step 8: gm mask lying on health controls ##################
maths = MultiImageMaths()
maths.inputs.in_file       = os.path.join(out_dir, subject_id[0:4],
                                         'brain_gmseg_mni3_mask_rest.nii.gz')
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = gm_healthy
maths.inputs.out_file      = os.path.join(out_dir, subject_id[0:4],
                                         'brain_gmseg_mni3_mask_rest_HC.nii.gz')
maths.run()

##### Step #9: get patient specific GM intersection with lesion mni
lesion_mask   = os.path.join(data_dir, subject_id[0:4] + '_' +  X, 
                             'lesion/lesion_mask_mni.nii.gz')
print lesion_mask
copyfile(lesion_mask, os.path.join(out_dir, subject_id[0:4], 
                                   'lesion_mask_mni.nii.gz'))

maths = MultiImageMaths()
maths.inputs.in_file       = lesion_mask
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = 'brain_gmseg_mni3_mask_rest_HC.nii.gz'
maths.inputs.out_file      = 'lesion_mask_mni_patient_gm.nii.gz'
maths.run()

##### Step #10: dilating lesion mask

lesion_mask_dil = os.path.join(out_dir, subject_id[0:4] ,
			                'lesion_mask_mni_dilated.nii.gz')
dilate = DilateImage()
dilate.inputs.in_file      = lesion_mask
dilate.inputs.operation    = 'modal'
dilate.inputs.out_file     = lesion_mask_dil
dilate.run()

####### Step 11: get patient specific GM intersection with lesion mni dilated 
maths = MultiImageMaths()
maths.inputs.in_file       = lesion_mask_dil
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = 'brain_gmseg_mni3_mask_rest_HC.nii.gz'
maths.inputs.out_file      = 'lesion_mask_mni_dilated_patient_gm.nii.gz'
maths.run()

##### Step #12: get healthy cohort GM intersection with lesion mni
maths = MultiImageMaths()
maths.inputs.in_file       = lesion_mask
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = gm_healthy
maths.inputs.out_file      = 'lesion_mask_mni_healthy_gm.nii.gz'
maths.run()

##### Step #13: get healthy cohort GM intersection with lesion mni dilated
maths = MultiImageMaths()
maths.inputs.in_file       = lesion_mask_dil
maths.inputs.op_string     = '-mul %s'
maths.inputs.operand_files = gm_healthy
maths.inputs.out_file      = 'lesion_mask_mni_dilated_healthy_gm.nii.gz'
maths.run()

###### Step 14: remove dilated lesion from gm #####################
maths = MultiImageMaths()
maths.inputs.in_file       = 'brain_gmseg_mni3_mask_rest_HC.nii.gz'
maths.inputs.op_string     = '-sub %s'
maths.inputs.operand_files = 'lesion_mask_mni_dilated_patient_gm.nii.gz'
maths.inputs.out_file      = 'gm_mask_no_lesion.nii.gz'
maths.run()

