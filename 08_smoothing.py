import os, sys



# data dir's
data_in   = '/scr/ilz2/bayrak/new_func2mni'
data_out  = '/scr/ilz2/bayrak/new_smooth'

# subject id, resting scan, T1 scan
subject_id = sys.argv[1]
rs_T1      = sys.argv[2]

if not os.path.exists(os.path.join(data_out, subject_id)):
	os.makedirs(os.path.join(data_out, subject_id))
work_dir = os.path.join(data_out, subject_id)
if not os.path.exists(os.path.join(work_dir, rs_T1)):
	os.makedirs(os.path.join(work_dir, rs_T1))
work_dir = os.path.join(work_dir, rs_T1)

# go into working directory
os.chdir(work_dir)


rest_fun2mni = os.path.join(data_in, subject_id, rs_T1,
				'rest_mni.nii.gz')

# Xiangyu
from nipype.interfaces.fsl import maths
smooth = maths.IsotropicSmooth()
smooth.inputs.in_file = rest_fun2mni
smooth.inputs.fwhm    = 6
smooth.run()
#print smooth.cmdline

# A.S.Kanaan
from nilearn.image import smooth_img
smoothed_img = smooth_img(rest_fun2mni, fwhm=6)
smoothed_img.to_filename("OUT.nii") 

