import os, sys
from subprocess import call

data_dir = '/scr/ilz2/bayrak/32_COIL_ordered/'
data_out = '/scr/ilz2/bayrak/tmp/'

subject_id = sys.argv[1]

scan_path = os.path.join(data_dir, subject_id)
print scan_path
scans = next(os.walk(scan_path))[1]
print ''
print scans
print ''

for scan in scans:

	dicom_files = os.path.join(data_dir, subject_id, scan)
	dicom_files = dicom_files + '/*dcm'

	sbj = 'sd' + subject_id

	if not os.path.exists(os.path.join(data_out, sbj)):
		os.makedirs(os.path.join(data_out, sbj))
	work_dir = os.path.join(data_out, sbj)

	if not os.path.exists(os.path.join(work_dir, scan)):
		os.makedirs(os.path.join(work_dir, scan))
	work_dir = os.path.join(work_dir, scan)

	os.chdir(work_dir)

	output_name = 'unknown'

	if scan[0:3] == 'rsd':

		output_name = 'rest.nii'
		print dicom_files

		os.system("isisconv -in %s -wdialect fsl -out %s" % (dicom_files, output_name))
		os.system("gzip %s" % (output_name))

	if scan[0:5] == 'FLAIR':
		output_name = 'flair'
	if scan[0:2] == 'DW':
		output_name = 'dwi'
	if scan[0:2] == 'T1':
		output_name = 'T1'

	#print "converting files ", dicom_files, "..."
	
	#A =["isisconv", "-in", dicom_files, "-wdialect", "fsl", "-out", work_dir+'/'+output_name+'.nii']
	#print A

	#call(["isisconv", "-in", dicom_files, "-wdialect", "fsl"
	#      "-out", work_dir+'/'+output_name+'.nii'])
	
	#img_nifti = os.path.join(output_name + '.nii.gz')

	# change the orientation of nifti-1 file
	#img_RPI = output_name + '.nii.gz'
	#os.system("fslswapdim %s RL PA IS %s" % (img_nifti, img_RPI))


