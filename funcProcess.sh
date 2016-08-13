#!/bin/bash


#!/bin/bash

path_run=$HOME/devel/stroke_preprop
outfile="$path_run/funcProcess"
job_dir='/scr/ilz2/bayrak/data_func'
file_name='rest'

TRstart=5
TRend=149
TR=2.3

echo "executable = $path_run/setenv.sh" > $outfile
echo "universe = vanilla" >> $outfile
echo "request_memory = $(( 3 * 1024 ))" >> $outfile
echo "getenv = True" >> $outfile
echo "notification = Error" >> $outfile

for xsubj in $job_dir/* ; do
for xscan in $xsubj/rsd??; do

	subj=$(basename $xsubj)
	scan=$(basename $xscan) 

	out="$job_dir/${subj}_${scan}"

	cd $job_dir/$subj/$scan

	echo "arguments = /usr/bin/time -v  $path_run/03_funcProcess.sh $subj $job_dir/$subj/$scan/ $file_name $TRstart $TRend $TR"
	echo "output = $out.out"
	echo "error = $out.out" # stderr and stdout into the same file
	echo "log = $out.log"
	echo "queue" 
	echo ""

	cd $job_dir
done
done >> $outfile 


