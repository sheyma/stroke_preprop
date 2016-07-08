#!/bin/bash

TRstart=5
TRend=149
TR=2.3


path_run=$HOME/devel/stroke_preprop
path_data='/scr/ilz2/bayrak/32_COIL_func'
outfile="$path_run/fprepro_condor_all"

echo "executable = $path_run/setenv.sh" > $outfile
echo "universe = vanilla" >> $outfile
echo "request_memory = 3072" >> $outfile
echo "getenv = True" >> $outfile
echo "notification = Error" >> $outfile


cd $path_data
echo $( pwd )

for subj in * ; do
	cd $subj || continue
		for rest in * ; do
   			out=$path_data/$subj/$rest/$rest
			echo "arguments = $path_run/fprepro.sh $subj $path_data/$subj/$rest/ $rest $TRstart $TRend $TR 2>&1"
			echo "output = $out.out "
			echo "error = $out.error"
			echo "log = $out.log"
			echo "queue" 
			echo ""		
		done >> $outfile
	cd ..
done
