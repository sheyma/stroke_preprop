import os
from nipype.pipeline.engine import Node, Workflow
from nipype.interfaces.dcmstack import DcmStack
from nipype.interfaces.utility import Function
import nipype.interfaces.io as nio
from nipype.interfaces.io import DataSink, SelectFiles

data_dir = '/scr/ilz2/bayrak/32_COIL_ordered/'
working_dir = '/scr/ilz2/bayrak/32_COIL_nifti/'

subject_list = ['01', '02']


def my_fun(a, b):
    # a : data directory
    # b : subject id
    scan_path = os.path.join(a, b)
    scans = next(os.walk(scan_path))[1]
    return scans 

  
workflow_dir = os.path.join(working_dir + 'wf')
   
wflow = Workflow(name='wflow')
wflow.base_dir = os.path.join(workflow_dir, subject_id, scan )
wflow.config['execution']['crashdump_dir'] = wflow.base_dir + "/crash_files"

# iterate over subjects -> output is a list!!!
subject_infosource = Node(util.IdentityInterface(fields=['subject']), 
                  name='subject_infosource')

subject_infosource.iterables=[('subject', subjects_list)]

# find scan sub dirs
findScans = Node(Function(input_names=['a', 'b'],
                  output_names=['scans'],
                  function=my_fun), name='fixhdr')

# if 'a' is a constant input over all subjects
findScans.inputs.a = data_dir

wflow.connect(subject_infosource, 'subject', findScans, 'b')

# iterate over scans -> output is a list!!!
scans_infosource = Node(util.IdentityInterface(fields=['scan']), 
                  name='scan_infosource')
                  
wflow.connect(findScans, 'scans', scans_infosource, 'scan')



