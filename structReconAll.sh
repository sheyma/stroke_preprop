#!/bin/bash

path_run=$HOME/devel/stroke_preprop
subj_dir='/scr/ilz2/bayrak/stroke_nifti'
out_dir='/scr/ilz2/bayrak/stroke_reconall'
outfile="$path_run/structReconAll"

echo "executable = $path_run/setenv.sh" > $outfile
echo "universe = vanilla" >> $outfile
echo "request_memory = $(( 3 * 1024 ))" >> $outfile
echo "getenv = True" >> $outfile
echo "notification = Error" >> $outfile


#for i in $subj_dir/*; do
#
#	subj=$(basename $i) 	
#
#	for j in $subj_dir/$subj/T*; do
#		
#		scan=$(basename $j) 
#		out="$out_dir/${subj}_${scan}"
#
#		echo "arguments = /usr/bin/time -v python $path_run/02_structReconAll.py $subj $scan";
#		echo "output = $out.out"
#		echo "error = $out.out" # stderr and stdout into the same file
#		echo "log = $out.log"
#		echo "queue" 
#		echo ""
#	done ;
#
#done >> $outfile 


for subj in 41 43 44 45 46 48 49 ; do		

	scan='T1d00' 
	out="$out_dir/${subj}_${scan}"

	echo "arguments = /usr/bin/time -v python $path_run/02_structReconAll.py $subj $scan";
	echo "output = $out.out"
	echo "error = $out.out" # stderr and stdout into the same file
	echo "log = $out.log"
	echo "queue" 
	echo ""

done >> $outfile 

