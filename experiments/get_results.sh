#!/usr/bin/env bash

##
## Master script to run tests and generate all .txt and .pdf files for the results.
##

## Uses:
# Run methods and generate new .txt and .pdf files:
# ./get_results.sh -rerun [-fast]
# Generate .txt tables files from existing .output files:
# ./get_results.sh -txt [-fast]
# Generate .pdf tables from existing .txt files:
# ./get_results.sh -tables [-fast] 
# Generate .txt files and .pdf tables:
# ./get_results.sh -txt -comp [-fast]
# Generate .pdf charts from existing .txt files:
# ./get_results.sh -charts [-fast] 
##

# Default list of domains.
export DOMAINS='
	blocks-world
	depots
	driverlog
	dwr
	easy-ipc-grid
	ferry
	logistics
	miconic
	rovers
	satellite
	sokoban
	zeno-travel'

# Root folder for all domains.
export DATASETS=../goal-plan-recognition-dataset

# Parse arguments.
for arg in "$@"; do
	if [[ "$arg" == "-fast" ]]; then
		# Use smaller list of domains.
		TEST=-fast
		export DOMAINS='
			blocks-world
			depots
			driverlog
			dwr
			rovers
			sokoban'
	elif [[ "$arg" == "-test" ]]; then
		# Use sample domain.
		TEST=-test
		export DOMAINS=small-sokoban
		export DATASETS=experiments/
	elif [[ "$arg" == "-txt" ]]; then
		# Generate method .txt tables.
		EXP=txt
	elif [[ "$arg" == "-rerun" ]]; then
		# Re-run all experiments.
		EXP=output
	elif [[ "$arg" == "-dd" ]]; then
		# Generate domain .txt tables.
		DD=txt
	elif [[ "$arg" == "-comp" ]]; then
		# Generate .txt tables for pair comparisons.
		COMP=txt
	elif [[ "$arg" == "-tables" ]]; then
		# Generate pdf tables.
		COMP=pdf
	elif [[ "$arg" == "-charts1" ]]; then
		# Generate pdf charts (ref goals).
		CHARTS=-ref
	elif [[ "$arg" == "-charts2" ]]; then
		# Generate pdf charts (nonref goals.
		CHARTS=-nonref
	elif [[ "$arg" == "-charts3" ]]; then
		# Generate pdf charts (all goals).
		CHARTS=-all
	elif [[ "$arg" == "-charts4" ]]; then
		# Generate pdf charts (all goals, sum scatter).
		CHARTS=-sums
	fi
done

# Methods from the First paper.
export BASIC="delta deltau"
export CONSTRAINT_PAIRS="delta-cps delta-cls delta-clp deltau-cps deltau-cls deltau-clp"
export CONSTRAINT_SINGLE="delta-cl delta-cp delta-cs deltau-cl deltau-cp deltau-cs"
export CONSTRAINT_NEW="delta-cd delta-o-cd delta-o-cl delta-cf1 delta-cf2"
export FILTERS="delta-f1 deltau-f1 delta-f2 deltau-f2"

# Methods from the second paper.
export LMC="delta-cl delta-o-cl delta-o-cl1"
export LMC_N="$LMC delta-o-cl2"
export DELR="delta-cdt delta-o-cdt delta-o-cdto delta-o-cdto1 delta-o-cdtb1"
export DELR_N="$DELR delta-o-cdta1"
export FLOW="delta-cf1 delta-cf1ab delta-o-cf17 delta-o-cf16 delta-cf2"

# Download datasets if necessary.
if [[ ! -d ../$DATASETS ]]; then
	echo "Datasets not found at ../$DATASETS"
	source get_datasets.sh
fi

pushd ..

# Generates result tables for each domain.
# Runs test_domain.py instead if flag -rerun is set.
# Choose the dataset type by providing it as the first argument for get_results.
# Choose the methods by setting the variable METHODS.
# Each method in METHODS should be separated by spaces.
get_results() {
	# $1 = data set type
	# $2 = method list
	for domain in $DOMAINS; do
		echo "Processing domain $domain-$1"
		# Domain .txt tables.
		if [[ "$DD" == "txt" ]]; then
			python2 data_domain.py $domain-$1 $TEST
		fi
		# Method's results.
		if [[ "$EXP" == "output" ]]; then
			# .output files + .txt tables.
			python2 test_domain.py $DATASETS $domain-$1 "$METHODS" $TEST -S cplex > experiments/stdout/$1.txt
		elif [[ "$EXP" == "txt" ]]; then
			# .txt tables only.
			python2 data_output.py "$METHODS" $domain-$1 $TEST
		fi
	done
}
echo "Generating results tables..."
if [[ "$TEST" == "-test" ]]; then
	METHODS="delta-cl delta-o-cl1"
	get_results optimal
else
	METHODS="$BASIC $LMC $DELR $FLOW"
	get_results optimal
	get_results suboptimal
	METHODS="$BACIC_N $LMC_N $DELR_N $FLOW_N"
	get_results optimal-old-noisy
	get_results suboptimal-old-noisy
fi
echo "Done."

# Generate .txt tables for group comparisons.
merge_comp_files() {
	for d in "optimal suboptimal optimal-old-noisy suboptimal-old-noisy"; do
		echo "$2" > $1-$d.txt
		for file in $1-*-$d.txt; do
			echo $file >> $1-$d.txt
			echo "$(cat $file)" >> $1-$d.txt
		done
	done
}
if [[ "$COMP" == "txt" ]]; then
	echo "Generating comparison tables..."
	if [[ "$TEST" == "-test" ]]; then
		./data_comparison.py lmc "delta-cl delta-o-cl1" optimal $TEST
	else 
		./data_comparison.py lmc "delta-cl delta-o-cl delta-o-cl1" optimal suboptimal $TEST
		./data_comparison.py lmc "delta-cl-f2 delta-o-cl-f2 delta-o-cl1-f2" optimal-old-noisy suboptimal-old-noisy $TEST
		./data_comparison.py delr "delta-o-cdt delta-o-cdto delta-o-cdtb5" optimal suboptimal $TEST
		./data_comparison.py delr "delta-o-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2"optimal-old-noisy suboptimal-old-noisy $TEST
		./data_comparison.py flow "delta-cf1 delta-cf1ab delta-o-cf17 delta-o-cf16 delta-cf2" optimal suboptimal $TEST
		./data_comparison.py flow "delta-cf1-f2 delta-cf1ab-f2 delta-o-cf17-f2 delta-o-cf16-f2 delta-cf2-f2" optimal-old-noisy suboptimal-old-noisy $TEST
		cd data-comparison
		merge_comp_files lmc "L	L+	L+(soft)" 
		merge_comp_files delr "D+	D+2	D+3"
		merge_comp_files flow "F	F(M2)	F(PxE-Intra)	F(PxE-Gen)	F2"
		cd ..
	fi
	echo "Done."
fi

if [[ "$TEST" != "-test" ]]; then
	# .pdf tables.
	if [[ ! -z "$COMP" || ! -z "$EXP" ]]; then
		echo "Generating pdf tables..."
		cd latex-tables
		bash generate_all_tables.sh full $TEST
		cd ..
		echo "Done."
	fi
	# .pdf charts.
	if [[ ! -z "$CHARTS" ]]; then
		echo "Generating pdf charts$CHARTS..."
		cd latex-charts
		bash generate_all_charts.sh $CHARTS $TEST
		cd ..
		echo "Done."
	fi
fi

popd