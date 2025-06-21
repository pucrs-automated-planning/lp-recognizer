#!/usr/bin/env bash

##
## Generate the different version of .pdf charts.
##

## Uses:
# Generate scatter charts and stat tables using all goals, separating by dataset:
# ./generate_all_charts.sh hc all [-fast]
# Generate scatter charts and stat tables using all goals, separating by ref vs nonref:
# ./generate_all_charts.sh hyps all [-fast]
# Generate scatter charts for sums of [h1 > h2]:
# ./generate_all_charts.sh sums all [-fast]
##

pushd ..
if [[ "$1" == "hc" ]]; then
	echo "Generating scatter plots for HC values."
	if [[ "$2" == "optimal" ]]; then
		./data_charts.py lm optimal -scatter -stats $2
		./data_charts.py fl optimal -scatter -stats $2
		#./data_charts.py dr optimal -stats $2
		popd
		for file in ../data-charts/*-scatter-all.dat; do 
			cat $file > scatter.dat
			jobname=$(echo ${file##*/} | sed 's/-all.dat//g')
			pdflatex -jobname=$jobname template_scatter.tex
		done
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
	else # All goals, by dataset
		echo "Separated by noisy vs non-noisy."
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
			jobname=$(echo $name | sed 's/.dat//g')
			pdflatex -jobname=$jobname template_scatter_datasets.tex
		done
		# Combined Stats
		pushd ..
		./data_charts.py lm all -scatter -stats
		./data_charts.py fl all -scatter -stats
		popd
	fi
	rm *scatter*.dat
elif [[ "$1" == "hyps" ]]; then # All goals, by hyp
	echo "Separated by ref vs nonref."
	./data_charts.py lm $2 -scatter -stats
	./data_charts.py fl $2 -scatter -stats
	popd
	for file in ../data-charts/*-scatter-ref.dat; do 
		jobname=$(echo ${file##*/} | sed 's/.dat//g')
		cat $file > $jobname.dat
	done
	for file in ../data-charts/*-scatter-nonref.dat; do 
		jobname=$(echo ${file##*/} | sed 's/.dat//g')
		cat $file > $jobname.dat
	done
	# PDF
	for file in ./*-scatter-ref.dat; do 
		name=$(echo ${file##*/} | sed 's/-scatter-ref.dat//g')
		cat ${name}-scatter-ref.dat > scatter-ref.dat
		cat ${name}-scatter-nonref.dat > scatter-nonref.dat
		jobname=$(echo $name | sed 's/.dat//g')
		pdflatex -jobname=$jobname template_scatter_hyps.tex
	done
elif [[ "$1" == "sums" ]]; then
	echo "Generating scatter plots for sums of [h1 > h2]."
	if [[ "$2" == "all" ]]; then
		./data_charts.py lm all -sums -stats $3
		./data_charts.py fl all -sums -stats $3
		#./data_charts.py dr all -sums $3
	else
		./data_charts.py lm $2 -sums -stats $3
		./data_charts.py fl $2 -sums -stats $3
		#./data_charts.py dr $2 -sums $3
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