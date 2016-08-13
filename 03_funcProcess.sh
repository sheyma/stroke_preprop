#!/usr/bin/env bash

##########################################################################################################################
## SCRIPT TO PREPROCESS THE FUNCTIONAL SCAN
## parameters are passed from 0_preprocess.sh
##
## Written by the Underpants Gnomes (a.k.a Clare Kelly, Zarrar Shehzad, Maarten Mennes & Michael Milham)
## for more information see www.nitrc.org/projects/fcon_1000
##
##########################################################################################################################

## subject
subject=$1
## full path to the resting scan
fun_dir=$2
## name of the resting-state scan
rest=$3
## first timepoint (remember timepoint numbering starts from 0)
TRstart=$4
## last timepoint
# TRend = 149 and TRstart=5 
TRend=$5
## TR
TR=$6

## set your desired spatial smoothing FWHM - we use 6 (acquisition voxel size is 3x3x4mm)
FWHM=6
sigma=`echo "scale=10 ; ${FWHM}/2.3548" | bc`

## Set high pass and low pass cutoffs for temporal filtering
hp=0.01
lp=0.1


##########################################################################################################################
##---START OF SCRIPT----------------------------------------------------------------------------------------------------##
##########################################################################################################################

echo ---------------------------------------
echo !!!! PREPROCESSING FUNCTIONAL SCAN !!!!
echo ---------------------------------------

cd $fun_dir || exit 1

## 1. Dropping first # TRS
echo "Dropping first TRs"
3dcalc -a ${rest}.nii.gz[$TRstart..$TRend] -expr 'a' -prefix ${rest}_dr.nii.gz

##2. Deoblique
echo "Deobliquing ${subject}"
3drefit -deoblique ${rest}_dr.nii.gz

##3. Reorient into fsl friendly space (what AFNI calls RPI)
echo "Reorienting ${subject}"
3dresample -orient RPI -inset ${rest}_dr.nii.gz -prefix ${rest}_ro.nii.gz

##4. Slice-time correction 
echo "Slice-time correction ${subject}"
3dTshift -prefix ${rest}_st.nii.gz -tzero 0.0 -tpattern alt+z2 -TR $TR ${rest}_ro.nii.gz

##5. Motion correct to average of timeseries
echo "Motion correcting ${subject}"
3dTstat -mean -prefix ${rest}_st_mean.nii.gz ${rest}_st.nii.gz 
3dvolreg  -Fourier -twopass -base ${rest}_st_mean.nii.gz -zpad 4 -prefix ${rest}_mc.nii.gz -dfile ${rest}_mc_rms.1D -maxdisp1D ${rest}_mc_maxdsp.1D -1Dfile ${rest}_mc.1D ${rest}_st.nii.gz

##1d "export motion parameters as a graph 1D plot file"
echo "export 1dplot graph pf motion parameters"
1dplot -volreg -ps ${rest}_mc.1D > ${rest}_motion.ps
1dplot -ps ${rest}_mc_rms.1D[7,8] > ${rest}_motion_rms.ps

##6. Remove skull/edge detect
echo "Skull stripping ${subject}"
3dAutomask -prefix ${rest}_mask.nii.gz -dilate 1 ${rest}_mc.nii.gz
3dcalc -a ${rest}_mc.nii.gz -b ${rest}_mask.nii.gz -expr 'a*b' -prefix ${rest}_ss.nii.gz


