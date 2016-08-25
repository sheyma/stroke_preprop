# Adapted from:
# Copyright (c) 2014 Bastian Rieck 
# https://github.com/Submanifold/DICOM/blob/master/dicomcat.py

import dicom
import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("files", metavar="FILE", type=str, nargs="+", help="File for concatenation")
arguments = parser.parse_args()

filenames = arguments.files

#filenames = ['/scr/ilz2/bayrak/32_COIL_ordered/01/T1d01/t1-2_97.dcm',
#             '/scr/ilz2/bayrak/32_COIL_ordered/01/T1d01/t1-2_97.dcm']

#filenames = ['/scr/ilz2/bayrak/TEST/rs1_9.dcm']


def getParams(filename):
    f = dicom.read_file(filename)
    return f.EchoNumbers ,\
            f.EchoTime,\
            f.ImagingFrequency,\
            f.PixelBandwidth,\
            f.RepetitionTime,\
            f.ScanningSequence,\
            f.SliceThickness,\
            f.PixelRepresentation,\
            f.SeriesDescription,\
            f.Columns,\
            f.Rows
            
for index, filename in enumerate(filenames):
    
    f = dicom.read_file(filename)    
    
    if index == 0:
        params_init = getParams(filename)
        depth = 1
              
        real_dir = os.path.realpath(filename)
        out_dir = os.path.dirname(os.path.dirname(real_dir))
        out_file = os.path.basename(os.path.dirname(real_dir))
    
    else :
        params = getParams(filename)
        
        if params != params_init:
            raise Exception("Scan parameters -> not same over slices!")
        else:
            depth += 1


new_params = params + (depth,)

OutFile = os.path.join(out_dir, out_file + '.csv')

df = pd.DataFrame({'KEYS': ['EchoNumbers', 
                              'EchoTime',
                              'ImagingFrequency',
                              'PixelBandwidth',
                              'RepetitionTime',
                              'ScanningSequence',
                              'SliceThickness',
                              'PixelRepresentation',
                              'SeriesDescription',
                              'Columns',
                              'Rows',
                              'Depth'],
                  'VALUES' : new_params})   
A = filenames[0]
print A

from dcmstack.extract import default_extractor
from dicom import read_file
from nipype.utils.filemanip import filename_to_list

def get_info(dicom_files):
	"""Given a Siemens dicom file return metadata
	Returns
	-------
	RepetitionTime
	Slice Acquisition Times
	Spacing between slices
	"""
	meta = default_extractor(read_file(filename_to_list(dicom_files)[0],
		                       stop_before_pixels=True,
		                       force=True))
	#print meta

	return (meta['RepetitionTime'] / 1000., meta['CsaImage.MosaicRefAcqTimes'],
		meta['SpacingBetweenSlices'])

print get_info(A)   
                           
#df.to_csv(OutFile, index=False, cols=('KEYS', 'VALUES'), sep='\t')    

#print "OUTFILE", OutFile
