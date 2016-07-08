#!/bin/bash

path_run=$HOME/devel/stroke_preprop
subj=02
path_rest='/scr/ilz2/bayrak/32_COIL_func/02/rsd01/'
rest_scan='rsd01'
TRstart=5
TRend=149
TR=2.3

out=$path_rest

echo "executable = $path_run/setenv.sh" > $path_run/fprepro_condor
echo "universe = vanilla" >> $path_run/fprepro_condor
echo "request_memory = 3072" >> $path_run/fprepro_condor
echo "getenv = True" >> $path_run/fprepro_condor
echo "notification = Error" >> $path_run/fprepro_condor 

echo "arguments = $path_run/fprepro.sh $subj $path_rest $rest_scan $TRstart $TRend $TR  " >> $path_run/fprepro_condor
echo "output = $out.out " >> $path_run/fprepro_condor
echo "error = $out.error" >> $path_run/fprepro_condor
echo "log = $out.log" >> $path_run/fprepro_condor
echo "queue" >> $path_run/fprepro_condor 
echo "" >> $path_run/fprepro_condor
