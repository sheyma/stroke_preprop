import os
import sys
import shutil
from nipype.pipeline.engine import Node, Workflow
from nipype.interfaces.dcmstack import DcmStack
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
from nipype.interfaces.io import DataSink, SelectFiles

data_dir = '/scr/ilz2/bayrak/32_COIL_ordered/'
working_dir = '/scr/ilz2/bayrak/test/'




wflow = Workflow(name='wflow')
wflow.base_dir = working_dir
wflow.config['execution']['crashdump_dir'] = wflow.base_dir + "/crash_files"

file_template = {'test' : '01/DWId00/*dcm'}


selectfiles = Node(SelectFiles(file_template, base_directory=data_dir),
                   name="selectfiles")


stacker = Node(DcmStack(embed_meta=True),
	       name='stacker')

stacker.inputs.out_format = 'DWId00'

ds_dir = os.path.join(working_dir, 'OUT')
ds = Node(DataSink(), name='ds')
ds.inputs.base_directory = ds_dir

wflow.connect(selectfiles, 'test', stacker, 'dicom_files')
wflow.connect(stacker, 'out_file' , ds, 'bla')

wflow.run()


