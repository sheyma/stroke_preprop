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
                              
df.to_csv(OutFile, index=False, cols=('KEYS', 'VALUES'), sep='\t')    

print "OUTFILE", OutFile