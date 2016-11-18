"""
convert dicoms to nifti for stroke patients data
"""
import os, sys, glob
from subprocess import call
from dcmstack.extract import default_extractor
from dicom import read_file
from nipype.utils.filemanip import filename_to_list


subject_id = sys.argv[1]

data_dir = '/nobackup/ilz2/bayrak/subjects/'

scan_path = os.path.join(data_dir, subject_id, 'dicom')

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

	dicom_dir = os.path.join(data_dir, subject_id, 'dicom', scan)

	nifti_dir = os.path.join(data_dir, subject_id, 'nifti', scan)

	if not os.path.exists(nifti_dir):
		os.makedirs(nifti_dir)
	os.chdir(nifti_dir)

	#output_name = 'unknown'
	
	if scan[0:4] == 'rest':
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
		
	if scan[0:5] == 'flair':
		output_name = 'flair'
	if scan[0:3] == 'dwi':
		output_name = 'dwi'
	if scan[0:6] == 'mprage':
		output_name = 'T1'
	
	print "converting files ", dicom_dir, "..."
	call(["dcmstack", dicom_dir,
		"--dest-dir", nifti_dir,
		"-o", output_name])

