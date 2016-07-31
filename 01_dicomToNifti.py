import os, sys
from subprocess import call

data_dir = '/scr/ilz2/bayrak/32_COIL_ordered/'
data_out = '/scr/ilz2/bayrak/stroke_nifti/'

subject_id = sys.argv[1]

scan_path = os.path.join(data_dir, subject_id)
print scan_path
scans = next(os.walk(scan_path))[1]
print ''
print scans
print ''

for scan in scans:

	dicom_files = os.path.join(data_dir, subject_id, scan)

	if not os.path.exists(os.path.join(data_out, subject_id)):
		os.makedirs(os.path.join(data_out, subject_id))
	work_dir = os.path.join(data_out, subject_id)

	if not os.path.exists(os.path.join(work_dir, scan)):
		os.makedirs(os.path.join(work_dir, scan))
	work_dir = os.path.join(work_dir, scan)

	os.chdir(work_dir)

	output_name = 'unknown'
	if scan[0:3] == 'rsd':
		output_name = 'rest'
	if scan[0:5] == 'FLAIR':
		output_name = 'flair'
	if scan[0:2] == 'DW':
		output_name = 'dwi'
	if scan[0:2] == 'T1':
		output_name = 'T1'

	print "converting files ", dicom_files, "..."
	call(["dcmstack", dicom_files,
		"--dest-dir", work_dir,
		"-o", output_name])
	
	img_nifti = os.path.join(output_name + '.nii.gz')

	# change the orientation of nifti-1 file
	img_RPI = output_name + '.nii.gz'
	os.system("fslswapdim %s RL PA IS %s" % (img_nifti, img_RPI))


