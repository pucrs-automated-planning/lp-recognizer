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
# Generate scatter charts for sums of [h1 > h2]:
# ./generate_all_charts.sh sums [-fast]
##

if [[ "$1" == "ref" ]]; then
	# Reference goal
	./generate_charts -full -stats -dat -pdf -lm -fl -ref $2
	#./generate_charts -full -stats -dr -ref $2
elif [[ "$1" == "nonref" ]]; then
	# Closest non-ref goal
	./generate_charts -full -stats -dat -pdf -lm -fl $2
	#./generate_charts -full -stats -dr $2
elif [[ "$1" == "all" ]]; then
	# All goals
	pushd ..
	if [[ "$2" == "all" ]]; then
		# Optimal
		./data_charts.py lm optimal -scatter -stats
		./data_charts.py fl optimal -scatter -stats
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			jobname=$(echo ${file##*/} | sed 's/-all.dat//g')
			cat $file > $jobname.dat
		done
		pushd ..
		# Suboptimal
		./data_charts.py lm suboptimal -scatter -stats
		./data_charts.py fl suboptimal -scatter -stats
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			jobname=$(echo ${file##*/} | sed 's/-all.dat/-sub/g')
			cat $file > $jobname.dat
		done
		pushd ..
		# Noisy
		./data_charts.py lm optimal-old-noisy -scatter -stats
		./data_charts.py fl optimal-old-noisy -scatter -stats
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			jobname=$(echo ${file##*/} | sed 's/-all.dat/-noisy/g')
			cat $file > $jobname.dat
		done
		pushd ..
		# Suboptimal Noisy
		./data_charts.py lm optimal-old-noisy -scatter -stats
		./data_charts.py fl optimal-old-noisy -scatter -stats
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			jobname=$(echo ${file##*/} | sed 's/-all.dat/-sub-noisy/g')
			cat $file > $jobname.dat
		done
		# PDF
		for file in ./*-scatter.dat; do 
			name=$(echo ${file##*/} | sed 's/-scatter.dat//g')
			cat ${name}-scatter.dat > scatter.dat
			cat ${name}-scatter-sub.dat > scatter-sub.dat
			cat ${name}-scatter-noisy.dat > scatter-noisy.dat
			cat ${name}-scatter-sub-noisy.dat > scatter-sub-noisy.dat
			jobname=$(echo $name | sed 's/-all.dat/-all/g')
			pdflatex -jobname=$jobname template_scatter_all.tex
		done
		# Combined Stats
		pushd ..
		./data_charts.py lm all -scatter -stats
		./data_charts.py fl all -scatter -stats
		popd
	elif [[ "$2" == "sub" ]]; then
		./data_charts.py lm suboptimal -scatter -stats
		./data_charts.py fl suboptimal -scatter -stats
		#./data_charts.py dr suboptimal -stats
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			cat $file > scatter.dat
			jobname=$(echo ${file##*/} | sed 's/-all.dat/-sub/g')
			pdflatex -jobname=$jobname template_scatter.tex
		done
	elif [[ "$2" == "sub-noisy" ]]; then
		./data_charts.py lm suboptimal-old-noisy -scatter -stats
		./data_charts.py fl suboptimal-old-noisy -scatter -stats
		#./data_charts.py dr suboptimal-old-noisy -stats
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			cat $file > scatter.dat
			jobname=$(echo ${file##*/} | sed 's/-all.dat/-sub-noisy/g')
			pdflatex -jobname=$jobname template_scatter.tex
		done
	elif [[ "$2" == "noisy" ]]; then
		./data_charts.py lm optimal-old-noisy -scatter -stats
		./data_charts.py fl optimal-old-noisy -scatter -stats
		#./data_charts.py dr optimal-old-noisy -stats
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			cat $file > scatter.dat
			jobname=$(echo ${file##*/} | sed 's/-all.dat/-noisy/g')
			pdflatex -jobname=$jobname template_scatter.tex
		done
	else
		./data_charts.py lm optimal -scatter -stats $2
		./data_charts.py fl optimal -scatter -stats $2
		#./data_charts.py dr optimal -stats $2
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			cat $file > scatter.dat
			jobname=$(echo ${file##*/} | sed 's/-all.dat//g')
			pdflatex -jobname=$jobname template_scatter.tex
		done
	fi
	rm *scatter*.dat
elif [[ "$1" == "sums" ]]; then
	pushd ..
	if [[ "$2" == "all" ]]; then
		./data_charts.py lm all -sums -stats $2
		./data_charts.py fl all -sums -stats $2
		#./data_charts.py dr all -sums $2
	else
		./data_charts.py lm optimal -sums -stats $2
		./data_charts.py fl optimal -sums -stats $2
		#./data_charts.py dr optimal -sums $2
		popd
		for file in ../data-charts/*-sums*.dat; do 
			cat $file > scatter.dat
			jobname=$(echo ${file##*/} | sed 's/.dat//g')
			pdflatex -jobname=$jobname template_sums.tex
		done
		rm scatter.dat
	fi
fi

# Clean-up.
rm *.log *.aux