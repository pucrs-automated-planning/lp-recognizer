#!/usr/bin/env bash

##
## Generate the different version of .pdf charts.
##

## Uses:
# Generate scatter and agr charts using the reference goal:
# ./generate_all_charts.sh ref [-fast]
# Generate scatter and agr charts using the closest non-reference goal:
# ./generate_all_charts.sh nonref [-fast]
# Generate scatter charts and stat tables using all goals:
# ./generate_all_charts.sh all [-fast]
##

if [[ "$1" == "ref" ]]; then
	# Reference goal
	./generate_charts -full -stats -dat -pdf -lmc -flow -ref $2
	./generate_charts -full -stats -dr -ref $2
elif [[ "$1" == "nonref" ]]; then
	# Closest non-ref goal
	./generate_charts -full -stats -dat -pdf -lmc -flow $2
	./generate_charts -full -stats -dr $2
elif [[ "$1" == "all" ]]; then
	# All goals
	pushd ..
	./data_output.py lm optimal -scatter -stats $2
	./data_output.py fl optimal -scatter -stats $2
	./data_output.py dr optimal -stats $2
	popd
	for file in ../data-charts/*-scatter-all.dat; do 
		cat $file > scatter.dat
		jobname=$(echo ${file##*/} | sed 's/-all.dat//g')
		pdflatex -jobname=$jobname template_scatter.tex
	done
fi

# Clean-up.
rm *.log *.aux