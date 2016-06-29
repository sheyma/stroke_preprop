import os
import sys
import shutil
from nipype.pipeline.engine import Node, Workflow
from nipype.interfaces.dcmstack import DcmStack
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
from nipype.interfaces.io import DataSink, SelectFiles

data_dir = '/scr/ilz2/bayrak/32_COIL_ordered/'
working_dir = '/scr/ilz2/bayrak/32_COIL_nifti/'

subject_id = sys.argv[1]

scan_path = os.path.join(data_dir, subject_id)
print scan_path
scans = next(os.walk(scan_path))[1]
print ''
print scans


for scan in scans:
    
  wflow = Workflow(name='wflow')
  wflow.base_dir = working_dir
  wflow.config['execution']['crashdump_dir'] = wflow.base_dir + "/crash_files"

  file_template = {'test' : subject_id + '/' + scan +'/*dcm'}

  selectfiles = Node(SelectFiles(file_template, base_directory=data_dir),
		    name="selectfiles")

  stacker = Node(DcmStack(embed_meta=True),
		name='stacker')
  stacker.inputs.out_format = scan

  ds_dir = working_dir
  ds = Node(DataSink(), name='ds')
  ds.inputs.base_directory = ds_dir

  wflow.connect(selectfiles, 'test', stacker, 'dicom_files')
  wflow.connect(stacker, 'out_file' , ds, subject_id)

  wflow.run()


