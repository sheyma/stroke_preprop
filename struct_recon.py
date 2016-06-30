from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.io as nio
import nipype.interfaces.freesurfer as fs
from nipype.interfaces.freesurfer.preprocess import ReconAll
from nipype.interfaces.io import DataSink, SelectFiles
import os

subject_list = ['01']

for subject in subject_list:


  working_dir = '/scr/ilz2/bayrak/TEST/' + subject + '/'
  
  if not os.path.exists(working_dir):
    os.mkdir(working_dir)
  
  
  data_dir = '/scr/ilz2/bayrak/32_COIL_nifti/' + subject + '/'
  
  templates={'stru': '{scan}.nii.gz'}

  selectfiles = Node(nio.SelectFiles(templates, 
		    base_directory = data_dir), name='selectfiles')

  selectfiles.iterables = ('scan', ['T1d01'])
  


  recon_all = Node(interface=ReconAll(), name='recon_all')

  recon_all.inputs.subjects_dir = working_dir
  
  wf = Workflow(name='work_flow')
  wf.base_dir = working_dir
  wf.config['execution']['crashdump_dir'] = wf.base_dir + "/crash_files"

  wf.connect(selectfiles, 'stru', recon_all, 'T1_files')
  
  ds = Node(DataSink(), name='ds')
  ds.inputs.base_directory = working_dir
  ds.inputs.regexp_substitutions = [ ('_scan_', '')]
  
  wf.connect(recon_all, 'out_file', ds, 'fuck')
  
  
  wf.run("MultiProc")


# recon-all -all -i /scr/ilz2/bayrak/32_COIL_nifti/01/T1d01.nii.gz -subjid recon_all -sd /scr/ilz2/bayrak/test/work_flow/01/recon_all