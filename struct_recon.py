from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.io as nio
import nipype.interfaces.freesurfer as fs
from nipype.interfaces.freesurfer.preprocess import ReconAll
import os, glob

subject = '02'

data_dir = '/scr/ilz2/bayrak/32_COIL_nifti/' + subject + '/'

scans = [os.path.basename(x) for x in glob.glob(data_dir + 'T*nii.gz')]


for scan in scans:

  SCAN = scan[:-7]
  
  working_dir = '/scr/ilz2/bayrak/TEST/' + subject + '/'
  
  if not os.path.exists(working_dir):
    os.mkdir(working_dir)
  
  working_dir_scan = working_dir + '/' + SCAN + '/'
  
  if not os.path.exists(working_dir_scan):
    os.mkdir(working_dir_scan)
    
  templates={'stru': scan}

  selectfiles = Node(nio.SelectFiles(templates, 
		    base_directory = data_dir), name='selectfiles')
 
  recon_all = Node(interface=ReconAll(), name='recon_all')

  recon_all.inputs.subjects_dir = working_dir_scan
  
  wf = Workflow(name='work_flow')
  wf.base_dir = working_dir_scan
  wf.config['execution']['crashdump_dir'] = wf.base_dir + "/crash_files"

  wf.connect(selectfiles, 'stru', recon_all, 'T1_files')
  wf.run("MultiProc")

