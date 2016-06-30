from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.io as nio
import nipype.interfaces.freesurfer as fs
from nipype.interfaces.freesurfer.preprocess import ReconAll


subject_list = ['01']

for subject in subject_list:


  working_dir = '/scr/ilz2/bayrak/test/' + subject + '/'
  data_dir = '/scr/ilz2/bayrak/32_COIL_nifti/' + subject + '/'
  out_dir = '/scr/ilz2/bayrak/test/out_dir/' 

  templates={'stru': 'T*.nii.gz'}

  selectfiles = Node(nio.SelectFiles(templates, 
		    base_directory = data_dir), name='selectfiles')


  


  recon_all = Node(interface=ReconAll(), name='recon_all')
		  #iterfield=['T1_files'] )
  
  #recon_all.inputs.subject_id = subject
  #recon_all.inputs.subjects_dir = data_dir
  
  wf = Workflow(name='work_flow')
  wf.base_dir = working_dir
  wf.config['execution']['crashdump_dir'] = wf.base_dir + "/crash_files"

  wf.connect(selectfiles, 'stru', recon_all, 'T1_files')
  wf.run("MultiProc")


# recon-all -all -i /scr/ilz2/bayrak/32_COIL_nifti/01/T1d01.nii.gz -subjid recon_all -sd /scr/ilz2/bayrak/test/work_flow/01/recon_all