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
	./output_format.py lm optimal -scatter -stats $2
	./output_format.py fl optimal -scatter -stats $2
	./output_format.py dr optimal -stats $2
	cd data-charts
	for file in *-scatter.dat; do
		jobname=$(echo $file | sed 's/.dat//g')
		cat $file > ../latex-charts/scatter.dat
		pdflatex -jobname=$jobname ../latex-charts/template_scatter.tex
		rm ../latex-charts/$jobname.aux ../latex-charts/$jobname.txt
	done
	popd
fi

# Clean-up.
rm *.txt *.aux