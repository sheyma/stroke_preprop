#!/bin/bash

#path_run=$HOME/devel/stroke_preprop
#subj_dir='/scr/ilz2/bayrak/stroke_nifti'
#out_dir='/scr/ilz2/bayrak/stroke_func'
#outfile="$path_run/funcProcess"
#for i in $subj_dir/*; do

#	subj=$(basename $i) 	

#	for j in $subj_dir/$subj/r*; do
		
#		scan=$(basename $j) 

#		echo $subj_dir/$subj/$scan/*
#		echo $out_dir/$subj/$scan
#		cp $subj_dir/$subj/$scan/*  $out_dir/$subj/$scan
#	done
#done


TRstart=5
TRend=149
TR=2.3


path_run=$HOME/devel/stroke_preprop
path_data='/scr/ilz2/bayrak/healthy_func'
file_name='rest'
outfile="$path_run/funcProcess"

subj_list='/scr/ilz2/bayrak/subject_healthy'

echo "executable = $path_run/setenv.sh" > $outfile
echo "universe = vanilla" >> $outfile
echo "request_memory = 3072" >> $outfile
echo "getenv = True" >> $outfile
echo "notification = Error" >> $outfile

cd $path_data
echo $( pwd )

#for subj in $(cat $subj_list) ; do
#	
#	cd $subj
#
#	for rest in * ; do
#		
#				
#		out="$path_data/${subj}_${rest}"
#
#		echo "arguments = /usr/bin/time -v  $path_run/03_funcProcess.sh $subj $path_data/$subj/$rest/ $file_name $TRstart $TRend $TR"
#		echo "output = $out.out"
#		echo "error = $out.out" # stderr and stdout into the same file
#		echo "log = $out.log"
#		echo "queue" 
#		echo ""		
#		
#	
#	done >> $outfile
#
#	cd ..
#done


for subj in  06 09 ; do

	cd $subj
	rest='rs'	
	out="$path_data/${subj}_${rest}"
	echo "arguments = /usr/bin/time -v  $path_run/03_funcProcess.sh $subj $path_data/$subj/$rest/ $file_name $TRstart $TRend $TR"
	echo "output = $out.out"
	echo "error = $out.out" # stderr and stdout into the same file
	echo "log = $out.log"
	echo "queue" 
	echo ""		

	cd ..
done	>> $outfile

