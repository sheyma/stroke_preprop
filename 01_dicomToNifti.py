import os, sys, glob
from subprocess import call
from dcmstack.extract import default_extractor
from dicom import read_file
from nipype.utils.filemanip import filename_to_list

data_dir = '/scr/ilz2/bayrak/32_COIL_ordered/'
data_out = '/scr/ilz2/bayrak/new_nifti/'

subject_id = sys.argv[1]

scan_path = os.path.join(data_dir, subject_id)
print scan_path
scans = next(os.walk(scan_path))[1]
print ''
print scans
print ''

# define a function getting slice time acquisition (STA) from dicoms
def get_info(dicom_files):
	"""Given a Siemens dicom file return metadata
	Returns
	-------
	Slice Acquisition Times
	"""
	meta = default_extractor(read_file(filename_to_list(dicom_files)[0],
		                       stop_before_pixels=True,
		                       force=True))
	# returning STA in seconds...
	return meta['CsaImage.MosaicRefAcqTimes']  


for scan in scans:

	dicom_dir = os.path.join(data_dir, subject_id, scan)

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

		dicom_files = []
		for file in os.listdir(dicom_dir):
			if file.endswith(".dcm") and not file.startswith('.'):
				dicom_files.append(os.path.join(dicom_dir, 
							file))

		print "getting slice sequence for resting state..."
		# get slice time acqusition(in sec)		
		sta = get_info(dicom_files)
		# convert sta into milisecond
		sta_ms = map(lambda x: x/1000., sta)
		# export sta as a text file
		thefile = open('slice_timing.txt', 'w')
		for item in sta_ms:
			thefile.write("%s\n" % item)
		
	if scan[0:5] == 'FLAIR':
		output_name = 'flair'
	if scan[0:2] == 'DW':
		output_name = 'dwi'
	if scan[0:2] == 'T1':
		output_name = 'T1'

	print "converting files ", dicom_dir, "..."
	call(["dcmstack", dicom_dir,
		"--dest-dir", work_dir,
		"-o", output_name])

