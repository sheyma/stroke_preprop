import os, sys
from subprocess import call

data_dir = '/scr/ilz2/bayrak/32_COIL_ordered/'
working_dir = '/scr/ilz2/bayrak/32_COIL_nifti/'

subject_id = sys.argv[1]

scan_path = os.path.join(data_dir, subject_id)
print scan_path
scans = next(os.walk(scan_path))[1]
print ''
print scans
print ''

for scan in scans:

	dicom_files = os.path.join(data_dir, subject_id, scan)

	out_dir = os.path.join(working_dir, subject_id, scan)
	if not os.path.exists(out_dir):
    		os.makedirs(out_dir)	

	output_name = scan	

	print "converting files ", out_dir, "..."
	call(["dcmstack", dicom_files,
		"--dest-dir", out_dir,
		"-o", output_name])


