#!/bin/bash

echo "BEGIN host info"
hostname
uptime
free
ulimit -a
echo "END host info"

CBSTOOLS FSL --version 5.0 FREESURFER --version 6.0.0 AFNI C3D DCMSTACK XLRD NUMPY SCIPY ANTSENV --version 2.1.0-rc3 "$@"

# cbstools 3.0
# fsl 5.0
# freesurfer 5.3.0
# afni 2011-12-21_1024-20141011n
# c3d 1.0.0-2014-06-11
# dcmstack 0.7.dev
# xlrd 0.9.3
# ants 2.1.0-rc3
# six 1.9.0
# pyparsing 2.0.3
# mathplotlib 1.4.2
# numpy 1.9.1
# scipy 0.15.1
